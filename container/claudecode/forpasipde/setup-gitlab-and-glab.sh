#!/bin/bash
# GitLab MCPとGitLab CLI (glab)のセットアップスクリプト

echo "====================================================="
echo "GitLab MCPとGitLab CLI (glab)のセットアップを開始します"
echo "====================================================="

# 必要な環境変数をチェック
if [ -z "$GITLAB_API_TOKEN" ]; then
    echo "エラー: GITLAB_API_TOKEN環境変数が設定されていません。"
    echo "GitLabからパーソナルアクセストークンを取得し、環境変数に設定してください。"
    exit 1
fi

# GitLab MCPのセットアップ
echo "1. GitLab MCPのセットアップを実行します..."
if [ -f ./setup_gitlab_mcp.sh ]; then
    ./setup_gitlab_mcp.sh
    if [ $? -ne 0 ]; then
        echo "GitLab MCPのセットアップに失敗しました。"
        exit 1
    fi
    echo "GitLab MCPのセットアップが完了しました。"
else
    echo "エラー: setup_gitlab_mcp.shファイルが見つかりません。"
    exit 1
fi

# GitLab CLI (glab)のセットアップ
echo "2. GitLab CLI (glab)のセットアップを実行します..."
if [ -f ./install_glab.sh ]; then
    ./install_glab.sh
    if [ $? -ne 0 ]; then
        echo "GitLab CLI (glab)のインストールに失敗しました。"
        exit 1
    fi
    
    # glabの設定
    echo "GitLab CLI (glab)の設定を行います..."
    glab auth login --token $GITLAB_API_TOKEN
    
    echo "GitLab CLI (glab)のセットアップが完了しました。"
else
    echo "エラー: install_glab.shファイルが見つかりません。"
    exit 1
fi

echo "====================================================="
echo "セットアップが正常に完了しました！"
echo "以下のツールが利用可能です:"
echo "- GitLab MCP: claude mcp list で確認できます"
echo "- GitLab CLI (glab): glab --version で確認できます"
echo "====================================================="