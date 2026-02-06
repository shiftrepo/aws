# 認証情報・アクセスガイド

## アクセスURL

| サービス | URL | 認証 | 説明 |
|---------|-----|------|------|
| **Frontend** | http://10.0.1.200:5006 | 不要 | React Web UI |
| **Backend API** | http://10.0.1.200:8083 | 不要 | REST API |
| **ArgoCD (HTTPS)** | https://10.0.1.200:8082 | 必要 | GitOps管理UI (推奨) |
| **ArgoCD (HTTP)** | http://10.0.1.200:8000 | 必要 | HTTPSへリダイレクト |
| **Traefik** | http://10.0.1.200:80 / https://10.0.1.200:443 | 不要 | Ingress Controller |
| **Traefik Dashboard** | kubectl port-forward | 不要 | ポート転送でアクセス |

## ArgoCD認証情報

### 現在のパスワード

```
Username: admin
Password: IQ1qooxuf1pyleRy
```

### パスワード取得方法（初期化後など）

```bash
# 方法1: kubectl経由で取得
sudo /usr/local/bin/k3s kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d && echo

# 方法2: 保存済みファイルから確認
sudo cat /root/argocd-credentials.txt
```

### ArgoCD CLI ログイン

```bash
# HTTPS経由（推奨）
argocd login 10.0.1.200:8082 \
  --username admin \
  --password 'IQ1qooxuf1pyleRy' \
  --insecure

# HTTP経由
argocd login 10.0.1.200:8000 \
  --username admin \
  --password 'IQ1qooxuf1pyleRy' \
  --insecure \
  --plaintext
```

### ArgoCD UI アクセス

1. ブラウザで https://10.0.1.200:8082 を開く
2. 証明書警告を承認（自己署名証明書使用のため）
3. Username: `admin`
4. Password: `IQ1qooxuf1pyleRy`

## Kubernetes管理サービス

K3sには以下の管理サービスが含まれています：

### K3s システムサービス

#### サービス管理

```bash
# K3s サービスステータス確認
sudo systemctl status k3s

# K3s サービス起動
sudo systemctl start k3s

# K3s サービス停止
sudo systemctl stop k3s

# K3s サービス再起動
sudo systemctl restart k3s

# K3s ログ確認
sudo journalctl -u k3s -f

# K3s バージョン確認
sudo /usr/local/bin/k3s --version
```

**現在のバージョン**: K3s v1.34.3+k3s1 (Kubernetes v1.34.3)

#### K3s 設定ファイル

```bash
# K3s サービス設定
/etc/systemd/system/k3s.service

# kubeconfig
/etc/rancher/k3s/k3s.yaml

# データディレクトリ
/var/lib/rancher/k3s/

# コンテナイメージ
/var/lib/rancher/k3s/agent/containerd/
```

### CoreDNS - DNS解決サービス

Kubernetes内部のDNS解決を提供します。

```bash
# CoreDNS Pod確認
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l k8s-app=kube-dns

# CoreDNS ログ確認
sudo /usr/local/bin/k3s kubectl logs -n kube-system -l k8s-app=kube-dns

# DNS解決テスト
sudo /usr/local/bin/k3s kubectl run -it --rm debug \
  --image=busybox --restart=Never -- nslookup kubernetes.default
```

**Service**: `kube-dns` (ClusterIP: 10.43.0.10)
**Ports**: 53/UDP, 53/TCP, 9153/TCP

### Traefik - Ingress Controller

K3sに組み込まれたIngress Controllerです。

#### Traefik サービス

```bash
# Traefik Pod確認
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik

# Traefik ログ確認
sudo /usr/local/bin/k3s kubectl logs -n kube-system -l app.kubernetes.io/name=traefik -f

# Traefik Service確認
sudo /usr/local/bin/k3s kubectl get svc traefik -n kube-system
```

**Service**: `traefik` (LoadBalancer)
**External IP**: 10.0.1.200
**Ports**:
- HTTP: 80 (NodePort: 31652)
- HTTPS: 443 (NodePort: 30914)

