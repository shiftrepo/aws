#!/bin/bash
# ========================================================================
# CICD環境 パスワード更新スクリプト
# .env ファイルのパスワードとトークンを更新
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENV_FILE="${BASE_DIR}/.env"

# ヘルプ表示
show_help() {
    cat << EOF
使い方: $0 [オプション] <新しい値>

環境変数ファイル (.env) のパスワードやトークンを更新します。

オプション:
  --gitlab <password>         GitLab rootパスワードを更新
  --nexus <password>          Nexus adminパスワードを更新
  --sonarqube <password>      SonarQube adminパスワードを更新
  --postgres <password>       PostgreSQLパスワードを更新
  --pgadmin <password>        pgAdminパスワードを更新
  --mattermost <password>     Mattermost DBパスワードを更新
  --sonar-db <password>       SonarQube DBパスワードを更新
  --sample-db <password>      Sample App DBパスワードを更新
  --sonar-token <token>       SonarQubeトークンを更新
  --runner-token <token>      GitLab Runnerトークンを更新
  --ec2-host <hostname/ip>    EC2ドメイン名/IPアドレスを更新
  --all <password>            すべてのパスワードを一括更新（トークンを除く）
  --show                      現在の設定値を表示
  -h, --help                  このヘルプを表示

例:
  # SonarQubeパスワードを更新
  $0 --sonarqube NewPassword123!

  # すべてのパスワードを一括更新
  $0 --all Degital2026!

  # 現在の設定を表示
  $0 --show

  # SonarQubeトークンを更新
  $0 --sonar-token sqa_1234567890abcdef

  # EC2ドメイン名/IPアドレスを更新
  $0 --ec2-host ec2-xx-xx-xx-xx.compute-1.amazonaws.com
  $0 --ec2-host 192.168.1.100

注意:
  - パスワードに特殊文字が含まれる場合、シングルクォートで囲んでください
  - 例: $0 --gitlab 'Pass!@#$%'
  - 更新後、関連サービスの再起動が必要な場合があります

EOF
}

# .envファイルの確認
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo "エラー: .env ファイルが見つかりません: $ENV_FILE"
        exit 1
    fi
}

# バックアップ作成
backup_env() {
    local backup_file="${ENV_FILE}.backup.$(date +%Y%m%d%H%M%S)"
    cp "$ENV_FILE" "$backup_file"
    echo "  ✓ バックアップ作成: $backup_file"
}

# パスワード更新
update_password() {
    local key="$1"
    local value="$2"
    local description="$3"

    echo ""
    echo "【${description}】"
    echo "  変数名: $key"
    echo "  新しい値: ${value:0:4}****"

    # sedで更新（macOSとLinux両対応）
    if sed --version >/dev/null 2>&1; then
        # GNU sed (Linux)
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        # BSD sed (macOS)
        sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    fi

    echo "  ✓ 更新完了"
}

# 現在の設定を表示
show_current_settings() {
    check_env_file
    source "$ENV_FILE"

    echo "==========================================="
    echo "現在の環境変数設定"
    echo "==========================================="
    echo ""
    echo "【CI/CDサービス】"
    echo "  GITLAB_ROOT_PASSWORD:      ${GITLAB_ROOT_PASSWORD:0:4}****"
    echo "  NEXUS_ADMIN_PASSWORD:      ${NEXUS_ADMIN_PASSWORD:0:4}****"
    echo "  SONARQUBE_ADMIN_PASSWORD:  ${SONARQUBE_ADMIN_PASSWORD:0:4}****"
    echo ""
    echo "【データベース】"
    echo "  POSTGRES_PASSWORD:         ${POSTGRES_PASSWORD:0:4}****"
    echo "  PGADMIN_PASSWORD:          ${PGADMIN_PASSWORD:0:4}****"
    echo "  SONAR_DB_PASSWORD:         ${SONAR_DB_PASSWORD:0:4}****"
    echo "  SAMPLE_DB_PASSWORD:        ${SAMPLE_DB_PASSWORD:0:4}****"
    echo "  MATTERMOST_DB_PASSWORD:    ${MATTERMOST_DB_PASSWORD:0:4}****"
    echo ""
    echo "【トークン】"
    echo "  SONAR_TOKEN:               ${SONAR_TOKEN:0:10}****"
    echo "  RUNNER_TOKEN:              ${RUNNER_TOKEN:0:10}****"
    echo ""
    echo "【データベース情報】"
    echo "  POSTGRES_USER:             $POSTGRES_USER"
    echo "  POSTGRES_DB:               $POSTGRES_DB"
    echo "  PGADMIN_EMAIL:             $PGADMIN_EMAIL"
    echo "  EC2_PUBLIC_IP:             $EC2_PUBLIC_IP"
    echo ""
}

