#!/bin/bash

# このスクリプトは特許分析MCPコンテナから他のコンテナへの接続をテストします

echo "======================================================"
echo "  特許分析MCPコンテナ通信テスト"
echo "======================================================"
echo ""

# カラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# podman-composeを使用
CONTAINER_RUNTIME="podman"
COMPOSE_COMMAND="podman-compose"
echo -e "${BLUE}podman-composeを使用します${NC}"

# podman-composeがインストールされているか確認
if ! command -v podman-compose &> /dev/null; then
  echo -e "${RED}エラー: podman-composeがインストールされていません${NC}"
  exit 1
fi

# patent-analysis-mcpコンテナが実行中かチェック
if ! $CONTAINER_RUNTIME ps | grep -q "patent-analysis-mcp"; then
  echo -e "${RED}patent-analysis-mcpコンテナが実行されていません。${NC}"
  echo -e "${YELLOW}$COMPOSE_COMMANDでサービスを起動してください。${NC}"
  exit 1
fi

echo -e "${BLUE}1. コンテナ内部からpatentdwh-db (http://patentdwh-db:5002) への接続をテストしています...${NC}"
$CONTAINER_RUNTIME exec patent-analysis-mcp curl -s -o /dev/null -w "%{http_code}" http://patentdwh-db:5002/health
if [ $? -eq 0 ]; then
  echo -e "${GREEN}patentdwh-dbへの接続に成功しました！${NC}"
else
  echo -e "${RED}patentdwh-dbへの接続に失敗しました${NC}"
  
  # DNS解決のテスト
  echo -e "${YELLOW}DNS解決テストを実行...${NC}"
  $CONTAINER_RUNTIME exec patent-analysis-mcp ping -c 2 patentdwh-db
fi

echo ""
echo -e "${BLUE}2. コンテナ内部からpatentdwh-mcp-enhanced (http://patentdwh-mcp-enhanced:8080) への接続をテストしています...${NC}"
$CONTAINER_RUNTIME exec patent-analysis-mcp curl -s -o /dev/null -w "%{http_code}" http://patentdwh-mcp-enhanced:8080/health
if [ $? -eq 0 ]; then
  echo -e "${GREEN}patentdwh-mcp-enhancedへの接続に成功しました！${NC}"
else
  echo -e "${RED}patentdwh-mcp-enhancedへの接続に失敗しました${NC}"
  
  # DNS解決のテスト
  echo -e "${YELLOW}DNS解決テストを実行...${NC}"
  $CONTAINER_RUNTIME exec patent-analysis-mcp ping -c 2 patentdwh-mcp-enhanced
fi

echo ""
echo -e "${BLUE}3. コンテナ内部からAPIs経由でDBに接続できるかテストしています...${NC}"
$CONTAINER_RUNTIME exec patent-analysis-mcp curl -s -X POST -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1 AS test_connection", "db_type": "sqlite"}' \
  http://patentdwh-db:5002/api/sql-query | grep -q "test_connection"
  
if [ $? -eq 0 ]; then
  echo -e "${GREEN}API経由でのDBへの接続に成功しました！${NC}"
else
  echo -e "${RED}API経由でのDBへの接続に失敗しました${NC}"
fi

echo ""
echo -e "${BLUE}4. コンテナのネットワーク設定を確認しています...${NC}"
echo -e "${YELLOW}patent-analysis-mcpコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patent-analysis-mcp --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}'
echo ""

echo -e "${YELLOW}patentdwh-dbコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patentdwh-db --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}' 2>/dev/null || echo "コンテナが見つかりません"
echo ""

echo -e "${YELLOW}patentdwh-mcp-enhancedコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patentdwh-mcp-enhanced --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}' 2>/dev/null || echo "コンテナが見つかりません"
echo ""

echo -e "${BLUE}5. ネットワーク一覧:${NC}"
$CONTAINER_RUNTIME network ls

# podman-composeの設定を表示
echo ""
echo -e "${BLUE}6. podman-compose設定ファイルの確認:${NC}"
echo -e "${YELLOW}podman-compose.yml の内容:${NC}"
cat podman-compose.yml | grep -A10 "networks:"
echo ""

# コンテナ接続性修正ヒント
echo ""
echo -e "${GREEN}テスト完了！${NC}"
echo "各テストの結果を確認し、ネットワーク設定を必要に応じて調整してください。"
echo ""
echo -e "${YELLOW}問題がある場合の対処法:${NC}"
echo "1. ネットワークが正しく設定されていることを確認してください。"
echo "2. patentdwh_defaultネットワークが存在することを確認："
echo "   $CONTAINER_RUNTIME network ls | grep patentdwh_default"
echo "3. 存在しない場合、以下のコマンドで作成できます："
echo "   $CONTAINER_RUNTIME network create patentdwh_default"
echo "4. 再度サービスを起動："
echo "   cd /root/aws.git/patent_analysis_container && $COMPOSE_COMMAND -f podman-compose.yml up -d"
