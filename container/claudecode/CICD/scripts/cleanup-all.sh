#!/bin/bash
# ========================================================================
# 完全環境クリーンアップスクリプト
# 全てのコンテナ、ボリューム、設定を削除
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "CICD環境完全クリーンアップ"
echo "=========================================="
echo ""
echo "警告: 以下を削除します:"
echo "  - 全てのコンテナ"
echo "  - 全てのボリューム"
echo "  - GitLab Runner設定"
echo "  - Maven設定"
echo ""

read -p "本当にクリーンアップしますか？ (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "クリーンアップをキャンセルしました。"
    exit 0
fi

# 1. GitLab Runnerの停止
echo "[1/6] GitLab Runnerを停止中..."
if systemctl is-active --quiet gitlab-runner; then
    sudo systemctl stop gitlab-runner
    sudo systemctl disable gitlab-runner
    echo "  ✓ GitLab Runnerを停止しました"
fi

# 2. コンテナの停止と削除
echo "[2/6] コンテナを停止・削除中..."
cd "${BASE_DIR}"
podman-compose down -v 2>/dev/null || true

# 個別コンテナの強制削除
for container in cicd-gitlab cicd-nexus cicd-sonarqube cicd-postgres cicd-pgadmin cicd-mattermost; do
    if podman ps -a | grep -q $container; then
        podman stop $container 2>/dev/null || true
        podman rm -f $container 2>/dev/null || true
    fi
done

echo "  ✓ 全てのコンテナを削除しました"

# 3. ボリュームの削除
echo "[3/6] ボリュームを削除中..."
for volume in $(podman volume ls -q | grep cicd); do
    podman volume rm -f $volume 2>/dev/null || true
done
echo "  ✓ 全てのボリュームを削除しました"

# 4. ネットワークの削除
echo "[4/6] ネットワークを削除中..."
podman network rm cicd_cicd-network 2>/dev/null || true
echo "  ✓ ネットワークを削除しました"

# 5. GitLab Runner設定の削除
echo "[5/6] GitLab Runner設定を削除中..."
if [ -d /etc/gitlab-runner ]; then
    sudo rm -rf /etc/gitlab-runner
    echo "  ✓ GitLab Runner設定を削除しました"
fi

if [ -d /home/gitlab-runner ]; then
    sudo rm -rf /home/gitlab-runner
    echo "  ✓ GitLab Runnerホームディレクトリを削除しました"
fi

# 6. Maven設定の削除（オプション）
echo "[6/6] Maven設定の削除確認..."
read -p "Maven設定も削除しますか？ (yes/no): " DELETE_MAVEN
if [ "$DELETE_MAVEN" = "yes" ]; then
    rm -rf /root/.m2/settings.xml 2>/dev/null || true
    rm -rf /home/ec2-user/.m2/settings.xml 2>/dev/null || true
    sudo rm -rf /home/gitlab-runner/.m2 2>/dev/null || true
    echo "  ✓ Maven設定を削除しました"
fi

echo ""
echo "=========================================="
echo "✓ クリーンアップ完了"
echo "=========================================="
echo ""
echo "残存リソース確認:"
echo "コンテナ:"
podman ps -a
echo ""
echo "ボリューム:"
podman volume ls
echo ""
echo "ネットワーク:"
podman network ls
echo ""
echo "再セットアップする場合:"
echo "  ./setup-from-scratch.sh"
echo ""
