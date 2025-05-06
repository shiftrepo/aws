#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQuery・SQLiteインポートテスト

このスクリプトは、BigQueryに接続し、日本の特許データを取得して
SQLiteデータベースに格納するテストを行います。
"""

import os
import logging
import sqlite3
import tempfile
import boto3
from google.cloud import bigquery
from google.oauth2 import service_account

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLiteデータベースのパス
DB_PATH = os.environ.get("SQLITE_DB_PATH", "patent_data.db")


def test_bigquery_connection():
    """
    BigQuery接続テスト
    """
    client = None
    temp_credentials_path = None
    
    try:
        # 環境変数から認証情報ファイルのパスを取得
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path and os.path.exists(credentials_path):
            logger.info(f"環境変数から認証情報を使用します: {credentials_path}")
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=["https://www.googleapis.com/auth/bigquery"]
                )
                client = bigquery.Client(credentials=credentials, project=credentials.project_id)
                logger.info("認証情報を使用してBigQueryクライアントを初期化しました")
            except Exception as e:
                logger.error(f"認証情報の初期化エラー: {e}")
                return None
        else:
            logger.warning(f"認証情報ファイルが見つかりません。AWS S3からの取得を試みることもできますが、AWS認証情報が必要です。")
            return None

        if client:
            # テストクエリを実行
            query = """
            SELECT
                COUNT(*) as count
            FROM
                `patents-public-data.patents.publications`
            WHERE
                country_code = 'JP'
            LIMIT 1
            """
            
            logger.info("BigQueryにテストクエリを実行しています...")
            query_job = client.query(query)
            results = list(query_job)
            
            if results:
                logger.info(f"クエリ結果: 日本国特許の数 = {results[0].get('count')}")
                return client
            else:
                logger.warning("クエリ結果が空です")
                return None
    
    except Exception as e:
        logger.error(f"BigQuery接続テスト中にエラーが発生しました: {e}")
        return None


def create_database_schema(db_path):
    """
    SQLiteデータベースのスキーマを作成
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create publications table for patent data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            publication_number TEXT PRIMARY KEY,
            filing_date TEXT,
            publication_date TEXT,
            application_number TEXT,
            assignee TEXT,
            title TEXT,
            abstract TEXT,
            ipc_code TEXT,
            family_id TEXT,
            country_code TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("データベーススキーマが作成されました")
        return True
    except Exception as e:
        logger.error(f"データベーススキーマの作成エラー: {e}")
        return False


def fetch_and_store_patents(client, db_path, limit=10):
    """
    BigQueryから特許データを取得してSQLiteに格納
    """
    try:
            # クエリを構築（実行時にパラメータを決定）
        query = f"""
        SELECT
            p.publication_number,
            p.filing_date,
            p.publication_date,
            p.application_number,
            ARRAY_TO_STRING(p.assignee_harmonized, '; ') as assignee,
            ARRAY_TO_STRING(p.title_localized.ja, ' ') as title,
            ARRAY_TO_STRING(p.abstract_localized.ja, ' ') as abstract,
            ARRAY_TO_STRING(p.ipc, '; ') as ipc_code,
            p.family_id,
            p.country_code
        FROM
            `patents-public-data.patents.publications` p
        LIMIT
            {limit}
        """
        
        logger.info(f"BigQueryから日本の特許データを{limit}件取得します...")
        query_job = client.query(query)
        
        # データベース接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # データ取得とSQLiteへの格納
        count = 0
        for row in query_job:
            # 行を辞書に変換
            patent_data = dict(row.items())
            
            # Noneの処理
            for key, value in patent_data.items():
                if value is None:
                    patent_data[key] = ""
            
            # 挿入用タプルの準備
            insertion_tuple = (
                patent_data.get('publication_number', ''),
                patent_data.get('filing_date', ''),
                patent_data.get('publication_date', ''),
                patent_data.get('application_number', ''),
                patent_data.get('assignee', ''),
                patent_data.get('title', ''),
                patent_data.get('abstract', ''),
                patent_data.get('ipc_code', ''),
                patent_data.get('family_id', ''),
                patent_data.get('country_code', '')
            )
            
            # データの挿入
            cursor.execute(
                '''
                INSERT OR REPLACE INTO publications
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                insertion_tuple
            )
            count += 1
        
        conn.commit()
        
        # 取得したデータのサンプル表示
        cursor.execute("SELECT publication_number, title, publication_date FROM publications LIMIT 3")
        samples = cursor.fetchall()
        logger.info("取得データのサンプル:")
        for sample in samples:
            pub_number, title, date = sample
            logger.info(f"  - {pub_number}: {title} ({date})")
        
        conn.close()
        logger.info(f"{count}件の特許データをSQLiteに格納しました")
        return count
    except Exception as e:
        logger.error(f"特許データの取得と格納中にエラーが発生しました: {e}")
        return 0


if __name__ == "__main__":
    print("BigQueryからSQLiteへのデータ取得テストを開始します...")
    
    # BigQueryへの接続をテスト
    client = test_bigquery_connection()
    
    if client:
        print("✅ BigQueryへの接続に成功しました")
        
        # データベーススキーマの作成
        if create_database_schema(DB_PATH):
            # 特許データの取得と格納
            count = fetch_and_store_patents(client, DB_PATH, limit=10)
            
            if count > 0:
                print(f"\n✅ {count}件の特許データをSQLiteデータベースに格納しました")
                print(f"データベースファイル: {DB_PATH}")
                
                # SQLiteデータベースの内容確認
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM publications")
                total = cursor.fetchone()[0]
                print(f"データベース内の特許データ総数: {total}件")
                
                print("\nSQLiteデータベースからのクエリ例:")
                cursor.execute("SELECT publication_number, title, publication_date FROM publications LIMIT 3")
                for row in cursor.fetchall():
                    print(f"特許番号: {row[0]}, タイトル: {row[1]}, 公開日: {row[2]}")
                
                conn.close()
            else:
                print("\n❌ 特許データの取得または格納に失敗しました")
        else:
            print("\n❌ SQLiteデータベーススキーマの作成に失敗しました")
    else:
        print("\n❌ BigQueryへの接続に失敗しました")
        print("正しい認証情報が設定されているか確認してください")
