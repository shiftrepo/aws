#!/bin/bash
# ========================================================================
# サンプルアプリ パイプライン実行スクリプト
# マスターリポジトリから /tmp にコピーして GitLab パイプラインを実行
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="/tmp/gitlab-sample-app"
BRANCH_NAME="feature/cicd-test-$(date +%Y%m%d-%H%M%S)"

# 環境変数を読み込み
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
else
    echo "❌ .env ファイルが見つかりません: $BASE_DIR/.env"
    exit 1
fi

# 必要な環境変数の確認
if [ -z "$EC2_PUBLIC_IP" ] || [ -z "$GITLAB_ROOT_PASSWORD" ]; then
    echo "❌ 必要な環境変数が設定されていません"
    echo "   EC2_PUBLIC_IP: ${EC2_PUBLIC_IP:-未設定}"
    echo "   GITLAB_ROOT_PASSWORD: ${GITLAB_ROOT_PASSWORD:-未設定}"
    exit 1
fi

GITLAB_URL="http://$EC2_PUBLIC_IP:5003"
PROJECT_PATH="root/sample-app"

echo "=========================================="
echo "サンプルアプリ パイプライン実行"
echo "EC2ホスト: $EC2_PUBLIC_IP"
echo "=========================================="

# 1. 作業ディレクトリの準備
echo "[1/4] 作業ディレクトリを準備中..."

if [ -d "$TEMP_DIR" ]; then
    echo "  既存の /tmp/gitlab-sample-app を削除中..."
    rm -rf "$TEMP_DIR"
fi

echo "  マスターリポジトリから /tmp にコピー中..."
rsync -a --exclude='.git' --exclude='.m2' --exclude='target' --exclude='node_modules' \
    "$BASE_DIR/sample-app/" "$TEMP_DIR/"

cd "$TEMP_DIR"
echo "  ✓ 作業ディレクトリ準備完了: $TEMP_DIR"

# 2. Git リポジトリの初期化
echo "[2/4] Git リポジトリを初期化中..."

git init
git config user.name "CI/CD Automation"
git config user.email "cicd@example.com"

# GitLab リモートを設定
git remote add origin "http://root:${GITLAB_ROOT_PASSWORD}@${EC2_PUBLIC_IP}:5003/root/sample-app.git"

echo "  ✓ Git リポジトリ初期化完了"

# 3. ブランチ作成とコミット
echo "[3/4] ブランチを作成してコミット中..."

git checkout -b "$BRANCH_NAME"
git add .
git commit -m "pipeline: パイプライン実行 - $(date '+%Y-%m-%d %H:%M:%S')"

echo "  ✓ ブランチ作成完了: $BRANCH_NAME"

# 4. GitLab にプッシュ
echo "[4/4] GitLab にプッシュ中..."

git push -u origin "$BRANCH_NAME"

echo "  ✓ プッシュ完了"

echo ""
echo "=========================================="
echo "✅ パイプライン実行開始"
echo "=========================================="
echo ""
echo "🔗 重要なURL:"
echo "  📋 パイプライン一覧: $GITLAB_URL/$PROJECT_PATH/-/pipelines"
echo "  🌿 ブランチ: $BRANCH_NAME"
echo ""
echo "📝 パイプラインは自動的に開始されます"
echo "   ブラウザで上記URLから進捗を確認してください"
echo ""
