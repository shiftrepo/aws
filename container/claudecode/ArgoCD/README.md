# Organization Management System - ArgoCD GitOps Deployment

Kubernetes（K3s）+ ArgoCD GitOpsによる組織管理システムの完全自動デプロイメント

## 目次

- [概要](#概要)
- [前提条件](#前提条件)
- [環境セットアップ](#環境セットアップ)
- [クイックスタート](#クイックスタート)
- [サービス一覧](#サービス一覧)
- [アクセス方法](#アクセス方法)
- [Kubernetes Dashboard](#kubernetes-dashboard)
- [アーキテクチャ](#アーキテクチャ)
- [主要コマンド](#主要コマンド)
- [開発ワークフロー](#開発ワークフロー)
- [トラブルシューティング](#トラブルシューティング)
- [技術スタック](#技術スタック)

## 概要

このプロジェクトは、以下のコンポーネントで構成されています：

### インフラストラクチャ
- **K3s v1.34.3**: 軽量Kubernetesディストリビューション（Kubernetes v1.34.3）
- **ArgoCD v2.10.0**: GitOps継続的デプロイメント
- **Kubernetes Dashboard v2.7.0**: Kubernetes管理Web UI
- **PostgreSQL 16**: リレーショナルデータベース
- **Redis 7**: セッション管理・キャッシュ

### アプリケーション
- **Backend**: Spring Boot 3.2.1 + Java 21 REST API（2レプリカ）
- **Frontend**: React 18 + Vite Web UI（2レプリカ）

### ネットワーク
- **socat**: ポート転送（外部アクセス用）
- **iptables**: ファイアウォールルール管理
- **LoadBalancer**: K3s ServiceLB（外部IPアサイン）

## 前提条件

### システム要件

| 項目 | 要件 |
|------|------|
| OS | Amazon Linux 2023 / RHEL 9 / CentOS 9 |
| CPU | 2コア以上（推奨: 4コア） |
| メモリ | 4GB以上（推奨: 8GB） |
| ディスク | 20GB以上の空き容量 |
| ネットワーク | インターネット接続必須 |

### 必要なソフトウェア

以下のソフトウェアは**Ansibleが自動インストール**します（手動インストール不要）：

- K3s v1.34.3
- ArgoCD v2.10.0
- Kubernetes Dashboard v2.7.0
- Maven 3.9.6
- Node.js 20.x
- Podman (コンテナビルド)
- socat (ポート転送)

### AWS EC2要件

- **セキュリティグループ**: 以下のポートを開放
  - 22 (SSH)
  - 3000 (Kubernetes Dashboard)
  - 5006 (Frontend)
  - 8000 (ArgoCD HTTP)
  - 8082 (ArgoCD HTTPS)
  - 8083 (Backend API)

- **IAMロール**: 不要（パブリックアクセスのみ）

## 環境セットアップ

### 1. 初回セットアップ

```bash
# 1. リポジトリクローン
cd /root
git clone https://github.com/shiftrepo/aws.git

# 2. プロジェクトディレクトリに移動
cd /root/aws.git/container/claudecode/ArgoCD

# 3. Ansible実行ユーザーの確認
whoami  # root または sudo権限を持つユーザー
```

### 2. EC2パブリックDNS名の確認

Kubernetes DashboardはEC2のパブリックDNS名でアクセスします。事前に確認しておきます。

```bash
# EC2パブリックDNS名を取得
curl -s http://169.254.169.254/latest/meta-data/public-hostname

# 出力例
# ec2-54-172-30-175.compute-1.amazonaws.com
```

**重要**: この値は環境削除・再構築後も変わりません（EC2インスタンスを停止/起動すると変わります）。

### 3. 完全自動デプロイ（初回構築）

**このplaybookを使用する場合**:
- 初回セットアップ
- 完全削除後の再構築
- K3s/ArgoCD/全サービスを一から構築する場合

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

**所要時間**: 約8-10分

**処理内容**:
1. K3s + ArgoCD インストール
2. ビルドツール（Maven, Node.js）セットアップ
3. Backend/Frontend ビルド
4. コンテナイメージ作成・インポート
5. Kubernetesへのデプロイ（PostgreSQL, Redis, Backend, Frontend）
6. ポート転送設定（socat systemdサービス作成）
7. iptablesファイアウォールルール設定
8. ArgoCD GitOpsアプリケーション設定
9. Kubernetes Dashboard インストール・設定

### 4. アプリケーションバージョンアップ

**このplaybookを使用する場合**:
- アプリケーションの新しいバージョンをデプロイする場合
- K3sとArgoCDは既にインストール済み
- アプリケーションコードの変更をデプロイしたい場合

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_app_version.yml
```

または、特定のバージョンを指定してデプロイ:

```bash
ansible-playbook playbooks/deploy_app_version.yml -e "app_version=1.2.0"
```

**所要時間**: 約3-5分

**処理内容**:
1. アプリケーションビルド（Backend/Frontend）
2. Dockerイメージビルド（バージョンタグ付き）
3. K3sへのイメージインポート
4. Deploymentのローリングアップデート
5. ヘルスチェック確認
6. ArgoCD同期

**詳細なバージョンアップ手順**:
- [VERSION_UPGRADE.md](./VERSION_UPGRADE.md) を参照

### 5. デプロイ完了確認

```bash
# 全Pod状態確認
sudo /usr/local/bin/k3s kubectl get pods -A

# サービス状態確認
systemctl status socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard

# ポート確認
ss -tlnp | grep -E "(3000|5006|8000|8082|8083)"
```

すべてのサービスが`Running`かつ`active`であれば正常です。

## クイックスタート

### デプロイ

**初回構築・完全再構築の場合**:
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

**アプリケーションバージョンアップの場合**:
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_app_version.yml
```

### アクセス

| サービス | URL | 認証 | デフォルトユーザー |
|---------|-----|------|-------------------|
| Frontend | http://10.0.1.200:5006 | 不要 | - |
| Backend API | http://10.0.1.200:8083 | 不要 | - |
| ArgoCD HTTPS | https://10.0.1.200:8082 | 必要 | admin / (CREDENTIALS.md参照) |
| ArgoCD HTTP | http://10.0.1.200:8000 | 必要 | admin / (CREDENTIALS.md参照) |
| Kubernetes Dashboard | https://\<EC2-DNS\>:3000 | トークン | (トークンファイル参照) |

### 認証情報

**すべての認証情報は以下のファイルに記載されています**:

```bash
# ArgoCD認証情報
cat /root/argocd-credentials.txt

# Kubernetes Dashboard トークン
cat /root/k8s-dashboard-token.txt
```

詳細は [CREDENTIALS.md](CREDENTIALS.md) を参照してください。

## サービス一覧

### アプリケーションサービス

| サービス名 | ポート | プロトコル | レプリカ | 説明 |
|-----------|--------|-----------|---------|------|
| **orgmgmt-frontend** | 5006 | HTTP | 2 | React Web UI（Nginx） |
| **orgmgmt-backend** | 8083 | HTTP | 2 | Spring Boot REST API |
| **postgres** | 5432 | TCP | 1 | PostgreSQL 16データベース |
| **redis** | 6379 | TCP | 1 | Redis 7キャッシュ |

### 管理サービス

| サービス名 | ポート | プロトコル | 説明 |
|-----------|--------|-----------|------|
| **ArgoCD Server** | 8082 (HTTPS)<br>8000 (HTTP) | HTTPS/HTTP | GitOps継続的デプロイメント管理UI |
| **Kubernetes Dashboard** | 3000 → 30000 | HTTPS | Kubernetes管理Web UI（DNS名必須） |

### Kubernetesシステムサービス

| サービス名 | Namespace | 説明 |
|-----------|-----------|------|
| **coredns** | kube-system | クラスタ内DNS解決 |
| **metrics-server** | kube-system | リソース使用量メトリクス収集 |
| **local-path-provisioner** | kube-system | 動的PersistentVolume作成 |
| **svclb-*** | kube-system | Service LoadBalancer（外部IP割り当て） |

### ポート転送サービス（socat）

| サービス名 | 外部ポート | 内部ポート | 説明 |
|-----------|-----------|-----------|------|
| socat-frontend | 5006 | NodePort（動的） | Frontendポート転送 |
| socat-backend | 8083 | NodePort（動的） | Backendポート転送 |
| socat-argocd-http | 8000 | NodePort（動的） | ArgoCD HTTPポート転送 |
| socat-argocd-https | 8082 | NodePort（動的） | ArgoCD HTTPSポート転送 |
| socat-k8s-dashboard | 3000 | 30000 | Kubernetes Dashboardポート転送 |

すべてのsocatサービスは`systemd`で管理され、自動起動されます。

## アクセス方法

### Frontend（Web UI）

```bash
# ブラウザでアクセス
http://10.0.1.200:5006

# curlでテスト
curl -I http://10.0.1.200:5006/
# HTTP/1.1 200 OK
```

**機能**:
- 組織管理（CRUD）
- 部署管理（CRUD）
- ユーザー管理（CRUD）

### Backend API（REST API）

```bash
# ヘルスチェック
curl http://10.0.1.200:8083/actuator/health
# {"status":"UP"}

# 組織一覧取得
curl http://10.0.1.200:8083/api/organizations

# 部署一覧取得
curl http://10.0.1.200:8083/api/departments

# ユーザー一覧取得
curl http://10.0.1.200:8083/api/users
```

**APIドキュメント**:
- Swagger UI: `http://10.0.1.200:8083/swagger-ui.html`（有効化されている場合）

### ArgoCD（GitOps管理）

**Web UI**:
```bash
# HTTPS（推奨）
https://10.0.1.200:8082

# HTTP（HTTPSにリダイレクト）
http://10.0.1.200:8000
```

**CLI**:
```bash
# ログイン
argocd login 10.0.1.200:8082 \
  --username admin \
  --password "$(cat /root/argocd-credentials.txt | grep Password | awk '{print $2}')" \
  --insecure

# アプリケーション一覧
argocd app list

# アプリケーション詳細
argocd app get orgmgmt-app

# 手動同期
argocd app sync orgmgmt-app
```

## Kubernetes Dashboard

Kubernetes管理用のWeb UIです。クラスタの全リソースを可視化・管理できます。

### アクセス方法

**⚠️ 重要**: Kubernetes DashboardはIPアドレスではアクセスできません。EC2インスタンスのパブリックDNS名を使用してください。

#### 1. EC2パブリックDNS名を取得

```bash
curl -s http://169.254.169.254/latest/meta-data/public-hostname
# 出力例: ec2-54-172-30-175.compute-1.amazonaws.com
```

#### 2. ブラウザでアクセス

```
https://<取得したDNS名>:3000/

例: https://ec2-54-172-30-175.compute-1.amazonaws.com:3000/
```

#### 3. 証明書警告を承認

自己署名証明書を使用しているため、ブラウザで警告が表示されます。

- **Chrome/Edge**: 「詳細設定」→「<DNS名> にアクセスする（安全ではありません）」
- **Firefox**: 「詳細情報」→「危険性を承知で続行」
- **Safari**: 「詳細を表示」→「このWebサイトを閲覧」

#### 4. トークン認証

1. ログイン画面で「トークン」を選択
2. 以下のコマンドでトークンを取得:
   ```bash
   cat /root/k8s-dashboard-token.txt
   ```
3. トークンを貼り付けて「サインイン」

**トークン有効期限**: 10年間（2036年まで）

### Dashboard機能

Kubernetes Dashboardでは以下の操作が可能です：

- **リソース管理**: Pods, Deployments, Services, ConfigMaps, Secrets等の表示・編集
- **ログ確認**: Pod単位でリアルタイムログ表示
- **シェル接続**: Pod内でコマンド実行（kubectl exec相当）
- **リソースメトリクス**: CPU/メモリ使用率のグラフ表示
- **イベント確認**: クラスタイベントの時系列表示
- **YAML編集**: リソース定義の直接編集

### トークン再発行

トークンを再発行する場合:

```bash
# 10年間有効なトークン生成
sudo /usr/local/bin/k3s kubectl create token admin-user \
  -n kubernetes-dashboard \
  --duration=87600h

# 1時間有効なトークン生成
sudo /usr/local/bin/k3s kubectl create token admin-user \
  -n kubernetes-dashboard \
  --duration=1h
```

### DNS名が変わる場合

EC2インスタンスを**停止/起動**するとパブリックDNS名が変わります。その場合は再度DNS名を取得してアクセスしてください。

```bash
# 最新のDNS名を取得
curl -s http://169.254.169.254/latest/meta-data/public-hostname
```

**注意**: インスタンスを再起動（reboot）するだけではDNS名は変わりません。

## アーキテクチャ

### システム構成図

```
                          外部アクセス（インターネット）
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            Port 3000 (HTTPS)  Port 5006 (HTTP)  Port 8083 (HTTP)
            Port 8000 (HTTP)   Port 8082 (HTTPS)
                    │               │               │
              ┌─────┴──────────────┴───────────────┴─────┐
              │         socat Port Forwarding             │
              │  (systemd services - 5 services)          │
              └─────┬──────────────┬───────────────┬─────┘
                    │              │               │
          ┌─────────┴──────┬──────┴───────┬──────┴─────────┐
          │                │              │                │
    K8s Dashboard    Frontend(x2)   Backend(x2)        ArgoCD
    (NodePort 30000) (LoadBalancer) (LoadBalancer)   (LoadBalancer)
          │                │              │                │
          │                └──────┬───────┘                │
          │                       │                        │
          │                  PostgreSQL                    │
          │                  Redis                         │
          │                       │                        │
          └───────────────────────┴────────────────────────┘
                    Kubernetes (K3s) Cluster
                     GitOps by ArgoCD
```

### GitOps Workflow

```
GitHub Repository
  └─ container/claudecode/ArgoCD/k8s-manifests/
       ├─ backend-deployment.yaml
       ├─ backend-service.yaml
       ├─ frontend-deployment.yaml
       ├─ frontend-service.yaml
       ├─ postgres-deployment.yaml
       └─ redis-deployment.yaml
            │
            ├─ ArgoCD自動検出（3分ごと）
            │
            └─→ Kubernetes Cluster
                 ├─ Backend Deployment (2 replicas)
                 ├─ Frontend Deployment (2 replicas)
                 ├─ PostgreSQL Deployment (1 replica)
                 └─ Redis Deployment (1 replica)
```

**GitOps機能**:
- **自動同期**: 3分ごとにGitリポジトリをチェック
- **Self Heal**: 手動変更を自動で元に戻す
- **Prune**: マニフェストから削除されたリソースを自動削除

### ポート構成

#### 外部公開ポート

| 外部ポート | サービス | プロトコル | 説明 |
|-----------|---------|-----------|------|
| 3000 | Kubernetes Dashboard | HTTPS | K8s管理UI（DNS名必須） |
| 5006 | Frontend | HTTP | React Web UI |
| 8000 | ArgoCD | HTTP | GitOps管理（HTTPSリダイレクト） |
| 8082 | ArgoCD | HTTPS | GitOps管理 |
| 8083 | Backend API | HTTP | REST API |

#### 内部ポート（NodePort）

NodePortは自動割り当てされます（30000-32767の範囲）。socatが自動的にマッピングします。

#### クラスタ内部ポート

| サービス | ClusterIP Port | 説明 |
|---------|---------------|------|
| postgres | 5432 | PostgreSQL接続 |
| redis | 6379 | Redis接続 |
| kubernetes | 443 | Kubernetes API Server |

### iptablesファイアウォールルール

外部アクセスを許可するため、以下のiptablesルールが**自動的に設定**されます：

```bash
# ルール確認
sudo iptables -L INPUT -n --line-numbers | head -10
```

**重要**: ルールはINPUTチェインの**先頭**に挿入されます（K3sのKUBE-ROUTER-INPUTより前）。

```
1. ACCEPT tcp dpt:3000  (Kubernetes Dashboard)
2. KUBE-ROUTER-INPUT    (K3s管理チェイン)
3. ACCEPT tcp dpt:8082  (ArgoCD HTTPS)
4. ACCEPT tcp dpt:8000  (ArgoCD HTTP)
5. ACCEPT tcp dpt:8083  (Backend API)
6. ACCEPT tcp dpt:5006  (Frontend)
```

この順序により、K3sのネットワークポリシーに影響を受けずに外部アクセスが可能になります。

## ディレクトリ構造

```
.
├── ansible/
│   ├── playbooks/
│   │   ├── deploy_k8s_complete.yml    # 完全自動デプロイ（メイン）
│   │   ├── install_k3s_and_argocd.yml # K3s+ArgoCD単独インストール
│   │   └── install_build_tools.yml    # Maven/Node.js単独インストール
│   └── inventory/
│       └── hosts.yml                   # Ansibleインベントリ（localhost）
├── k8s-manifests/                      # Kubernetesマニフェスト（ArgoCD管理対象）
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── redis-deployment.yaml
│   └── redis-service.yaml
├── app/
│   ├── backend/                        # Spring Boot アプリケーション
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/
│   │       └── main/
│   │           ├── java/
│   │           └── resources/
│   │               ├── application.yml
│   │               └── db/migration/   # Flyway DBマイグレーション
│   └── frontend/                       # React アプリケーション
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── package.json
│       └── src/
│           ├── components/
│           ├── api/
│           └── App.jsx
├── argocd-application.yaml             # ArgoCD Applicationマニフェスト
├── CREDENTIALS.md                      # 認証情報・アクセスガイド
├── README.md                           # このファイル
└── archive/                            # 過去の経緯・履歴ファイル

```

## 主要コマンド

### Kubernetesクラスタ管理

```bash
# クラスタ情報
sudo /usr/local/bin/k3s kubectl cluster-info

# 全Namespace のPod確認
sudo /usr/local/bin/k3s kubectl get pods -A

# 特定Namespace のPod確認
sudo /usr/local/bin/k3s kubectl get pods -n default
sudo /usr/local/bin/k3s kubectl get pods -n argocd
sudo /usr/local/bin/k3s kubectl get pods -n kubernetes-dashboard

# サービス確認
sudo /usr/local/bin/k3s kubectl get svc -A

# ノード確認
sudo /usr/local/bin/k3s kubectl get nodes -o wide
```

### ArgoCD管理

```bash
# ArgoCD Application確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd

# Application詳細
sudo /usr/local/bin/k3s kubectl describe application orgmgmt-app -n argocd

# Application ステータス（簡易）
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd \
  -o jsonpath='{.status.sync.status}:{.status.health.status}'
# 出力例: Synced:Healthy
```

### ログ確認

```bash
# Backend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend

# Frontend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-frontend

# PostgreSQL ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/postgres

# ArgoCD Server ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/argocd-server -n argocd

# Kubernetes Dashboard ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/kubernetes-dashboard -n kubernetes-dashboard
```

### サービス管理

```bash
# socat サービス状態確認
systemctl status socat-frontend
systemctl status socat-backend
systemctl status socat-argocd-http
systemctl status socat-argocd-https
systemctl status socat-k8s-dashboard

# socat サービス再起動
sudo systemctl restart socat-frontend
sudo systemctl restart socat-backend

# K3s サービス確認
sudo systemctl status k3s

# K3s サービス再起動
sudo systemctl restart k3s
```

### ポート確認

```bash
# リスニングポート確認
ss -tlnp | grep -E "(3000|5006|8000|8082|8083)"

# iptablesルール確認
sudo iptables -L INPUT -n --line-numbers | head -15
```

## 開発ワークフロー

### 1. マニフェスト変更（GitOps）

Kubernetesマニフェストを変更してGitにプッシュすると、ArgoCDが自動的にデプロイします。

```bash
# 1. マニフェストファイルを編集
vim k8s-manifests/backend-deployment.yaml

# 例: レプリカ数を変更
# replicas: 2 → replicas: 3

# 2. 変更をコミット・プッシュ
git add k8s-manifests/backend-deployment.yaml
git commit -m "feat: Increase backend replicas to 3"
git push origin main

# 3. ArgoCDが自動的にデプロイ（最大3分）
# ブラウザでArgoCD UIを開いて進捗確認
# https://10.0.1.200:8082

# 4. 同期状態確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd
```

### 2. アプリケーションイメージ更新

アプリケーションコードを変更してイメージを更新します。

#### Backend更新

```bash
# 1. コード変更
vim app/backend/src/main/java/com/example/orgmgmt/controller/OrganizationController.java

# 2. ビルド
cd app/backend
mvn clean package -DskipTests

# 3. コンテナイメージビルド
podman build -t orgmgmt-backend:latest .

# 4. イメージエクスポート・インポート
podman save localhost/orgmgmt-backend:latest -o /tmp/backend.tar
sudo k3s ctr images import /tmp/backend.tar

# 5. Podを再起動（ローリングアップデート）
sudo /usr/local/bin/k3s kubectl rollout restart deployment/orgmgmt-backend

# 6. ロールアウト状態確認
sudo /usr/local/bin/k3s kubectl rollout status deployment/orgmgmt-backend
```

#### Frontend更新

```bash
# 1. コード変更
vim app/frontend/src/App.jsx

# 2. ビルド
cd app/frontend
npm install
npm run build

# 3. コンテナイメージビルド
podman build -t orgmgmt-frontend:latest .

# 4. イメージエクスポート・インポート
podman save localhost/orgmgmt-frontend:latest -o /tmp/frontend.tar
sudo k3s ctr images import /tmp/frontend.tar

# 5. Podを再起動
sudo /usr/local/bin/k3s kubectl rollout restart deployment/orgmgmt-frontend

# 6. ロールアウト状態確認
sudo /usr/local/bin/k3s kubectl rollout status deployment/orgmgmt-frontend
```

### 3. データベースマイグレーション

Flywayを使用してデータベーススキーマを管理します。

```bash
# 1. マイグレーションファイル作成
vim app/backend/src/main/resources/db/migration/V5__add_new_column.sql

# 例:
# ALTER TABLE organizations ADD COLUMN description TEXT;

# 2. Backendを再ビルド・デプロイ
cd app/backend
mvn clean package -DskipTests
# ... （イメージビルド・インポート・再起動）

# 3. マイグレーション実行確認
sudo /usr/local/bin/k3s kubectl logs deployment/orgmgmt-backend | grep Flyway
```

## トラブルシューティング

### 外部アクセスできない

**症状**: ブラウザでサービスにアクセスできない

```bash
# 1. socatサービス状態確認
systemctl status socat-frontend
systemctl status socat-backend
systemctl status socat-argocd-http
systemctl status socat-argocd-https
systemctl status socat-k8s-dashboard

# 2. ポートリッスン確認
ss -tlnp | grep -E "(3000|5006|8000|8082|8083)"

# 出力例:
# LISTEN 0  5  0.0.0.0:3000  0.0.0.0:*  users:(("socat",pid=XXX,fd=5))

# 3. iptablesルール確認
sudo iptables -L INPUT -n --line-numbers | head -10

# ルールが先頭にあることを確認
# 1. ACCEPT tcp dpt:3000
# 2. KUBE-ROUTER-INPUT

# 4. socatサービス再起動
sudo systemctl restart socat-frontend
sudo systemctl restart socat-backend
sudo systemctl restart socat-argocd-http
sudo systemctl restart socat-argocd-https
sudo systemctl restart socat-k8s-dashboard

# 5. アクセステスト
curl -I http://10.0.1.200:5006/
curl -I http://10.0.1.200:8083/actuator/health
curl -k -I https://10.0.1.200:8082/
```

### Kubernetes Dashboard にアクセスできない

**症状**: `https://ec2-xxx.compute-1.amazonaws.com:3000/` にアクセスできない

```bash
# 1. 最新のEC2パブリックDNS名を取得
curl -s http://169.254.169.254/latest/meta-data/public-hostname

# 2. Dashboard Pod状態確認
sudo /usr/local/bin/k3s kubectl get pods -n kubernetes-dashboard

# 3. Dashboard Service確認
sudo /usr/local/bin/k3s kubectl get svc kubernetes-dashboard -n kubernetes-dashboard
# TYPE: NodePort, PORT(S): 443:30000/TCP

# 4. socat-k8s-dashboard サービス確認
systemctl status socat-k8s-dashboard

# 5. ポート3000確認
ss -tlnp | grep :3000

# 6. iptablesルール確認（先頭にあることを確認）
sudo iptables -L INPUT -n --line-numbers | grep 3000

# 7. 内部アクセステスト
curl -k -I https://127.0.0.1:30000/
curl -k -I https://127.0.0.1:3000/

# 8. トークン確認
cat /root/k8s-dashboard-token.txt
```

**解決策**:
- EC2インスタンスを停止/起動した場合、パブリックDNS名が変わります
- 最新のDNS名で再度アクセスしてください
- IPアドレス（10.0.1.200）ではアクセスできません

### ArgoCD Application が OutOfSync

**症状**: ArgoCD UIで「OutOfSync」と表示される

```bash
# 1. Application状態確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd

# 2. 手動同期
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge \
  -p '{"operation": {"sync": {"prune": true}}}'

# 3. ArgoCDの同期設定確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd -o yaml | grep -A 5 syncPolicy

# 4. GitリポジトリのマニフェストとK8sリソースの差分確認
# ArgoCD UIで "App Diff" を確認
```

### Pod が起動しない

**症状**: Pod が `Pending`、`CrashLoopBackOff`、`Error` 状態

```bash
# 1. Pod状態詳細確認
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>

# 2. イベント確認
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp' | tail -20

# 3. ログ確認
sudo /usr/local/bin/k3s kubectl logs <pod-name>
sudo /usr/local/bin/k3s kubectl logs <pod-name> --previous  # 前回のログ

# 4. リソース不足確認
sudo /usr/local/bin/k3s kubectl top nodes
sudo /usr/local/bin/k3s kubectl top pods

# 5. イメージPull確認
sudo /usr/local/bin/k3s kubectl describe pod <pod-name> | grep -A 5 Events

# 6. Pod再起動
sudo /usr/local/bin/k3s kubectl delete pod <pod-name>
```

**よくある原因**:
- イメージがK3sにインポートされていない
- リソース不足（メモリ/CPU）
- ConfigMap/Secretが存在しない
- 環境変数の設定ミス

### Backend API が 500 エラー

**症状**: Backend API で Internal Server Error

```bash
# 1. Backend ログ確認
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend

# 2. PostgreSQL接続確認
sudo /usr/local/bin/k3s kubectl get pods | grep postgres
sudo /usr/local/bin/k3s kubectl logs deployment/postgres

# 3. PostgreSQL サービス確認
sudo /usr/local/bin/k3s kubectl get svc postgres

# 4. Backend環境変数確認
sudo /usr/local/bin/k3s kubectl describe deployment orgmgmt-backend | grep -A 10 Environment

# 5. データベース接続テスト（Backend Pod内）
sudo /usr/local/bin/k3s kubectl exec -it deployment/orgmgmt-backend -- \
  curl postgres:5432
```

### システム全体のリセット

すべてのサービスを削除して再構築する場合:

```bash
# 1. K3s完全削除
sudo /usr/local/bin/k3s-uninstall.sh

# 2. socat サービス削除
for service in socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard; do
  sudo systemctl stop $service 2>/dev/null
  sudo systemctl disable $service 2>/dev/null
  sudo rm -f /etc/systemd/system/${service}.service
done
sudo systemctl daemon-reload

# 3. 認証情報ファイル削除
sudo rm -f /root/argocd-credentials.txt /root/k8s-dashboard-token.txt

# 4. Podman イメージ削除
podman rmi -f $(podman images -q localhost/orgmgmt-backend localhost/orgmgmt-frontend 2>/dev/null) 2>/dev/null || true

# 5. 再構築
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

## 環境削除

```bash
# K3s完全削除（すべてのリソースを削除）
sudo /usr/local/bin/k3s-uninstall.sh
```

このコマンドにより、以下がすべて削除されます:
- K3s クラスタ
- ArgoCD
- Kubernetes Dashboard
- すべてのアプリケーション（Backend, Frontend, PostgreSQL, Redis）
- コンテナイメージ
- ネットワーク設定

**注意**: socatサービスは自動削除されません。手動で削除する場合は上記「システム全体のリセット」を参照してください。

## ドキュメント

- **[CREDENTIALS.md](CREDENTIALS.md)**: 🔑 認証情報・アクセスガイド（必読）
  - ArgoCD / Kubernetes Dashboard / PostgreSQL / Redis 認証情報
  - パスワード・トークン取得方法
  - セキュリティ設定とトラブルシューティング
- **[ARGOCD-DEPLOYMENT-GUIDE.md](ARGOCD-DEPLOYMENT-GUIDE.md)**: ArgoCDの詳細な運用ガイド
- **[DEPLOYMENT-SUMMARY.md](DEPLOYMENT-SUMMARY.md)**: デプロイメント詳細サマリー
- **[EXTERNAL-ACCESS-SOLUTION.md](EXTERNAL-ACCESS-SOLUTION.md)**: 外部アクセスのためのsocat設定
- **[EXTERNAL-PORTS.md](EXTERNAL-PORTS.md)**: ポート設定ガイド
- **[PORT-ALLOCATION-STATUS.md](PORT-ALLOCATION-STATUS.md)**: 現在のポート使用状況

## 技術スタック

### インフラストラクチャ
- **K3s v1.34.3** (Kubernetes v1.34.3)
- **ArgoCD v2.10.0**
- **Kubernetes Dashboard v2.7.0**
- **PostgreSQL 16 Alpine**
- **Redis 7 Alpine**

### Backend
- **Java 21** (OpenJDK)
- **Spring Boot 3.2.1**
- **Spring Data JPA** (Hibernate)
- **Flyway 10** (Database Migration)
- **Lombok** (Code Generation)
- **Maven 3.9.6** (Build Tool)

### Frontend
- **React 18.2.0**
- **Vite 5** (Build Tool)
- **React Router DOM** (Routing)
- **Axios 1.6.5** (HTTP Client)
- **Nginx Alpine** (Web Server)
- **Node.js 20.x** (Runtime)

### デプロイ・運用
- **Ansible 2.14+** (Infrastructure as Code)
- **Podman** (Container Build)
- **socat** (Port Forwarding)
- **systemd** (Service Management)
- **iptables** (Firewall Management)

### Kubernetes エコシステム
- **K3s ServiceLB** (Load Balancer)
- **CoreDNS** (DNS Server)
- **Metrics Server** (Resource Metrics)
- **Local Path Provisioner** (Storage)
- **Kube-Router** (Network Policy)

## バージョン

**Current Version**: 1.0.0

**Tag**: v1.0.0 (Stable Release)

**最終更新**: 2026-02-06

## サポート

### 問題報告

問題や質問がある場合は、GitHubのIssueで報告してください。

### コミュニティ

- Repository: https://github.com/shiftrepo/aws
- Path: container/claudecode/ArgoCD

---

**Repository**: https://github.com/shiftrepo/aws
**Path**: container/claudecode/ArgoCD
**License**: Private
