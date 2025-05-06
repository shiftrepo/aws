#!/bin/bash

# このスクリプトはBigQuery接続をテストするためのものです
# S3から認証情報を取得し、BigQueryに接続してデータを取得できるかテストします

# 実行権限を付与
chmod +x test_bigquery_connection.py

echo "BigQuery接続テストを開始します..."

echo "S3からBigQuery認証情報を取得してテストを実行します。"
echo "認証情報ソース: s3://ndi-3supervision/MIT/GCPServiceKey/tosapi-bf0ac4918370.json"
echo ""

# 現在の環境変数の設定状態を確認 (フォールバックのため)
echo "フォールバック用環境変数の設定状況 (S3からの取得に失敗した場合に使用):"
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "✓ GOOGLE_APPLICATION_CREDENTIALS が設定されています: $GOOGLE_APPLICATION_CREDENTIALS"
  if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "  ファイルが存在します"
  else
    echo "  ファイルが見つかりません"
  fi
else
  echo "✗ GOOGLE_APPLICATION_CREDENTIALS は設定されていません"
  echo "  S3から認証情報を取得するため、通常の動作には影響しません"
fi

# AWS認証情報と資格情報のS3パスの確認
echo ""
echo "AWS認証情報の設定状況 (S3アクセスに必要):"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "✓ AWS_ACCESS_KEY_ID および AWS_SECRET_ACCESS_KEY が設定されています"
  if [ -n "$AWS_DEFAULT_REGION" ]; then
    echo "✓ AWS_DEFAULT_REGION が設定されています: $AWS_DEFAULT_REGION"
  else
    echo "✗ AWS_DEFAULT_REGION が設定されていません。デフォルトで ap-northeast-1 を使用します"
  fi
else
  echo "✗ AWS認証情報が設定されていません"
  echo "  環境変数を設定する例:"
  echo "    export AWS_ACCESS_KEY_ID=あなたのアクセスキーID"
  echo "    export AWS_SECRET_ACCESS_KEY=あなたのシークレットアクセスキー"
  echo "    export AWS_DEFAULT_REGION=ap-northeast-1"
fi

# GCP認証情報のS3パスの確認
echo ""
echo "GCP認証情報のS3パス設定状況:"
if [ -n "$GCP_CREDENTIALS_S3_BUCKET" ] && [ -n "$GCP_CREDENTIALS_S3_KEY" ]; then
  echo "✓ GCP_CREDENTIALS_S3_BUCKET および GCP_CREDENTIALS_S3_KEY が設定されています:"
  echo "  バケット: $GCP_CREDENTIALS_S3_BUCKET"
  echo "  キー: $GCP_CREDENTIALS_S3_KEY"
else
  echo "✓ GCP_CREDENTIALS_S3_BUCKET または GCP_CREDENTIALS_S3_KEY の一部または両方が設定されていません。"
  echo "  デフォルト値を使用します:"
  echo "  バケット: ndi-3supervision"
  echo "  キー: MIT/GCPServiceKey/tosapi-bf0ac4918370.json"
fi

echo ""
echo "BigQueryテストを実行します..."
python3 test_bigquery_connection.py

# 結果に基づいたメッセージ表示
if [ $? -eq 0 ]; then
  echo ""
  echo "BigQuery接続テストが成功しました。"
  echo "docker-composeを使用して次のように実行できます:"
  echo ""
  echo "  # AWS環境変数のエクスポート (S3アクセスに必要)"
  if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "  export AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID'"
    echo "  export AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY'"
    if [ -n "$AWS_DEFAULT_REGION" ]; then
      echo "  export AWS_DEFAULT_REGION='$AWS_DEFAULT_REGION'"
    else
      echo "  export AWS_DEFAULT_REGION='ap-northeast-1'"
    fi
  else
    echo "  export AWS_ACCESS_KEY_ID='あなたのアクセスキーID'"
    echo "  export AWS_SECRET_ACCESS_KEY='あなたのシークレットアクセスキー'"
    echo "  export AWS_DEFAULT_REGION='ap-northeast-1'"
  fi
  echo ""
  echo "  # docker-composeの実行"
  echo "  cd /root/aws.git/inpit-sqlite-mcp/"
  echo "  docker-compose up -d"
  echo ""
  echo "  # または環境変数を一度に指定してdocker-composeを実行"
  if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "  AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID' AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY' AWS_DEFAULT_REGION='${AWS_DEFAULT_REGION:-ap-northeast-1}' docker-compose up -d"
  fi
  echo ""
else
  echo ""
  echo "BigQuery接続テストが失敗しました。"
  echo "AWS認証情報の設定を確認してください:"
  echo "  export AWS_ACCESS_KEY_ID='あなたのアクセスキーID'"
  echo "  export AWS_SECRET_ACCESS_KEY='あなたのシークレットアクセスキー'"
  echo "  export AWS_DEFAULT_REGION='ap-northeast-1'"
  echo ""
  echo "詳細はログメッセージを参照してください。"
fi
