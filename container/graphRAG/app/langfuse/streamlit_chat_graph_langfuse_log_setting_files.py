import os
import uuid
import logging
import streamlit as st
import boto3
import tenacity
import textwrap

# LlamaIndex Core imports
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.embeddings.bedrock import BedrockEmbedding

# Langfuse関連
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler, LlamaIndexInstrumentor

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🌐 Streamlitセッション初期化
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]
session_id = st.session_state["session_id"]
logger.info(f"Streamlit Session ID: {session_id}")

# 🔧 LLM 設定 UI（追加）
with st.sidebar:
    st.header("LLM設定")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    max_output_tokens = st.slider("最大出力トークン数", min_value=100, max_value=4096, value=1024, step=100)
    max_text_length = st.slider("最大テキスト長さ (文字数)", min_value=1000, max_value=10000, value=3000, step=100)  # ユーザーが設定できる最大文字数

# Langfuse環境変数
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")

# Langfuse Instrumentor 初期化
instrumentor = LlamaIndexInstrumentor(
    secret_key=langfuse_secret_key,
    public_key=langfuse_public_key,
    host=langfuse_host
)

# Langfuse Callback Handler 設定
if not (langfuse_public_key and langfuse_secret_key and langfuse_host):
    logger.warning("Langfuseの環境変数が設定されていません。トレースは無効になります。")
else:
    try:
        langfuse_callback_handler = LlamaIndexCallbackHandler(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host,
            tags=["streamlit-app", "neo4j-rag", f"st_session:{session_id}"]
        )
        logger.info("Langfuse callback handler を設定")
        Settings.callback_manager = CallbackManager([langfuse_callback_handler])
        langfuse_callback_handler.set_trace_params(session_id=session_id)
    except Exception as e:
        logger.error(f"Langfuse callback handler の初期化に失敗: {e}")

# AWS認証
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

if not (aws_access_key_id and aws_secret_access_key and aws_region):
    st.error("AWSの環境変数が設定されていません")
    st.stop()

boto3_session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
bedrock_client = boto3_session.client('bedrock-runtime')

# LLM（変更あり：temperatureとmax_tokens追加）
llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    client=bedrock_client,
    temperature=temperature,
    max_tokens=max_output_tokens
)

# Embedding
@tenacity.retry(stop=tenacity.stop_after_attempt(3),
                wait=tenacity.wait_fixed(5),
                retry=tenacity.retry_if_exception_type(Exception),
                before_sleep=tenacity.before_sleep_log(logging, logging.WARNING))
def create_embedding_with_retry(client, model_name, request_timeout):
    logger.info("Embedding モデルの初期化中...")
    return BedrockEmbedding(
        model_name=model_name,
        client=client,
        use_async=False,
        request_timeout=request_timeout
    )

embedding = create_embedding_with_retry(
    bedrock_client,
    "amazon.titan-embed-text-v2:0",
    request_timeout=60
)

# グローバル設定
Settings.llm = llm
Settings.embed_model = embedding

# Neo4j 接続
neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
neo4j_url = os.getenv("NEO4J_URL", "bolt://neo4jRAG:7687")

graph_store = Neo4jPropertyGraphStore(
    username=neo4j_username,
    password=neo4j_password,
    url=neo4j_url,
)

# インデックス読み込み
try:
    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
        show_progress=True,
    )
except Exception as e:
    logger.error(f"インデックスの読み込みに失敗: {e}")
    st.error(f"既存のグラフインデックスの読み込みに失敗しました: {e}")
    st.stop()

# Retriever + Chat Engine
if "chat_engine" not in st.session_state:
    retriever = index.as_retriever(include_text=False)
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        memory=memory,
    )
    st.session_state["chat_engine"] = chat_engine

chat_engine = st.session_state["chat_engine"]

# テキストファイルをプロンプトに追加する関数
def split_text(text, max_length):
    # textwrapでテキストを分割
    return textwrap.wrap(text, width=max_length)

# Streamlit UI
st.title("Neo4j + Claude Haiku チャット")

# ファイルのアップロード
uploaded_files = st.file_uploader("テキストファイルをアップロードしてください", type=["txt"], accept_multiple_files=True)

# ファイル内容をプロンプトに追加
if uploaded_files:
    all_content = ""
    
    # 各ファイルの内容を読み込む
    for uploaded_file in uploaded_files:
        file_content = uploaded_file.read().decode("utf-8")
        all_content += f"\n\n----- {uploaded_file.name} -----\n\n{file_content}"

    # ファイルの内容が設定された最大文字数を超える場合のみ分割
    if len(all_content) > max_text_length:
        split_content = split_text(all_content, max_text_length)
    else:
        split_content = [all_content]  # 分割せずそのまま使用
    
    # テキストエリアに分割された内容を表示
    st.text_area("アップロードされたファイルの内容", value="\n".join(split_content), height=300)

# チャット履歴表示
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, content in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(content)

# 入力処理
if prompt := st.chat_input("質問を入力してください"):
    logger.info(f"User input: {prompt}")
    st.session_state["chat_history"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # ファイル内容と質問を組み合わせてプロンプトを作成
    full_prompt = f"""次の複数のテキストに基づいて質問に答えてください:

{textwrap.shorten("\n".join(split_content), width=max_text_length)}

質問: {prompt}
"""
    
    # LLMによる回答生成
    with st.chat_message("assistant"):
        with st.spinner("考え中..."):
            status_placeholder = st.empty()  # 動的メッセージ表示用
            try:
                status_placeholder.info("Retriever を呼び出しています...")
                response = chat_engine.chat(full_prompt)

                status_placeholder.info("応答を生成中...")
                response_text = response.response
                logger.info(f"Response: {response_text}")

                status_placeholder.empty()
                st.markdown(response_text)
                st.session_state["chat_history"].append(("assistant", response_text))
                instrumentor.flush()

            except Exception as e:
                logger.error(f"エラー発生: {e}", exc_info=True)
                status_placeholder.error("応答中にエラーが発生しました。")
                st.error(f"応答の生成中にエラーが発生しました: {e}")
                st.session_state["chat_history"].append(("assistant", f"エラー: {e}"))

