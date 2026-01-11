#!/bin/bash
# ========================================================================
# ゼロから完全環境構築スクリプト
# 新しいEC2インスタンスで実行可能
# パスワードは環境変数から取得
# ========================================================================

set -e

# Bash環境最適化設定（permission denied エラー対策）
export SHELL=/bin/bash
export LC_ALL=C
umask 0022

# 権限確保と環境チェック
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ このスクリプトはroot権限で実行してください"
    echo "実行方法: sudo $0"
    exit 1
fi

# シェル環境の権限確認
chmod +x "$0" 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${BASE_DIR}/.env"

# スクリプトディレクトリ内のファイルに実行権限を付与（permission denied対策）
if [ -d "${SCRIPT_DIR}" ]; then
    find "${SCRIPT_DIR}" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
fi

# エラーハンドリング関数（permission denied エラー対策）
handle_command_error() {
    local exit_code=$1
    local command="$2"
    if [ $exit_code -eq 126 ]; then
        echo "  ⚠ Permission denied エラーが発生しました"
        echo "  コマンド: $command"
        echo "  対処: 権限を確認して再実行してください"
        return 1
    elif [ $exit_code -ne 0 ]; then
        echo "  ❌ コマンドエラー (終了コード: $exit_code)"
        echo "  コマンド: $command"
        return $exit_code
    fi
    return 0
}

echo "=========================================="
echo "CICD環境完全セットアップ"
echo "=========================================="
echo ""

# 実行確認
read -p "新規環境をセットアップしますか？ (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "セットアップをキャンセルしました。"
    exit 0
fi

# 1. システム前提条件のインストール
echo "[1/12] システムパッケージをインストール中..."
sudo yum update -y
sudo yum install -y git wget curl podman podman-compose maven java-17-openjdk-devel python3 python3-pip

# Docker Composeのインストール
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 2. SELinux設定
echo "[2/12] SELinux設定を調整中..."
if [ "$(getenforce)" != "Disabled" ]; then
    sudo setenforce 0
    sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
    echo "  ✓ SELinuxをPermissiveに設定"
fi

# 3. Podmanソケットの有効化
echo "[3/12] Podmanソケットを有効化中..."
sudo systemctl enable --now podman.socket
sudo systemctl status podman.socket --no-pager | head -5

# 4. 必要なディレクトリの作成
echo "[4/12] ディレクトリ構造を作成中..."
mkdir -p "${BASE_DIR}"/{config/{gitlab,nexus,sonarqube,postgres,pgadmin,gitlab-runner,maven},volumes,scripts}

