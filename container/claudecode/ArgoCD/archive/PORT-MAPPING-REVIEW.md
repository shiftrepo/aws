# ポート番号見直し - Issue #123 要件対応

**更新日**: 2026-02-05
**要件**: Issue #123に記載された利用可能なポート番号のみを使用

---

## 📋 Issue #123 で指定された利用可能ポート

```
3000, 8501, 8000, 8082, 8083, 5001, 5002, 5003, 5004, 5005, 5006
```

**重要な制約**:
- ユーザは外部IPを通して接続
- すべてのノードからの接続を許可
- 上記ポートのみ開放済み

---

## 🔍 現在のポート使用状況

| サービス | 現在のポート | 状態 | 利用可能リストに含まれるか |
|---------|-------------|------|------------------------|
| PostgreSQL | 5432 | 使用中 | ❌ No |
| pgAdmin | 5050 | 使用中 | ❌ No |
| Nexus HTTP | 8081 | 使用中 | ❌ No |
| Nexus Docker | 8082 | 使用中 | ✅ Yes |
| GitLab HTTP | 5003 | 使用中 | ✅ Yes |
| GitLab Registry | 5005 | 使用中 | ✅ Yes |
| GitLab SSH | 2222 | 使用中 | ❌ No |
| ArgoCD | 30010 (NodePort) | 使用中 | ❌ No |
| Frontend | 5006 | 未使用 (予定) | ✅ Yes |
| Backend | 8080 | 未使用 (予定) | ❌ No |
| Redis | 6379 | 使用中 (内部) | ❌ No |

**問題**: 現在のポート割り当ての多くが利用可能リストに含まれていない

---

## ✅ 新しいポートマッピング計画

### 外部公開サービス (利用可能ポートに変更)

| サービス | 旧ポート | 新ポート | 理由 |
|---------|---------|---------|------|
| **PostgreSQL** | 5432 | **5001** | 外部接続必要 |
| **pgAdmin** | 5050 | **5002** | Web UI外部アクセス |
| **Nexus HTTP** | 8081 | **8000** | Web UI + Maven Repository |
| **Nexus Docker** | 8082 | **8082** | ✅ 既に利用可能リスト内 |
| **GitLab HTTP** | 5003 | **5003** | ✅ 既に利用可能リスト内 |
| **GitLab Registry** | 5005 | **5005** | ✅ 既に利用可能リスト内 |
| **ArgoCD** | 30010 | **8501** | Web UI外部アクセス |
| **Frontend** | 5006 | **5006** | ✅ 既に利用可能リスト内 |
| **Backend API** | 8080 | **8083** | REST API外部アクセス |

### 内部専用サービス (変更不要)

| サービス | ポート | 公開範囲 | 備考 |
|---------|-------|---------|------|
| Redis | 6379 | 内部のみ | コンテナネットワーク内 |
| GitLab SSH | 2222 | 削除検討 | 外部SSH不要ならポート開放不要 |

### 利用可能だが未使用のポート

- **3000** - 予備
- **5004** - 予備
- **8083** → Backend APIに割り当て済み

---

## 🔧 必要な変更作業

### 1. Infrastructure サービス (Podman)

**ファイル**: `infrastructure/podman-compose.yml`

```yaml
# PostgreSQL
postgres:
  ports:
    - "5001:5432"  # 変更: 5432 → 5001

# pgAdmin
pgadmin:
  ports:
    - "5002:80"  # 変更: 5050 → 5002

# Nexus
nexus:
  ports:
    - "8000:8081"  # 変更: 8081 → 8000
    - "8082:8082"  # 変更なし (既にリスト内)

# GitLab (変更なし - 既にリスト内)
gitlab:
  ports:
    - "5003:5003"
    - "5005:5005"
    - "2222:22"  # SSH削除を検討

# ArgoCD用ポート開放不要 (K3s NodePort対応)
```

### 2. ArgoCD (Kubernetes)

**NodePort変更**: 30010 → 8501

**方法**: K3s APIサーバーのポートマッピング設定が必要

**問題**: K3sのNodePortはデフォルトで30000-32767の範囲
**解決策**: K3s Service LoadBalancerまたはIngressを使用

```yaml
# Option 1: LoadBalancer Service
apiVersion: v1
kind: Service
metadata:
  name: argocd-server-external
  namespace: argocd
spec:
  type: LoadBalancer
  externalIPs:
    - <host-ip>
  ports:
    - port: 8501
      targetPort: 8080
  selector:
    app.kubernetes.io/name: argocd-server
```

または

```yaml
# Option 2: HostPort (より簡単)
# Deployment patchでhostPort追加
```

### 3. Application サービス (GitOps)

