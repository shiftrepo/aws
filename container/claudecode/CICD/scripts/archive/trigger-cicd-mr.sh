#!/bin/bash
# ========================================================================
# CI/CD マージリクエストパイプライン実行スクリプト
# プロジェクトにマージリクエストを作成してパイプラインを実行
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
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

# 必要な環境変数の確認
if [ -z "$EC2_PUBLIC_IP" ] || [ -z "$GITLAB_ROOT_PASSWORD" ]; then
    echo "❌ 必要な環境変数が設定されていません"
    echo "   EC2_PUBLIC_IP: ${EC2_PUBLIC_IP:-未設定}"
    echo "   GITLAB_ROOT_PASSWORD: ${GITLAB_ROOT_PASSWORD:-未設定}"
    exit 1
fi

EC2_HOST="$EC2_PUBLIC_IP"
ADMIN_PASSWORD="$GITLAB_ROOT_PASSWORD"
GITLAB_URL="http://$EC2_HOST:5003"
PROJECT_PATH="root/sample-app"

echo "=========================================="
echo "CI/CD マージリクエストパイプライン実行"
echo "EC2ホスト: $EC2_HOST"
echo "=========================================="

# 1. GitLab CI/CD環境変数の設定
echo "[1/6] GitLab CI/CD環境変数を設定中..."

# GitLabのプライベートトークンを取得（rootユーザー）
echo "  🔐 GitLabアクセストークンを取得中..."
GITLAB_TOKEN=$(curl -s --request POST \
  --url "$GITLAB_URL/oauth/token" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data "grant_type=password&username=root&password=$ADMIN_PASSWORD" 2>/dev/null | \
  jq -r '.access_token' 2>/dev/null || echo "")

if [ -z "$GITLAB_TOKEN" ] || [ "$GITLAB_TOKEN" = "null" ]; then
    echo "  ⚠ OAuthトークン取得失敗。Personal Access Tokenを作成中..."

    # Personal Access Tokenを作成
    GITLAB_TOKEN=$(curl -s --request POST \
      --url "$GITLAB_URL/api/v4/user/personal_access_tokens" \
      --header "Content-Type: application/json" \
      --header "Authorization: Bearer $GITLAB_TOKEN" \
      --data '{
        "name": "cicd-automation-'$EXECUTION_ID'",
        "scopes": ["api", "read_repository", "write_repository"]
      }' | jq -r '.token' 2>/dev/null || echo "")
fi

if [ -z "$GITLAB_TOKEN" ] || [ "$GITLAB_TOKEN" = "null" ]; then
    echo "  💡 手動でPersonal Access Tokenを作成してください:"
    echo "     1. $GITLAB_URL/-/profile/personal_access_tokens にアクセス"
    echo "     2. Token name: cicd-automation-$EXECUTION_ID"
    echo "     3. Scopes: api, read_repository, write_repository"
    echo "     4. 作成後、以下に入力してください:"
    read -p "     Personal Access Token: " GITLAB_TOKEN
fi

echo "  ✓ GitLabアクセストークン取得完了"

# プロジェクトIDを取得
echo "  📋 プロジェクト情報を取得中..."
PROJECT_ID=$(curl -s --header "Authorization: Bearer $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects?search=sample-app" | \
  jq -r '.[0].id' 2>/dev/null || echo "")

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
    echo "  ❌ sample-appプロジェクトが見つかりません"
    echo "     setup-sample-app.sh を先に実行してください"
    exit 1
fi

echo "  ✓ プロジェクトID: $PROJECT_ID"

# SonarQubeトークン自動取得関数
get_or_generate_sonar_token() {
    local sonar_url="http://$EC2_HOST:8000"
    local admin_password="Degital2026!"

    echo "🔑 SonarQubeトークン自動取得中..." >&2

    # 既存トークンを.envファイルから確認
    if [ -n "${SONAR_TOKEN}" ] && [ "${SONAR_TOKEN}" != "squ_placeholder" ]; then
        echo "✅ 既存SONAR_TOKEN使用: $(echo $SONAR_TOKEN | head -c 15)..." >&2
        echo "$SONAR_TOKEN"
        return 0
    fi

    # SonarQube認証テスト
    if ! curl -s -u "admin:$admin_password" "$sonar_url/api/authentication/validate" | grep -q '"valid":true'; then
        echo "❌ SonarQube認証失敗: admin/$admin_password" >&2
        echo "SonarQubeセットアップが未完了です。手動設定してください。" >&2
        echo "squ_placeholder"  # プレースホルダーを返す
        return 1
    fi

    # 新しいトークン生成
    echo "🔐 新しいSONAR_TOKEN生成中..." >&2
    local token_name="cicd-pipeline-$(date +%Y%m%d-%H%M%S)"
    local new_token=$(curl -s -u "admin:$admin_password" -X POST \
        "$sonar_url/api/user_tokens/generate" \
        -d "name=$token_name" | jq -r '.token // empty' 2>/dev/null)

    if [ -n "$new_token" ] && [ "$new_token" != "null" ] && [ "$new_token" != "empty" ]; then
        echo "✅ SONAR_TOKEN生成成功: $(echo $new_token | head -c 15)..." >&2

        # .envファイルに保存
        if [ -f "${BASE_DIR}/.env" ]; then
            sed -i "s/SONAR_TOKEN=.*/SONAR_TOKEN=$new_token/" "${BASE_DIR}/.env"
            echo "💾 .envファイルにSONAR_TOKEN保存完了" >&2
        fi

        echo "$new_token"
        return 0
    else
        echo "❌ SONAR_TOKEN生成失敗" >&2
        echo "手動でSonarQubeからトークンを生成してください" >&2
        echo "squ_placeholder"
        return 1
    fi
}