# 5. 管理者パスワードの設定
echo "[5/12] 管理者パスワードを設定中..."
if [ ! -f "$ENV_FILE" ] || ! grep -q "GITLAB_ROOT_PASSWORD" "$ENV_FILE"; then
    echo ""
    echo "管理者パスワードを設定してください（GitLab、Nexus、SonarQubeで共通使用）"
    echo "※ 最低8文字、英数字記号を含むことを推奨"
    echo ""

    while true; do
        read -s -p "管理者パスワード: " ADMIN_PASSWORD
        echo ""
        read -s -p "管理者パスワード（確認）: " ADMIN_PASSWORD_CONFIRM
        echo ""

        if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ]; then
            if [ ${#ADMIN_PASSWORD} -ge 8 ]; then
                break
            else
                echo "エラー: パスワードは8文字以上にしてください"
            fi
        else
            echo "エラー: パスワードが一致しません"
        fi
    done

    echo "  ✓ 管理者パスワードを設定しました"
else
    echo "  ✓ 既存の .env ファイルからパスワードを読み込みます"
    source "$ENV_FILE"
    ADMIN_PASSWORD="${GITLAB_ROOT_PASSWORD}"
fi

# 6. EC2ドメイン名/IPアドレスの設定
echo "[6/12] EC2ドメイン名/IPアドレスを設定中..."
if [ ! -f "$ENV_FILE" ] || ! grep -q "EC2_PUBLIC_IP" "$ENV_FILE"; then
    echo ""
    echo "EC2インスタンスのドメイン名またはIPアドレスを入力してください"
    echo "例: ec2-xx-xx-xx-xx.compute-1.amazonaws.com"
    echo "例: 192.168.1.100"
    echo ""
    echo "※ 入力しない場合は自動検出します（EC2メタデータから取得）"
    echo ""

    read -p "ドメイン名/IPアドレス: " EC2_HOST

    if [ -z "$EC2_HOST" ]; then
        # 入力がない場合は自動検出
        echo "  自動検出を試行中..."
        EC2_HOST=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-ipv4 || echo "")

        if [ -z "$EC2_HOST" ]; then
            echo "  ⚠️ 自動検出に失敗しました。localhostを使用します"
            EC2_HOST="localhost"
        else
            echo "  ✓ 自動検出成功: $EC2_HOST"
        fi
    else
        # 入力があった場合は検証
        echo "  入力されたホスト: $EC2_HOST"
        echo "  ✓ ドメイン名/IPアドレスを設定しました"
    fi
else
    echo "  ✓ 既存の .env ファイルからドメイン名/IPを読み込みます"
    source "$ENV_FILE"
    EC2_HOST="${EC2_PUBLIC_IP}"

    # 既存設定でも最新のEC2アドレスを確認
    echo "  現在の設定値を確認中..."
    CURRENT_EC2_IP=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-ipv4 || echo "")

    if [ -n "$CURRENT_EC2_IP" ] && [ "$EC2_HOST" != "$CURRENT_EC2_IP" ]; then
        echo "  ⚠️ EC2アドレスが変更されている可能性があります"
        echo "     設定値: $EC2_HOST"
        echo "     実際値: $CURRENT_EC2_IP"
        echo ""
        read -p "最新のEC2アドレス ($CURRENT_EC2_IP) に更新しますか？ (yes/no): " UPDATE_IP

        if [ "$UPDATE_IP" = "yes" ]; then
            EC2_HOST="$CURRENT_EC2_IP"
            echo "  ✓ EC2アドレスを更新しました: $EC2_HOST"
        else
            echo "  既存の設定値を維持します: $EC2_HOST"
        fi
    elif [ -n "$CURRENT_EC2_IP" ]; then
        echo "  ✓ EC2アドレスは最新です: $EC2_HOST"
    else
        echo "  ⚠️ EC2メタデータ取得に失敗、既存設定を使用: $EC2_HOST"
    fi
fi

echo ""
echo "  使用するホスト: $EC2_HOST"
echo ""

# 7. 環境変数ファイルの作成または更新
echo "[7/12] 環境変数ファイルを作成中..."

if [ ! -f "$ENV_FILE" ]; then
    # 新規作成
    cat > "$ENV_FILE" << EOF
# PostgreSQL Configuration
POSTGRES_PASSWORD=${ADMIN_PASSWORD}
POSTGRES_DB=cicddb
POSTGRES_USER=cicduser

# SonarQube Database
SONAR_DB_PASSWORD=${ADMIN_PASSWORD}

# Sample App Database
SAMPLE_DB_PASSWORD=${ADMIN_PASSWORD}

# Mattermost Database
MATTERMOST_DB_PASSWORD=${ADMIN_PASSWORD}

# pgAdmin Configuration
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=${ADMIN_PASSWORD}

# Nexus Configuration
NEXUS_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Configuration
SONARQUBE_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# GitLab Configuration
GITLAB_ROOT_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Token (初回セットアップ後に更新)
SONAR_TOKEN=

# SonarQube CI/CD Configuration (動的に設定)
SONAR_HOST_URL=http://${EC2_HOST}:8000
SONAR_PROJECT_KEY=sample-app-backend

# GitLab Runner Token (GitLab UIから取得して設定)
RUNNER_TOKEN=

# External Access
EC2_PUBLIC_IP=${EC2_HOST}
EOF

    echo "  ✓ .env ファイルを作成しました"
