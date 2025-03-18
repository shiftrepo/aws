import os
from neo4j import GraphDatabase

# 環境変数からNeo4jの接続設定を取得
NEO4J_URI = os.environ.get("TARGET_NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.environ.get("TARGET_NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("TARGET_NEO4J_PASSWORD", "password")

class Neo4jRecursiveSearch:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def recursive_relationships(self, start_label, start_property_key, start_property_value, depth=None):
        """
        再帰的に関連を検索するメソッド。
        :param start_label: 開始ノードのラベル (例: 'テーブル')
        :param start_property_key: 開始ノードのプロパティキー (例: 'テーブルID')
        :param start_property_value: 開始ノードのプロパティ値 (例: 'table1')
        :param depth: 探索する深さ (例: 3, 無制限の場合は None)
        :return: 関連するパスリスト
        """
        with self.driver.session() as session:
            # 再帰的なクエリを構築
            depth_specifier = f"*1..{depth}" if depth else "*"
            query = f"""
            MATCH path = (start:{start_label} {{ {start_property_key}: $start_property_value }})-[*]-()
            RETURN path
            """
            print(f"Debug Query: {query}")  # クエリをデバッグ出力
            result = session.run(query, start_property_value=start_property_value)
            paths = [record["path"] for record in result]
            return paths

# 再帰的検索を実行する部分
if __name__ == "__main__":
    neo4j_recursive = Neo4jRecursiveSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # ユーザー入力を動的に受け取る
        print("\n--- 再帰的な関連検索 ---")
        start_label = input("開始ノードのラベルを入力してください（例: テーブル）: ").strip()
        start_property_key = input("開始ノードのプロパティキーを入力してください（例: テーブルID）: ").strip()
        start_property_value = input("開始ノードのプロパティ値を入力してください: ").strip()
        depth = input("検索の深さを入力してください（無制限の場合は空でOK）: ").strip()
        depth = int(depth) if depth.isdigit() else None

        # 再帰的検索の実行
        paths = neo4j_recursive.recursive_relationships(
            start_label=start_label,
            start_property_key=start_property_key,
            start_property_value=start_property_value,
            depth=depth
        )

        # 検索結果の表示
        print("\n--- 検索結果: 再帰的な関連 ---")
        if paths:
            for path in paths:
                print(f"Found Path: {path}")
        else:
            print("該当する関連は見つかりませんでした。")

    finally:
        neo4j_recursive.close()

