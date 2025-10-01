#!/bin/bash

# GitLab MCPをインストール
npm install -g @modelcontextprotocol/server-gitlab

# 環境変数の設定
if [ -z "$GITLAB_API_TOKEN" ]; then
    echo "GITLAB_API_TOKEN環境変数が設定されていません。"
    echo "GitLabからパーソナルアクセストークンを取得し、環境変数に設定してください。"
    exit 1
fi

# 一時ファイルに環境変数を展開した設定を作成
envsubst < add_gitlab_mcp.json > add_token_gitlab_mcp.json

# GitLab MCPをClaude Codeに追加
claude mcp add-json gitlab-org "$(cat add_token_gitlab_mcp.json)" --verbose

# 一時ファイルを削除
rm -f add_token_gitlab_mcp.json

echo "GitLab MCPの設定が完了しました。"