else
    # 既存のファイルがある場合は、必要な項目のみ更新
    echo "  ✓ 既存の .env ファイルを保持します"

    # 既存のトークンを読み込み
    source "$ENV_FILE"
    EXISTING_SONAR_TOKEN="${SONAR_TOKEN}"
    EXISTING_RUNNER_TOKEN="${RUNNER_TOKEN}"

    # バックアップ作成
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d%H%M%S)"

    # 既存のトークンを保持しながら更新
    cat > "$ENV_FILE" << EOF
# PostgreSQL Configuration
POSTGRES_PASSWORD=${ADMIN_PASSWORD}
POSTGRES_DB=cicddb
POSTGRES_USER=cicduser

# SonarQube Database
SONAR_DB_PASSWORD=${ADMIN_PASSWORD}

# Sample App Database
SAMPLE_DB_PASSWORD=${ADMIN_PASSWORD}

# Mattermost Database
MATTERMOST_DB_PASSWORD=${ADMIN_PASSWORD}

# pgAdmin Configuration
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=${ADMIN_PASSWORD}

# Nexus Configuration
NEXUS_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Configuration
SONARQUBE_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# GitLab Configuration
GITLAB_ROOT_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Token (初回セットアップ後に更新)
SONAR_TOKEN=${EXISTING_SONAR_TOKEN}

# SonarQube CI/CD Configuration (動的に設定)
SONAR_HOST_URL=http://${EC2_HOST}:8000
SONAR_PROJECT_KEY=sample-app-backend

# GitLab Runner Token (GitLab UIから取得して設定)
RUNNER_TOKEN=${EXISTING_RUNNER_TOKEN}

# External Access
EC2_PUBLIC_IP=${EC2_HOST}
EOF

    echo "  ✓ .env ファイルを更新しました（トークンは保持）"
fi

# 7. Docker Composeファイルの確認
echo "[8/12] Docker Compose設定を確認中..."
if [ ! -f "${BASE_DIR}/docker-compose.yml" ]; then
    echo "  ✗ docker-compose.yml が見つかりません"
    echo "  バックアップから復元するか、手動で作成してください"
    exit 1
fi
echo "  ✓ docker-compose.yml が存在します"

# PostgreSQL初期化スクリプトの生成
echo "  PostgreSQL初期化スクリプトを生成中..."
if [ -f "${BASE_DIR}/config/postgres/init.sql" ]; then
    # プレースホルダーを環境変数で置換
    sed -e "s/__SONAR_DB_PASSWORD__/${ADMIN_PASSWORD}/g" \
        -e "s/__SAMPLE_DB_PASSWORD__/${ADMIN_PASSWORD}/g" \
        -e "s/__MATTERMOST_DB_PASSWORD__/${ADMIN_PASSWORD}/g" \
        "${BASE_DIR}/config/postgres/init.sql" > "${BASE_DIR}/config/postgres/init-runtime.sql"
    echo "  ✓ PostgreSQL初期化スクリプトを生成しました"
else
    echo "  ⚠ PostgreSQL初期化スクリプトのテンプレートが見つかりません"
fi

# 8. コンテナの起動
echo "[9/12] コンテナを起動中..."
cd "${BASE_DIR}"
podman-compose down 2>/dev/null || true
podman-compose up -d

echo "  コンテナ起動待機中（90秒）..."
sleep 90

# コンテナ状態確認
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 9. GitLab Runnerのインストール
echo "[10/12] GitLab Runnerをインストール中..."
if ! command -v gitlab-runner &> /dev/null; then
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" | sudo bash
    sudo yum install -y gitlab-runner
    echo "  ✓ GitLab Runnerをインストールしました"
else
    echo "  ✓ GitLab Runnerは既にインストール済みです"
fi

# GitLab Runnerサービスの設定
sudo mkdir -p /home/gitlab-runner/builds
sudo useradd --system --shell /bin/bash --home /home/gitlab-runner gitlab-runner 2>/dev/null || true

# GitLab Runner systemdサービスの作成
sudo tee /etc/systemd/system/gitlab-runner.service > /dev/null << 'EOFSERVICE'
[Unit]
Description=GitLab Runner
After=network.target

