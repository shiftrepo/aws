from neo4j import GraphDatabase
import csv
import os

# ローカルのファイルパス設定
LOCAL_DIRECTORY = './tableAndAp/'  # ローカルディレクトリのパス
LOCAL_KEY_TABLES = 'tables.csv'
LOCAL_KEY_ITEMS = 'items.csv'
LOCAL_KEY_APPLICATIONS = 'applications.csv'
LOCAL_KEY_TABLE_ITEMS = 'table_items.csv'
LOCAL_KEY_ITEM_APPLICATIONS_INPUT = 'item_applications_input.csv'
LOCAL_KEY_APPLICATION_ITEMS_OUTPUT = 'application_items_output.csv'

# Neo4jの設定
NEO4J_URI = 'bolt://neo4j:7687'  # Neo4jのBolt URI
NEO4J_USER = 'neo4j'  # Neo4jのユーザー名
NEO4J_PASSWORD = 'password'  # Neo4jのパスワード

def load_csv_from_local(file_name):
    file_path = os.path.join(LOCAL_DIRECTORY, file_name)
    with open(file_path, mode='r', encoding='utf-8') as file:
        return list(csv.DictReader(file))  # CSV内容をメモリに全て読み込む

def create_nodes_and_relationships(tx):
    # テーブルノードの作成
    tables_reader = load_csv_from_local(LOCAL_KEY_TABLES)
    for row in tables_reader:
        tx.run("MERGE (t:テーブル {テーブルID: $テーブルID, 名前: $テーブル名})", row)

    # 項目ノードの作成
    items_reader = load_csv_from_local(LOCAL_KEY_ITEMS)
    for row in items_reader:
        tx.run("MERGE (i:項目 {項目ID: $項目ID, 名前: $項目名})", row)

    # アプリケーションノードの作成
    applications_reader = load_csv_from_local(LOCAL_KEY_APPLICATIONS)
    for row in applications_reader:
        tx.run("MERGE (a:アプリケーション {アプリケーションID: $アプリケーションID, 名前: $アプリケーション名})", row)

    # テーブル - (保持する) -> 項目のリレーションシップ作成
    table_items_reader = load_csv_from_local(LOCAL_KEY_TABLE_ITEMS)
    for row in table_items_reader:
        tx.run("""
            MATCH (t:テーブル {テーブルID: $テーブルID})
            MATCH (i:項目 {項目ID: $項目ID})
            CREATE (t)-[:保持する]->(i)
        """, row)

    # 項目 - (入力) -> アプリケーションのリレーションシップ作成
    item_applications_input_reader = load_csv_from_local(LOCAL_KEY_ITEM_APPLICATIONS_INPUT)
    for row in item_applications_input_reader:
        tx.run("""
            MATCH (i:項目 {項目ID: $項目ID})
            MATCH (a:アプリケーション {アプリケーションID: $アプリケーションID})
            CREATE (i)-[:入力]->(a)
        """, row)

    # アプリケーション - (出力) -> 項目のリレーションシップ作成
    application_items_output_reader = load_csv_from_local(LOCAL_KEY_APPLICATION_ITEMS_OUTPUT)
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
        print("Data loaded successfully from local files to Neo4j.")
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        driver.close()

