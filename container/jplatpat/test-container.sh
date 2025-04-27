#!/bin/bash

# Script to test the jplatpat container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "===== J-PlatPat コンテナテスト ====="
echo "コンテナをビルドしています..."
echo ""

podman-compose build

echo ""
echo "コンテナのヘルプメッセージをテストしています..."
echo ""

podman-compose run --rm jplatpat

echo ""
echo "SQLクエリ機能をテストしています..."
echo ""

podman-compose run --rm jplatpat sql --tables

echo ""
echo "===== テスト完了 ====="
echo ""
echo "コンテナが正常に動作している場合、上記に J-PlatPat CLIのヘルプメッセージとSQLテーブル一覧が表示されているはずです。"
echo "次のステップ："
echo "  1. データをインポート："
echo "     podman-compose run --rm jplatpat import --company \"トヨタ自動車\" --limit 10"
echo ""
echo "  2. データを分析："
echo "     podman-compose run --rm jplatpat analyze trend --years 5 --top-n 10"
echo ""
echo "  3. SQLクエリを実行："
echo "     podman-compose run --rm jplatpat sql -q \"SELECT * FROM patents LIMIT 5\""
echo ""
echo "  4. ファイルからのSQLクエリを実行："
echo "     podman-compose run --rm -v \$(pwd)/test_sql_queries.sql:/queries.sql jplatpat sql -f /queries.sql"
echo ""
echo "詳細は README.md をご覧ください。"
