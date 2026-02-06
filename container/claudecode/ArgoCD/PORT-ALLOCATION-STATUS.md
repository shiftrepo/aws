# ポート割り当て状況

## 利用可能な外部ポート一覧

| ポート | ステータス | サービス | 用途 |
|-------|----------|---------|------|
| 3000 | ⚪ 未使用 | - | 利用可能 |
| 8501 | ⚪ 未使用 | - | 利用可能 |
| 8000 | ✅ 使用中 | ArgoCD | HTTP (リダイレクト) |
| 8082 | ✅ 使用中 | ArgoCD | HTTPS (UI) |
| 8083 | ✅ 使用中 | Backend | REST API |
| 5001 | ⚪ 未使用 | - | 利用可能 |
| 5002 | ⚪ 未使用 | - | 利用可能 |
| 5003 | ⚪ 未使用 | - | 利用可能 |
| 5004 | ⚪ 未使用 | - | 利用可能 |
| 5005 | ⚪ 未使用 | - | 利用可能 |
| 5006 | ✅ 使用中 | Frontend | Web UI |

## 現在のサービスアクセスURL

### アプリケーション
- **Frontend**: http://10.0.1.200:5006
- **Backend API**: http://10.0.1.200:8083
  - Health Check: http://10.0.1.200:8083/actuator/health
  - Organizations API: http://10.0.1.200:8083/api/organizations

### GitOps管理
- **ArgoCD HTTPS**: https://10.0.1.200:8082 (推奨)
- **ArgoCD HTTP**: http://10.0.1.200:8000 (HTTPSにリダイレクト)
  - Username: admin
  - Password: /root/argocd-credentials.txt 参照

## 動作確認結果

| サービス | URL | ステータス | 備考 |
|---------|-----|-----------|------|
| Frontend | http://10.0.1.200:5006 | ✅ HTTP 200 | 正常 (iptables転送) |
| Backend | http://10.0.1.200:8083 | ✅ HTTP 200 | 正常 (iptables転送) |
| ArgoCD HTTPS | https://10.0.1.200:8082 | ✅ HTTP 200 | 正常 (iptables転送、自己署名証明書) |
| ArgoCD HTTP | http://10.0.1.200:8000 | ✅ HTTP 307 | HTTPS リダイレクト (iptables転送) |

## ポート転送の仕組み

外部ポートからKubernetesのNodePortへiptables NATルールでリダイレクトしています：

| 外部ポート | NodePort | サービス |
|----------|----------|---------|
| 5006 | 31899 | Frontend |
| 8083 | 31383 | Backend |
| 8000 | 30460 | ArgoCD HTTP |
| 8082 | 30010 | ArgoCD HTTPS |

### iptablesルール
```bash
# PREROUTING: 外部からのアクセス
iptables -t nat -A PREROUTING -p tcp --dport 5006 -j REDIRECT --to-port 31899
iptables -t nat -A PREROUTING -p tcp --dport 8083 -j REDIRECT --to-port 31383
iptables -t nat -A PREROUTING -p tcp --dport 8000 -j REDIRECT --to-port 30460
iptables -t nat -A PREROUTING -p tcp --dport 8082 -j REDIRECT --to-port 30010

# OUTPUT: ローカルからのアクセス
iptables -t nat -A OUTPUT -o lo -p tcp --dport 5006 -j REDIRECT --to-port 31899
iptables -t nat -A OUTPUT -o lo -p tcp --dport 8083 -j REDIRECT --to-port 31383
iptables -t nat -A OUTPUT -o lo -p tcp --dport 8000 -j REDIRECT --to-port 30460
iptables -t nat -A OUTPUT -o lo -p tcp --dport 8082 -j REDIRECT --to-port 30010
```

### 永続化
- スクリプト: `/usr/local/bin/setup-port-forwarding.sh`
- Systemdサービス: `k3s-port-forwarding.service` (有効化済み)
- 再起動後も自動適用

## 未使用ポート（利用可能）

今後新しいサービスを追加する場合は、以下のポートが利用可能です：

```
3000
8501
5001
5002
5003
5004
5005
```

## Kubernetesサービス設定

### Frontend Service
```yaml
spec:
  type: LoadBalancer
  externalIPs: [10.0.1.200]
  ports:
  - port: 5006
    targetPort: 80
```

### Backend Service
```yaml
spec:
  type: LoadBalancer
  externalIPs: [10.0.1.200]
  ports:
  - port: 8083
    targetPort: 8080
```

### ArgoCD Service
```yaml
spec:
  type: LoadBalancer
  externalIPs: [10.0.1.200]
  ports:
  - name: http
    port: 8000
    targetPort: 8080
  - name: https
    port: 8082
    targetPort: 8080
```

---
Updated: 2026-02-06
