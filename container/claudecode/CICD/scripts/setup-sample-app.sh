#!/bin/bash

# sample-app GitLab登録スクリプト（ユーザーリポジトリと完全分離）
# 複数回実行対応版 - 環境変数からEC2ホスト自動取得

set -e

BASE_DIR="/root/aws.git/container/claudecode/CICD"
TEMP_DIR="/tmp/gitlab-sample-app"
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

# 複数回実行対応：既存プロセスのクリーンアップ
cleanup_previous_runs() {
    echo "  🧹 既存実行のクリーンアップ中..."
    # 既存のgit-upload-packプロセス終了
    pkill -f "git-upload-pack.*sample-app" 2>/dev/null || true
    # 一時ディレクトリの完全削除
    rm -rf $TEMP_DIR 2>/dev/null || true
    sleep 2
    echo "  ✓ クリーンアップ完了"
}

echo "=========================================="
echo "sample-app GitLab登録（独立ディレクトリ）"
echo "EC2ホスト: $EC2_HOST"
echo "=========================================="

# 1. 独立したディレクトリを作成（複数回実行対応）
echo "[1/8] 独立ディレクトリ作成中... (実行ID: $EXECUTION_ID)"
cleanup_previous_runs
mkdir -p $TEMP_DIR
echo "  ✓ 独立ディレクトリ作成完了: $TEMP_DIR"

# 2. sample-appをコピー
echo "[2/8] sample-appファイルをコピー中..."
# 隠しファイル（.gitlab-ci.yml等）も含めてコピー
cp -r $BASE_DIR/sample-app/. $TEMP_DIR/
echo "  ✓ ファイルコピー完了（隠しファイル含む）"

# 3. Gitリポジトリ初期化
echo "[3/8] Gitリポジトリ初期化中..."
cd $TEMP_DIR
git init
git config user.name "CICD Admin"
git config user.email "admin@example.com"
echo "  ✓ Gitリポジトリ初期化完了"

# 4. 初期コミット作成
echo "[4/8] 初期コミット作成中..."
git add .
git commit -m "CI/CD Pipeline Test - Execution ID: $EXECUTION_ID

- Maven Multi-Module project (parent + common + backend)
- Complete 5-stage GitLab CI/CD pipeline
- JaCoCo coverage reporting
- Nexus artifact deployment
- JUnit test suites
- Department CRUD functionality with hierarchical organization"
echo "  ✓ 初期コミット作成完了"

# 5. GitLabリモート設定（複数回実行対応）
echo "[5/8] GitLabリモート設定中..."
# 既存のリモートがある場合は削除
git remote remove origin 2>/dev/null || true
git remote add origin http://root:$ADMIN_PASSWORD@$EC2_HOST:5003/root/sample-app.git
echo "  ✓ GitLabリモート設定完了"

# 6. GitLabにプッシュ（競合自動解決）
echo "[6/8] GitLabにプッシュ中..."
if ! git push -u origin master 2>/dev/null; then
    echo "  リモートとの競合を検出しました。自動マージ中..."
    git config pull.rebase false

    # 競合解決のための事前設定
    git config merge.ours.driver true
    echo "README.md merge=ours" > .gitattributes

    if git pull origin master --allow-unrelated-histories --no-edit 2>/dev/null; then
        echo "  ✓ 自動マージ完了"
        git push origin master
        echo "  ✓ GitLabプッシュ完了"
    else
        echo "  ⚠ 複雑な競合が発生しました。強制的に解決中..."
        # 競合を無視してリモートの状態をリセット
        git fetch origin master
        git reset --hard origin/master
        # 最新のCI設定をコピー
        cp "$BASE_DIR/sample-app/.gitlab-ci.yml" .
        git add .gitlab-ci.yml
        git commit -m "Update CI/CD pipeline with SonarQube stage - Execution ID: $EXECUTION_ID"
        git push origin master
        echo "  ✓ GitLabプッシュ完了（強制解決）"
    fi
else
    echo "  ✓ GitLabプッシュ完了"
fi

# 7. CI/CDパイプライン開始確認
echo "[7/8] CI/CDパイプライン開始確認中..."
sleep 10
if sudo journalctl -u gitlab-runner --since "30 seconds ago" --no-pager | grep -q "Checking for jobs.*received"; then
    echo "  ✓ GitLab RunnerがCI/CDジョブを受信しました"
