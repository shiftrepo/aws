# Organization Management System - ArgoCD GitOps Deployment

Kubernetes（K3s）+ ArgoCD GitOpsによる組織管理システムの完全自動デプロイメント

## 概要

このプロジェクトは、以下のコンポーネントで構成されています：

- **K3s Kubernetes Cluster**: 軽量Kubernetesディストリビューション
- **ArgoCD**: GitOps継続的デプロイメント
- **Backend**: Spring Boot 3.2.1 + Java 21 REST API
- **Frontend**: React 18 + Vite Web UI
- **PostgreSQL 16**: データベース
- **Redis 7**: セッション管理

## クイックスタート

### 1. 完全自動デプロイ

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

このプレイブックは以下を自動実行します：
1. K3s + ArgoCD インストール
2. ビルドツール（Maven, Node.js）セットアップ
3. Backend/Frontend ビルド
4. コンテナイメージ作成・インポート
5. Kubernetesへのデプロイ
6. ポート転送設定（socat）

### 2. アクセス

デプロイ完了後、以下のURLでアクセスできます：

| サービス | URL | 認証 |
|---------|-----|------|
| Frontend | http://\<外部IP\>:5006 | 不要 |
| Backend API | http://\<外部IP\>:8083 | 不要 |
| ArgoCD UI | https://\<外部IP\>:8082 | 必要 |
| **Kubernetes Dashboard** | **https://\<EC2パブリックDNS\>:3000** | **必要** |

**⚠️ 重要: Kubernetes Dashboardのアクセス方法**

Kubernetes Dashboardは**IPアドレスではアクセスできません**。EC2インスタンスのパブリックDNS名を使用してください。

```bash
# EC2のパブリックDNS名を取得
curl -s http://169.254.169.254/latest/meta-data/public-hostname

# 例: ec2-54-172-30-175.compute-1.amazonaws.com
```

アクセスURL例:
```
https://ec2-54-172-30-175.compute-1.amazonaws.com:3000/
```

**認証情報**: 詳細は [CREDENTIALS.md](CREDENTIALS.md) を参照してください。

- ArgoCD認証情報とパスワード取得方法
- Kubernetes Dashboard トークン（`/root/k8s-dashboard-token.txt`）
- Kubernetes APIトークン取得方法
- PostgreSQL / Redis接続情報
- 各種トラブルシューティング

## アーキテクチャ

```
                         外部アクセス
                              │
                ┌─────────────┼─────────────┐
                │             │             │
            Port 5006     Port 8083     Port 8082
                │             │             │
            (socat)       (socat)       (socat)
                │             │             │
         ┌──────┴─────┬──────┴──────┬──────┴─────┐
         │            │             │            │
    Frontend(x2)  Backend(x2)   ArgoCD      PostgreSQL
         │            │             │            │
         └────────────┴─────────────┴────────────┘
                    Kubernetes (K3s)
                 GitOps by ArgoCD
```

## デプロイメントアーキテクチャ

### GitOps Workflow

```
GitHub Repository (k8s-manifests)
         │
         ├─ ArgoCD自動検出（3分ごと）
         │
         └─→ Kubernetes Cluster
              ├─ Backend Deployment (2 replicas)
              ├─ Frontend Deployment (2 replicas)
              ├─ PostgreSQL Deployment (1 replica)
              └─ Redis Deployment (1 replica)
```

### ポート構成

| 内部 | 外部 | サービス | 説明 |
|------|------|---------|------|
| NodePort 31899 | 5006 | Frontend | React Web UI |
| NodePort 31383 | 8083 | Backend | REST API |
| NodePort 30010 | 8082 | ArgoCD | GitOps管理 (HTTPS) |
| NodePort 30460 | 8000 | ArgoCD | GitOps管理 (HTTP) |

## ディレクトリ構造

