# サービス認証情報一覧

**環境**: Issue #123 準拠環境
**作成日**: 2026-02-05
**セキュリティレベル**: 開発環境 (本番環境では認証情報を変更してください)

---

## 📋 目次

1. [PostgreSQL](#1-postgresql)
2. [pgAdmin](#2-pgadmin)
3. [Nexus Repository](#3-nexus-repository)
4. [GitLab](#4-gitlab)
5. [ArgoCD](#5-argocd)
6. [Backend API](#6-backend-api-未デプロイ)
7. [Frontend Web](#7-frontend-web-未デプロイ)
8. [認証情報一覧表](#認証情報一覧表)

---

## 1. PostgreSQL

### 接続情報

**サービス**: PostgreSQL 16
**ポート**: 5001 (Issue #123 準拠)
**データベース**: orgmgmt

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `orgmgmt_user` |
| **パスワード** | `SecurePassword123!` |
| **データベース名** | `orgmgmt` |
| **ホスト (ローカル)** | `localhost` |
| **ホスト (外部)** | `10.0.1.191` |
| **ポート** | `5001` |

### 接続方法

**psql コマンド**:
```bash
# ローカル接続
psql -h localhost -p 5001 -U orgmgmt_user -d orgmgmt

# 外部接続
psql -h 10.0.1.191 -p 5001 -U orgmgmt_user -d orgmgmt
```

**接続文字列**:
```
# ローカル
postgresql://orgmgmt_user:SecurePassword123!@localhost:5001/orgmgmt

# 外部
postgresql://orgmgmt_user:SecurePassword123!@10.0.1.191:5001/orgmgmt
```

**Java/Spring Boot**:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5001/orgmgmt
    username: orgmgmt_user
    password: SecurePassword123!
```

### 特記事項

- ✅ **外部接続有効**: すべてのホストから接続可能
- ⚠️ **認証方式**: `trust` (パスワード不要 - 開発環境のみ)
- ⚠️ **本番環境**: 認証方式を `md5` または `scram-sha-256` に変更してください

---

## 2. pgAdmin

### 接続情報

**サービス**: pgAdmin 4 Web UI
**ポート**: 5002 (Issue #123 準拠)

### 認証情報

| 項目 | 値 |
|------|-----|
| **Email** | `admin@example.com` |
| **パスワード** | `AdminPassword123!` |
| **URL (ローカル)** | `http://localhost:5002` |
| **URL (外部)** | `http://10.0.1.191:5002` |

### 接続方法

1. ブラウザで http://localhost:5002 または http://10.0.1.191:5002 にアクセス
2. Email: `admin@example.com` を入力
3. Password: `AdminPassword123!` を入力
4. "Login" をクリック

### PostgreSQL サーバー登録方法

pgAdmin にログイン後、PostgreSQLサーバーを登録:

1. 左側の "Servers" を右クリック → "Register" → "Server"
2. "General" タブ:
   - Name: `Local PostgreSQL`
3. "Connection" タブ:
   - Host name/address: `orgmgmt-postgres` (コンテナ名) または `10.0.1.191`
   - Port: `5001`
   - Maintenance database: `orgmgmt`
   - Username: `orgmgmt_user`
   - Password: `SecurePassword123!`
   - Save password: チェック
4. "Save" をクリック

---

## 3. Nexus Repository

### 接続情報

**サービス**: Nexus Repository Manager 3.63.0
**ポート**:
- HTTP: 8000 (Issue #123 準拠)
- Docker: 8082 (Issue #123 準拠)

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `admin` |
| **初期パスワード** | コンテナ内ファイルから取得 (下記参照) |
| **URL (ローカル)** | `http://localhost:8000` |
| **URL (外部)** | `http://10.0.1.191:8000` |
| **Docker Registry (ローカル)** | `localhost:8082` |
| **Docker Registry (外部)** | `10.0.1.191:8082` |

### 初期パスワード取得方法

Nexusの初期化完了後 (起動後10-15分)、以下のコマンドで初期パスワードを取得:

```bash
# 初期パスワード取得
podman exec orgmgmt-nexus cat /nexus-data/admin.password

# または
podman exec -it orgmgmt-nexus bash
cat /nexus-data/admin.password
```

### 初回ログイン手順

1. ブラウザで http://localhost:8000 にアクセス
2. 右上の "Sign in" をクリック
3. Username: `admin`
4. Password: 上記コマンドで取得した初期パスワードを入力
5. "Sign in" をクリック
6. Setup wizard が表示される:
   - 新しいパスワードを設定 (推奨: `NexusAdmin123!`)
   - Anonymous access を有効化 (推奨: Enable)
7. Setup 完了

### リポジトリURL

**Maven**:
```
http://localhost:8000/repository/maven-public/
http://localhost:8000/repository/maven-snapshots/
http://localhost:8000/repository/maven-releases/
```

**NPM**:
```
http://localhost:8000/repository/npm-public/
http://localhost:8000/repository/npm-proxy/
```

**Docker**:
```
localhost:8082
10.0.1.191:8082
```

### Docker Registry 認証設定

```bash
# Docker/Podman ログイン
podman login localhost:8082 \
  --username admin \
  --password NexusAdmin123! \
  --tls-verify=false
```

### 特記事項

- ⏳ **初期化時間**: 初回起動後 10-15分
- ⚠️ **初期パスワード**: 初回ログイン後に必ず変更してください
- ⚠️ **HTTP使用**: 開発環境のため非TLS (本番環境ではHTTPS推奨)

---

## 4. GitLab

### 接続情報

**サービス**: GitLab CE (Community Edition)
**ポート**:
- HTTP: 5003 (Issue #123 準拠)
- Registry: 5005 (Issue #123 準拠)
- SSH: 2222 (内部のみ)

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `root` |
| **パスワード** | `GitLabRoot123!` |
| **URL (ローカル)** | `http://localhost:5003` |
| **URL (外部)** | `http://10.0.1.191:5003` |
| **Registry (ローカル)** | `localhost:5005` |
| **Registry (外部)** | `10.0.1.191:5005` |

### 接続方法

**Web UI ログイン**:
1. ブラウザで http://localhost:5003 または http://10.0.1.191:5003 にアクセス
2. Username: `root`
3. Password: `GitLabRoot123!`
4. "Sign in" をクリック

**Git コマンド (HTTP)**:
```bash
# リポジトリクローン
git clone http://root:GitLabRoot123!@localhost:5003/root/project-name.git

# または認証情報を後で入力
git clone http://localhost:5003/root/project-name.git
Username: root
Password: GitLabRoot123!
```

**Git コマンド (SSH)**:
```bash
# SSH設定 (カスタムポート 2222)
git clone ssh://git@localhost:2222/root/project-name.git

# ~/.ssh/config に以下を追加
Host localhost
  Port 2222
  User git
```

### GitLab Runner トークン

GitLab Runner のトークンは以下の方法で取得:

1. GitLab Web UI にログイン
2. 左側メニュー → "Admin" → "CI/CD" → "Runners"
3. "New instance runner" をクリック
4. トークンをコピー

### Container Registry ログイン

```bash
# Docker/Podman ログイン
podman login localhost:5005 \
  --username root \
  --password GitLabRoot123! \
  --tls-verify=false

# 外部アクセス
podman login 10.0.1.191:5005 \
  --username root \
  --password GitLabRoot123! \
  --tls-verify=false
```

### イメージのPush/Pull

```bash
# イメージのタグ付け
podman tag my-app:latest localhost:5005/root/my-project/my-app:latest

# イメージのPush
podman push localhost:5005/root/my-project/my-app:latest

# イメージのPull
podman pull localhost:5005/root/my-project/my-app:latest
```

### 特記事項

- ⏳ **初期化時間**: 初回起動後 10-15分
- ⚠️ **HTTP使用**: 開発環境のため非TLS (本番環境ではHTTPS推奨)
- ⚠️ **SSH ポート**: 標準22番ではなく2222番を使用

---

## 5. ArgoCD

### 接続情報

**サービス**: ArgoCD v2.10.0
**ポート**:
- LoadBalancer (HTTP): 8501 (Issue #123 準拠)
- NodePort (HTTPS): 30010

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `admin` |
| **パスワード** | `3bDsm8ftlmbmWnRG` |
| **URL (LoadBalancer)** | `http://10.0.1.191:8501` |
| **URL (LoadBalancer ローカル)** | `http://localhost:8501` |
| **URL (NodePort HTTPS)** | `https://10.0.1.191:30010` |

### 接続方法

**Web UI ログイン (推奨: LoadBalancer)**:
1. ブラウザで http://localhost:8501 または http://10.0.1.191:8501 にアクセス
2. Username: `admin`
3. Password: `3bDsm8ftlmbmWnRG`
4. "Sign in" をクリック

**Web UI ログイン (NodePort HTTPS)**:
1. ブラウザで https://10.0.1.191:30010 にアクセス
2. 自己署名証明書の警告を受け入れる
3. Username: `admin`
4. Password: `3bDsm8ftlmbmWnRG`
5. "Sign in" をクリック

**CLI ログイン**:

```bash
# LoadBalancer経由 (HTTP) - 推奨
argocd login 10.0.1.191:8501 \
  --username admin \
  --password '3bDsm8ftlmbmWnRG' \
  --insecure

# NodePort経由 (HTTPS)
argocd login 10.0.1.191:30010 \
  --username admin \
  --password '3bDsm8ftlmbmWnRG' \
  --insecure

# Port Forward経由
kubectl port-forward svc/argocd-server -n argocd 8080:443 &
argocd login localhost:8080 \
  --username admin \
  --password '3bDsm8ftlmbmWnRG' \
  --insecure
```

### kubectl/k3s コマンド

```bash
# K3s kubectl使用
sudo /usr/local/bin/k3s kubectl get pods -n argocd

# または環境変数設定
export KUBECONFIG=/root/.kube/config
kubectl get pods -n argocd
```

### ArgoCD アプリケーション作成

```bash
# アプリケーション作成
argocd app create my-app \
  --repo http://localhost:5003/root/my-repo.git \
  --path gitops/dev \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default

# アプリケーション同期
argocd app sync my-app

# アプリケーション一覧
argocd app list
```

### 特記事項

- ✅ **Insecure Mode**: TLS検証なし (開発環境)
- ⚠️ **パスワード変更推奨**: 初回ログイン後にパスワード変更を推奨
- ⚠️ **認証情報ファイル**: `/root/argocd-credentials.txt` に保存済み

---

## 6. Backend API (未デプロイ)

### 接続情報

**サービス**: Spring Boot 3.2.1 + Java 17
**ポート**: 8083 (Issue #123 準拠)
**状態**: 📦 未デプロイ

### 予定認証情報

| 項目 | 値 |
|------|-----|
| **URL (ローカル)** | `http://localhost:8083` |
| **URL (外部)** | `http://10.0.1.191:8083` |
| **API Base Path** | `/api` |
| **Health Check** | `http://localhost:8083/actuator/health` |
| **API Info** | `http://localhost:8083/actuator/info` |

### API エンドポイント (予定)

**Organizations API**:
```
GET    /api/organizations          - 組織一覧取得
POST   /api/organizations          - 組織作成
GET    /api/organizations/{id}     - 組織詳細取得
PUT    /api/organizations/{id}     - 組織更新
DELETE /api/organizations/{id}     - 組織削除
```

**Departments API**:
```
GET    /api/departments            - 部門一覧取得
POST   /api/departments            - 部門作成
GET    /api/departments/{id}       - 部門詳細取得
PUT    /api/departments/{id}       - 部門更新
DELETE /api/departments/{id}       - 部門削除
GET    /api/departments/tree       - 部門ツリー取得
```

**Users API**:
```
GET    /api/users                  - ユーザー一覧取得
POST   /api/users                  - ユーザー作成
GET    /api/users/{id}             - ユーザー詳細取得
PUT    /api/users/{id}             - ユーザー更新
DELETE /api/users/{id}             - ユーザー削除
```

### デプロイ後の接続テスト

```bash
# Health Check
curl http://localhost:8083/actuator/health

# API Test
curl http://localhost:8083/api/organizations
```

### 特記事項

- 📦 **未デプロイ**: アプリケーションビルド・デプロイが必要
- ⚠️ **認証**: 現在認証機能なし (将来実装予定)

---

## 7. Frontend Web (未デプロイ)

### 接続情報

**サービス**: React 18 + Vite 5
**ポート**: 5006 (Issue #123 準拠)
**状態**: 📦 未デプロイ

### 予定認証情報

| 項目 | 値 |
|------|-----|
| **URL (ローカル)** | `http://localhost:5006` |
| **URL (外部)** | `http://10.0.1.191:5006` |

### デプロイ後の接続方法

1. ブラウザで http://localhost:5006 または http://10.0.1.191:5006 にアクセス
2. 組織管理画面が表示される

### API接続設定

フロントエンドは以下のBackend APIに接続:
```
API Base URL: http://localhost:8083/api
外部: http://10.0.1.191:8083/api
```

### 特記事項

- 📦 **未デプロイ**: アプリケーションビルド・デプロイが必要
- ⚠️ **プロキシ設定**: Nginx経由でBackend APIにプロキシ

---

## 認証情報一覧表

| サービス | ポート | ユーザー名 / Email | パスワード | URL |
|---------|--------|-------------------|-----------|-----|
| **PostgreSQL** | 5001 | `orgmgmt_user` | `SecurePassword123!` | `localhost:5001` |
| **pgAdmin** | 5002 | `admin@example.com` | `AdminPassword123!` | `http://localhost:5002` |
| **Nexus** | 8000 | `admin` | 初回: コンテナ内ファイルから取得<br>変更後: `NexusAdmin123!` | `http://localhost:8000` |
| **Nexus Docker** | 8082 | `admin` | `NexusAdmin123!` | `localhost:8082` |
| **GitLab** | 5003 | `root` | `GitLabRoot123!` | `http://localhost:5003` |
| **GitLab Registry** | 5005 | `root` | `GitLabRoot123!` | `localhost:5005` |
| **ArgoCD** | 8501 | `admin` | `3bDsm8ftlmbmWnRG` | `http://localhost:8501` |
| **Backend API** | 8083 | N/A (未実装) | N/A (未実装) | `http://localhost:8083` |
| **Frontend** | 5006 | N/A (未実装) | N/A (未実装) | `http://localhost:5006` |

---

## 🔐 セキュリティ注意事項

### 開発環境の設定

このドキュメントに記載されている認証情報は**開発環境専用**です:

- ✅ PostgreSQL: trust認証 (パスワード不要)
- ✅ すべてのサービス: HTTP (非TLS)
- ✅ ArgoCD: Insecure mode
- ✅ 固定パスワード使用

### 本番環境への移行時の推奨事項

**必須対応**:
1. ✅ **すべてのパスワードを変更**
   - 強力なパスワードポリシー適用
   - パスワード管理ツール使用 (1Password, LastPass等)

2. ✅ **TLS/SSL証明書の導入**
   - Let's Encrypt等で証明書取得
   - すべてのHTTPをHTTPSに変更

3. ✅ **PostgreSQL認証強化**
   - trust → md5 または scram-sha-256
   - listen_addresses の制限

4. ✅ **Secrets管理の強化**
   - HashiCorp Vault
   - Kubernetes Secrets (encrypted at rest)
   - AWS Secrets Manager

5. ✅ **ファイアウォール/ネットワーク設定**
   - 必要最小限のポートのみ開放
   - IPホワイトリスト設定
   - VPN経由のアクセスのみ許可

6. ✅ **RBAC (Role-Based Access Control)**
   - ArgoCD: RBACポリシー設定
   - GitLab: プロジェクト/グループごとの権限設定
   - PostgreSQL: ユーザー権限の最小化

7. ✅ **監査ログ**
   - すべてのサービスでログ有効化
   - 中央ログ管理 (ELK Stack, CloudWatch等)

### パスワード変更方法

**PostgreSQL**:
```sql
ALTER USER orgmgmt_user WITH PASSWORD 'NewStrongPassword123!@#';
```

**pgAdmin**:
- Web UI → File → Preferences → Security → Change Password

**Nexus**:
- Web UI → admin (プロフィールアイコン) → Change password

**GitLab**:
- Web UI → User Settings → Password → Change password

**ArgoCD**:
```bash
# 新しいパスワードでBcryptハッシュ生成
htpasswd -nbBC 10 "" NewPassword123! | tr -d ':\n' | sed 's/$2y/$2a/'

# Secretを更新
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {"admin.password": "生成したハッシュ"}}'
```

---

## 📚 関連ドキュメント

- `REBUILD-VERIFICATION-COMPLETE.md` - システム検証レポート
- `FINAL-VERIFICATION-COMPLETE.md` - 最終検証レポート
- `PORT-RECONFIGURATION-COMPLETE.md` - ポート再構成レポート
- `/root/argocd-credentials.txt` - ArgoCD認証情報詳細
- `infrastructure/.env` - 環境変数定義

---

## 📞 サポート情報

### コンテナログ確認

```bash
# PostgreSQL
podman logs orgmgmt-postgres

# Nexus
podman logs orgmgmt-nexus

# GitLab
podman logs orgmgmt-gitlab

# ArgoCD (K3s)
sudo /usr/local/bin/k3s kubectl logs -n argocd deployment/argocd-server
```

### サービス再起動

```bash
# 特定のコンテナ再起動
podman restart orgmgmt-postgres
podman restart orgmgmt-nexus
podman restart orgmgmt-gitlab

# すべてのインフラサービス再起動
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
/usr/local/bin/podman-compose restart

# ArgoCD再起動
sudo /usr/local/bin/k3s kubectl rollout restart -n argocd deployment/argocd-server
```

---

**ドキュメント作成日**: 2026-02-05
**環境**: Issue #123 準拠環境
**セキュリティレベル**: 🔓 開発環境 (本番環境では認証情報を変更してください)
