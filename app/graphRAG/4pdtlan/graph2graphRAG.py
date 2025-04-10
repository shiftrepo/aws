import boto3
from langchain_community.vectorstores import Neo4jVector
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from neo4j import GraphDatabase

# =========================
# 接続情報
# =========================

# Neo4j情報（RAG用データ）
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

# AWS情報
region = "us-east-1"
bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)

# 推論プロファイル ARN
inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"

# =========================
# Embedding & LLM
# =========================

embedding = BedrockEmbeddings(
    client=bedrock_runtime,
    model_id="amazon.titan-embed-text-v2:0",
    region_name=region
)

llm = ChatBedrock(
    client=bedrock_runtime,
    model_id=inference_profile_arn,  # 推論プロファイル ARN を使用
    provider="anthropic",  # モデルプロバイダーを指定
    region_name=region,
    model_kwargs={"temperature": 0.5, "max_tokens": 1024}
)

# =========================
# Retrieval QAチェーン構築
# =========================

print("Retrieval QAチェーン構築中...")

# VectorStoreの初期化
vectorstore = Neo4jVector(
    embedding=embedding,
    url=NEO4J_URI_RAG,
    username=NEO4J_USER_RAG,
    password=NEO4J_PASS_RAG,
    index_name="graphrag_index",
    node_label="GraphRAGChunk",
    text_node_property="text"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt_template = PromptTemplate.from_template(
    """あなたは社内のデータ構造に詳しいアシスタントです。
質問に対して、以下の情報に基づいて答えてください。

{context}

質問: {question}
回答:"""
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# =========================
# 質問処理関数
# =========================

def get_answer(question):
    """指定された質問に基づいて回答を取得します。"""
    response = qa_chain.invoke({"query": question})
    return response

