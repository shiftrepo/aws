#!/bin/bash

# =============================================================================
# アプリケーションデプロイスクリプト
# Nexusから最新の成果物を取得してアプリケーション環境にデプロイ
# =============================================================================

set -e

# 色付きログ関数
log_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

log_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# 環境変数読み込み
if [[ -f .env ]]; then
    source .env
    log_info "環境変数を.envから読み込みました"
else
    log_error ".envファイルが見つかりません"
    exit 1
fi

# 必要な変数チェック
if [[ -z "$EC2_PUBLIC_IP" ]]; then
    log_error "EC2_PUBLIC_IP が設定されていません"
    exit 1
fi

# Nexus設定
NEXUS_URL="http://${EC2_PUBLIC_IP}:8082"
NEXUS_USER="admin"
NEXUS_PASS="Degital2026!"

# デプロイディレクトリ
DEPLOY_DIR="./deployment"
FRONTEND_DIR="${DEPLOY_DIR}/frontend"
BACKEND_DIR="${DEPLOY_DIR}/backend"

log_info "🚀 アプリケーションデプロイを開始します"
log_info "Nexus URL: ${NEXUS_URL}"

# =============================================================================
# 1. デプロイディレクトリの準備
# =============================================================================

log_info "📁 デプロイディレクトリを準備中..."

# 既存のプロセスを停止
if pgrep -f "frontend.*8500" > /dev/null; then
    log_warning "Frontend プロセスを停止中..."
    pkill -f "frontend.*8500" || true
fi

if pgrep -f "backend.*8501" > /dev/null; then
    log_warning "Backend プロセスを停止中..."
    pkill -f "backend.*8501" || true
fi

# ディレクトリ作成
mkdir -p ${FRONTEND_DIR}
mkdir -p ${BACKEND_DIR}

# =============================================================================
# 2. Frontend デプロイ
# =============================================================================

log_info "🌐 Frontend デプロイ中..."

# Frontend成果物をNexusからダウンロード
FRONTEND_URL="${NEXUS_URL}/repository/raw-hosted/frontend/frontend-latest.tar.gz"
log_info "Frontend成果物をダウンロード: ${FRONTEND_URL}"

if curl -f -u "${NEXUS_USER}:${NEXUS_PASS}" -o "${FRONTEND_DIR}/frontend-latest.tar.gz" "${FRONTEND_URL}"; then
    log_success "Frontend成果物ダウンロード完了"

    # tar.gz展開
    cd ${FRONTEND_DIR}
    tar -xzf frontend-latest.tar.gz
    rm frontend-latest.tar.gz
    cd - > /dev/null

    # 簡易HTTPサーバーでFrontend配信（ポート8500）
    log_info "Frontend サーバーを起動中（ポート8500）..."
    cd ${FRONTEND_DIR}

    # Python3がある場合
    if command -v python3 &> /dev/null; then
        nohup python3 -m http.server 8500 > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > frontend.pid
        log_success "Frontend サーバーが起動しました (PID: $FRONTEND_PID)"
    # Node.js http-serverがある場合
    elif command -v npx &> /dev/null; then
        nohup npx http-server -p 8500 > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > frontend.pid
        log_success "Frontend サーバーが起動しました (PID: $FRONTEND_PID)"
    else
        log_error "Python3またはNode.jsが必要です"
        exit 1
    fi

    cd - > /dev/null
else
    log_error "Frontend成果物のダウンロードに失敗しました"
    exit 1
fi

# =============================================================================
# 3. Backend デプロイ
# =============================================================================

log_info "⚙️ Backend デプロイ中..."

# Backend成果物をNexusからダウンロード（最新のSNAPSHOTを探す）
BACKEND_SEARCH_URL="${NEXUS_URL}/service/rest/v1/search/assets?repository=maven-snapshots&group=com.example&name=backend"
log_info "Backend成果物を検索中..."

# 最新のJARファイルURLを取得
BACKEND_JAR_URL=$(curl -s -u "${NEXUS_USER}:${NEXUS_PASS}" "${BACKEND_SEARCH_URL}" | \
    grep -o '"downloadUrl":"[^"]*\.jar"' | \
    head -1 | \
    sed 's/"downloadUrl":"//;s/"//')

if [[ -n "$BACKEND_JAR_URL" ]]; then
    log_info "Backend JAR URL: ${BACKEND_JAR_URL}"

    # JARファイルダウンロード
    JAR_FILENAME="backend-latest.jar"
    if curl -f -u "${NEXUS_USER}:${NEXUS_PASS}" -o "${BACKEND_DIR}/${JAR_FILENAME}" "${BACKEND_JAR_URL}"; then
        log_success "Backend JAR ダウンロード完了"

        # Spring Boot アプリケーション起動（ポート8501）
        log_info "Backend アプリケーションを起動中（ポート8501）..."
        cd ${BACKEND_DIR}

        # Javaでアプリケーション起動
        nohup java -jar ${JAR_FILENAME} \
            --server.port=8501 \
            --spring.datasource.url="jdbc:postgresql://${EC2_PUBLIC_IP}:5001/sampledb" \
            --spring.datasource.username=sampleuser \
            --spring.datasource.password=Degital2026! \
            > backend.log 2>&1 &

        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        log_success "Backend アプリケーションが起動しました (PID: $BACKEND_PID)"

        cd - > /dev/null
    else
        log_error "Backend JAR のダウンロードに失敗しました"
        exit 1
    fi
else
    log_error "Backend 成果物が見つかりませんでした"
    log_info "Nexus で maven-snapshots リポジトリを確認してください"
    exit 1
fi

# =============================================================================
# 4. デプロイ完了
# =============================================================================

log_success "🎉 アプリケーションデプロイ完了！"
echo
echo "=========================================="
echo "🌐 アプリケーションURL:"
echo "   Frontend: http://${EC2_PUBLIC_IP}:8500"
echo "   Backend:  http://${EC2_PUBLIC_IP}:8501"
echo "   Swagger:  http://${EC2_PUBLIC_IP}:8501/swagger-ui.html"
echo
echo "📊 プロセス情報:"
if [[ -f ${FRONTEND_DIR}/frontend.pid ]]; then
    echo "   Frontend PID: $(cat ${FRONTEND_DIR}/frontend.pid)"
fi
if [[ -f ${BACKEND_DIR}/backend.pid ]]; then
    echo "   Backend PID:  $(cat ${BACKEND_DIR}/backend.pid)"
fi
echo
echo "📄 ログファイル:"
echo "   Frontend: ${FRONTEND_DIR}/frontend.log"
echo "   Backend:  ${BACKEND_DIR}/backend.log"
echo
echo "🛑 停止方法:"
echo "   ./scripts/stop-applications.sh"
echo "=========================================="

log_info "✅ デプロイ処理が正常に完了しました"