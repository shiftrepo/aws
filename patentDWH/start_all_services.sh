#!/bin/bash

# patentDWH 統合起動スクリプト
# このスクリプトはpatentDWHシステムの全コンポーネントを起動します

# テキストカラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# AWS認証情報の確認
if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
  echo -e "${YELLOW}警告: AWS認証情報が環境変数に設定されていません。${NC}"
  echo -e "${YELLOW}自然言語クエリ機能を使用する場合は、以下の変数を設定してください:${NC}"
  echo -e "${YELLOW}  export AWS_ACCESS_KEY_ID=\"your_key_id\"${NC}"
  echo -e "${YELLOW}  export AWS_SECRET_ACCESS_KEY=\"your_secret_key\"${NC}"
  echo -e "${YELLOW}  export AWS_REGION=\"us-east-1\" # または適切なリージョン${NC}"
  echo ""
  read -p "環境変数なしで続行しますか？ (y/n): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}起動を中止します。${NC}"
    exit 1
  fi
fi

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}patentDWH システム 統合起動スクリプト${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# カレントディレクトリがpatentDWHディレクトリか確認
if [[ ! -f "./docker-compose.consolidated.yml" ]]; then
  echo -e "${RED}エラー: patentDWHディレクトリで実行してください${NC}"
  exit 1
fi

# サービスディレクトリの存在確認
if [[ ! -d "../patent_analysis_container" ]]; then
  echo -e "${RED}エラー: patent_analysis_container ディレクトリが見つかりません${NC}"
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
  echo -e "${YELLOW}dockerを使用します (podman推奨)${NC}"
else
  echo -e "${RED}エラー: podmanもdockerもインストールされていません${NC}"
  exit 1
fi

# コンテナネットワークを確認・作成
NETWORK_NAME="patentdwh_default"
if ! $CONTAINER_RUNTIME network exists $NETWORK_NAME &>/dev/null; then
  echo -e "${YELLOW}ネットワーク $NETWORK_NAME が存在しないため、作成します${NC}"
  $CONTAINER_RUNTIME network create $NETWORK_NAME
  if [ $? -ne 0 ]; then
    echo -e "${RED}ネットワーク $NETWORK_NAME の作成に失敗しました${NC}"
    exit 1
  fi
  echo -e "${GREEN}ネットワーク $NETWORK_NAME を作成しました${NC}"
else
  echo -e "${GREEN}既存のネットワーク $NETWORK_NAME を使用します${NC}"
fi

# 前回のサービスをクリーンアップ
echo -e "${BLUE}1. 前回のサービスをクリーンアップしています...${NC}"
$COMPOSE_CMD -f docker-compose.consolidated.yml down 2>/dev/null
cd ../patent_analysis_container
$COMPOSE_CMD -f docker-compose.mcp.yml down 2>/dev/null
cd ../patentDWH
echo -e "${GREEN}クリーンアップ完了${NC}"
echo ""

# ログ出力関数
log_info() {
  echo -e "${BLUE}[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_success() {
  echo -e "${GREEN}[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_error() {
  echo -e "${RED}[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

# patentDWH基本サービスを起動
echo -e "${BLUE}2. patentDWHの基本サービス（DB、MCPサーバー）を起動しています...${NC}"
log_info "docker-compose.consolidated.yml ファイルを使用してサービスを起動します"
$COMPOSE_CMD -f docker-compose.consolidated.yml up -d patentdwh-db patentdwh-mcp-enhanced
if [ $? -eq 0 ]; then
  log_success "サービス起動コマンドが正常に実行されました"
else
  log_error "サービス起動コマンドの実行中にエラーが発生しました"
fi

# コンテナIDとステータスを表示
log_info "起動したコンテナの状態を確認します"
$CONTAINER_RUNTIME ps -a | grep "patentdwh"

# サービスのログを一部表示
log_info "patentdwh-dbの最新のログを表示します（最大20行）"
$COMPOSE_CMD -f docker-compose.consolidated.yml logs --tail=20 patentdwh-db

# サービスが起動するまで待機
echo -e "${BLUE}   サービスの起動を確認中...${NC}"
log_info "データベースサービスの起動を確認しています: http://localhost:5002/health"
MAX_RETRIES=30
RETRY_COUNT=0
while ! curl -s http://localhost:5002/health > /dev/null && [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
  echo -n "."
  sleep 2
  ((RETRY_COUNT++))
done

if [[ $RETRY_COUNT -ge $MAX_RETRIES ]]; then
  echo -e "${RED}\nデータベースサービスの起動確認に失敗しました。ログを確認してください。${NC}"
  echo -e "${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patentdwh-db${NC}"
  exit 1
fi

echo -e "${GREEN}\n   データベースサービス稼働中${NC}"

# MCPサービスの起動確認
log_info "MCPサービスの起動を確認しています: http://localhost:8080/health"
RETRY_COUNT=0
while ! curl -s http://localhost:8080/health > /dev/null && [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
  echo -n "."
  sleep 2
  ((RETRY_COUNT++))
done

if [[ $RETRY_COUNT -ge $MAX_RETRIES ]]; then
  log_error "MCPサービスの起動確認に失敗しました"
  log_info "patentdwh-mcp-enhancedの最新のログを表示します（最大20行）"
  $COMPOSE_CMD -f docker-compose.consolidated.yml logs --tail=20 patentdwh-mcp-enhanced
  echo -e "${RED}\nMCPサービスの起動確認に失敗しました。ログを確認してください。${NC}"
  echo -e "${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patentdwh-mcp-enhanced${NC}"
  exit 1
fi

log_success "MCPサービス稼働中"
echo -e "${GREEN}\n   MCPサービス稼働中${NC}"
echo ""

# 特許分析MCPサーバーの起動
echo -e "${BLUE}3. 特許分析MCPサーバーを起動しています...${NC}"
log_info "特許分析MCPサーバー（patent-analysis-mcp）を起動します"
$COMPOSE_CMD -f docker-compose.consolidated.yml up -d patent-analysis-mcp
if [ $? -eq 0 ]; then
  log_success "特許分析MCPサーバー起動コマンドが正常に実行されました"
else
  log_error "特許分析MCPサーバーの起動中にエラーが発生しました"
fi

# コンテナの状態を確認
log_info "起動した特許分析MCPサーバーの状態を確認します"
$CONTAINER_RUNTIME ps -a | grep "patent-analysis-mcp"

# サービスのログを一部表示
log_info "patent-analysis-mcpの最新のログを表示します（最大20行）"
$COMPOSE_CMD -f docker-compose.consolidated.yml logs --tail=20 patent-analysis-mcp

# サービスが起動するまで待機
echo -e "${BLUE}   特許分析MCPサーバーの起動を確認中...${NC}"
log_info "特許分析MCPサーバーの起動を確認しています: http://localhost:8000/"
RETRY_COUNT=0
while ! curl -s http://localhost:8000/ > /dev/null && [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
  echo -n "."
  sleep 2
  ((RETRY_COUNT++))
  
  # 10回ごとにステータスを表示
  if (( RETRY_COUNT % 10 == 0 )); then
    log_info "まだ起動を確認できません... コンテナの状態を再確認します"
    $CONTAINER_RUNTIME ps -a | grep "patent-analysis-mcp"
  fi
done

if [[ $RETRY_COUNT -ge $MAX_RETRIES ]]; then
  log_error "特許分析MCPサーバーの起動確認に失敗しました"
  log_info "patent-analysis-mcpの詳細ログを確認してください"
  echo -e "${RED}\n特許分析MCPサーバーの起動確認に失敗しました。ログを確認してください。${NC}"
  echo -e "${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patent-analysis-mcp${NC}"
else
  log_success "特許分析MCPサーバー稼働中"
  echo -e "${GREEN}\n   特許分析MCPサーバー稼働中${NC}"
fi
echo ""

# 起動完了メッセージ
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}patentDWH システムの起動が完了しました${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}利用可能なサービス:${NC}"
echo -e "1. データベース & WebUI: ${GREEN}http://localhost:5002/${NC}"
echo -e "2. MCPサーバー: ${GREEN}http://localhost:8080/${NC}"
echo -e "3. 特許分析MCPサーバー: ${GREEN}http://localhost:8000/${NC}"
echo ""
echo -e "${BLUE}サービスの動作確認:${NC}"
echo -e "データベース: ${YELLOW}curl http://localhost:5002/health${NC}"
echo -e "MCPサーバー: ${YELLOW}curl http://localhost:8080/health${NC}"
echo -e "特許分析サーバー: ${YELLOW}curl http://localhost:8000/${NC}"
echo ""
echo -e "${BLUE}特許分析の実行例:${NC}"
echo -e "${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml run patent-analysis \"トヨタ\" inpit${NC}"
echo ""
echo -e "${BLUE}サービスの停止:${NC}"
echo -e "${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml down${NC}"
echo -e "${YELLOW}または ./stop_all_services.sh${NC}"
echo ""
echo -e "${BLUE}各サービスのログ確認:${NC}"
echo -e "データベース: ${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patentdwh-db${NC}"
echo -e "MCPサーバー: ${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patentdwh-mcp-enhanced${NC}"
echo -e "特許分析サーバー: ${YELLOW}$COMPOSE_CMD -f docker-compose.consolidated.yml logs -f patent-analysis-mcp${NC}"
