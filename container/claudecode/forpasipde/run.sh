#!/bin/bash

# Claude Code実行環境起動スクリプト（複数ベースイメージ対応）

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
    echo "起動後の追加設定:"
    echo "  docker-compose -f <COMPOSE_FILE> exec claudecode-<BASE_IMAGE> bash -c './setup-gitlab-and-glab.sh' # GitLab MCPとglabをセットアップ"
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

# 必要な環境変数の確認
if [ -z "$GITLAB_API_TOKEN" ]; then
    echo "警告: GITLAB_API_TOKEN環境変数が設定されていません。"
    echo "GitLab MCPの機能を使用する場合は、GitLabからパーソナルアクセストークンを取得し、環境変数に設定してください。"
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

# DockerとDocker Compose/Podman Composeの確認
if command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
elif command -v podman &> /dev/null; then
    DOCKER_CMD="podman"
else
    echo "エラー: DockerまたはPodmanがインストールされていません。"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
else
    echo "エラー: Docker ComposeまたはPodman Composeがインストールされていません。"
    exit 1
fi

# 既存のコンテナを停止（クリーンアップ）
echo "既存のコンテナを停止しています..."
$COMPOSE_CMD -f "$COMPOSE_FILE" down 2>/dev/null || true

# コンテナの起動
echo "コンテナを起動しています..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d

# 起動確認
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Claude Code環境が正常に起動しました！"
    echo ""
    echo "次のステップ:"
    echo "1. コンテナに接続: $COMPOSE_CMD -f $COMPOSE_FILE exec claude-code-$BASE_IMAGE bash"
    echo "2. MCPサーバーのセットアップ: $COMPOSE_CMD -f $COMPOSE_FILE exec claude-code-$BASE_IMAGE bash -c '/app/setup_mcp_servers.sh'"
    echo "3. ログ確認: $COMPOSE_CMD -f $COMPOSE_FILE logs -f"
    echo "4. 停止: $COMPOSE_CMD -f $COMPOSE_FILE down"
    echo ""
    echo "GitLab管理画面:"
    case $BASE_IMAGE in
        node)
            echo "  http://localhost:8080 (Node.js版用)"
            ;;
        debian)
            echo "  http://localhost:8081 (Debian版用)"
            ;;
        amazonlinux|*)
            echo "  http://localhost:80 (Amazon Linux版用)"
            ;;
    esac
    echo ""
else
    echo "❌ コンテナの起動に失敗しました。"
    echo "ログを確認してください: $COMPOSE_CMD -f $COMPOSE_FILE logs"
    exit 1
fi