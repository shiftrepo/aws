# デプロイメント状態サマリー

## 概要

K3s + ArgoCD GitOpsによる組織管理システムの完全自動デプロイメントが完了し、正常稼働中です。

**デプロイ日**: 2026-02-06
**バージョン**: v1.0.0 (Stable Release)
**デプロイ方法**: Ansible完全自動化

## システム構成

### インフラストラクチャ

| コンポーネント | バージョン | ステータス | レプリカ数 |
|------------|----------|----------|----------|
| K3s Cluster | v1.34.3 | Running | 1 node |
| ArgoCD | v2.10.0 | Running | 7 pods |
| PostgreSQL | 16-alpine | Running | 1/1 |
| Redis | 7-alpine | Running | 1/1 |

### アプリケーション

| コンポーネント | イメージ | ステータス | レプリカ数 |
|------------|---------|----------|----------|
| Backend | localhost/orgmgmt-backend:latest | Running | 2/2 |
| Frontend | localhost/orgmgmt-frontend:latest | Running | 2/2 |

## サービスアクセス

### 外部アクセスURL

| サービス | URL | 認証 | 備考 |
|---------|-----|------|------|
| Frontend | http://10.0.1.200:5006 | 不要 | React Web UI |
| Backend API | http://10.0.1.200:8083 | 不要 | REST API |
| ArgoCD UI (HTTPS) | https://10.0.1.200:8082 | 必要 | GitOps管理 (推奨) |
| ArgoCD UI (HTTP) | http://10.0.1.200:8000 | 必要 | HTTPSへリダイレクト |

### 認証情報

**ArgoCD**:
- Username: `admin`
- Password: `Hp6-IAZKocd7yw8n`
- Credentials File: `/root/argocd-credentials.txt`

**PostgreSQL** (内部のみ):
- Host: `postgres` (ClusterIP)
- Port: `5432`
- Database: `orgmgmt`
- Username: `orgmgmt_user`
- Password: `SecurePassword123!`

**Redis** (内部のみ):
- Host: `redis` (ClusterIP)
- Port: `6379`
- Password: なし

## GitOps運用状態

### ArgoCD Application

**名前**: `orgmgmt-app`
**リポジトリ**: https://github.com/shiftrepo/aws.git
**パス**: `container/claudecode/ArgoCD/k8s-manifests`
**ブランチ**: `main`

**同期ステータス**: ✅ Synced
**ヘルスステータス**: ✅ Healthy
**最終同期**: 2026-02-06T04:44:45Z

### 管理リソース (12個)

| リソースタイプ | 名前 | ステータス | ヘルス |
|------------|------|----------|-------|
| Deployment | orgmgmt-backend | Synced | Healthy |
| Deployment | orgmgmt-frontend | Synced | Healthy |
| Deployment | postgres | Synced | Healthy |
| Deployment | redis | Synced | Healthy |
| Service | orgmgmt-backend | Synced | Healthy |
| Service | orgmgmt-frontend | Synced | Healthy |
| Service | postgres | Synced | Healthy |
| Service | redis | Synced | Healthy |
| ConfigMap | postgres-config | Synced | - |
| PVC | postgres-pvc | Synced | Healthy |
| Ingress | orgmgmt-frontend | Synced | Healthy |
| NetworkPolicy | orgmgmt-frontend-allow-all | Synced | - |

### 自動同期設定

- **Automated Sync**: ✅ 有効 (3分ごとにポーリング)
- **Self Heal**: ✅ 有効 (手動変更を自動修復)
- **Prune**: ✅ 有効 (削除されたリソースを自動削除)

## ポート転送構成

外部ポートからKubernetes NodePortへの転送は**socat**で実現しています。

### socat systemdサービス

| サービス名 | 外部ポート | NodePort | ステータス |
|----------|----------|----------|----------|
| socat-frontend | 5006 | 31899 | ✅ Running |
| socat-backend | 8083 | 31383 | ✅ Running |
| socat-argocd-http | 8000 | 30460 | ✅ Running |
| socat-argocd-https | 8082 | 30010 | ✅ Running |

