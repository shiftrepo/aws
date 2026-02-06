# アプリケーションバージョンアップ・ロールバック手順

このドキュメントでは、ArgoCDを使用したアプリケーションのバージョンアップとロールバック手順を説明します。

## 目次

- [概要](#概要)
- [バージョニング戦略](#バージョニング戦略)
- [バージョンアップ手順](#バージョンアップ手順)
- [ロールバック手順](#ロールバック手順)
- [バージョン確認方法](#バージョン確認方法)
- [トラブルシューティング](#トラブルシューティング)

---

## 概要

本システムでは、以下のバージョン管理戦略を採用しています：

- **セマンティックバージョニング**: `MAJOR.MINOR.PATCH` 形式（例: `1.1.0`）
- **Gitタグ**: 各バージョンにGitタグを付与し、リリース履歴を管理
- **Dockerイメージタグ**: アプリケーションのバージョンとDockerイメージタグを一致させる
- **ArgoCDによるGitOps**: Gitリポジトリの変更を検知し、自動的にデプロイ

### 現在のバージョン

- **Backend**: 1.1.0
- **Frontend**: 1.1.0
- **K3s**: v1.34.3+k3s1
- **ArgoCD**: v2.10.0

---

## バージョニング戦略

### セマンティックバージョニング

```
MAJOR.MINOR.PATCH

MAJOR: 互換性のない API 変更
MINOR: 後方互換性のある機能追加
PATCH: 後方互換性のあるバグ修正
```

### ファイル更新箇所

新しいバージョンをリリースする際は、以下のファイルを更新します：

1. **Backend**: `app/backend/pom.xml`
   ```xml
   <version>1.1.0</version>
   ```

2. **Frontend**: `app/frontend/package.json`
   ```json
   "version": "1.1.0"
   ```

3. **K8s Manifests**:
   - `k8s-manifests/backend-deployment.yaml`
   - `k8s-manifests/frontend-deployment.yaml`
   ```yaml
   image: localhost/orgmgmt-backend:1.1.0
   ```

4. **Ansible Playbook**: `ansible/playbooks/deploy_k8s_complete.yml`
   ```yaml
   app_version: "1.1.0"
   ```

---

## バージョンアップ手順

### 手順1: コード変更とバージョン番号更新

```bash
# 作業ディレクトリに移動
cd /root/aws.git/container/claudecode/ArgoCD

# 新機能の開発やバグ修正を実施
# ...

# バージョン番号を更新（例: 1.1.0 → 1.2.0）
# 1. app/backend/pom.xml
vim app/backend/pom.xml
# <version>1.2.0</version> に変更

# 2. app/frontend/package.json
vim app/frontend/package.json
# "version": "1.2.0" に変更

# 3. K8s manifests
vim k8s-manifests/backend-deployment.yaml
# image: localhost/orgmgmt-backend:1.2.0 に変更

vim k8s-manifests/frontend-deployment.yaml
# image: localhost/orgmgmt-frontend:1.2.0 に変更

# 4. Ansible playbook
vim ansible/playbooks/deploy_k8s_complete.yml
# app_version: "1.2.0" に変更
```

### 手順2: 変更をコミット

```bash
# 変更をステージング
git add -A

# コミット
git commit -m "feat: Bump version to 1.2.0

- Add new feature X
- Fix bug Y
- Update dependencies

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 手順3: Gitタグを作成

```bash
# 説明付きタグを作成
git tag -a v1.2.0 -m "Release version 1.2.0

New Features:
- Feature X: Description
- Feature Y: Description

Bug Fixes:
- Fix Z: Description

Breaking Changes:
- None
"

# タグを確認
git tag -l -n9 v1.2.0
```

### 手順4: GitHubにプッシュ

```bash
# コミットをプッシュ
git push origin main

# タグをプッシュ
git push origin v1.2.0
```

### 手順5: アプリケーションをビルドしてデプロイ

```bash
# Ansibleプレイブックを実行（完全再デプロイ）
cd ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

または、既存環境に対してバージョンアップのみ実行する場合：

```bash
# 1. アプリケーションをビルド
cd /root/aws.git/container/claudecode/ArgoCD

# Backend ビルド
cd app/backend
mvn clean package -DskipTests

# Frontend ビルド
cd ../frontend
npm install
npm run build

# 2. Dockerイメージをビルド（バージョンタグ付き）
cd ../backend
podman build -t orgmgmt-backend:1.2.0 -t orgmgmt-backend:latest -f Dockerfile .

cd ../frontend
podman build -t orgmgmt-frontend:1.2.0 -t orgmgmt-frontend:latest -f Dockerfile .

# 3. イメージをエクスポート
podman save localhost/orgmgmt-backend:1.2.0 localhost/orgmgmt-backend:latest -o /tmp/backend.tar
podman save localhost/orgmgmt-frontend:1.2.0 localhost/orgmgmt-frontend:latest -o /tmp/frontend.tar

# 4. K3sにインポート
/usr/local/bin/k3s ctr images import /tmp/backend.tar
/usr/local/bin/k3s ctr images import /tmp/frontend.tar

# 5. イメージを確認
/usr/local/bin/k3s crictl images | grep orgmgmt
```

### 手順6: ArgoCDで同期

```bash
# ArgoCDにログイン（必要に応じて）
argocd login 10.0.1.200:8082 --username admin --password '<password>' --insecure

# アプリケーション一覧を確認
argocd app list

# 同期実行
argocd app sync orgmgmt-app

# 同期状態を確認
argocd app get orgmgmt-app
```

または、ArgoCD UIから手動同期：

1. `https://10.0.1.200:8082` にアクセス
2. `orgmgmt-app` を選択
3. `SYNC` ボタンをクリック
4. 同期オプションを確認して `SYNCHRONIZE` をクリック

### 手順7: デプロイ状態を確認

```bash
# Pod状態を確認
kubectl get pods -l app=orgmgmt-backend
kubectl get pods -l app=orgmgmt-frontend

# Pod内のイメージタグを確認
kubectl describe pod -l app=orgmgmt-backend | grep Image:
kubectl describe pod -l app=orgmgmt-frontend | grep Image:

# ログを確認
kubectl logs -l app=orgmgmt-backend --tail=50
kubectl logs -l app=orgmgmt-frontend --tail=50
```

### 手順8: アプリケーションで動作確認

1. **フロントエンドにアクセス**: `http://10.0.1.200:5006`
2. **システム情報を確認**:
   - トップページに表示される「System Information」カードを確認
   - Pod名が新しいPod名になっていることを確認
   - Session IDが表示されることを確認
   - Flyway Versionが正しいことを確認
   - Database Statusが `✅ OK` になっていることを確認

3. **機能テスト**:
   - Organizations、Departments、Users の各ページで CRUD 操作を実行
   - エラーが発生しないことを確認

---

## ロールバック手順

デプロイ後に問題が発生した場合、以前のバージョンにロールバックできます。

### 方法1: ArgoCDで以前のGitコミットに戻す

```bash
# 以前の正常なコミットハッシュを確認
git log --oneline

# ArgoCDアプリケーションを特定のコミットに同期
argocd app sync orgmgmt-app --revision <commit-hash>

# 例:
argocd app sync orgmgmt-app --revision fbd1876
```

### 方法2: Gitでrevertしてプッシュ

```bash
# 問題のあるコミットをrevert
git revert <commit-hash>

# プッシュ
git push origin main

# ArgoCDが自動的に検知して同期（3分以内）
# または手動同期:
argocd app sync orgmgmt-app
```

### 方法3: Kubernetesで以前のイメージに戻す

```bash
# 以前のイメージタグを指定してDeploymentを更新
kubectl set image deployment/orgmgmt-backend backend=localhost/orgmgmt-backend:1.1.0
kubectl set image deployment/orgmgmt-frontend frontend=localhost/orgmgmt-frontend:1.1.0

# ロールアウト状態を確認
kubectl rollout status deployment/orgmgmt-backend
kubectl rollout status deployment/orgmgmt-frontend
```

### 方法4: Kubernetes Deploymentのロールバック機能を使用

```bash
# ロールアウト履歴を確認
kubectl rollout history deployment/orgmgmt-backend
kubectl rollout history deployment/orgmgmt-frontend

# 直前のリビジョンにロールバック
kubectl rollout undo deployment/orgmgmt-backend
kubectl rollout undo deployment/orgmgmt-frontend

# 特定のリビジョンにロールバック
kubectl rollout undo deployment/orgmgmt-backend --to-revision=2
kubectl rollout undo deployment/orgmgmt-frontend --to-revision=2
```

### ロールバック後の確認

```bash
# Pod状態を確認
kubectl get pods

# イメージタグを確認
kubectl describe pod -l app=orgmgmt-backend | grep Image:

# アプリケーションにアクセスして動作確認
curl http://10.0.1.200:8083/actuator/health
curl http://10.0.1.200:5006/
```

---

## バージョン確認方法

### 1. アプリケーションUIでの確認

- **URL**: `http://10.0.1.200:5006`
- トップページの「System Information」カードで以下を確認できます：
  - **Pod Name**: 現在実行中のPod名
  - **Session ID**: 現在のHTTPセッションID
  - **Flyway Version**: データベースマイグレーションバージョン
  - **Database Status**: データベース接続状態

### 2. コマンドラインでの確認

```bash
# バックエンドバージョン確認（pom.xml）
grep -A 1 "<artifactId>orgmgmt-backend</artifactId>" app/backend/pom.xml | grep version

# フロントエンドバージョン確認（package.json）
grep '"version"' app/frontend/package.json

# K8s Deploymentのイメージタグ確認
kubectl get deployment orgmgmt-backend -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get deployment orgmgmt-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'

# 実行中のPodのイメージ確認
kubectl describe pod -l app=orgmgmt-backend | grep Image:
kubectl describe pod -l app=orgmgmt-frontend | grep Image:

# Gitタグ一覧
git tag -l
```

### 3. ArgoCD UIでの確認

1. `https://10.0.1.200:8082` にアクセス
2. `orgmgmt-app` を選択
3. 以下を確認：
   - **Sync Status**: `Synced` / `OutOfSync`
   - **Health Status**: `Healthy` / `Degraded`
   - **Last Sync**: 最後に同期した時刻
   - **Revision**: 現在デプロイされているGitコミット

---

## トラブルシューティング

### 問題: ArgoCDが同期しない

**原因**: 自動同期が無効化されている、またはGit接続エラー

**解決策**:
```bash
# アプリケーション状態を確認
argocd app get orgmgmt-app

# 手動で同期を実行
argocd app sync orgmgmt-app

# Git接続を確認
argocd repo list
```

### 問題: Podが起動しない（ImagePullBackOff）

**原因**: K3sにイメージがインポートされていない

**解決策**:
```bash
# K3sのイメージ一覧を確認
/usr/local/bin/k3s crictl images | grep orgmgmt

# イメージが無い場合は再インポート
/usr/local/bin/k3s ctr images import /tmp/backend.tar
/usr/local/bin/k3s ctr images import /tmp/frontend.tar
```

### 問題: Podが起動しない（CrashLoopBackOff）

**原因**: アプリケーションエラー、環境変数不足、データベース接続エラー

**解決策**:
```bash
# ログを確認
kubectl logs -l app=orgmgmt-backend --tail=100

# Pod詳細を確認
kubectl describe pod -l app=orgmgmt-backend

# 環境変数を確認
kubectl exec -it <pod-name> -- env | grep -E 'POSTGRES|REDIS|POD_NAME'

# データベース接続を確認
kubectl exec -it <backend-pod> -- curl -s http://localhost:8080/actuator/health
```

### 問題: データベースマイグレーションエラー

**原因**: Flyway マイグレーションスクリプトエラー、データベース接続エラー

**解決策**:
```bash
# Flywayマイグレーション履歴を確認
kubectl exec -it <backend-pod> -- psql -h postgres -U orgmgmt_user -d orgmgmt -c "SELECT * FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;"

# 手動でマイグレーションを実行（必要に応じて）
kubectl exec -it <backend-pod> -- java -jar /app/orgmgmt-backend.jar --spring.flyway.enabled=true
```

### 問題: セッション情報が表示されない

**原因**: Redis接続エラー、CORS設定エラー

**解決策**:
```bash
# Redis接続を確認
kubectl get pods -l app=redis
kubectl logs -l app=redis

# Redis接続テスト
kubectl exec -it <backend-pod> -- curl -s http://localhost:8080/api/system/info

# CORS設定を確認（ブラウザのDevToolsでネットワークタブを確認）
```

### 問題: ロールバック後もエラーが続く

**原因**: データベーススキーマの不整合、永続データの問題

**解決策**:
```bash
# データベースの状態を確認
kubectl exec -it <postgres-pod> -- psql -U orgmgmt_user -d orgmgmt -c "\dt"

# 必要に応じてデータベースをバックアップから復元
# （事前にバックアップを取得している場合）

# 最終手段: 完全再デプロイ
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/deploy_k8s_complete.yml
```

---

## ベストプラクティス

1. **バージョンアップ前の確認事項**:
   - 現在のバージョンが安定して動作していること
   - データベースバックアップが取得されていること
   - ロールバック計画が準備されていること

2. **段階的なデプロイ**:
   - 開発環境でテスト
   - ステージング環境で検証
   - 本番環境にデプロイ

3. **モニタリング**:
   - デプロイ後、最低15分間はログとメトリクスを監視
   - エラーレートの増加がないか確認
   - レスポンスタイムが正常か確認

4. **ドキュメント化**:
   - 各バージョンの変更内容をGitタグのコメントに記載
   - 重大な変更は別途リリースノートを作成
   - トラブルシューティング情報を蓄積

---

## 参考情報

- [ArgoCD公式ドキュメント](https://argo-cd.readthedocs.io/)
- [Kubernetesデプロイメント戦略](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [セマンティックバージョニング](https://semver.org/lang/ja/)
- [本プロジェクトREADME](./README.md)
- [認証情報ガイド](./CREDENTIALS.md)
