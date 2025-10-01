import os
import uuid
import logging
import streamlit as st
import boto3
import tenacity

# LlamaIndex Core imports
from llama_index.core import PropertyGraphIndex, Settings # ChatPromptTemplate は未使用なので削除も可
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.embeddings.bedrock import BedrockEmbedding

# --- Langfuse関連のインポートを変更 ---
# from langfuse.callback import CallbackHandler # 古いハンドラを削除
from llama_index.core.callbacks import CallbackManager # CallbackManagerを追加
from langfuse.llama_index import LlamaIndexCallbackHandler # LlamaIndexCallbackHandlerを追加

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🌐 Langfuse session init (これは Streamlit セッション管理用なので残す)
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]
session_id = st.session_state["session_id"]
logger.info(f"Streamlit Session ID: {session_id}") # ログメッセージを明確化

# --- Langfuse LlamaIndex Callback Handler の初期化とグローバル設定 ---
logger.info("Initializing Langfuse LlamaIndex callback handler...")
# 環境変数から Langfuse の設定を読み込む
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")

from langfuse.llama_index import LlamaIndexInstrumentor

# LlamaIndexの操作をトレースするためにLlamaIndexInstrumentorを初期化
instrumentor = LlamaIndexInstrumentor(
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    host=os.environ.get("LANGFUSE_HOST")
)

if not (langfuse_public_key and langfuse_secret_key and langfuse_host):
    logger.warning("Langfuse environment variables (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) are not fully set. Langfuse callback handler will not be initialized.")
    # ハンドラが初期化できない場合は、Settings.callback_manager を設定しない
    # もしくはエラーにするなど、必要に応じて処理を変更してください
else:
    try:
        langfuse_callback_handler = LlamaIndexCallbackHandler(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host,
            # session_id は LlamaIndexCallbackHandler の初期化引数にはありません。
            # Langfuse はトレースごとにセッションを管理します。
            # 必要であれば、トレースのメタデータやタグで Streamlit の session_id を渡すことを検討します。
            # 例: tags=["streamlit", f"session:{session_id}"]
            tags=["streamlit-app", "neo4j-rag", f"st_session:{session_id}"] # タグに session_id を含める例
        )
        logger.info("Setting global callback manager with Langfuse handler...")
        Settings.callback_manager = CallbackManager([langfuse_callback_handler])
        langfuse_callback_handler.set_trace_params(
                session_id = session_id
                )
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse callback handler: {e}")
        # Langfuseの初期化に失敗してもアプリの実行を続ける場合があるため、
        # Settings.callback_manager は設定されないまま進む。

# Bedrock clients
logger.info("Creating boto3 session and bedrock client...")
# 環境変数のチェックを追加 (オプション)
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

if not (aws_access_key_id and aws_secret_access_key and aws_region):
    st.error("AWS credentials or region not found in environment variables!")
    st.stop() # 必須情報がない場合はアプリを停止

boto3_session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
bedrock_client = boto3_session.client('bedrock-runtime')

# LLM
logger.info("Initializing Bedrock LLM...")
llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    client=bedrock_client,
    # callbacks=[langfuse_handler] # Settings.callback_manager でグローバルに設定するため不要
)

# Embedding
@tenacity.retry(stop=tenacity.stop_after_attempt(3),
                 wait=tenacity.wait_fixed(5),
                 retry=tenacity.retry_if_exception_type(Exception),
                 before_sleep=tenacity.before_sleep_log(logging, logging.WARNING))
def create_embedding_with_retry(client, model_name, request_timeout):
    logger.info("Creating Bedrock embedding model with retry...")
    # BedrockEmbedding も Settings.callback_manager を参照する
    return BedrockEmbedding(
        model_name=model_name,
        client=client,
        use_async=False, # 同期処理のまま
        request_timeout=request_timeout
    )

embedding = create_embedding_with_retry(
    bedrock_client,
    "amazon.titan-embed-text-v2:0",
    request_timeout=60
)

# Set global settings (Callback Manager は上で設定済み)
logger.info("Setting global LLM and embedding settings...")
Settings.llm = llm
Settings.embed_model = embedding
# Settings.callback_manager は langfuse_callback_handler の初期化後に設定済み

# Neo4j store
logger.info("Initializing Neo4j property graph store...")
# Neo4j の接続情報も環境変数から取得するのが望ましい
neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
neo4j_url = os.getenv("NEO4J_URL", "bolt://neo4jRAG:7687") # 環境変数がない場合のデフォルト値

graph_store = Neo4jPropertyGraphStore(
    username=neo4j_username,
    password=neo4j_password,
    url=neo4j_url,
)

# Index
logger.info("Loading existing PropertyGraphIndex...")
try:
    index = PropertyGraphIndex.from_existing(
        # embed_model や llm は Settings から取得される
        property_graph_store=graph_store,
        show_progress=True,
        # callback_manager も Settings から取得される
    )
except Exception as e:
    logger.error(f"Failed to load PropertyGraphIndex from Neo4j: {e}")
    st.error(f"既存のグラフインデックスの読み込みに失敗しました: {e}")
    st.stop() # インデックスがないと動作しないため停止

# Retriever + Chat engine
if "chat_engine" not in st.session_state:
    logger.info("Creating chat engine with retriever and memory...")
    retriever = index.as_retriever(include_text=False) # include_text=False は意図通りか確認
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    # ContextChatEngine.from_defaults は Settings を参照する
    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        memory=memory,
        # llm, callback_manager は Settings から自動的に適用される
        # verbose=True # デバッグ用に詳細ログが必要な場合
    )
    st.session_state["chat_engine"] = chat_engine

chat_engine = st.session_state["chat_engine"]

# Streamlit UI
st.title("Neo4j + Claude Haiku チャット") # モデル名を合わせる (Haiku)

# Display chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, content in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(content)

# Input
if prompt := st.chat_input("質問を入力してください"):
    # 自動トレースを開始
    #instrumentor.start()
    logger.info(f"User input received: {prompt}")
    st.session_state["chat_history"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # langfuse_handler.flush() # LlamaIndexCallbackHandler では通常不要

    with st.chat_message("assistant"):
        with st.spinner("考え中..."): # 応答待機中にスピナーを表示
            logger.info("Generating response from chat engine...")
            try:
                # Chat Engine の呼び出し時にトレース情報が付与される (Settings経由)
                response = chat_engine.chat(prompt)
                response_text = response.response
                logger.info(f"Response generated: {response_text}")
                st.markdown(response_text)
                st.session_state["chat_history"].append(("assistant", response_text))
                instrumentor.flush()

            except Exception as e:
                logger.error(f"Error during chat engine execution: {e}", exc_info=True)
                st.error(f"応答の生成中にエラーが発生しました: {e}")
                # エラー発生時も履歴に追加（オプション）
                st.session_state["chat_history"].append(("assistant", f"エラー: {e}"))


# --- アプリ終了時の処理 ---
# Streamlit では明示的な終了フックは標準ではないが、
# Langfuse ハンドラのシャットダウンが必要な場合 (通常 LlamaIndexCallbackHandler では不要) は
# try...finally ブロックなどを検討する必要があるかもしれません。
# logger.info("Shutting down Langfuse handler (if necessary)...")
# if 'langfuse_callback_handler' in locals() and hasattr(langfuse_callback_handler, 'shutdown'):
#      langfuse_callback_handler.shutdown()


