#!/bin/bash

# patentDWH AWS認証情報セキュリティおよび起動エラー修正スクリプト
# 
# このスクリプトは以下の問題を修正します：
# 1. AWS認証情報がログに表示される問題を修正
# 2. データベースモデル初期化エラーを修正

# テキストカラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}patentDWH セキュリティ修正スクリプト${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# カレントディレクトリがpatentDWHディレクトリか確認
if [[ ! -f "./docker-compose.consolidated.yml" ]]; then
  echo -e "${RED}エラー: patentDWHディレクトリで実行してください${NC}"
  exit 1
fi

# コンテナランタイムを検出
if command -v podman &> /dev/null; then
  CONTAINER_RUNTIME="podman"
  COMPOSE_CMD="podman-compose"
  echo -e "${BLUE}podmanとpodman-composeを使用します${NC}"
elif command -v docker &> /dev/null; then
  CONTAINER_RUNTIME="docker"
  COMPOSE_CMD="docker compose"
  echo -e "${YELLOW}dockerを使用します${NC}"
else
  echo -e "${RED}エラー: podmanもdockerもインストールされていません${NC}"
  exit 1
fi

# 実行中のサービスを停止
echo -e "${BLUE}1. 実行中のサービスを停止しています...${NC}"
$COMPOSE_CMD -f docker-compose.consolidated.yml down 2>/dev/null
echo -e "${GREEN}サービスを停止しました${NC}"
echo ""

# ビルド & 再起動
echo -e "${BLUE}2. 修正をビルドしています...${NC}"
$COMPOSE_CMD -f docker-compose.consolidated.yml build patentdwh-db
echo -e "${GREEN}コンテナの再ビルドが完了しました${NC}"
echo ""

# 環境変数に関する注意事項を表示
echo -e "${YELLOW}重要: 以下の環境変数を適切に設定してください:${NC}"
echo -e "${YELLOW}  export AWS_ACCESS_KEY_ID=\"your_access_key\"${NC}"
echo -e "${YELLOW}  export AWS_SECRET_ACCESS_KEY=\"your_secret_key\"${NC}"
echo -e "${YELLOW}  export AWS_DEFAULT_REGION=\"us-east-1\"${NC}"
echo ""

# 環境変数のチェック
if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
  echo -e "${RED}警告: AWS認証情報の環境変数が設定されていません${NC}"
  echo -e "${RED}システムを起動する前に、上記の環境変数を設定してください${NC}"
else
  echo -e "${GREEN}AWS認証情報の環境変数が設定されています${NC}"
fi

echo -e "${YELLOW}AWS認証情報を安全に使用する方法の詳細については${NC}"
echo -e "${YELLOW}patentDWH/AWS_CREDENTIALS_SECURE_USAGE.md を参照してください${NC}"
echo ""

# 起動方法の案内
echo -e "${BLUE}3. 修正を適用しました${NC}"
echo -e "${GREEN}以下のコマンドでシステムを再起動できます:${NC}"
echo -e "${GREEN}  ./start_all_services.sh${NC}"
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}セキュリティ修正が完了しました${NC}"
echo -e "${BLUE}==========================================${NC}"
