#!/bin/bash

# Claude Code実行環境起動スクリプト（podman-compose対応版）

# 使用方法を表示する関数
show_usage() {
    echo "使用方法: $0 [BASE_IMAGE]"
    echo ""
    echo "BASE_IMAGE オプション:"
    echo "  node        Node.js slim版を起動（デフォルト）"
    echo "  debian      Debian slim版を起動"
    echo "  amazonlinux Amazon Linux版を起動"
    echo ""
    echo "例:"
    echo "  $0           # Node.js slim版を起動"
    echo "  $0 node      # Node.js slim版を起動"
    echo "  $0 debian    # Debian slim版を起動"
    echo "  $0 amazonlinux # Amazon Linux版を起動"
    echo ""
}

# .envファイルが存在するか確認
if [ ! -f .env ]; then
    echo "エラー: .envファイルが見つかりません。"
    echo ".env.exampleをコピーして必要な値を設定してください。"
    echo "cp .env.example .env"
    exit 1
fi

# workdirディレクトリの確認と作成
if [ ! -d ./workdir ]; then
    echo "workdirディレクトリが存在しません。作成します..."
    mkdir -p ./workdir
    echo "✅ workdirディレクトリを作成しました。"
fi

# 引数の処理
BASE_IMAGE=${1:-node}  # デフォルトはNode.js slim版

# 対応するdocker-composeファイルの選択
case $BASE_IMAGE in
    node)
        COMPOSE_FILE="docker-compose-node.yml"
        echo "🚀 Node.js slim版 Claude Code環境を起動します..."
        ;;
    debian)
        COMPOSE_FILE="docker-compose-debian.yml"
        echo "⚡ Debian slim版 Claude Code環境を起動します..."
        ;;
    amazonlinux)
        COMPOSE_FILE="docker-compose-amazonlinux.yml"
        echo "📝 Amazon Linux版 Claude Code環境を起動します..."
        ;;
    --help|-h|help)
        show_usage
        exit 0
        ;;
    *)
        echo "エラー: 無効なベースイメージ '$BASE_IMAGE' が指定されました。"
        echo ""
        show_usage
        exit 1
        ;;
esac

# docker-composeファイルの存在確認
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "エラー: $COMPOSE_FILE が見つかりません。"
    echo "選択されたベースイメージ ($BASE_IMAGE) はまだ実装されていない可能性があります。"
    echo ""
    echo "利用可能なファイル:"
    ls -la docker-compose*.yml 2>/dev/null || echo "  docker-composeファイルが見つかりません"
    exit 1
fi

# 実行前の確認
echo "設定内容:"
echo "  ベースイメージ: $BASE_IMAGE"
echo "  Composeファイル: $COMPOSE_FILE"
echo "  環境設定ファイル: .env"
echo ""

# podmanとpodman-composeの確認
if ! command -v podman &> /dev/null; then
    echo "エラー: podmanがインストールされていません。"
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo "エラー: podman-composeがインストールされていません。"
    exit 1
fi

# GitLabコンテナの手動起動
echo "GitLabコンテナを起動中..."
podman run -d --name gitlab-node \
    -p 8080:80 -p 8443:443 -p 2223:22 \
    -v gitlab-config-node:/etc/gitlab:z \
    -v gitlab-logs-node:/var/log/gitlab:z \
    -v gitlab-data-node:/var/opt/gitlab:z \
    --shm-size=256m \
    --hostname gitlab.local \
    gitlab/gitlab-ce:latest

sleep 10

# Claude Codeコンテナの起動
echo "Claude Codeコンテナを起動中..."
podman build -t claudecode-node -f node-slim.Dockerfile .

podman run -d --name claude-code-node \
    -v ./.env:/.env:ro \
    -v ./workdir:/app/workdir:z \
    -v ./add_gitlab_mcp.json:/app/add_gitlab_mcp.json:z \
    -v ./add_mcp.json:/app/add_mcp.json:z \
    --env-file .env \
    --tty \
    claudecode-node

# 起動確認
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Claude Code環境が正常に起動しました！"
    echo ""
    echo "次のステップ:"
    echo "1. コンテナに接続: podman exec -it claude-code-node bash"
    echo "2. ログ確認: podman logs -f claude-code-node"
    echo "3. 停止: podman stop claude-code-node gitlab-node"
    echo ""
    echo "GitLab管理画面:"
    echo "  http://localhost:8080 (Node.js版用)"
    echo ""
else
    echo "❌ コンテナの起動に失敗しました。"
    echo "ログを確認してください: podman logs claude-code-node"
    exit 1
fi