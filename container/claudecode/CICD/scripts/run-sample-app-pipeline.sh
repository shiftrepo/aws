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

# 0. GitLab CI/CD環境変数を設定
echo "[0/5] GitLab CI/CD環境変数を設定中..."

# GitLab Personal Access Tokenがあれば変数を設定（オプション）
if [ ! -z "$GITLAB_ACCESS_TOKEN" ]; then
    echo "  GitLab API経由で環境変数を設定中..."

    # プロジェクトID取得
    PROJECT_ID=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
      "$GITLAB_URL/api/v4/projects?search=sample-app" 2>/dev/null | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

    if [ ! -z "$PROJECT_ID" ]; then
        # EC2_PUBLIC_IP変数を設定/更新
        curl -s --request POST --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
          "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
          --form "key=EC2_PUBLIC_IP" \
          --form "value=$EC2_PUBLIC_IP" 2>/dev/null || \
        curl -s --request PUT --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
          "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/EC2_PUBLIC_IP" \
          --form "value=$EC2_PUBLIC_IP" 2>/dev/null

        echo "  ✓ EC2_PUBLIC_IP = $EC2_PUBLIC_IP"

        # NEXUS_ADMIN_PASSWORD変数を設定/更新
        if [ ! -z "$NEXUS_ADMIN_PASSWORD" ]; then
            curl -s --request POST --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
              "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
              --form "key=NEXUS_ADMIN_PASSWORD" \
              --form "value=$NEXUS_ADMIN_PASSWORD" \
              --form "masked=true" 2>/dev/null || \
            curl -s --request PUT --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
              "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/NEXUS_ADMIN_PASSWORD" \
              --form "value=$NEXUS_ADMIN_PASSWORD" \
              --form "masked=true" 2>/dev/null
            echo "  ✓ NEXUS_ADMIN_PASSWORD = ********"
        fi

        # SONAR_TOKEN変数を設定/更新
        if [ ! -z "$SONAR_TOKEN" ]; then
            curl -s --request POST --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
              "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
              --form "key=SONAR_TOKEN" \
              --form "value=$SONAR_TOKEN" \
              --form "masked=true" 2>/dev/null || \
            curl -s --request PUT --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
              "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/SONAR_TOKEN" \
              --form "value=$SONAR_TOKEN" \
              --form "masked=true" 2>/dev/null
            echo "  ✓ SONAR_TOKEN = ********"
        fi
    else
        echo "  ⚠️ GitLabプロジェクトが見つかりません（初回実行時は正常）"
    fi
else
    echo "  ⚠️ GITLAB_ACCESS_TOKENが未設定 - 手動でGitLab CI/CD変数を確認してください"
    echo "     GitLab: Settings → CI/CD → Variables"
    echo "     - EC2_PUBLIC_IP = $EC2_PUBLIC_IP"
    echo "     - NEXUS_ADMIN_PASSWORD = ${NEXUS_ADMIN_PASSWORD:-未設定}"
    echo "     - SONAR_TOKEN = ${SONAR_TOKEN:-未設定}"
fi

echo "  ✓ 環境変数設定完了"

# 1. 作業ディレクトリの準備
echo "[1/5] 作業ディレクトリを準備中..."

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
echo "[2/5] Git リポジトリを初期化中..."

git init
git config user.name "CI/CD Automation"
git config user.email "cicd@example.com"

# GitLab リモートを設定
git remote add origin "http://root:${GITLAB_ROOT_PASSWORD}@${EC2_PUBLIC_IP}:5003/root/sample-app.git"

echo "  ✓ Git リポジトリ初期化完了"

# 3. ブランチ作成とコミット
echo "[3/5] ブランチを作成してコミット中..."

git checkout -b "$BRANCH_NAME"
git add .
git commit -m "pipeline: パイプライン実行 - $(date '+%Y-%m-%d %H:%M:%S')"

echo "  ✓ ブランチ作成完了: $BRANCH_NAME"

# 4. GitLab にプッシュ
echo "[4/5] GitLab にプッシュ中..."

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
echo "⚙️  GitLab CI/CD変数の確認:"
echo "   $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd → Variables"
echo ""
