#!/bin/bash

# =============================================================================
# アプリケーション停止スクリプト
# デプロイされたFrontend・Backendアプリケーションを停止
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

# デプロイディレクトリ
DEPLOY_DIR="./deployment"
FRONTEND_DIR="${DEPLOY_DIR}/frontend"
BACKEND_DIR="${DEPLOY_DIR}/backend"

log_info "🛑 アプリケーション停止を開始します"

# =============================================================================
# 1. Frontend停止
# =============================================================================

log_info "🌐 Frontend アプリケーション停止中..."

if [[ -f ${FRONTEND_DIR}/frontend.pid ]]; then
    FRONTEND_PID=$(cat ${FRONTEND_DIR}/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        log_success "Frontend プロセス (PID: $FRONTEND_PID) を停止しました"
    else
        log_warning "Frontend プロセス (PID: $FRONTEND_PID) は既に停止しています"
    fi
    rm -f ${FRONTEND_DIR}/frontend.pid
else
    log_warning "Frontend PIDファイルが見つかりません"
fi

# ポート8500を使用するプロセスを強制停止
if pgrep -f ":8500" > /dev/null; then
    log_info "ポート8500を使用するプロセスを停止中..."
    pkill -f ":8500" || true
fi

# =============================================================================
# 2. Backend停止
# =============================================================================

log_info "⚙️ Backend アプリケーション停止中..."

if [[ -f ${BACKEND_DIR}/backend.pid ]]; then
    BACKEND_PID=$(cat ${BACKEND_DIR}/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        sleep 2

        # 正常に停止したかチェック
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            log_warning "正常停止に時間がかかっています。強制停止します..."
            kill -9 $BACKEND_PID || true
        fi

        log_success "Backend プロセス (PID: $BACKEND_PID) を停止しました"
    else
        log_warning "Backend プロセス (PID: $BACKEND_PID) は既に停止しています"
    fi
    rm -f ${BACKEND_DIR}/backend.pid
else
    log_warning "Backend PIDファイルが見つかりません"
fi

# ポート8501を使用するプロセスを強制停止
if pgrep -f ":8501" > /dev/null; then
    log_info "ポート8501を使用するプロセスを停止中..."
    pkill -f ":8501" || true
fi

# Spring Bootアプリケーションを確実に停止
if pgrep -f "sample-app-backend-latest.jar" > /dev/null; then
    log_info "残存するBackend JARプロセスを停止中..."
    pkill -f "sample-app-backend-latest.jar" || true
fi

# =============================================================================
# 3. 停止確認
# =============================================================================

sleep 1

log_info "📊 停止状況を確認中..."

# ポート使用状況確認
if ! netstat -tuln 2>/dev/null | grep -q ":8500 "; then
    log_success "ポート8500は使用可能です"
else
    log_warning "ポート8500がまだ使用中の可能性があります"
fi

if ! netstat -tuln 2>/dev/null | grep -q ":8501 "; then
    log_success "ポート8501は使用可能です"
else
    log_warning "ポート8501がまだ使用中の可能性があります"
fi

# =============================================================================
# 4. 停止完了
# =============================================================================

log_success "🎉 アプリケーション停止完了！"
echo
echo "=========================================="
echo "🛑 停止されたサービス:"
echo "   Frontend (ポート8500)"
echo "   Backend  (ポート8501)"
echo
echo "📄 ログファイルは保持されています:"
if [[ -f ${FRONTEND_DIR}/frontend.log ]]; then
    echo "   Frontend: ${FRONTEND_DIR}/frontend.log"
fi
if [[ -f ${BACKEND_DIR}/backend.log ]]; then
    echo "   Backend:  ${BACKEND_DIR}/backend.log"
fi
echo
echo "🚀 再起動方法:"
echo "   ./scripts/deploy-applications.sh"
echo "=========================================="

log_info "✅ 停止処理が正常に完了しました"