#### Traefik Dashboard アクセス

Traefik Dashboardは有効ですが、デフォルトでは外部公開されていません。

**ポート転送でアクセス**:

```bash
# ポート転送開始
sudo /usr/local/bin/k3s kubectl port-forward \
  -n kube-system \
  $(sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik -o name) \
  9000:9000

# ブラウザで開く
# http://localhost:9000/dashboard/
```

**IngressRouteで公開する場合**（オプション）:

```bash
sudo /usr/local/bin/k3s kubectl apply -f - <<EOF
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-dashboard
  namespace: kube-system
spec:
  entryPoints:
    - web
  routes:
    - match: Host(\`traefik.local\`)
      kind: Rule
      services:
        - name: api@internal
          kind: TraefikService
EOF

# /etc/hostsに追加
# 10.0.1.200 traefik.local

# アクセス: http://traefik.local/dashboard/
```

### Metrics Server - リソースモニタリング

CPU/メモリ使用状況を収集します。

```bash
# Metrics Server Pod確認
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l k8s-app=metrics-server

# ノードのリソース使用状況
sudo /usr/local/bin/k3s kubectl top nodes

# Podのリソース使用状況
sudo /usr/local/bin/k3s kubectl top pods -A

# 特定namespaceのPod
sudo /usr/local/bin/k3s kubectl top pods -n default

# リソース使用量でソート
sudo /usr/local/bin/k3s kubectl top pods -A --sort-by=memory
sudo /usr/local/bin/k3s kubectl top pods -A --sort-by=cpu
```

**Service**: `metrics-server` (ClusterIP: 10.43.243.176)
**Port**: 443/TCP

### Local Path Provisioner - ストレージ管理

動的なPersistentVolume作成を提供します。

```bash
# Provisioner Pod確認
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l app=local-path-provisioner

# StorageClass確認
sudo /usr/local/bin/k3s kubectl get storageclass

# PersistentVolume一覧
sudo /usr/local/bin/k3s kubectl get pv

# PersistentVolumeClaim一覧
sudo /usr/local/bin/k3s kubectl get pvc -A
```

**StorageClass**: `local-path` (デフォルト)
**ボリュームパス**: `/var/lib/rancher/k3s/storage/`

### Kubernetes Dashboard（オプション）

Kubernetes Dashboardをインストールする場合：

#### インストール

```bash
# Kubernetes Dashboard インストール
sudo /usr/local/bin/k3s kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# ServiceAccount作成
sudo /usr/local/bin/k3s kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOF

# トークン取得
sudo /usr/local/bin/k3s kubectl create token admin-user -n kubernetes-dashboard
```

#### アクセス

```bash
# ポート転送
sudo /usr/local/bin/k3s kubectl port-forward -n kubernetes-dashboard \
  svc/kubernetes-dashboard 8443:443

# ブラウザで開く
# https://localhost:8443/

# トークンでログイン
```

**または、NodePortで公開**:

```bash
sudo /usr/local/bin/k3s kubectl patch svc kubernetes-dashboard -n kubernetes-dashboard \
  -p '{"spec": {"type": "NodePort", "ports": [{"port": 443, "targetPort": 8443, "nodePort": 30443}]}}'

# アクセス: https://10.0.1.200:30443/
```

## Kubernetes認証情報

### kubeconfig ファイル場所

```bash
# システム全体のkubeconfig
/etc/rancher/k3s/k3s.yaml

# ユーザー用コピー（存在する場合）
~/.kube/config
```

### kubectl コマンド

```bash
# K3s組み込みkubectl
sudo /usr/local/bin/k3s kubectl get nodes
sudo /usr/local/bin/k3s kubectl get pods -A

# 環境変数設定後は sudo なしで実行可能
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl get nodes
```

### Kubernetes APIサーバー

```
URL: https://127.0.0.1:6443
証明書: /var/lib/rancher/k3s/server/tls/server-ca.crt
```

### Kubernetes 認証トークン取得方法

#### 方法1: デフォルトServiceAccountトークン取得

