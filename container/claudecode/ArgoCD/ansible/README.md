# Ansible Playbooks リファレンス

K3s / ArgoCD / Gitea を含む全サービスの構築・削除・回帰テストを自動化する Ansible Playbook 群です。

## ディレクトリ構造

```
ansible/
├── ansible.cfg                                  # Ansible 設定
├── config/
│   └── environment.yml                          # 唯一の設定ファイル（環境ごとに編集）
├── group_vars/
│   └── all.yml                                  # environment.yml から変数をマッピング
├── inventory/
│   └── hosts.yml                                # ローカルホスト inventory
├── playbooks/
│   ├── start_all.yml                            # 全サービス一括起動（推奨）
│   ├── uninstall_all.yml                        # 全サービス一括削除
│   ├── deploy_regression_test_complete.yml      # 完全自動回帰テスト
│   ├── deploy_k8s_complete.yml                  # K3s+ArgoCD+アプリ構築
│   ├── install_k3s_and_argocd.yml               # K3s + ArgoCD 単独
│   ├── install_build_tools.yml                  # Java / Maven / Node.js
│   ├── uninstall_build_tools.yml                # ビルドツール削除
│   ├── install_gitea.yml                        # Gitea インストール
│   ├── uninstall_gitea.yml                      # Gitea 削除
│   ├── gitea_regression_test.yml                # Gitea バージョン回帰テスト
│   ├── deploy_app_version_gitops.yml            # GitOps アップグレード
│   ├── rollback_app_version_gitops.yml          # GitOps ロールバック
│   ├── deploy_app_version.yml                   # 直接デプロイ
│   └── rollback_app_version.yml                 # 直接ロールバック
└── README.md                                    # このファイル
```

## 設定ファイル

### `config/environment.yml`

全 Playbook が参照する唯一の設定ファイルです。環境ごとにこのファイルのみ変更します。

```yaml
network:
  external_ip: "10.0.1.84"   # 空 "" にすると ansible_default_ipv4.address を自動使用

directories:
  base_dir: "/root/aws.git/container/claudecode/ArgoCD"

containers:
  runtime: "podman"           # "docker" に変更すると Docker を使用

features:
  gitea_enabled: true         # false にすると Gitea をスキップ

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

`environment.yml` の値を Playbook 変数にマッピングします。直接編集は不要です。

## Playbook 詳細

### start_all.yml — 全サービス一括起動

`import_playbook` を使用して `deploy_k8s_complete.yml` → `install_gitea.yml` を順番に実行します。`ansible-playbook` バイナリへのパスをハードコードせず、Ansible 内部のプレイ読み込み機構を使用します。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml
```

**実行順序**:
1. 起動プラン表示
2. `deploy_k8s_complete.yml`（K3s・ArgoCD・アプリ・socat・Dashboard）
3. `install_gitea.yml`（`gitea_enabled: true` の場合のみ）
4. 全サービスアクセス情報サマリー表示

---

### uninstall_all.yml — 全サービス一括削除

```bash
# 通常削除（データ・ビルドツール保持）
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml

# データも削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true"

# すべて完全削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml \
  -e "purge_data=true remove_build_tools=true"
```

**削除フェーズ**:
| Phase | 内容 |
|-------|------|
| 1 | socat port forwarding systemd サービス |
| 2 | Gitea コンテナ / systemd / イメージ |
| 3 | K3s（ArgoCD・全 K8s ワークロード含む） |
| 4 | コンテナイメージ全削除 + prune |
| 5 | ファイアウォールルール |
| 6 | データディレクトリ（`purge_data=true` 時のみ） |
| 7 | Java / Maven / Node.js（`remove_build_tools=true` 時のみ） |
| 8 | 一時ファイル / Ansible ファクトキャッシュ |
| 9 | 削除確認サマリー |

---

### install_gitea.yml — Gitea インストール

K3s が起動中でなくても単独で実行できます。`gitea_enabled: false` の場合は `meta: end_play` でスキップ（エラーにならない）。

```bash
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
```

**フェーズ**:
| Phase | 内容 |
|-------|------|
| 0 | `gitea_enabled` フラグ確認（false ならスキップ） |
| 1 | コンテナランタイム確認 |
| 2 | データディレクトリ作成（UID 1000 所有権・SELinux `:Z`） |
| 3 | Gitea イメージ取得 |
| 4 | 既存コンテナ停止・削除 |
| 5 | コンテナ起動（`-v /var/lib/gitea:/data:Z`） |
| 6 | HTTP ポート待機 + DB 初期化待機（30秒） |
| 7 | 管理者ユーザー作成（`--user git` で実行） |
| 8 | firewalld ポート開放 |
| 9 | systemd 自動起動設定（`podman generate systemd` またはフォールバック） |
| 10 | 確認・アクセス情報サマリー |

**SELinux 対応**:
- ボリュームマウントに `:Z` フラグを使用
- `chcon -Rt container_file_t` でコンテキストを設定

---

### uninstall_gitea.yml — Gitea 削除

```bash
# データ保持
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml

# データも完全削除
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml \
  -e "purge_data=true"
```

---

### gitea_regression_test.yml — Gitea バージョン回帰テスト

1プレイブックで「構築→アップグレード→ダウングレード」とデータ永続性を自動検証します。

