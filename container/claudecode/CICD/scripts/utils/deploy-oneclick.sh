#!/bin/bash
# ========================================================================
# ワンクリックデプロイメントスクリプト
# クリーンアップ → セットアップ → バックアップまで一括実行
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "CICD環境ワンクリックデプロイメント"
echo "=========================================="
echo ""
echo "実行内容:"
echo "  1. 既存環境のバックアップ"
echo "  2. 環境のクリーンアップ"
echo "  3. ゼロからセットアップ"
echo ""

read -p "続行しますか？ (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "デプロイをキャンセルしました。"
    exit 0
fi

# 1. 既存環境が存在する場合はバックアップ
if [ -f "${BASE_DIR}/docker-compose.yml" ] && podman ps | grep -q cicd; then
    echo ""
    echo "=========================================="
    echo "Step 1: 既存環境のバックアップ"
    echo "=========================================="
    "${SCRIPT_DIR}/utils/backup-all.sh"
else
    echo ""
    echo "Step 1: スキップ（既存環境なし）"
fi

# 2. クリーンアップ（対話なし）
echo ""
echo "=========================================="
echo "Step 2: 環境のクリーンアップ"
echo "=========================================="
echo "yes" | "${SCRIPT_DIR}/cleanup-all.sh" || true
echo "no" # Maven設定は保持

# 3. セットアップ
echo ""
echo "=========================================="
echo "Step 3: ゼロからセットアップ"
echo "=========================================="
echo "yes" | "${SCRIPT_DIR}/setup-from-scratch.sh"

echo ""
echo "=========================================="
echo "✓ デプロイメント完了"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "  1. 各サービスにアクセスして初期設定を実施"
echo "  2. GitLab Runnerを登録"
echo "  3. sample-appをGitLabにプッシュ"
echo "  4. パイプラインをテスト"
echo ""
