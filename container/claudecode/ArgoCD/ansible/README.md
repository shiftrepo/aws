# Ansible Playbooks リファレンス

K3s / ArgoCD / アプリ / Gitea の構築・削除・バージョン管理・回帰テストを自動化する Ansible Playbook 群です。

## ディレクトリ構造

```
ansible/
├── ansible.cfg
├── config/
│   └── environment.yml          ← 唯一の設定ファイル（環境ごとに編集）
├── group_vars/
│   └── all.yml                  ← environment.yml から Ansible 変数へマッピング
├── inventory/
│   └── hosts.yml                ← localhost 向け inventory
└── playbooks/
    ├── start_all.yml
    ├── uninstall_all.yml
    ├── deploy_regression_test_complete.yml
    ├── deploy_k8s_complete.yml
    ├── install_k3s_and_argocd.yml
    ├── install_build_tools.yml
    ├── uninstall_build_tools.yml
    ├── install_gitea.yml
    ├── uninstall_gitea.yml
    ├── gitea_regression_test.yml
    ├── deploy_app_version.yml
    ├── deploy_app_version_gitops.yml
    ├── rollback_app_version.yml
    └── rollback_app_version_gitops.yml
```

---

## 設定ファイル

### `config/environment.yml`

全 Playbook が読み込む唯一の設定ファイルです。

```yaml
network:
  external_ip: "10.0.1.84"       # 空 "" = ansible_default_ipv4.address を自動使用

directories:
  base_dir: "/root/aws.git/container/claudecode/ArgoCD"
  data_dir: "/var/lib/orgmgmt"
  kubeconfig_path: "/etc/rancher/k3s/k3s.yaml"
  version_history_file: "/root/app-version-history.txt"

kubernetes:
  k3s_version: "v1.34.3+k3s1"

git:
  repository_url: "https://github.com/shiftrepo/aws.git"
  branch: "main"
  manifests_path: "container/claudecode/ArgoCD/k8s-manifests/overlays"

argocd:
  version: "v2.10.0"
  namespace: "argocd"
  application:
    name: "orgmgmt-app"
    initial_version: "1.0.0"
    auto_sync: true
    prune: true
    self_heal: true

ports:
  frontend: 5006
  backend: 8083
  argocd_https: 8082
  argocd_http: 8000
  dashboard: 3000

containers:
  runtime: "podman"              # "docker" に変更すると Docker を使用

application:
  version: "1.1.0"

features:
  gitea_enabled: true            # false にすると install_gitea.yml をスキップ

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

### `group_vars/all.yml`

`environment.yml` の値を Ansible 変数にマッピングします。直接編集は不要です。

---

## Playbook 詳細

### start_all.yml — 全サービス一括起動

`import_playbook` を使って `deploy_k8s_complete.yml` → `install_gitea.yml` を順次実行します。`ansible-playbook` バイナリのパスをハードコードせず Ansible 内部のプレイ読み込み機構を使用します。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

実行順序：
1. 起動プラン表示（gitea_enabled の値を表示）
2. `deploy_k8s_complete.yml`（K3s / ArgoCD / ビルド / デプロイ / socat / Dashboard）
3. `install_gitea.yml`（`gitea_enabled: true` の場合のみ）
4. 全サービスアクセス情報サマリー

---

### uninstall_all.yml — 全サービス一括削除

```bash
# 通常（データ・ビルドツール保持）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml

# データも削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true"

