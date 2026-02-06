# ArgoCD GitOps デプロイメントガイド

## 概要

アプリケーションはArgoCDを使用してGitOpsでデプロイされています。GitHubリポジトリの`k8s-manifests`ディレクトリにあるマニフェストを監視し、自動的にKubernetesクラスターに適用します。

## ArgoCD Application

**Name**: `orgmgmt-app`

**Repository**: https://github.com/shiftrepo/aws.git

**Path**: `container/claudecode/ArgoCD/k8s-manifests`

**Branch**: `main`

## 管理されているリソース

| リソース | 名前 | レプリカ数 | 説明 |
|---------|------|-----------|------|
| Deployment | orgmgmt-backend | 2 | Spring Boot バックエンド |
| Deployment | orgmgmt-frontend | 2 | React フロントエンド |
| Deployment | postgres | 1 | PostgreSQL データベース |
| Deployment | redis | 1 | Redis キャッシュ |
| Service | orgmgmt-backend | - | LoadBalancer (8083) |
| Service | orgmgmt-frontend | - | LoadBalancer (5006) |
| Service | postgres | - | ClusterIP |
| Service | redis | - | ClusterIP |
| ConfigMap | postgres-config | - | PostgreSQL設定 |
| PVC | postgres-pvc | - | PostgreSQLデータ永続化 |

## 自動同期設定

ArgoCD Applicationは以下の自動同期設定が有効になっています：

### Automated Sync
- **有効**: ✅
- GitHubリポジトリの変更を検出すると自動的にKubernetesに適用

### Self Heal
- **有効**: ✅
- Kubernetesクラスター上で手動で変更された場合、Gitの状態に自動的に戻す

### Prune
- **有効**: ✅
- Gitから削除されたリソースをKubernetesからも自動的に削除

## デプロイフロー

```
1. 開発者がk8s-manifestsを変更
   ↓
2. GitHub mainブランチにpush
   ↓
3. ArgoCDが変更を検出 (3分ごとにポーリング)
   ↓
4. ArgoCDが自動的にKubernetesに適用
   ↓
5. Podが再起動/更新される
```

## ArgoCD UI でのアクセス

### アクセス方法

**URL**: https://10.0.1.200:8082 または http://10.0.1.200:8000

**認証情報**:
```bash
Username: admin
Password: <see /root/argocd-credentials.txt>
```

### UIでできること

1. **アプリケーション状態の確認**
   - Sync Status (Synced/OutOfSync)
   - Health Status (Healthy/Degraded)
   - リソースツリー表示

2. **手動同期**
   - UIから"SYNC"ボタンをクリック
   - 特定のリソースのみ同期も可能

3. **ロールバック**
   - History タブから以前のリビジョンに戻す

4. **リソース詳細**
   - 各リソースのYAML表示
   - ログ確認
   - イベント確認

## CLIでの操作

### ArgoCD CLIログイン

```bash
# HTTPS
argocd login 10.0.1.200:8082 --username admin --password '<password>' --insecure

# HTTP
argocd login 10.0.1.200:8000 --username admin --password '<password>' --insecure --plaintext
```

### アプリケーション一覧

```bash
argocd app list
```

### アプリケーション詳細

```bash
argocd app get orgmgmt-app
```

### 手動同期

```bash
argocd app sync orgmgmt-app
```

### ロールバック

```bash
# 履歴確認
argocd app history orgmgmt-app

# 特定のリビジョンにロールバック
argocd app rollback orgmgmt-app <revision-id>
```

### リソース差分確認

```bash
argocd app diff orgmgmt-app
```

## kubectl での確認

### ArgoCD Application状態

```bash
kubectl get application orgmgmt-app -n argocd
```

### 管理されているリソース

```bash
kubectl get all -n default -l argocd.argoproj.io/instance=orgmgmt-app
```

## マニフェスト変更手順

### 1. マニフェストを変更

```bash
cd /root/aws.git/container/claudecode/ArgoCD/k8s-manifests
vim backend-deployment.yaml  # 例: レプリカ数を変更
```

### 2. 変更をコミット

```bash
git add backend-deployment.yaml
git commit -m "feat: Increase backend replicas to 3"
git push origin main
```

### 3. ArgoCDが自動同期

- 最大3分待つ（ポーリング間隔）
- または、UIで手動同期

### 4. 確認

```bash
kubectl get pods | grep orgmgmt-backend
```

## トラブルシューティング

### アプリケーションがOutOfSync

**原因**: GitHubとKubernetesの状態が一致していない

**解決策**:
```bash
# 手動同期
argocd app sync orgmgmt-app

# または kubectl patch
kubectl patch application orgmgmt-app -n argocd --type merge -p '{"operation": {"sync": {"prune": true}}}'
```

### アプリケーションがDegraded

**原因**: Podが起動しない、サービスが正常でない

**解決策**:
```bash
# Pod状態確認
kubectl get pods

# ログ確認
kubectl logs <pod-name>

# イベント確認
kubectl get events --sort-by='.lastTimestamp'
```

### 同期が遅い

**原因**: デフォルトポーリング間隔は3分

**解決策**:
- 手動同期を使用
- Webhook設定でプッシュ時に即座に同期（高度な設定）

## 再デプロイ手順

ArgoCD Applicationを再作成する場合：

```bash
# Application削除
kubectl delete application orgmgmt-app -n argocd

# Application再作成
kubectl apply -f /root/aws.git/container/claudecode/ArgoCD/argocd-application.yaml
```

## セキュリティ注意事項

- ArgoCD UIには外部からアクセス可能（ポート8082, 8000）
- 強力なパスワードに変更することを推奨
- 本番環境ではGitHubプライベートリポジトリ + SSH認証を推奨

## まとめ

✅ **GitOpsワークフロー完成**
- GitHubがシングルソースオブトゥルース
- 自動同期・自己修復・自動削除が有効
- ArgoCD UIで可視化・管理可能

✅ **変更は全てGit経由**
- `kubectl apply`は不要
- マニフェストを変更してプッシュするだけ

✅ **監査・ロールバックが容易**
- Git履歴 = デプロイ履歴
- いつでも以前の状態に戻せる

---
Updated: 2026-02-06