[Service]
Type=simple
User=root
# CRITICAL: GitLabRunnerのパスは /usr/local/bin/gitlab-runner が正しい
# /usr/bin/gitlab-runner は存在しない - 絶対に変更禁止
# 確認コマンド: which gitlab-runner → /usr/local/bin/gitlab-runner
# 実行ファイル: /usr/local/bin/gitlab-runner (ELF 64-bit LSB executable)
# FIXED: User=root に変更 - Maven build時の権限問題を解決
ExecStart=/usr/local/bin/gitlab-runner run --config /etc/gitlab-runner/config.toml --working-directory /home/gitlab-runner --service gitlab-runner --user root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOFSERVICE

# GitLab Runner設定ディレクトリとサービス準備
sudo mkdir -p /etc/gitlab-runner
sudo chown gitlab-runner:gitlab-runner /home/gitlab-runner/builds
sudo chown gitlab-runner:gitlab-runner /home/gitlab-runner
sudo systemctl daemon-reload
sudo systemctl enable gitlab-runner
echo "  ✓ GitLab Runnerサービスを設定しました"

# 10. Maven設定
echo "[11/12] Maven設定を作成中..."
mkdir -p /root/.m2 /home/ec2-user/.m2
sudo mkdir -p /home/gitlab-runner/.m2
sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner/.m2

# .envから管理者パスワードとドメイン名を読み込んでMaven settings.xmlを生成
if [ -f "${BASE_DIR}/config/maven/settings.xml" ]; then
    # settings.xmlのパスワードとIPアドレスを環境変数の値で置換
    sed -e "s/Degital2026!/${ADMIN_PASSWORD}/g" \
        -e "s/34\.205\.156\.203/${EC2_HOST}/g" \
        "${BASE_DIR}/config/maven/settings.xml" > /root/.m2/settings.xml

    sed -e "s/Degital2026!/${ADMIN_PASSWORD}/g" \
        -e "s/34\.205\.156\.203/${EC2_HOST}/g" \
        "${BASE_DIR}/config/maven/settings.xml" > /home/ec2-user/.m2/settings.xml

    sudo sed -e "s/Degital2026!/${ADMIN_PASSWORD}/g" \
            -e "s/34\.205\.156\.203/${EC2_HOST}/g" \
            "${BASE_DIR}/config/maven/settings.xml" | sudo tee /home/gitlab-runner/.m2/settings.xml > /dev/null

    sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner/.m2 2>/dev/null || true
    echo "  ✓ Maven settings.xml を配置しました（パスワード、ドメイン名を置換）"
else
    echo "  ⚠ Maven settings.xml が見つかりません"
fi

# Maven POM ファイルのNexus URLを更新
if [ -f "${BASE_DIR}/sample-app/pom.xml" ]; then
    echo "  Maven POM ファイルのNexus URLを更新中..."
    sed -i.backup "s|http://34\.205\.156\.203:8082|http://${EC2_HOST}:8082|g" "${BASE_DIR}/sample-app/pom.xml"
    echo "  ✓ Maven POM ファイルのNexus URLを更新しました"
else
    echo "  ⚠ sample-app/pom.xml が見つかりません"
fi

# 11. 完了メッセージ
echo "[12/12] セットアップ完了チェック..."
sleep 5