# すべて完全削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true remove_build_tools=true"
```

| Phase | 削除対象 | 条件 |
|-------|---------|------|
| 1 | socat port forwarding systemd サービス | 常時 |
| 2 | Gitea（コンテナ / systemd / イメージ） | 常時 |
| 3 | K3s（ArgoCD / 全 K8s ワークロード含む） | 常時 |
| 4 | コンテナイメージ全削除 + prune | 常時 |
| 5 | ファイアウォールルール | 常時 |
| 6 | データディレクトリ | `purge_data=true` 時のみ |
| 7 | Java / Maven / Node.js | `remove_build_tools=true` 時のみ |
| 8 | 一時ファイル / Ansible ファクトキャッシュ | 常時 |
| 9 | 削除確認サマリー | 常時 |

---

### deploy_regression_test_complete.yml — K3s 完全回帰テスト

K3s 削除からバージョンアップ/ダウンテストまで一括実行します。**Gitea は含まれません**。Gitea を含む全サービスを起動するには `start_all.yml` を使用してください。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

| Phase | 内容 |
|-------|------|
| 1 | 既存環境の完全削除（K3s / コンテナ / 履歴ファイル） |
| 2 | v1.0.0 ビルド（tag: argocd-regression-v1.0.0） |
| 3 | v1.1.0 ビルド（branch: main） |
| 3.5 | 環境依存マニフェスト準備（externalIPs パッチ・argocd-application.yaml 生成） |
| 4 | K3s + ArgoCD インストール |
| 5 | v1.0.0 / v1.1.0 イメージを K3s へインポート |
| 6 | v1.0.0 初期デプロイ |
| 7 | アップグレードテスト v1.0.0 → v1.1.0（GitOps） |
| 8 | ロールバックテスト v1.1.0 → v1.0.0（GitOps） |
| 9 | 再アップグレードテスト v1.0.0 → v1.1.0（GitOps） |
| 10 | 最終確認（ArgoCD 状態・Deployment・バージョン履歴） |

利用可能なタグ:
```bash
--tags=cleanup
--tags=build-v1.0.0
--tags=build-v1.1.0
--tags=prepare-manifests
--tags=install-k3s
--tags=import-images
--tags=deploy-v1.0.0
--tags=upgrade-test
--tags=rollback-test
--tags=reupgrade-test
--tags=verification
```

サブプレイブック呼び出し（`command: {{ ansible_playbook_cmd }}`）:
- `install_k3s_and_argocd.yml`
- `deploy_app_version_gitops.yml`
- `rollback_app_version_gitops.yml`

---

### deploy_k8s_complete.yml — K3s + ArgoCD + アプリ構築

`start_all.yml` のステップ 1 として呼ばれますが、単独実行も可能です。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_k8s_complete.yml
```

| Phase | 内容 |
|-------|------|
| 0 | 環境情報表示 |
| 1 | K3s + ArgoCD インストール（`install_k3s_and_argocd.yml` を呼び出し） |
| 2 | ビルドツール確認・インストール（未インストール時のみ `install_build_tools.yml` を呼び出し） |
| 3 | Maven ビルド（backend）・npm ビルド（frontend） |
| 4 | コンテナイメージビルド・tar エクスポート・K3s へインポート |
| 5 | PostgreSQL / Redis / backend / frontend デプロイ |
| 5.5 | externalIPs パッチ・イメージタグ更新 |
| 6 | ヘルスチェック |
| 7 | socat ポート転送 systemd サービス設定（5006/8083/8000/8082） |
| — | ArgoCD Application 適用 |
| — | Kubernetes Dashboard インストール・トークン生成 |

コンテナランタイムと `ansible-playbook` パスは起動時に動的に解決します（`which ansible-playbook` を root コンテキストで実行）。

---

### install_k3s_and_argocd.yml — K3s + ArgoCD 単独インストール

```bash
ansible-playbook -i inventory/hosts.yml playbooks/install_k3s_and_argocd.yml
```

K3s インストール → kubeconfig 設定 → ArgoCD namespace 作成・マニフェスト適用 → ArgoCD Pod 待機 → LoadBalancer externalIPs 設定 → 認証情報保存（`/root/argocd-credentials.txt`）

---

### install_gitea.yml — Gitea インストール

K3s が無くても単独で実行できます。`gitea_enabled: false` の場合は `meta: end_play` でスキップ（失敗しない）。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
```

| Phase | 内容 |
|-------|------|
| 0 | `gitea_enabled` 確認（false なら end_play） |
| 1 | コンテナランタイム確認 |
| 2 | データディレクトリ作成（owner: UID 1000、SELinux context 設定） |
| 3 | Gitea イメージ取得 |
| 4 | 既存コンテナ停止・削除 |
| 5 | コンテナ起動（`-v /var/lib/gitea:/data:Z`） |
| 6 | HTTP ポート待機 + DB 初期化待機（30 秒） |
| 7 | 管理者ユーザー作成（`podman exec --user git`） |
| 8 | firewalld ポート開放（firewalld が起動中の場合のみ） |
| 9 | systemd 自動起動設定（`podman generate systemd` またはフォールバック） |
| 10 | 確認・アクセス情報サマリー表示 |

---

### uninstall_gitea.yml — Gitea 削除

```bash
# データ保持
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml

