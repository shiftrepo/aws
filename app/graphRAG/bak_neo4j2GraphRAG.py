import os
from neo4j import GraphDatabase
import boto3
import json

# 環境変数から設定情報を取得
SOURCE_NEO4J_URI = os.environ.get("SOURCE_NEO4J_URI", "bolt://neo4j:7687")
SOURCE_NEO4J_USER = os.environ.get("SOURCE_NEO4J_USER", "neo4j")
SOURCE_NEO4J_PASSWORD = os.environ.get("SOURCE_NEO4J_PASSWORD", "password")

TARGET_NEO4J_URI = os.environ.get("TARGET_NEO4J_URI", "bolt://neo4jRAG:7687")
TARGET_NEO4J_USER = os.environ.get("TARGET_NEO4J_USER", "neo4j")
TARGET_NEO4J_PASSWORD = os.environ.get("TARGET_NEO4J_PASSWORD", "password")

# Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")  # 例: 米国東部リージョン

# デバッグログ
print(f"SOURCE_NEO4J_URI: {SOURCE_NEO4J_URI}")
print(f"SOURCE_NEO4J_USER: {SOURCE_NEO4J_USER}")
print(f"SOURCE_NEO4J_PASSWORD: {SOURCE_NEO4J_PASSWORD}")
print(f"TARGET_NEO4J_URI: {TARGET_NEO4J_URI}")
print(f"TARGET_NEO4J_USER: {TARGET_NEO4J_USER}")
print(f"TARGET_NEO4J_PASSWORD: {TARGET_NEO4J_PASSWORD}")
print(f"AWS_REGION: {AWS_REGION}")

# AWSクライアントの初期化
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def get_all_nodes_and_relationships(uri, user, password):
    """既存のNeo4jから全てのノードとリレーションシップを取得する"""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        def work(tx):
            query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, collect(r) as relationships
            """
            result = tx.run(query)
            data = []
            for record in result:
                print(f"Debug record: {record}")  # デバッグ用ログ
                node = record.get("n")
                relationships = record.get("relationships", [])
                data.append({"node": node, "relationships": relationships})
            return data
        with driver.session() as session:
            return session.execute_read(work)
    finally:
        driver.close()

def create_embedding(text):
    """Amazon Titan Embeddingsでテキストのベクトル表現を作成する"""
    body = json.dumps({"inputText": text})
    modelId = 'amazon.titan-embed-text-v2:0'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    embedding = response_body.get('embedding')
    return embedding

def store_graph_with_embeddings(uri, user, password, graph_data):
    """GraphRAG用のNeo4jにグラフデータとエンベディングを格納する"""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        def work(tx):
            for record in graph_data:
                # ノードを取得
                node = record.get("node")
                if not node:
                    print("No node found in record.")
                    continue

                # ノードのデバッグ
                print(f"Debug node: {node}")

                # プロパティを明確化して取得
                node_props = node._properties if hasattr(node, '_properties') else {}
                if not node_props:
                    print(f"No properties found for node: {node}")
                    continue

                # 必須プロパティの確認 (テーブルIDが空の場合スキップ)
                table_id = node_props.get('テーブルID', None)
                if not table_id:
                    print(f"Skipping node with missing or empty テーブルID: {node_props}")
                    continue

                # ノードラベルとリレーションシップ
                node_labels = list(node.labels) if hasattr(node, 'labels') else []
                relationships = record.get("relationships", [])

                # エンベディング対象のテキストを生成
                embedding_text = " ".join(str(value) for value in node_props.values())
                embedding = None
                if embedding_text:
                    embedding = create_embedding(embedding_text)
                    node_props["embedding"] = embedding  # エンベディングをプロパティに追加

                # ノードの作成または更新
                node_label_str = ":".join(node_labels)
                create_node_query = f"""
                MERGE (n:{node_label_str} {{テーブルID: }})
                SET n += 
                """
                print(f"Debug create_node_query: {create_node_query}")  # デバッグ用出力
                print(f"Debug props: {node_props}")  # デバッグ用出力

                tx.run(create_node_query, table_id=table_id, props=node_props)

                # リレーションシップの作成
                for rel in relationships:
                    start_node_id = rel.get("startNodeId")
                    end_node_id = rel.get("endNodeId")
                    rel_type = rel.get("type")
                    rel_props = rel.get("properties", {})
                    if start_node_id is not None and end_node_id is not None and rel_type:
                        create_rel_query = f"""
                        MATCH (start), (end)
                        WHERE id(start) =  AND id(end) = 
                        CREATE (start)-[r:{rel_type}]->(end)
                        SET r = 
                        """
                        tx.run(create_rel_query, start_id=start_node_id, end_id=end_node_id, rel_props=rel_props)
        with driver.session() as session:
            session.execute_write(work)
        print("Graph data with embeddings stored successfully in the target Neo4j.")
    finally:
        driver.close()

if __name__ == "__main__":
    print("Fetching graph data from the source Neo4j...")
    graph_data = get_all_nodes_and_relationships(SOURCE_NEO4J_URI, SOURCE_NEO4J_USER, SOURCE_NEO4J_PASSWORD)
    print(f"Fetched {len(graph_data)} nodes and their relationships.")

    print("Creating embeddings and storing data in the target Neo4j...")
    store_graph_with_embeddings(TARGET_NEO4J_URI, TARGET_NEO4J_USER, TARGET_NEO4J_PASSWORD, graph_data)
