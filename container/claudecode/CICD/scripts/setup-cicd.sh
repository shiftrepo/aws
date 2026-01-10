#!/bin/bash
# ========================================================================
# CI/CD環境セットアップスクリプト
# コンテナ起動とパスワード設定完了後に実行
# GitLab Runner登録、プロジェクト作成、パイプライン設定を自動化
# ========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${BASE_DIR}/.env"

# 色付きメッセージ関数
print_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
print_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
print_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }
print_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

echo "=========================================="
echo "CI/CD環境セットアップ"
echo "=========================================="
echo ""

# 前提条件チェック
print_info "前提条件をチェック中..."

# 環境変数ファイル確認
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env ファイルが見つかりません"
    print_error "先に setup-from-scratch.sh を実行してください"
    exit 1
fi

# 環境変数読み込み
source "$ENV_FILE"

# コンテナ起動確認
print_info "サービス起動状況を確認中..."
REQUIRED_CONTAINERS=("cicd-gitlab" "cicd-nexus" "cicd-sonarqube" "cicd-postgres")
for container in "${REQUIRED_CONTAINERS[@]}"; do
    if ! podman ps --format "{{.Names}}" | grep -q "^${container}$"; then
        print_error "コンテナ ${container} が起動していません"
        print_error "先にコンテナを起動してください: podman-compose up -d"
        exit 1
    fi
done
print_success "必要なコンテナがすべて起動しています"

# サービス接続確認
print_info "サービス接続を確認中..."
for i in {1..5}; do
    if curl -s http://localhost:5003/ > /dev/null && \
       curl -s http://localhost:8082/ > /dev/null && \
       curl -s http://localhost:8000/api/system/status > /dev/null; then
        print_success "すべてのサービスが応答しています"
        break
    fi
    if [ $i -eq 5 ]; then
        print_error "サービスが応答しません。パスワード設定と起動確認を完了してください"
        exit 1
    fi
    print_info "サービス応答待機中... ($i/5)"
    sleep 10
done

echo ""
print_warning "重要: 以下の手動設定が完了していることを確認してください:"
echo "  1. Nexus: http://${EC2_PUBLIC_IP}:8082 (admin/admin123 → パスワード変更完了)"
echo "  2. SonarQube: http://${EC2_PUBLIC_IP}:8000 (admin/admin → パスワード変更完了)"
echo "  3. GitLab: http://${EC2_PUBLIC_IP}:5003 (root/${GITLAB_ROOT_PASSWORD} でアクセス可能)"
echo ""

read -p "上記の手動設定が完了していますか？ (yes/no): " SETUP_CONFIRMED
if [ "$SETUP_CONFIRMED" != "yes" ]; then
    print_error "手動設定を完了してから再実行してください"
    exit 0
fi

# ========================================================================
# ステップ1: 更新されたパスワードとトークンの取得
# ========================================================================
echo ""
echo "=========================================="
echo "[1/6] 認証情報の確認・更新"
echo "=========================================="

print_info "Nexusパスワード設定確認中..."
echo "  前提: admin/admin123 → admin/Degital2026! への変更完了済み"
echo "  使用パスワード: ${NEXUS_ADMIN_PASSWORD}"

# Nexusパスワード確認（疎通確認）
if curl -s -u admin:${NEXUS_ADMIN_PASSWORD} "http://${EC2_PUBLIC_IP}:8082/service/rest/v1/status" > /dev/null; then
    print_success "Nexusパスワード確認完了 (admin/${NEXUS_ADMIN_PASSWORD})"
else
    print_warning "Nexusパスワード確認に失敗しました"
    echo "  確認事項:"
    echo "  1. http://${EC2_PUBLIC_IP}:8082 にアクセス"
    echo "  2. admin/admin123 → admin/Degital2026! への変更完了"
    echo "  3. Nexusサービスが正常に起動していることを確認"
    echo ""
    read -p "続行しますか？ (yes/no): " NEXUS_CONTINUE
    if [ "$NEXUS_CONTINUE" != "yes" ]; then
        print_error "Nexusパスワード設定を完了してから再実行してください"
        exit 1
    fi
fi

# SonarQubeトークン自動生成
print_info "SonarQubeトークンを自動生成中..."
echo "  方法: SonarQube API経由 (admin権限)"