### socat設定詳細

```bash
# 例: Frontend (5006 -> 31899)
ExecStart=/usr/bin/socat TCP-LISTEN:5006,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:31899
```

**特徴**:
- `bind=0.0.0.0`: すべてのネットワークインターフェースでリッスン
- `fork`: 複数の同時接続を処理
- `reuseaddr`: ポートの再利用を許可
- 再起動時に自動起動 (systemd enabled)

## 動作確認

### Backend Health Check

```bash
curl http://10.0.1.200:8083/actuator/health
# Response: {"status":"UP","groups":["liveness","readiness"]}
```

### Backend API - Organizations

```bash
curl http://10.0.1.200:8083/api/organizations
# Response: JSON array with sample organizations
```

### Frontend

```bash
curl http://10.0.1.200:5006/
# Response: HTML (Organization Management System)
```

### ArgoCD Application Status

```bash
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd
# NAME           SYNC STATUS   HEALTH STATUS
# orgmgmt-app    Synced        Healthy
```

## デプロイフロー

### 1. 完全自動デプロイ (Ansible)

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

**実行内容**:
1. K3s + ArgoCD インストール
2. ビルドツール (Maven, Node.js) セットアップ
3. Backend/Frontend ビルド
4. コンテナイメージ作成・インポート
5. Kubernetesへのデプロイ
6. ArgoCD Application作成
7. ポート転送設定 (socat)

### 2. GitOpsによる継続的デプロイ

```
開発者がk8s-manifestsを変更
         ↓
GitHub mainブランチにpush
         ↓
ArgoCD自動検出 (3分以内)
         ↓
Kubernetes自動適用
         ↓
Pod自動更新
```

## 技術スタック

### インフラストラクチャ
- K3s v1.34.3
- ArgoCD v2.10.0
- PostgreSQL 16 Alpine
- Redis 7 Alpine
- socat (Port Forwarding)

### Backend
- Java 21
- Spring Boot 3.2.1
- Spring Data JPA
- Flyway Migration
- Lombok

### Frontend
- React 18
- Vite 5
- React Router DOM
- Axios
- Nginx Alpine

### デプロイ・運用
- Ansible 2.14
- Podman (Container Build)
- systemd (Service Management)
- Git (Version Control)

## Kubernetesリソース状態

### Pods (default namespace)

```
NAME                                READY   STATUS    RESTARTS   AGE
orgmgmt-backend-6f588c9748-46gtt    1/1     Running   0          55m
orgmgmt-backend-6f588c9748-qmqhz    1/1     Running   0          55m
orgmgmt-frontend-66799dfdc6-7whsf   1/1     Running   0          55m
orgmgmt-frontend-66799dfdc6-hssxm   1/1     Running   0          55m
postgres-57db9d88bc-4l27d           1/1     Running   0          56m
redis-5f8cc46b8b-6l6wd              1/1     Running   0          56m
```

### Services (default namespace)

```
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
orgmgmt-backend    LoadBalancer   10.43.107.241   10.0.1.200    8083:31383/TCP
orgmgmt-frontend   LoadBalancer   10.43.22.133    10.0.1.200    5006:31899/TCP
postgres           ClusterIP      10.43.249.228   <none>        5432/TCP
redis              ClusterIP      10.43.124.125   <none>        6379/TCP
```

### ArgoCD Pods (argocd namespace)

```
NAME                                                READY   STATUS
argocd-application-controller-0                     1/1     Running
argocd-applicationset-controller-57d7cf846f-xxxxx   1/1     Running
argocd-dex-server-57446447b4-xxxxx                  1/1     Running
argocd-notifications-controller-6dff6fd785-xxxxx    1/1     Running
argocd-redis-5f998f8d84-xxxxx                       1/1     Running
argocd-repo-server-6f58bf5567-xxxxx                 1/1     Running
argocd-server-6c6ddbf4fb-xxxxx                      1/1     Running
```

