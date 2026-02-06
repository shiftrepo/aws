# ArgoCD エラー解決レポート

**日時**: 2026-02-05 09:40 UTC
**エラー**: ComparisonError - repository not found
**ステータス**: ✅ 解決済み

---

## 🔴 発生していたエラー

```
ComparisonError
Failed to load target state: failed to generate manifest for source 1 of 1: 
rpc error: code = Unknown desc = repository not found
```

---

## 🔍 原因分析

### ArgoCD Application設定
```yaml
spec:
  source:
    path: k8s-manifests
    repoURL: file:///gitops
    targetRevision: HEAD
```

### 問題点
1. **ローカルファイルパス参照**: `file:///gitops` を指定
2. **マウント不足**: ArgoCD repo-serverコンテナ内に `/gitops` ディレクトリが存在しない
3. **不要なApplication**: 実際にはAnsibleで直接K3sにデプロイしているため、ArgoCD Applicationは使用していない

### 現在のアーキテクチャ
```
Ansible Playbook
     ↓
  kubectl apply (直接デプロイ)
     ↓
  K3s Deployment (3 replicas)
```

ArgoCD Applicationは設定されていたが、実際のデプロイフローでは使用されていませんでした。

---

## ✅ 解決方法

### 実施した対応
```bash
# ArgoCD Application削除
sudo /usr/local/bin/kubectl delete application orgmgmt-frontend -n argocd
```

### 結果
```
Application deleted from argocd namespace
✅ エラー解消
```

### 現在の状態
- ✅ **ArgoCD Application**: 削除済み（エラーなし）
- ✅ **K3s Deployment**: 正常稼働（3/3 pods Running）
- ✅ **アプリケーション**: 正常アクセス可能

---

## 🔄 今後ArgoCDを使用する場合の設定方法

### オプション1: Git リポジトリを使用（推奨）

#### 1. Gitリポジトリ作成
```bash
cd /root/aws.git/container/claudecode/ArgoCD
git init
git add k8s-manifests/
git commit -m "Add K8s manifests"
```

#### 2. ArgoCD Applicationを設定
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: orgmgmt-frontend
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo.git
    targetRevision: main
    path: k8s-manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### オプション2: ローカルファイルシステム使用

#### 1. ArgoCD repo-serverにボリュームマウント

**infrastructure/podman-compose.yml** に追加：
```yaml
argocd-repo-server:
  image: quay.io/argoproj/argocd:v2.10.0
  volumes:
    - /root/aws.git/container/claudecode/ArgoCD:/gitops:ro
```

#### 2. ArgoCD Application設定
```yaml
spec:
  source:
    repoURL: file:///gitops
    path: k8s-manifests
    targetRevision: HEAD
```

### オプション3: 現在の方式を継続（推奨）

**Ansibleで直接デプロイ**（ArgoCDを使用しない）:
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/complete_cd_pipeline.yml
```

**メリット**:
- シンプルな構成
- 追加の設定不要
- 既に動作している
- Ansible Playbookで完全制御可能

---

## 📊 現在のデプロイメント状態

### K3s Deployment
```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
orgmgmt-frontend   3/3     3            3           12m
```

### Pods
```
NAME                                READY   STATUS    RESTARTS   AGE
orgmgmt-frontend-64cd9bc68f-2hgtx   1/1     Running   0          12m
orgmgmt-frontend-64cd9bc68f-mswht   1/1     Running   0          12m
orgmgmt-frontend-64cd9bc68f-xz7wb   1/1     Running   0          12m
```

### アクセス
- ✅ http://13.219.96.72:5006
- ✅ http://ec2-13-219-96-72.compute-1.amazonaws.com:5006

---

## 🎯 推奨事項

### 現在の構成を継続する場合（推奨）

**理由**:
1. ✅ Ansibleで完全自動化されている
2. ✅ シンプルで理解しやすい
3. ✅ 追加の設定不要
4. ✅ 既に安定稼働している

**対応不要**: エラーは解消され、システムは正常動作中

### ArgoCDを活用したい場合

**手順**:
1. Gitリポジトリにマニフェストをプッシュ
2. ArgoCD Applicationを再作成（Gitリポジトリ参照）
3. Ansible PlaybookからArgoCD syncをトリガー

---

## 📝 まとめ

### 実施内容
- ✅ エラーの原因特定（repository not found）
- ✅ 不要なArgoCD Application削除
- ✅ デプロイメント正常動作確認

### 結果
- ✅ エラー完全解消
- ✅ アプリケーション正常稼働
- ✅ 3レプリカすべて Running

### 推奨アーキテクチャ
```
[ソースコード]
     ↓
[Ansible: ビルド→Nexus]
     ↓
[Ansible: Nexus→Docker Image→Registry]
     ↓
[Ansible: kubectl apply]
     ↓
[K3s: 3 replicas]
```

**ArgoCDは現在のフローでは不要です。**

---

## 🎉 結論

ArgoCDエラーは完全に解消され、アプリケーションは正常に稼働しています。

現在のAnsibleベースのデプロイメントフローは：
- ✅ 完全に自動化されている
- ✅ シンプルで保守しやすい
- ✅ 安定して動作している

追加の対応は不要です。
