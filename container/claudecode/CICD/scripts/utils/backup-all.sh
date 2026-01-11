#!/bin/bash
# ========================================================================
# 完全環境バックアップスクリプト
# 全ての設定、データ、リポジトリをバックアップ
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKUP_DIR="${BASE_DIR}/backup-$(date +%Y%m%d-%H%M%S)"

echo "=========================================="
echo "CICD環境完全バックアップ"
echo "=========================================="
echo "バックアップ先: ${BACKUP_DIR}"
echo ""

# バックアップディレクトリ作成
mkdir -p "${BACKUP_DIR}"/{config,volumes,repos,scripts}

# 1. 設定ファイルのバックアップ
echo "[1/7] 設定ファイルをバックアップ中..."
cp -r "${BASE_DIR}/config" "${BACKUP_DIR}/"
cp "${BASE_DIR}/docker-compose.yml" "${BACKUP_DIR}/"
cp "${BASE_DIR}/.env" "${BACKUP_DIR}/"
cp "${BASE_DIR}/.gitignore" "${BACKUP_DIR}/" 2>/dev/null || true
cp "${BASE_DIR}/README.md" "${BACKUP_DIR}/" 2>/dev/null || true

# 2. GitLab リポジトリのバックアップ（sample-app）
echo "[2/7] GitLabリポジトリをバックアップ中..."
if [ -d "${BASE_DIR}/sample-app/.git" ]; then
    cd "${BASE_DIR}/sample-app"
    git bundle create "${BACKUP_DIR}/repos/sample-app.bundle" --all
    tar czf "${BACKUP_DIR}/repos/sample-app-files.tar.gz" \
        --exclude='.git' \
        --exclude='target' \
        --exclude='node_modules' \
        .
    cd "${BASE_DIR}"
fi

# 3. GitLab データのバックアップ
echo "[3/7] GitLabデータをバックアップ中..."
if podman ps | grep -q cicd-gitlab; then
    podman exec cicd-gitlab gitlab-backup create SKIP=registry 2>/dev/null || true

    # バックアップファイルをホストにコピー
    LATEST_BACKUP=$(podman exec cicd-gitlab ls -t /var/opt/gitlab/backups/ | head -1)
    if [ ! -z "$LATEST_BACKUP" ]; then
        podman cp cicd-gitlab:/var/opt/gitlab/backups/${LATEST_BACKUP} \
            "${BACKUP_DIR}/volumes/gitlab-backup.tar"
        echo "  ✓ GitLabバックアップ: ${LATEST_BACKUP}"
    fi
fi

# 4. GitLab Runner設定のバックアップ
echo "[4/7] GitLab Runner設定をバックアップ中..."
if [ -f /etc/gitlab-runner/config.toml ]; then
    sudo cp /etc/gitlab-runner/config.toml "${BACKUP_DIR}/config/runner-config.toml"
    sudo chown $(whoami):$(whoami) "${BACKUP_DIR}/config/runner-config.toml"
fi

# 5. Maven settings.xmlのバックアップ
echo "[5/7] Maven設定をバックアップ中..."
[ -f /home/ec2-user/.m2/settings.xml ] && \
    cp /home/ec2-user/.m2/settings.xml "${BACKUP_DIR}/config/maven-settings.xml"
[ -f /root/.m2/settings.xml ] && \
    cp /root/.m2/settings.xml "${BACKUP_DIR}/config/maven-settings-root.xml"
[ -f /home/gitlab-runner/.m2/settings.xml ] && \
    sudo cp /home/gitlab-runner/.m2/settings.xml "${BACKUP_DIR}/config/maven-settings-runner.xml" && \
    sudo chown $(whoami):$(whoami) "${BACKUP_DIR}/config/maven-settings-runner.xml"

# 6. 環境情報の記録
echo "[6/7] 環境情報を記録中..."
cat > "${BACKUP_DIR}/environment-info.txt" << EOF
# CICD環境情報
バックアップ日時: $(date)
ホスト名: $(hostname)
OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
カーネル: $(uname -r)
Podmanバージョン: $(podman --version)
Dockerバージョン: $(docker --version 2>/dev/null || echo "Not installed")
Mavenバージョン: $(mvn --version 2>/dev/null | head -1 || echo "Not installed")
Gitバージョン: $(git --version)

# コンテナ状態
$(podman ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")

# ボリューム
$(podman volume ls)

# ネットワーク
$(podman network ls)

# EC2 Public IP
$(grep EC2_PUBLIC_IP "${BASE_DIR}/.env" || echo "EC2_PUBLIC_IP=Not set")
EOF

# 7. スクリプトのバックアップ
echo "[7/7] スクリプトをバックアップ中..."
cp -r "${BASE_DIR}/scripts" "${BACKUP_DIR}/"

# バックアップアーカイブの作成
echo ""
echo "バックアップアーカイブを作成中..."
cd "$(dirname "${BACKUP_DIR}")"
tar czf "$(basename ${BACKUP_DIR}).tar.gz" "$(basename ${BACKUP_DIR})"

echo ""
echo "=========================================="
echo "✓ バックアップ完了"
echo "=========================================="
echo "バックアップディレクトリ: ${BACKUP_DIR}"
echo "バックアップアーカイブ: ${BACKUP_DIR}.tar.gz"
echo ""
echo "復元方法:"
echo "  1. バックアップを新環境にコピー"
echo "  2. tar xzf backup-YYYYMMDD-HHMMSS.tar.gz"
echo "  3. cd backup-YYYYMMDD-HHMMSS"
echo "  4. ./restore-all.sh backup-YYYYMMDD-HHMMSS"
echo ""
