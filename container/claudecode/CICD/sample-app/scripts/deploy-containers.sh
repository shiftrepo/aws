#!/bin/bash
# ========================================================================
# コンテナデプロイスクリプト
# CI/CD経由でMavenビルド成果物をコンテナ化＆デプロイ
# ========================================================================

set -euo pipefail

# ========================================
# 設定
# ========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CICD_ROOT="/root/aws.git/container/claudecode/CICD"
BACKEND_JAR_PATH="${PROJECT_ROOT}/backend/target"
HEALTH_CHECK_TIMEOUT=180
HEALTH_CHECK_INTERVAL=10

# ========================================
# ログ関数（詳細出力）
# ========================================
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - ✅ $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - ❌ $1" >&2
}

log_step() {
    echo ""
    echo "=========================================="
    echo "[STEP $1/$2] $3"
    echo "=========================================="
}

log_variable() {
    echo "  📋 $1 = $2"
}

# ========================================
# 環境変数読み込み
# ========================================
source_env() {
    log_info "環境変数を読み込み中..."
    log_variable "PROJECT_ROOT" "$PROJECT_ROOT"
    log_variable "CICD_ROOT" "$CICD_ROOT"

    if [ ! -f "${CICD_ROOT}/.env" ]; then
        log_error ".envファイルが見つかりません: ${CICD_ROOT}/.env"
        exit 1
    fi
    source "${CICD_ROOT}/.env"
    log_success ".env読み込み完了"

    if [ -z "$EC2_PUBLIC_IP" ]; then
        log_error "EC2_PUBLIC_IP環境変数が設定されていません"
        exit 1
    fi
    log_variable "EC2_PUBLIC_IP" "$EC2_PUBLIC_IP"
    log_variable "BACKEND_JAR_PATH" "$BACKEND_JAR_PATH"
}

# ========================================
# 事前チェック
# ========================================
pre_deployment_checks() {
    log_step "1" "6" "事前チェック"

    log_info "JARファイルを検索中..."
    log_variable "検索パス" "$BACKEND_JAR_PATH"

    JAR_FILE=$(find "$BACKEND_JAR_PATH" -name "*.jar" -not -name "*-sources.jar" -not -name "*-javadoc.jar" 2>/dev/null | head -1)

    if [ -z "$JAR_FILE" ]; then
        log_error "JARファイルが見つかりません"
        log_error "mvn clean package -DskipTests を先に実行してください"
        exit 1
    fi

    JAR_SIZE=$(du -h "$JAR_FILE" | cut -f1)
    JAR_NAME=$(basename "$JAR_FILE")
    log_success "JARファイル確認完了"
    log_variable "JAR名" "$JAR_NAME"
    log_variable "JARサイズ" "$JAR_SIZE"
    log_variable "JAR絶対パス" "$JAR_FILE"

    log_info "docker-compose.yml確認中..."
    if [ ! -f "${CICD_ROOT}/docker-compose.yml" ]; then
        log_error "docker-compose.ymlが見つかりません"
        exit 1
    fi
    log_success "docker-compose.yml確認完了"
    log_variable "docker-compose.yml" "${CICD_ROOT}/docker-compose.yml"
}

