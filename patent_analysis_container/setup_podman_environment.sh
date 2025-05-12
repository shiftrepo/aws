#!/bin/bash

# このスクリプトはpodman-compose環境をセットアップし、特許分析MCPコンテナを使用するための準備をします

# カラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo "======================================================"
echo "  Podman特許分析環境セットアップ"
echo "======================================================"
echo ""

# podman-composeが利用可能か確認
if ! command -v podman-compose &> /dev/null; then
  echo -e "${RED}エラー: podman-composeがインストールされていません${NC}"
  echo "podman-composeをインストールしてください"
  exit 1
fi

# podmanが利用可能か確認
if ! command -v podman &> /dev/null; then
  echo -e "${RED}エラー: podmanがインストールされていません${NC}"
  echo "podmanをインストールしてください"
  exit 1
fi

# スクリプトを実行可能にする
echo -e "${BLUE}スクリプトに実行権限を付与しています...${NC}"
chmod +x ./start_mcp_server.sh
chmod +x ./test_container_connectivity.sh
echo -e "${GREEN}完了！${NC}"

# 必要なディレクトリを作成
echo -e "${BLUE}必要なディレクトリを作成しています...${NC}"
mkdir -p ./output
chmod 777 ./output
mkdir -p ../app/patent_system/data
chmod 777 ../app/patent_system/data
echo -e "${GREEN}完了！${NC}"

# コンテナイメージを再ビルドしてネットワークユーティリティを含めるようにします
echo -e "${BLUE}コンテナイメージを再ビルドしています...${NC}"
echo -e "${YELLOW}このプロセスには数分かかる場合があります${NC}"
podman-compose -f podman-compose.yml build
echo -e "${GREEN}イメージのビルドが完了しました${NC}"

# ネットワークのセットアップ
echo -e "${BLUE}ネットワーク設定を確認しています...${NC}"
if ! podman network ls | grep -q "patentdwh_default"; then
  echo -e "${YELLOW}patentdwh_defaultネットワークが見つかりません。作成します...${NC}"
  podman network create patentdwh_default
  echo -e "${GREEN}patentdwh_defaultネットワークを作成しました${NC}"
else
  echo -e "${GREEN}patentdwh_defaultネットワークは既に存在します${NC}"
fi

# AWS認証情報の確認
echo -e "${BLUE}AWS認証情報を確認しています...${NC}"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}警告: AWS_ACCESS_KEY_ID または AWS_SECRET_ACCESS_KEY 環境変数が設定されていません${NC}"
    echo "サーバー機能を正しく動作させるには、以下の環境変数を設定してください:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "export AWS_DEFAULT_REGION=your_region  # オプション, デフォルトは us-east-1"
fi

echo ""
echo -e "${GREEN}セットアップ完了！${NC}"
echo ""
echo "以下のコマンドでサービスを起動できます:"
echo "./start_mcp_server.sh"

echo "または直接podman-composeコマンドを使用することもできます:"
echo "podman-compose -f podman-compose.yml up -d"
echo ""
echo "サービスが起動したら、以下のコマンドでコンテナの接続性をテストできます:"
echo "./test_container_connectivity.sh"
echo ""
echo "詳細な使用方法については、README_PODMAN_USAGE.mdを参照してください"
echo ""
