#!/bin/bash
# ========================================================================
# CICD環境 認証情報表示スクリプト
# 全サービスの認証情報を表示し、オプションでファイルに出力
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENV_FILE="${BASE_DIR}/.env"
OUTPUT_FILE="${BASE_DIR}/credentials.txt"

# .envファイルの確認
if [ ! -f "$ENV_FILE" ]; then
    echo "エラー: .env ファイルが見つかりません: $ENV_FILE"
    exit 1
fi

# .envファイルを読み込み
source "$ENV_FILE"

# EC2 IPを取得（失敗時はlocalhostを使用）
if [ -z "$EC2_PUBLIC_IP" ]; then
    EC2_PUBLIC_IP=$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")
fi

# 出力先の確認
OUTPUT_TO_FILE=false
if [ "$1" = "-f" ] || [ "$1" = "--file" ]; then
    OUTPUT_TO_FILE=true
fi

# ヘッダー生成関数
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# サービス情報出力関数
print_service() {
    local service_name="$1"
    local url="$2"
    local username="$3"
    local password="$4"
    local notes="$5"

    echo ""
    echo "【${service_name}】"
    echo "  URL:        $url"
    echo "  ユーザー名: $username"
    echo "  パスワード: $password"
    if [ -n "$notes" ]; then
        echo "  備考:       $notes"
    fi
}

# データベース情報出力関数
print_database() {
    local db_name="$1"
    local host="$2"
    local port="$3"
    local username="$4"
    local password="$5"
    local database="$6"

    echo ""
    echo "【${db_name}】"
    echo "  ホスト:         $host"
    echo "  ポート:         $port"
    echo "  ユーザー名:     $username"
    echo "  パスワード:     $password"
    echo "  データベース:   $database"
}

