# Organization Management System - ArgoCD GitOps Deployment

Kubernetes（K3s）+ ArgoCD GitOps + Kustomize + Gitea による組織管理システムの完全自動デプロイメント・バージョン管理

## 目次

- [概要](#概要)
- [環境依存パラメータ](#環境依存パラメータ)
- [Ansibleのインストール](#ansibleのインストール)
- [クイックスタート](#クイックスタート)
- [Gitea Git サーバー](#gitea-git-サーバー)
- [完全自動回帰テスト](#完全自動回帰テスト)
- [GitOpsバージョン管理](#gitopsバージョン管理)
- [サービス一覧](#サービス一覧)
- [アクセス方法](#アクセス方法)
- [アーキテクチャ](#アーキテクチャ)
- [Playbook一覧](#playbook一覧)
- [主要コマンド](#主要コマンド)
- [スクラップビルド（完全削除と再構築）](#スクラップビルド完全削除と再構築)
- [トラブルシューティング](#トラブルシューティング)
- [技術スタック](#技術スタック)

## 概要

### 特徴

- **完全自動化**: 1コマンドで環境削除→構築→回帰テスト実行
- **GitOps準拠**: Kustomize overlaysによる宣言的バージョン管理
- **Gitea統合**: オンプレミス Git サーバーを Ansible で自動構築・管理
- **両バージョン対応**: v1.0.0とv1.1.0を自動ビルド・インポート
- **ゼロダウンタイム**: ローリングアップデートによる無停止デプロイ
- **コンテナランタイム切替**: Docker / Podman を設定ファイル1行で切替可能
- **完全なポータビリティ**: どの環境でも同一の手順で実行可能

### システム構成

| コンポーネント | バージョン | 説明 |
|--------------|----------|------|
| **K3s** | v1.34.3 | 軽量Kubernetesディストリビューション |
| **ArgoCD** | v2.10.0 | GitOps継続的デプロイメント |
| **Kustomize** | Built-in | Kubernetes ネイティブ構成管理 |
| **Gitea** | 1.22 | オンプレミス Git サーバー（Podman コンテナ） |
| **PostgreSQL** | 16-alpine | リレーショナルデータベース |
| **Redis** | 7-alpine | セッション管理・キャッシュ |
| **Backend** | Spring Boot 3.2.1 + Java 21 | REST API (2レプリカ) |
| **Frontend** | React 18 + Vite | Web UI (2レプリカ) |

### 前提条件

| 項目 | 要件 |
|------|------|
| OS | Fedora / RHEL 9 / CentOS Stream 9 |
| CPU | 2コア以上（推奨: 4コア） |
| メモリ | 4GB以上（推奨: 8GB） |
| ディスク | 20GB以上の空き容量 |
| ネットワーク | インターネット接続必須 |

**必要なソフトウェアはAnsibleが自動インストール**します：
- K3s, ArgoCD, Java 21 (OpenJDK), Maven, Node.js, socat
- コンテナランタイム: Docker または Podman（`environment.yml` で選択）

## 環境依存パラメータ

### 設定ファイルの構造

**`ansible/config/environment.yml` を唯一の設定ファイルとして管理します。**
k8s マニフェスト・`argocd-application.yaml` を直接編集する必要はありません。

```
ansible/config/environment.yml            ← 環境ごとに編集するファイル（唯一）
        │
        ├─ network.external_ip            → backend-service.yaml / frontend-service.yaml (externalIPs)
        ├─ git.repository_url             → argocd-application.yaml (repoURL)
        ├─ git.branch                     → argocd-application.yaml (targetRevision)
        ├─ directories.base_dir           → 全 playbook の project_root
        ├─ application.version            → 全 playbook の app_version デフォルト値
        ├─ kubernetes.k3s_version         → K3s バージョン
        ├─ argocd.version                 → ArgoCD バージョン
        ├─ containers.runtime             → "podman" または "docker" で切替
        ├─ features.gitea_enabled         → true で Gitea を有効化
        └─ gitea.*                        → Gitea のバージョン・ポート・認証情報
```

### 変更必須パラメータ

#### ネットワーク（IPアドレス）

```yaml
network:
  external_ip: ""          # 空 = 自動検出（推奨）
  # external_ip: "192.168.1.100"  # 固定したい場合は明記
```

#### プロジェクトパス

```yaml
directories:
  base_dir: "/root/aws.git/container/claudecode/ArgoCD"
```

#### Gitリポジトリ

```yaml
git:
  repository_url: "https://github.com/shiftrepo/aws.git"
  branch: "main"
  manifests_path: "container/claudecode/ArgoCD/k8s-manifests/overlays"
```

### コンテナランタイムの選択

Docker と Podman を設定ファイル1行で切り替えられます。

```yaml
containers:
  runtime: "podman"   # "docker" に変更すると Docker を使用
```

> この環境では `/usr/bin/docker` は Podman へのラッパーです。`runtime: "docker"` でも実体は Podman が動作します。

### Gitea 設定

```yaml
features:
  gitea_enabled: true    # false にすると install_gitea.yml / start_all.yml で Gitea をスキップ

gitea:
  version: "1.22"
  port: 3001             # Web UI ポート
  ssh_port: 2222         # SSH ポート
  data_dir: "/var/lib/gitea"
  container_name: "gitea"
  admin:
    username: "gitea_admin"
    password: "GiteaAdmin123!"
    email: "admin@gitea.local"
```

### 変更推奨パラメータ（セキュリティ）

```yaml
database:
  name: "orgmgmt"
  user: "orgmgmt_user"
  password: "SecurePassword123!"   # 本番環境では必ず変更
```

### 変更任意パラメータ（ポート番号）

| キー | デフォルト値 | 説明 |
|-----|------------|------|
| `ports.frontend` | `5006` | フロントエンド外部ポート |
| `ports.backend` | `8083` | バックエンド外部ポート |
| `ports.argocd_https` | `8082` | ArgoCD HTTPS ポート |
| `ports.argocd_http` | `8000` | ArgoCD HTTP ポート |
| `ports.dashboard` | `3000` | Kubernetes Dashboard ポート |
| `gitea.port` | `3001` | Gitea Web UI ポート |
| `gitea.ssh_port` | `2222` | Gitea SSH ポート |

### 別環境へのデプロイ手順（チェックリスト）

```
[ ] 1. リポジトリをクローン
       git clone https://github.com/shiftrepo/aws.git /root/aws.git

[ ] 2. ansible/config/environment.yml を編集
       - directories.base_dir  : クローン先が /root/aws.git 以外の場合は変更
       - network.external_ip   : 固定IPにしたい場合のみ設定（空 = 自動検出）
       - git.repository_url    : フォーク先リポジトリの場合は変更
       - database.password     : 本番環境では必ず変更
       - features.gitea_enabled: Gitea を使う場合は true

[ ] 3. Ansible をインストール
       sudo python3 -m pip install ansible
       sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook

[ ] 4. 全サービスを一括起動
       cd /root/aws.git/container/claudecode/ArgoCD/ansible
       ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

## Ansibleのインストール

### インストール（推奨: システム全体）

```bash
# pip3 でシステム全体にインストール（root権限必須）
sudo python3 -m pip install ansible

# PATH に追加（root で実行する場合は不要）
sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook

# バージョン確認
ansible-playbook --version
```

### インストール（dnf）

```bash
sudo dnf install -y ansible
ansible --version
```

### インストール確認

```bash
ansible-playbook --version
# ansible-playbook [core 2.15.x]

ansible localhost -m ping
# localhost | SUCCESS => { "ping": "pong" }
```

### PATH の設定

| インストール方法 | バイナリパス |
|--------------|------------|
| `sudo python3 -m pip install ansible` | `/usr/local/bin/ansible-playbook` |
| `sudo dnf install ansible` | `/usr/bin/ansible-playbook` |
| `pip3 install --user ansible` | `~/.local/bin/ansible-playbook` |

> **注意**: `pip3 install --user` でインストールした場合、root として実行する playbook から呼び出せないことがあります。システム全体へのインストール（`sudo pip3`）を推奨します。

## クイックスタート

### リポジトリクローン

```bash
git clone https://github.com/shiftrepo/aws.git /root/aws.git
cd /root/aws.git/container/claudecode/ArgoCD/ansible
```

### 全サービス一括起動（推奨）

K3s・ArgoCD・アプリ・Gitea をすべて一括で構築・起動します。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

**実行内容**:
1. `deploy_k8s_complete.yml` — K3s・ArgoCD・ビルド・デプロイ・socat
2. `install_gitea.yml` — Gitea コンテナ起動・管理者ユーザー作成（`gitea_enabled: true` の場合）

### 全サービス一括削除

```bash
# データ保持（再インストール用）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml

# データも含めて完全削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"

# ビルドツール（Java/Maven/Node.js）も削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true remove_build_tools=true"
```

### 完全自動回帰テスト

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

## Gitea Git サーバー

### 概要

Gitea はオンプレミスの Git サーバーです。Podman コンテナとして起動し、systemd で自動起動管理されます。`features.gitea_enabled` フラグで有効・無効を切り替えられます。

### 有効化

```yaml
# ansible/config/environment.yml
features:
  gitea_enabled: true
```

### 単独インストール・削除

```bash
# インストール（K3s が起動済みの状態でも単独追加可能）
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml

# 削除（データ保持）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml

# 完全削除（データも削除）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml -e "purge_data=true"
```

### バージョンアップ・バージョンダウン回帰テスト

1つのプレイブックで「構築→バージョンアップ確認→バージョンダウン確認」まで自動検証します。

```bash
# デフォルト: 1.21 → 1.22 → 1.21
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml

# バージョン指定
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml \
  -e "test_version_old=1.21 test_version_new=1.22"
```

**テストフロー**:
```
Phase 1: 既存 Gitea 削除（クリーンスタート）
Phase 2: 旧・新バージョン イメージ事前取得
Phase 3: 旧バージョン (1.21) インストール
Phase 4: 動作確認 + テストデータ作成（Org/Repo）
Phase 5: バージョンアップ (1.21 → 1.22)
Phase 6: 新バージョン確認 + データ保持確認
Phase 7: バージョンダウン (1.22 → 1.21)
Phase 8: 旧バージョン確認 + データ保持確認
Phase 9: 全テスト結果サマリー
```

### アクセス情報

| 項目 | 値（デフォルト） |
|------|--------------|
| Web UI | `http://<HOST_IP>:3001` |
| SSH | `<HOST_IP>:2222` |
| 管理者ユーザー | `gitea_admin` |
| 管理者パスワード | `GiteaAdmin123!` |

> パスワードは `ansible/config/environment.yml` の `gitea.admin.password` で変更できます。

### 技術的注意事項

- **SELinux**: ボリュームマウントに `:Z` フラグを使用（自動でコンテキストを設定）
- **ディレクトリ権限**: コンテナ内 git ユーザー（UID 1000）でデータディレクトリを事前作成
- **systemd**: `podman generate systemd` で自動起動サービスを生成（フォールバックあり）
- **Docker 切替**: `runtime: "docker"` に変更すると `docker generate systemd` は非対応のためフォールバックで手動 systemd サービスを生成

## 完全自動回帰テスト

### 実行方法

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

### テストフロー

```
Phase 1: 環境削除
  └─> K3s uninstall / コンテナクリーンアップ / 履歴ファイル削除

Phase 2-3: 両バージョンビルド
  └─> v1.0.0 (tag: argocd-regression-v1.0.0)
  └─> v1.1.0 (branch: main)

Phase 4: K3s + ArgoCD構築

Phase 5: イメージインポート
  └─> v1.0.0 / v1.1.0 両方を K3s containerd へ

Phase 6: v1.0.0 初期デプロイ

Phase 7-9: バージョン変更テスト
  └─> Upgrade   v1.0.0 → v1.1.0 (GitOps)
  └─> Rollback  v1.1.0 → v1.0.0 (GitOps)
  └─> Re-upgrade v1.0.0 → v1.1.0 (GitOps)

Phase 10: 最終確認
```

### タグベース実行

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml --tags=cleanup
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml --tags=build-v1.0.0
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml --tags=upgrade-test
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml --tags=rollback-test
```

## GitOpsバージョン管理

### Kustomize構造

```
k8s-manifests/
├── base/                           # 共通ベース
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   └── kustomization.yaml
└── overlays/
    ├── v1.0.0/
    │   └── kustomization.yaml     # newTag: "1.0.0"
    └── v1.1.0/
        └── kustomization.yaml     # newTag: "1.1.0"
```

### バージョンアップグレード（GitOps方式）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml -e "app_version=1.1.0"
```

### バージョンロールバック（GitOps方式）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml -e "target_version=1.0.0"
```

### バージョン履歴確認

```bash
cat /root/app-version-history.txt
```

## サービス一覧

### アプリケーションサービス（K3s 内）

| サービス名 | ポート | レプリカ | 説明 |
|-----------|--------|---------|------|
| **orgmgmt-frontend** | 5006 | 2 | React Web UI（Nginx） |
| **orgmgmt-backend** | 8083 | 2 | Spring Boot REST API |
| **postgres** | 5432 | 1 | PostgreSQL 16 |
| **redis** | 6379 | 1 | Redis 7 キャッシュ |

### 管理サービス（K3s 内）

| サービス名 | ポート | 説明 |
|-----------|--------|------|
| **ArgoCD Server** | 8082 (HTTPS) / 8000 (HTTP) | GitOps 管理 UI |
| **Kubernetes Dashboard** | 3000 | K8s 管理 Web UI |

### インフラサービス（Podman コンテナ）

| サービス名 | ポート | 説明 |
|-----------|--------|------|
| **Gitea** | 3001 (HTTP) / 2222 (SSH) | オンプレミス Git サーバー |

## アクセス方法

### Frontend

```bash
http://<HOST_IP>:5006
```

### Backend API

```bash
# ヘルスチェック
curl http://<HOST_IP>:8083/actuator/health

# API エンドポイント
curl http://<HOST_IP>:8083/api/organizations
curl http://<HOST_IP>:8083/api/departments
curl http://<HOST_IP>:8083/api/users
```

### ArgoCD

```bash
# Web UI
https://<HOST_IP>:8082

# 認証情報
cat /root/argocd-credentials.txt

# CLI ログイン
argocd login <HOST_IP>:8082 \
  --username admin \
  --password "$(grep Password /root/argocd-credentials.txt | awk '{print $2}')" \
  --insecure
```

### Kubernetes Dashboard

```bash
# EC2 の場合はパブリック DNS 名でアクセス
https://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:3000/

# トークン取得
cat /root/k8s-dashboard-token.txt
```

### Gitea

```bash
# Web UI
http://<HOST_IP>:3001

# SSH git clone
git clone git@<HOST_IP>:2222/<user>/<repo>.git

# API バージョン確認
curl http://<HOST_IP>:3001/api/v1/version

# 管理者ログイン情報
Username : gitea_admin
Password : GiteaAdmin123!  (environment.yml で変更可)
```

## アーキテクチャ

### システム構成図

```
                          外部アクセス（インターネット）
                                    │
          ┌─────────────────────────┼──────────────────────────────┐
          │                         │                              │
    Port 3001 (HTTP)           Port 5006/8083                Port 8082/8000/3000
    Port 2222 (SSH)           (Frontend/Backend)             (ArgoCD/Dashboard)
          │                         │                              │
    ┌─────┴──────┐      ┌───────────┴──────────────────────────────┴───┐
    │   Gitea    │      │          socat Port Forwarding               │
    │  (Podman)  │      │       (systemd services × 5)                 │
    └────────────┘      └───────────┬──────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────┐
          │                         │                     │
    Frontend(×2)             Backend(×2)              ArgoCD(×7)
    (LoadBalancer)           (LoadBalancer)           (LoadBalancer)
          │                         │                     │
          └────────────┬────────────┘                     │
                       │                                  │
                  PostgreSQL                    Kubernetes Dashboard
                  Redis                         (NodePort)
                       │
          ┌────────────┴────────────────────┐
          │   Kubernetes (K3s) Cluster       │
          │    GitOps by ArgoCD              │
          └──────────────────────────────────┘
```

### GitOps Workflow

```
GitHub Repository
  └─ k8s-manifests/
       ├─ base/              (image: latest)
       └─ overlays/
           ├─ v1.0.0/        (newTag: "1.0.0")
           └─ v1.1.0/        (newTag: "1.1.0")
                │
                ├─ ArgoCD 自動検出（3分ごと）
                │
                └─→ Kubernetes Cluster
                     ├─ Backend  (×2 replicas)
                     ├─ Frontend (×2 replicas)
                     ├─ PostgreSQL
                     └─ Redis
```

### ディレクトリ構造

```
.
├── ansible/
│   ├── config/
│   │   └── environment.yml              ← 唯一の設定ファイル
│   ├── group_vars/
│   │   └── all.yml                      ← 変数マッピング
│   ├── inventory/
│   │   └── hosts.yml
│   └── playbooks/
│       ├── start_all.yml                ← 全サービス一括起動（推奨）
│       ├── uninstall_all.yml            ← 全サービス一括削除
│       ├── deploy_regression_test_complete.yml  ← 完全自動回帰テスト
│       ├── deploy_k8s_complete.yml      ← K3s+ArgoCD+アプリ構築
│       ├── install_k3s_and_argocd.yml   ← K3s+ArgoCD単独
│       ├── install_build_tools.yml      ← Java/Maven/Node.js
│       ├── uninstall_build_tools.yml    ← ビルドツール削除
│       ├── install_gitea.yml            ← Gitea インストール
│       ├── uninstall_gitea.yml          ← Gitea 削除
│       ├── gitea_regression_test.yml    ← Gitea バージョン回帰テスト
│       ├── deploy_app_version_gitops.yml      ← GitOps アップグレード
│       ├── rollback_app_version_gitops.yml    ← GitOps ロールバック
│       ├── deploy_app_version.yml       ← 直接デプロイ
│       └── rollback_app_version.yml     ← 直接ロールバック
├── k8s-manifests/                       ← ArgoCD 管理対象
│   ├── base/
│   └── overlays/
│       ├── v1.0.0/
│       └── v1.1.0/
├── app/
│   ├── backend/                         ← Spring Boot
│   └── frontend/                        ← React
├── argocd-application.yaml
└── README.md
```

## Playbook一覧

### 起動・削除

| Playbook | 用途 |
|----------|------|
| **start_all.yml** | **全サービス一括起動（推奨）** K3s+ArgoCD+アプリ+Gitea |
| **uninstall_all.yml** | **全サービス一括削除** socat/Gitea/K3s/イメージ/データ |

### K3s / アプリ

| Playbook | 用途 |
|----------|------|
| deploy_regression_test_complete.yml | 完全自動回帰テスト（削除→ビルド→デプロイ→バージョンテスト） |
| deploy_k8s_complete.yml | K3s+ArgoCD+アプリ構築（`start_all` のステップ1） |
| install_k3s_and_argocd.yml | K3s + ArgoCD 単独インストール |
| deploy_app_version_gitops.yml | GitOps バージョンアップグレード |
| rollback_app_version_gitops.yml | GitOps バージョンロールバック |

### Gitea

| Playbook | 用途 |
|----------|------|
| install_gitea.yml | Gitea インストール（単独追加可能） |
| uninstall_gitea.yml | Gitea 削除（`-e purge_data=true` でデータも削除） |
| gitea_regression_test.yml | バージョンアップ・バージョンダウン回帰テスト |

### ビルドツール

| Playbook | 用途 |
|----------|------|
| install_build_tools.yml | Java 21 / Maven / Node.js インストール |
| uninstall_build_tools.yml | Java / Maven / Node.js 削除 |

## 主要コマンド

### Kubernetesクラスタ管理

```bash
# 全 Namespace の Pod 確認
sudo /usr/local/bin/k3s kubectl get pods -A

# サービス確認
sudo /usr/local/bin/k3s kubectl get svc -A

# ArgoCD Application 状態確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd \
  -o jsonpath='{.status.sync.status}/{.status.health.status}'
```

### Gitea コンテナ管理

```bash
# コンテナ状態確認
podman ps | grep gitea

# ログ確認
podman logs gitea

# コンテナ再起動
systemctl restart container-gitea
```

### ログ確認

```bash
# Backend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend

# Frontend ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-frontend

# ArgoCD Server ログ
sudo /usr/local/bin/k3s kubectl logs -f deployment/argocd-server -n argocd
```

## スクラップビルド（完全削除と再構築）

### 方法1: Ansible playbook による一括削除・再構築（推奨）

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# 全削除（データ保持）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml

# 全削除（データも含めて完全削除）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"

# 削除後すぐに再構築
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

**削除対象**:
- socat ポート転送 systemd サービス
- Gitea コンテナ / systemd サービス / イメージ
- K3s（ArgoCD・全 K8s ワークロードを含む）
- コンテナイメージ（orgmgmt-backend/frontend, gitea 等）
- ファイアウォールルール
- データディレクトリ（`purge_data=true` 時のみ）
- ビルドツール（`remove_build_tools=true` 時のみ）

### 方法2: 回帰テストによる再構築

削除→ビルド→デプロイ→バージョン検証まで一括実行：

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

### 方法3: 手動による完全削除

#### K3s アンインストール

```bash
sudo /usr/local/bin/k3s-uninstall.sh
sudo rm -rf /etc/rancher/ /var/lib/rancher/ ~/.kube/
```

#### socat サービス停止・削除

```bash
sudo systemctl stop socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard
sudo systemctl disable socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard
sudo rm -f /etc/systemd/system/socat-*.service
sudo systemctl daemon-reload
```

#### Gitea 削除

```bash
podman stop gitea && podman rm gitea
systemctl stop container-gitea && systemctl disable container-gitea
rm -f /etc/systemd/system/container-gitea.service
rm -rf /var/lib/gitea
```

#### コンテナリソース削除

```bash
podman system prune -af --volumes
```

## トラブルシューティング

### ArgoCD Application が OutOfSync

```bash
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge \
  -p '{"operation": {"sync": {"prune": true}}}'
```

### Pod が起動しない

```bash
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### Gitea が起動しない

```bash
# ログ確認
podman logs gitea

# よくある原因:
# 1. ディレクトリ権限 → chown -R 1000:1000 /var/lib/gitea
# 2. SELinux → chcon -Rt container_file_t /var/lib/gitea
# 3. ポート競合 → ss -tlnp | grep 3001

# 再インストール
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
```

### ansible-playbook が見つからない

```bash
# システム全体にインストール
sudo python3 -m pip install ansible
sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook

# 確認
which ansible-playbook
```

### システム全体のリセット

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

## 技術スタック

### インフラストラクチャ
- **K3s v1.34.3** (Kubernetes v1.34.3)
- **ArgoCD v2.10.0** (GitOps CD)
- **Kustomize** (Built-in K8s)
- **Gitea 1.22** (Git Server, Podman コンテナ)
- **PostgreSQL 16 Alpine**
- **Redis 7 Alpine**

### Backend
- **Java 21** (OpenJDK)
- **Spring Boot 3.2.1**
- **Spring Data JPA** (Hibernate)
- **Flyway 10** (Database Migration)
- **Maven 3.9.6** (Build Tool)

### Frontend
- **React 18.2.0**
- **Vite 5** (Build Tool)
- **Axios 1.6.5** (HTTP Client)
- **Nginx Alpine** (Web Server)
- **Node.js 20.x** (Runtime)

### デプロイ・運用
- **Ansible 2.15+** (IaC、`import_playbook` によるサブプレイブック呼び出し)
- **Docker / Podman** (コンテナビルド・実行、`environment.yml` で切替可能)
- **socat** (Port Forwarding)
- **systemd** (Service Management)
- **iptables** (Firewall Management)

## バージョン

**Current Version**: 1.1.0

**Git Tags**:
- `argocd-regression-v1.0.0`: ベースバージョン
- `argocd-regression-v1.1.0`: System Information機能追加

**最終更新**: 2026-02-20

## ドキュメント

- **[ansible/README.md](ansible/README.md)**: Ansible Playbook 詳細リファレンス

## リポジトリ情報

- **Repository**: https://github.com/shiftrepo/aws
- **Path**: container/claudecode/ArgoCD
- **License**: Private

---

**完全自動化されたGitOps継続的デプロイメント + Gitea Git サーバー**
1コマンドで環境構築からバージョン管理まで完全自動化