# データも完全削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml \
  -e "purge_data=true"
```

systemd サービス停止・削除 → コンテナ停止・削除 → イメージ削除 → firewall ルール削除 → データディレクトリ削除（`purge_data=true` 時のみ）

---

### gitea_regression_test.yml — Gitea バージョン回帰テスト

```bash
# デフォルト（1.21 → 1.22 → 1.21）
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml

# バージョン指定
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml \
  -e "test_version_old=1.21 test_version_new=1.22"
```

| Phase | 内容 |
|-------|------|
| 1 | 既存 Gitea 削除（クリーンスタート） |
| 2 | 旧・新バージョン イメージ取得 |
| 3 | 旧バージョン (1.21) インストール |
| 4 | 動作確認 + テストデータ作成（Organization: `gitea-regression-org` / Repository: `gitea-regression-repo`） |
| 5 | バージョンアップ → 新バージョン (1.22) |
| 6 | 新バージョン API 確認 + データ ID 一致チェック |
| 7 | バージョンダウン → 旧バージョン (1.21) |
| 8 | 旧バージョン API 確認 + データ ID 一致チェック |
| 9 | 全テスト結果サマリー |

---

### deploy_app_version_gitops.yml — GitOps バージョンアップグレード

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml \
  -e "app_version=1.1.0"
```

ArgoCD Application の path を `overlays/v{version}` に変更 → ArgoCD 同期待機 → ヘルスチェック → バージョン履歴記録

---

### rollback_app_version_gitops.yml — GitOps バージョンロールバック

```bash
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml \
  -e "target_version=1.0.0"
```

デフォルトの `target_version` は `environment.yml` の `argocd.application.initial_version`（1.0.0）。

---

### deploy_app_version.yml — 直接デプロイ（非 GitOps）

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version.yml \
  -e "app_version=1.1.0"
```

ソースビルド → コンテナイメージビルド → K3s インポート → kubectl 適用 → ヘルスチェック → バージョン履歴記録

---

### rollback_app_version.yml — 直接ロールバック（非 GitOps）

```bash
# 直前バージョンに戻す
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version.yml

# バージョン指定
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version.yml \
  -e "target_version=1.0.0"

# Kubernetes rollout 番号指定
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version.yml \
  -e "target_revision=2"
```

---

### install_build_tools.yml / uninstall_build_tools.yml — ビルドツール管理

```bash
ansible-playbook -i inventory/hosts.yml playbooks/install_build_tools.yml
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_build_tools.yml
```

インストール対象: Java 21 (OpenJDK) / Maven 3.9.6（`/opt/maven`）/ Node.js 20.x

---

## クイックリファレンス

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# 全サービス起動（K3s + ArgoCD + アプリ + Gitea）
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml

# 全サービス削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"

# K3s 回帰テストのみ（Gitea 除く）
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml

# Gitea のみ操作
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml -e "purge_data=true"
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml

# アプリ バージョン管理（GitOps）
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml \
  -e "app_version=1.1.0"
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml \
  -e "target_version=1.0.0"

# 構文チェック
ansible-playbook --syntax-check playbooks/start_all.yml
```

---

## 設計上のポイント

### ansible-playbook パスのハードコードなし

- `start_all.yml` は `import_playbook` を使用しており、サブプロセスとして `ansible-playbook` バイナリを呼び出しません
- `deploy_k8s_complete.yml` / `deploy_regression_test_complete.yml` でサブプレイブックを呼び出す箇所は `which ansible-playbook` で動的に解決します（root コンテキストで実行するため `/bin/ansible-playbook` が使われます）

### コンテナランタイムの切替

全 Playbook は `{{ container_runtime }}` 変数を使用します。`environment.yml` の `containers.runtime` を変更するだけで Docker / Podman を切り替えられます。

### gitea_enabled フラグ

`install_gitea.yml` は `gitea_enabled: false` の場合 `fail:` ではなく `meta: end_play` でスキップします。そのため `import_playbook` 経由で呼ばれても親プレイが継続します。

### 冪等性

全 Playbook は複数回実行しても同じ結果になるよう設計されています。
