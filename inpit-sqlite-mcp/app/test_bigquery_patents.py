#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQuery特許データ総合テスト

このスクリプトは、BigQuery特許データへの接続とデータ取得、ファミリー構築の
テストを行います。
"""

import os
import logging
import sqlite3
from google_patents_fetcher import GooglePatentsFetcher

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLiteデータベースのパス
DB_PATH = os.path.join(os.path.dirname(__file__), "test_patents_full.db")

def test_patents_full():
    """BigQuery特許データの総合テスト"""
    logger.info("BigQuery特許データ総合テストを開始します...")
    
    # GooglePatentsFetcherを初期化（S3から認証情報を取得）
    fetcher = GooglePatentsFetcher(db_path=DB_PATH)
    
    # BigQueryクライアントが正しく初期化されたことを確認
    if not fetcher.client:
        logger.error("BigQueryクライアントの初期化に失敗しました")
        return False
    
    # テスト1: 単純なクエリテスト
    try:
        logger.info("テスト1: BigQueryへの単純なクエリを実行します")
        query = """
        SELECT COUNT(*) as count
        FROM `patents-public-data.patents.publications`
        WHERE country_code = 'JP'
        """
        
        query_job = fetcher.client.query(query)
        results = list(query_job)
        
        if results:
            count = results[0].get('count')
            logger.info(f"日本国特許の総数: {count}")
            logger.info("✅ テスト1: 単純なクエリテストが成功しました")
        else:
            logger.error("❌ テスト1: クエリ結果を取得できませんでした")
            return False
    except Exception as e:
        logger.error(f"❌ テスト1: エラーが発生しました: {e}")
        return False
    
    # テスト2: 特許データの取得
    try:
        logger.info("テスト2: 特許データを取得してSQLiteデータベースに格納します")
        # 少ない件数でテスト
        count = fetcher.fetch_japanese_patents(limit=15)
        
        if count > 0:
            logger.info(f"特許データの取得成功: {count}件")
            logger.info("✅ テスト2: 特許データ取得テストが成功しました")
        else:
            logger.error("❌ テスト2: 特許データを取得できませんでした")
            return False
    except Exception as e:
        logger.error(f"❌ テスト2: エラーが発生しました: {e}")
        return False
    
    # テスト3: データベースのデータ確認
    try:
        logger.info("テスト3: SQLiteデータベースのデータを確認します")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 特許データの確認
        cursor.execute("SELECT COUNT(*) FROM publications")
        pub_count = cursor.fetchone()[0]
        logger.info(f"特許公開データ数: {pub_count}件")
        
        # ファミリーデータの確認
        cursor.execute("SELECT COUNT(*) FROM patent_families")
        family_count = cursor.fetchone()[0]
        logger.info(f"特許ファミリーデータ数: {family_count}件")
        
        # ファミリーIDの確認
        cursor.execute("SELECT COUNT(DISTINCT family_id) FROM patent_families")
        unique_family_count = cursor.fetchone()[0]
        logger.info(f"固有の特許ファミリーID数: {unique_family_count}件")
        
        # サンプルデータの表示
        cursor.execute("""
        SELECT p.publication_number, p.title_ja, p.family_id, 
               COUNT(f.publication_number) as family_members
        FROM publications p
        JOIN patent_families f ON p.family_id = f.family_id
        GROUP BY p.publication_number
        LIMIT 3
        """)
        
        samples = cursor.fetchall()
        logger.info("サンプルデータ:")
        for sample in samples:
            pub_number, title, family_id, family_size = sample
            logger.info(f"  - {pub_number}: {title} (ファミリーID: {family_id}, メンバー数: {family_size})")
        
        conn.close()
        logger.info("✅ テスト3: データベース確認テストが成功しました")
    except Exception as e:
        logger.error(f"❌ テスト3: エラーが発生しました: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_patents_full()
    if success:
        print("\n✅ BigQuery特許データ総合テストが成功しました")
        print(f"SQLiteデータベース: {DB_PATH}")
    else:
        print("\n❌ BigQuery特許データ総合テストに失敗しました")
