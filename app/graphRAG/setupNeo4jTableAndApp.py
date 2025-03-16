import boto3
from neo4j import GraphDatabase
import csv
import io

# S3の設定
S3_BUCKET_NAME = 'ndi-3supervision'
S3_KEY_TABLES = 'MIT/demo/neo4j/tableAndAp/tables.csv'
S3_KEY_ITEMS = 'MIT/demo/neo4j/tableAndAp/items.csv'
S3_KEY_APPLICATIONS = 'MIT/demo/neo4j/tableAndAp/applications.csv'
S3_KEY_TABLE_ITEMS = 'MIT/demo/neo4j/tableAndAp/table_items.csv'
S3_KEY_ITEM_APPLICATIONS_INPUT = 'MIT/demo/neo4j/tableAndAp/item_applications_input.csv'
S3_KEY_APPLICATION_ITEMS_OUTPUT = 'MIT/demo/neo4j/tableAndAp/application_items_output.csv'

# Neo4jの設定
NEO4J_URI = 'bolt://neo4j:7687'  # Neo4jのBolt URI
NEO4J_USER = 'neo4j'  # Neo4jのユーザー名
NEO4J_PASSWORD = 'password'  # Neo4jのパスワード

def load_csv_from_s3(bucket_name, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)
    csv_data = response['Body'].read().decode('utf-8')
    return csv.DictReader(io.StringIO(csv_data))

def create_nodes_and_relationships(tx):
    # テーブルノードの作成
    tables_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_TABLES)
    for row in tables_reader:
        tx.run("MERGE (t:テーブル {テーブルID: $テーブルID, 名前: $テーブル名})", row)

    # 項目ノードの作成
    items_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_ITEMS)
    for row in items_reader:
        tx.run("MERGE (i:項目 {項目ID: $項目ID, 名前: $項目名})", row)

    # アプリケーションノードの作成
    applications_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_APPLICATIONS)
    for row in applications_reader:
        tx.run("MERGE (a:アプリケーション {アプリケーションID: $アプリケーションID, 名前: $アプリケーション名})", row)

    # テーブル - (保持する) -> 項目のリレーションシップ作成
    table_items_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_TABLE_ITEMS)
    for row in table_items_reader:
        tx.run("""
            MATCH (t:テーブル {テーブルID: $テーブルID})
            MATCH (i:項目 {項目ID: $項目ID})
            CREATE (t)-[:保持する]->(i)
        """, row)

    # 項目 - (入力) -> アプリケーションのリレーションシップ作成
    item_applications_input_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_ITEM_APPLICATIONS_INPUT)
    for row in item_applications_input_reader:
        tx.run("""
            MATCH (i:項目 {項目ID: $項目ID})
            MATCH (a:アプリケーション {アプリケーションID: $アプリケーションID})
            CREATE (i)-[:入力]->(a)
        """, row)

    # アプリケーション - (出力) -> 項目のリレーションシップ作成
    application_items_output_reader = load_csv_from_s3(S3_BUCKET_NAME, S3_KEY_APPLICATION_ITEMS_OUTPUT)
    for row in application_items_output_reader:
        tx.run("""
            MATCH (a:アプリケーション {アプリケーションID: $アプリケーションID})
            MATCH (i:項目 {項目ID: $項目ID})
            CREATE (a)-[:出力]->(i)
        """, row)

if __name__ == "__main__":
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            session.execute_write(create_nodes_and_relationships)
        print("Data loaded successfully from S3 to Neo4j.")
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        driver.close()
