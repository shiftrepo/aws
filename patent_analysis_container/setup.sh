#!/bin/bash

# Patent Analysis Container - Setup Script

# Function to check if an environment variable is set
check_env_var() {
  if [ -z "${!1}" ]; then
    echo "環境変数 $1 が設定されていません。"
    echo "例: export $1=your_$1_value"
    return 1
  else
    echo "✓ 環境変数 $1 が設定されています。"
    return 0
  fi
}

# Create output directory
mkdir -p output
echo "✓ 出力ディレクトリを作成しました。"

# Check required environment variables
echo "AWS認証情報の確認中..."
aws_creds_ok=true

if ! check_env_var AWS_ACCESS_KEY_ID; then
  aws_creds_ok=false
fi

if ! check_env_var AWS_SECRET_ACCESS_KEY; then
  aws_creds_ok=false
fi

# Region has a default, so it's optional
if [ -z "$AWS_REGION" ]; then
  echo "環境変数 AWS_REGION が設定されていません。デフォルト (us-east-1) を使用します。"
  echo "変更する場合: export AWS_REGION=your_preferred_region"
else
  echo "✓ 環境変数 AWS_REGION が設定されています: $AWS_REGION"
fi

if [ "$aws_creds_ok" = false ]; then
  echo ""
  echo "警告: 一部のAWS認証情報が設定されていません。"
  echo "以下のコマンドを実行して設定してください:"
  echo "export AWS_ACCESS_KEY_ID=your_key_id"
  echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
  echo "export AWS_REGION=your_region  # オプション、デフォルトはus-east-1"
  echo ""
else
  echo "✓ すべての必要な環境変数が設定されています。"
fi

# Ask user if they want to build the container
echo ""
echo "特許分析コンテナをビルドしますか？ (y/n)"
read -r build_choice

if [ "$build_choice" = "y" ] || [ "$build_choice" = "Y" ]; then
  echo "コンテナをビルドしています..."
  docker-compose build
  echo "✓ コンテナのビルドが完了しました。"
else
  echo "コンテナのビルドをスキップしました。"
fi

# Ask user if they want to run an analysis
echo ""
echo "特許出願動向分析を実行しますか？ (y/n)"
read -r run_choice

if [ "$run_choice" = "y" ] || [ "$run_choice" = "Y" ]; then
  echo "分析対象の出願人名を入力してください (例: \"トヨタ\"):"
  read -r applicant_name
  
  echo "データベースタイプを選択してください:"
  echo "1) inpit (デフォルト)"
  echo "2) google_patents_gcp"
  echo "3) google_patents_s3"
  read -r db_choice
  
  case $db_choice in
    2)
      db_type="google_patents_gcp"
      ;;
    3)
      db_type="google_patents_s3"
      ;;
    *)
      db_type="inpit"
      ;;
  esac
  
  echo "分析を実行中... (出願人: $applicant_name, DB: $db_type)"
  docker-compose run patent-analysis "$applicant_name" "$db_type"
  
  echo "✓ 分析が完了しました。結果は output/ ディレクトリに保存されています。"
else
  echo "分析の実行をスキップしました。"
  echo "後で分析を実行する場合は以下のコマンドを使用してください:"
  echo "docker-compose run patent-analysis \"出願人名\" [db_type]"
fi

echo ""
echo "セットアップが完了しました。"
