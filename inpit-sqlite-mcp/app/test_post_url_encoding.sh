#!/bin/bash
# -*- coding: utf-8 -*-

# Test script for URL encoding in POST requests with Japanese text
# Testing specifically the format:
# curl -X POST "http://localhost:8000/applicant" --data-urlencode "name=テック 株式会社"

# ANSI color codes for nice output formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL (can be overridden by first argument)
BASE_URL=${1:-"http://localhost:8000"}

echo -e "${YELLOW}===== POST URLエンコーディングテスト =====${NC}"
echo "日本語と空白を含むデータの POST リクエストテスト"
echo ""

# Check if the server is running
echo -e "${BLUE}サーバー接続確認:${NC}"
if curl -s "${BASE_URL}/status" > /dev/null; then
    echo "✓ サーバーは実行中です"
else
    echo -e "${RED}エラー: サーバー ${BASE_URL} に接続できません。サーバーが起動していることを確認してください。${NC}"
    exit 1
fi

echo ""

# Test with the SQL endpoint (which already accepts POST requests)
echo -e "${BLUE}1. SQLエンドポイントでのテスト (/sql):${NC}"
echo -e "${GREEN}コマンド:${NC} curl -X POST \"${BASE_URL}/sql\" --data-urlencode \"query=SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック 株式会社%' LIMIT 5\""

echo -e "\n${BLUE}実行結果:${NC}"
curl -X POST "${BASE_URL}/sql" --data-urlencode "query=SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック 株式会社%' LIMIT 5"
echo -e "\n"

# Test with JSON body
echo -e "${BLUE}2. JSONボディでのテスト (/sql/json):${NC}"
echo -e "${GREEN}コマンド:${NC} curl -X POST \"${BASE_URL}/sql/json\" -H \"Content-Type: application/json\" -d '{\"query\": \"SELECT * FROM inpit_data WHERE 出願人 LIKE \\\"%テック 株式会社%\\\" LIMIT 5\"}'"

echo -e "\n${BLUE}実行結果:${NC}"
curl -X POST "${BASE_URL}/sql/json" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"SELECT * FROM inpit_data WHERE 出願人 LIKE \\\"%テック 株式会社%\\\" LIMIT 5\"}"
echo -e "\n"

# Test the specific requested format (if the endpoint exists)
echo -e "${BLUE}3. ユーザー指定形式テスト (/applicant):${NC}"
echo -e "${GREEN}コマンド:${NC} curl -X POST \"${BASE_URL}/applicant\" --data-urlencode \"name=テック 株式会社\""

echo -e "\n${BLUE}実行結果:${NC}"
curl -X POST "${BASE_URL}/applicant" --data-urlencode "name=テック 株式会社"
echo -e "\n"
echo -e "${YELLOW}注意:${NC} もしこのエンドポイントが404エラーを返す場合は、POSTメソッドで/applicantエンドポイントが存在しないことを意味します。"
echo -e "      エンドポイントが存在することを確認するか、サーバーコードを確認してください。"

echo ""
echo -e "${YELLOW}==== 補足情報 ====${NC}"
echo -e "${BLUE}--data-urlencodeフラグの動作:${NC}"
echo "curlの--data-urlencodeフラグは自動的にフォームデータをURLエンコードします。"
echo "例: 'テック 株式会社' → 'テック%20株式会社' または '%E3%83%86%E3%83%83%E3%82%AF%20%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE'"
echo ""
echo -e "${BLUE}Pythonでの同等実装例:${NC}"
echo "import requests"
echo "response = requests.post('${BASE_URL}/applicant', data={'name': 'テック 株式会社'})"
echo ""
