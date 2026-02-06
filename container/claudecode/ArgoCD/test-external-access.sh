#!/bin/bash
# Test external access to all services

echo "=========================================="
echo "外部アクセステスト"
echo "=========================================="
echo ""

test_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    printf "%-20s: " "$name"
    status=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" --max-time 5)
    if [ "$status" == "$expected" ]; then
        echo "✅ HTTP $status"
    else
        echo "❌ HTTP $status (expected $expected)"
    fi
}

echo "【アプリケーション】"
test_service "Frontend" "http://10.0.1.200:5006/" "200"
test_service "Backend Health" "http://10.0.1.200:8083/actuator/health" "200"
test_service "Backend API" "http://10.0.1.200:8083/api/organizations" "200"

echo ""
echo "【GitOps管理】"
test_service "ArgoCD HTTPS" "https://10.0.1.200:8082/" "200"
test_service "ArgoCD HTTP" "http://10.0.1.200:8000/" "307"

echo ""
echo "【iptablesルール確認】"
iptables -t nat -L PREROUTING -n -v | grep -E "5006|8083|8082|8000" | grep REDIRECT | wc -l | xargs echo "  PREROUTING rules:"
iptables -t nat -L OUTPUT -n -v | grep -E "5006|8083|8082|8000" | grep REDIRECT | wc -l | xargs echo "  OUTPUT rules:"

echo ""
echo "【Kubernetesサービス】"
kubectl get svc -A | grep -E "NAME|orgmgmt|argocd-server"

echo ""
echo "=========================================="
echo "テスト完了"
echo "=========================================="
