#!/bin/bash

# Patent API curl examples with proper URL encoding for Japanese characters
# This script demonstrates how to make API calls with Japanese applicant names

BASE_URL="http://localhost:8000"

# ASCII art header
echo "=========================================================="
echo "  特許 API curl コマンド例 - Patent API curl examples"
echo "=========================================================="

# Function to display usage info
show_usage() {
  echo 
  echo "Usage: $0 [applicant_name]"
  echo
  echo "If no argument is provided, the script will run examples with predefined applicant names."
  echo "If an argument is provided, it will generate a properly encoded curl command for that applicant name."
  echo
}

# Check if curl is installed
if ! command -v curl &> /dev/null; then
  echo "Error: curl is not installed. Please install curl first."
  exit 1
fi

# If an argument is provided, use it as the applicant name
if [ "$#" -eq 1 ]; then
  applicant="$1"
  
  # URL encode the applicant name
  # This uses Python to ensure proper encoding of non-ASCII characters
  encoded_applicant=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$applicant'))")
  
  echo "原本 (Original): $applicant"
  echo "エンコード済み (URL Encoded): $encoded_applicant"
  echo
  echo "curl コマンド (curl command):"
  echo "curl \"$BASE_URL/applicant/$encoded_applicant\""
  echo
  exit 0
fi

# Display usage info
show_usage

# Run examples with predefined applicant names
applicants=(
  "テック株式会社"
  "日本特許株式会社" 
  "東京電機株式会社"
  "ソフトウェア技術研究所"
)

# Demonstrate URL encoding for each applicant name
for applicant in "${applicants[@]}"; do
  echo
  echo "----------------------------------------------------------"
  echo "出願人 (Applicant): $applicant"
  
  # URL encode the applicant name using Python
  encoded_applicant=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$applicant'))")
  
  echo "エンコード済み (URL Encoded): $encoded_applicant"
  echo
  echo "curl コマンド (curl command):"
  echo "curl \"$BASE_URL/applicant/$encoded_applicant\""
  echo
  echo "レポート取得 (Get report):"
  echo "curl \"$BASE_URL/report/$encoded_applicant\""
  echo
  echo "評価分析 (Assessment analysis):"
  echo "curl \"$BASE_URL/assessment/$encoded_applicant\""
  echo
  echo "技術分野分析 (Technical field analysis):"
  echo "curl \"$BASE_URL/technical/$encoded_applicant\""
  echo
  echo "競合比較 (Compare with competitors):"
  echo "curl \"$BASE_URL/compare/$encoded_applicant\""
  echo "----------------------------------------------------------"
done

echo
echo "特許情報 (Patent information):"
echo "curl \"$BASE_URL/resources\""
echo
echo "利用可能なツール (Available tools):"
echo "curl \"$BASE_URL/tools\""
echo

# Show a more complex POST example for completeness
echo "POSTリクエスト例 (POST request example):"
echo "curl -X POST \"$BASE_URL/tools/execute\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"tool_name\": \"generate_pdf_report\", \"arguments\": {\"applicant_name\": \"テック株式会社\", \"years\": 5}}'"
echo

echo "Done! Script complete."
