#!/bin/bash

# sample-app GitLab登録スクリプト（フロントエンド/バックエンド分割版）
# フロントエンドとバックエンドを別プロジェクトとしてGitLabに登録

set -e

BASE_DIR="/root/aws.git/container/claudecode/CICD"
TEMP_DIR_FRONTEND="/tmp/gitlab-sample-app-frontend"
TEMP_DIR_BACKEND="/tmp/gitlab-sample-app-backend"
EXECUTION_ID=$(date +%Y%m%d-%H%M%S)

# 環境変数を読み込み
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
else
    echo "❌ .env ファイルが見つかりません: $BASE_DIR/.env"
    echo "   setup-from-scratch.sh を先に実行してください"
    exit 1
fi

# EC2_PUBLIC_IPとパスワードの確認
if [ -z "$EC2_PUBLIC_IP" ]; then
    echo "❌ EC2_PUBLIC_IP が .env ファイルに設定されていません"
    exit 1
fi

if [ -z "$GITLAB_ROOT_PASSWORD" ]; then
    echo "❌ GITLAB_ROOT_PASSWORD が .env ファイルに設定されていません"
    exit 1
fi

EC2_HOST="$EC2_PUBLIC_IP"
ADMIN_PASSWORD="$GITLAB_ROOT_PASSWORD"

echo "🌐 使用するEC2ホスト: $EC2_HOST"

# クリーンアップ
cleanup_previous_runs() {
    echo "  🧹 既存実行のクリーンアップ中..."
    pkill -f "git-upload-pack.*sample-app" 2>/dev/null || true
    rm -rf $TEMP_DIR_FRONTEND $TEMP_DIR_BACKEND 2>/dev/null || true
    sleep 2
    echo "  ✓ クリーンアップ完了"
}

echo "=========================================="
echo "sample-app GitLab登録（フロントエンド/バックエンド分割版）"
echo "EC2ホスト: $EC2_HOST"
echo "=========================================="

cleanup_previous_runs

####################################
# フロントエンドプロジェクト作成
####################################

echo ""
echo "[フロントエンド] プロジェクト作成開始"
echo "=========================================="

# 1. ディレクトリ作成
echo "[1/5] ディレクトリ作成中..."
mkdir -p $TEMP_DIR_FRONTEND
cd $TEMP_DIR_FRONTEND
echo "  ✓ ディレクトリ作成完了: $TEMP_DIR_FRONTEND"

# 2. フロントエンドファイルをコピー
echo "[2/5] フロントエンドファイルをコピー中..."
cp -r $BASE_DIR/sample-app/frontend/. ./
cp $BASE_DIR/sample-app/.gitlab-ci.yml.frontend ./.gitlab-ci.yml
echo "  ✓ ファイルコピー完了"

# 3. Gitリポジトリ初期化
echo "[3/5] Gitリポジトリ初期化中..."
git init
git config user.name "CICD Admin"
git config user.email "admin@example.com"
git add .
git commit -m "Frontend Project - Execution ID: $EXECUTION_ID

- React + Vite
- ESLint + Jest
- CI/CD Pipeline (install → lint → test → sonar → build)"
echo "  ✓ 初期コミット作成完了"

# 4. GitLabリモート設定
echo "[4/5] GitLabリモート設定中..."
git remote remove origin 2>/dev/null || true
git remote add origin http://root:$ADMIN_PASSWORD@$EC2_HOST:5003/root/sample-app-frontend.git
echo "  ✓ GitLabリモート設定完了"

# 5. GitLabにプッシュ
echo "[5/5] GitLabにプッシュ中..."
if ! git push -u origin master -f 2>&1; then
    echo "  ⚠️ プッシュに失敗しました"
    exit 1
fi
echo "  ✅ フロントエンドプロジェクト登録完了"

####################################
# バックエンドプロジェクト作成
####################################

echo ""
echo "[バックエンド] プロジェクト作成開始"
echo "=========================================="

# 1. ディレクトリ作成
echo "[1/5] ディレクトリ作成中..."
mkdir -p $TEMP_DIR_BACKEND
cd $TEMP_DIR_BACKEND
echo "  ✓ ディレクトリ作成完了: $TEMP_DIR_BACKEND"

# 2. バックエンドファイルをコピー
echo "[2/5] バックエンドファイルをコピー中..."
cp -r $BASE_DIR/sample-app/backend ./
cp -r $BASE_DIR/sample-app/common ./
cp $BASE_DIR/sample-app/pom.xml ./
cp -r $BASE_DIR/sample-app/scripts ./
cp $BASE_DIR/sample-app/.gitlab-ci.yml.backend ./.gitlab-ci.yml
echo "  ✓ ファイルコピー完了"

# 3. Gitリポジトリ初期化
echo "[3/5] Gitリポジトリ初期化中..."
git init
git config user.name "CICD Admin"
git config user.email "admin@example.com"
git add .
git commit -m "Backend Project - Execution ID: $EXECUTION_ID

- Spring Boot 3.2 + Java 17
- Maven Multi-Module (parent + common + backend)
- CI/CD Pipeline (build → test → coverage → sonar → package → deploy)
- JaCoCo Coverage + Nexus Deploy"
echo "  ✓ 初期コミット作成完了"

# 4. GitLabリモート設定
echo "[4/5] GitLabリモート設定中..."
git remote remove origin 2>/dev/null || true
git remote add origin http://root:$ADMIN_PASSWORD@$EC2_HOST:5003/root/sample-app-backend.git
echo "  ✓ GitLabリモート設定完了"

# 5. GitLabにプッシュ
echo "[5/5] GitLabにプッシュ中..."
if ! git push -u origin master -f 2>&1; then
    echo "  ⚠️ プッシュに失敗しました"
    exit 1
fi
echo "  ✅ バックエンドプロジェクト登録完了"

####################################
# 完了サマリー
####################################

echo ""
echo "=========================================="
echo "✅ sample-app分割プロジェクト登録完了"
echo "=========================================="
echo ""
echo "🌐 GitLab プロジェクト:"
echo "   フロントエンド: http://$EC2_HOST:5003/root/sample-app-frontend"
echo "   バックエンド:   http://$EC2_HOST:5003/root/sample-app-backend"
echo ""
echo "📊 パイプライン状況:"
echo "   フロントエンド: http://$EC2_HOST:5003/root/sample-app-frontend/-/pipelines"
echo "   バックエンド:   http://$EC2_HOST:5003/root/sample-app-backend/-/pipelines"
echo ""
echo "🗂️ 独立ディレクトリ:"
echo "   フロントエンド: $TEMP_DIR_FRONTEND"
echo "   バックエンド:   $TEMP_DIR_BACKEND"
echo ""
echo "✅ サービス URL:"
echo "   GitLab:    http://$EC2_HOST:5003 (root/$ADMIN_PASSWORD)"
echo "   Nexus:     http://$EC2_HOST:8082 (admin/Degital2026!)"
echo "   SonarQube: http://$EC2_HOST:8000 (admin/Degital2026!)"
echo ""
