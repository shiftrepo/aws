# ポート割り当て状況

## 利用可能な外部ポート一覧

| ポート | ステータス | サービス | 用途 |
|-------|----------|---------|------|
| 3000 | ⚪ 未使用 | - | 利用可能 |
| 8501 | ⚪ 未使用 | - | 利用可能 |
| 8000 | ✅ 使用中 | ArgoCD | HTTP (HTTPSリダイレクト) |
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
  - 用途: React Web UI
  - 認証: 不要

- **Backend API**: http://10.0.1.200:8083
  - 用途: REST API
  - 認証: 不要
  - Health Check: http://10.0.1.200:8083/actuator/health
  - Organizations API: http://10.0.1.200:8083/api/organizations
  - Departments API: http://10.0.1.200:8083/api/departments
  - Users API: http://10.0.1.200:8083/api/users

### GitOps管理
- **ArgoCD HTTPS**: https://10.0.1.200:8082 (推奨)
  - 用途: GitOps管理UI
  - 認証: 必要

- **ArgoCD HTTP**: http://10.0.1.200:8000
  - 用途: HTTPSへリダイレクト
  - 認証: 必要

- **認証情報**:
  - Username: `admin`
  - Password: `/root/argocd-credentials.txt` 参照

## 外部アクセス実装方法

### socat systemdサービス

外部ポートからKubernetes NodePortへの転送は**socat**で実現しています。

| サービス名 | 外部ポート | NodePort | ステータス | 起動モード |
|----------|----------|----------|----------|----------|
| socat-frontend.service | 5006 | 31899 | ✅ Running | enabled |
| socat-backend.service | 8083 | 31383 | ✅ Running | enabled |
| socat-argocd-http.service | 8000 | 30460 | ✅ Running | enabled |
| socat-argocd-https.service | 8082 | 30010 | ✅ Running | enabled |

### socat設定詳細

#### Frontend (5006 → 31899)
```ini
[Unit]
Description=Socat Port Forward - Frontend (5006 -> 31899)
After=network.target k3s.service
Requires=k3s.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:31899
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Backend (8083 → 31383)
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8083,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:31383
```

