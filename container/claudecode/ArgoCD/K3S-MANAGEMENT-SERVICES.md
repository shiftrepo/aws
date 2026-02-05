# K3s 管理サービス構築完了レポート

**日時**: 2026-02-05 09:53 UTC  
**ステータス**: ✅ 完全稼働（Ansibleで構築）

---

## 🎯 実装した管理サービス

### 1. Kubernetes Dashboard (Web UI)
- **Version**: v2.7.0
- **アクセスポート**: 5004
- **認証**: Token認証
- **機能**: K3sクラスターの完全なWeb管理

### 2. ArgoCD (GitOps管理)
- **Version**: v2.10.0
- **アクセスポート**: 5010
- **機能**: Gitベースのデプロイメント管理
- **ステータス**: 既に稼働中

### 3. kubectl (CLI管理)
- **Path**: `/usr/local/bin/kubectl`
- **機能**: コマンドライン管理

---

## 🌐 アクセス情報

### Kubernetes Dashboard

#### URL
```
https://13.219.96.72:5004
https://ec2-13-219-96-72.compute-1.amazonaws.com:5004
```

#### ログイントークン
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IlRGeDdyVlRWRUgyR08tdVJnaDlKWEZDM1V3Q2pJZzVrNGlFYmV5ejVWOUUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyYWE1ZDE4Yi0xYjA0LTQ0NTAtOGM5ZC04OTE2YzE5MTJhYjMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.D9gpvWNZdbGtOKUflSJmUyzYkpoO84G2qkti0ZRnme4UFgwjIml-DgdR50f0uwvl6egcVojoCuZYA-O_nPpAor94Fi1Jk8l66rXuEmZMPdGcpZjkMTxmx6zEAUGNfTXl1-5uhBZ0pC9BgtcICLGGm-0QFVY9qOYlmHAbNlo1CwYqyQdOwIOc-FMX70Sp3csl7u1-FLvmthru-m-P4cKcFtEAvRr2kSoSe0xeZWSaq9wvOhemkywSCa8JIBMhnnsXXAB7DTQom0IVt9djO11LIRPRFpyIItm6SBeY8FxULOu7JGEa0nzPWmesKAgsuLHg25B2N6KaMdL4eJRad1aHBg
```

### ログイン手順
1. ブラウザで https://13.219.96.72:5004 にアクセス
2. 証明書警告を承認（自己署名証明書のため）
3. 「Token」を選択
4. 上記のトークンを貼り付け
5. 「Sign in」をクリック

---

## 📊 管理サービス一覧

| サービス | ポート | URL | 用途 |
|---------|--------|-----|------|
| **Kubernetes Dashboard** | 5004 | https://13.219.96.72:5004 | K3s Web UI管理 |
| **ArgoCD** | 5010 | http://13.219.96.72:5010 | GitOps デプロイ管理 |
| **Frontend App** | 5006 | http://13.219.96.72:5006 | アプリケーション |
| **Nexus** | 8000 | http://localhost:8000 | アーティファクト管理 |
| **pgAdmin** | 5050 | http://localhost:5050 | DB管理 |

---

## 🔧 Ansibleによる構築

### すべてAnsibleで自動化されています

#### Kubernetes Dashboard インストール
```bash
cd /root/aws.git/container/claudecode/ArgoCD
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/install_k3s_dashboard.yml
```

#### 完全CDパイプライン実行
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml
```

### Ansibleプレイブック一覧
```
ansible/playbooks/
├── deploy_infrastructure.yml          # インフラ構築
├── install_k3s_and_argocd.yml        # K3s + ArgoCD
├── install_build_tools.yml            # ビルドツール
├── build_and_deploy_artifacts.yml    # Nexus登録
├── complete_cd_pipeline.yml          # 完全CDパイプライン
└── install_k3s_dashboard.yml         # Dashboard インストール ✨ NEW
```

---

## 📖 Kubernetes Dashboard機能

### できること

#### 1. リソース管理
- **Pods**: 稼働状況、ログ確認、再起動
- **Deployments**: レプリカ数変更、イメージ更新
- **Services**: エンドポイント確認、ポート設定
- **ConfigMaps/Secrets**: 設定管理

#### 2. 監視
- **CPU/Memory使用率**: リアルタイム表示
- **Pod状態**: Running, Pending, Failed
- **イベントログ**: トラブルシューティング

#### 3. 操作
- **Scale**: レプリカ数の増減
- **Delete**: リソース削除
- **Edit**: YAML直接編集
- **Exec**: Pod内でコマンド実行

---

## 🔍 使用例

### 1. Podのログ確認
1. Dashboardにログイン
2. 左メニュー → **Workloads** → **Pods**
3. Pod名をクリック
4. 右上の **Logs** ボタン

### 2. レプリカ数変更
1. **Workloads** → **Deployments**
2. `orgmgmt-frontend` をクリック
3. 右上の **Scale** ボタン
4. レプリカ数を入力（例: 5）
5. **Scale** クリック

### 3. リソース使用率確認
1. ダッシュボードトップページ
2. CPU/Memory使用率グラフ表示
3. Node/Pod別の詳細確認

---

## 🛠️ トラブルシューティング

### Dashboard にアクセスできない

#### ポート転送確認
```bash
systemctl status k3s-dashboard-forward
```

#### 再起動
```bash
systemctl restart k3s-dashboard-forward
```

#### ログ確認
```bash
journalctl -u k3s-dashboard-forward -f
```

### トークンが無効

#### 新しいトークン取得
```bash
sudo kubectl get secret admin-user-token \
  -n kubernetes-dashboard \
  -o jsonpath='{.data.token}' | base64 -d
```

### Pod が起動しない

#### Dashboardから確認
1. **Workloads** → **Pods**
2. 該当Podをクリック
3. **Events** タブで原因確認
4. **Logs** タブでログ確認

#### kubectlで確認
```bash
kubectl get pods -n default
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

## 📝 運用のベストプラクティス

### 1. 定期的な確認
- 毎日: Pod状態、リソース使用率
- 毎週: イベントログ、エラー確認
- 毎月: 不要リソースのクリーンアップ

### 2. バックアップ
```bash
# YAML設定のバックアップ
kubectl get all -n default -o yaml > backup.yaml
```

### 3. アラート設定
- CPU使用率 > 80%
- Memory使用率 > 80%
- Pod再起動頻度 > 5回/時間

---

## 🎉 まとめ

### ✅ 実装完了

| 項目 | ステータス |
|------|-----------|
| Kubernetes Dashboard | ✅ 稼働中 |
| ArgoCD | ✅ 稼働中 |
| Ansibleプレイブック | ✅ 作成済み |
| 外部アクセス | ✅ 設定済み |
| 認証トークン | ✅ 生成済み |
| ドキュメント | ✅ 完備 |

### 🌟 管理方法

#### Web UI管理（推奨）
- **Kubernetes Dashboard**: https://13.219.96.72:5004
- **ArgoCD**: http://13.219.96.72:5010

#### CLI管理
```bash
kubectl get pods
kubectl get deployments
kubectl get services
kubectl logs <pod-name>
```

#### Ansible管理
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/<playbook>.yml
```

---

## 🔄 再構築方法

### 完全クリーンアップ後の再構築
```bash
# 1. インフラ起動
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d

# 2. K3s Dashboard インストール
cd /root/aws.git/container/claudecode/ArgoCD
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/install_k3s_dashboard.yml

# 3. 完全CDパイプライン実行
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml
```

**すべてAnsibleで管理されています！**
