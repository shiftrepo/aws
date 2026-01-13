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
if ! git push -u origin master 2>&1; then
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
if ! git push -u origin master 2>&1; then
    echo "  ⚠️ プッシュに失敗しました"
    exit 1
fi
echo "  ✅ バックエンドプロジェクト登録完了"

####################################
# CI/CD Variables 自動設定
####################################

echo ""
echo "[CI/CD Variables] 自動設定開始"
echo "=========================================="

# 1. GitLab Personal Access Token 作成
echo "[1/3] GitLab Personal Access Token 作成中..."
GITLAB_TOKEN=$(sudo podman exec cicd-gitlab gitlab-rails runner "
  user = User.find_by_username('root')
  # 既存のトークンを削除
  user.personal_access_tokens.where(name: 'CICD Setup Token').destroy_all
  # 新しいトークンを作成
  token = user.personal_access_tokens.create(
    name: 'CICD Setup Token',
    scopes: [:api, :read_api, :write_repository],
    expires_at: 365.days.from_now
  )
  puts token.token
" 2>/dev/null | tail -1)

if [ -z "$GITLAB_TOKEN" ]; then
    echo "  ⚠️ Personal Access Token の作成に失敗しました"
    echo "  手動で CI/CD Variables を設定してください："
    echo "  - http://$EC2_HOST:5003/root/sample-app-frontend/-/settings/ci_cd"
    echo "  - http://$EC2_HOST:5003/root/sample-app-backend/-/settings/ci_cd"
    echo "  変数名: EC2_PUBLIC_IP, 値: $EC2_HOST"
else
    echo "  ✓ Personal Access Token 作成完了"

    # 2. フロントエンドプロジェクトに CI/CD Variables 設定
    echo "[2/3] フロントエンドプロジェクトに EC2_PUBLIC_IP 設定中..."
    response=$(curl -s -X POST "http://$EC2_HOST:5003/api/v4/projects/root%2Fsample-app-frontend/variables" \
      -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
      -F "key=EC2_PUBLIC_IP" \
      -F "value=$EC2_HOST" \
      -F "masked=false" \
      -F "protected=false")

    if echo "$response" | grep -q "key"; then
        echo "  ✓ フロントエンドプロジェクトに EC2_PUBLIC_IP 設定完了"
    else
        echo "  ⚠️ 設定に失敗しました: $response"
    fi

    # 3. バックエンドプロジェクトに CI/CD Variables 設定
    echo "[3/3] バックエンドプロジェクトに EC2_PUBLIC_IP 設定中..."
    response=$(curl -s -X POST "http://$EC2_HOST:5003/api/v4/projects/root%2Fsample-app-backend/variables" \
      -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
      -F "key=EC2_PUBLIC_IP" \
      -F "value=$EC2_HOST" \
      -F "masked=false" \
      -F "protected=false")

    if echo "$response" | grep -q "key"; then
        echo "  ✓ バックエンドプロジェクトに EC2_PUBLIC_IP 設定完了"
    else
        echo "  ⚠️ 設定に失敗しました: $response"
    fi

    # 4. フロントエンドプロジェクトに SONAR_TOKEN 設定
    echo "[4/4] フロントエンドプロジェクトに SONAR_TOKEN 設定中..."
    SONAR_TOKEN=$(curl -s -u admin:Degital2026! \
      -X POST "http://${EC2_PUBLIC_IP}:8000/api/user_tokens/generate" \
      -d "name=frontend-ci-token" \
      | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

    if [ -n "$SONAR_TOKEN" ]; then
        response=$(curl -s -X POST "http://$EC2_HOST:5003/api/v4/projects/root%2Fsample-app-frontend/variables" \
          -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
          -F "key=SONAR_TOKEN" \
          -F "value=$SONAR_TOKEN" \
          -F "masked=true" \
          -F "protected=false")

        if echo "$response" | grep -q "key"; then
            echo "  ✓ フロントエンドプロジェクトに SONAR_TOKEN 設定完了"
        else
            echo "  ⚠️ SONAR_TOKEN設定に失敗しました: $response"
        fi
    else
        echo "  ⚠️ SonarQubeトークン生成に失敗しました"
        echo "  手動でトークンを生成し、CI/CD Variablesに登録してください："
        echo "  - SonarQube: http://$EC2_HOST:8000/account/security"
        echo "  - GitLab Variables: http://$EC2_HOST:5003/root/sample-app-frontend/-/settings/ci_cd"
    fi

    echo "  ✅ CI/CD Variables 自動設定完了"
fi

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