```bash
# default namespaceのServiceAccountトークン
sudo /usr/local/bin/k3s kubectl create token default -n default

# argocd namespaceのServiceAccountトークン
sudo /usr/local/bin/k3s kubectl create token argocd-server -n argocd
```

#### 方法2: 長期有効なトークン作成

```bash
# ServiceAccountとSecretを作成
sudo /usr/local/bin/k3s kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kube-system
---
apiVersion: v1
kind: Secret
metadata:
  name: admin-user-token
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: admin-user
type: kubernetes.io/service-account-token
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kube-system
EOF

# トークン取得
sudo /usr/local/bin/k3s kubectl get secret admin-user-token \
  -n kube-system \
  -o jsonpath='{.data.token}' | base64 -d && echo
```

#### 方法3: kubeconfigから抽出

```bash
# kubeconfigに含まれる証明書データ
sudo cat /etc/rancher/k3s/k3s.yaml

# client-certificate-data (Base64エンコード済み)
sudo cat /etc/rancher/k3s/k3s.yaml | grep "client-certificate-data:" | awk '{print $2}'

# client-key-data (Base64エンコード済み)
sudo cat /etc/rancher/k3s/k3s.yaml | grep "client-key-data:" | awk '{print $2}'
```

### Kubernetes CA証明書

```bash
# CA証明書データ（Base64エンコード済み）
sudo cat /etc/rancher/k3s/k3s.yaml | grep "certificate-authority-data:" | awk '{print $2}

# CA証明書ファイル
/var/lib/rancher/k3s/server/tls/server-ca.crt
```

### Kubernetes APIアクセス例

```bash
# トークン取得
TOKEN=$(sudo /usr/local/bin/k3s kubectl create token default -n default)

# API呼び出し
curl -k https://127.0.0.1:6443/api/v1/namespaces/default/pods \
  -H "Authorization: Bearer $TOKEN"
```

## PostgreSQL認証情報

### 接続情報

| 項目 | 値 |
|------|-----|
| **Host** | postgres (Kubernetes内部) |
| **Port** | 5432 |
| **Database** | orgmgmt |
| **Username** | orgmgmt_user |
| **Password** | SecurePassword123! |

### Pod内から接続

```bash
# PostgreSQL Podに接続
POD_NAME=$(sudo /usr/local/bin/k3s kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')
sudo /usr/local/bin/k3s kubectl exec -it $POD_NAME -- psql -U orgmgmt_user -d orgmgmt

# SQL実行例
sudo /usr/local/bin/k3s kubectl exec -it $POD_NAME -- \
  psql -U orgmgmt_user -d orgmgmt -c "SELECT * FROM organizations;"
```

### ポート転送でローカルアクセス

```bash
# ポート転送開始
sudo /usr/local/bin/k3s kubectl port-forward svc/postgres 5432:5432 &

# ローカルから接続
psql -h 127.0.0.1 -p 5432 -U orgmgmt_user -d orgmgmt
# Password: SecurePassword123!
```

### 環境変数（Backend Podで設定済み）

```yaml
SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/orgmgmt
SPRING_DATASOURCE_USERNAME: orgmgmt_user
SPRING_DATASOURCE_PASSWORD: SecurePassword123!
```

## Redis認証情報

### 接続情報

| 項目 | 値 |
|------|-----|
| **Host** | redis (Kubernetes内部) |
| **Port** | 6379 |
| **Password** | なし（認証不要） |

### Pod内から接続

```bash
# Redis Podに接続
POD_NAME=$(sudo /usr/local/bin/k3s kubectl get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
sudo /usr/local/bin/k3s kubectl exec -it $POD_NAME -- redis-cli

# コマンド例
redis-cli> PING
redis-cli> KEYS *
redis-cli> INFO
```

### ポート転送でローカルアクセス

```bash
# ポート転送開始
sudo /usr/local/bin/k3s kubectl port-forward svc/redis 6379:6379 &

# ローカルから接続
redis-cli -h 127.0.0.1 -p 6379
```

### 環境変数（Backend Podで設定済み）