```bash
# デフォルト（1.21 → 1.22 → 1.21）
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml

# バージョン指定
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml \
  -e "test_version_old=1.21 test_version_new=1.22"
```

**テストフェーズ**:
| Phase | 内容 |
|-------|------|
| 1 | 既存 Gitea 削除（クリーンスタート） |
| 2 | 旧・新バージョン イメージ事前取得 |
| 3 | 旧バージョン (1.21) インストール |
| 4 | 動作確認・テストデータ作成（Organization / Repository） |
| 5 | バージョンアップ (1.21 → 1.22) |
| 6 | 新バージョン確認・データ保持確認（ID 一致チェック） |
| 7 | バージョンダウン (1.22 → 1.21) |
| 8 | 旧バージョン確認・データ保持確認 |
| 9 | 全テスト結果サマリー |

---

### deploy_regression_test_complete.yml — K8s 完全回帰テスト

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml
```

K3s 削除 → v1.0.0/v1.1.0 ビルド → K3s 構築 → デプロイ → アップグレード/ロールバックテストを一括実行します。

---

### deploy_k8s_complete.yml — K3s + ArgoCD + アプリ構築

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_k8s_complete.yml
```

`start_all.yml` のステップ 1 として使われますが、単独実行も可能です。

**フェーズ**:
1. K3s + ArgoCD インストール
2. ビルドツール確認・インストール（未インストール時のみ）
3. Maven ビルド（backend）
4. npm ビルド（frontend）
5. コンテナイメージビルド + K3s インポート
6. K8s デプロイ（PostgreSQL, Redis, Backend, Frontend）
7. ExternalIP / イメージタグの動的パッチ適用
8. ArgoCD Application 適用
9. Kubernetes Dashboard インストール
10. socat ポート転送 systemd サービス設定

**ansible-playbook パス解決**:
`become: no` を使わず root コンテキストで `which ansible-playbook` を実行するため、`/bin/ansible-playbook`（システム全体インストール）が使われます。

---

### deploy_app_version_gitops.yml / rollback_app_version_gitops.yml

```bash
# アップグレード
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml \
  -e "app_version=1.1.0"

# ロールバック
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml \
  -e "target_version=1.0.0"
```

---

### install_build_tools.yml / uninstall_build_tools.yml

```bash
ansible-playbook -i inventory/hosts.yml playbooks/install_build_tools.yml
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_build_tools.yml
```

Java 21 (OpenJDK)・Maven 3.9.6・Node.js 20.x をインストール / 削除します。

## クイックリファレンス

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# --- 全サービス起動 ---
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml

# --- 全サービス削除 ---
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_all.yml -e "purge_data=true"

# --- Gitea のみ操作 ---
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
ansible-playbook -i inventory/hosts.yml playbooks/uninstall_gitea.yml -e "purge_data=true"
ansible-playbook -i inventory/hosts.yml playbooks/gitea_regression_test.yml

# --- アプリバージョン管理 ---
ansible-playbook -i inventory/hosts.yml playbooks/deploy_app_version_gitops.yml -e "app_version=1.1.0"
ansible-playbook -i inventory/hosts.yml playbooks/rollback_app_version_gitops.yml -e "target_version=1.0.0"

# --- 完全回帰テスト ---
ansible-playbook -i inventory/hosts.yml playbooks/deploy_regression_test_complete.yml

# --- 構文チェック ---
ansible-playbook --syntax-check playbooks/start_all.yml
```

## 設計上の注意点

### ansible-playbook パスのハードコードなし

- `start_all.yml` は `import_playbook` を使用しており、サブプロセスとして `ansible-playbook` バイナリを呼び出しません
- `deploy_k8s_complete.yml` 等でサブプレイブックを呼び出す箇所は `which ansible-playbook` で動的に解決します（`become: no` を使わず root コンテキストで実行）

### コンテナランタイムの切替

全 Playbook は `{{ container_runtime }}` 変数を使用します。`environment.yml` の `containers.runtime` を `"docker"` または `"podman"` に変更するだけで切り替えられます。

### Gitea の `gitea_enabled` フラグ

`install_gitea.yml` は `gitea_enabled: false` の場合 `meta: end_play` でスキップします（`fail:` でないため `import_playbook` 経由で呼ばれても親プレイが継続します）。

### 冪等性

全 Playbook は冪等性を持ちます（複数回実行しても同じ結果になります）。

## トラブルシューティング

### ansible-playbook が見つからない

```bash
sudo python3 -m pip install ansible
sudo ln -sf /usr/local/bin/ansible-playbook /usr/bin/ansible-playbook
which ansible-playbook  # /bin/ansible-playbook
```

### Gitea コンテナが起動しない

```bash
podman logs gitea

# 権限エラーの場合
chown -R 1000:1000 /var/lib/gitea
chcon -Rt container_file_t /var/lib/gitea

# 再インストール
ansible-playbook -i inventory/hosts.yml playbooks/install_gitea.yml
```

### K3s Pod が起動しない

```bash
sudo /usr/local/bin/k3s kubectl get pods -A
sudo /usr/local/bin/k3s kubectl describe pod <pod-name>
sudo /usr/local/bin/k3s kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### Verbose モード

```bash
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml -v
ansible-playbook -i inventory/hosts.yml playbooks/start_all.yml -vvv
```
