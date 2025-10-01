#!/bin/bash

# Node.js版Claude Code環境セットアップスクリプト
echo "=== Node.js slim版 Claude Code セットアップ開始 ==="

# Node.jsとnpmのバージョン確認
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Claude Codeの確認
if command -v claude &> /dev/null; then
    echo "Claude Code version: $(claude --version)"
else
    echo "Claude Codeがインストールされていません。インストールを実行します..."
    npm install -g @anthropic-ai/claude-code
fi

# GitLab MCPサーバーの確認
if npm list -g @modelcontextprotocol/server-gitlab &> /dev/null; then
    echo "GitLab MCPサーバーは既にインストール済みです"
else
    echo "GitLab MCPサーバーをインストールします..."
    npm install -g @modelcontextprotocol/server-gitlab
fi

# 環境変数の確認
echo "=== 環境変数の確認 ==="
if [ -z "$GITLAB_API_TOKEN" ]; then
    echo "⚠️  GITLAB_API_TOKEN環境変数が設定されていません。"
    echo "   GitLabからパーソナルアクセストークンを取得し、環境変数に設定してください。"
else
    echo "✅ GITLAB_API_TOKEN: 設定済み"
fi

if [ -z "$ANTHROPIC_MODEL" ]; then
    echo "⚠️  ANTHROPIC_MODEL環境変数が設定されていません。"
else
    echo "✅ ANTHROPIC_MODEL: $ANTHROPIC_MODEL"
fi

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️  AWS認証情報が設定されていません。"
else
    echo "✅ AWS認証情報: 設定済み"
fi

# Claude Code設定ディレクトリの作成
if [ ! -d ~/.claude ]; then
    mkdir -p ~/.claude
    echo "Claude Code設定ディレクトリを作成しました: ~/.claude"
fi

# GitLab MCPの設定
echo "=== GitLab MCP設定 ==="
if [ -n "$GITLAB_API_TOKEN" ]; then
    echo "GitLab MCPを設定します..."
    
    # 一時ファイルに環境変数を展開した設定を作成
    if [ -f "/app/add_gitlab_mcp.json" ]; then
        envsubst < /app/add_gitlab_mcp.json > /tmp/add_token_gitlab_mcp.json
        
        # GitLab MCPをClaude Codeに追加
        claude mcp add-json gitlab-org "$(cat /tmp/add_token_gitlab_mcp.json)" --verbose
        
        # 一時ファイルを削除
        rm -f /tmp/add_token_gitlab_mcp.json
        
        echo "✅ GitLab MCPの設定が完了しました"
    else
        echo "⚠️  GitLab MCP設定ファイルが見つかりません: /app/add_gitlab_mcp.json"
    fi
else
    echo "⚠️  GITLAB_API_TOKENが設定されていないため、GitLab MCPの設定をスキップします"
fi

# MCP設定の確認
echo "=== MCP設定確認 ==="
claude mcp list

# bashrcに環境設定を追加（Node.js版専用）
echo "=== bashrc設定の追加 ==="
cat <<EOF >> ~/.bashrc
# Node.js Claude Code環境設定
export PATH=\$PATH:/usr/local/bin
export NODE_ENV=production

# Claude Code設定
export CLAUDE_CODE_USE_BEDROCK=\${CLAUDE_CODE_USE_BEDROCK:-1}
export ANTHROPIC_MODEL=\${ANTHROPIC_MODEL:-us.anthropic.claude-sonnet-4-20250514-v1:0}
export ANTHROPIC_SMALL_FAST_MODEL=\${ANTHROPIC_SMALL_FAST_MODEL:-us.anthropic.claude-3-5-haiku-20241022-v1:0}

# GitLab連携設定
export GITLAB_HOST=gitlab.local
EOF

echo "✅ bashrc設定を追加しました"

# 設定の反映
source ~/.bashrc

echo "=== Node.js slim版 Claude Code セットアップ完了 ==="
echo ""
echo "次のステップ:"
echo "1. 'claude code' コマンドでClaude Codeを起動"
echo "2. GitLab連携が必要な場合は、http://gitlab.local でGitLabにアクセス"
echo "3. 作業ディレクトリは /app/workdir を使用してください"
echo ""