```yaml
REDIS_HOST: redis
REDIS_PORT: 6379
```

## Backend API認証情報

### REST API

現在の実装では**認証なし**でアクセス可能です。

```bash
# Health Check
curl http://10.0.1.200:8083/actuator/health

# Organizations API
curl http://10.0.1.200:8083/api/organizations

# Departments API
curl http://10.0.1.200:8083/api/departments

# Users API
curl http://10.0.1.200:8083/api/users
```

### 将来的な認証実装（予定）

- Spring Security + JWT認証
- OAuth2 / OpenID Connect
- API Key認証

## セキュリティ注意事項

### 本番環境での推奨事項

1. **ArgoCD パスワード変更**
   ```bash
   argocd account update-password \
     --account admin \
     --current-password 'IQ1qooxuf1pyleRy' \
     --new-password '<強力なパスワード>'
   ```

2. **PostgreSQL パスワード変更**
   - Secretを更新してPodを再起動

3. **Redisに認証追加**
   - redis.conf で requirepass 設定

4. **Kubernetes RBAC設定**
   - 最小権限の原則に基づいたRole/RoleBinding設定

5. **ネットワークポリシー設定**
   - Pod間通信の制限

6. **TLS証明書の適切な管理**
   - Let's Encrypt等の正式な証明書使用

## トラブルシューティング

### ArgoCD パスワードを忘れた場合

```bash
# パスワードリセット（初期パスワードに戻す）
sudo /usr/local/bin/k3s kubectl delete secret argocd-initial-admin-secret -n argocd
sudo /usr/local/bin/k3s kubectl rollout restart deployment argocd-server -n argocd

# 新しいパスワード取得（30秒ほど待つ）
sleep 30
sudo /usr/local/bin/k3s kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d && echo
```

### Kubernetes APIにアクセスできない場合

```bash
# kubeconfigのパーミッション確認
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# K3s サービス確認
sudo systemctl status k3s

# API サーバーログ確認
sudo journalctl -u k3s -f
```

### PostgreSQL接続エラー

```bash
# Pod状態確認
sudo /usr/local/bin/k3s kubectl get pod -l app=postgres

# ログ確認
sudo /usr/local/bin/k3s kubectl logs -l app=postgres

# Service確認
sudo /usr/local/bin/k3s kubectl get svc postgres
```

## クイックリファレンス

### 全サービス状態確認

```bash
# すべてのPod確認
sudo /usr/local/bin/k3s kubectl get pods -A

# すべてのService確認
sudo /usr/local/bin/k3s kubectl get svc -A

# ArgoCD Application確認
sudo /usr/local/bin/k3s kubectl get application -n argocd

# socat ポート転送確認
sudo systemctl status socat-frontend socat-backend socat-argocd-http socat-argocd-https

# リッスンポート確認
sudo ss -tlnp | grep -E "5006|8083|8000|8082"
```

### ログ確認

```bash
# Backend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend

# Frontend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-frontend

# PostgreSQL ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/postgres

# Redis ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/redis

# ArgoCD Server ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/argocd-server -n argocd
```

### Kubernetes管理サービス確認

```bash
# K3s サービス状態
sudo systemctl status k3s

# K3s ログ
sudo journalctl -u k3s -f

# CoreDNS 状態
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l k8s-app=kube-dns

# Traefik 状態
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik

# Metrics Server 状態
sudo /usr/local/bin/k3s kubectl get pods -n kube-system -l k8s-app=metrics-server

# リソース使用状況
sudo /usr/local/bin/k3s kubectl top nodes
sudo /usr/local/bin/k3s kubectl top pods -A

# StorageClass確認
sudo /usr/local/bin/k3s kubectl get storageclass

# PersistentVolume確認
sudo /usr/local/bin/k3s kubectl get pv
sudo /usr/local/bin/k3s kubectl get pvc -A
```

---

**作成日**: 2026-02-06
**バージョン**: v1.0.0
**最終更新**: 2026-02-06 (Kubernetes管理サービス情報追加)
