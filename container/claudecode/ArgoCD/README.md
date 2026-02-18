# Organization Management System - ArgoCD GitOps Deployment

Kubernetes（K3s）+ ArgoCD GitOps + Kustomizeによる組織管理システムの完全自動デプロイメント・バージョン管理

## 目次

- [概要](#概要)
- [環境依存パラメータ](#環境依存パラメータ)
- [Ansibleのインストール](#ansibleのインストール)
- [クイックスタート](#クイックスタート)
- [完全自動回帰テスト](#完全自動回帰テスト)
- [GitOpsバージョン管理](#gitopsバージョン管理)
- [サービス一覧](#サービス一覧)
- [アクセス方法](#アクセス方法)
- [アーキテクチャ](#アーキテクチャ)
- [主要コマンド](#主要コマンド)
- [スクラップビルド（完全削除と再構築）](#スクラップビルド完全削除と再構築)
- [トラブルシューティング](#トラブルシューティング)
- [技術スタック](#技術スタック)

## 概要

### 特徴

- **完全自動化**: 1コマンドで環境削除→構築→回帰テスト実行
- **GitOps準拠**: Kustomize overlaysによる宣言的バージョン管理
- **両バージョン対応**: v1.0.0とv1.1.0を自動ビルド・インポート
- **ゼロダウンタイム**: ローリングアップデートによる無停止デプロイ
- **完全なポータビリティ**: どの環境でも同一の手順で実行可能

### システム構成

| コンポーネント | バージョン | 説明 |
|--------------|----------|------|
| **K3s** | v1.34.3 | 軽量Kubernetesディストリビューション |
| **ArgoCD** | v2.10.0 | GitOps継続的デプロイメント |
| **Kustomize** | Built-in | Kubernetes ネイティブ構成管理 |
| **PostgreSQL** | 16-alpine | リレーショナルデータベース |
| **Redis** | 7-alpine | セッション管理・キャッシュ |
| **Backend** | Spring Boot 3.2.1 + Java 21 | REST API (2レプリカ) |
| **Frontend** | React 18 + Vite | Web UI (2レプリカ) |

### 前提条件

| 項目 | 要件 |
|------|------|
| OS | Amazon Linux 2023 / RHEL 9 / CentOS 9 |
| CPU | 2コア以上（推奨: 4コア） |
| メモリ | 4GB以上（推奨: 8GB） |
| ディスク | 20GB以上の空き容量 |
| ネットワーク | インターネット接続必須 |

**必要なソフトウェアはAnsibleが自動インストール**します：
- K3s, ArgoCD, Maven, Node.js, Podman, socat

## 環境依存パラメータ

別のFedora環境で本プロジェクトを動かす際に変更が必要なパラメータを一覧化します。

### 変更必須パラメータ

環境ごとに必ず変更が必要な項目です。

#### ネットワーク（IPアドレス）

| パラメータ | デフォルト値 | 変更対象ファイル | 説明 |
|-----------|------------|----------------|------|
| `externalIPs` | `10.0.1.200` | `k8s-manifests/base/backend-service.yaml` | バックエンド外部公開IP |
| `externalIPs` | `10.0.1.200` | `k8s-manifests/base/frontend-service.yaml` | フロントエンド外部公開IP |
| `host` | `ec2-13-219-96-72.compute-1.amazonaws.com` | `k8s-manifests/base/frontend-ingress.yaml` | IngressのFQDN（DNS名） |

変更方法（各サービスYAMLの `spec.externalIPs`）:
```yaml
spec:
  externalIPs:
    - 192.168.1.100   # ← 実際のホストIPに変更
```

#### Gitリポジトリ

| パラメータ | デフォルト値 | 変更対象ファイル | 説明 |
|-----------|------------|----------------|------|
| `repoURL` | `https://github.com/shiftrepo/aws.git` | `argocd-application.yaml` | ArgoCDが参照するGitリポジトリURL |
| `targetRevision` | `main` | `argocd-application.yaml` | 参照ブランチ |
| `path` | `container/claudecode/ArgoCD/k8s-manifests/overlays/v1.0.0` | `argocd-application.yaml` | マニフェストのリポジトリ内パス |

#### プロジェクトルートパス

| パラメータ | デフォルト値 | 変更対象ファイル | 説明 |
|-----------|------------|----------------|------|
| `project_root` | `/root/aws.git/container/claudecode/ArgoCD` | `ansible/playbooks/deploy_app_version.yml` 他 | クローン先ディレクトリ |
| `version_history_file` | `/root/app-version-history.txt` | 各Ansible playbook | バージョン履歴ファイルパス |
| `kubeconfig_path` | `/etc/rancher/k3s/k3s.yaml` | `ansible/playbooks/install_k3s_and_argocd.yml` | K3s kubeconfigパス |

---

### 変更推奨パラメータ（セキュリティ）

本番・検証環境では必ず変更してください。

#### データベース認証情報

同一の値が複数ファイルに存在します。すべて一致させる必要があります。

| パラメータ | デフォルト値 | 変更対象ファイル |
|-----------|------------|----------------|
| `POSTGRES_USER` / `SPRING_DATASOURCE_USERNAME` | `orgmgmt_user` | `k8s-manifests/base/postgres-deployment.yaml`<br>`k8s-manifests/base/backend-deployment.yaml`<br>`app/backend/src/main/resources/application.yml` |
| `POSTGRES_PASSWORD` / `SPRING_DATASOURCE_PASSWORD` | `SecurePassword123!` | 同上 |
| `POSTGRES_DB` | `orgmgmt` | `k8s-manifests/base/postgres-deployment.yaml`<br>`app/backend/src/main/resources/application.yml` |

---

### 変更任意パラメータ（ポート番号）

ポートが競合する場合のみ変更してください。

#### 外部公開ポート

| サービス | デフォルトポート | 変更対象ファイル |
|---------|---------------|----------------|
| Frontend | `5006` | `k8s-manifests/base/frontend-service.yaml`<br>`ansible/playbooks/deploy_k8s_complete.yml` |
| Backend | `8083` | `k8s-manifests/base/backend-service.yaml`<br>`ansible/playbooks/deploy_k8s_complete.yml` |
| ArgoCD HTTPS | `8082` | `ansible/playbooks/install_k3s_and_argocd.yml`<br>`ansible/playbooks/deploy_k8s_complete.yml` |
| ArgoCD HTTP | `8000` | 同上 |
| K8s Dashboard | `3000` | `ansible/playbooks/deploy_k8s_complete.yml` |

#### 内部ポート（通常変更不要）

| サービス | ポート | 備考 |
|---------|--------|------|
| Backend (コンテナ内) | `8080` | `app/backend/src/main/resources/application.yml` |
| Frontend / Nginx (コンテナ内) | `80` | `app/frontend/Dockerfile` |
| PostgreSQL | `5432` | K8s内部通信 |
| Redis | `6379` | K8s内部通信 |

---

### 変更任意パラメータ（バージョン）

使用するミドルウェアのバージョンを変更する場合に編集してください。

| ソフトウェア | デフォルト値 | 変更対象ファイル |
|------------|------------|----------------|
| K3s | `v1.34.3+k3s1` | `ansible/playbooks/install_k3s_and_argocd.yml` |
| ArgoCD | `v2.10.0` | `ansible/playbooks/install_k3s_and_argocd.yml` |
| PostgreSQL イメージ | `postgres:16-alpine` | `k8s-manifests/base/postgres-deployment.yaml` |
| Redis イメージ | `redis:7-alpine` | `k8s-manifests/base/redis-deployment.yaml` |
| Java (Backend ベースイメージ) | `eclipse-temurin:21-jre-alpine` | `app/backend/Dockerfile` |
| Maven | `3.9.6` | `ansible/playbooks/install_build_tools.yml` |
| Node.js | `20` | `ansible/playbooks/install_build_tools.yml` |

---

### 変更任意パラメータ（リソース制限）

ホストのスペックに合わせて調整してください。

| コンポーネント | requests (CPU/Memory) | limits (CPU/Memory) | 変更対象ファイル |
|-------------|----------------------|--------------------|----|
| Backend | `250m` / `256Mi` | `500m` / `512Mi` | `k8s-manifests/base/backend-deployment.yaml` |
| Frontend | `100m` / `64Mi` | `200m` / `128Mi` | `k8s-manifests/base/frontend-deployment.yaml` |
| PostgreSQL | `-` / `256Mi` | `-` / `512Mi` | `k8s-manifests/base/postgres-deployment.yaml` |
| JVM (Backend) | `-Xms256m` | `-Xmx512m` | `app/backend/Dockerfile` |

---

### 別環境へのデプロイ手順（チェックリスト）

新しいFedora環境にデプロイする際の手順です。

```
[ ] 1. リポジトリをクローン
       git clone <repoURL> /root/aws.git

[ ] 2. IPアドレスを変更
       k8s-manifests/base/backend-service.yaml  → externalIPs
       k8s-manifests/base/frontend-service.yaml → externalIPs

[ ] 3. Ingressホスト名を変更（DNS名でアクセスする場合）
       k8s-manifests/base/frontend-ingress.yaml → host

[ ] 4. argocd-application.yaml を変更
       repoURL       → 自環境のGitリポジトリURL
       targetRevision → 使用するブランチ名

[ ] 5. DBパスワードを変更（本番環境の場合）
       k8s-manifests/base/postgres-deployment.yaml
       k8s-manifests/base/backend-deployment.yaml
       app/backend/src/main/resources/application.yml

[ ] 6. Ansibleをインストール（未インストールの場合）
       sudo dnf install -y ansible

[ ] 7. 完全自動回帰テストを実行
       cd /root/aws.git/container/claudecode/ArgoCD/ansible
       ansible-playbook playbooks/deploy_regression_test_complete.yml
```

## Ansibleのインストール

Ansibleはすべての自動化playbook実行に必要です。FedoraベースのOSでの手順を示します。

### Fedora

```bash
# 標準リポジトリからインストール
sudo dnf install -y ansible

# バージョン確認
ansible --version
```

### Fedora / RHEL系（pip3を使用）

特定バージョンのAnsibleが必要な場合やパッケージ版が古い場合はpip3を使用します。

```bash
# pip3のインストール
sudo dnf install -y python3-pip

# Ansibleインストール（ユーザーローカル）
pip3 install --user ansible

# PATHに追加
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# バージョン確認
ansible --version
```

### インストール確認

```bash
# バージョン確認
ansible --version
# ansible [core 2.14.x]  (2.14以上推奨)

# playbookコマンド確認
ansible-playbook --version

# localhostへの接続テスト
ansible localhost -m ping
# localhost | SUCCESS => { "ping": "pong" }
```

### 注意事項

- Ansible **2.14以上**が必要です
- rootユーザーまたはsudo権限が必要です
- Python **3.9以上**が前提です（Fedoraはデフォルトで満たします）

## クイックスタート

### リポジトリクローン

```bash
cd /root
git clone https://github.com/shiftrepo/aws.git
cd /root/aws.git/container/claudecode/ArgoCD
```

### 完全自動回帰テスト（推奨）

**すべての操作を1コマンドで実行**:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_regression_test_complete.yml
```

**所要時間**: 約15-20分

**実行内容**:
1. **環境削除**: K3s、Podman、履歴ファイルの完全削除
2. **v1.0.0ビルド**: Git tag `argocd-regression-v1.0.0` から自動ビルド
3. **v1.1.0ビルド**: mainブランチから自動ビルド
4. **K3s + ArgoCD構築**: 新規環境構築
5. **イメージインポート**: v1.0.0とv1.1.0の両方をK3sにインポート
6. **v1.0.0初期デプロイ**: Kustomize overlays/v1.0.0でデプロイ
7. **アップグレードテスト**: v1.0.0 → v1.1.0 (GitOps)
8. **ロールバックテスト**: v1.1.0 → v1.0.0 (GitOps)
9. **再アップグレードテスト**: v1.0.0 → v1.1.0 (GitOps)
10. **最終確認**: ステータス、履歴、サマリー表示

**実行結果例**:
```
PLAY RECAP
========
localhost: ok=48  changed=36  unreachable=0  failed=0  skipped=0

ArgoCD Status: Synced/Healthy

All Tests Passed:
  ✅ v1.0.0 and v1.1.0 images built
  ✅ K3s and ArgoCD installed
  ✅ Initial v1.0.0 deployment
  ✅ Upgrade v1.0.0 → v1.1.0
  ✅ Rollback v1.1.0 → v1.0.0
  ✅ Re-upgrade v1.0.0 → v1.1.0
```

### 個別構築（詳細制御が必要な場合）

#### 1. 初回環境構築のみ

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/install_k3s_and_argocd.yml
```

#### 2. アプリケーションデプロイのみ

```bash
ansible-playbook playbooks/deploy_k8s_complete.yml
```

## 完全自動回帰テスト

### 実行方法

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_regression_test_complete.yml
```

### テストフロー

```
Phase 1: 環境削除
  └─> K3s uninstall
  └─> Podman cleanup
  └─> 履歴ファイル削除

Phase 2-3: 両バージョンビルド
  └─> v1.0.0 (tag: argocd-regression-v1.0.0)
      ├─> Backend Maven build
      ├─> Frontend npm build
      └─> Podman image build
  └─> v1.1.0 (branch: main)
      ├─> Backend Maven build
      ├─> Frontend npm build
      └─> Podman image build

Phase 4: K3s + ArgoCD構築
  └─> K3s installation
  └─> ArgoCD installation
  └─> Wait for ready

Phase 5: イメージインポート
  └─> Export to tar files
  └─> Import to K3s containerd
  └─> Verify both versions

Phase 6: v1.0.0初期デプロイ
  └─> Apply Kustomize overlays/v1.0.0
  └─> Wait for pods ready
  └─> Apply ArgoCD Application
  └─> Wait for sync

Phase 7-9: バージョン変更テスト
  └─> Upgrade v1.0.0 → v1.1.0 (GitOps)
  └─> Rollback v1.1.0 → v1.0.0 (GitOps)
  └─> Re-upgrade v1.0.0 → v1.1.0 (GitOps)

Phase 10: 最終確認
  └─> ArgoCD status
  └─> Deployments
  └─> Pods
  └─> Version history
```

### タグベース実行

特定のフェーズのみ実行する場合:

```bash
# 環境削除のみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=cleanup

# v1.0.0ビルドのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=build-v1.0.0

# v1.1.0ビルドのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=build-v1.1.0

# K3sインストールのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=install-k3s

# イメージインポートのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=import-images

# 初期デプロイのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=deploy-v1.0.0

# アップグレードテストのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=upgrade-test

# ロールバックテストのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=rollback-test

# 再アップグレードテストのみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=reupgrade-test

# 最終確認のみ
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=verification
```

## GitOpsバージョン管理

### Kustomize構造

```
k8s-manifests/
├── base/                           # 共通ベース
│   ├── backend-deployment.yaml     # image: latest (placeholder)
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml    # image: latest (placeholder)
│   ├── frontend-service.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── v1.0.0/                     # v1.0.0環境
│   │   └── kustomization.yaml     # newTag: "1.0.0"
│   └── v1.1.0/                     # v1.1.0環境
│       └── kustomization.yaml     # newTag: "1.1.0"
```

### バージョン変更の仕組み

**GitOps方式** - ArgoCD Application pathの変更でバージョン切り替え:

```bash
# v1.0.0にロールバック
kubectl patch application orgmgmt-app -n argocd --type merge \
  -p '{"spec":{"source":{"path":"k8s-manifests/overlays/v1.0.0"}}}'

# v1.1.0にアップグレード
kubectl patch application orgmgmt-app -n argocd --type merge \
  -p '{"spec":{"source":{"path":"k8s-manifests/overlays/v1.1.0"}}}'
```

**重要**: `kubectl set image`は使用しません（非GitOps準拠のため）。

### バージョンアップグレード（GitOps方式）

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_app_version_gitops.yml -e "app_version=1.1.0"
```

**処理内容**:
1. ArgoCD Application pathを`overlays/v1.1.0`に変更
2. ArgoCD syncを自動トリガー
3. Kustomizeが`newTag: "1.1.0"`を適用
4. Deploymentがローリングアップデート
5. Health checkで確認

**所要時間**: 約2-3分

### バージョンロールバック（GitOps方式）

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/rollback_app_version_gitops.yml -e "target_version=1.0.0"
```

**処理内容**:
1. ArgoCD Application pathを`overlays/v1.0.0`に変更
2. ArgoCD syncを自動トリガー
3. Kustomizeが`newTag: "1.0.0"`を適用
4. Deploymentがローリングアップデート
5. Health checkで確認

**所要時間**: 約2-3分

### バージョン履歴確認

```bash
cat /root/app-version-history.txt
```

**出力例**:
```
2026-02-07T07:17:09Z | DEPLOY (GitOps) | 1.1.0 | Backend: localhost/orgmgmt-backend:1.1.0, Frontend: localhost/orgmgmt-frontend:1.1.0
2026-02-07T07:17:09Z | ROLLBACK (GitOps) | 1.0.0 | Backend: localhost/orgmgmt-backend:1.0.0, Frontend: localhost/orgmgmt-frontend:1.0.0
2026-02-07T07:17:09Z | DEPLOY (GitOps) | 1.1.0 | Backend: localhost/orgmgmt-backend:1.1.0, Frontend: localhost/orgmgmt-frontend:1.1.0
```

### Gitタグによるバージョン管理

```bash
# 利用可能なバージョンを確認
git tag -l argocd-regression-v*

# 出力例:
# argocd-regression-v1.0.0  <- ベースバージョン
# argocd-regression-v1.1.0  <- System Information機能追加
```

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

### ArgoCD（GitOps管理）

**Web UI**:
```bash
# HTTPS（推奨）
https://10.0.1.200:8082

# HTTP（HTTPSにリダイレクト）
http://10.0.1.200:8000
```

**認証情報**:
```bash
cat /root/argocd-credentials.txt
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

### Kubernetes Dashboard

**⚠️ 重要**: IPアドレスではアクセスできません。EC2インスタンスのパブリックDNS名を使用してください。

```bash
# EC2パブリックDNS名を取得
curl -s http://169.254.169.254/latest/meta-data/public-hostname
# 出力例: ec2-54-172-30-175.compute-1.amazonaws.com

# ブラウザでアクセス
https://ec2-54-172-30-175.compute-1.amazonaws.com:3000/

# トークン取得
cat /root/k8s-dashboard-token.txt
```

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

### GitOps Workflow with Kustomize

```
GitHub Repository
  └─ container/claudecode/ArgoCD/k8s-manifests/
       ├─ base/
       │   ├─ backend-deployment.yaml     (image: latest)
       │   ├─ frontend-deployment.yaml    (image: latest)
       │   └─ kustomization.yaml
       └─ overlays/
           ├─ v1.0.0/
           │   └─ kustomization.yaml      (newTag: "1.0.0")
           └─ v1.1.0/
               └─ kustomization.yaml      (newTag: "1.1.0")
                  │
                  ├─ ArgoCD自動検出（3分ごと）
                  │
                  └─→ Kubernetes Cluster
                       ├─ Backend Deployment (2 replicas, image:1.1.0)
                       ├─ Frontend Deployment (2 replicas, image:1.1.0)
                       ├─ PostgreSQL Deployment (1 replica)
                       └─ Redis Deployment (1 replica)
```

**GitOps機能**:
- **自動同期**: 3分ごとにGitリポジトリをチェック
- **Self Heal**: 手動変更を自動で元に戻す
- **Prune**: マニフェストから削除されたリソースを自動削除
- **Kustomize**: ネイティブサポート（overlaysによるバージョン管理）

### ディレクトリ構造

```
.
├── ansible/
│   └── playbooks/
│       ├── deploy_regression_test_complete.yml  # 完全自動回帰テスト（推奨）
│       ├── deploy_app_version_gitops.yml        # GitOpsアップグレード
│       ├── rollback_app_version_gitops.yml      # GitOpsロールバック
│       ├── install_k3s_and_argocd.yml           # K3s+ArgoCD単独
│       └── install_build_tools.yml              # Maven/Node.js単独
├── k8s-manifests/                               # ArgoCD管理対象
│   ├── base/                                    # Kustomize base
│   │   ├── backend-deployment.yaml
│   │   ├── backend-service.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── frontend-service.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── redis-deployment.yaml
│   │   └── kustomization.yaml
│   └── overlays/                                # Kustomize overlays
│       ├── v1.0.0/
│       │   └── kustomization.yaml               # newTag: "1.0.0"
│       └── v1.1.0/
│           └── kustomization.yaml               # newTag: "1.1.0"
├── app/
│   ├── backend/                                 # Spring Boot
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/
│   └── frontend/                                # React
│       ├── Dockerfile
│       ├── package.json
│       └── src/
├── argocd-application.yaml                      # ArgoCD Application
└── README.md                                    # このファイル
```

## 主要コマンド

### Kubernetesクラスタ管理

```bash
# 全Namespace のPod確認
sudo /usr/local/bin/k3s kubectl get pods -A

# Deployments確認
sudo /usr/local/bin/k3s kubectl get deployments -o wide

# サービス確認
sudo /usr/local/bin/k3s kubectl get svc -A
```

### ArgoCD管理

```bash
# ArgoCD Application確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd

# Application ステータス（簡易）
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd \
  -o jsonpath='{.status.sync.status}/{.status.health.status}'
# 出力例: Synced/Healthy

# 手動同期
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge \
  -p '{"operation": {"sync": {"prune": true}}}'
```

### イメージ確認

```bash
# K3sにインポートされたイメージ確認
sudo /usr/local/bin/k3s crictl images | grep orgmgmt

# 出力例:
# localhost/orgmgmt-backend    1.0.0    xxx    259MB
# localhost/orgmgmt-backend    1.1.0    xxx    268MB
# localhost/orgmgmt-frontend   1.0.0    xxx    64.8MB
# localhost/orgmgmt-frontend   1.1.0    xxx    64.8MB
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

既存環境をすべて削除してゼロから再構築する手順です。

### 方法1: Ansible playbook による一括削除（推奨）

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_regression_test_complete.yml --tags=cleanup
```

削除対象:
- K3s（`k3s-uninstall.sh` を自動実行）
- Podman コンテナ・ボリューム・イメージ
- バージョン履歴ファイル（`/root/app-version-history.txt`）

> 削除後すぐに再構築する場合は `--tags` なしで実行するとフルフローが実行されます。

---

### 方法2: 手動による完全削除

Ansible が使えない場合や、より細かく制御したい場合の手順です。

#### Step 1: K3s アンインストール

```bash
# K3s と関連リソースをすべて削除
sudo /usr/local/bin/k3s-uninstall.sh

# 残存ディレクトリの手動削除
sudo rm -rf /etc/rancher/
sudo rm -rf /var/lib/rancher/
sudo rm -f /usr/local/bin/k3s*
sudo rm -f /usr/local/bin/kubectl
sudo rm -rf ~/.kube/
```

#### Step 2: socat ポートフォワードサービスの停止・削除

```bash
# サービス停止・無効化
sudo systemctl stop socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard
sudo systemctl disable socat-frontend socat-backend socat-argocd-http socat-argocd-https socat-k8s-dashboard

# サービスファイル削除
sudo rm -f /etc/systemd/system/socat-*.service
sudo systemctl daemon-reload
```

#### Step 3: iptables ルールの削除

```bash
# 追加したルールを個別削除
sudo iptables -D INPUT -p tcp --dport 5006 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 8083 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 8082 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 3000 -j ACCEPT

# ルールを永続化ファイルに反映
sudo iptables-save > /etc/sysconfig/iptables
```

#### Step 4: Podman リソースの削除

```bash
# 全コンテナ強制削除
podman rm -af

# 全ボリューム削除
podman volume prune -f

# 全イメージ削除（ビルドキャッシュ含む）
podman system prune -af

# ネットワーク削除
podman network rm argocd-network 2>/dev/null || true
```

#### Step 5: 一時ファイル・生成ファイルの削除

```bash
# イメージ tar ファイル
rm -f /tmp/backend-*.tar /tmp/frontend-*.tar
rm -f /tmp/k3s-install.sh /tmp/argocd-*.yaml

# バージョン履歴・認証情報
rm -f /root/app-version-history.txt
rm -f /root/argocd-credentials.txt
rm -f /root/k8s-dashboard-token.txt
rm -f /root/K3S-ARGOCD-INSTALLATION-REPORT.md
```

#### Step 6: ビルド成果物の削除（再ビルドしたい場合）

```bash
PROJECT_ROOT=/root/aws.git/container/claudecode/ArgoCD

# Mavenビルド成果物
rm -rf ${PROJECT_ROOT}/app/backend/target/

# npmビルド成果物・依存関係
rm -rf ${PROJECT_ROOT}/app/frontend/dist/
rm -rf ${PROJECT_ROOT}/app/frontend/node_modules/

# Playwrightテスト結果
rm -rf ${PROJECT_ROOT}/playwright-tests/test-results/
rm -rf ${PROJECT_ROOT}/playwright-tests/playwright-report/
rm -rf ${PROJECT_ROOT}/playwright-tests/node_modules/
```

---

### 削除確認

削除後、以下のコマンドで確認してください。

```bash
# K3s 削除確認
which k3s 2>/dev/null && echo "残存あり" || echo "OK: k3s削除済み"
ls /etc/rancher/ 2>/dev/null && echo "残存あり" || echo "OK: /etc/rancher削除済み"

# socat サービス確認
systemctl list-units --type=service | grep socat || echo "OK: socatサービスなし"

# ポート開放確認
ss -tlnp | grep -E "5006|8083|8000|8082|3000" || echo "OK: 対象ポートは未使用"

# Podman リソース確認
echo "コンテナ:"; podman ps -a
echo "ボリューム:"; podman volume ls
echo "イメージ:"; podman images | grep orgmgmt || echo "OK: orgmgmtイメージなし"
```

---

### スクラップビルド（削除→再構築を一括実行）

削除と再構築を続けて行う場合:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# 完全削除 → 再構築 → 回帰テストまで一括実行
ansible-playbook playbooks/deploy_regression_test_complete.yml
```

このコマンド1つで以下がすべて自動実行されます：

```
1. 既存環境の完全削除
2. v1.0.0 / v1.1.0 のイメージビルド
3. K3s + ArgoCD の新規インストール
4. イメージのインポート
5. v1.0.0 初期デプロイ
6. v1.1.0 アップグレードテスト
7. v1.0.0 ロールバックテスト
8. v1.1.0 再アップグレードテスト
```

## トラブルシューティング

### ArgoCD Application が OutOfSync

```bash
# Application状態確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd

# 手動同期
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge \
  -p '{"operation": {"sync": {"prune": true}}}'

# syncPolicy確認
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd \
  -o jsonpath='{.spec.syncPolicy}' | jq .
```

### Pod が起動しない

```bash
# Pod状態詳細確認
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>

# イベント確認
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp' | tail -20

# ログ確認
sudo /usr/local/bin/k3s kubectl logs <pod-name>
```

### イメージが見つからない

```bash
# K3sのイメージ確認
sudo /usr/local/bin/k3s crictl images | grep orgmgmt

# イメージが無い場合、再インポート
podman save localhost/orgmgmt-backend:1.1.0 -o /tmp/backend.tar
sudo /usr/local/bin/k3s ctr images import /tmp/backend.tar
```

### システム全体のリセット

```bash
# K3s完全削除
sudo /usr/local/bin/k3s-uninstall.sh

# Podman イメージ削除
podman rmi -af

# バージョン履歴削除
rm -f /root/app-version-history.txt

# 再構築
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_regression_test_complete.yml
```

## Playbook一覧

| Playbook | 用途 | 所要時間 |
|----------|------|---------|
| **deploy_regression_test_complete.yml** | **完全自動回帰テスト（推奨）** | 15-20分 |
| install_k3s_and_argocd.yml | K3s + ArgoCD単独インストール | 3-5分 |
| deploy_app_version_gitops.yml | GitOpsアップグレード | 2-3分 |
| rollback_app_version_gitops.yml | GitOpsロールバック | 2-3分 |
| install_build_tools.yml | Maven/Node.js単独インストール | 2-3分 |

## 技術スタック

### インフラストラクチャ
- **K3s v1.34.3** (Kubernetes v1.34.3)
- **ArgoCD v2.10.0** (GitOps CD)
- **Kustomize** (Built-in K8s)
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
- **Ansible 2.14+** (IaC)
- **Podman** (Container Build)
- **socat** (Port Forwarding)
- **systemd** (Service Management)
- **iptables** (Firewall Management)

## バージョン

**Current Version**: 1.1.0

**Git Tags**:
- `argocd-regression-v1.0.0`: ベースバージョン
- `argocd-regression-v1.1.0`: System Information機能追加

**最終更新**: 2026-02-07

## ドキュメント

- **[CREDENTIALS.md](CREDENTIALS.md)**: 認証情報・アクセスガイド
- **[QUICKSTART.md](QUICKSTART.md)**: クイックスタートガイド
- **[VERSION_UPGRADE.md](VERSION_UPGRADE.md)**: バージョンアップグレード手順

## サポート

### 問題報告

問題や質問がある場合は、GitHubのIssueで報告してください。

### リポジトリ情報

- **Repository**: https://github.com/shiftrepo/aws
- **Path**: container/claudecode/ArgoCD
- **License**: Private

---

**完全自動化されたGitOps継続的デプロイメント**
1コマンドで環境構築からバージョン管理まで完全自動化
