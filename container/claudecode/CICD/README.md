# CI/CD環境構築

このディレクトリには、完全なCI/CD環境が含まれています。GitLab、Nexus、SonarQube、PostgreSQL、pgAdmin、およびサンプルアプリケーションがDockerコンテナとして構築されています。

## 概要

**ディレクトリ**: `/root/aws.git/container/claudecode/CICD/`

**採用技術（グローバルスタンダード準拠）**:
- GitLab CE（コンテナレジストリ有効）
- Mattermost Team Edition（独立コンテナ）
- Sonatype Nexus Repository（Maven/npm/Docker）
- SonarQube Community Edition
- PostgreSQL 16 + pgAdmin
- Spring Boot 3.2 + Java 17 + Maven
- React + Vite + JavaScript

## サービス一覧

| サービス | ポート | 用途 | 外部アクセスURL |
|---------|-------|------|----------------|
| GitLab | 5003 (HTTP), 8443 (HTTPS), 2223 (SSH) | リポジトリ、CI/CD | http://ec2-34-205-156-203.compute-1.amazonaws.com:5003 |
| Mattermost | 5004 | チャット・コラボレーション | http://ec2-34-205-156-203.compute-1.amazonaws.com:5004 |
| Container Registry | 5005 | Dockerイメージレジストリ | http://ec2-34-205-156-203.compute-1.amazonaws.com:5005 |
| Nexus | 8082 (UI/Maven), 8083 (Docker Registry) | アーティファクト管理 | http://ec2-34-205-156-203.compute-1.amazonaws.com:8082 |
| SonarQube | 8000 | 静的解析・品質管理 | http://ec2-34-205-156-203.compute-1.amazonaws.com:8000 |
| PostgreSQL | 5001 (external) | RDB | ec2-34-205-156-203.compute-1.amazonaws.com:5001 |
| pgAdmin | 5002 | DB GUI | http://ec2-34-205-156-203.compute-1.amazonaws.com:5002 |
| Backend API | 8501 | Spring Boot REST API | http://ec2-34-205-156-203.compute-1.amazonaws.com:8501 |
| Frontend | 3000 | React開発サーバ | http://ec2-34-205-156-203.compute-1.amazonaws.com:3000 |

### 認証情報

| サービス | ユーザー名 | パスワード |
|---------|-----------|-----------|
| GitLab | root | password123! |
| Nexus | admin | 初回起動時に生成 (後述) |
| SonarQube | admin | admin (初回変更必要) |
| pgAdmin | admin@example.com | pgadmin_pass_2026 |
| PostgreSQL | cicduser | cicd_postgres_pass_2026 |
| Mattermost | (初回セットアップ時に作成) | (初回セットアップ時に設定) |

## セットアップ

### 1. 前提条件

- Docker/Podman + docker-compose/podman-compose インストール済み
- 利用可能ポート: 3000, 8000, 8080, 8082, 8083, 8443, 2223, 5001, 5002, 8501
- 最低ディスク空き容量: 20GB

### 2. 環境変数設定

`.env`ファイルを編集し、各サービスのパスワードとトークンを設定します。

```bash
cp .env.example .env
vim .env
```

### 3. サービス起動

#### すべてのサービスを一括起動

```bash
podman-compose up -d
```

#### 個別にサービスを起動

```bash
# データベース
podman-compose up -d postgres pgadmin

# CI/CDツール
podman-compose up -d gitlab nexus sonarqube

# サンプルアプリ（ビルド後）
podman-compose up -d sample-backend sample-frontend
```

### 4. 初期設定

#### GitLab

1. ブラウザでアクセス
   - **外部からアクセス**: http://ec2-34-205-156-203.compute-1.amazonaws.com:5003
   - **ローカルアクセス**: http://localhost:5003
2. 初期rootパスワード: `password123!`
   (または以下のコマンドで取得)
   ```bash
   podman exec -it cicd-gitlab cat /etc/gitlab/initial_root_password
   ```
