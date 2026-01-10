#!/bin/bash
# ========================================================================
# ゼロから完全環境構築スクリプト
# 新しいEC2インスタンスで実行可能
# パスワードは環境変数から取得
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${BASE_DIR}/.env"

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
echo "[1/11] システムパッケージをインストール中..."
sudo yum update -y
sudo yum install -y git wget curl podman podman-compose maven java-17-openjdk-devel python3 python3-pip

# Docker Composeのインストール
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 2. SELinux設定
echo "[2/11] SELinux設定を調整中..."
if [ "$(getenforce)" != "Disabled" ]; then
    sudo setenforce 0
    sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
    echo "  ✓ SELinuxをPermissiveに設定"
fi

# 3. Podmanソケットの有効化
echo "[3/11] Podmanソケットを有効化中..."
sudo systemctl enable --now podman.socket
sudo systemctl status podman.socket --no-pager | head -5

# 4. 必要なディレクトリの作成
echo "[4/11] ディレクトリ構造を作成中..."
mkdir -p "${BASE_DIR}"/{config/{gitlab,nexus,sonarqube,postgres,pgadmin,gitlab-runner,maven},volumes,scripts}

# 5. 管理者パスワードの設定
echo "[5/11] 管理者パスワードを設定中..."
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

# 6. 環境変数ファイルの作成または更新
echo "[6/11] 環境変数ファイルを作成中..."
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")

cat > "$ENV_FILE" << EOF
# PostgreSQL Configuration
POSTGRES_PASSWORD=cicd_postgres_pass_2026
POSTGRES_DB=cicddb
POSTGRES_USER=cicduser

# SonarQube Database
SONAR_DB_PASSWORD=sonar_db_pass_2026

# Sample App Database
SAMPLE_DB_PASSWORD=sample_app_pass_2026

# pgAdmin Configuration
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=pgadmin_pass_2026

# Nexus Configuration
NEXUS_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Configuration
SONARQUBE_ADMIN_PASSWORD=${ADMIN_PASSWORD}

# GitLab Configuration
GITLAB_ROOT_PASSWORD=${ADMIN_PASSWORD}

# SonarQube Token (初回セットアップ後に更新)
SONAR_TOKEN=

# GitLab Runner Token (GitLab UIから取得して設定)
RUNNER_TOKEN=

# External Access
EC2_PUBLIC_IP=${EC2_IP}
EOF

echo "  ✓ .env ファイルを作成しました"

# 7. Docker Composeファイルの確認
echo "[7/11] Docker Compose設定を確認中..."
if [ ! -f "${BASE_DIR}/docker-compose.yml" ]; then
    echo "  ✗ docker-compose.yml が見つかりません"
    echo "  バックアップから復元するか、手動で作成してください"
    exit 1
fi
echo "  ✓ docker-compose.yml が存在します"

# 8. コンテナの起動
echo "[8/11] コンテナを起動中..."
cd "${BASE_DIR}"
podman-compose down 2>/dev/null || true
podman-compose up -d

echo "  コンテナ起動待機中（90秒）..."
sleep 90

# コンテナ状態確認
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 9. GitLab Runnerのインストール
echo "[9/11] GitLab Runnerをインストール中..."
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
ExecStart=/usr/local/bin/gitlab-runner run --config /etc/gitlab-runner/config.toml --working-directory /home/gitlab-runner --service gitlab-runner --user root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOFSERVICE

# 10. Maven設定
echo "[10/11] Maven設定を作成中..."
mkdir -p /root/.m2 /home/ec2-user/.m2 /home/gitlab-runner/.m2

# .envから管理者パスワードを読み込んでMaven settings.xmlを生成
if [ -f "${BASE_DIR}/config/maven/settings.xml" ]; then
    # settings.xmlのパスワードを環境変数の値で置換
    sed "s/Degital2026!/${ADMIN_PASSWORD}/g" "${BASE_DIR}/config/maven/settings.xml" > /root/.m2/settings.xml
    sed "s/Degital2026!/${ADMIN_PASSWORD}/g" "${BASE_DIR}/config/maven/settings.xml" > /home/ec2-user/.m2/settings.xml
    sudo sed "s/Degital2026!/${ADMIN_PASSWORD}/g" "${BASE_DIR}/config/maven/settings.xml" > /home/gitlab-runner/.m2/settings.xml
    sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner/.m2 2>/dev/null || true
    echo "  ✓ Maven settings.xml を配置しました"
else
    echo "  ⚠ Maven settings.xml が見つかりません"
fi

# 11. 完了メッセージ
echo "[11/11] セットアップ完了チェック..."
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
echo "     http://${EC2_IP}:8082"
echo "     初回ログイン後、パスワード変更が求められる場合があります"
echo ""
echo "  2. SonarQubeにログイン:"
echo "     http://${EC2_IP}:8000"
echo "     初回ログイン後、パスワード変更が必要です"
echo ""
echo "  3. GitLabにログイン:"
echo "     http://${EC2_IP}:5003"
echo "     rootユーザーでログインしてください"
echo ""
echo "  4. GitLab Runnerの登録:"
echo "     sudo gitlab-runner register \\"
echo "       --url http://${EC2_IP}:5003 \\"
echo "       --executor shell \\"
echo "       --description 'CICD Shell Runner'"
echo ""
echo "  5. sample-appプロジェクトをGitLabにプッシュ:"
echo "     cd ${BASE_DIR}/sample-app"
echo "     git remote set-url origin http://${EC2_IP}:5003/root/sample-app.git"
echo "     git push -u origin master"
echo ""
echo "コンテナ状態:"
podman ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "環境変数ファイル: ${ENV_FILE}"
echo ""

# 認証情報をファイルに出力
echo "認証情報をファイルに出力中..."
if [ -f "${SCRIPT_DIR}/show-credentials.sh" ]; then
    bash "${SCRIPT_DIR}/show-credentials.sh" --file
    echo ""
    echo "✓ 認証情報ファイル: ${BASE_DIR}/credentials.txt"
    echo "  内容を確認: cat ${BASE_DIR}/credentials.txt"
    echo "  確認後は削除推奨: rm ${BASE_DIR}/credentials.txt"
else
    echo "⚠️ show-credentials.sh が見つかりません"
fi
echo ""
