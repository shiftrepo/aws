#!/bin/bash

# このスクリプトは特許分析MCPコンテナの接続性をpythonを使用してテストします
# curl、pingなどのネットワークユーティリティが利用できない場合の代替スクリプトです

# カラー定義
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo "======================================================"
echo "  特許分析MCPコンテナ通信テスト (代替版)"
echo "======================================================"
echo ""

# podman-composeを使用
CONTAINER_RUNTIME="podman"
COMPOSE_COMMAND="podman-compose"
echo -e "${BLUE}podman-composeを使用します${NC}"

# podman-composeがインストールされているか確認
if ! command -v podman-compose &> /dev/null; then
  echo -e "${RED}エラー: podman-composeがインストールされていません${NC}"
  exit 1
fi

# patent-analysis-mcpコンテナが実行中かチェック
if ! $CONTAINER_RUNTIME ps | grep -q "patent-analysis-mcp"; then
  echo -e "${RED}patent-analysis-mcpコンテナが実行されていません。${NC}"
  echo -e "${YELLOW}$COMPOSE_COMMANDでサービスを起動してください。${NC}"
  exit 1
fi

echo ""
echo -e "${BLUE}1. Pythonを使用してコンテナ内からの接続テスト...${NC}"

# Pythonスクリプトの作成
cat > test_connection.py << 'EOF'
import socket
import sys
import urllib.request
import json

def check_dns(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"ホスト名 {hostname} は {ip} に解決されました")
        return True
    except socket.gaierror:
        print(f"ホスト名 {hostname} を解決できません")
        return False

def check_http(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return response.getcode() == 200
    except Exception as e:
        print(f"HTTP接続エラー: {e}")
        return False

def test_api_query(url, query_data):
    try:
        data = json.dumps(query_data).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode('utf-8'))
        return "test_connection" in str(result)
    except Exception as e:
        print(f"API接続エラー: {e}")
        return False

# メイン処理
print("=== DNS解決テスト ===")
patentdwh_db_dns = check_dns("patentdwh-db")
patentdwh_mcp_dns = check_dns("patentdwh-mcp-enhanced")

print("\n=== HTTP接続テスト ===")
patentdwh_db_http = False
if patentdwh_db_dns:
    try:
        patentdwh_db_http = check_http("http://patentdwh-db:5002/health")
        if patentdwh_db_http:
            print("patentdwh-dbへのHTTP接続に成功しました")
        else:
            print("patentdwh-dbへのHTTP接続に失敗しました")
    except Exception as e:
        print(f"HTTP接続テストでエラーが発生しました: {e}")

patentdwh_mcp_http = False
if patentdwh_mcp_dns:
    try:
        patentdwh_mcp_http = check_http("http://patentdwh-mcp-enhanced:8080/health")
        if patentdwh_mcp_http:
            print("patentdwh-mcp-enhancedへのHTTP接続に成功しました")
        else:
            print("patentdwh-mcp-enhancedへのHTTP接続に失敗しました")
    except Exception as e:
        print(f"HTTP接続テストでエラーが発生しました: {e}")

print("\n=== API経由のDBアクセステスト ===")
if patentdwh_db_dns:
    try:
        query_data = {"query": "SELECT 1 AS test_connection", "db_type": "sqlite"}
        api_success = test_api_query("http://patentdwh-db:5002/api/sql-query", query_data)
        if api_success:
            print("API経由でのDBクエリに成功しました")
        else:
            print("API経由でのDBクエリに失敗しました")
    except Exception as e:
        print(f"APIテストでエラーが発生しました: {e}")

# 結果の要約
print("\n=== テスト結果の要約 ===")
success_count = sum([patentdwh_db_dns, patentdwh_mcp_dns, patentdwh_db_http, patentdwh_mcp_http])
total_tests = 4

print(f"成功: {success_count}/{total_tests}")
if success_count == total_tests:
    print("すべてのテストに成功しました！")
elif success_count > 0:
    print("一部のテストに成功しましたが、問題があります")
else:
    print("すべてのテストが失敗しました")

print("\nテストが完了しました。")
EOF

# Pythonスクリプトの実行
echo -e "${YELLOW}Pythonスクリプトをコンテナ内で実行しています...${NC}"
$CONTAINER_RUNTIME cp test_connection.py patent-analysis-mcp:/app/
$CONTAINER_RUNTIME exec patent-analysis-mcp python /app/test_connection.py
rm test_connection.py

echo ""
echo -e "${BLUE}2. コンテナのネットワーク設定を確認しています...${NC}"
echo -e "${YELLOW}patent-analysis-mcpコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patent-analysis-mcp --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}'
echo ""

echo -e "${YELLOW}patentdwh-dbコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patentdwh-db --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}' 2>/dev/null || echo "コンテナが見つかりません"
echo ""

echo -e "${YELLOW}patentdwh-mcp-enhancedコンテナのネットワーク設定:${NC}"
$CONTAINER_RUNTIME inspect patentdwh-mcp-enhanced --format='{{range $key, $value := .NetworkSettings.Networks}}{{$key}}{{end}}' 2>/dev/null || echo "コンテナが見つかりません"
echo ""

echo -e "${BLUE}3. ネットワーク一覧:${NC}"
$CONTAINER_RUNTIME network ls

# podman-composeの設定を表示
echo ""
echo -e "${BLUE}4. podman-compose設定ファイルの確認:${NC}"
echo -e "${YELLOW}podman-compose.yml の内容:${NC}"
cat podman-compose.yml | grep -A10 "networks:"
echo ""

# コンテナ接続性修正ヒント
echo ""
echo -e "${GREEN}テスト完了！${NC}"
echo "各テストの結果を確認し、ネットワーク設定を必要に応じて調整してください。"
echo ""
echo -e "${YELLOW}問題がある場合の対処法:${NC}"
echo "1. セットアップスクリプトを実行してネットワーク設定とユーティリティのインストールを確認してください："
echo "   ./setup_podman_environment.sh"
echo ""
echo "2. patentdwh_defaultネットワークが存在することを確認してください："
echo "   $CONTAINER_RUNTIME network ls | grep patentdwh_default"
echo ""
echo "3. 存在しない場合、以下のコマンドで作成できます："
echo "   $CONTAINER_RUNTIME network create patentdwh_default"
echo ""
echo "4. 再度サービスを起動してください："
echo "   cd /root/aws.git/patent_analysis_container && $COMPOSE_COMMAND -f podman-compose.yml up -d"
echo ""
echo "5. コンテナ内にnetcatユーティリティがインストールされている場合は、以下のコマンドでポート接続性を確認できます："
echo "   $CONTAINER_RUNTIME exec patent-analysis-mcp bash -c 'nc -zv patentdwh-db 5002'"
echo "   $CONTAINER_RUNTIME exec patent-analysis-mcp bash -c 'nc -zv patentdwh-mcp-enhanced 8080'"
echo ""