# ========================================
# コンテナ停止＆削除（名前指定）
# ========================================
stop_and_remove_containers() {
    log_step "2" "6" "既存コンテナ停止＆削除"

    log_info "アプリケーションコンテナを確認中..."
    BACKEND_EXISTS=$(sudo podman ps -a --format "{{.Names}}" | grep -w "sample-backend" || echo "")
    FRONTEND_EXISTS=$(sudo podman ps -a --format "{{.Names}}" | grep -w "nginx-frontend" || echo "")

    if [ -n "$BACKEND_EXISTS" ]; then
        log_variable "Backend Container" "sample-backend (存在)"
    else
        log_variable "Backend Container" "sample-backend (存在しない)"
    fi

    if [ -n "$FRONTEND_EXISTS" ]; then
        log_variable "Frontend Container" "nginx-frontend (存在)"
    else
        log_variable "Frontend Container" "nginx-frontend (存在しない)"
    fi

    # Backendコンテナの停止＆削除
    if [ -n "$BACKEND_EXISTS" ]; then
        log_info "sample-backend コンテナを停止中..."
        if sudo podman stop sample-backend 2>/dev/null; then
            log_success "sample-backend 停止完了"
        else
            log_info "sample-backend は既に停止済み"
        fi

        log_info "sample-backend コンテナを削除中..."
        if sudo podman rm sample-backend 2>/dev/null; then
            log_success "sample-backend 削除完了"
        else
            log_error "sample-backend の削除に失敗"
        fi
    fi

    # Frontendコンテナの停止＆削除
    if [ -n "$FRONTEND_EXISTS" ]; then
        log_info "nginx-frontend コンテナを停止中..."
        if sudo podman stop nginx-frontend 2>/dev/null; then
            log_success "nginx-frontend 停止完了"
        else
            log_info "nginx-frontend は既に停止済み"
        fi

        log_info "nginx-frontend コンテナを削除中..."
        if sudo podman rm nginx-frontend 2>/dev/null; then
            log_success "nginx-frontend 削除完了"
        else
            log_error "nginx-frontend の削除に失敗"
        fi
    fi

    log_info "削除後のコンテナ状態確認..."
    REMAINING=$(sudo podman ps -a --format "{{.Names}}" | grep -E "^(sample-backend|nginx-frontend)$" || echo "")
    if [ -z "$REMAINING" ]; then
        log_success "アプリケーションコンテナ削除確認完了"
    else
        log_error "コンテナが残っています: $REMAINING"
        exit 1
    fi
}

# ========================================
# コンテナビルド
# ========================================
build_containers() {
    log_step "3" "6" "コンテナビルド"

    cd "$CICD_ROOT"
    log_variable "作業ディレクトリ" "$(pwd)"
    log_variable "ビルドコンテキスト(backend)" "${CICD_ROOT}/sample-app/backend"
    log_variable "ビルドコンテキスト(nginx)" "${CICD_ROOT}/sample-app"

    log_info "Backend コンテナビルド中..."
    log_variable "コマンド" "sudo podman-compose build --no-cache sample-backend"
    log_info "  --no-cache: キャッシュ無効化（最新JARを確実に反映）"

    if sudo podman-compose build --no-cache sample-backend 2>&1 | tee /tmp/backend-build.log; then
        log_success "Backend コンテナビルド完了"
        BACKEND_IMAGE_ID=$(sudo podman images sample-backend:latest --format "{{.ID}}")
        log_variable "Backend Image ID" "$BACKEND_IMAGE_ID"
    else
        log_error "Backend コンテナビルド失敗"
        echo "========== ビルドログ =========="
        cat /tmp/backend-build.log | tail -50
        exit 1
    fi

    log_info "Nginx Frontend コンテナビルド中..."
    log_variable "コマンド" "sudo podman-compose build --no-cache nginx-frontend"

    if sudo podman-compose build --no-cache nginx-frontend 2>&1 | tee /tmp/frontend-build.log; then
        log_success "Nginx Frontend コンテナビルド完了"
        FRONTEND_IMAGE_ID=$(sudo podman images nginx-frontend:latest --format "{{.ID}}")
        log_variable "Frontend Image ID" "$FRONTEND_IMAGE_ID"
    else
        log_error "Nginx Frontend コンテナビルド失敗"
        echo "========== ビルドログ =========="
        cat /tmp/frontend-build.log | tail -50
        exit 1
    fi
}

# ========================================
# コンテナ起動
# ========================================
start_containers() {
    log_step "4" "6" "コンテナ起動"

    cd "$CICD_ROOT"
    log_variable "作業ディレクトリ" "$(pwd)"
    log_variable "コマンド" "sudo podman-compose --profile app up -d"
    log_info "  --profile app: sample-backend, nginx-frontend のみ起動"
    log_info "  -d: デタッチドモード（バックグラウンド実行）"

    if sudo podman-compose --profile app up -d 2>&1 | tee /tmp/podman-up.log; then
        log_success "コンテナ起動完了"

        log_info "起動後のコンテナ状態確認..."
        sudo podman ps --filter "label=io.podman.compose.project=cicd" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAMES|sample-backend|nginx-frontend)"

        BACKEND_CONTAINER_ID=$(sudo podman ps -qf "name=sample-backend")
        FRONTEND_CONTAINER_ID=$(sudo podman ps -qf "name=nginx-frontend")
        log_variable "Backend Container ID" "$BACKEND_CONTAINER_ID"
        log_variable "Frontend Container ID" "$FRONTEND_CONTAINER_ID"
    else
        log_error "コンテナ起動失敗"
        cat /tmp/podman-up.log
        exit 1
    fi
}

