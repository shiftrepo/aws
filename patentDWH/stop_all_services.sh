#!/bin/bash

# patentDWH 統合停止スクリプト
# このスクリプトはpatentDWHシステムの全コンポーネントを停止します

# テキストカラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}patentDWH システム 統合停止スクリプト${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# カレントディレクトリがpatentDWHディレクトリか確認
if [[ ! -f "./docker-compose.consolidated.yml" ]]; then
  echo -e "${RED}エラー: patentDWHディレクトリで実行してください${NC}"
  exit 1
fi

# サービスディレクトリの存在確認
if [[ ! -d "../patent_analysis_container" ]]; then
  echo -e "${YELLOW}警告: patent_analysis_container ディレクトリが見つかりません${NC}"
  echo -e "${YELLOW}特許分析MCPサーバーの停止をスキップします${NC}"
  SKIP_PATENT_ANALYSIS=true
else
  SKIP_PATENT_ANALYSIS=false
fi

# Check for podman or docker
if command -v podman &> /dev/null; then
  CONTAINER_CMD="podman"
  COMPOSE_CMD="podman-compose"
  echo -e "${GREEN}[INFO] Using Podman for containerization${NC}"
elif command -v docker &> /dev/null; then
  CONTAINER_CMD="docker"
  COMPOSE_CMD="docker compose"
  echo -e "${GREEN}[INFO] Using Docker for containerization${NC}"
  if command -v docker-compose &> /dev/null && ! command -v "docker compose" &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "${YELLOW}[INFO] Using docker-compose command${NC}"
  fi
else
  echo -e "${RED}エラー: Dockerまたはpodmanがインストールされていません${NC}"
  exit 1
fi

# 実行中のコンテナ一覧を表示
echo -e "${BLUE}現在実行中のコンテナ:${NC}"
$CONTAINER_CMD ps
echo ""

# 特許分析MCPサーバーを停止
if [[ "$SKIP_PATENT_ANALYSIS" == "false" ]]; then
  echo -e "${BLUE}1. 特許分析MCPサーバーを停止しています...${NC}"
  cd ../patent_analysis_container
  $COMPOSE_CMD -f docker-compose.mcp.yml down
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}特許分析MCPサーバーを停止しました${NC}"
  else
    echo -e "${YELLOW}特許分析MCPサーバーの停止に問題があるかもしれません${NC}"
  fi
  cd ../patentDWH
  echo ""
fi

# patentDWH基本サービスを停止
echo -e "${BLUE}2. patentDWHの基本サービスを停止しています...${NC}"
$COMPOSE_CMD -f docker-compose.consolidated.yml down
if [ $? -eq 0 ]; then
  echo -e "${GREEN}patentDWHの基本サービスを停止しました${NC}"
else
  echo -e "${YELLOW}patentDWHの基本サービスの停止に問題があるかもしれません${NC}"
fi
echo ""

# 他のDocker Composeファイルで起動したサービスも念のため停止を試みる
echo -e "${BLUE}3. その他の関連サービスの停止を確認しています...${NC}"
$COMPOSE_CMD -f docker-compose.patched.yml down 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.enhanced.yml down 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.fixed.yml down 2>/dev/null || true
echo -e "${GREEN}完了${NC}"
echo ""

# 実行中のコンテナが残っていないか確認
echo -e "${BLUE}4. 残りのコンテナを確認しています...${NC}"
REMAINING_CONTAINERS=$($CONTAINER_CMD ps -q -f "name=patentdwh|patent-analysis")

if [[ -n "$REMAINING_CONTAINERS" ]]; then
  echo -e "${YELLOW}以下のコンテナがまだ実行中です:${NC}"
  $CONTAINER_CMD ps -f "name=patentdwh|patent-analysis"
  echo ""
  echo -e "${YELLOW}これらのコンテナを強制停止しますか？ (y/n):${NC} "
  read -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}残りのコンテナを強制停止しています...${NC}"
    echo $REMAINING_CONTAINERS | xargs -r $CONTAINER_CMD stop
    echo $REMAINING_CONTAINERS | xargs -r $CONTAINER_CMD rm -f
    echo -e "${GREEN}強制停止完了${NC}"
  else
    echo -e "${YELLOW}残りのコンテナはそのままにしています${NC}"
  fi
else
  echo -e "${GREEN}全てのコンテナが正常に停止されました${NC}"
fi
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}patentDWH システムの停止が完了しました${NC}"
echo -e "${GREEN}=========================================${NC}"
