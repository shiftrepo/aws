# サービスアクセスガイド

**作成日**: 2026-02-05
**環境**: RHEL 9 / EC2インスタンス
**パブリックIP**: 13.219.96.72

---

## 📋 目次

1. [全サービス一覧](#全サービス一覧)
2. [Kubernetes Dashboard](#kubernetes-dashboard)
3. [ArgoCD](#argocd)
4. [フロントエンドアプリケーション](#フロントエンドアプリケーション)
5. [Nexus Repository](#nexus-repository)
6. [pgAdmin](#pgadmin)
7. [PostgreSQL](#postgresql)
8. [Container Registry](#container-registry)
9. [認証情報一覧表](#認証情報一覧表)
10. [トラブルシューティング](#トラブルシューティング)

---

## 全サービス一覧

| サービス | 外部URL | 内部ポート | 用途 | 認証 |
|---------|---------|-----------|------|------|
| **Kubernetes Dashboard** | https://13.219.96.72:5004 | 30443 | K3s Web管理 | Token |
| **ArgoCD** | http://13.219.96.72:5010 | 30799 | GitOps デプロイ | admin/password |
| **Frontend App** | http://13.219.96.72:5006 | 30006 | アプリケーション | なし |
| **Nexus** | http://13.219.96.72:8000 | 8081 | アーティファクト管理 | admin/admin123 |
| **pgAdmin** | http://13.219.96.72:5002 | 80 | DB管理 | admin@orgmgmt.local/password |
| **PostgreSQL** | 13.219.96.72:5001 | 5432 | データベース | orgmgmt_user/password |
| **Container Registry** | localhost:5000 | 5000 | コンテナイメージ | なし |
| **Redis** | localhost:6379 | 6379 | ArgoCD キャッシュ | なし |

---

## Kubernetes Dashboard

### アクセス情報

**URL:**
```
https://13.219.96.72:5004
https://ec2-13-219-96-72.compute-1.amazonaws.com:5004
```

**認証方式:** Token認証

### ログイン手順

#### 1. トークン取得

**コマンド:**
```bash
sudo /usr/local/bin/kubectl get secret admin-user-token \
  -n kubernetes-dashboard \
  -o jsonpath='{.data.token}' | base64 -d
```

**または:**
```bash
cat /tmp/kubernetes-dashboard-token.txt
```

#### 2. ブラウザでアクセス

1. https://13.219.96.72:5004 にアクセス
2. 証明書警告を承認（自己署名証明書のため）
   - Chrome/Edge: 「詳細設定」→「安全でないサイトに進む」
   - Firefox: 「詳細情報」→「危険を承認して続行」
3. ログイン画面で「Token」を選択
4. 取得したトークンを貼り付け
5. 「Sign in」をクリック

### トークン情報

**現在のトークン:**
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IlRGeDdyVlRWRUgyR08tdVJnaDlKWEZDM1V3Q2pJZzVrNGlFYmV5ejVWOUUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyYWE1ZDE4Yi0xYjA0LTQ0NTAtOGM5ZC04OTE2YzE5MTJhYjMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.D9gpvWNZdbGtOKUflSJmUyzYkpoO84G2qkti0ZRnme4UFgwjIml-DgdR50f0uwvl6egcVojoCuZYA-O_nPpAor94Fi1Jk8l66rXuEmZMPdGcpZjkMTxmx6zEAUGNfTXl1-5uhBZ0pC9BgtcICLGGm-0QFVY9qOYlmHAbNlo1CwYqyQdOwIOc-FMX70Sp3csl7u1-FLvmthru-m-P4cKcFtEAvRr2kSoSe0xeZWSaq9wvOhemkywSCa8JIBMhnnsXXAB7DTQom0IVt9djO11LIRPRFpyIItm6SBeY8FxULOu7JGEa0nzPWmesKAgsuLHg25B2N6KaMdL4eJRad1aHBg
```

**権限:** cluster-admin（全権限）
**有効期限:** なし（永続的）

### できること

- Pod、Deployment、Service の管理
- リソース使用状況の確認（CPU/Memory）
- ログの確認とリアルタイム表示
- Pod内でのコマンド実行
- YAML編集による設定変更
- レプリカ数のスケーリング
- リソースの削除と作成

---

## ArgoCD

### アクセス情報

**URL:**
```
http://13.219.96.72:5010
http://ec2-13-219-96-72.compute-1.amazonaws.com:5010
```

**認証方式:** ユーザー名/パスワード

### ログイン情報

**ユーザー名:** `admin`
**パスワード:** `3bDsm8ftlmbmWnRG`

### パスワード取得コマンド

```bash
sudo /usr/local/bin/kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```

### ログイン手順

1. http://13.219.96.72:5010 にアクセス
2. ユーザー名: `admin` を入力
3. パスワード: `3bDsm8ftlmbmWnRG` を入力
4. 「SIGN IN」をクリック

### ArgoCD CLI ログイン

```bash
argocd login 13.219.96.72:5010 \
  --username admin \
  --password 3bDsm8ftlmbmWnRG \
  --insecure
```

### 管理中のアプリケーション

**Application名:** `orgmgmt-frontend`
**Gitリポジトリ:** https://github.com/shiftrepo/aws.git
**パス:** container/claudecode/ArgoCD/gitops/orgmgmt-frontend
**ブランチ:** main
**同期ポリシー:** 自動同期（prune & self-heal 有効）

### よく使うコマンド

```bash
# アプリケーション一覧
argocd app list

# アプリケーション詳細
argocd app get orgmgmt-frontend

# 手動同期
argocd app sync orgmgmt-frontend

# デプロイ履歴
argocd app history orgmgmt-frontend

# ロールバック
argocd app rollback orgmgmt-frontend <revision>
```

---

## フロントエンドアプリケーション

### アクセス情報

**URL:**
```
http://13.219.96.72:5006
http://ec2-13-219-96-72.compute-1.amazonaws.com:5006
```

**認証:** なし（パブリックアクセス）

### アプリケーション情報

**フレームワーク:** React 18 + Vite
**レプリカ数:** 3
**ロードバランシング:** ラウンドロビン
**バックエンドAPI:** 内部ポート 8080

### API エンドポイント

```bash
# 組織一覧
curl http://13.219.96.72:5006/api/organizations

# 部門一覧
curl http://13.219.96.72:5006/api/departments

# ユーザー一覧
curl http://13.219.96.72:5006/api/users

# ヘルスチェック
curl http://13.219.96.72:5006/api/actuator/health
```

### 動作確認

```bash
# HTTPステータスコード確認
curl -s -o /dev/null -w '%{http_code}' http://13.219.96.72:5006/

# すべてのエンドポイントテスト
for endpoint in / /api/organizations /api/departments /api/users; do
  echo "Testing: $endpoint"
  curl -s -o /dev/null -w "Status: %{http_code}\n" http://13.219.96.72:5006$endpoint
done
```

---

## Nexus Repository

### アクセス情報

**URL:**
```
http://13.219.96.72:8000
http://ec2-13-219-96-72.compute-1.amazonaws.com:8000
```

### ログイン情報

**ユーザー名:** `admin`
**パスワード:** `admin123`

### 初回セットアップ（完了済み）

初期パスワードは変更済みです。現在のパスワードは `admin123` です。

### リポジトリ一覧

| リポジトリ名 | タイプ | URL | 用途 |
|------------|--------|-----|------|
| **maven-central** | proxy | https://repo1.maven.org/maven2/ | Maven プロキシ |
| **maven-releases** | hosted | - | リリース版 |
| **maven-snapshots** | hosted | - | スナップショット版 |
| **maven-public** | group | - | Maven グループ |
| **raw-hosted** | hosted | - | ビルド成果物 |
| **npm-proxy** | proxy | https://registry.npmjs.org | NPM プロキシ |
| **docker-hosted** | hosted | localhost:8082 | Docker イメージ |

### Mavenの設定

**~/.m2/settings.xml:**
```xml
<settings>
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>http://localhost:8000/repository/maven-public/</url>
    </mirror>
  </mirrors>
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>admin</username>
      <password>admin123</password>
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>admin</username>
      <password>admin123</password>
    </server>
  </servers>
</settings>
```

### アーティファクトアップロード

```bash
# curlでアップロード
curl -v -u admin:admin123 \
  --upload-file target/orgmgmt-frontend-1.0-SNAPSHOT.jar \
  http://localhost:8000/repository/raw-hosted/orgmgmt-frontend-1.0-SNAPSHOT.jar

# ダウンロード
curl -O http://localhost:8000/repository/raw-hosted/orgmgmt-frontend-1.0-SNAPSHOT.jar
```

---

## pgAdmin

### アクセス情報

**URL:**
```
http://13.219.96.72:5002
http://ec2-13-219-96-72.compute-1.amazonaws.com:5002
```

### ログイン情報

**Email:** `admin@orgmgmt.local`
**パスワード:** `password`

### データベース接続設定

#### 新しいサーバー登録

1. pgAdminにログイン
2. 左側ツリーで「Servers」を右クリック
3. 「Register」→「Server...」を選択

**General タブ:**
- Name: `OrgMgmt PostgreSQL`

**Connection タブ:**
- Host name/address: `orgmgmt-postgres`（Podmanネットワーク内）
  - または外部から: `13.219.96.72`
- Port: `5432`（内部）または `5001`（外部）
- Maintenance database: `orgmgmt`
- Username: `orgmgmt_user`
- Password: `password`
- Save password: ✓

### データベース情報

| 項目 | 値 |
|------|-----|
| データベース名 | orgmgmt |
| スキーマ | public |
| テーブル数 | 3 (organizations, departments, users) |
| エンコーディング | UTF8 |
| タイムゾーン | UTC |

---

## PostgreSQL

### アクセス情報

**外部接続:**
```
Host: 13.219.96.72
Port: 5001
```

**内部接続（Podmanネットワーク）:**
```
Host: orgmgmt-postgres
Port: 5432
```

### 認証情報

**データベース:** `orgmgmt`
**ユーザー名:** `orgmgmt_user`
**パスワード:** `password`

### psqlで接続

#### ホストOSから

```bash
# PostgreSQLクライアントがインストールされている場合
psql -h 13.219.96.72 -p 5001 -U orgmgmt_user -d orgmgmt

# Podman経由で接続
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt
```

#### パスワード入力を省略

**~/.pgpass ファイル作成:**
```bash
echo "13.219.96.72:5001:orgmgmt:orgmgmt_user:password" >> ~/.pgpass
chmod 600 ~/.pgpass
```

### データベーススキーマ

#### organizations テーブル
```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    established_date DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### departments テーブル
```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    parent_department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, code)
);
```

#### users テーブル
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### バックアップ・リストア

#### バックアップ

```bash
# Podman経由
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > backup.sql

# ホストOSから
pg_dump -h 13.219.96.72 -p 5001 -U orgmgmt_user orgmgmt > backup.sql
```

#### リストア

```bash
# Podman経由
podman exec -i orgmgmt-postgres psql -U orgmgmt_user orgmgmt < backup.sql

# ホストOSから
psql -h 13.219.96.72 -p 5001 -U orgmgmt_user orgmgmt < backup.sql
```

---

## Container Registry

### アクセス情報

**URL:** `localhost:5000`
**認証:** なし（insecureレジストリ）

### イメージのプッシュ

```bash
# タグ付け
podman tag localhost/orgmgmt-frontend:latest localhost:5000/orgmgmt-frontend:latest

# プッシュ
podman push localhost:5000/orgmgmt-frontend:latest --tls-verify=false
```

### イメージのプル

```bash
podman pull localhost:5000/orgmgmt-frontend:latest --tls-verify=false
```

### レジストリ内のイメージ一覧

```bash
# APIで確認
curl http://localhost:5000/v2/_catalog

# タグ一覧
curl http://localhost:5000/v2/orgmgmt-frontend/tags/list
```

### Podmanレジストリ設定

**/etc/containers/registries.conf.d/localhost.conf:**
```toml
[[registry]]
location = "localhost:5000"
insecure = true
```

---

## 認証情報一覧表

| サービス | URL | ユーザー名 | パスワード/Token | 取得方法 |
|---------|-----|-----------|-----------------|---------|
| **Kubernetes Dashboard** | https://13.219.96.72:5004 | - | Token認証 | `sudo kubectl get secret admin-user-token -n kubernetes-dashboard -o jsonpath='{.data.token}' \| base64 -d` |
| **ArgoCD** | http://13.219.96.72:5010 | admin | 3bDsm8ftlmbmWnRG | `sudo kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' \| base64 -d` |
| **Nexus** | http://13.219.96.72:8000 | admin | admin123 | 手動設定済み |
| **pgAdmin** | http://13.219.96.72:5002 | admin@orgmgmt.local | password | infrastructure/.env |
| **PostgreSQL** | 13.219.96.72:5001 | orgmgmt_user | password | infrastructure/.env |
| **Registry** | localhost:5000 | - | なし | 認証なし |

---

## トラブルシューティング

### サービスにアクセスできない

#### ポート転送サービスの確認

```bash
# 全ポート転送サービスの状態確認
systemctl status k3s-dashboard-forward
systemctl status k3s-frontend-forward
systemctl status k3s-argocd-forward

# 再起動
sudo systemctl restart k3s-dashboard-forward
sudo systemctl restart k3s-frontend-forward
```

#### ファイアウォール確認

```bash
# 開いているポート確認
sudo firewall-cmd --list-ports

# 必要なポートを開く
sudo firewall-cmd --permanent --add-port=5004/tcp
sudo firewall-cmd --permanent --add-port=5006/tcp
sudo firewall-cmd --permanent --add-port=5010/tcp
sudo firewall-cmd --reload
```

#### Podmanコンテナ確認

```bash
# コンテナ状態確認
podman ps -a

# コンテナログ確認
podman logs orgmgmt-nexus
podman logs orgmgmt-postgres
podman logs argocd-application-controller
```

### トークン/パスワードが無効

#### Kubernetes Dashboard トークン再取得

```bash
sudo /usr/local/bin/kubectl get secret admin-user-token \
  -n kubernetes-dashboard \
  -o jsonpath='{.data.token}' | base64 -d
```

#### ArgoCD パスワード再取得

```bash
sudo /usr/local/bin/kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```

#### Nexus パスワードリセット

```bash
# Nexusコンテナに入る
podman exec -it orgmgmt-nexus bash

# 管理者パスワードリセット（要再起動）
# /nexus-data/admin.password ファイルを確認
```

### データベース接続エラー

#### PostgreSQL接続テスト

```bash
# ホストOSから
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT version();"

# 外部から
psql -h 13.219.96.72 -p 5001 -U orgmgmt_user -d orgmgmt -c "SELECT 1;"
```

#### PostgreSQLログ確認

```bash
podman logs orgmgmt-postgres --tail 100
```

### K3s Pod が起動しない

```bash
# Pod状態確認
sudo /usr/local/bin/kubectl get pods -n default

# Pod詳細
sudo /usr/local/bin/kubectl describe pod <pod-name> -n default

# Podログ
sudo /usr/local/bin/kubectl logs <pod-name> -n default

# イベント確認
sudo /usr/local/bin/kubectl get events -n default --sort-by='.lastTimestamp' | tail -20
```

---

## セキュリティに関する注意事項

### 開発環境の設定

現在の設定は**開発環境向け**です：

⚠️ **注意事項:**
- 平文パスワードを使用
- 自己署名証明書（Kubernetes Dashboard）
- insecureレジストリ（TLS無効）
- すべてのポートが外部公開
- ArgoCD insecureモード

### 本番環境への推奨事項

✅ **推奨設定:**
- パスワードマネージャー（HashiCorp Vault等）を使用
- 正式なTLS証明書（Let's Encrypt等）
- レジストリにTLS認証を追加
- ファイアウォールで必要最小限のポート開放
- ArgoCD SSO/OIDC認証を有効化
- RBAC（Role-Based Access Control）を設定
- ネットワークポリシーを実装
- 定期的なパスワードローテーション

---

## クイックリファレンス

### すべてのサービスをテスト

```bash
echo "=== Service Health Check ==="
echo "Kubernetes Dashboard: $(curl -k -s -o /dev/null -w '%{http_code}' https://localhost:5004/)"
echo "ArgoCD: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5010/)"
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5006/)"
echo "Nexus: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/)"
echo "pgAdmin: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5002/)"
echo "PostgreSQL: $(podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c 'SELECT 1;' &>/dev/null && echo '200' || echo '500')"
```

### 全サービスの認証情報表示

```bash
cat << 'EOF'
=================================================
認証情報クイックリファレンス
=================================================

Kubernetes Dashboard (https://13.219.96.72:5004)
  Token: $(sudo /usr/local/bin/kubectl get secret admin-user-token -n kubernetes-dashboard -o jsonpath='{.data.token}' | base64 -d)

ArgoCD (http://13.219.96.72:5010)
  Username: admin
  Password: $(sudo /usr/local/bin/kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d)

Nexus (http://13.219.96.72:8000)
  Username: admin
  Password: admin123

pgAdmin (http://13.219.96.72:5002)
  Email: admin@orgmgmt.local
  Password: password

PostgreSQL (13.219.96.72:5001)
  Database: orgmgmt
  Username: orgmgmt_user
  Password: password

=================================================
EOF
```

---

## 関連ドキュメント

- `HOST-OS-COMMANDS.md` - ホストOSコマンドリファレンス
- `K3S-MANAGEMENT-SERVICES.md` - K3s管理サービス詳細
- `K3S-DASHBOARD-INSTALLATION.md` - Dashboard設定手順
- `ARGOCD-GITOPS-DEPLOYMENT.md` - ArgoCD GitOps設定
- `COMPLETE-CD-PIPELINE-REPORT.md` - CDパイプライン詳細
- `FRESH-DEPLOYMENT-REPORT.md` - デプロイメント手順

---

**すべてのサービスにアクセス可能です！**