# SonarQubeトークン自動生成関数
generate_sonar_token() {
    local token_name="gitlab-ci-auto-$(date +%Y%m%d%H%M%S)"
    local response

    # 既存トークンをクリーンアップ
    curl -s -u admin:${SONARQUBE_ADMIN_PASSWORD} -X POST \
        "http://${EC2_PUBLIC_IP}:8000/api/user_tokens/revoke" \
        -d "name=gitlab-ci-auto" > /dev/null 2>&1 || true

    # 新しいトークンを生成
    response=$(curl -s -u admin:${SONARQUBE_ADMIN_PASSWORD} -X POST \
        "http://${EC2_PUBLIC_IP}:8000/api/user_tokens/generate" \
        -d "name=${token_name}" \
        -d "type=GLOBAL_ANALYSIS_TOKEN")

    if echo "$response" | grep -q '"token"'; then
        echo "$response" | sed 's/.*"token":"\([^"]*\)".*/\1/'
        return 0
    else
        return 1
    fi
}

# トークン自動生成を試行
if NEW_SONAR_TOKEN=$(generate_sonar_token); then
    # トークン更新
    sed -i "s/SONAR_TOKEN=.*/SONAR_TOKEN=${NEW_SONAR_TOKEN}/" "$ENV_FILE"
    source "$ENV_FILE"
    print_success "SonarQubeトークンを自動生成・更新しました"
    echo "  トークン: ${NEW_SONAR_TOKEN:0:20}..."
else
    print_warning "SonarQubeトークン自動生成に失敗しました。手動で取得してください"
    echo "  1. http://${EC2_PUBLIC_IP}:8000 にアクセス"
    echo "  2. My Account → Security → Generate Token"
    echo "  3. Name: gitlab-ci, Type: Project Analysis Token"
    echo ""
    read -p "SonarQubeトークン: " NEW_SONAR_TOKEN
    if [ -n "$NEW_SONAR_TOKEN" ]; then
        sed -i "s/SONAR_TOKEN=.*/SONAR_TOKEN=${NEW_SONAR_TOKEN}/" "$ENV_FILE"
        source "$ENV_FILE"
        print_success "SonarQubeトークンを更新しました"
    fi
fi

# ========================================================================
# ステップ2: GitLab Runner登録
# ========================================================================
echo ""
echo "=========================================="
echo "[2/6] GitLab Runner登録"
echo "=========================================="

# Runner状態確認
# CRITICAL: GitLabRunnerパスは /usr/bin/gitlab-runner 固定 - 変更禁止
if sudo /usr/bin/gitlab-runner list 2>/dev/null | grep -q "CICD Shell Runner"; then
    print_warning "GitLab Runnerは既に登録されています"
    sudo /usr/bin/gitlab-runner list
else
    # GitLab Runner Registration Token自動生成
    print_info "GitLab Runner Registration Tokenを自動生成中..."
    echo "  方法: GitLab Rails Console経由 (root権限)"

    # GitLab Runner Registration Token自動生成関数
    generate_runner_token() {
        local token

        token=$(podman exec -i cicd-gitlab gitlab-rails console <<EOF 2>/dev/null | grep "^runner_token=" | cut -d= -f2
runner = Ci::Runner.new(
  runner_type: :instance_type,
  description: 'CICD Shell Runner Auto-Generated',
  tag_list: ['shell', 'cicd']
)
runner.set_token
runner.save!
puts "runner_token=#{runner.token}" if runner.persisted?
exit
EOF
        )

        if [ -n "$token" ]; then
            echo "$token"
            return 0
        else
            return 1
        fi
    }

    # トークン自動生成を試行
    if RUNNER_REG_TOKEN=$(generate_runner_token); then
        print_success "GitLab Runner Registration Tokenを自動生成しました"
        echo "  トークン: ${RUNNER_REG_TOKEN:0:20}..."
    else
        print_warning "GitLab Runner Registration Token自動生成に失敗しました。手動で取得してください"
        echo "  1. http://${EC2_PUBLIC_IP}:5003 にアクセス"
        echo "  2. root/${GITLAB_ROOT_PASSWORD} でログイン"
        echo "  3. Settings → CI/CD → Runners → New instance runner"
        echo "  4. 「Create runner」をクリックしてトークンを取得"
        echo ""
        read -p "Registration Token: " RUNNER_REG_TOKEN
    fi

    if [ -n "$RUNNER_REG_TOKEN" ]; then
        print_info "GitLab Runnerを登録中..."
        sudo /usr/bin/gitlab-runner register \
            --non-interactive \
            --url "http://${EC2_PUBLIC_IP}:5003" \
            --token "$RUNNER_REG_TOKEN" \
            --executor shell

        # Runner起動
        sudo systemctl start gitlab-runner
        sudo systemctl enable gitlab-runner

        # トークン保存
        sed -i "s/RUNNER_TOKEN=.*/RUNNER_TOKEN=${RUNNER_REG_TOKEN}/" "$ENV_FILE"

        print_success "GitLab Runnerを登録・起動しました"
        sudo /usr/bin/gitlab-runner list
    else
        print_error "Registration Tokenが入力されませんでした"
        exit 1
    fi
