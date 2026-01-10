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

# 8. CI/CDパイプライン実行状況監視（強化版）
echo "[8/8] CI/CDパイプライン実行状況監視中..."
echo "  🚀 6ステージパイプライン監視開始（最大5分）..."
echo "     build → test → coverage → sonarqube → package → deploy"
echo ""

# ステージ定義
declare -a STAGES=("build" "test" "coverage" "sonarqube" "package" "deploy")
declare -a STAGE_ICONS=("🏗️" "🧪" "📊" "🔍" "📦" "🚀")
declare -A stage_status
declare -A stage_start_time

# ステージ状態初期化
for stage in "${STAGES[@]}"; do
    stage_status[$stage]="pending"
done

# 監視関数
check_stage_status() {
    local stage=$1
    local icon=$2
    local logs=$(sudo journalctl -u gitlab-runner --since "5 minutes ago" --no-pager 2>/dev/null || echo "")

    # ステージ開始チェック
    if echo "$logs" | grep -q "step_script.*$stage.*Running on" && [ "${stage_status[$stage]}" = "pending" ]; then
        stage_status[$stage]="running"
        stage_start_time[$stage]=$(date +%s)
        printf "  %-12s %s %-10s %s\n" "[$stage]" "$icon" "開始" "$(date '+%H:%M:%S')"
        return 1
    fi

    # ステージ成功チェック
    if echo "$logs" | grep -q "Job succeeded.*$stage" && [ "${stage_status[$stage]}" != "completed" ]; then
        stage_status[$stage]="completed"
        local duration=""
        if [ -n "${stage_start_time[$stage]}" ]; then
            local elapsed=$(($(date +%s) - ${stage_start_time[$stage]}))
            duration="(${elapsed}秒)"
        fi
        printf "  %-12s %s %-10s %s %s\n" "[$stage]" "$icon" "✅完了" "$(date '+%H:%M:%S')" "$duration"
        return 0
    fi

    # ステージ失敗チェック
    if echo "$logs" | grep -q "Job failed.*$stage"; then
        stage_status[$stage]="failed"
        printf "  %-12s %s %-10s %s\n" "[$stage]" "$icon" "❌失敗" "$(date '+%H:%M:%S')"
        return 2
    fi

    return 1
}

# 進捗バー表示関数
show_progress() {
    local completed=0
    local failed=0

    for stage in "${STAGES[@]}"; do
        case "${stage_status[$stage]}" in
            "completed") ((completed++)) ;;
            "failed") ((failed++)) ; break ;;
        esac
    done

    if [ $failed -gt 0 ]; then
        printf "  📈 進捗: %d/6 ステージ完了 (❌失敗あり)\n" $completed
        return 1
    else
        printf "  📈 進捗: %d/6 ステージ完了\n" $completed
        return 0
    fi
}

# パイプライン詳細状態表示
show_pipeline_details() {
    echo "  📋 パイプライン詳細状態:"
    for i in "${!STAGES[@]}"; do
        local stage="${STAGES[$i]}"
        local icon="${STAGE_ICONS[$i]}"
        local status="${stage_status[$stage]}"
        local status_display

        case $status in
            "pending")   status_display="⏳待機中" ;;
            "running")   status_display="🔄実行中" ;;
            "completed") status_display="✅完了" ;;
            "failed")    status_display="❌失敗" ;;
        esac

        printf "     %s %-12s %s\n" "$icon" "[$stage]" "$status_display"
    done
    echo ""
}

# メイン監視ループ（5分 = 60回 x 5秒）
pipeline_success=false
pipeline_failed=false
last_completed_count=0

echo "  ⏰ 監視開始時刻: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

for i in {1..60}; do
    sleep 5

    # 各ステージの状態をチェック
    current_completed=0
    current_failed=false

    for j in "${!STAGES[@]}"; do
        check_stage_status "${STAGES[$j]}" "${STAGE_ICONS[$j]}"
        case "${stage_status[${STAGES[$j]}]}" in
            "completed") ((current_completed++)) ;;
            "failed") current_failed=true ; break ;;
        esac
    done

    # 進捗が変わった場合のみ詳細表示
    if [ $current_completed -ne $last_completed_count ] || [ "$current_failed" = true ]; then
        show_progress

        # 5秒に1回詳細表示（進捗変化時は毎回）
        if [ $((i % 6)) -eq 0 ] || [ $current_completed -ne $last_completed_count ]; then
            show_pipeline_details
        fi

        last_completed_count=$current_completed
    fi

    # 全ステージ完了チェック
    if [ $current_completed -eq 6 ]; then
        echo "  🎉 全6ステージが正常完了しました！"
        echo "  ⏰ 完了時刻: $(date '+%Y-%m-%d %H:%M:%S')"
        pipeline_success=true
        break
    fi

    # 失敗チェック
    if [ "$current_failed" = true ]; then
        echo "  💥 パイプラインでエラーが発生しました"

        # 失敗したステージの詳細ログ表示
        echo "  🔍 エラーログ（直近30行）:"
        sudo journalctl -u gitlab-runner --since "5 minutes ago" --no-pager -n 30 | grep -E "(ERROR|FAIL|error|fail)" | tail -10 || echo "     詳細ログを取得できませんでした"

        pipeline_failed=true
        break
    fi

    # 30秒毎に生存確認メッセージ
    if [ $((i % 6)) -eq 0 ]; then
        printf "  ⏳ 監視継続中... (%d/60) - 経過時間: %d分%02d秒\n" $i $((i * 5 / 60)) $((i * 5 % 60))
    fi
done

# 最終結果サマリー
echo ""
echo "  📊 パイプライン実行結果サマリー"
echo "  ════════════════════════════════"

if [ "$pipeline_success" = true ]; then
    echo "  🎉 CI/CDパイプライン全ステージが正常完了！"
    echo "  📊 SonarQube: http://$EC2_HOST:8000/dashboard?id=sample-app-backend"
    echo "  📦 Nexus Repository: http://$EC2_HOST:8082/#browse/browse:maven-snapshots"
elif [ "$pipeline_failed" = true ]; then
    echo "  💥 パイプライン実行中にエラーが発生しました"
    show_pipeline_details
else
    echo "  ⏰ パイプライン完了の確認がタイムアウトしました（5分経過）"
    show_pipeline_details
    echo "  🔧 トラブルシューティング："
    echo "     1. GitLab Runner状態: sudo systemctl status gitlab-runner"
    echo "     2. CI/CD環境変数: GitLab → Settings → CI/CD → Variables"
    echo "     3. SonarQube接続: curl http://$EC2_HOST:8000/api/system/status"
    echo "     4. 手動実行: GitLab UI → CI/CD → Run Pipeline"
fi

echo "  🌐 GitLab Pipeline UI: http://$EC2_HOST:5003/root/sample-app/-/pipelines"

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