#### ArgoCD HTTP (8000 → 30460)
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8000,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:30460
```

#### ArgoCD HTTPS (8082 → 30010)
```ini
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:8082,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:30010
```

### socatの特徴

| オプション | 説明 |
|----------|------|
| `TCP-LISTEN:<port>` | 指定ポートでTCP接続を待ち受け |
| `bind=0.0.0.0` | すべてのネットワークインターフェースでリッスン（外部アクセス可能） |
| `fork` | 複数の同時接続を処理 |
| `reuseaddr` | ポートの再利用を許可 |
| `TCP:127.0.0.1:<nodeport>` | ローカルのNodePortへ転送 |

**重要**: `bind=0.0.0.0` により、外部IPからのアクセスが可能になります。

## ポート転送の仕組み

```
外部クライアント
    ↓ (例: http://10.0.1.200:5006)
外部IP:5006 (すべてのインターフェースでリッスン)
    ↓ socat転送
127.0.0.1:31899 (NodePort)
    ↓ Kubernetes Service
Pod内部ポート:80 (orgmgmt-frontend)
```

## 動作確認結果

| サービス | URL | ステータス | 備考 |
|---------|-----|-----------|------|
| Frontend | http://10.0.1.200:5006 | ✅ HTTP 200 | 正常 (socat転送) |
| Backend | http://10.0.1.200:8083 | ✅ HTTP 200 | 正常 (socat転送) |
| ArgoCD HTTPS | https://10.0.1.200:8082 | ✅ HTTP 200 | 正常 (socat転送、自己署名証明書) |
| ArgoCD HTTP | http://10.0.1.200:8000 | ✅ HTTP 307 | HTTPSリダイレクト (socat転送) |

### 確認コマンド

```bash
# socatサービスステータス確認
sudo systemctl status socat-frontend socat-backend socat-argocd-http socat-argocd-https

# ポートリッスン確認 (0.0.0.0で待ち受けていることを確認)
sudo ss -tlnp | grep -E "5006|8083|8000|8082"

# 出力例:
# LISTEN 0   5   0.0.0.0:5006   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:8083   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:8000   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))
# LISTEN 0   5   0.0.0.0:8082   0.0.0.0:*   users:(("socat",pid=xxx,fd=5))

# socatプロセス確認
sudo ps aux | grep socat

# アクセステスト
curl http://10.0.1.200:5006/
curl http://10.0.1.200:8083/actuator/health
curl -k https://10.0.1.200:8082/
```

## Kubernetesサービス設定

### Frontend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-frontend
  namespace: default
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 5006        # External port (socat source)
    targetPort: 80    # Container port (nginx)
    nodePort: 31899   # NodePort (socat destination)
  selector:
    app: orgmgmt-frontend
```

### Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orgmgmt-backend
  namespace: default
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 8083        # External port (socat source)
    targetPort: 8080  # Container port (Spring Boot)
    nodePort: 31383   # NodePort (socat destination)
  selector:
    app: orgmgmt-backend
```

### ArgoCD Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: argocd-server
  namespace: argocd
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 8000        # External port (socat source)
    targetPort: 8080  # Container port
    nodePort: 30460   # NodePort (socat destination)
  - name: https
    port: 8082        # External port (socat source)
    targetPort: 8080  # Container port
    nodePort: 30010   # NodePort (socat destination)
```

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

## 新しいサービスの追加手順

### 1. Kubernetes Serviceを作成

未使用ポートから選択して、LoadBalancer Serviceを作成します。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: new-service
  namespace: default
spec:
  type: LoadBalancer
  externalIPs:
  - 10.0.1.200
  ports:
  - name: http
    port: 5001        # 未使用ポートを選択
    targetPort: 8080  # Podの内部ポート
  selector:
    app: new-service
```

### 2. NodePortを確認

```bash
sudo /usr/local/bin/k3s kubectl get svc new-service -o jsonpath='{.spec.ports[0].nodePort}'
# 例: 30123
```

### 3. socatサービスを作成

```bash
sudo tee /etc/systemd/system/socat-new-service.service > /dev/null <<EOF
[Unit]
Description=Socat Port Forward - New Service (5001 -> 30123)
After=network.target k3s.service
Requires=k3s.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/socat TCP-LISTEN:5001,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:30123
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 4. サービスを有効化・起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable socat-new-service
sudo systemctl start socat-new-service
sudo systemctl status socat-new-service
```

### 5. 動作確認

```bash
# ポート確認
sudo ss -tlnp | grep 5001

# アクセステスト
curl http://10.0.1.200:5001/
```

## トラブルシューティング

### 外部からアクセスできない

**原因**:
1. socatサービスが起動していない
2. ポートが0.0.0.0でリッスンしていない
3. AWSセキュリティグループで閉じている
4. ファイアウォールが有効

**解決策**:

```bash
# サービス確認
sudo systemctl status socat-frontend

# ログ確認
sudo journalctl -u socat-frontend -n 50

# ポート確認 (0.0.0.0を確認)
sudo ss -tlnp | grep 5006

# socatプロセス確認
sudo ps aux | grep socat

# AWSセキュリティグループ確認 (手動確認)

# ファイアウォール確認
sudo systemctl status firewalld
# 無効であることを確認
```

### socatサービスが起動しない

**原因**: K3sが起動していない、またはNodePortが利用できない

**解決策**:

```bash
# K3s確認
sudo systemctl status k3s

# NodePort確認
sudo /usr/local/bin/k3s kubectl get svc orgmgmt-frontend

# socatサービス再起動
sudo systemctl restart socat-frontend
```

### ポート競合

**原因**: 同じポートを別のプロセスが使用

**解決策**:

```bash
# ポート使用確認
sudo lsof -i :5006

# 競合プロセス停止
sudo kill <pid>

# socatサービス再起動
sudo systemctl restart socat-frontend
```

## 永続化・再起動対応

すべてのsocatサービスは**systemd enabled**状態のため、サーバー再起動後も自動的に起動します。

```bash
# サービス自動起動確認
sudo systemctl is-enabled socat-frontend socat-backend socat-argocd-http socat-argocd-https

# 出力: enabled × 4
```

## まとめ

| 項目 | 詳細 |
|------|------|
| **ポート転送方式** | socat (systemd サービス) |
| **外部アクセス** | ✅ 完全対応 (bind=0.0.0.0) |
| **再起動後の動作** | ✅ 自動起動 (systemd enabled) |
| **使用中ポート** | 4個 (5006, 8083, 8000, 8082) |
| **未使用ポート** | 7個 (3000, 8501, 5001-5005) |
| **管理方法** | systemctl コマンド |

**利点**:
- 外部IPから直接アクセス可能
- 複数同時接続対応 (fork)
- 自動再起動・永続化 (systemd)
- 設定がシンプル

---
**Updated**: 2026-02-06
**Version**: v1.0.0
