#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQuery接続とデータインポートのテスト

このスクリプトは、S3から認証情報を取得し、BigQueryから日本の特許データを
少数取得してSQLiteデータベースに格納します。
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
DB_PATH = os.path.join(os.path.dirname(__file__), "test_patents.db")

def test_patent_import():
    """
    S3から認証情報を取得し、BigQueryから少数の日本特許データを取得してSQLiteに格納
    """
    logger.info("BigQueryからの特許データインポートテストを開始します...")
    
    # GooglePatentsFetcherを初期化（S3から認証情報を自動的に取得）
    fetcher = GooglePatentsFetcher(db_path=DB_PATH)
    
    # BigQueryクライアントが正しく初期化されたか確認
    if not fetcher.client:
        logger.error("BigQueryクライアントの初期化に失敗しました")
        return False
    
    # 少数の特許データを取得（速度のため少なめに設定）
    try:
        logger.info("BigQueryから日本の特許データを10件取得します...")
        count = fetcher.fetch_japanese_patents(limit=10)
        
        if count > 0:
            logger.info(f"成功: {count}件の特許データをSQLiteデータベースに格納しました")
            
            # 結果の確認
            logger.info("SQLiteデータベースのデータを確認します...")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 特許データの確認
            cursor.execute("SELECT COUNT(*) FROM publications")
            pub_count = cursor.fetchone()[0]
            logger.info(f"特許公開データ: {pub_count}件")
            
            # 特許データのサンプル表示
            cursor.execute("SELECT publication_number, title_ja, publication_date FROM publications LIMIT 3")
            samples = cursor.fetchall()
            logger.info("データサンプル:")
            for sample in samples:
                pub_number, title, date = sample
                logger.info(f"  - {pub_number}: {title} ({date})")
                
            # ファミリーデータの確認
            cursor.execute("SELECT COUNT(*) FROM patent_families")
            family_count = cursor.fetchone()[0]
            logger.info(f"特許ファミリーデータ: {family_count}件")
            
            conn.close()
            return True
        else:
            logger.error("特許データが取得できませんでした")
            return False
            
    except Exception as e:
        logger.error(f"特許データの取得中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_patent_import()
    if success:
        print("\n✅ BigQueryからのデータ取得とSQLiteへの格納が成功しました")
        print(f"SQLiteデータベース: {DB_PATH}")
    else:
        print("\n❌ BigQueryからのデータ取得またはSQLiteへの格納に失敗しました")
