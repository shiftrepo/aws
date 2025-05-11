#!/bin/bash

# コード行数カウントスクリプト
# 各ディレクトリ内の実コード行とコメント行数をカウントします

# テキストカラー
GREEN="\033[0;32m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}patentDWH システム コード行数統計${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# 結果を格納する配列
declare -A code_lines
declare -A comment_lines
declare -A total_lines

# ディレクトリリスト
dirs=(
  "patentDWH/app"
  "patentDWH/db"
  "patent_analysis_container"
  "patent-mcp-server/app"
  "patent-sqlite"
  "app/patent_system"
)

# カウント関数
count_lines() {
  local dir=$1
  local code=0
  local comment=0
  local total=0
  
  if [ -d "../$dir" ]; then
    # Pythonファイル
    if [ -n "$(find ../$dir -name "*.py" 2>/dev/null)" ]; then
      py_stats=$(find ../$dir -name "*.py" -exec grep -v "^\s*$" {} \; | wc -l)
      py_comments=$(find ../$dir -name "*.py" -exec grep -E "^\s*(#|\"\"\")" {} \; | wc -l)
      code=$((code + py_stats - py_comments))
      comment=$((comment + py_comments))
    fi
    
    # JavaScriptファイル
    if [ -n "$(find ../$dir -name "*.js" 2>/dev/null)" ]; then
      js_stats=$(find ../$dir -name "*.js" -exec grep -v "^\s*$" {} \; | wc -l)
      js_comments=$(find ../$dir -name "*.js" -exec grep -E "^\s*(//|/\*|\*)" {} \; | wc -l)
      code=$((code + js_stats - js_comments))
      comment=$((comment + js_comments))
    fi
    
    # シェルスクリプト
    if [ -n "$(find ../$dir -name "*.sh" 2>/dev/null)" ]; then
      sh_stats=$(find ../$dir -name "*.sh" -exec grep -v "^\s*$" {} \; | wc -l)
      sh_comments=$(find ../$dir -name "*.sh" -exec grep -E "^\s*#" {} \; | wc -l)
      code=$((code + sh_stats - sh_comments))
      comment=$((comment + sh_comments))
    fi
    
    # HTMLファイル
    if [ -n "$(find ../$dir -name "*.html" 2>/dev/null)" ]; then
      html_stats=$(find ../$dir -name "*.html" -exec grep -v "^\s*$" {} \; | wc -l)
      html_comments=$(find ../$dir -name "*.html" -exec grep -E "^\s*(<!--.*-->)" {} \; | wc -l)
      code=$((code + html_stats - html_comments))
      comment=$((comment + html_comments))
    fi
    
    total=$((code + comment))
    
    code_lines["$dir"]=$code
    comment_lines["$dir"]=$comment
    total_lines["$dir"]=$total
    
    echo -e "ディレクトリ: ${GREEN}$dir${NC}"
    echo "  実コード行数: $code"
    echo "  コメント行数: $comment"
    echo "  合計行数: $total"
    echo ""
  else
    echo "ディレクトリ ${dir} は存在しません。スキップします。"
    echo ""
  fi
}

# 各ディレクトリの行数をカウント
for dir in "${dirs[@]}"; do
  count_lines "$dir"
done

# 合計を計算
total_code=0
total_comment=0
total_all=0

for dir in "${dirs[@]}"; do
  if [[ -v code_lines["$dir"] ]]; then
    total_code=$((total_code + code_lines["$dir"]))
    total_comment=$((total_comment + comment_lines["$dir"]))
    total_all=$((total_all + total_lines["$dir"]))
  fi
done

# マークダウンテーブルの出力
echo -e "${BLUE}### マークダウン形式の統計表${NC}"
echo ""
echo "| コンポーネント | 実コード行数 | コメント行数 | 合計行数 |"
echo "|-------------|-----------|----------|--------|"

for dir in "${dirs[@]}"; do
  if [[ -v code_lines["$dir"] ]]; then
    echo "| $dir | ${code_lines["$dir"]} | ${comment_lines["$dir"]} | ${total_lines["$dir"]} |"
  fi
done

echo "| **合計** | **$total_code** | **$total_comment** | **$total_all** |"
echo ""
echo -e "${BLUE}注：この統計は空白行を除外し、Python、JavaScript、シェルスクリプト、HTMLファイルを対象に計測しています。${NC}"