echo ""
echo "=========================================="
echo "✓ セットアップ完了"
echo "=========================================="
echo ""
echo "管理者認証情報:"
echo "  ユーザー名: admin (Nexus/SonarQube) / root (GitLab)"
echo "  パスワード: [設定したパスワード]"
echo ""
echo "次のステップ:"
echo "  1. Nexusにログイン:"
echo "     http://${EC2_HOST}:8082"
echo "     ユーザー名: admin"
echo "     パスワード: ${ADMIN_PASSWORD}"
echo "     ※ 初回起動時は admin123 ですが、手動で変更してください"
echo ""
echo "  2. SonarQubeにログイン:"
echo "     http://${EC2_HOST}:8000"
echo "     初回ログイン後、パスワード変更が必要です"
echo ""
echo "  3. GitLabにログイン:"
echo "     http://${EC2_HOST}:5003"
echo "     rootユーザーでログインしてください"
echo ""
echo "  4. GitLab Runnerの登録:"
echo "     sudo gitlab-runner register \\"
echo "       --url http://${EC2_HOST}:5003 \\"
echo "       --executor shell \\"
echo "       --description 'CICD Shell Runner'"
echo ""
echo "  5. GitLab CI/CD 環境変数の設定:"
echo "     プロジェクト > Settings > CI/CD > Variables で以下を追加:"
echo "     NEXUS_ADMIN_PASSWORD (Masked): ${ADMIN_PASSWORD}"
echo "     SONAR_TOKEN (Masked): <SonarQubeで生成したトークン>"
echo ""
echo "  6. sample-appプロジェクトをGitLabにプッシュ:"
echo "     # 独立したディレクトリでGitLab登録（ユーザーリポジトリと分離）"
echo "     ${BASE_DIR}/scripts/setup-sample-app.sh ${EC2_HOST} ${ADMIN_PASSWORD}"
echo ""
echo "     ※ 自動スクリプトが実行されます（手動実行の場合）:"
echo "     mkdir -p /tmp/gitlab-sample-app"
echo "     cp -r ${BASE_DIR}/sample-app/* /tmp/gitlab-sample-app/"
echo "     cd /tmp/gitlab-sample-app"
echo "     git init && git add ."
echo "     git commit -m 'Initial commit for GitLab CI/CD'"
echo "     git remote add origin http://${EC2_HOST}:5003/root/sample-app.git"
echo "     git push -u origin master"
echo ""
echo "コンテナ状態:"
podman ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "環境変数ファイル: ${ENV_FILE}"
echo ""

# Step 13: GitLab Runner権限設定（CI/CD最適化）
echo ""
echo "=========================================="
echo "Step 13: GitLab Runner権限設定"
echo "=========================================="

# GitLab Runner Mavenディレクトリ権限設定
echo "GitLab Runner権限を設定中..."
echo "  💡 目的: Maven Local Repository権限エラーの防止"

# gitlab-runnerユーザーの存在確認
if id gitlab-runner >/dev/null 2>&1; then
    # .m2ディレクトリの作成と権限設定
    echo "  🔧 GitLab Runner用Mavenディレクトリを設定中..."
    sudo mkdir -p /home/gitlab-runner/.m2/repository
    sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner/.m2
    sudo chmod -R 755 /home/gitlab-runner/.m2

    # 権限確認
    if [ -d "/home/gitlab-runner/.m2" ] && [ "$(stat -c %U /home/gitlab-runner/.m2)" = "gitlab-runner" ]; then
        echo "  ✅ GitLab Runner権限設定完了"
        echo "     Maven Local Repository権限エラーが解決されました"
    else
        echo "  ⚠️ GitLab Runner権限設定に失敗しました"
    fi
else
    echo "  ⚠️ gitlab-runnerユーザーが見つかりません"
    echo "     GitLab Runnerがインストールされていない可能性があります"
fi

echo ""
echo "✅ GitLab Runner権限設定完了"
echo "  📋 Maven権限エラー防止策が適用されました"
echo ""

# 認証情報をファイルに出力
echo "=========================================="
echo "認証情報ファイル出力"
echo "=========================================="
echo "認証情報をファイルに出力中..."
if [ -f "${SCRIPT_DIR}/utils/show-credentials.sh" ]; then
    bash "${SCRIPT_DIR}/utils/show-credentials.sh" --file
    echo ""
    echo "✓ 認証情報ファイル: ${BASE_DIR}/credentials.txt"
    echo "  内容を確認: cat ${BASE_DIR}/credentials.txt"
    echo "  確認後は削除推奨: rm ${BASE_DIR}/credentials.txt"
else
    echo "⚠️ utils/show-credentials.sh が見つかりません"
fi
echo ""
