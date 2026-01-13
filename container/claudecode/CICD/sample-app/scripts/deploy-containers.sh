#!/bin/bash
# ========================================================================
# バックエンドコンテナデプロイスクリプト
# CI/CD経由でMavenビルド成果物をコンテナ化＆デプロイ（バックエンド専用）
# ========================================================================

set -euo pipefail

# ========================================
# 設定
# ========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_JAR_PATH="${PROJECT_ROOT}/backend/target"
HEALTH_CHECK_TIMEOUT=180
HEALTH_CHECK_INTERVAL=10

# コンテナ設定
BACKEND_CONTAINER_NAME="sample-backend"
BACKEND_IMAGE="sample-backend:latest"
NETWORK_NAME="cicd_cicd-network"

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
# 環境変数チェック
# ========================================
check_env() {
    log_info "環境変数をチェック中..."
    log_variable "PROJECT_ROOT" "$PROJECT_ROOT"

    # 必須環境変数
    if [ -z "${EC2_PUBLIC_IP:-}" ]; then
        log_error "EC2_PUBLIC_IP環境変数が設定されていません"
        log_error "GitLab CI/CDで設定してください"
        exit 1
    fi
    log_variable "EC2_PUBLIC_IP" "$EC2_PUBLIC_IP"

    # デフォルト値設定
    POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    POSTGRES_DB="${POSTGRES_DB:-sampledb}"
    POSTGRES_USER="${POSTGRES_USER:-sampleuser}"
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-Degital2026!}"

    log_variable "POSTGRES_HOST" "$POSTGRES_HOST"
    log_variable "POSTGRES_DB" "$POSTGRES_DB"
    log_variable "BACKEND_JAR_PATH" "$BACKEND_JAR_PATH"
    log_success "環境変数チェック完了"
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

    log_info "Dockerfile確認中..."
    if [ ! -f "${PROJECT_ROOT}/backend/Dockerfile" ]; then
        log_error "backend/Dockerfileが見つかりません"
        exit 1
    fi
    log_success "Dockerfile確認完了"
}

# ========================================
# ネットワーク確認
# ========================================
ensure_network() {
    log_step "2" "6" "ネットワーク確認"

    if sudo podman network exists "$NETWORK_NAME" 2>/dev/null; then
        log_success "ネットワーク $NETWORK_NAME を使用します"
    else
        log_error "ネットワーク $NETWORK_NAME が存在しません"
        log_error "docker-composeでネットワークを作成してください"
        exit 1
    fi
}

# ========================================
# コンテナ停止＆削除
# ========================================
stop_and_remove_containers() {
    log_step "3" "6" "既存コンテナ停止＆削除"

    log_info "バックエンドコンテナを確認中..."
    BACKEND_EXISTS=$(sudo podman ps -a --format "{{.Names}}" | grep -w "$BACKEND_CONTAINER_NAME" || echo "")

    if [ -n "$BACKEND_EXISTS" ]; then
        log_variable "Backend Container" "$BACKEND_CONTAINER_NAME (存在)"

        log_info "$BACKEND_CONTAINER_NAME コンテナを停止中..."
        if sudo podman stop "$BACKEND_CONTAINER_NAME" 2>/dev/null; then
            log_success "$BACKEND_CONTAINER_NAME 停止完了"
        else
            log_info "$BACKEND_CONTAINER_NAME は既に停止済み"
        fi

        log_info "$BACKEND_CONTAINER_NAME コンテナを削除中..."
        if sudo podman rm "$BACKEND_CONTAINER_NAME" 2>/dev/null; then
            log_success "$BACKEND_CONTAINER_NAME 削除完了"
        else
            log_error "$BACKEND_CONTAINER_NAME の削除に失敗"
        fi
    else
        log_variable "Backend Container" "$BACKEND_CONTAINER_NAME (存在しない)"
    fi

    log_info "削除後のコンテナ状態確認..."
    REMAINING=$(sudo podman ps -a --format "{{.Names}}" | grep -w "$BACKEND_CONTAINER_NAME" || echo "")
    if [ -z "$REMAINING" ]; then
        log_success "バックエンドコンテナ削除確認完了"
    else
        log_error "コンテナが残っています: $REMAINING"
        exit 1
    fi
}