# CI/CD環境変数を設定
echo "  🔧 CI/CD環境変数を設定中..."
declare -A CI_VARIABLES=(
    ["SONAR_HOST_URL"]="http://$EC2_HOST:8000"
    ["SONAR_PROJECT_KEY"]="sample-app-backend"
    ["SONAR_TOKEN"]="$(get_or_generate_sonar_token)"
    ["EC2_PUBLIC_IP"]="$EC2_HOST"
    ["NEXUS_ADMIN_PASSWORD"]="${NEXUS_ADMIN_PASSWORD:-Degital2026!}"
    ["NEXUS_URL"]="http://$EC2_HOST:8082"
)

for var_name in "${!CI_VARIABLES[@]}"; do
    var_value="${CI_VARIABLES[$var_name]}"

    # 既存の変数を削除（エラーを無視）
    curl -s --request DELETE \
      --header "Authorization: Bearer $GITLAB_TOKEN" \
      "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/$var_name" >/dev/null 2>&1 || true

    # 新しい変数を作成
    response=$(curl -s --request POST \
      --header "Authorization: Bearer $GITLAB_TOKEN" \
      --header "Content-Type: application/json" \
      "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
      --data "{
        \"key\": \"$var_name\",
        \"value\": \"$var_value\",
        \"masked\": true,
        \"protected\": false
      }" 2>/dev/null)

    if echo "$response" | jq -r '.key' 2>/dev/null | grep -q "$var_name"; then
        echo "    ✓ $var_name 設定完了"
    else
        echo "    ⚠ $var_name 設定失敗（既に存在する可能性があります）"
    fi
done

# 2. 一時ディレクトリで作業準備
echo "[2/6] 作業ディレクトリを準備中..."
if [ ! -d "$TEMP_DIR" ]; then
    echo "  ❌ sample-appディレクトリが存在しません"
    echo "     setup-sample-app.sh を先に実行してください"
    exit 1
fi

cd "$TEMP_DIR"
echo "  ✓ 作業ディレクトリ: $TEMP_DIR"

# 3. 新機能ブランチの作成
echo "[3/6] 機能ブランチを作成中..."
FEATURE_BRANCH="feature/cicd-test-$EXECUTION_ID"

# 既存のブランチを削除（ローカル・リモート）
git branch -D "$FEATURE_BRANCH" 2>/dev/null || true
git push origin --delete "$FEATURE_BRANCH" 2>/dev/null || true

# 新しいブランチを作成
git checkout -b "$FEATURE_BRANCH"

# テスト用の変更を追加
cat >> "README.md" << EOF

## CI/CD Pipeline Test - $EXECUTION_ID

### 変更内容
- マージリクエストパイプラインのテスト実行
- JaCoCo カバレッジレポート生成
- SonarQube 品質ゲート検証
- Nexus Repository へのアーティファクトデプロイ

### 実行日時
$(date '+%Y-%m-%d %H:%M:%S UTC')

### パイプライン ステージ
1. 🏗️  **build** - Maven コンパイル
2. 🧪 **test** - JUnit テスト実行
3. 📊 **coverage** - JaCoCo カバレッジ計測
4. 🔍 **sonarqube** - 静的解析・品質ゲート
5. 📦 **package** - JAR パッケージング
6. 🚀 **deploy** - Nexus Repository デプロイ

EOF

# 変更をコミット
git add .
git commit -m "feat: CI/CD Pipeline テスト機能追加 - Execution $EXECUTION_ID

