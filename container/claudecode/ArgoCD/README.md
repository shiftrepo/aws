# Organization Management System - ArgoCD GitOps Deployment

Kubernetes（K3s）+ ArgoCD GitOps + Kustomize + Gitea による組織管理システムの完全自動デプロイメント・バージョン管理

## 目次

- [概要](#概要)
- [クイックスタート](#クイックスタート)
- [環境設定](#環境設定)
- [Playbook 一覧](#playbook-一覧)
- [Gitea Git サーバー](#gitea-git-サーバー)
- [GitOps バージョン管理](#gitops-バージョン管理)
- [完全自動回帰テスト](#完全自動回帰テスト)
- [サービス一覧・アクセス方法](#サービス一覧アクセス方法)
- [アーキテクチャ](#アーキテクチャ)
- [主要コマンド](#主要コマンド)
- [トラブルシューティング](#トラブルシューティング)
- [技術スタック](#技術スタック)

---

## 概要

### システム構成

| コンポーネント | バージョン | 実行場所 | 説明 |
|--------------|----------|---------|------|
| **K3s** | v1.34.3 | ホスト | 軽量 Kubernetes |
| **ArgoCD** | v2.10.0 | K3s Pod | GitOps 継続的デプロイメント |
| **Kustomize** | built-in | K3s | Kubernetes ネイティブ構成管理 |
| **PostgreSQL** | 16-alpine | K3s Pod | データベース |
| **Redis** | 7-alpine | K3s Pod | セッション管理・キャッシュ |
| **orgmgmt-backend** | Spring Boot 3.2.1 + Java 21 | K3s Pod | REST API（2 レプリカ） |
| **orgmgmt-frontend** | React 18 + Vite + Nginx | K3s Pod | Web UI（2 レプリカ） |
| **Gitea** | 1.22 | Podman コンテナ | オンプレミス Git サーバー |
| **Kubernetes Dashboard** | v2.7.0 | K3s Pod | K8s 管理 UI |

### 前提条件

| 項目 | 要件 |
|------|------|
| OS | Fedora / RHEL 9 / CentOS Stream 9 |
| CPU | 2コア以上（推奨: 4コア） |
| メモリ | 4GB以上（推奨: 8GB） |
| ディスク | 20GB以上の空き容量 |
| ネットワーク | インターネット接続必須 |

Ansible が自動インストールするもの：K3s、ArgoCD、Java 21、Maven、Node.js、socat

---

## クイックスタート

### Ansible インストール（初回のみ）

```bash
sudo python3 -m pip install ansible
sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook
```

### リポジトリクローン

```bash
git clone https://github.com/shiftrepo/aws.git /root/aws.git
cd /root/aws.git/container/claudecode/ArgoCD/ansible
```

### 全サービス一括起動（K3s + ArgoCD + アプリ + Gitea）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

`start_all.yml` は以下を順番に実行します：

1. `deploy_k8s_complete.yml` — K3s / ArgoCD / ビルド / デプロイ / socat / Dashboard
2. `install_gitea.yml` — Gitea（`features.gitea_enabled: true` の場合のみ）

### K3s + アプリのみ（回帰テスト付き）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

> **注意**: `deploy_regression_test_complete.yml` は K3s・ArgoCD・アプリのバージョン回帰テストのみです。**Gitea は含まれません**。Gitea も含めて一括起動するには `start_all.yml` を使用してください。

### 全サービス一括削除

```bash
# データ・ビルドツールは保持
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml

# データも削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"

# データ + ビルドツールも削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true remove_build_tools=true"
```

---

## 環境設定

### 設定ファイル

**`ansible/config/environment.yml` が唯一の設定ファイルです。** k8s マニフェストや `argocd-application.yaml` を直接編集する必要はありません。

```yaml
network:
  external_ip: "10.0.1.84"    # 空 "" にすると ansible_default_ipv4.address を自動使用

directories:
  base_dir: "/root/aws.git/container/claudecode/ArgoCD"

kubernetes:
  k3s_version: "v1.34.3+k3s1"

git:
  repository_url: "https://github.com/shiftrepo/aws.git"
  branch: "main"
  manifests_path: "container/claudecode/ArgoCD/k8s-manifests/overlays"

argocd:
  version: "v2.10.0"
  namespace: "argocd"

ports:
  frontend: 5006
  backend: 8083
  argocd_https: 8082
  argocd_http: 8000
  dashboard: 3000

containers:
  runtime: "podman"            # "docker" に変更すると Docker を使用

application:
  version: "1.1.0"

features:
  argocd_enabled: true
  dashboard_enabled: true
  gitea_enabled: true          # false にすると Gitea をスキップ

gitea:
  version: "1.22"
  port: 3001
  ssh_port: 2222
  data_dir: "/var/lib/gitea"
  container_name: "gitea"
  admin:
    username: "gitea_admin"
    password: "GiteaAdmin123!"
    email: "admin@gitea.local"
```

### 別環境へのデプロイ（チェックリスト）

```
[ ] 1. リポジトリをクローン
       git clone https://github.com/shiftrepo/aws.git /root/aws.git

[ ] 2. ansible/config/environment.yml を編集
       - directories.base_dir : クローン先が異なる場合は変更
       - network.external_ip  : 固定したい場合のみ設定（空 = 自動）
       - git.repository_url   : フォーク先の場合は変更
       - database.password    : 本番環境では必ず変更

[ ] 3. Ansible をインストール
       sudo python3 -m pip install ansible
       sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook

[ ] 4. 全サービス一括起動
       cd .../ansible
       ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

---

## Playbook 一覧

### 起動・削除

| Playbook | 内容 |
|----------|------|
| **start_all.yml** | **全サービス一括起動（推奨）** `import_playbook` で deploy_k8s_complete → install_gitea を順次実行 |
| **uninstall_all.yml** | **全サービス一括削除** socat / Gitea / K3s / イメージ / データ（オプション）/ ビルドツール（オプション） |

### K3s / アプリ

| Playbook | 内容 |
|----------|------|
| **deploy_regression_test_complete.yml** | 完全自動回帰テスト。K3s 削除 → v1.0.0/v1.1.0 ビルド → K3s 構築 → バージョンアップ → ロールバック → 再アップグレード。**Gitea は含まない** |
| **deploy_k8s_complete.yml** | K3s + ArgoCD + ビルド + デプロイ + socat + Dashboard を一括構築 |
| **install_k3s_and_argocd.yml** | K3s + ArgoCD 単独インストール |
| **deploy_app_version_gitops.yml** | ArgoCD Application path を変更してバージョンアップグレード（GitOps） |
| **rollback_app_version_gitops.yml** | ArgoCD Application path を変更してバージョンロールバック（GitOps） |

### Gitea

| Playbook | 内容 |
|----------|------|
| **install_gitea.yml** | Gitea インストール。`gitea_enabled: false` の場合はスキップ（失敗しない）。K3s が無くても単独で実行可能 |
| **uninstall_gitea.yml** | Gitea 削除。`-e purge_data=true` でデータも削除 |
| **gitea_regression_test.yml** | Gitea バージョンアップ（1.21→1.22）・バージョンダウン（1.22→1.21）とデータ永続性を自動検証 |

### ビルドツール

| Playbook | 内容 |
|----------|------|
| **install_build_tools.yml** | Java 21 / Maven 3.9.6 / Node.js 20 をインストール |
| **uninstall_build_tools.yml** | Java / Maven / Node.js を削除 |

### 主要オプション

```bash
# バージョン指定
-e "app_version=1.1.0"
-e "target_version=1.0.0"

# Gitea バージョン指定（gitea_regression_test.yml）
-e "test_version_old=1.21 test_version_new=1.22"

# 削除オプション（uninstall_all.yml / uninstall_gitea.yml）
-e "purge_data=true"           # データディレクトリも削除
-e "remove_build_tools=true"   # ビルドツールも削除（uninstall_all.yml のみ）
```

---

## Gitea Git サーバー

### 単独インストール・削除

K3s が起動していなくても Gitea だけを単独で追加・削除できます。

```bash
# インストール（environment.yml の gitea_enabled: true が必要）
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml

# 削除（データ保持）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml

# 完全削除（データも削除）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml -e "purge_data=true"
```

### バージョン回帰テスト

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
Phase 2: 旧・新バージョン イメージ取得
Phase 3: 旧バージョン (1.21) インストール・管理者作成
Phase 4: 動作確認 + テストデータ作成（Organization / Repository）
Phase 5: バージョンアップ → 新バージョン (1.22)
Phase 6: 新バージョン確認 + データ保持確認（ID 一致チェック）
Phase 7: バージョンダウン → 旧バージョン (1.21)
Phase 8: 旧バージョン確認 + データ保持確認
Phase 9: 全テスト結果サマリー
```

### アクセス情報

| 項目 | デフォルト値 |
|------|------------|
| Web UI | `http://<HOST_IP>:3001` |
| SSH | `<HOST_IP>:2222` |
| 管理者ユーザー | `gitea_admin` |
| 管理者パスワード | `GiteaAdmin123!`（environment.yml で変更可） |

---

## GitOps バージョン管理

### Kustomize 構造

```
k8s-manifests/
├── base/                     # 共通マニフェスト（image: latest）
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   └── kustomization.yaml
└── overlays/
    ├── v1.0.0/
    │   └── kustomization.yaml    # newTag: "1.0.0"
    └── v1.1.0/
        └── kustomization.yaml    # newTag: "1.1.0"
```

### バージョンアップグレード（GitOps）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml \
  -e "app_version=1.1.0"
```

ArgoCD Application の path を `overlays/v1.1.0` に変更 → ArgoCD が自動同期 → ローリングアップデート

### バージョンロールバック（GitOps）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml \
  -e "target_version=1.0.0"
```

### バージョン履歴

```bash
cat /root/app-version-history.txt
```

---

## 完全自動回帰テスト

K3s 削除からバージョンアップ/ダウンテストまでを一括実行します。**Gitea は含まれません**。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

### テストフロー

```
Phase 1 : 既存環境を完全削除
Phase 2 : v1.0.0 ビルド (tag: argocd-regression-v1.0.0)
Phase 3 : v1.1.0 ビルド (branch: main)
Phase 3.5: 環境依存マニフェスト準備（externalIPs パッチ）
Phase 4 : K3s + ArgoCD インストール
Phase 5 : v1.0.0 / v1.1.0 イメージを K3s へインポート
Phase 6 : v1.0.0 初期デプロイ
Phase 7 : アップグレード v1.0.0 → v1.1.0（GitOps）
Phase 8 : ロールバック v1.1.0 → v1.0.0（GitOps）
Phase 9 : 再アップグレード v1.0.0 → v1.1.0（GitOps）
Phase 10: 最終確認（ArgoCD 状態・Deployment・バージョン履歴）
```

### タグ指定で特定フェーズのみ実行

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml \
  --tags=cleanup

# 利用可能なタグ:
# cleanup, build-v1.0.0, build-v1.1.0, prepare-manifests,
# install-k3s, import-images, deploy-v1.0.0,
# upgrade-test, rollback-test, reupgrade-test, verification
```

---

## サービス一覧・アクセス方法

### K3s 内サービス

| サービス | ポート | レプリカ | 説明 |
|---------|--------|---------|------|
| orgmgmt-frontend | 5006 | 2 | React Web UI |
| orgmgmt-backend | 8083 | 2 | Spring Boot REST API |
| postgres | 5432（K3s 内部） | 1 | PostgreSQL 16 |
| redis | 6379（K3s 内部） | 1 | Redis 7 |
| ArgoCD Server | 8082 (HTTPS) / 8000 (HTTP) | — | GitOps 管理 UI |
| Kubernetes Dashboard | 3000 | — | K8s 管理 UI |

### Podman コンテナ

| サービス | ポート | 説明 |
|---------|--------|------|
| Gitea | 3001 (HTTP) / 2222 (SSH) | Git サーバー |

### アクセス URL

```bash
# orgmgmt フロントエンド
http://<HOST_IP>:5006

# orgmgmt バックエンド（ヘルスチェック）
curl http://<HOST_IP>:8083/actuator/health

# ArgoCD Web UI
https://<HOST_IP>:8082
cat /root/argocd-credentials.txt   # 認証情報

# Kubernetes Dashboard（EC2 の場合はパブリック DNS 名が必要）
https://<PUBLIC_DNS>:3000
cat /root/k8s-dashboard-token.txt  # トークン

# Gitea Web UI
http://<HOST_IP>:3001
# Username: gitea_admin / Password: GiteaAdmin123!

# Gitea API
curl http://<HOST_IP>:3001/api/v1/version
```

---

## アーキテクチャ

### システム構成図

```
                     外部アクセス
                         │
    ┌────────────────────┼──────────────────────┐
    │                    │                      │
 :3001/:2222         :5006/:8083           :8082/:8000/:3000
    │                    │                      │
┌───┴────┐    ┌──────────┴───────────────────────┴──┐
│ Gitea  │    │      socat Port Forwarding           │
│(Podman)│    │  (systemd services × 5)              │
└────────┘    └──────────┬───────────────────────────┘
                         │
            ┌────────────┴─────────────────────┐
            │     Kubernetes (K3s) Cluster      │
            │                                  │
            ├─ orgmgmt-frontend (×2)            │
            ├─ orgmgmt-backend  (×2)            │
            ├─ postgres         (×1)            │
            ├─ redis            (×1)            │
            ├─ argocd           (×7)            │
            └─ kubernetes-dashboard             │
            └──────────────────────────────────┘
```

### GitOps フロー

```
GitHub Repository
  └─ k8s-manifests/overlays/v1.0.0 または v1.1.0
            │
            ├─ ArgoCD が 3分ごとに自動検出
            ├─ 差分があれば自動同期（Auto Sync）
            ├─ 手動変更を自動修復（Self Heal）
            └─ 不要リソースを自動削除（Prune）
```

### ディレクトリ構造

```
ansible/
├── config/environment.yml          ← 唯一の設定ファイル
├── group_vars/all.yml               ← 変数マッピング
├── inventory/hosts.yml
└── playbooks/
    ├── start_all.yml                ← 全サービス一括起動
    ├── uninstall_all.yml            ← 全サービス一括削除
    ├── deploy_regression_test_complete.yml  ← K3s 回帰テスト（Gitea 除く）
    ├── deploy_k8s_complete.yml
    ├── install_k3s_and_argocd.yml
    ├── install_build_tools.yml
    ├── uninstall_build_tools.yml
    ├── install_gitea.yml            ← Gitea インストール（単独可）
    ├── uninstall_gitea.yml          ← Gitea 削除
    ├── gitea_regression_test.yml    ← Gitea バージョン回帰テスト
    ├── deploy_app_version_gitops.yml
    └── rollback_app_version_gitops.yml
k8s-manifests/
├── base/
└── overlays/
    ├── v1.0.0/
    └── v1.1.0/
app/
├── backend/   (Spring Boot)
└── frontend/  (React)
argocd-application.yaml
```

---

## 主要コマンド

### K3s / Kubernetes

```bash
# Pod 一覧
sudo /usr/local/bin/k3s kubectl get pods -A

# Service 一覧
sudo /usr/local/bin/k3s kubectl get svc -A

# ArgoCD Application 状態
sudo /usr/local/bin/k3s kubectl get application orgmgmt-app -n argocd \
  -o jsonpath='{.status.sync.status}/{.status.health.status}'

# ログ確認
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-backend
sudo /usr/local/bin/k3s kubectl logs -f deployment/orgmgmt-frontend
```

### Gitea

```bash
# コンテナ状態
podman ps | grep gitea
podman logs gitea

# systemd サービス確認
systemctl status container-gitea
```

### ArgoCD 手動同期

```bash
sudo /usr/local/bin/k3s kubectl patch application orgmgmt-app -n argocd \
  --type merge -p '{"operation": {"sync": {"prune": true}}}'
```

---

## トラブルシューティング

### Pod が起動しない

```bash
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### Gitea が起動しない

```bash
podman logs gitea
# よくある原因: ディレクトリ権限（chown -R 1000:1000 /var/lib/gitea）
#               SELinux（chcon -Rt container_file_t /var/lib/gitea）

# 再インストール
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
```

### ansible-playbook が見つからない

```bash
sudo python3 -m pip install ansible
sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook
```

### システム全体のリセット

```bash
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

---

## 技術スタック

### インフラ
- K3s v1.34.3 / ArgoCD v2.10.0 / Kustomize / Gitea 1.22
- PostgreSQL 16-alpine / Redis 7-alpine
- socat（ポート転送）/ systemd / iptables

### バックエンド
- Java 21 / Spring Boot 3.2.1 / Spring Data JPA / Flyway 10 / Maven 3.9.6

### フロントエンド
- React 18.2.0 / Vite 5 / Axios 1.6.5 / Nginx Alpine / Node.js 20.x

### 自動化
- Ansible 2.15+（`import_playbook` でサブプレイブックを呼び出し）
- Docker / Podman（`environment.yml` の `containers.runtime` で切替）

---

## バージョン

**Current Version**: 1.1.0
**Git Tags**: `argocd-regression-v1.0.0`（ベース）、`argocd-regression-v1.1.0`（System Information 追加）
**最終更新**: 2026-02-20

## リポジトリ

- **Repository**: https://github.com/shiftrepo/aws
- **Path**: container/claudecode/ArgoCD
