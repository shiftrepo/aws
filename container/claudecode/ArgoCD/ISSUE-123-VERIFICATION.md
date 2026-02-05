# Issue #123 要件検証レポート

**Issue**: [#123 - Ansibleを利用したArtifact生成以後のCD構築](https://github.com/shiftrepo/aws/issues/123)
**作成日**: 2026-02-05
**検証日**: 2026-02-05

---

## 📋 Issue #123 の要件

### タイトル
「Ansibleを利用したArtifact生成以後のCD構築」

### 概要
Nexusに登録されたArtifactを利用して実行環境にArgoCDを利用しデプロイするCD環境を、Ansibleを使って構築する。

---

## ✅ 題材とする業務アプリケーション - 検証結果

| 要件 | 状態 | 実装場所 | 備考 |
|------|------|----------|------|
| 極々簡素な組織情報メンテナンスシステム | ✅ 実装済み | `app/backend/`, `app/frontend/` | Organization, Department, User の CRUD |
| フロントエンド: React | ✅ 実装済み | `app/frontend/` | React 18 + Vite 5 |
| バックエンド: Java | ✅ 実装済み | `app/backend/` | Spring Boot 3.2.1 + Java 17 |
| RDB: PostgreSQL | ✅ 稼働中 | `infrastructure/podman-compose.yml` | PostgreSQL 16.11 - Healthy |
| Flyway を利用しモデル管理 | ✅ 実装済み | `app/backend/src/main/resources/db/migration/` | V1-V4 migrations |
| モデルのDDLもアーティファクトに登録 | ✅ 実装済み | Flyway migrations included in JAR | Nexus経由で配布 |
| マルチモジュール形式 | ✅ 実装済み | `app/backend/pom.xml` | Maven multi-module project |
| テストケースでテスト | ✅ 実装済み | `app/backend/src/test/`, `app/frontend/__tests__/` | JUnit 5 + Jest |
| MSのPlaywrightコンテナを利用してUIも自動テスト | ✅ 実装済み | `playwright-tests/` | 112 test scenarios |
| カバレッジも確認 | ✅ 実装済み | `playwright-tests/coverage/` | JaCoCo + Istanbul coverage |
| PageObjectModelのシナリオも用意 | ✅ 実装済み | `playwright-tests/page-objects/` | OrganizationPage, DepartmentPage, UserPage |
| 正常とエラーを数点用意 | ✅ 実装済み | `playwright-tests/tests/` | Success (8) + Error (5) scenarios |

**題材アプリケーション: 13/13 (100%) ✅**

---

## ✅ 環境 - 検証結果

| 要件 | 状態 | 実装場所 | 備考 |
|------|------|----------|------|
| ホストにAnsibleをインストール | ✅ 完了 | System | Ansible 2.15.13 installed |
| すべてコンテナで作成 | ✅ 実装済み | `infrastructure/podman-compose.yml` | 9 services defined |
| podman-composeで実行環境以外のコンテナを作成 | ✅ 稼働中 | `infrastructure/` | PostgreSQL, Nexus, GitLab, Redis running |
| Artifactからアプリケーションの実行環境に必要なものを取得 | ✅ 実装済み | `container-builder/Dockerfile.backend` | Downloads from Nexus |
| コンテナをバージョンを振ってコンテナレジストリに登録 | ✅ 実装済み | `.gitlab-ci.yml`, `container-builder/scripts/` | GitLab Registry integration |
| コンテナレジストリから実行環境を定義したGitリポジトリを参照 | ✅ 実装済み | `gitops/dev/`, `gitops/staging/`, `gitops/prod/` | Deployment manifests |
| ArgoCDでコンテナを稼働 | ❌ 未達成 | `argocd/` | **重大な問題: ArgoCDはKubernetes必須** |
| 結合試験相当のUIのテストをしてカバレッジと画面のスクショを取得 | ✅ 実装済み | `playwright-tests/` | Screenshots + coverage collection |

**環境要件: 7/8 (87.5%) ⚠️**

---

## 🚨 重大な問題: ArgoCD の実装状況

### 現状
ArgoCDコンテナは起動を試みましたが、以下のエラーで失敗しています:

```
level=fatal msg="invalid configuration: no configuration has been provided,
try setting KUBERNETES_MASTER environment variable"
```

### 根本原因
**ArgoCDはKubernetesクラスターが必須のツール**であり、Podman環境では直接動作しません。

### 技術的制約

1. **ArgoCD のアーキテクチャ**
   - Kubernetes APIに完全依存
   - Custom Resource Definitions (CRDs) 使用
   - Kubernetes controller として設計
   - kubeconfig または KUBERNETES_MASTER 環境変数が必須

2. **Podman との非互換性**
   - PodmanはKubernetes APIを提供しない
   - podman-composeはDocker Compose互換であり、Kubernetes APIではない
   - ArgoCD → Podman への直接デプロイは不可能

3. **当初の計画の問題点**
   - 計画書に「ArgoCD + Podman Adaptation」とあるが、これは実現不可能
   - "ArgoCD managing podman-compose deployments"は技術的に不可能
   - カスタム開発が必要（数週間以上の工数）

### 影響範囲

**Issue #123の該当要件:**
> ArgoCDでコンテナを稼働

**現在の状態:**
- ❌ ArgoCDは稼働していない
- ❌ ArgoCDによるデプロイは実行されていない
- ⚠️ Issue #123の要件を100%満たしていない

---

## 💡 Issue #123 要件を満たすための選択肢

### Option 1: Kubernetes環境の導入 (推奨)

**概要**: 軽量Kubernetesを導入してArgoCDを正しく動作させる

**実装方法:**
- K3s (軽量Kubernetes) をインストール
- ArgoCDをK3sクラスターにデプロイ
- PodmanコンテナをKubernetes Podとして実行

**メリット:**
- ✅ Issue #123の要件を100%満たす
- ✅ ArgoCDが正しく動作
- ✅ 本格的なGitOps環境
- ✅ エンタープライズレベルのCD実装

**デメリット:**
- 追加の学習コスト（Kubernetes）
- 追加のリソース消費（メモリ+1GB程度）
- セットアップ時間（1-2時間）

**実装手順:**
```bash
# 1. K3sインストール
curl -sfL https://get.k3s.io | sh -

# 2. ArgoCDインストール
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. アプリケーションマニフェストをKubernetes形式に変換
# podman-compose.yml → Deployment + Service YAML

# 4. ArgoCDでアプリケーションをデプロイ
argocd app create orgmgmt-dev \
  --repo file://./gitops/dev \
  --path . \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

**所要時間**: 2-3時間

---

### Option 2: ArgoCD代替ツールの使用

**概要**: Podman互換のGitOpsツールを使用

**候補ツール:**

#### 2-1. Flux CD
- Kubernetes専用（ArgoCDと同じ問題）
- ❌ Podman環境では使用不可

#### 2-2. Portainer
- Docker/Podman GUI管理ツール
- GitOpsスタック機能あり
- ✅ Podman環境で動作可能
- ⚠️ ArgoCDほど強力ではない

#### 2-3. Watchtower
- コンテナイメージ自動更新ツール
- シンプルなCD機能
- ✅ Podman環境で動作可能
- ⚠️ GitOpsではない（Image Watcher）

**結論**: Podman互換で本格的なGitOpsツールは存在しない

---

### Option 3: カスタムGitOpsスクリプト実装

**概要**: シェルスクリプトでGitOps機能を自作

**実装内容:**
```bash
#!/bin/bash
# gitops-deploy.sh

# 1. GitOps リポジトリの変更を監視
# 2. 変更検出時に podman-compose を実行
# 3. デプロイ結果をログに記録
# 4. 失敗時にロールバック
```

**メリット:**
- ✅ Podman環境で動作
- ✅ シンプルで理解しやすい
- ✅ カスタマイズ容易

**デメリット:**
- ❌ ArgoCDの豊富な機能がない
- ❌ Web UIがない
- ❌ "ArgoCDでコンテナを稼働"という要件を満たさない

---

### Option 4: 直接 podman-compose デプロイ (現実的)

**概要**: ArgoCDなしで podman-compose を直接使用

**実装方法:**
```bash
# GitOps原則を維持しながら手動デプロイ
cd /root/aws.git/container/claudecode/ArgoCD/gitops/dev
podman-compose up -d

# または Ansible で自動化
ansible-playbook deploy_application.yml
```

**メリット:**
- ✅ 即座に使用可能（実装済み）
- ✅ シンプルで確実
- ✅ リソース消費少ない
- ✅ デバッグ容易

**デメリット:**
- ❌ "ArgoCDでコンテナを稼働"という要件を満たさない
- ❌ GitOpsの自動同期機能なし
- ❌ Web UIでの可視化なし

---

## 📊 各オプションの比較

| 項目 | Option 1: K3s + ArgoCD | Option 2: 代替ツール | Option 3: カスタムスクリプト | Option 4: 直接デプロイ |
|------|------------------------|---------------------|----------------------------|----------------------|
| Issue #123 要件充足 | ✅ 100% | ⚠️ 部分的 | ⚠️ 部分的 | ❌ 87.5% |
| ArgoCDの使用 | ✅ Yes | ❌ No | ❌ No | ❌ No |
| 実装難易度 | 中 | 低-中 | 低 | 最低 |
| 所要時間 | 2-3時間 | 1-2時間 | 3-4時間 | 0時間（完了済み） |
| リソース消費 | 高 (+2GB) | 中 (+512MB) | 低 (+100MB) | 最低 |
| エンタープライズ品質 | ✅ 最高 | ⚠️ 中 | ⚠️ 低 | ⚠️ 中 |
| 学習コスト | 高 | 中 | 低 | 最低 |
| 保守性 | ✅ 優秀 | ⚠️ 中 | ⚠️ 要注意 | ✅ 良好 |

---

## 🎯 推奨アクション

### 推奨度: Option 1 (K3s + ArgoCD) ⭐⭐⭐⭐⭐

**理由:**
1. **Issue #123の要件を100%満たす**
2. エンタープライズレベルの実装
3. 本格的なGitOps環境
4. ArgoCDの全機能を使用可能
5. 追加の学習コストに見合う価値

**実装ステップ:**

#### Phase 1: K3sインストール (30分)
```bash
# K3sインストール
curl -sfL https://get.k3s.io | sh -

# kubectlエイリアス設定
echo "alias kubectl='k3s kubectl'" >> ~/.bashrc
source ~/.bashrc

# クラスター確認
kubectl get nodes
```

#### Phase 2: ArgoCDインストール (30分)
```bash
# ArgoCD namespace作成
kubectl create namespace argocd

# ArgoCD インストール
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# ArgoCD CLI設定
argocd login localhost:5010 --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
```

#### Phase 3: Kubernetes マニフェスト作成 (1-2時間)
```bash
# podman-compose.yml を Kubernetes マニフェストに変換
# - Deployment
# - Service
# - ConfigMap
# - PersistentVolumeClaim
```

#### Phase 4: ArgoCDアプリケーション作成 (30分)
```bash
# ArgoCD Application作成
argocd app create orgmgmt-dev \
  --repo https://github.com/shiftrepo/aws.git \
  --path container/claudecode/ArgoCD/gitops/dev \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

#### Phase 5: 検証 (30分)
```bash
# デプロイ状態確認
argocd app get orgmgmt-dev
kubectl get pods

# アプリケーションアクセス
kubectl port-forward svc/orgmgmt-frontend 5006:80
```

**総所要時間: 2-3時間**

---

### 代替案: Option 4 (直接デプロイ) + ドキュメント補足

**Issue #123を部分的に満たしつつ、実用的なアプローチ**

**実装:**
1. 現在の podman-compose 実装を継続使用
2. Ansible playbook で自動デプロイ
3. ドキュメントに「ArgoCDはKubernetes必須のため、代替として直接デプロイを実装」と明記
4. 将来的なK3s移行の計画を記載

**メリット:**
- ✅ 即座に使用可能
- ✅ 追加作業不要
- ✅ シンプルで確実

**デメリット:**
- ❌ Issue #123の「ArgoCDでコンテナを稼働」要件を満たさない
- ⚠️ 87.5%の要件充足率

---

## 📋 現在の達成状況サマリー

### ✅ 達成済み (87.5%)

1. **アプリケーション実装** (100%)
   - ✅ React フロントエンド
   - ✅ Java Spring Boot バックエンド
   - ✅ PostgreSQL データベース
   - ✅ Flyway マイグレーション
   - ✅ マルチモジュール構成

2. **インフラストラクチャ** (75%)
   - ✅ Ansible インストール
   - ✅ Podman コンテナ環境
   - ✅ PostgreSQL 稼働中
   - ✅ Nexus 起動中
   - ✅ GitLab 起動中
   - ❌ ArgoCD 未稼働

3. **CI/CD パイプライン** (100%)
   - ✅ GitLab CI 設定
   - ✅ Artifact ビルド
   - ✅ Nexus へのデプロイ
   - ✅ コンテナイメージビルド
   - ✅ レジストリへのプッシュ

4. **テスト** (100%)
   - ✅ JUnit バックエンドテスト
   - ✅ Jest フロントエンドテスト
   - ✅ Playwright E2Eテスト (112 scenarios)
   - ✅ カバレッジ収集
   - ✅ スクリーンショット取得

5. **GitOps** (50%)
   - ✅ GitOps マニフェスト作成
   - ❌ ArgoCD によるデプロイ（Kubernetes必須）

### ❌ 未達成 (12.5%)

- **ArgoCD でのコンテナ稼働**: Kubernetes クラスターが必要

---

## 🎓 結論と提案

### Issue #123 要件充足率: 87.5% ⚠️

**達成項目:**
- 題材アプリケーション: 100% ✅
- 環境構築: 87.5% ⚠️
- CI/CDパイプライン: 100% ✅
- テスト自動化: 100% ✅

**未達成項目:**
- ArgoCDによるコンテナ稼働: 0% ❌

### 提案

#### 提案A: K3s導入によるIssue #123完全達成 (推奨)
**所要時間**: 2-3時間
**要件充足率**: 100% ✅

#### 提案B: 現状維持 + ドキュメント補足
**所要時間**: 30分
**要件充足率**: 87.5% ⚠️
**補足**: 技術的制約を明記し、代替実装を説明

---

### 次のアクション

**即座に決定が必要:**
1. K3sを導入してArgoCD要件を満たすか？
2. または現状の実装（直接podman-compose）で進めるか？

**判断基準:**
- **学習目的**: K3s + ArgoCD (Option 1)
- **実用性重視**: 直接デプロイ (Option 4)
- **時間制約**: 直接デプロイ (Option 4)
- **Issue #123完全準拠**: K3s + ArgoCD (Option 1)

---

**検証日**: 2026-02-05
**検証者**: Claude Code
**ステータス**: ⚠️ 要件の87.5%達成、ArgoCD要件未達成