fi

# ========================================================================
# ステップ3: GitLabプロジェクト作成
# ========================================================================
echo ""
echo "=========================================="
echo "[3/6] GitLabプロジェクト作成"
echo "=========================================="

# GitLab APIでプロジェクト存在確認
GITLAB_API="http://${EC2_PUBLIC_IP}:5003/api/v4"
PROJECT_EXISTS=$(curl -s -H "PRIVATE-TOKEN: dummy" "${GITLAB_API}/projects/root%2Fsample-app" | grep -o '"id"' || echo "")

if [ -n "$PROJECT_EXISTS" ]; then
    print_warning "sample-appプロジェクトは既に存在します"
else
    print_info "GitLabにsample-appプロジェクトを作成中..."

    # Personal Access Token自動生成
    print_info "GitLab Personal Access Tokenを自動生成中..."
    echo "  方法: GitLab Rails Console経由 (root権限)"

    # GitLab Personal Access Token自動生成関数
    generate_gitlab_token() {
        local token_name="cicd-automation-$(date +%Y%m%d%H%M%S)"
        local token

        token=$(podman exec -i cicd-gitlab gitlab-rails console <<EOF 2>/dev/null | grep "^token=" | cut -d= -f2
user = User.find_by(username: 'root')
token = user.personal_access_tokens.create(
  name: '${token_name}',
  scopes: ['api', 'read_repository', 'write_repository'],
  expires_at: 1.year.from_now
)
puts "token=#{token.token}" if token.persisted?
exit
EOF
        )

        if [ -n "$token" ]; then
            echo "$token"
            return 0
        else
            return 1
        fi
    }

    # トークン自動生成を試行
    if GITLAB_TOKEN=$(generate_gitlab_token); then
        print_success "GitLab Personal Access Tokenを自動生成しました"
        echo "  トークン: ${GITLAB_TOKEN:0:20}..."
    else
        print_warning "GitLab Personal Access Token自動生成に失敗しました。手動で取得してください"
        echo "  1. http://${EC2_PUBLIC_IP}:5003/-/user_settings/personal_access_tokens"
        echo "  2. Token name: cicd-automation"
        echo "  3. Scopes: api, read_repository, write_repository"
        echo "  4. Create personal access token をクリック"
        echo ""
        read -s -p "Personal Access Token: " GITLAB_TOKEN
    fi
    echo ""

    if [ -n "$GITLAB_TOKEN" ]; then
        # プロジェクト作成
        PROJECT_RESPONSE=$(curl -s -X POST \
            -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{
                \"name\": \"sample-app\",
                \"path\": \"sample-app\",
                \"description\": \"CI/CD Sample Multi-Module Application\",
                \"visibility\": \"internal\",
                \"issues_enabled\": true,
                \"merge_requests_enabled\": true,
                \"wiki_enabled\": true,
                \"snippets_enabled\": true
            }" \
            "${GITLAB_API}/projects")

        if echo "$PROJECT_RESPONSE" | grep -q '"id"'; then
            print_success "sample-appプロジェクトを作成しました"
        else
            print_error "プロジェクト作成に失敗しました: $PROJECT_RESPONSE"
            # 手動作成の指示
            print_warning "手動でプロジェクトを作成してください:"
            echo "  1. http://${EC2_PUBLIC_IP}:5003/projects/new"
            echo "  2. Project name: sample-app"
            echo "  3. Visibility Level: Internal"
            echo "  4. Create project"
        fi
    else
        print_warning "Personal Access Tokenが入力されませんでした"
        print_warning "手動でプロジェクトを作成してください:"
        echo "  1. http://${EC2_PUBLIC_IP}:5003/projects/new"
        echo "  2. Project name: sample-app"
        echo "  3. Visibility Level: Internal"
    fi
fi

# ========================================================================
# ステップ4: GitLab CI/CD環境変数設定
# ========================================================================
echo ""
echo "=========================================="
echo "[4/6] GitLab CI/CD環境変数設定"
echo "=========================================="

if [ -n "$GITLAB_TOKEN" ]; then
    print_info "CI/CD環境変数を設定中..."

    # 環境変数設定
    VARIABLES=(
        "SONAR_TOKEN:${SONAR_TOKEN}:true"
        "NEXUS_ADMIN_PASSWORD:${NEXUS_ADMIN_PASSWORD}:true"
        "EC2_PUBLIC_IP:${EC2_PUBLIC_IP}:false"
    )

    for var in "${VARIABLES[@]}"; do
        IFS=':' read -r key value masked <<< "$var"

        # 既存変数確認
        EXISTING=$(curl -s -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
            "${GITLAB_API}/projects/root%2Fsample-app/variables/${key}" | grep -o '"key"' || echo "")

        if [ -n "$EXISTING" ]; then
            # 更新
            curl -s -X PUT \
                -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
                -H "Content-Type: application/json" \
                -d "{\"value\": \"${value}\", \"masked\": ${masked}}" \
                "${GITLAB_API}/projects/root%2Fsample-app/variables/${key}" > /dev/null
            print_success "環境変数 ${key} を更新しました"
        else
            # 新規作成
            curl -s -X POST \
                -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
                -H "Content-Type: application/json" \
                -d "{\"key\": \"${key}\", \"value\": \"${value}\", \"masked\": ${masked}}" \
                "${GITLAB_API}/projects/root%2Fsample-app/variables" > /dev/null
            print_success "環境変数 ${key} を作成しました"
        fi
    done
else
    print_warning "GitLab Personal Access Tokenがないため、手動で環境変数を設定してください:"
    echo "  1. http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/settings/ci_cd"
    echo "  2. Variables セクションを展開"
    echo "  3. 以下の変数を追加:"
    echo "     - SONAR_TOKEN: ${SONAR_TOKEN} (Masked)"
    echo "     - NEXUS_ADMIN_PASSWORD: ${NEXUS_ADMIN_PASSWORD} (Masked)"
    echo "     - EC2_PUBLIC_IP: ${EC2_PUBLIC_IP}"
fi

# ========================================================================
# ステップ5: sample-appをGitLabにプッシュ
# ========================================================================
echo ""
echo "=========================================="
echo "[5/6] sample-appをGitLabにプッシュ"
echo "=========================================="

cd "${BASE_DIR}/sample-app"

print_info "sample-appの変更をコミット中..."

# 変更ファイルを確認してコミット
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "chore: CI/CD環境構築に伴う設定更新

- GitLab CI/CDパイプライン設定を更新
- Maven POM設定を環境に合わせて調整
- PostgreSQL接続設定を更新

Co-Authored-By: Claude <noreply@anthropic.com>" || true
    print_success "変更をコミットしました"
else
    print_info "コミットする変更がありません"
fi

# SSH認証セットアップとプッシュ実行
print_info "SSH認証を設定してGitLabにプッシュ中..."
echo "  方法: SSH鍵自動生成・登録経由"

# SSH鍵ペア自動生成・登録関数
setup_ssh_authentication() {
    local ssh_key_path="$HOME/.ssh/gitlab_cicd_ed25519"
    local ssh_config="$HOME/.ssh/config"

    # SSH ディレクトリ作成
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"

    # SSH鍵ペア生成（既存がない場合のみ）
    if [ ! -f "${ssh_key_path}" ]; then
        print_info "SSH鍵ペアを生成中..."
        ssh-keygen -t ed25519 -f "${ssh_key_path}" -N "" -C "cicd-automation@${EC2_PUBLIC_IP}"
        chmod 600 "${ssh_key_path}"
        chmod 644 "${ssh_key_path}.pub"
        print_success "SSH鍵ペアを生成しました: ${ssh_key_path}"
    else
        print_info "既存のSSH鍵を使用します: ${ssh_key_path}"
    fi

    # SSH設定ファイル更新
    if ! grep -q "Host gitlab-cicd" "${ssh_config}" 2>/dev/null; then
        cat >> "${ssh_config}" << EOF

# GitLab CICD Configuration (Auto-Generated)
Host gitlab-cicd
    HostName ${EC2_PUBLIC_IP}
    Port 2223
    User git
    IdentityFile ${ssh_key_path}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
        chmod 600 "${ssh_config}"
        print_success "SSH設定を更新しました: ${ssh_config}"
    fi

    # GitLab APIでSSH鍵を登録
    if [ -n "$GITLAB_TOKEN" ]; then
        local public_key=$(cat "${ssh_key_path}.pub")
        local key_title="CICD-Auto-$(date +%Y%m%d%H%M%S)"

        # 既存SSH鍵の重複チェック
        local existing_keys=$(curl -s -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
            "${GITLAB_API}/user/keys" | grep -o '"title":"CICD-Auto-[^"]*"' || echo "")

        if [ -z "$existing_keys" ]; then
            # SSH鍵をGitLabに登録
            local ssh_response=$(curl -s -X POST \
                -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
                -H "Content-Type: application/json" \
                -d "{\"title\": \"${key_title}\", \"key\": \"${public_key}\"}" \
                "${GITLAB_API}/user/keys")

            if echo "$ssh_response" | grep -q '"id"'; then
                print_success "SSH公開鍵をGitLabに登録しました: ${key_title}"
            else
                print_warning "SSH鍵登録に失敗しました: $ssh_response"
                return 1
            fi
        else
            print_info "既存のSSH鍵が登録済みです"
        fi
    else
        print_warning "GitLab Personal Access Tokenがないため、手動でSSH鍵を登録してください"
        print_info "SSH公開鍵: ${ssh_key_path}.pub"
        cat "${ssh_key_path}.pub"
        return 1
    fi

    return 0
}

# SSH認証セットアップ実行
if setup_ssh_authentication; then
    # SSH形式のリモートURL設定
    print_info "GitLabリモートURL（SSH）を設定中..."
    git remote set-url origin "git@gitlab-cicd:root/sample-app.git"
    print_success "リモートURLを設定しました: git@gitlab-cicd:root/sample-app.git"

    # SSH経由でプッシュ実行
    print_info "SSH経由でGitLabにプッシュ中..."
    if git push -u origin master 2>/dev/null; then
        print_success "GitLabへのプッシュが完了しました"
        print_info "CI/CDパイプラインが自動実行されます"
    else
        print_warning "SSH経由のプッシュに失敗しました"
        echo "  デバッグ情報:"
        echo "    SSH鍵: $HOME/.ssh/gitlab_cicd_ed25519"
        echo "    接続テスト: ssh -T git@gitlab-cicd"
        echo "  手動プッシュ:"
        echo "    cd ${BASE_DIR}/sample-app"
        echo "    git push -u origin master"
    fi
else
    print_warning "SSH認証セットアップに失敗しました。手動でSSH鍵を設定してください"
    echo "  1. SSH鍵生成: ssh-keygen -t ed25519 -f ~/.ssh/gitlab_cicd_ed25519"
    echo "  2. 公開鍵をGitLabに登録: User Settings → SSH Keys"
    echo "  3. リモートURL変更: git remote set-url origin git@${EC2_PUBLIC_IP}:root/sample-app.git"
    echo "  4. プッシュ実行: git push -u origin master"
fi

# ========================================================================
# ステップ6: セットアップ完了確認
# ========================================================================
echo ""
echo "=========================================="
echo "[6/6] セットアップ完了確認"
echo "=========================================="

print_info "GitLab Runner状態確認..."
if sudo systemctl is-active --quiet gitlab-runner; then
    print_success "GitLab Runnerが正常に動作しています"
    # CRITICAL: GitLabRunnerパスは /usr/bin/gitlab-runner 固定 - 変更禁止
    sudo /usr/bin/gitlab-runner list
else
    print_warning "GitLab Runnerが停止しています"
    sudo systemctl status gitlab-runner --no-pager
fi

print_info "CI/CDパイプライン確認..."
echo "  パイプライン実行状況: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/pipelines"
echo "  プロジェクト設定: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/settings/ci_cd"

echo ""
echo "=========================================="
echo "✅ CI/CDセットアップ完了"
echo "=========================================="
echo ""
echo "🚀 次のステップ:"
echo "  1. パイプライン実行確認:"
echo "     http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/pipelines"
echo ""
echo "  2. sample-appの開発開始:"
echo "     cd ${BASE_DIR}/sample-app"
echo "     # コード変更"
echo "     git add ."
echo "     git commit -m \"feat: 新機能追加\""
echo "     git push origin master"
echo ""
echo "  3. パイプライン構成 (6ステージ):"
echo "     build → test → coverage → sonarqube → package → deploy"
echo ""
echo "  4. 品質ゲート基準:"
echo "     - 行カバレッジ: ≥80%"
echo "     - ブランチカバレッジ: ≥70%"
echo "     - 重大バグ: 0件"
echo ""
echo "🔧 管理用コマンド:"
echo "  - Runner確認: sudo systemctl status gitlab-runner"
echo "  - ログ確認: sudo journalctl -u gitlab-runner -f"
echo "  - 環境変数確認: ${BASE_DIR}/scripts/show-credentials.sh"
echo ""

# 認証情報の最終表示
print_info "更新された認証情報を表示中..."
"${SCRIPT_DIR}/show-credentials.sh"

print_success "CI/CD環境セットアップが完了しました！"