**ファイル**: `gitops/dev/podman-compose.yml` (未作成)

```yaml
# Backend
backend:
  ports:
    - "8083:8080"  # 外部: 8083, 内部: 8080

# Frontend
frontend:
  ports:
    - "5006:80"  # 既に正しい
```

---

## 📝 Ansible Playbook 変更

### 修正が必要なPlaybook

1. **infrastructure/deploy_infrastructure.yml**
   - PostgreSQL, pgAdmin, Nexusのポート変更

2. **ansible/playbooks/install_k3s_and_argocd.yml**
   - ArgoCDアクセスポート変更 (8501)

3. **新規作成: ansible/playbooks/configure_argocd_external_access.yml**
   - ArgoCD外部アクセス用LoadBalancer/HostPort設定

### infrastructure/.env 更新

```bash
# PostgreSQL
POSTGRES_PORT=5001  # 変更: 5432 → 5001

# pgAdmin
PGADMIN_PORT=5002  # 変更: 5050 → 5002

# Nexus
NEXUS_HTTP_PORT=8000  # 変更: 8081 → 8000
NEXUS_DOCKER_PORT=8082  # 変更なし

# GitLab (変更なし)
GITLAB_HTTP_PORT=5003
GITLAB_REGISTRY_PORT=5005
GITLAB_SSH_PORT=2222  # 削除検討

# ArgoCD
ARGOCD_SERVER_PORT=8501  # 変更: 30010 → 8501

# Application
APP_BACKEND_PORT=8083  # 変更: 8080 → 8083
APP_FRONTEND_PORT=5006  # 変更なし
```

---

## 🚀 実装手順

### Phase 1: インフラストラクチャポート変更

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure

# 1. .env更新
# 2. podman-compose.yml更新
# 3. 既存コンテナ停止
podman-compose down

# 4. 新ポートで再起動
podman-compose up -d
```

### Phase 2: ArgoCD外部アクセス設定

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# Ansible playbook実行
ansible-playbook -i inventory/hosts.yml \
  playbooks/configure_argocd_external_access.yml
```

### Phase 3: 検証

```bash
# PostgreSQL
psql -h localhost -p 5001 -U orgmgmt_user -d postgres

# pgAdmin
curl http://localhost:5002

# Nexus
curl http://localhost:8000

# GitLab
curl http://localhost:5003

# ArgoCD
curl http://localhost:8501
```

---

## 📊 変更後のポートマップ全体像

```
外部ポート  →  内部ポート    サービス           状態
──────────────────────────────────────────────────
5001       →  5432         PostgreSQL         ✅ 利用可能リスト内
5002       →  80           pgAdmin            ✅ 利用可能リスト内
5003       →  5003         GitLab HTTP        ✅ 既に正しい
5004       →  (未使用)      予備               ✅ 利用可能
5005       →  5005         GitLab Registry    ✅ 既に正しい
5006       →  80           Frontend           ✅ 既に正しい
8000       →  8081         Nexus HTTP         ✅ 利用可能リスト内
8082       →  8082         Nexus Docker       ✅ 既に正しい
8083       →  8080         Backend API        ✅ 利用可能リスト内
8501       →  8080         ArgoCD UI          ✅ 利用可能リスト内
3000       →  (未使用)      予備               ✅ 利用可能
```

**すべてのポートが利用可能リストに含まれる** ✅

---

## ⚠️ 影響範囲

### ドキュメント更新が必要

1. **POSTGRESQL-SETUP-COMPLETE.md**
   - 接続ポート: 5432 → 5001

2. **K3S-ARGOCD-INSTALLATION-REPORT.md**
   - ArgoCD アクセスポート: 30010 → 8501

3. **argocd-credentials.txt**
   - URL更新

4. **すべてのREADME**
   - ポート情報更新

### アプリケーション設定更新が必要

1. **application.yml** (Backend)
   ```yaml
   spring:
     datasource:
       url: jdbc:postgresql://postgres:5432/orgmgmt
   ```
   → 内部接続なので変更不要

2. **Frontend API設定**
   ```javascript
   const API_URL = 'http://localhost:8083/api'
   ```
   → 8080から8083に変更

---

## ✅ 次のアクション

1. **即座に実施**: ポート番号を変更したAnsible playbookを作成
2. **検証**: すべてのサービスが新ポートで正常動作することを確認
3. **ドキュメント更新**: すべての関連ドキュメントを更新
4. **Issue #123更新**: ポート変更完了を報告

---

**作成日**: 2026-02-05
**ステータス**: ⚠️ 変更計画策定完了、実装待ち
**優先度**: 🔴 HIGH (Issue #123要件)