# ========================================
# ヘルスチェック
# ========================================
health_check() {
    log_step "5" "6" "ヘルスチェック"

    log_variable "タイムアウト" "${HEALTH_CHECK_TIMEOUT}秒"
    log_variable "チェック間隔" "${HEALTH_CHECK_INTERVAL}秒"
    log_info "  Backend: http://localhost:8080/actuator/health (コンテナ内)"
    log_info "  Frontend: http://localhost:80/health (コンテナ内)"

    local backend_healthy=false
    local frontend_healthy=false
    local elapsed=0

    while [ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]; do
        # Backend（コンテナ内部からのチェック）
        if [ "$backend_healthy" = false ]; then
            if sudo podman exec sample-backend wget --no-verbose --tries=1 --spider \
               http://localhost:8080/actuator/health 2>/dev/null; then
                backend_healthy=true
                log_success "Backend ヘルスチェック成功 (${elapsed}秒経過)"
            else
                log_info "Backend 起動中... (${elapsed}秒経過)"
            fi
        fi

        # Frontend（コンテナ内部からのチェック）
        if [ "$frontend_healthy" = false ]; then
            if sudo podman exec nginx-frontend wget --no-verbose --tries=1 --spider \
               http://localhost:80/health 2>/dev/null; then
                frontend_healthy=true
                log_success "Frontend ヘルスチェック成功 (${elapsed}秒経過)"
            else
                log_info "Frontend 起動中... (${elapsed}秒経過)"
            fi
        fi

        if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ]; then
            log_success "全コンテナのヘルスチェック完了"
            return 0
        fi

        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done

    log_error "ヘルスチェックタイムアウト（${HEALTH_CHECK_TIMEOUT}秒）"
    log_error "コンテナログを確認してください:"
    log_error "  sudo podman logs --tail 100 sample-backend"
    log_error "  sudo podman logs --tail 100 nginx-frontend"
    exit 1
}

# ========================================
# デプロイ検証（環境変数使用）
# ========================================
verify_deployment() {
    log_step "6" "6" "デプロイ検証"

    local EXTERNAL_URL="http://${EC2_PUBLIC_IP}:5006"
    log_variable "外部URL" "$EXTERNAL_URL"
    log_variable "ポート" "5006 (nginx-frontend)"

    log_info "外部アクセス確認中..."
    log_variable "テストURL" "${EXTERNAL_URL}/health"

    if curl -f -s "${EXTERNAL_URL}/health" > /dev/null; then
        log_success "外部アクセス確認完了"

        log_info "API動作確認中..."
        if curl -f -s "${EXTERNAL_URL}/api/organizations" > /dev/null; then
            log_success "API動作確認完了"
        else
            log_error "API接続失敗（Backendに問題がある可能性）"
        fi
    else
        log_error "外部アクセス失敗: ${EXTERNAL_URL}/health"
        log_error "以下を確認してください:"
        log_error "  1. EC2セキュリティグループでポート5006が許可されているか"
        log_error "  2. firewalld設定: sudo firewall-cmd --list-ports"
        log_error "  3. コンテナが正常に起動しているか: sudo podman ps"
        exit 1
    fi

    echo ""
    echo "=========================================="
    echo "🎉 デプロイ完了"
    echo "=========================================="
    echo "📱 アクセスURL:"
    echo "  - Frontend: ${EXTERNAL_URL}/"
    echo "  - API: ${EXTERNAL_URL}/api/organizations"
    echo "  - Health: ${EXTERNAL_URL}/health"
    echo ""
    echo "📊 コンテナ状態:"
    sudo podman ps --filter "label=io.podman.compose.project=cicd" --format "  {{.Names}}: {{.Status}}" | grep -E "(sample-backend|nginx-frontend)"
}

# ========================================
# メイン処理
# ========================================
main() {
    echo "=========================================="
    echo "🚀 コンテナデプロイ開始"
    echo "=========================================="
    echo "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "実行ユーザー: $(whoami)"
    echo "実行ホスト: $(hostname)"
    echo ""

    source_env
    pre_deployment_checks
    stop_and_remove_containers
    build_containers
    start_containers
    health_check
    verify_deployment
}

# エラートラップ
trap 'log_error "デプロイ中にエラーが発生しました（Line: $LINENO, Exit Code: $?）"' ERR

main "$@"