3. rootユーザーでログイン
4. プロジェクト作成

#### Nexus

1. ブラウザでアクセス
   - **外部からアクセス**: http://ec2-34-205-156-203.compute-1.amazonaws.com:8082
   - **ローカルアクセス**: http://localhost:8082
2. 初期adminパスワードを取得:
   ```bash
   podman exec -it cicd-nexus cat /nexus-data/admin.password
   ```
3. リポジトリ設定:
   - maven-central (proxy)
   - maven-releases (hosted)
   - maven-snapshots (hosted)
   - npm-proxy (proxy)
   - docker-hosted (docker)

#### SonarQube

1. ブラウザでアクセス
   - **外部からアクセス**: http://ec2-34-205-156-203.compute-1.amazonaws.com:8000
   - **ローカルアクセス**: http://localhost:8000
2. デフォルトログイン: admin / admin
3. パスワード変更
4. プロジェクト作成
5. トークン生成して`.env`に追加

#### pgAdmin

1. ブラウザでアクセス
   - **外部からアクセス**: http://ec2-34-205-156-203.compute-1.amazonaws.com:5002
   - **ローカルアクセス**: http://localhost:5002
2. `.env`のPGADMIN_EMAILとPGADMIN_PASSWORDでログイン
3. PostgreSQL接続追加:
   - Host: postgres
   - Port: 5432
   - User: cicduser
   - Database: cicddb

#### Mattermost

1. ブラウザでアクセス
   - **外部からアクセス**: http://ec2-34-205-156-203.compute-1.amazonaws.com:5004
   - **ローカルアクセス**: http://localhost:5004
2. 初回アクセス時にアカウント作成
3. チーム作成
4. GitLab連携（オプション）:
   - System Console → Integrations → GitLab
   - GitLab URL: http://34.205.156.203:5003

**注意**: Mattermostは独立コンテナとして稼働しています。GitLab内蔵のMattermostは無効化されています。

## サンプルアプリケーション

### ビルドと実行

#### バックエンド（Spring Boot）

```bash
cd sample-app
mvn clean package
cd backend
java -jar target/backend-1.0.0-SNAPSHOT.jar
```

#### フロントエンド（React + Vite）

```bash
cd sample-app/frontend
npm install
npm run dev
```

### テスト実行

#### バックエンド

```bash
cd sample-app
mvn clean test
mvn jacoco:report
```

#### フロントエンド

```bash
cd sample-app/frontend
npm test
npx playwright test
```

## CI/CDパイプライン

### パイプラインステージ

1. **build** - Maven/npm ビルド
2. **test** - 単体テスト（JUnit/Jest）
3. **coverage** - カバレッジ測定（JaCoCo）
4. **sonar** - SonarQube静的解析
5. **package** - JAR/Docker イメージ作成
6. **e2e** - E2Eテスト（Playwright）
7. **deploy** - Nexusへのデプロイ

### パイプライン実行

1. GitLabプロジェクトにコードをpush
2. マージリクエスト作成
3. パイプライン自動実行
4. Quality Gate通過確認
5. マージ承認

## トラブルシューティング

### メモリ不足

```bash
sudo sysctl -w vm.max_map_count=262144
```

### ポート競合確認

```bash
ss -tuln | grep <port>
```

### コンテナログ確認

```bash
podman-compose logs <service-name>
```

### サービス再起動

```bash
podman-compose restart <service-name>
```

## 運用スクリプト

- `scripts/setup.sh` - 初回セットアップ自動化
- `scripts/start-all.sh` - 全サービス起動
- `scripts/stop-all.sh` - 全サービス停止
- `scripts/backup-db.sh` - データベースバックアップ
- `scripts/init-gitlab.sh` - GitLabプロジェクト自動作成

## ドキュメント

- `docs/API.md` - REST API仕様
- `docs/DATABASE.md` - データベース設計
- `docs/DEPLOYMENT.md` - デプロイ手順

## サポート

Issue: https://github.com/shiftrepo/aws/issues/115
