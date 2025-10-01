#!/bin/bash
# MCPサーバーの登録スクリプト

echo "====================================================="
echo "MCPサーバーの登録を開始します"
echo "====================================================="

# 環境変数の確認
if [ -z "$GITLAB_API_TOKEN" ]; then
    echo "警告: GITLAB_API_TOKEN環境変数が設定されていません。"
    echo "GitLab MCPの機能を使用する場合は、設定してください。"
fi

# GitLab MCPの登録
echo "1. GitLab MCPサーバーを登録します..."
claude mcp add-json gitlab-org "$(cat <<EOF
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-gitlab"],
  "env": {
    "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}"
  }
}
EOF
)" --verbose || echo "GitLab MCPの登録に失敗しました"

# Filesystem MCPの登録
if [ "${MCP_FILESYSTEM_ENABLED:-0}" = "1" ]; then
    echo "2. Filesystem MCPサーバーを登録します..."
    claude mcp add-json filesystem "$(cat <<EOF
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": {}
}
EOF
)" --verbose || echo "Filesystem MCPの登録に失敗しました"
else
    echo "2. Filesystem MCPサーバーはスキップします（MCP_FILESYSTEM_ENABLED=1を設定してください）"
fi

# Sequential Thinking MCPの登録
if [ "${MCP_SEQUENTIAL_THINKING_ENABLED:-0}" = "1" ]; then
    echo "3. Sequential Thinking MCPサーバーを登録します..."
    claude mcp add-json thinking "$(cat <<EOF
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "env": {}
}
EOF
)" --verbose || echo "Sequential Thinking MCPの登録に失敗しました"
else
    echo "3. Sequential Thinking MCPサーバーはスキップします（MCP_SEQUENTIAL_THINKING_ENABLED=1を設定してください）"
fi

# SQLite MCPの登録
if [ "${MCP_SQLITE_ENABLED:-0}" = "1" ]; then
    echo "4. SQLite MCPサーバーを登録します..."
    claude mcp add-json sqlite "$(cat <<EOF
{
  "command": "npx",
  "args": ["-y", "mcp-server-sqlite-npx"],
  "env": {}
}
EOF
)" --verbose || echo "SQLite MCPの登録に失敗しました"
else
    echo "4. SQLite MCPサーバーはスキップします（MCP_SQLITE_ENABLED=1を設定してください）"
fi

# Git MCPの登録
if [ "${MCP_GIT_ENABLED:-0}" = "1" ]; then
    echo "5. Git MCPサーバーを登録します..."
    claude mcp add-json git "$(cat <<EOF
{
  "command": "python3",
  "args": ["-m", "mcp_server_git"],
  "env": {}
}
EOF
)" --verbose || echo "Git MCPの登録に失敗しました"
else
    echo "5. Git MCPサーバーはスキップします（MCP_GIT_ENABLED=1を設定してください）"
fi

# 登録確認
echo "====================================================="
echo "MCPサーバーの登録状況を確認します:"
claude mcp list
echo "====================================================="
echo "セットアップが完了しました。"
echo "====================================================="