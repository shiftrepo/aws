#!/bin/bash

# この実行スクリプトはBigQueryからデータを取得し、SQLiteに格納するテストを実行します
# S3からBigQuery認証情報を取得し、日本の特許データを取得してSQLiteに保存します

# 実行権限を付与
chmod +x test_import_patents.py

echo "BigQueryデータインポートテストを開始します..."
echo "認証情報ソース: s3://ndi-3supervision/MIT/GCPServiceKey/tosapi-bf0ac4918370.json"
echo ""

# AWS認証情報の確認
echo "AWS認証情報の設定状況 (S3アクセスに必要):"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "✓ AWS_ACCESS_KEY_ID および AWS_SECRET_ACCESS_KEY が設定されています"
  if [ -n "$AWS_DEFAULT_REGION" ]; then
    echo "✓ AWS_DEFAULT_REGION が設定されています: $AWS_DEFAULT_REGION"
  else
    echo "- AWS_DEFAULT_REGION が設定されていません。デフォルトで ap-northeast-1 を使用します"
    export AWS_DEFAULT_REGION=ap-northeast-1
  fi
else
  echo "✗ AWS認証情報が設定されていません"
  echo "  環境変数を設定する例:"
  echo "    export AWS_ACCESS_KEY_ID=あなたのアクセスキーID"
  echo "    export AWS_SECRET_ACCESS_KEY=あなたのシークレットアクセスキー"
  echo "    export AWS_DEFAULT_REGION=ap-northeast-1"
  echo ""
  echo "テストを続行できないため終了します"
  exit 1
fi

echo ""
echo "特許データインポートテストを実行します..."
python3 test_import_patents.py

# 結果に基づいたメッセージ表示
if [ $? -eq 0 ]; then
  echo ""
  echo "テストが完了しました。データベースファイルが作成されました。"
  echo ""
  echo "次のコマンドで同じテストをdocker-compose環境でも実行できます:"
  echo ""
  echo "  # AWS環境変数のエクスポートとdocker-composeの実行"
  if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "  cd /root/aws.git/inpit-sqlite-mcp/"
    echo "  AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID' AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY' AWS_DEFAULT_REGION='${AWS_DEFAULT_REGION:-ap-northeast-1}' docker-compose up -d"
  fi
  echo ""
else
  echo ""
  echo "テストが失敗しました。詳細はログメッセージを確認してください。"
  echo ""
fi
