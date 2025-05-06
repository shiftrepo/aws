#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BigQuery接続テスト

このスクリプトはS3から認証情報を取得し、BigQueryに接続してデータを取得できるかテストします。
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

def test_bigquery_connection():
    """
    S3から認証情報を取得し、BigQueryに接続してデータを取得するテスト
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
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    temp_credentials_path,
                    scopes=["https://www.googleapis.com/auth/bigquery"]
                )
                client = bigquery.Client(credentials=credentials, project=credentials.project_id)
                logger.info(f"S3から取得した認証情報を使用してBigQueryクライアントを初期化しました")
            except Exception as e:
                logger.error(f"認証情報の初期化エラー: {e}")
                return False
        else:
            logger.error(f"ダウンロードした認証情報ファイルが見つかりません: {temp_credentials_path}")
            return False
    except Exception as e:
        logger.error(f"S3からの認証情報取得エラー: {e}")
        
        # 環境変数からのフォールバック
        logger.info("環境変数からのフォールバック認証情報を確認します...")
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path:
            logger.info(f"GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されています: {credentials_path}")
            if os.path.exists(credentials_path):
                logger.info("認証情報ファイルが存在します")
                try:
                    credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=["https://www.googleapis.com/auth/bigquery"]
                    )
                    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
                    logger.info(f"フォールバック認証情報を使用してBigQueryクライアントを初期化しました")
                except Exception as e:
                    logger.error(f"フォールバック認証情報の初期化エラー: {e}")
                    return False
            else:
                logger.warning(f"認証情報ファイル {credentials_path} が見つかりません")
                return False
        else:
            logger.error("GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません")
            logger.error("S3から認証情報を取得できず、フォールバック認証情報も利用できません")
            return False

    try:
        # BigQueryにクエリを実行
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
                return True
            else:
                logger.warning("クエリ結果が空です")
                return False
        else:
            logger.error("BigQueryクライアントの初期化に失敗しました")
            return False
    
    except Exception as e:
        logger.error(f"BigQuery接続テスト中にエラーが発生しました: {e}")
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
    success = test_bigquery_connection()
    if success:
        print("✅ BigQueryへの接続とデータ取得が成功しました")
    else:
        print("❌ BigQueryへの接続またはデータ取得に失敗しました")
