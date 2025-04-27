#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building J-PlatPat container..."
podman-compose build

echo ""
echo "J-PlatPat コンテナ化システムを起動しました。"
echo "以下のコマンド例を試すことができます："
echo ""
echo "ヘルプの表示："
echo "  podman-compose run --rm jplatpat"
echo ""
echo "企業名によるデータインポート："
echo "  podman-compose run --rm jplatpat import --company \"トヨタ自動車\" --limit 10"
echo ""
echo "レポート生成："
echo "  podman-compose run --rm jplatpat analyze report --output /data/my_report.md"
echo ""

echo "コンテナの使い方の詳細については README.md をご覧ください。"
