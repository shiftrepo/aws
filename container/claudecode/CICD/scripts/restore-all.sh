#!/bin/bash
# ========================================================================
# 完全環境復元スクリプト
# バックアップから環境を復元
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# 引数チェック
if [ $# -lt 1 ]; then
    echo "使用方法: $0 <バックアップディレクトリ>"
    echo ""
    echo "例: $0 /path/to/backup-20260110-073000"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "エラー: バックアップディレクトリが見つかりません: $BACKUP_DIR"
    exit 1
fi

echo "=========================================="
echo "CICD環境復元"
echo "=========================================="
echo "バックアップ元: ${BACKUP_DIR}"
echo "復元先: ${BASE_DIR}"
echo ""

# 実行確認
read -p "既存の環境を上書きして復元しますか？ (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "復元をキャンセルしました。"
    exit 0
fi

# 1. 既存コンテナの停止と削除
echo "[1/8] 既存のコンテナを停止中..."
cd "${BASE_DIR}"
podman-compose down 2>/dev/null || true
echo "  ✓ コンテナを停止しました"

# 2. 設定ファイルの復元
echo "[2/8] 設定ファイルを復元中..."
cp -r "${BACKUP_DIR}/config" "${BASE_DIR}/"
cp "${BACKUP_DIR}/docker-compose.yml" "${BASE_DIR}/"
cp "${BACKUP_DIR}/.env" "${BASE_DIR}/"
cp "${BACKUP_DIR}/.gitignore" "${BASE_DIR}/" 2>/dev/null || true
cp "${BACKUP_DIR}/README.md" "${BASE_DIR}/" 2>/dev/null || true
echo "  ✓ 設定ファイルを復元しました"

# 3. スクリプトの復元
echo "[3/8] スクリプトを復元中..."
if [ -d "${BACKUP_DIR}/scripts" ]; then
    cp -r "${BACKUP_DIR}/scripts"/* "${BASE_DIR}/scripts/"
    chmod +x "${BASE_DIR}/scripts"/*.sh
    echo "  ✓ スクリプトを復元しました"
fi

# 4. GitLabリポジトリの復元
echo "[4/8] GitLabリポジトリを復元中..."
if [ -f "${BACKUP_DIR}/repos/sample-app.bundle" ]; then
    mkdir -p "${BASE_DIR}/sample-app"
    cd "${BASE_DIR}/sample-app"

    if [ -d ".git" ]; then
        echo "  既存のリポジトリをクリーンアップ中..."
        rm -rf .git
    fi

    git clone "${BACKUP_DIR}/repos/sample-app.bundle" . 2>/dev/null || \
        git init && git pull "${BACKUP_DIR}/repos/sample-app.bundle" master

    # 追加のファイル復元
    if [ -f "${BACKUP_DIR}/repos/sample-app-files.tar.gz" ]; then
        tar xzf "${BACKUP_DIR}/repos/sample-app-files.tar.gz"
    fi

    cd "${BASE_DIR}"
    echo "  ✓ リポジトリを復元しました"
fi

# 5. Maven設定の復元
echo "[5/8] Maven設定を復元中..."
mkdir -p /root/.m2 /home/ec2-user/.m2 /home/gitlab-runner/.m2

if [ -f "${BACKUP_DIR}/config/maven-settings.xml" ]; then
    cp "${BACKUP_DIR}/config/maven-settings.xml" /home/ec2-user/.m2/settings.xml
    echo "  ✓ ec2-user Maven設定を復元"
fi

if [ -f "${BACKUP_DIR}/config/maven-settings-root.xml" ]; then
    cp "${BACKUP_DIR}/config/maven-settings-root.xml" /root/.m2/settings.xml
    echo "  ✓ root Maven設定を復元"
fi

if [ -f "${BACKUP_DIR}/config/maven-settings-runner.xml" ]; then
    sudo cp "${BACKUP_DIR}/config/maven-settings-runner.xml" /home/gitlab-runner/.m2/settings.xml
    sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner/.m2 2>/dev/null || true
    echo "  ✓ GitLab Runner Maven設定を復元"
fi

# 6. GitLab Runner設定の復元
echo "[6/8] GitLab Runner設定を復元中..."
if [ -f "${BACKUP_DIR}/config/runner-config.toml" ]; then
    sudo mkdir -p /etc/gitlab-runner
    sudo cp "${BACKUP_DIR}/config/runner-config.toml" /etc/gitlab-runner/config.toml
    echo "  ✓ GitLab Runner設定を復元しました"
fi

# 7. コンテナの起動
echo "[7/8] コンテナを起動中..."
cd "${BASE_DIR}"
podman-compose up -d

echo "  コンテナ起動待機中（90秒）..."
sleep 90

# 8. GitLabバックアップの復元（オプション）
echo "[8/8] GitLabバックアップの復元を確認中..."
if [ -f "${BACKUP_DIR}/volumes/gitlab-backup.tar" ]; then
    read -p "GitLabバックアップを復元しますか？ (yes/no): " RESTORE_GITLAB
    if [ "$RESTORE_GITLAB" = "yes" ]; then
        echo "  GitLabコンテナにバックアップをコピー中..."
        BACKUP_FILE=$(basename "${BACKUP_DIR}/volumes/gitlab-backup.tar")
        podman cp "${BACKUP_DIR}/volumes/gitlab-backup.tar" cicd-gitlab:/var/opt/gitlab/backups/

        echo "  GitLabバックアップを復元中（数分かかります）..."
        podman exec cicd-gitlab gitlab-backup restore BACKUP=${BACKUP_FILE%.tar} force=yes
        podman restart cicd-gitlab

        echo "  ✓ GitLabバックアップを復元しました"
        echo "  GitLab再起動待機中（60秒）..."
        sleep 60
    fi
fi

# GitLab Runnerサービスの再起動
if systemctl is-active --quiet gitlab-runner; then
    sudo systemctl restart gitlab-runner
    echo "  ✓ GitLab Runnerを再起動しました"
fi

echo ""
echo "=========================================="
echo "✓ 復元完了"
echo "=========================================="
echo ""
echo "環境情報:"
cat "${BACKUP_DIR}/environment-info.txt" 2>/dev/null || echo "  環境情報ファイルが見つかりません"
echo ""
echo "コンテナ状態:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "次のステップ:"
echo "  1. サービスにアクセス可能か確認"
echo "  2. GitLabでsample-appプロジェクトを確認"
echo "  3. パイプラインが正常に動作するかテスト"
echo ""
