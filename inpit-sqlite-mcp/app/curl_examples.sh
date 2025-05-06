#!/bin/bash
# -*- coding: utf-8 -*-

# Example curl commands for inpit-sqlite-mcp server with non-ASCII characters
# This script demonstrates how to use the API with Japanese characters

# Base URL
BASE_URL="http://localhost:8000"

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== inpit-sqlite-mcp API curlコマンド例 =====${NC}"
echo "非ASCIIキャラクター（日本語など）を直接URLで使用できるようになりました。"
echo "スペースを含む日本語のURLも処理できます。"
echo ""

echo -e "${BLUE}【スペースを含む日本語URLの対応方法】${NC}"
echo " 1. URLエンコードされた%20を使用"
echo " 2. クオート（'）で囲む方法"
echo " 3. すべての文字をパーセントエンコードする方法"
echo ""

# Check server status
echo -e "${GREEN}サーバーステータスの確認:${NC}"
echo "curl ${BASE_URL}/status"
echo ""

# Get patents by applicant name
echo -e "${GREEN}出願人名によるデータ取得 (日本語を直接使用):${NC}"
echo "curl ${BASE_URL}/applicant/テック株式会社"
echo ""

# Get patents by applicant name with spaces
echo -e "${GREEN}出願人名によるデータ取得 (スペースを含む場合):${NC}"
echo "# 方法1: %20でエンコード"
echo "curl ${BASE_URL}/applicant/テック%20株式会社"
echo ""
echo "# 方法2: シングルクォートで囲む"
echo "curl '${BASE_URL}/applicant/テック 株式会社'"
echo ""
echo "# 方法3: 完全URLエンコード"
echo "curl ${BASE_URL}/applicant/%E3%83%86%E3%83%83%E3%82%AF%20%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
echo ""

# POST method for applicant with Japanese name
echo -e "${GREEN}POST形式での出願人名によるデータ取得 (URLエンコード):${NC}"
echo "# --data-urlencode を使用したPOSTリクエスト"
echo "curl -X POST \"${BASE_URL}/applicant\" --data-urlencode \"name=テック 株式会社\""
echo ""
echo "# フォームデータとしての送信"
echo "curl -X POST -F \"name=テック 株式会社\" ${BASE_URL}/applicant"
echo ""

# Get applicant summary
echo -e "${GREEN}出願人のサマリー取得:${NC}"
echo "curl ${BASE_URL}/applicant-summary/テック株式会社"
echo ""

# Get assessment ratios
echo -e "${GREEN}審査比率の分析:${NC}"
echo "curl ${BASE_URL}/assessment/テック株式会社"
echo ""

# Get technical field analysis
echo -e "${GREEN}技術分野の分析:${NC}"
echo "curl ${BASE_URL}/technical/テック株式会社"
echo ""

# Compare with competitors
echo -e "${GREEN}競合他社との比較:${NC}"
echo "curl ${BASE_URL}/compare/テック株式会社"
echo ""

# Generate visual report
echo -e "${GREEN}視覚的なレポートの生成:${NC}"
echo "curl ${BASE_URL}/visual-report/テック株式会社"
echo ""

# Execute SQL query
echo -e "${GREEN}SQLクエリの実行:${NC}"
echo 'curl -X POST -d "query=SELECT * FROM inpit_data WHERE 出願人 LIKE '\''%テック%'\'' LIMIT 5" ${BASE_URL}/sql'
echo ""

# Execute SQL query with spaces in the query
echo -e "${GREEN}SQLクエリの実行 (スペースを含む検索):${NC}"
echo 'curl -X POST -d "query=SELECT * FROM inpit_data WHERE 出願人 LIKE '\''%テック 株式%'\'' LIMIT 5" ${BASE_URL}/sql'
echo ""

echo -e "${GREEN}テスト用スクリプトの実行:${NC}"
echo "# URLエンコーディングテストの実行"
echo "python test_url_encoding.py"
echo ""
echo "# スペース処理特化テストの実行"
echo "python test_space_encoding.py" 
echo ""

# Execute SQL query with JSON
echo -e "${GREEN}JSON形式でのSQLクエリ:${NC}"
echo 'curl -X POST -H "Content-Type: application/json" -d '\''{"query": "SELECT * FROM inpit_data WHERE 出願人 LIKE '\''%テック%'\'' LIMIT 5"}'\''" ${BASE_URL}/sql/json'
echo ""

echo -e "${YELLOW}=====================================${NC}"
echo "注: 適切なデータベース、テーブル、カラムに合わせてSQLクエリを調整してください。"
echo "    実行するには、上記のコマンドをコピーしてターミナルに貼り付けてください。"
echo ""
echo -e "${BLUE}注意事項:${NC}"
echo "日本語のURLに関して以下の点に注意してください："
echo "1. スペースを含む場合は、%20を使用するか、URLをシングルクォートで囲みます。"
echo "2. curl使用時は、シングルクォート内でのエスケープが必要な場合があります。"
echo "3. ブラウザなどのクライアントは通常自動的にURLエンコーディングを行いますが、"
echo "   curlなどのツールを使用する場合は明示的なエンコーディングが必要な場合があります。"
echo ""