```
.
├── ansible/
│   ├── playbooks/
│   │   └── deploy_k8s_complete.yml    # 完全自動デプロイ
│   └── templates/
│       └── port-forward.service.j2     # socat systemdテンプレート
├── k8s-manifests/                      # Kubernetesマニフェスト
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres-deployment.yaml
│   └── redis-deployment.yaml
├── app/
│   ├── backend/                        # Spring Boot アプリケーション
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/
│   └── frontend/                       # React アプリケーション
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── package.json
│       └── src/
├── argocd-application.yaml             # ArgoCD Applicationマニフェスト
└── archive/                            # 過去の経緯・履歴ファイル

```

## 主要コマンド

### デプロイ状態確認

```bash
# ArgoCD Application確認
kubectl get application orgmgmt-app -n argocd

# 全Pod確認
kubectl get pods

# サービス確認
kubectl get svc
```

### ログ確認

```bash
# Backend
kubectl logs -f deployment/orgmgmt-backend

# Frontend
kubectl logs -f deployment/orgmgmt-frontend
```

### ArgoCD操作

```bash
# ArgoCD CLIログイン
argocd login 10.0.1.200:8082 --username admin --password '<password>' --insecure

# アプリケーション同期
argocd app sync orgmgmt-app

# アプリケーション状態確認
argocd app get orgmgmt-app
```

## 開発ワークフロー

### マニフェスト変更

1. マニフェストファイルを編集
```bash
vim k8s-manifests/backend-deployment.yaml
```

2. 変更をコミット・プッシュ
```bash
git add k8s-manifests/backend-deployment.yaml
git commit -m "feat: Update backend configuration"
git push origin main
```

3. ArgoCDが自動的にデプロイ（最大3分）

### イメージ更新

1. アプリケーションをビルド
```bash
cd app/backend
mvn clean package -DskipTests
```

2. イメージをビルド・インポート
```bash
podman build -t orgmgmt-backend:latest .
podman save localhost/orgmgmt-backend:latest -o /tmp/backend.tar
sudo k3s ctr images import /tmp/backend.tar
```

3. Podを再起動
```bash
kubectl rollout restart deployment/orgmgmt-backend
```

## トラブルシューティング

### 外部アクセスできない

```bash
# socat サービス確認
sudo systemctl status socat-frontend
sudo systemctl status socat-backend

# ポートリッスン確認
sudo ss -tlnp | grep -E "5006|8083"
```

### ArgoCD Application OutOfSync

```bash
# 手動同期
kubectl patch application orgmgmt-app -n argocd --type merge -p '{"operation": {"sync": {"prune": true}}}'
```

### Pod起動しない

```bash
# イベント確認
kubectl get events --sort-by='.lastTimestamp'

# Pod詳細確認
kubectl describe pod <pod-name>
```

## 環境削除

```bash
# K3s完全削除
sudo /usr/local/bin/k3s-uninstall.sh
```

## ドキュメント

- **[CREDENTIALS.md](CREDENTIALS.md)**: 🔑 認証情報・アクセスガイド（必読）
  - ArgoCD / Kubernetes / PostgreSQL / Redis 認証情報
  - パスワード・トークン取得方法
  - セキュリティ設定とトラブルシューティング
- **[ARGOCD-DEPLOYMENT-GUIDE.md](ARGOCD-DEPLOYMENT-GUIDE.md)**: ArgoCDの詳細な運用ガイド
- **[DEPLOYMENT-SUMMARY.md](DEPLOYMENT-SUMMARY.md)**: デプロイメント詳細サマリー
- **[EXTERNAL-ACCESS-SOLUTION.md](EXTERNAL-ACCESS-SOLUTION.md)**: 外部アクセスのためのsocat設定
- **[EXTERNAL-PORTS.md](EXTERNAL-PORTS.md)**: ポート設定ガイド
- **[PORT-ALLOCATION-STATUS.md](PORT-ALLOCATION-STATUS.md)**: 現在のポート使用状況

## 技術スタック

### インフラストラクチャ
- K3s v1.34.3
- ArgoCD v2.10.0
- PostgreSQL 16 Alpine
- Redis 7 Alpine

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
- socat (Port Forwarding)
- systemd (Service Management)

## バージョン

**Current Version**: 1.0.0

**Tag**: v1.0.0 (Stable Release)

---

**Repository**: https://github.com/shiftrepo/aws  
**Path**: container/claudecode/ArgoCD  
**License**: Private