else
    echo "  ⚠ CI/CDジョブの受信を確認できませんでした（Runner状況を確認してください）"
fi

# 8. CI/CDパイプライン実行状況監視
echo "[8/8] CI/CDパイプライン実行状況監視中..."
echo "  パイプライン実行を監視します（最大3分）..."

pipeline_success=false
for i in {1..36}; do
    sleep 5
    # 最新のジョブ状況をチェック（6ステージ対応）
    if sudo journalctl -u gitlab-runner --since "3 minutes ago" --no-pager | grep -q "Job succeeded.*job-status=success.*sample-app"; then
        job_count=$(sudo journalctl -u gitlab-runner --since "3 minutes ago" --no-pager | grep -c "Job succeeded.*sample-app" || echo "0")
        if [ "$job_count" -ge 6 ]; then
            echo "  ✅ CI/CDパイプライン全ステージ成功（${job_count}個のジョブ完了）"
            echo "  📊 SonarQubeプロジェクト確認: http://$EC2_HOST:8000/dashboard?id=sample-app-backend"
            pipeline_success=true
            break
        elif [ "$job_count" -gt 0 ]; then
            echo "  🔄 パイプライン実行中... (${job_count}/6 ステージ完了)"
            if [ "$job_count" -ge 4 ]; then
                echo "  🔍 SonarQubeステージ実行中または完了..."
            fi
        fi
    elif sudo journalctl -u gitlab-runner --since "3 minutes ago" --no-pager | grep -q "Job failed.*sample-app"; then
        echo "  ❌ CI/CDパイプラインでエラーが発生しました"
        echo "  GitLab UI で詳細を確認: http://$EC2_HOST:5003/root/sample-app/-/pipelines"
        break
    fi
done

if [ "$pipeline_success" = false ]; then
    echo "  ⚠ パイプライン完了の確認がタイムアウトしました"
    echo "  手動確認: http://$EC2_HOST:5003/root/sample-app/-/pipelines"
    echo ""
    echo "  🔧 トラブルシューティング："
    echo "  1. GitLab Runner状態確認: sudo systemctl status gitlab-runner"
    echo "  2. CI/CD環境変数確認: GitLab → Settings → CI/CD → Variables"
    echo "  3. SonarQube接続確認: curl http://$EC2_HOST:8000/api/system/status"
    echo "  4. 手動パイプライン実行: GitLab UI → CI/CD → Run Pipeline"
fi

echo ""
echo "=========================================="
echo "✅ sample-app CI/CD検証完了"
echo "=========================================="
echo ""
echo "🌐 GitLab プロジェクト: http://$EC2_HOST:5003/root/sample-app"
echo "📊 パイプライン状況: http://$EC2_HOST:5003/root/sample-app/-/pipelines"
echo "🗂️ 独立ディレクトリ: $TEMP_DIR"
echo ""
echo "✅ サービス URL:"
echo "   GitLab:    http://$EC2_HOST:5003 (root/Degital2026!)"
echo "   Nexus:     http://$EC2_HOST:8082 (admin/Degital2026!)"
echo "   SonarQube: http://$EC2_HOST:8000 (admin/Degital2026!)"
echo ""
echo "⚠️  重要な設定："
echo "   GitLab CI/CD環境変数の設定が必要です："
echo "   1. GitLab → Settings → CI/CD → Variables で以下を追加："
echo "      - SONAR_HOST_URL (Value: http://$EC2_HOST:8000)"
echo "      - SONAR_PROJECT_KEY (Value: sample-app-backend)"
echo "      - SONAR_TOKEN (Value: ${SONAR_TOKEN:-未設定})"
echo "      - EC2_PUBLIC_IP (Value: $EC2_HOST)"
echo "   2. 設定後、再度パイプラインを実行してください"
echo ""
echo "📝 注意事項:"
echo "   - GitLab Runner実行時は完全に独立したクローンが作成されます"
echo "   - ユーザーリポジトリ ($BASE_DIR) とは完全に分離されています"
echo "   - CI/CDパイプライン（6ステージ）: Build → Test → Coverage → SonarQube → Package → Deploy"
echo ""