#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQuery TABLE探索テスト

このスクリプトは、BigQueryのテーブル構造を確認し、
特にfamiliesテーブルの存在を確認します。
"""

import os
import logging
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

def test_bigquery_tables():
    """
    BigQueryのテーブル構造を確認する
    """
    client = None
    temp_credentials_path = None
    
    # S3 bucket and key for GCP credentials from environment variables or defaults
    s3_bucket = os.environ.get('GCP_CREDENTIALS_S3_BUCKET', 'ndi-3supervision')
    s3_key = os.environ.get('GCP_CREDENTIALS_S3_KEY', 'MIT/GCPServiceKey/tosapi-bf0ac4918370.json')
    
    logger.info(f"S3から認証情報を取得します: バケット={s3_bucket}, キー={s3_key}")
    
    try:
        # S3から認証情報を取得
        s3_client = boto3.client('s3')
        
        # 一時ファイルに認証情報を保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_credentials_path = temp_file.name
        
        # 認証情報をS3からダウンロード
        s3_client.download_file(s3_bucket, s3_key, temp_credentials_path)
        logger.info(f"認証情報を一時ファイル {temp_credentials_path} にダウンロードしました")
        
        # 認証情報を使用してBigQueryクライアントを初期化
        if os.path.exists(temp_credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                temp_credentials_path,
                scopes=["https://www.googleapis.com/auth/bigquery"]
            )
            client = bigquery.Client(credentials=credentials, project=credentials.project_id)
            logger.info(f"BigQueryクライアントを初期化しました")
        else:
            logger.error(f"ダウンロードした認証情報ファイルが見つかりません: {temp_credentials_path}")
            return False
    except Exception as e:
        logger.error(f"S3からの認証情報取得エラー: {e}")
        return False

    try:
        # データセット一覧を取得
        logger.info("BigQueryのデータセット一覧を取得します...")
        datasets = list(client.list_datasets(project='patents-public-data'))
        
        logger.info(f"プロジェクト patents-public-data には {len(datasets)} 個のデータセットがあります:")
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            logger.info(f"- データセット: {dataset_id}")
            
            # データセット内のテーブル一覧を取得
            tables = list(client.list_tables(f"patents-public-data.{dataset_id}"))
            logger.info(f"  テーブル数: {len(tables)}")
            
            for table in tables:
                logger.info(f"  - テーブル: {table.table_id}")
                
                # テーブルスキーマを取得
                if dataset_id == 'patents' and table.table_id == 'publications':
                    logger.info("patents.publications テーブルの詳細を取得します...")
                    table_ref = client.get_table(f"patents-public-data.{dataset_id}.{table.table_id}")
                    logger.info(f"行数: {table_ref.num_rows}")
                    logger.info("スキーマ:")
                    for field in table_ref.schema:
                        logger.info(f"  - {field.name}: {field.field_type}")
        
        # familiesテーブルの特定検索
        try:
            logger.info("patents.families テーブルの存在を確認します...")
            families_ref = client.get_table("patents-public-data.patents.families")
            logger.info(f"patents.families テーブルが存在します。行数: {families_ref.num_rows}")
            logger.info("スキーマ:")
            for field in families_ref.schema:
                logger.info(f"  - {field.name}: {field.field_type}")
        except Exception as e:
            logger.error(f"patents.families テーブルの取得に失敗しました: {e}")
            logger.info("patents.publications テーブルからfamily情報を取得する方法を検討します...")
            
            # familiesテーブルが無い場合の確認クエリ
            query = """
            SELECT
                family_id,
                COUNT(*) as family_size
            FROM
                `patents-public-data.patents.publications`
            WHERE
                family_id IS NOT NULL
            GROUP BY 
                family_id
            ORDER BY 
                family_size DESC
            LIMIT 5
            """
            
            logger.info("family_id に基づくファミリーサイズのテストクエリを実行しています...")
            query_job = client.query(query)
            results = list(query_job)
            
            if results:
                logger.info("ファミリー情報のサンプル:")
                for row in results:
                    logger.info(f"ファミリーID: {row.family_id}, サイズ: {row.family_size}")
                logger.info("publications テーブルの family_id フィールドを使用してファミリー関係を構築できます")
            else:
                logger.warning("ファミリー情報が取得できませんでした")
            
        return True
    
    except Exception as e:
        logger.error(f"BigQueryのテーブル構造確認中にエラーが発生しました: {e}")
        return False
    finally:
        # 一時ファイルの削除
        if temp_credentials_path and os.path.exists(temp_credentials_path):
            try:
                os.unlink(temp_credentials_path)
                logger.info("一時認証情報ファイルを削除しました")
            except Exception as e:
                logger.warning(f"一時ファイル削除時にエラー: {e}")

if __name__ == "__main__":
    success = test_bigquery_tables()
    if success:
        print("\n✅ BigQueryのテーブル構造確認が完了しました")
    else:
        print("\n❌ BigQueryのテーブル構造確認中にエラーが発生しました")