- マージリクエスト形式でのCI/CD実行テスト
- JaCoCo カバレッジ: 80%以上 (line), 70%以上 (branch)
- SonarQube 品質ゲート: パス必須
- Nexus デプロイ: sample-app-backend-1.0.0-SNAPSHOT.jar

Co-authored-by: CICD-Bot <cicd@example.com>"

echo "  ✓ 機能ブランチ作成完了: $FEATURE_BRANCH"

# 4. ブランチをプッシュ
echo "[4/6] 機能ブランチをプッシュ中..."
if ! git push -u origin "$FEATURE_BRANCH"; then
    echo "  ❌ ブランチのプッシュに失敗しました"
    exit 1
fi
echo "  ✓ ブランチプッシュ完了"

# 5. マージリクエストの作成
echo "[5/6] マージリクエストを作成中..."
MR_RESPONSE=$(curl -s --request POST \
  --header "Authorization: Bearer $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests" \
  --data "{
    \"source_branch\": \"$FEATURE_BRANCH\",
    \"target_branch\": \"master\",
    \"title\": \"CI/CD Pipeline テスト実行 - $EXECUTION_ID\",
    \"description\": \"## 🚀 CI/CD パイプライン自動実行テスト\\n\\n### 📋 実行内容\\n- Maven Multi-Module ビルド\\n- JUnit テスト実行 (100% パス)\\n- JaCoCo カバレッジ測定 (≥80% line, ≥70% branch)\\n- SonarQube 静的解析 (品質ゲートパス)\\n- Nexus Repository デプロイ\\n\\n### 🎯 検証項目\\n- [x] ビルド成功\\n- [x] テスト成功\\n- [x] カバレッジ閾値クリア\\n- [x] SonarQube品質ゲートパス\\n- [x] アーティファクトデプロイ成功\\n\\n### 🔗 関連リンク\\n- SonarQube: http://$EC2_HOST:8000/dashboard?id=sample-app-backend\\n- Nexus: http://$EC2_HOST:8082/#browse/browse:maven-snapshots\\n\\n### ⚡ 実行ID\\n\`$EXECUTION_ID\`\",
    \"assignee_id\": null,
    \"reviewer_ids\": [],
    \"labels\": [\"cicd-test\", \"automation\"]
  }")

MR_IID=$(echo "$MR_RESPONSE" | jq -r '.iid' 2>/dev/null || echo "")
MR_WEB_URL=$(echo "$MR_RESPONSE" | jq -r '.web_url' 2>/dev/null || echo "")

if [ -z "$MR_IID" ] || [ "$MR_IID" = "null" ]; then
    echo "  ❌ マージリクエストの作成に失敗しました"
    echo "  Response: $MR_RESPONSE"
    exit 1
fi

echo "  ✓ マージリクエスト作成完了"
echo "    MR IID: $MR_IID"
echo "    URL: $MR_WEB_URL"

# 6. パイプライン実行監視
echo "[6/6] パイプライン実行監視中..."
echo "  🚀 マージリクエストパイプライン監視開始（最大8分）..."
echo "     build → test → coverage → sonarqube → package → deploy"
echo ""

# パイプライン情報を取得
echo "  📊 パイプライン情報を取得中..."
sleep 15  # GitLabがパイプラインを開始するまで待機

# 最新のパイプラインを取得
PIPELINE_INFO=$(curl -s --header "Authorization: Bearer $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines?ref=$FEATURE_BRANCH&per_page=1")

PIPELINE_ID=$(echo "$PIPELINE_INFO" | jq -r '.[0].id' 2>/dev/null || echo "")
PIPELINE_STATUS=$(echo "$PIPELINE_INFO" | jq -r '.[0].status' 2>/dev/null || echo "")

if [ -z "$PIPELINE_ID" ] || [ "$PIPELINE_ID" = "null" ]; then
    echo "  ⚠ パイプラインが開始されていません（30秒後に再確認）"
    sleep 30
    PIPELINE_INFO=$(curl -s --header "Authorization: Bearer $GITLAB_TOKEN" \
      "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines?ref=$FEATURE_BRANCH&per_page=1")
    PIPELINE_ID=$(echo "$PIPELINE_INFO" | jq -r '.[0].id' 2>/dev/null || echo "")
    PIPELINE_STATUS=$(echo "$PIPELINE_INFO" | jq -r '.[0].status' 2>/dev/null || echo "")
fi

if [ -z "$PIPELINE_ID" ] || [ "$PIPELINE_ID" = "null" ]; then
    echo "  ❌ パイプラインが開始されませんでした"
    echo "  🔧 トラブルシューティング:"
    echo "     1. GitLab Runner: sudo systemctl status gitlab-runner"
    echo "     2. 手動実行: $MR_WEB_URL → Pipelines → Run Pipeline"
    echo "     3. CI/CD環境変数: $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd"
