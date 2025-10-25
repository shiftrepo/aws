#!/bin/bash
# Docling Container 管理スクリプト

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
    echo "Docling Container 管理スクリプト"
    echo ""
    echo "使用方法: ./scripts.sh [コマンド]"
    echo ""
    echo "利用可能なコマンド:"
    echo "  build          コンテナイメージをビルド"
    echo "  start          コンテナを起動（バックグラウンド）"
    echo "  stop           コンテナを停止"
    echo "  restart        コンテナを再起動"
    echo "  logs           コンテナのログを表示"
    echo "  shell          コンテナ内のシェルに接続"
    echo "  status         コンテナの状態を確認"
    echo "  clean          停止済みコンテナとイメージを削除"
    echo "  process [file] ファイルを処理（Markdown形式で出力）"
    echo "  help           このヘルプを表示"
}

# コンテナビルド
build_container() {
    echo -e "${YELLOW}Doclingコンテナをビルドしています...${NC}"
    podman-compose build
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}ビルドが完了しました！${NC}"
    else
        echo -e "${RED}ビルドに失敗しました。${NC}"
        exit 1
    fi
}

# コンテナ起動
start_container() {
    echo -e "${YELLOW}Doclingコンテナを起動しています...${NC}"
    podman-compose up -d
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}コンテナが起動しました！${NC}"
        show_status
    else
        echo -e "${RED}コンテナの起動に失敗しました。${NC}"
        exit 1
    fi
}

# コンテナ停止
stop_container() {
    echo -e "${YELLOW}Doclingコンテナを停止しています...${NC}"
    podman-compose down
    echo -e "${GREEN}コンテナを停止しました。${NC}"
}

# コンテナ再起動
restart_container() {
    echo -e "${YELLOW}Doclingコンテナを再起動しています...${NC}"
    stop_container
    start_container
}

# ログ表示
show_logs() {
    echo -e "${YELLOW}コンテナのログを表示します（Ctrl+Cで終了）：${NC}"
    podman-compose logs -f docling
}

# シェル接続
connect_shell() {
    echo -e "${YELLOW}コンテナのシェルに接続します...${NC}"
    podman exec -it docling-processor bash
}

# 状態確認
show_status() {
    echo -e "${YELLOW}コンテナの状態：${NC}"
    podman-compose ps
    echo ""
    echo -e "${YELLOW}共有ディレクトリの状態：${NC}"
    echo "入力ファイル数: $(find data/input -type f 2>/dev/null | wc -l)"
    echo "出力ファイル数: $(find data/output -type f 2>/dev/null | wc -l)"
    echo "キャッシュサイズ: $(du -sh data/cache 2>/dev/null | cut -f1 || echo "0B")"
}

# クリーンアップ
clean_up() {
    echo -e "${YELLOW}不要なコンテナとイメージを削除しています...${NC}"
    podman-compose down
    podman system prune -f
    echo -e "${GREEN}クリーンアップが完了しました。${NC}"
}

# ファイル処理
process_file() {
    if [ -z "$1" ]; then
        echo -e "${RED}エラー: ファイル名を指定してください。${NC}"
        echo "使用方法: ./scripts.sh process <ファイル名>"
        exit 1
    fi

    local file_path="$1"
    echo -e "${YELLOW}ファイルを処理しています: ${file_path}${NC}"

    podman exec docling-processor python process_documents.py "${file_path}"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}ファイルの処理が完了しました！${NC}"
        echo "出力ファイルは data/output/ ディレクトリで確認できます。"
    else
        echo -e "${RED}ファイルの処理に失敗しました。${NC}"
        exit 1
    fi
}

# メイン処理
case "$1" in
    build)
        build_container
        ;;
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        connect_shell
        ;;
    status)
        show_status
        ;;
    clean)
        clean_up
        ;;
    process)
        process_file "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}エラー: 不明なコマンド '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac