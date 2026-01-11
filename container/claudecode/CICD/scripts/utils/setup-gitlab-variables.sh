#!/bin/bash

# GitLab CI/CD環境変数自動設定スクリプト
# Issue #115 CI/CD環境構築 - SonarQube連携修正

set -e

BASE_DIR="/root/aws.git/container/claudecode/CICD"
EXECUTION_ID=$(date +%Y%m%d-%H%M%S)

echo "==========================================="
echo "GitLab CI/CD環境変数設定スクリプト"
echo "実行ID: $EXECUTION_ID"
echo "==========================================="

# 環境変数を読み込み
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
else
    echo "❌ .env ファイルが見つかりません: $BASE_DIR/.env"
    exit 1
fi

# 必要な変数の確認
if [ -z "$EC2_PUBLIC_IP" ] || [ -z "$SONAR_TOKEN" ]; then
    echo "❌ 必要な環境変数が設定されていません"
    echo "   EC2_PUBLIC_IP: ${EC2_PUBLIC_IP:-未設定}"
    echo "   SONAR_TOKEN: ${SONAR_TOKEN:+設定済み}"
    exit 1
fi

echo ""
echo "🔧 GitLab CI/CD環境変数設定手順："
echo ""
echo "1. GitLabプロジェクト設定にアクセス："
echo "   http://$EC2_PUBLIC_IP:5003/root/sample-app/-/settings/ci_cd"
echo ""
echo "2. 'Variables' セクションを展開"
echo ""
echo "3. 以下の環境変数を追加（Add Variable）："
echo ""
echo "   Variable 1:"
echo "   ├── Key: SONAR_HOST_URL"
echo "   ├── Value: $SONAR_HOST_URL"
echo "   ├── Type: Variable"
echo "   ├── Environment scope: *"
echo "   ├── Protected variable: No"
echo "   └── Masked variable: No"
echo ""
echo "   Variable 2:"
echo "   ├── Key: SONAR_PROJECT_KEY"
echo "   ├── Value: $SONAR_PROJECT_KEY"
echo "   ├── Type: Variable"
echo "   ├── Environment scope: *"
echo "   ├── Protected variable: No"
echo "   └── Masked variable: No"
echo ""
echo "   Variable 3:"
echo "   ├── Key: SONAR_TOKEN"
echo "   ├── Value: $SONAR_TOKEN"
echo "   ├── Type: Variable"
echo "   ├── Environment scope: *"
echo "   ├── Protected variable: No"
echo "   └── Masked variable: Yes"
echo ""
echo "   Variable 4:"
echo "   ├── Key: EC2_PUBLIC_IP"
echo "   ├── Value: $EC2_PUBLIC_IP"
echo "   ├── Type: Variable"
echo "   ├── Environment scope: *"
echo "   ├── Protected variable: No"
echo "   └── Masked variable: No"
echo ""
echo "   Variable 5:"
echo "   ├── Key: NEXUS_ADMIN_PASSWORD"
echo "   ├── Value: $NEXUS_ADMIN_PASSWORD"
echo "   ├── Type: Variable"
echo "   ├── Environment scope: *"
echo "   ├── Protected variable: No"
echo "   └── Masked variable: Yes"
echo ""

# GitLab APIを使った自動設定（オプション）
if command -v jq &> /dev/null; then
    echo "🤖 自動設定を試行しますか？ (GitLab APIを使用)"
    echo "   ⚠️  GitLab Personal Access Token が必要です"
    echo ""
    read -p "自動設定を実行しますか？ (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "GitLab Personal Access Token を入力してください："
        echo "（GitLab → User Settings → Access Tokens → Create personal access token）"
        echo "必要スコープ: api, read_api, read_user"
        read -s -p "Token: " GITLAB_TOKEN
        echo ""

        if [ -n "$GITLAB_TOKEN" ]; then
            echo ""
            echo "🔄 CI/CD環境変数を自動設定中..."

            PROJECT_ID="1" # root/sample-app project ID
            GITLAB_URL="http://$EC2_PUBLIC_IP:5003"

            # 環境変数配列
            declare -A variables=(
                ["SONAR_HOST_URL"]="$SONAR_HOST_URL"
                ["SONAR_PROJECT_KEY"]="$SONAR_PROJECT_KEY"
                ["SONAR_TOKEN"]="$SONAR_TOKEN"
                ["EC2_PUBLIC_IP"]="$EC2_PUBLIC_IP"
                ["NEXUS_ADMIN_PASSWORD"]="$NEXUS_ADMIN_PASSWORD"
            )

            # マスク対象変数
            masked_vars=("SONAR_TOKEN" "NEXUS_ADMIN_PASSWORD")

            success_count=0
            total_count=${#variables[@]}

            for var_name in "${!variables[@]}"; do
                var_value="${variables[$var_name]}"
                masked="false"

                # マスク設定確認
                for masked_var in "${masked_vars[@]}"; do
                    if [ "$var_name" = "$masked_var" ]; then
                        masked="true"
                        break
                    fi
                done

                echo "  設定中: $var_name..."

                # 既存変数削除（エラーを無視）
                curl -s -X DELETE \
                    -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
                    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/$var_name" \
                    > /dev/null 2>&1 || true

                # 新しい変数作成
                response=$(curl -s -X POST \
                    -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d "{
                        \"key\": \"$var_name\",
                        \"value\": \"$var_value\",
                        \"masked\": $masked,
                        \"protected\": false
                    }" \
                    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables")

                if echo "$response" | grep -q '"key"'; then
                    echo "  ✅ $var_name 設定完了"
                    ((success_count++))
                else
                    echo "  ❌ $var_name 設定失敗: $response"
                fi
            done

            echo ""
            echo "📊 設定結果: $success_count/$total_count 個の変数が設定されました"

            if [ $success_count -eq $total_count ]; then
                echo "✅ すべての環境変数の自動設定が完了しました"
            else
                echo "⚠️  一部の環境変数は手動で設定してください"
            fi
        fi
    fi
fi

echo ""
echo "==========================================="
echo "✅ 設定手順表示完了"
echo "==========================================="
echo ""
echo "📝 次のステップ："
echo "1. 上記の環境変数をGitLab CI/CDに設定"
echo "2. sample-appリポジトリに新しいコミットをプッシュ"
echo "3. パイプラインが6ステージすべて実行されることを確認"
echo "4. SonarQubeプロジェクト登録確認: http://$EC2_PUBLIC_IP:8000"
echo ""
echo "🔍 パイプライン監視コマンド："
echo "   sudo journalctl -u gitlab-runner -f"
echo ""
echo "🌐 関連URL："
echo "   GitLab Project: http://$EC2_PUBLIC_IP:5003/root/sample-app"
echo "   Pipeline: http://$EC2_PUBLIC_IP:5003/root/sample-app/-/pipelines"
echo "   SonarQube: http://$EC2_PUBLIC_IP:8000"
echo "   Nexus: http://$EC2_PUBLIC_IP:8082"
echo ""