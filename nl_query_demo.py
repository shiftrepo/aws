#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQueryデータを使用した自然言語クエリのデモ

このスクリプトはBigQueryから取得した特許データに対して、
自然言語による問い合わせを行い、SQLiteデータベースから結果を取得します。
"""

import os
import sqlite3
import logging
import sys
import argparse

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# データベースパス - 環境変数から取得、または引数で指定
DB_PATH = os.environ.get("SQLITE_DB_PATH", "patent_data.db")


def import_nl_processor():
    """動的にNL処理モジュールをインポート"""
    try:
        sys.path.append(os.path.abspath('.'))
        # 相対パスでインポートを試みる
        from inpit_sqlite_mcp.app.nl_query_processor import PatentNLQueryProcessor
        return PatentNLQueryProcessor
    except ImportError:
        try:
            # プロジェクトルートにある場合のパス
            sys.path.append(os.path.join(os.path.dirname(__file__), 'inpit-sqlite-mcp', 'app'))
            from nl_query_processor import PatentNLQueryProcessor
            return PatentNLQueryProcessor
        except ImportError:
            logger.error("nl_query_processorモジュールをインポートできません")
            return None


def import_patents_fetcher():
    """動的にPatentsFetcherモジュールをインポート"""
    try:
        sys.path.append(os.path.abspath('.'))
        # 相対パスでインポートを試みる
        from inpit_sqlite_mcp.app.google_patents_fetcher import GooglePatentsFetcher
        return GooglePatentsFetcher
    except ImportError:
        try:
            # プロジェクトルートにある場合のパス
            sys.path.append(os.path.join(os.path.dirname(__file__), 'inpit-sqlite-mcp', 'app'))
            from google_patents_fetcher import GooglePatentsFetcher
            return GooglePatentsFetcher
        except ImportError:
            logger.error("google_patents_fetcherモジュールをインポートできません")
            return None


def setup_database(limit):
    """
    BigQueryから特許データを取得しSQLiteに格納
    
    Args:
        limit: 取得する特許データの件数
    """
    logger.info(f"BigQueryから特許データを{limit}件取得してSQLiteに格納します...")
    
    # 必要なモジュールをインポート
    GooglePatentsFetcher = import_patents_fetcher()
    if not GooglePatentsFetcher:
        return False
    
    try:
        # GooglePatentsFetcherを初期化
        fetcher = GooglePatentsFetcher(db_path=DB_PATH)
        
        # BigQueryクライアントが正常に初期化されたか確認
        if not fetcher.client:
            logger.error("BigQueryクライアントの初期化に失敗しました")
            return False
        
        # 特許データを取得
        count = fetcher.fetch_japanese_patents(limit=limit)
        
        if count > 0:
            logger.info(f"成功: {count}件の特許データをSQLiteデータベースに格納しました")
            return True
        else:
            logger.error("特許データの取得に失敗しました")
            return False
    except Exception as e:
        logger.error(f"データベース設定中にエラーが発生しました: {e}")
        return False


def display_database_info():
    """データベースの基本情報を表示"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # テーブル一覧を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("\nデータベース内のテーブル:")
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
            
            # テーブルのカラム情報を取得
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("  カラム:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  - {col_name} ({col_type}){' PRIMARY KEY' if pk else ''}")
            
            # 各テーブルの行数を取得
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  行数: {row_count}")
            print()
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"データベース情報表示中にエラー: {e}")
        return False


def process_natural_language_query(query):
    """
    自然言語クエリを処理
    
    Args:
        query: 処理する自然言語クエリ
    """
    # 必要なモジュールをインポート
    PatentNLQueryProcessor = import_nl_processor()
    if not PatentNLQueryProcessor:
        print("自然言語処理モジュールをロードできません")
        return False
    
    try:
        # 自然言語クエリプロセッサを初期化
        processor = PatentNLQueryProcessor(db_path=DB_PATH)
        
        print(f"\n=== 自然言語クエリ: \"{query}\" ===")
        
        # クエリを処理してSQL変換
        processed = processor.process_query(query)
        sql_query = processed["sql_query"]
        print(f"変換されたSQL: {sql_query}")
        
        # SQLクエリを実行
        result = processor.execute_query(sql_query)
        
        if result.get("success", False):
            found = result.get("count", 0)
            print(f"{found}件の結果が見つかりました")
            
            # 結果を表示（最大5件まで）
            max_results = min(5, found)
            for i, patent in enumerate(result.get("results", [])[:max_results]):
                print(f"\n結果 {i+1}:")
                for key, value in patent.items():
                    # 重要なフィールドのみ表示
                    if key in ['publication_number', 'title_ja', 'title_en', 'abstract_ja', 
                              'publication_date', 'assignee_harmonized']:
                        print(f"  {key}: {value}")
            
            return True
        else:
            print(f"クエリの実行に失敗しました: {result.get('error', '不明なエラー')}")
            return False
    except Exception as e:
        print(f"自然言語クエリの処理中にエラーが発生しました: {e}")
        return False


def interactive_mode():
    """インタラクティブモードでユーザーからのクエリを処理"""
    print("\n=== 自然言語特許クエリシステム ===")
    print("特許データに対して自然言語で問い合わせができます")
    print("例: 「電気自動車に関する特許を検索」、「最新の特許を5件表示」など")
    print("終了するには 'exit' または 'quit' と入力してください")
    
    while True:
        try:
            query = input("\n自然言語クエリ> ")
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            process_natural_language_query(query)
        except KeyboardInterrupt:
            print("\n終了します...")
            break


if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='自然言語による特許検索')
    parser.add_argument('-d', '--db', type=str, help='SQLiteデータベースのパス')
    parser.add_argument('-i', '--import_data', action='store_true', help='BigQueryからデータをインポート')
    parser.add_argument('-l', '--limit', type=int, default=20, help='インポートする特許データの件数')
    parser.add_argument('-q', '--query', type=str, help='処理する自然言語クエリ')
    parser.add_argument('-s', '--show_info', action='store_true', help='データベース情報を表示')
    
    args = parser.parse_args()
    
    # データベースパスの設定
    if args.db:
        DB_PATH = args.db
        print(f"データベースパスを設定: {DB_PATH}")
    
    # データのインポート
    if args.import_data:
        if setup_database(args.limit):
            print(f"✅ {args.limit}件のデータをインポートしました")
        else:
            print("❌ データのインポートに失敗しました")
            sys.exit(1)
    
    # データベース情報の表示
    if args.show_info:
        display_database_info()
    
    # 単一クエリの実行
    if args.query:
        process_natural_language_query(args.query)
        sys.exit(0)
    
    # 引数がない場合はインタラクティブモード
    if not (args.import_data or args.show_info or args.query):
        interactive_mode()
