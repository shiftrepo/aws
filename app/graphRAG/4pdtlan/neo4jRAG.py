import boto3
import json
from langchain_community.vectorstores import Neo4jVector
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from neo4j import GraphDatabase

# =========================
# 接続情報
# =========================

# 元Neo4j（データ抽出元）
NEO4J_URI_SRC = "bolt://neo4j:7687"
NEO4J_USER_SRC = "neo4j"
NEO4J_PASS_SRC = "password"

# RAG用Neo4j（データ格納先）
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
# 元Neo4jからドキュメント作成
# =========================

print("元Neo4jからグラフ情報を取得中...")

def fetch_graph_data():
    driver = GraphDatabase.driver(NEO4J_URI_SRC, auth=(NEO4J_USER_SRC, NEO4J_PASS_SRC))
    cypher = """
    MATCH (t:テーブル)-[:保持する]->(i:項目)
    OPTIONAL MATCH (i)-[:入力]->(a:アプリケーション)
    OPTIONAL MATCH (a)-[:出力]->(o:項目)
    RETURN t, i, a, o
    """
    documents = []

    with driver.session() as session:
        results = session.run(cypher)
        for record in results:
            lines = []
            t = record["t"]
            i = record["i"]
            a = record["a"]
            o = record["o"]

            if t:
                lines.append(f"テーブル: {t['名前']} (ID: {t['テーブルID']})")
            if i:
                lines.append(f"  - 項目: {i['名前']} (ID: {i['項目ID']})")
            if a:
                lines.append(f"    - 入力元アプリ: {a['名前']} (ID: {a['アプリケーションID']})")
            if o:
                lines.append(f"      - アプリ出力項目: {o['名前']} (ID: {o['項目ID']})")

            content = "\n".join(lines)
            documents.append(Document(page_content=content))

    driver.close()
    return documents

docs = fetch_graph_data()

# =========================
# RAG用Neo4jに保存
# =========================

print("RAG用Neo4jにベクトル保存中...")

vectorstore = Neo4jVector.from_documents(
    documents=docs,
    embedding=embedding,
    url=NEO4J_URI_RAG,
    username=NEO4J_USER_RAG,
    password=NEO4J_PASS_RAG,
    index_name="graphrag_index",
    node_label="GraphRAGChunk",
    text_node_property="text"
)

# =========================
# Retrieval QAチェーン構築
# =========================

print("Retrieval QAチェーン構築中...")

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
# 質問してみる
# =========================

question = "項目名：顧客名の変更によって影響を受けるものは何ですか？"

response = qa_chain.invoke({"query": question})

# StreamingBodyの処理を追加
response_body = response["result"]
if isinstance(response_body, bytes):
    response_body = response_body.decode("utf-8")

print("\n==== 質問 ====")
print(question)

print("\n==== 回答 ====")
print(response_body)

print("\n==== ソース ====")
for i, doc in enumerate(response["source_documents"], 1):
    print(f"[{i}] {doc.page_content}")