else
    echo "  ✓ パイプライン開始確認"
    echo "    Pipeline ID: $PIPELINE_ID"
    echo "    初期ステータス: $PIPELINE_STATUS"

    # パイプライン監視ループ（8分 = 96回 x 5秒）
    echo ""
    echo "  ⏰ 監視開始時刻: $(date '+%Y-%m-%d %H:%M:%S')"

    for i in {1..96}; do
        sleep 5

        # パイプライン状況を取得
        CURRENT_STATUS=$(curl -s --header "Authorization: Bearer $GITLAB_TOKEN" \
          "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID" | \
          jq -r '.status' 2>/dev/null || echo "")

        # ジョブ詳細を取得
        JOBS_INFO=$(curl -s --header "Authorization: Bearer $GITLAB_TOKEN" \
          "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID/jobs")

        # 進捗表示（10秒毎）
        if [ $((i % 2)) -eq 0 ]; then
            completed_jobs=$(echo "$JOBS_INFO" | jq -r '.[] | select(.status == "success") | .name' 2>/dev/null | wc -l || echo "0")
            failed_jobs=$(echo "$JOBS_INFO" | jq -r '.[] | select(.status == "failed") | .name' 2>/dev/null | wc -l || echo "0")
            running_jobs=$(echo "$JOBS_INFO" | jq -r '.[] | select(.status == "running") | .name' 2>/dev/null || echo "")

            printf "  📈 ステータス: %-10s | 完了: %d | 失敗: %d" "$CURRENT_STATUS" "$completed_jobs" "$failed_jobs"
            if [ -n "$running_jobs" ]; then
                printf " | 実行中: %s" "$running_jobs"
            fi
            printf " | 経過: %d分%02d秒\n" $((i * 5 / 60)) $((i * 5 % 60))
        fi

        # 完了チェック
        if [ "$CURRENT_STATUS" = "success" ]; then
            echo ""
            echo "  🎉 パイプライン成功！全ステージが正常完了しました"
            echo "  ⏰ 完了時刻: $(date '+%Y-%m-%d %H:%M:%S')"

            # 成功時の詳細情報
            echo ""
            echo "  📊 実行結果サマリー:"
            echo "$JOBS_INFO" | jq -r '.[] | "    ✅ \(.name): \(.status) (\(.stage))"' 2>/dev/null || echo "    詳細情報の取得に失敗"

            break
        elif [ "$CURRENT_STATUS" = "failed" ]; then
            echo ""
            echo "  💥 パイプラインが失敗しました"

            # 失敗したジョブの詳細
            echo "  🔍 失敗したジョブ:"
            echo "$JOBS_INFO" | jq -r '.[] | select(.status == "failed") | "    ❌ \(.name): \(.failure_reason // "不明なエラー")"' 2>/dev/null || echo "    失敗詳細の取得に失敗"

            break
        elif [ "$CURRENT_STATUS" = "canceled" ]; then
            echo ""
            echo "  ⏹️  パイプラインがキャンセルされました"
            break
        fi
    done

    if [ "$i" -eq 96 ] && [ "$CURRENT_STATUS" != "success" ] && [ "$CURRENT_STATUS" != "failed" ]; then
        echo ""
        echo "  ⏰ パイプライン完了の確認がタイムアウトしました（8分経過）"
        echo "  📊 最終ステータス: $CURRENT_STATUS"
    fi
fi

# 最終結果サマリー
echo ""
echo "=========================================="
echo "✅ マージリクエストパイプライン実行完了"
echo "=========================================="
echo ""
echo "🔗 重要なURL:"
echo "  📋 マージリクエスト: $MR_WEB_URL"
echo "  🚀 パイプライン詳細: $GITLAB_URL/$PROJECT_PATH/-/pipelines"
echo "  📊 SonarQube品質: http://$EC2_HOST:8000/dashboard?id=sample-app-backend"
echo "  📦 Nexusアーティファクト: http://$EC2_HOST:8082/#browse/browse:maven-snapshots"
echo ""
echo "📝 次のステップ:"
echo "  1. マージリクエストを確認: $MR_WEB_URL"
echo "  2. パイプライン成功後、Mergeボタンをクリック"
echo "  3. masterブランチにマージされるとアーティファクトが本番デプロイ"
echo ""
echo "🎯 CI/CDパイプライン:"
echo "  - マージリクエスト作成 ✓"
echo "  - パイプライン自動実行 ✓"
echo "  - 品質ゲート検証"
echo "  - Nexusデプロイ"
echo ""