# 認証情報を生成
generate_credentials() {
    print_header "CICD環境 認証情報一覧"
    echo "生成日時: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "サーバIP: $EC2_PUBLIC_IP"

    print_header "1. CI/CDサービス"

    print_service "GitLab CE" \
        "http://${EC2_PUBLIC_IP}:5003" \
        "root" \
        "${GITLAB_ROOT_PASSWORD}" \
        "Git リポジトリ、CI/CD、Mattermost"

    print_service "Nexus Repository" \
        "http://${EC2_PUBLIC_IP}:8082" \
        "admin" \
        "admin123 (初期固定パスワード)" \
        "初回ログイン時にパスワード変更が必須です"

    print_service "SonarQube" \
        "http://${EC2_PUBLIC_IP}:8000" \
        "admin" \
        "admin" \
        "⚠️ 初回ログイン後、必ずパスワード変更が必要です"

    print_service "Mattermost" \
        "http://${EC2_PUBLIC_IP}:5004" \
        "admin" \
        "（初回セットアップで設定）" \
        "チームコラボレーションツール"

    print_header "2. データベース管理"

    print_service "pgAdmin" \
        "http://${EC2_PUBLIC_IP}:5002" \
        "${PGADMIN_EMAIL}" \
        "${PGADMIN_PASSWORD}" \
        "PostgreSQL GUI管理ツール"

    print_header "3. PostgreSQLデータベース"

    print_database "PostgreSQL (外部アクセス)" \
        "${EC2_PUBLIC_IP}" \
        "5001" \
        "${POSTGRES_USER}" \
        "${POSTGRES_PASSWORD}" \
        "${POSTGRES_DB}"

    print_database "PostgreSQL (内部アクセス)" \
        "postgres" \
        "5432" \
        "${POSTGRES_USER}" \
        "${POSTGRES_PASSWORD}" \
        "${POSTGRES_DB}"

    echo ""
    echo "【PostgreSQL データベーススキーマ】"
    echo "  1. cicddb       - CICD環境用データベース"
    echo "     ユーザー:    ${POSTGRES_USER}"
    echo "     パスワード:  ${POSTGRES_PASSWORD}"
    echo ""
    echo "  2. gitlabhq     - GitLab用データベース"
    echo "     ユーザー:    gitlab"
    echo "     パスワード:  ${POSTGRES_PASSWORD}"
    echo ""
    echo "  3. sonarqube    - SonarQube用データベース"
    echo "     ユーザー:    sonar"
    echo "     パスワード:  ${SONAR_DB_PASSWORD}"
    echo ""
    echo "  4. sample_app   - サンプルアプリ用データベース"
    echo "     ユーザー:    sampleuser"
    echo "     パスワード:  ${SAMPLE_DB_PASSWORD}"
    echo ""
    echo "  5. mattermost   - Mattermost用データベース"
    echo "     ユーザー:    mattermostuser"
    echo "     パスワード:  ${MATTERMOST_DB_PASSWORD}"

    print_header "4. CI/CD設定情報"

    echo ""
    echo "【SonarQube トークン】"
    echo "  トークン: ${SONAR_TOKEN:-未設定}"
    echo "  備考:     初回ログイン後、My Account → Security → Generate Token で生成"

    echo ""
    echo "【GitLab Runner トークン】"
    echo "  トークン: ${RUNNER_TOKEN:-未設定}"
    echo "  備考:     GitLab → Settings → CI/CD → Runners で確認"

    print_header "5. 初回ログイン後の対応が必要なサービス"

    echo ""
    echo "⚠️ 以下のサービスは初回ログイン後にパスワード変更が必要です："
    echo ""
    echo "【SonarQube】"
    echo "  1. http://${EC2_PUBLIC_IP}:8000 にアクセス"
    echo "  2. admin / admin でログイン"
    echo "  3. 新しいパスワードを設定（推奨: Degital2026!）"
    echo "  4. 環境変数を更新:"
    echo "     cd ${BASE_DIR}"
    echo "     ./update-passwords.sh --sonarqube <新しいパスワード>"
    echo "  5. SonarQubeトークンを生成:"
    echo "     My Account → Security → Generate Token"
    echo "     ./update-passwords.sh --sonar-token <生成されたトークン>"
    echo ""
    echo "【Nexus Repository】"
    echo "  1. http://${EC2_PUBLIC_IP}:8082 にアクセス"
    echo "  2. admin / admin123 でログイン"
    echo "  3. 初回ログイン時、必ずパスワード変更が求められます"
    echo "  4. 新しいパスワードを設定（推奨: Degital2026!）"
    echo "  5. パスワード変更後、環境変数を更新:"
    echo "     ./update-passwords.sh --nexus <新しいパスワード>"
    echo ""
    echo "【GitLab Runner】"
    echo "  1. GitLab → Settings → CI/CD → Runners からトークンを取得"
    echo "  2. Runnerを登録:"
    echo "     sudo gitlab-runner register \\"
    echo "       --url http://${EC2_PUBLIC_IP}:5003 \\"
    echo "       --token <YOUR_TOKEN> \\"
    echo "       --executor shell \\"
    echo "       --description \"CICD Shell Runner\""
    echo "  3. 環境変数を更新:"
    echo "     ./update-passwords.sh --runner-token <YOUR_TOKEN>"

    print_header "6. 接続確認コマンド"

    echo ""
    echo "【サービス接続確認】"
    echo "  curl http://${EC2_PUBLIC_IP}:5003/  # GitLab"
    echo "  curl http://${EC2_PUBLIC_IP}:8082/  # Nexus"
    echo "  curl http://${EC2_PUBLIC_IP}:8000/  # SonarQube"
    echo "  curl http://${EC2_PUBLIC_IP}:5002/  # pgAdmin"
    echo ""
    echo "【PostgreSQL接続確認】"
    echo "  psql -h ${EC2_PUBLIC_IP} -p 5001 -U ${POSTGRES_USER} -d ${POSTGRES_DB}"
    echo "  # パスワード: ${POSTGRES_PASSWORD}"
    echo ""
    echo "【コンテナ状態確認】"
    echo "  podman ps"
    echo "  podman-compose logs -f <service_name>"

    print_header "セキュリティに関する注意事項"

    echo ""
    echo "⚠️ このファイルには重要な認証情報が含まれています"
    echo ""
    echo "1. このファイルは安全な場所に保管してください"
    echo "2. 不要になったら確実に削除してください: rm ${OUTPUT_FILE}"
    echo "3. Gitリポジトリにコミットしないでください（.gitignoreに含まれています）"
    echo "4. 本番環境では、より強固なパスワードを設定してください"
    echo "5. 定期的にパスワードを変更してください（推奨: 90日ごと）"
    echo ""
}

# メイン処理
if [ "$OUTPUT_TO_FILE" = true ]; then
    # ファイルに出力
    generate_credentials > "$OUTPUT_FILE"
    chmod 600 "$OUTPUT_FILE"  # パーミッション制限

    echo "==========================================="
    echo "✓ 認証情報をファイルに出力しました"
    echo "==========================================="
    echo ""
    echo "出力先: $OUTPUT_FILE"
    echo "パーミッション: 600 (所有者のみ読み書き可能)"
    echo ""
    echo "内容を表示:"
    echo "  cat $OUTPUT_FILE"
    echo ""
    echo "内容を確認後、削除することを推奨:"
    echo "  rm $OUTPUT_FILE"
    echo ""
else
    # 標準出力に表示
    generate_credentials
    echo ""
    echo "==========================================="
    echo "ファイルに出力する場合:"
    echo "  $0 --file"
    echo "==========================================="
    echo ""
fi
