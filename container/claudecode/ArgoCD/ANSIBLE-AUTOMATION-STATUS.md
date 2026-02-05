# Ansible自動化ステータス確認

**日時**: 2026-02-05 08:50 UTC

---

## 📋 要求される4つのステップ

1. **構成するサービス環境を構築**
2. **コンパイルしたものをNexusに登録**
3. **Nexusに登録されたアーティファクトから実行環境のコンテナイメージを生成しレジストリに登録**
4. **レジストリに登録されたコンテナイメージからアプリケーションサービスを起動**

---

## ✅ 現在の実装状況

### ステップ1: 構成するサービス環境を構築 ✅

**実装済みプレイブック**:
- `ansible/playbooks/deploy_infrastructure.yml` - インフラ構築
- `ansible/playbooks/install_k3s_and_argocd.yml` - K3s/ArgoCD設定
- `ansible/playbooks/install_build_tools.yml` - ビルドツール導入

**実装内容**:
- PostgreSQL 16
- Nexus Repository 3
- K3s (Kubernetes)
- ArgoCD v2.10.0
- Build Tools (Maven, Node.js, NPM)

**ステータス**: ✅ **完全に自動化済み**

---

### ステップ2: コンパイルしたものをNexusに登録 ✅

**実装済みプレイブック**:
- `ansible/playbooks/build_and_deploy_artifacts.yml`

**実装内容**:
- Backend: Maven clean package → Nexus maven-snapshots
- Frontend: NPM build → Nexus npm-hosted (tarball)

**ステータス**: ✅ **完全に自動化済み**

---

### ステップ3: Nexusからコンテナイメージ生成 ❌

**現状**: ⚠️ **部分的に実装**

**問題点**:
- 現在の `deploy_frontend_with_argocd.yml` はローカルの `dist` ディレクトリから直接イメージをビルド
- Nexusに登録されたアーティファクトを使用していない
- 完全な自動化フローが実現できていない

**必要な実装**:
1. Nexusからアーティファクトをダウンロード
2. ダウンロードしたアーティファクトからDockerイメージをビルド
3. ローカルレジストリにプッシュ

**ステータス**: ❌ **未実装（要対応）**

---

### ステップ4: レジストリからサービス起動 ✅

**実装済みプレイブック**:
- `ansible/playbooks/deploy_frontend_with_argocd.yml`

**実装内容**:
- K3s deploymentの作成
- Kubernetes serviceの作成
- ArgoCD applicationの作成
- 3レプリカ + ラウンドロビン

**ステータス**: ✅ **完全に自動化済み**

---

## 🎯 総合評価

| ステップ | ステータス | 自動化率 |
|---------|----------|---------|
| 1. 環境構築 | ✅ | 100% |
| 2. ビルド→Nexus | ✅ | 100% |
| 3. Nexus→イメージ | ❌ | 0% |
| 4. イメージ→起動 | ✅ | 100% |
| **合計** | ⚠️ | **75%** |

---

## 🔍 現在のワークフロー

### 実際の動作

```
1. [Ansible] 環境構築
   ↓
2. [Ansible] ソースコード → ビルド → Nexus登録
   ↓
3. [手動] ローカルdist → Dockerイメージ作成 ← ❌ 手動
   ↓
4. [Ansible] レジストリ登録 → K3sデプロイ
```

### あるべき姿

```
1. [Ansible] 環境構築
   ↓
2. [Ansible] ソースコード → ビルド → Nexus登録
   ↓
3. [Ansible] Nexusダウンロード → Dockerイメージ作成 ← ✅ 自動化必要
   ↓
4. [Ansible] レジストリ登録 → K3sデプロイ
```

---

## 📝 詳細分析

### 現在のデプロイメントプロセス

#### deploy_frontend_with_argocd.yml の動作

```yaml
# Phase 3: フロントエンドビルド
- name: Install NPM dependencies
  shell: |
    cd {{ app_dir }}
    npm install

- name: Build frontend
  shell: |
    cd {{ app_dir }}
    npm run build

# Phase 4: コンテナイメージビルド
- name: Build frontend container image
  shell: |
    cd {{ base_dir }}
    podman build \
      -f {{ container_builder_dir }}/Dockerfile.frontend-simple \
      -t {{ image_full }} \
      .
```

**問題**:
- `npm run build` でローカルビルドを実行
- `dist` ディレクトリから直接Dockerイメージを作成
- Nexusに登録されたアーティファクトを使用していない

### あるべきプロセス