# ========================================
# コンテナビルド
# ========================================
build_containers() {
    log_step "4" "6" "コンテナビルド"

    log_info "Backend コンテナビルド中..."
    log_variable "ビルドコンテキスト" "${PROJECT_ROOT}/backend"
    log_variable "Dockerfile" "${PROJECT_ROOT}/backend/Dockerfile"
    log_variable "イメージ名" "$BACKEND_IMAGE"

    cd "${PROJECT_ROOT}/backend"
    if sudo podman build --no-cache -t "$BACKEND_IMAGE" . 2>&1 | tee /tmp/backend-build.log; then
        log_success "Backend コンテナビルド完了"
        BACKEND_IMAGE_ID=$(sudo podman images "$BACKEND_IMAGE" --format "{{.ID}}")
        log_variable "Backend Image ID" "$BACKEND_IMAGE_ID"
    else
        log_error "Backend コンテナビルド失敗"
        echo "========== ビルドログ =========="
        cat /tmp/backend-build.log | tail -50
        exit 1
    fi
}

# ========================================
# コンテナ起動
# ========================================
start_containers() {
    log_step "5" "6" "コンテナ起動"

    log_info "Backend コンテナ起動中..."
    log_variable "コンテナ名" "$BACKEND_CONTAINER_NAME"
    log_variable "イメージ" "$BACKEND_IMAGE"
    log_variable "ネットワーク" "$NETWORK_NAME"

    DATASOURCE_URL="jdbc:postgresql://${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
    log_variable "SPRING_DATASOURCE_URL" "$DATASOURCE_URL"

    if sudo podman run -d \
        --name "$BACKEND_CONTAINER_NAME" \
        --network "$NETWORK_NAME" \
        -e SPRING_PROFILES_ACTIVE=dev \
        -e SPRING_DATASOURCE_URL="$DATASOURCE_URL" \
        -e SPRING_DATASOURCE_USERNAME="$POSTGRES_USER" \
        -e SPRING_DATASOURCE_PASSWORD="$POSTGRES_PASSWORD" \
        -p 8501:8080 \
        "$BACKEND_IMAGE" 2>&1 | tee /tmp/backend-run.log; then
        log_success "Backend コンテナ起動完了"
        BACKEND_CONTAINER_ID=$(sudo podman ps -qf "name=$BACKEND_CONTAINER_NAME")
        log_variable "Backend Container ID" "$BACKEND_CONTAINER_ID"
        log_variable "ポートマッピング" "8501:8080"
    else
        log_error "Backend コンテナ起動失敗"
        cat /tmp/backend-run.log
        exit 1
    fi

    log_info "起動後のコンテナ状態確認..."
    sudo podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAMES|$BACKEND_CONTAINER_NAME)"
}

# ========================================
# ヘルスチェック
# ========================================
health_check() {
    log_step "6" "6" "ヘルスチェック"

    log_variable "タイムアウト" "${HEALTH_CHECK_TIMEOUT}秒"
    log_variable "チェック間隔" "${HEALTH_CHECK_INTERVAL}秒"
    log_info "  Backend: http://${EC2_PUBLIC_IP}:8501/api/organizations"

    local backend_healthy=false
    local elapsed=0

    while [ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]; do
        if [ "$backend_healthy" = false ]; then
            if curl -f -s --max-time 5 "http://${EC2_PUBLIC_IP}:8501/api/organizations" > /dev/null 2>&1; then
                backend_healthy=true
                log_success "Backend ヘルスチェック成功 (${elapsed}秒経過)"
            else
                log_info "Backend 起動中... (${elapsed}秒経過)"
            fi
        fi

        if [ "$backend_healthy" = true ]; then
            log_success "ヘルスチェック完了"
            return 0
        fi

        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done

    log_error "ヘルスチェックタイムアウト（${HEALTH_CHECK_TIMEOUT}秒）"
    log_error "コンテナログを確認してください:"
    log_error "  sudo podman logs --tail 100 $BACKEND_CONTAINER_NAME"
    exit 1
}

# ========================================
# メイン処理
# ========================================
main() {
    echo "=========================================="
    echo "🚀 バックエンドコンテナデプロイ開始"
    echo "=========================================="
    echo "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "実行ユーザー: $(whoami)"
    echo "実行ホスト: $(hostname)"
    echo ""

    check_env
    pre_deployment_checks
    ensure_network
    stop_and_remove_containers
    build_containers
    start_containers
    health_check

    echo ""
    echo "=========================================="
    echo "🎉 デプロイ完了"
    echo "=========================================="
    echo "📱 アクセスURL:"
    echo "  - API: http://${EC2_PUBLIC_IP}:8501/api/organizations"
    echo "  - Swagger UI: http://${EC2_PUBLIC_IP}:8501/swagger-ui.html"
    echo ""
    echo "📊 コンテナ状態:"
    sudo podman ps --format "  {{.Names}}: {{.Status}}" | grep "$BACKEND_CONTAINER_NAME"
}

# エラートラップ
trap 'log_error "デプロイ中にエラーが発生しました（Line: $LINENO, Exit Code: $?）"' ERR

main "$@"