# すべてのパスワードを更新
update_all_passwords() {
    local password="$1"

    echo "==========================================="
    echo "すべてのパスワードを一括更新"
    echo "==========================================="

    backup_env

    update_password "GITLAB_ROOT_PASSWORD" "$password" "GitLab"
    update_password "NEXUS_ADMIN_PASSWORD" "$password" "Nexus"
    update_password "SONARQUBE_ADMIN_PASSWORD" "$password" "SonarQube"
    update_password "POSTGRES_PASSWORD" "$password" "PostgreSQL"
    update_password "PGADMIN_PASSWORD" "$password" "pgAdmin"
    update_password "SONAR_DB_PASSWORD" "$password" "SonarQube DB"
    update_password "SAMPLE_DB_PASSWORD" "$password" "Sample App DB"
    update_password "MATTERMOST_DB_PASSWORD" "$password" "Mattermost DB"

    echo ""
    echo "==========================================="
    echo "✓ すべてのパスワードを更新しました"
    echo "==========================================="
    echo ""
    echo "⚠️ 変更を反映するには、コンテナの再起動が必要です:"
    echo "  cd ${BASE_DIR}"
    echo "  podman-compose down"
    echo "  podman-compose up -d"
    echo ""
}

# メイン処理
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi

    check_env_file

    case "$1" in
        --gitlab)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "GITLAB_ROOT_PASSWORD" "$2" "GitLab"
            echo ""
            echo "✓ GitLabパスワードを更新しました"
            ;;

        --nexus)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "NEXUS_ADMIN_PASSWORD" "$2" "Nexus"
            echo ""
            echo "✓ Nexusパスワードを更新しました"
            echo ""
            echo "⚠️ GitLab CI/CD環境変数も更新してください:"
            echo "  GitLab → Settings → CI/CD → Variables → NEXUS_ADMIN_PASSWORD"
            ;;

        --sonarqube)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "SONARQUBE_ADMIN_PASSWORD" "$2" "SonarQube"
            echo ""
            echo "✓ SonarQubeパスワードを更新しました"
            ;;

        --postgres)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "POSTGRES_PASSWORD" "$2" "PostgreSQL"
            echo ""
            echo "✓ PostgreSQLパスワードを更新しました"
            echo ""
            echo "⚠️ 変更を反映するには、コンテナの再起動が必要です:"
            echo "  cd ${BASE_DIR}"
            echo "  podman-compose down"
            echo "  podman-compose up -d"
            ;;

        --pgadmin)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "PGADMIN_PASSWORD" "$2" "pgAdmin"
            echo ""
            echo "✓ pgAdminパスワードを更新しました"
            echo ""
            echo "⚠️ 変更を反映するには、pgAdminコンテナの再起動が必要です:"
            echo "  podman-compose restart pgadmin"
            ;;

        --mattermost)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "MATTERMOST_DB_PASSWORD" "$2" "Mattermost DB"
            echo ""
            echo "✓ Mattermostデータベースパスワードを更新しました"
            echo ""
            echo "⚠️ 変更を反映するには、Mattermostコンテナの再起動が必要です:"
            echo "  podman-compose restart mattermost"
            ;;

        --sonar-db)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "SONAR_DB_PASSWORD" "$2" "SonarQube DB"
            echo ""
            echo "✓ SonarQube DBパスワードを更新しました"
            ;;

        --sample-db)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            backup_env
            update_password "SAMPLE_DB_PASSWORD" "$2" "Sample App DB"
            echo ""
            echo "✓ Sample App DBパスワードを更新しました"
            ;;

        --sonar-token)
            if [ -z "$2" ]; then
                echo "エラー: トークンを指定してください"
                exit 1
            fi
            backup_env
            update_password "SONAR_TOKEN" "$2" "SonarQube Token"
            echo ""
            echo "✓ SonarQubeトークンを更新しました"
            echo ""
            echo "⚠️ GitLab CI/CD環境変数も更新してください:"
            echo "  GitLab → Settings → CI/CD → Variables → SONAR_TOKEN"
            ;;

        --runner-token)
            if [ -z "$2" ]; then
                echo "エラー: トークンを指定してください"
                exit 1
            fi
            backup_env
            update_password "RUNNER_TOKEN" "$2" "GitLab Runner Token"
            echo ""
            echo "✓ GitLab Runnerトークンを更新しました"
            ;;

        --ec2-host)
            if [ -z "$2" ]; then
                echo "エラー: ドメイン名/IPアドレスを指定してください"
                exit 1
            fi
            backup_env
            update_password "EC2_PUBLIC_IP" "$2" "EC2 ドメイン名/IPアドレス"

            # SONAR_HOST_URLも更新
            echo ""
            echo "【SonarQube設定更新】"
            echo "  SONAR_HOST_URL を更新中..."
            sed -i "s|SONAR_HOST_URL=.*|SONAR_HOST_URL=http://$2:8000|" "$ENV_FILE"
            echo "  ✓ SONAR_HOST_URL を更新しました"

            # GitLab Runner設定ファイル更新
            RUNNER_CONFIG="${BASE_DIR}/config/gitlab-runner/config.toml"
            if [ -f "$RUNNER_CONFIG" ]; then
                echo ""
                echo "【GitLab Runner設定更新】"
                echo "  $RUNNER_CONFIG を更新中..."
                sed -i.backup "s|url = \"http://[^\"]*:5003\"|url = \"http://$2:5003\"|" "$RUNNER_CONFIG"
                echo "  ✓ GitLab Runner設定を更新しました"
            fi

            # Maven設定ファイル更新
            MAVEN_CONFIG="${BASE_DIR}/config/maven/settings.xml"
            if [ -f "$MAVEN_CONFIG" ]; then
                echo ""
                echo "【Maven設定更新】"
                echo "  $MAVEN_CONFIG を更新中..."
                sed -i.backup "s|http://[^/]*:8082|http://$2:8082|g" "$MAVEN_CONFIG"
                echo "  ✓ Maven設定ファイルを更新しました"
            fi

            # Maven POM ファイルのNexus URLも更新
            if [ -f "${BASE_DIR}/sample-app/pom.xml" ]; then
                echo ""
                echo "【Maven POM ファイル更新】"
                echo "  sample-app/pom.xml のNexus URLを更新中..."
                # 現在のIPアドレスを検索して新しいものに置換
                sed -i.backup "s|http://[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+:8082|http://$2:8082|g" "${BASE_DIR}/sample-app/pom.xml"
                # ドメイン名の場合も対応
                sed -i "s|http://ec2-[^:]*\.compute[^:]*\.amazonaws\.com:8082|http://$2:8082|g" "${BASE_DIR}/sample-app/pom.xml"
                echo "  ✓ Maven POM ファイルのNexus URLを更新しました"
            fi

            echo ""
            echo "✓ EC2ドメイン名/IPアドレスを更新しました: $2"
            echo ""
            echo "⚠️ 変更後の確認方法:"
            echo "  ./show-credentials.sh"
            echo ""
            echo "⚠️ コンテナの再起動は不要ですが、GitLabなどのURL設定が変わります"
            echo "  sample-appのリモートURLも更新してください:"
            echo "  cd sample-app"
            echo "  git remote set-url origin http://$2:5003/root/sample-app.git"
            ;;

        --all)
            if [ -z "$2" ]; then
                echo "エラー: パスワードを指定してください"
                exit 1
            fi
            update_all_passwords "$2"
            ;;

        --show)
            show_current_settings
            ;;

        -h|--help)
            show_help
            ;;

        *)
            echo "エラー: 不明なオプション: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