```yaml
# Phase 3: Nexusからアーティファクトダウンロード
- name: Download frontend artifact from Nexus
  get_url:
    url: "{{ nexus_url }}/repository/npm-hosted/..."
    dest: "/tmp/frontend.tgz"

- name: Extract frontend artifact
  unarchive:
    src: "/tmp/frontend.tgz"
    dest: "/tmp/frontend-dist"

# Phase 4: コンテナイメージビルド（Nexusアーティファクト使用）
- name: Build frontend container image from Nexus artifact
  shell: |
    podman build \
      -f {{ container_builder_dir }}/Dockerfile.frontend-from-nexus \
      -t {{ image_full }} \
      /tmp/frontend-dist
```

---

## 🔧 必要な対応

### 1. Dockerfile作成（Nexus用）

**新規ファイル**: `container-builder/Dockerfile.frontend-from-nexus`

```dockerfile
# Stage 1: Download from Nexus
FROM curlimages/curl:latest AS downloader
ARG NEXUS_URL=http://localhost:8000
ARG ARTIFACT_PATH=repository/npm-hosted/@orgmgmt/frontend/-/frontend-1.0.0.tgz

RUN curl -o /tmp/frontend.tgz \
  ${NEXUS_URL}/${ARTIFACT_PATH}

RUN tar -xzf /tmp/frontend.tgz -C /tmp/

# Stage 2: Nginx runtime
FROM nginx:1.25-alpine

COPY --from=downloader /tmp/package/dist /usr/share/nginx/html
COPY container-builder/nginx-with-mock-api-fixed.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Ansibleプレイブック更新

**更新ファイル**: `ansible/playbooks/build_and_deploy_artifacts.yml`

**追加内容**:
- フロントエンドアーティファクトのtarball作成
- Nexusへのアップロード
- アーティファクトURLの記録

### 3. 新規統合プレイブック作成

**新規ファイル**: `ansible/playbooks/complete_cd_pipeline.yml`

**内容**:
1. ソースコードビルド
2. Nexusにアーティファクト登録
3. Nexusからアーティファクトダウンロード
4. Dockerイメージビルド
5. レジストリ登録
6. K3sデプロイ

---

## 📋 実装すべきタスク

### 優先度: 高

- [ ] **Task 1**: Dockerfile.frontend-from-nexus 作成
- [ ] **Task 2**: フロントエンドtarballをNexusに登録する処理追加
- [ ] **Task 3**: complete_cd_pipeline.yml プレイブック作成
- [ ] **Task 4**: Nexusからのダウンロード処理実装
- [ ] **Task 5**: 既存プレイブックの統合

### 優先度: 中

- [ ] **Task 6**: バックエンド用のDockerfile作成（Nexus対応）
- [ ] **Task 7**: エラーハンドリング追加
- [ ] **Task 8**: ロールバック機能実装

### 優先度: 低

- [ ] **Task 9**: ドキュメント更新
- [ ] **Task 10**: テストプレイブック作成

---

## 🎯 実装後の期待される動作

### 完全自動化フロー

```bash
# 1コマンドで完全なCD実行
ansible-playbook -i inventory/hosts.yml playbooks/complete_cd_pipeline.yml
```

**実行内容**:
1. ✅ ソースコードをビルド（Maven, NPM）
2. ✅ Nexusにアーティファクト登録
3. ✅ Nexusからアーティファクトダウンロード
4. ✅ Dockerイメージビルド（Nexusアーティファクト使用）
5. ✅ ローカルレジストリにプッシュ
6. ✅ K3sでデプロイメント（ArgoCD経由）
7. ✅ サービス起動確認

**所要時間**: 約10-15分

---

## 🚀 次のステップ

### 即座に実装すべき項目

1. **complete_cd_pipeline.yml の作成**
   - すべてのステップを統合
   - Nexusからのダウンロード処理追加
   - エラーハンドリング

2. **Dockerfile.frontend-from-nexus の作成**
   - Multi-stage build
   - Nexusからアーティファクトダウンロード
   - Nginx設定適用

3. **build_and_deploy_artifacts.yml の更新**
   - フロントエンドtarball作成
   - Nexusアップロード処理追加

---

## 📊 現状まとめ

### できていること ✅

- Ansible完全自動化: 環境構築、ビルド、Nexus登録、デプロイ
- 3レプリカ + ラウンドロビン負荷分散
- ArgoCD統合
- モックAPI実装

### できていないこと ❌

- **Nexusからのアーティファクトダウンロード→イメージビルド**
- 完全なCD自動化フロー
- ステップ3の自動化

### 影響

現時点では、**手動でビルドしたdistディレクトリを使用**しているため、完全なCI/CD自動化は実現できていません。

---

## 結論

**回答**: いいえ、現時点ですべてをAnsibleで実現できていません。

**達成率**: 75%（4ステップ中3ステップ完了）

**不足部分**: ステップ3（Nexusからコンテナイメージ生成）

**推奨対応**: 完全自動化プレイブック（complete_cd_pipeline.yml）の作成が必要です。
