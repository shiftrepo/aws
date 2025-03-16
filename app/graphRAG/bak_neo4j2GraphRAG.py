# graphRAG_creation.py

import boto3
import json
import numpy as np
from py2neo import Graph

# AWSクライアント設定
client = boto3.client("bedrock", region_name="us-east-1")  # 必要に応じてリージョンを設定

# Neo4j接続設定（元のNeo4j）
source_graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))  # 既存のNeo4jデータベース

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

# Neo4jからノードとリレーションを取得し、埋め込みを生成してGraphRAGに保存
def create_graphRAG():
    # Neo4jのグラフデータを取得
    query = """
    MATCH (n)-[r]->(m)
    RETURN n.id AS node_id, n.text AS node_text, m.id AS related_node_id, m.text AS related_node_text
    """
    result = source_graph.run(query)

    for record in result:
        node_id = record['node_id']
        node_text = record['node_text']
        related_node_id = record['related_node_id']
        related_node_text = record['related_node_text']

        # 埋め込みを生成
        node_embedding = generate_embedding(node_text)
        related_node_embedding = generate_embedding(related_node_text)

        # GraphRAG用に保存
        save_embedding_to_rag_graph(node_id, node_embedding, node_text)
        save_embedding_to_rag_graph(related_node_id, related_node_embedding, related_node_text)
        save_relationship_to_rag_graph(node_id, related_node_id)

# Neo4j (GraphRAG用) に埋め込みを保存する関数
def save_embedding_to_rag_graph(node_id, embedding_vector, node_text):
    query = """
    MERGE (n:Node {id: $node_id})
    SET n.embedding = $embedding, n.text = $node_text
    """
    rag_graph.run(query, node_id=node_id, embedding=embedding_vector, node_text=node_text)

# ノード間のリレーションを保存する関数
def save_relationship_to_rag_graph(node_id1, node_id2):
    query = """
    MATCH (n1:Node {id: $node_id1}), (n2:Node {id: $node_id2})
    MERGE (n1)-[:RELATED_TO]->(n2)
    """
    rag_graph.run(query, node_id1=node_id1, node_id2=node_id2)

# 実行
create_graphRAG()
