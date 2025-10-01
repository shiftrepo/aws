# graphRAG_search.py

import boto3
import json
import numpy as np
from scipy.spatial.distance import cosine
from py2neo import Graph

# AWSクライアント設定
client = boto3.client("bedrock", region_name="us-west-2")  # 必要に応じてリージョンを設定

# Neo4j接続設定（GraphRAG用Neo4j）
rag_graph = Graph("bolt://neo4jRAG:7687", auth=("neo4j", "password"))  # GraphRAG用のNeo4jデータベース

# 埋め込み生成関数（Titan Embedding）
def generate_embedding(text: str):
    response = client.invoke_model(
        ModelId="amazon.titan-embed-text-v2:0",
        Body=text.encode("utf-8"),
        ContentType="application/json"
    )
    embedding = response["Body"].read()
    return json.loads(embedding)

# 質問の埋め込みを生成
def find_most_similar_node(question_embedding):
    query = "MATCH (n:Node) RETURN n.id AS id, n.embedding AS embedding LIMIT 100"
    result = rag_graph.run(query)

    similarities = []
    for record in result:
        node_id = record['id']
        node_embedding = np.array(record['embedding'])
        similarity = 1 - cosine(question_embedding, node_embedding)
        similarities.append((node_id, similarity))

    # 最も類似するノードのIDを返す
    most_similar_node = max(similarities, key=lambda x: x[1])
    return most_similar_node[0]  # 最も類似するノードID

# 応答生成関数（Claude-3）
def generate_response(question: str):
    response = client.invoke_model(
        ModelId="anthropic.claude-3-haiku-20240307-v1:0",
        Body=f"Human: {question}\nAssistant:",
        ContentType="application/json"
    )
    return response["Body"].read().decode('utf-8')

# 最も関連するノードに基づいて応答を生成
def generate_answer_using_claude(question, node_id):
    query = "MATCH (n:Node) WHERE n.id = $node_id RETURN n.text AS text"
    result = rag_graph.run(query, node_id=node_id).single()
    node_text = result['text']

    # ノードの内容と質問を含めてClaude-3に送信
    prompt = f"関連するノード:\n{node_text}\n質問: {question}\n応答:"
    response = generate_response(prompt)
    return response

# 質問を受け付け、関連ノードを検索して応答を生成
question = "GraphRAGの使い方を教えてください"
question_embedding = generate_embedding(question)

most_similar_node_id = find_most_similar_node(question_embedding)
answer = generate_answer_using_claude(question, most_similar_node_id)

print(f"最も関連するノードID: {most_similar_node_id}")
print(f"生成された応答: {answer}")

