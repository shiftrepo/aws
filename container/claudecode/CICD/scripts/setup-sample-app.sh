#!/bin/bash

# sample-app GitLab登録スクリプト（ユーザーリポジトリと完全分離）

set -e

EC2_HOST=$1
ADMIN_PASSWORD=$2
BASE_DIR="/root/aws.git/container/claudecode/CICD"
TEMP_DIR="/tmp/gitlab-sample-app"

if [ -z "$EC2_HOST" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "Usage: $0 <EC2_HOST> <ADMIN_PASSWORD>"
    exit 1
fi

echo "=========================================="
echo "sample-app GitLab登録（独立ディレクトリ）"
echo "=========================================="

# 1. 独立したディレクトリを作成
echo "[1/6] 独立ディレクトリ作成中..."
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR
echo "  ✓ 独立ディレクトリ作成完了: $TEMP_DIR"

# 2. sample-appをコピー
echo "[2/6] sample-appファイルをコピー中..."
cp -r $BASE_DIR/sample-app/* $TEMP_DIR/
echo "  ✓ ファイルコピー完了"

# 3. Gitリポジトリ初期化
echo "[3/6] Gitリポジトリ初期化中..."
cd $TEMP_DIR
git init
git config user.name "CICD Admin"
git config user.email "admin@example.com"
echo "  ✓ Gitリポジトリ初期化完了"

# 4. 初期コミット作成
echo "[4/6] 初期コミット作成中..."
git add .
git commit -m "Initial commit: Sample App for CI/CD Pipeline

- Maven Multi-Module project (parent + common + backend)
- Complete 5-stage GitLab CI/CD pipeline
- JaCoCo coverage reporting
- Nexus artifact deployment
- JUnit test suites"
echo "  ✓ 初期コミット作成完了"

# 5. GitLabリモート設定
echo "[5/6] GitLabリモート設定中..."
git remote add origin http://root:$ADMIN_PASSWORD@$EC2_HOST:5003/root/sample-app.git
echo "  ✓ GitLabリモート設定完了"

# 6. GitLabにプッシュ
echo "[6/6] GitLabにプッシュ中..."
git push -u origin master
echo "  ✓ GitLabプッシュ完了"

echo ""
echo "=========================================="
echo "✓ sample-app GitLab登録完了"
echo "=========================================="
echo ""
echo "GitLabプロジェクト URL: http://$EC2_HOST:5003/root/sample-app"
echo "独立ディレクトリ: $TEMP_DIR"
echo ""
echo "注意: GitLab Runner実行時は完全に独立したクローンが作成されます"
echo "ユーザーリポジトリ ($BASE_DIR) とは完全に分離されています"
echo ""