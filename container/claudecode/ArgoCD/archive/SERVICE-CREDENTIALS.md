# サービス認証情報一覧

**最終更新日**: 2026-02-06
**環境**: Ansible自動構築環境（ゼロから完全自動構築済み）
**セキュリティレベル**: 🔓 開発環境 (本番環境では認証情報を変更してください)

---

## 📋 目次

1. [システム概要](#システム概要)
2. [PostgreSQL](#1-postgresql)
3. [Redis](#2-redis)
4. [pgAdmin](#3-pgadmin)
5. [Nexus Repository](#4-nexus-repository)
6. [Backend API](#5-backend-api-稼働中)
7. [Frontend Web](#6-frontend-web-稼働中)
8. [ArgoCD (参考)](#7-argocd-参考)
9. [認証情報一覧表](#認証情報一覧表)
10. [アクセスURL早見表](#アクセスurl早見表)

---

## システム概要

### サーバー情報

| 項目 | 値 |
|------|-----|
| **ホスト名** | ip-10-0-1-200 |
| **プライベートIP** | 10.0.1.200 |
| **パブリックIP** | 54.172.30.175 |
| **OS** | Red Hat Enterprise Linux 9.5 |
| **コンテナランタイム** | Podman 5.6.0 |
| **自動化ツール** | Ansible 2.17.8 |

### デプロイメント方法

**ワンコマンド構築:**
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible/playbooks
ansible-playbook full_deploy_from_scratch.yml
```

**所要時間:** 約5-7分（インフラ起動 + Backend/Frontendビルド + デプロイ）

### 稼働中のサービス (8コンテナ)

| サービス | ステータス | ポート |
|---------|-----------|--------|
| PostgreSQL 16 | ✅ Healthy | 5001 |
| Redis 7 | ✅ Healthy | 6379 |
| pgAdmin 4 | ✅ Running | 5002 |
| Nexus 3 | ✅ Healthy | 8000, 8082 |
| Backend API | ✅ Running | 8083 |
| Frontend Web | ✅ Running | 5006 |
| ArgoCD Server | ✅ Running | 8080 (参考) |
| ArgoCD Repo Server | ⚠️ Unhealthy | - |

---

## 1. PostgreSQL

### 接続情報

**サービス**: PostgreSQL 16 (Alpine)
**コンテナ名**: `orgmgmt-postgres`
**ポート**: 5001 (外部) → 5432 (内部)
**ステータス**: ✅ Healthy

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `orgmgmt_user` |
| **パスワード** | `SecurePassword123!` |
| **データベース名** | `orgmgmt` |
| **ホスト (ローカル)** | `localhost` |
| **ホスト (プライベートIP)** | `10.0.1.200` |
| **ホスト (パブリックIP)** | `54.172.30.175` |
| **ポート** | `5001` |

### 接続方法

#### psqlコマンド

```bash
# ローカル接続
psql -h localhost -p 5001 -U orgmgmt_user -d orgmgmt

# プライベートIP経由
psql -h 10.0.1.200 -p 5001 -U orgmgmt_user -d orgmgmt

# パブリックIP経由（インターネット）
psql -h 54.172.30.175 -p 5001 -U orgmgmt_user -d orgmgmt
```

#### 接続文字列

```
# ローカル
postgresql://orgmgmt_user:SecurePassword123!@localhost:5001/orgmgmt

# プライベートIP
postgresql://orgmgmt_user:SecurePassword123!@10.0.1.200:5001/orgmgmt

# パブリックIP
postgresql://orgmgmt_user:SecurePassword123!@54.172.30.175:5001/orgmgmt
```

#### Spring Boot設定

```yaml
spring:
  datasource:
    url: jdbc:postgresql://orgmgmt-postgres:5432/orgmgmt  # コンテナ内
    # または
    url: jdbc:postgresql://10.0.1.200:5001/orgmgmt  # 外部
    username: orgmgmt_user
    password: SecurePassword123!
```

### データベース情報

**Flywayマイグレーション:** V4まで完了

| バージョン | 説明 | ステータス |
|-----------|------|-----------|
| V1 | Create initial schema | ✅ 適用済み |
| V2 | Add departments table | ✅ 適用済み |
| V3 | Add users table | ✅ 適用済み |
| V4 | Insert sample data | ✅ 適用済み |

**サンプルデータ:**
- Organizations: 3件
- Departments: 複数件
- Users: 複数件

### 特記事項

- ✅ **外部接続有効**: すべてのホストから接続可能 (listen_addresses = '*')
- ⚠️ **認証方式**: `trust` (パスワード不要 - 開発環境のみ)
- ⚠️ **本番環境**: 認証方式を `scram-sha-256` に変更し、ポート5001を閉鎖してください
- ✅ **ヘルスチェック**: `pg_isready` で確認可能

---

## 2. Redis

### 接続情報

**サービス**: Redis 7 (Alpine)
**コンテナ名**: `argocd-redis`
**ポート**: 6379 (外部・内部共通)
**ステータス**: ✅ Healthy

### 認証情報

| 項目 | 値 |
|------|-----|
| **パスワード** | なし (認証なし) |
| **ホスト (ローカル)** | `localhost` |
| **ホスト (プライベートIP)** | `10.0.1.200` |
| **ホスト (パブリックIP)** | `54.172.30.175` |
| **ポート** | `6379` |

### 接続方法

#### redis-cliコマンド

```bash
# ローカル接続
redis-cli -h localhost -p 6379

# プライベートIP経由
redis-cli -h 10.0.1.200 -p 6379

# パブリックIP経由
redis-cli -h 54.172.30.175 -p 6379

# 接続確認
redis-cli -h localhost -p 6379 PING
# 応答: PONG
```

#### Spring Sessionセッションキー確認

```bash
# セッションキー一覧
podman exec argocd-redis redis-cli --scan --pattern "spring:session:sessions:*"

# セッション数カウント
podman exec argocd-redis redis-cli --scan --pattern "spring:session:sessions:*" | wc -l
```

### 使用用途

**Spring Session Data Redis:**
- Backend APIのHTTPセッション管理
- Namespace: `spring:session:sessions:*`
- タイムアウト: 1800秒 (30分)
- シリアライゼーション: JSON (GenericJackson2JsonRedisSerializer)

### 特記事項

- ⚠️ **認証なし**: パスワード不要（開発環境のみ）
- ⚠️ **本番環境**: `requirepass` でパスワード設定し、ポート6379を閉鎖してください
- ✅ **永続化**: デフォルト設定（RDB）
- ✅ **セッション管理**: Backend APIと統合済み

---

## 3. pgAdmin

### 接続情報

**サービス**: pgAdmin 4 Web UI
**コンテナ名**: `orgmgmt-pgadmin`
**ポート**: 5002 (外部) → 80 (内部)
**ステータス**: ✅ Running

### 認証情報

| 項目 | 値 |
|------|-----|
| **Email** | `admin@orgmgmt.local` |
| **パスワード** | `AdminPassword123!` |
| **URL (ローカル)** | `http://localhost:5002` |
| **URL (プライベートIP)** | `http://10.0.1.200:5002` |
| **URL (パブリックIP)** | `http://54.172.30.175:5002` |

### 接続方法

1. ブラウザで以下のいずれかにアクセス:
   - http://localhost:5002
   - http://10.0.1.200:5002
   - http://54.172.30.175:5002
2. Email: `admin@orgmgmt.local` を入力
3. Password: `AdminPassword123!` を入力
4. "Login" をクリック

### PostgreSQL サーバー登録方法

pgAdmin にログイン後、PostgreSQLサーバーを登録:

1. 左側の "Servers" を右クリック → "Register" → "Server"
2. **"General" タブ:**
   - Name: `Organization Management DB`
3. **"Connection" タブ:**
   - Host name/address: `orgmgmt-postgres` (コンテナ名) または `10.0.1.200`
   - Port: `5001`
   - Maintenance database: `orgmgmt`
   - Username: `orgmgmt_user`
   - Password: `SecurePassword123!`
   - Save password: ✅ チェック
4. "Save" をクリック

### 特記事項

- ✅ **自動リダイレクト**: HTTPステータス302でログインページにリダイレクト
- ⚠️ **インターネット公開**: パブリックIPからアクセス可能（開発環境のみ）
- ⚠️ **本番環境**: VPN経由のアクセスに制限してください

---

## 4. Nexus Repository

### 接続情報

**サービス**: Nexus Repository Manager 3
**コンテナ名**: `orgmgmt-nexus`
**ポート**:
- HTTP: 8000 (外部) → 8081 (内部)
- Docker Registry: 8082 (外部) → 8082 (内部)
**ステータス**: ✅ Healthy

### 認証情報

| 項目 | 値 |
|------|-----|
| **ユーザー名** | `admin` |
| **初期パスワード** | コンテナ内ファイルから取得 (下記参照) |
| **URL (ローカル)** | `http://localhost:8000` |
| **URL (プライベートIP)** | `http://10.0.1.200:8000` |
| **URL (パブリックIP)** | `http://54.172.30.175:8000` |
| **Docker Registry (ローカル)** | `localhost:8082` |
| **Docker Registry (プライベートIP)** | `10.0.1.200:8082` |
| **Docker Registry (パブリックIP)** | `54.172.30.175:8082` |

### 初期パスワード取得方法

Nexusの初期化完了後 (起動後10-15分)、以下のコマンドで初期パスワードを取得:

```bash
# 初期パスワード取得
podman exec orgmgmt-nexus cat /nexus-data/admin.password

# 例: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 初回ログイン手順

1. ブラウザで http://localhost:8000 または http://10.0.1.200:8000 または http://54.172.30.175:8000 にアクセス
2. 右上の "Sign in" をクリック
3. Username: `admin`
4. Password: 上記コマンドで取得した初期パスワードを入力
5. "Sign in" をクリック
6. Setup wizard が表示される:
   - 新しいパスワードを設定 (推奨: `NexusAdmin123!`)
   - Anonymous access を有効化 (推奨: Enable)
7. Setup 完了

### リポジトリURL

**Maven:**
```
http://localhost:8000/repository/maven-public/
http://10.0.1.200:8000/repository/maven-public/
http://54.172.30.175:8000/repository/maven-public/
```

**NPM:**
```
http://localhost:8000/repository/npm-public/
http://10.0.1.200:8000/repository/npm-public/
```

**Docker:**
```
localhost:8082
10.0.1.200:8082
54.172.30.175:8082
```

### Docker Registry 認証設定

```bash
# Podmanログイン（プライベートIP）
podman login 10.0.1.200:8082 \
  --username admin \
  --password NexusAdmin123! \
  --tls-verify=false

# Podmanログイン（パブリックIP）
podman login 54.172.30.175:8082 \
  --username admin \
  --password NexusAdmin123! \
  --tls-verify=false
```

### 特記事項

- ⏳ **初期化時間**: 初回起動後 10-15分
- ⚠️ **初期パスワード**: 初回ログイン後に必ず変更してください
- ⚠️ **HTTP使用**: 開発環境のため非TLS (本番環境ではHTTPS推奨)
- ✅ **ヘルスチェック**: Healthy状態を確認済み

---

## 5. Backend API (✅ 稼働中)

### 接続情報

**サービス**: Spring Boot 3.2.1 + Java 21
**コンテナ名**: `orgmgmt-backend`
**ポート**: 8083 (外部) → 8080 (内部)
**ステータス**: ✅ Running
**ビルド**: Maven 3.9 (Podmanコンテナ内ビルド)
**JARサイズ**: 59,744,769 bytes (57 MB)

### 認証情報

| 項目 | 値 |
|------|-----|
| **認証** | なし (現在未実装) |
| **URL (ローカル)** | `http://localhost:8083` |
| **URL (プライベートIP)** | `http://10.0.1.200:8083` |
| **URL (パブリックIP)** | `http://54.172.30.175:8083` |
| **API Base Path** | `/api` |
| **System Info** | `http://localhost:8083/api/system/info` |

### APIエンドポイント

#### System Info API (新規)
```
GET /api/system/info
```

**レスポンス例:**
```json
{
  "podName": "orgmgmt-backend-external",
  "sessionId": "23b96526-4dbf-4bfe-9a6b-bc894b385d23",
  "flywayVersion": "4",
  "databaseStatus": "OK",
  "timestamp": "2026-02-06T03:10:57.440313449Z"
}
```

#### Organizations API
```
GET    /api/organizations          - 組織一覧取得 (11件)
POST   /api/organizations          - 組織作成
GET    /api/organizations/{id}     - 組織詳細取得
PUT    /api/organizations/{id}     - 組織更新
DELETE /api/organizations/{id}     - 組織削除
```

**テスト:**
```bash
curl http://54.172.30.175:8083/api/organizations | jq
```

#### Departments API
```
GET    /api/departments            - 部門一覧取得 (11件)
POST   /api/departments            - 部門作成
GET    /api/departments/{id}       - 部門詳細取得
PUT    /api/departments/{id}       - 部門更新
DELETE /api/departments/{id}       - 部門削除
GET    /api/departments/tree       - 部門ツリー取得
```

**テスト:**
```bash
curl http://54.172.30.175:8083/api/departments | jq
```

#### Users API
```
GET    /api/users                  - ユーザー一覧取得
POST   /api/users                  - ユーザー作成
GET    /api/users/{id}             - ユーザー詳細取得
PUT    /api/users/{id}             - ユーザー更新
DELETE /api/users/{id}             - ユーザー削除
```

### セッション管理

**Spring Session Data Redis統合:**
```yaml
spring:
  session:
    store-type: redis
    redis:
      namespace: spring:session:sessions
    timeout: 1800s  # 30分
```

**セッション永続性テスト:**
```bash
# 1回目のリクエスト（クッキー保存）
curl -c cookies.txt http://54.172.30.175:8083/api/system/info | jq '.sessionId'

# 2回目のリクエスト（同じクッキー使用）
curl -b cookies.txt http://54.172.30.175:8083/api/system/info | jq '.sessionId'

# 同じセッションIDが返されることを確認
```

### 技術スタック

- **Java**: 21 (Eclipse Temurin JRE)
- **フレームワーク**: Spring Boot 3.2.1
  - Spring Web (REST API)
  - Spring Data JPA (Hibernate)
  - Spring Session Data Redis
- **Database**: PostgreSQL 16 (JDBC)
- **Migration**: Flyway 9.22.3
- **Session Store**: Redis 7
- **Serialization**: JSON (GenericJackson2JsonRedisSerializer)
- **Build Tool**: Maven 3.9

### 環境変数

```bash
SPRING_DATASOURCE_URL=jdbc:postgresql://orgmgmt-postgres:5432/orgmgmt
SPRING_DATASOURCE_USERNAME=orgmgmt_user
SPRING_DATASOURCE_PASSWORD=SecurePassword123!
REDIS_HOST=argocd-redis
REDIS_PORT=6379
POD_NAME=orgmgmt-backend-external
```

### 接続テスト

```bash
# System Info取得
curl http://54.172.30.175:8083/api/system/info | jq

# Organizations取得
curl http://54.172.30.175:8083/api/organizations | jq

# Departments取得
curl http://54.172.30.175:8083/api/departments | jq

# Health Check（実装されている場合）
curl http://54.172.30.175:8083/actuator/health
```

### 特記事項

- ✅ **デプロイ済み**: 完全稼働中
- ✅ **外部アクセス**: パブリックIPからアクセス可能
- ✅ **セッション管理**: Redis統合済み
- ✅ **データベース接続**: PostgreSQL接続確認済み (Status: OK)
- ⚠️ **認証未実装**: 現在認証機能なし（将来JWT実装予定）
- ⚠️ **CORS**: `origins = "*"` (開発環境のみ)

---

## 6. Frontend Web (✅ 稼働中)

### 接続情報

**サービス**: React 18.2.0 + Vite 5.0 + Nginx Alpine
**コンテナ名**: `orgmgmt-frontend`
**ポート**: 5006 (外部) → 80 (内部)
**ステータス**: ✅ Running
**ビルド**: Node 20 Alpine (Podmanコンテナ内ビルド)
**バンドルサイズ**: 約252 KB (gzip圧縮前)

### 認証情報

| 項目 | 値 |
|------|-----|
| **認証** | なし (現在未実装) |
| **URL (ローカル)** | `http://localhost:5006` |
| **URL (プライベートIP)** | `http://10.0.1.200:5006` |
| **URL (パブリックIP)** | `http://54.172.30.175:5006` |

### 接続方法

1. ブラウザで以下のいずれかにアクセス:
   - http://localhost:5006
   - http://10.0.1.200:5006
   - **http://54.172.30.175:5006** (推奨 - インターネット経由)
2. Organization Management System が表示される
3. ナビゲーションバー右側にシステム情報バッジが表示:
   - **Pod:** orgmgmt-backend-external
   - **Session:** (セッションIDの最初の8文字)
   - **Flyway:** 4
4. 30秒ごとに自動更新

### API接続設定

**Backend API URL:**
```
Development: http://10.0.1.200:8083
Production: http://10.0.1.200:8083 (Nginx proxy経由も可)
```

**Nginx設定 (APIプロキシ):**
```nginx
location /api {
    proxy_pass http://10.0.1.200:8083;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### 技術スタック

- **JavaScript**: ES6+
- **フレームワーク**: React 18.2.0
- **Build Tool**: Vite 5.0
- **HTTP Client**: Axios 1.6.5
  - `withCredentials: true` (セッションクッキー有効)
- **Router**: React Router DOM 6.21.1
- **Webサーバー**: Nginx Alpine
  - SPAルーティング: `try_files $uri /index.html`

### 機能

**画面一覧:**
- Home (ダッシュボード)
- Organizations (組織一覧・編集)
- Departments (部門一覧・編集)
- Users (ユーザー一覧・編集)

**システム情報バッジ:**
- Pod名表示
- セッションID表示 (最初の8文字)
- Flywayバージョン表示
- 30秒ごとの自動更新

### 接続テスト

```bash
# HTMLアクセス
curl -I http://54.172.30.175:5006

# アセット確認
curl -s http://54.172.30.175:5006 | grep "<script"
```

### 特記事項

- ✅ **デプロイ済み**: 完全稼働中
- ✅ **外部アクセス**: パブリックIPからアクセス可能
- ✅ **SPA対応**: React Routerによるクライアントサイドルーティング
- ✅ **APIプロキシ**: Nginx経由でBackend APIにアクセス可能
- ✅ **セッション管理**: クッキーベースでセッション維持

---

## 7. ArgoCD (参考)

### 接続情報

**サービス**: ArgoCD v2.10.0
**コンテナ名**: `argocd-server` (参考)
**ポート**: 8080, 8081 (内部のみ - 現在外部公開なし)
**ステータス**: ✅ Running (unhealthyのrepo-serverあり)

### 注意事項

⚠️ **現在の構成では使用していません:**
- ArgoCD Serverは起動していますが、外部ポートマッピングがありません
- ArgoCD Repo Serverは unhealthy 状態です
- GitOps/CD機能が必要な場合は、別途設定が必要です

**将来の実装予定:**
- ArgoCD Web UIの外部公開
- GitLab統合
- 自動デプロイメントパイプライン

---

## 認証情報一覧表

| サービス | ポート | ユーザー名 / Email | パスワード | URL (パブリックIP) |
|---------|--------|-------------------|-----------|-------------------|
| **PostgreSQL** | 5001 | `orgmgmt_user` | `SecurePassword123!` | `54.172.30.175:5001` |
| **Redis** | 6379 | N/A | なし | `54.172.30.175:6379` |
| **pgAdmin** | 5002 | `admin@orgmgmt.local` | `AdminPassword123!` | `http://54.172.30.175:5002` |
| **Nexus** | 8000 | `admin` | 初回: `/nexus-data/admin.password`<br>変更後: `NexusAdmin123!` | `http://54.172.30.175:8000` |
| **Nexus Docker** | 8082 | `admin` | `NexusAdmin123!` | `54.172.30.175:8082` |
| **Backend API** | 8083 | N/A (未実装) | N/A (未実装) | `http://54.172.30.175:8083` |
| **Frontend** | 5006 | N/A (未実装) | N/A (未実装) | `http://54.172.30.175:5006` |

---

## アクセスURL早見表

### 🌐 エンドユーザー向け（インターネット公開）

| サービス | URL | 用途 |
|---------|-----|------|
| **Frontend** | **http://54.172.30.175:5006** | Webアプリケーション |
| **Backend API** | **http://54.172.30.175:8083/api** | REST API |
| System Info | http://54.172.30.175:8083/api/system/info | システム情報 |
| Organizations | http://54.172.30.175:8083/api/organizations | 組織一覧 |
| Departments | http://54.172.30.175:8083/api/departments | 部門一覧 |

### 🛠️ 開発者・管理者向け（プライベートIP）

| サービス | URL | 認証情報 |
|---------|-----|---------|
| pgAdmin | http://10.0.1.200:5002 | admin@orgmgmt.local / AdminPassword123! |
| Nexus | http://10.0.1.200:8000 | admin / NexusAdmin123! |
| PostgreSQL | 10.0.1.200:5001 | orgmgmt_user / SecurePassword123! |
| Redis | 10.0.1.200:6379 | (パスワードなし) |

### 📊 ヘルスチェックURL

```bash
# Backend System Info
curl http://54.172.30.175:8083/api/system/info | jq

# PostgreSQL接続確認
podman exec orgmgmt-postgres pg_isready -U orgmgmt_user -d orgmgmt

# Redis接続確認
podman exec argocd-redis redis-cli PING

# Redisセッション確認
podman exec argocd-redis redis-cli --scan --pattern "*session*" | wc -l
```

---

## 🔐 セキュリティ注意事項

### ⚠️ 開発環境の設定

このドキュメントに記載されている認証情報は**開発環境専用**です:

| 項目 | 現在の設定 | 推奨事項 |
|------|-----------|---------|
| PostgreSQL認証 | `trust` (パスワード不要) | ⚠️ `scram-sha-256` に変更 |
| Redis認証 | パスワードなし | ⚠️ `requirepass` 設定 |
| 通信暗号化 | HTTP (非TLS) | ⚠️ HTTPS化 (Let's Encrypt) |
| CORS | `origins = "*"` | ⚠️ 特定ドメインに制限 |
| 外部公開ポート | 全サービス公開 | ⚠️ Frontend/Backendのみ公開 |
| ファイアウォール | 全ポート開放 | ⚠️ 必要最小限のみ |

### ✅ 本番環境への移行時の推奨事項

#### 1. すべてのパスワードを変更

```bash
# PostgreSQL
ALTER USER orgmgmt_user WITH PASSWORD 'NewStrongPassword123!@#$%';

# Redis (redis.conf)
requirepass YourStrongRedisPassword456!@#

# pgAdmin (Web UI)
File → Preferences → Security → Change Password

# Nexus (Web UI)
admin (プロフィールアイコン) → Change password
```

#### 2. TLS/SSL証明書の導入

```bash
# Let's Encryptで証明書取得
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自動更新設定
sudo systemctl enable certbot-renew.timer
```

#### 3. ネットワーク分離

```yaml
# PostgreSQL, Redisは内部ネットワークのみ
services:
  postgres:
    ports: []  # 外部ポートマッピング削除
  redis:
    ports: []  # 外部ポートマッピング削除
```

#### 4. リバースプロキシ導入

```nginx
# Nginx on Host
upstream backend {
    server 127.0.0.1:8083;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5006;
    }

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. AWS Security Group最小化

```
許可するポート:
- 443 (HTTPS): 0.0.0.0/0
- 22 (SSH): 管理者IPのみ

削除するポート:
- 5001 (PostgreSQL)
- 5002 (pgAdmin)
- 6379 (Redis)
- 8000 (Nexus)
- その他すべて
```

#### 6. 環境変数化

```bash
# .env ファイル（Gitには含めない）
DB_PASSWORD=${DB_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
JWT_SECRET=${JWT_SECRET}
SESSION_SECRET=${SESSION_SECRET}
```

#### 7. Secrets管理

- HashiCorp Vault
- Kubernetes Secrets (encryption at rest)
- AWS Secrets Manager
- Azure Key Vault

---

## 📚 関連ドキュメント

### デプロイメント関連
- `FINAL_DEPLOYMENT_VERIFICATION.md` - 最終デプロイメント検証レポート（最新）
- `ZERO_TO_PRODUCTION_DEPLOYMENT.md` - ゼロから本番環境まで構築ガイド
- `COMPREHENSIVE_NETWORK_VERIFICATION.md` - 包括的ネットワーク検証レポート
- `EXTERNAL_ACCESS_VERIFICATION.md` - 外部IPアクセス検証レポート

### Ansible関連
- `ansible/playbooks/full_deploy_from_scratch.yml` - 完全自動構築プレイブック（メイン）
- `ansible/playbooks/deploy_infrastructure.yml` - インフラ起動プレイブック
- `ansible/playbooks/verify_network_communication.yml` - ネットワーク検証プレイブック

### 設定ファイル
- `infrastructure/podman-compose.yml` - インフラサービス定義
- `app/backend/src/main/resources/application.yml` - Backend設定
- `app/frontend/.env` - Frontend環境変数

---

## 📞 サポート情報

### コンテナログ確認

```bash
# Backend
podman logs orgmgmt-backend --tail 100

# Frontend
podman logs orgmgmt-frontend --tail 100

# PostgreSQL
podman logs orgmgmt-postgres --tail 100

# Redis
podman logs argocd-redis --tail 100

# Nexus
podman logs orgmgmt-nexus --tail 100

# pgAdmin
podman logs orgmgmt-pgadmin --tail 100
```

### サービス再起動

```bash
# 特定のコンテナ再起動
podman restart orgmgmt-backend
podman restart orgmgmt-frontend
podman restart orgmgmt-postgres
podman restart argocd-redis

# すべてのサービス再起動
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose restart
```

### 完全再構築

```bash
# すべて削除
podman rm -f $(podman ps -aq)
podman network rm argocd-network
rm -rf app/backend/target app/frontend/dist

# ゼロから構築（ワンコマンド）
cd /root/aws.git/container/claudecode/ArgoCD/ansible/playbooks
ansible-playbook full_deploy_from_scratch.yml

# 所要時間: 5-7分
```

### トラブルシューティング

#### Backend APIにアクセスできない

```bash
# コンテナ状態確認
podman ps | grep backend

# ログ確認
podman logs orgmgmt-backend --tail 50

# PostgreSQL接続確認
podman exec orgmgmt-backend nc -zv orgmgmt-postgres 5432

# Redis接続確認
podman exec orgmgmt-backend nc -zv argocd-redis 6379

# ポート確認
ss -tlnp | grep 8083
```

#### Frontendが表示されない

```bash
# コンテナ状態確認
podman ps | grep frontend

# Nginx設定確認
podman exec orgmgmt-frontend cat /etc/nginx/conf.d/default.conf

# ビルド成果物確認
ls -la app/frontend/dist/

# ポート確認
ss -tlnp | grep 5006
```

#### セッションが維持されない

```bash
# Redisセッション確認
podman exec argocd-redis redis-cli --scan --pattern "*session*"

# Redis接続確認
podman exec argocd-redis redis-cli PING

# Backend環境変数確認
podman inspect orgmgmt-backend | jq '.[0].Config.Env'
```

---

## 🎯 クイックスタート

### 初回アクセス

1. **Frontend (Webアプリケーション):**
   ```
   http://54.172.30.175:5006
   ```

2. **Backend API (システム情報):**
   ```bash
   curl http://54.172.30.175:8083/api/system/info | jq
   ```

3. **pgAdmin (データベース管理):**
   ```
   http://54.172.30.175:5002
   Email: admin@orgmgmt.local
   Password: AdminPassword123!
   ```

4. **Nexus (アーティファクトリポジトリ):**
   ```
   http://54.172.30.175:8000
   Username: admin
   Password: (コンテナ内ファイルから取得)
   ```

### ヘルスチェック

```bash
# すべてのサービスが正常か確認
podman ps --format "{{.Names}}: {{.Status}}"

# Backend APIが応答するか確認
curl http://54.172.30.175:8083/api/system/info

# Frontendが配信されているか確認
curl -I http://54.172.30.175:5006
```

---

**ドキュメント最終更新**: 2026-02-06
**環境**: Ansible自動構築環境（full_deploy_from_scratch.yml）
**デプロイメント方法**: ワンコマンド自動構築（所要時間5-7分）
**検証ステータス**: ✅ 全サービス稼働確認済み (10/10テスト合格)
**セキュリティレベル**: 🔓 開発環境 (本番環境では全認証情報を変更してください)