## ファイル構成

### Kubernetesマニフェスト (k8s-manifests/)
- `backend-deployment.yaml` - Backend Deployment (2 replicas)
- `backend-service.yaml` - Backend LoadBalancer Service
- `frontend-deployment.yaml` - Frontend Deployment (2 replicas)
- `frontend-service.yaml` - Frontend LoadBalancer Service
- `postgres-deployment.yaml` - PostgreSQL Deployment + ConfigMap + PVC
- `redis-deployment.yaml` - Redis Deployment + Service

### Ansibleプレイブック (ansible/playbooks/)
- `deploy_k8s_complete.yml` - 完全自動デプロイ (推奨)
- `install_k3s_and_argocd.yml` - K3s + ArgoCD インストール
- `install_build_tools.yml` - ビルドツールセットアップ

### アプリケーション (app/)
- `backend/` - Spring Boot 3.2.1 + Java 21
- `frontend/` - React 18 + Vite 5

### ArgoCD設定
- `argocd-application.yaml` - ArgoCD Application定義

## 運用コマンド

### デプロイ状態確認

```bash
# ArgoCD Application確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd

# 全Pod確認
sudo /usr/local/bin/k3s kubectl get pods

# サービス確認
sudo /usr/local/bin/k3s kubectl get svc

# ポート転送確認
sudo systemctl status socat-frontend socat-backend socat-argocd-http socat-argocd-https

# ポートリッスン確認
sudo ss -tlnp | grep -E "5006|8083|8000|8082"
```

### ログ確認

```bash
# Backend
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend

# Frontend
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-frontend

# PostgreSQL
sudo /usr/local/bin/k3s kubectl logs -f deployment/postgres

# Redis
sudo /usr/local/bin/k3s kubectl logs -f deployment/redis
```

### ArgoCD操作

```bash
# CLIログイン
argocd login 10.0.1.200:8082 --username admin --password 'Hp6-IAZKocd7yw8n' --insecure

# アプリケーション一覧
argocd app list

# アプリケーション詳細
argocd app get orgmgmt-app

# 手動同期
argocd app sync orgmgmt-app

# 履歴確認
argocd app history orgmgmt-app
```

## トラブルシューティング

### 外部アクセスできない

```bash
# socatサービス確認
sudo systemctl status socat-frontend

# ポート確認
sudo ss -tlnp | grep 5006

# socatプロセス確認
sudo ps aux | grep socat
```

### ArgoCD Application OutOfSync

```bash
# 手動同期
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge -p '{"operation": {"sync": {"prune": true}}}'
```

### Pod起動しない

```bash
# イベント確認
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp'

# Pod詳細確認
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>
```

## 環境削除

```bash
# K3s完全削除
sudo /usr/local/bin/k3s-uninstall.sh

# socatサービス停止・削除
sudo systemctl stop socat-frontend socat-backend socat-argocd-http socat-argocd-https
sudo systemctl disable socat-frontend socat-backend socat-argocd-http socat-argocd-https
sudo rm -f /etc/systemd/system/socat-*.service
sudo systemctl daemon-reload
```

## まとめ

✅ **Kubernetes環境構築完了**
- K3s + ArgoCD GitOpsプラットフォーム稼働中
- すべてのサービスが正常稼働

✅ **GitOpsワークフロー確立**
- GitHub がシングルソースオブトゥルース
- 自動同期・自己修復・自動削除が有効
- マニフェスト変更を push するだけで自動デプロイ

✅ **外部アクセス完全対応**
- socat systemd サービスで安定したポート転送
- すべてのサービスが外部IPからアクセス可能

✅ **完全自動化**
- Ansibleプレイブック1つで0から環境構築
- 再現性の高いインフラストラクチャ

---
**Generated**: 2026-02-06
**Version**: v1.0.0
**Repository**: https://github.com/shiftrepo/aws
**Path**: container/claudecode/ArgoCD
