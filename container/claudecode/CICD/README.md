# CICD完全環境構築プロジェクト

グローバルスタンダードに準拠した、完全なCI/CD環境とサンプルアプリケーションの統合パッケージです。GitLab、Nexus、SonarQube、PostgreSQLを使用した本格的な開発環境を、スクラッチビルドから完全復元まで対応します。

[![Pipeline Status](http://34.205.156.203:5003/root/sample-app/badges/master/pipeline.svg)](http://34.205.156.203:5003/root/sample-app/-/commits/master)
[![Quality Gate](http://34.205.156.203:8000/api/project_badges/measure?project=sample-app-backend&metric=alert_status)](http://34.205.156.203:8000/dashboard?id=sample-app-backend)
[![Coverage](http://34.205.156.203:8000/api/project_badges/measure?project=sample-app-backend&metric=coverage)](http://34.205.156.203:8000/dashboard?id=sample-app-backend)

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [主な機能](#主な機能)
- [技術スタック](#技術スタック)
- [アーキテクチャ](#アーキテクチャ)
- [前提条件](#前提条件)
- [クイックスタート](#クイックスタート)
- [初回ログイン情報](#初回ログイン情報)
- [サンプルアプリケーション](#サンプルアプリケーション)
- [CI/CDパイプライン](#cicdパイプライン)
- [運用管理](#運用管理)
- [トラブルシューティング](#トラブルシューティング)
- [セキュリティ](#セキュリティ)

---

## 🌟 プロジェクト概要

このプロジェクトは、以下を提供します：

1. **完全なCI/CD環境** - GitLab、Nexus、SonarQube、PostgreSQLの統合環境
2. **サンプルアプリケーション** - Spring Boot + Reactによる組織管理システム（CRUD機能）
3. **自動化されたパイプライン** - ビルド → テスト → カバレッジ → 静的解析 → パッケージ → デプロイ
4. **品質保証基盤** - 80%カバレッジ、SonarQube品質ゲート
5. **運用スクリプト** - ゼロからのセットアップ、バックアップ、復元、クリーンアップ
6. **スクラッチビルド対応** - 完全な環境再構築が可能

### ディレクトリ構成

```
/root/aws.git/container/claudecode/CICD/
├── docker-compose.yml              # 全サービス統合定義
├── .env                            # 環境変数（パスワード含む）
├── .gitignore                      # Git除外設定
├── README.md                       # 本ドキュメント
├── QUICKSTART.md                   # クイックスタートガイド
│
├── config/                         # サービス設定ファイル
│   ├── gitlab/
│   ├── nexus/
│   ├── sonarqube/
│   ├── postgres/
│   ├── pgadmin/
│   ├── gitlab-runner/
│   └── maven/
│
├── volumes/                        # 永続化ボリューム（.gitignore）
│   ├── gitlab-config/
│   ├── gitlab-logs/
│   ├── gitlab-data/
│   ├── nexus-data/
│   ├── sonarqube-data/
│   ├── postgres-data/
│   └── pgadmin-data/
│
├── scripts/                        # 運用スクリプト
│   ├── setup-from-scratch.sh      # ゼロからセットアップ（パスワード設定含む）
│   ├── backup-all.sh              # 完全バックアップ
│   ├── restore-all.sh             # バックアップから復元
│   ├── cleanup-all.sh             # 全リソース削除
│   └── deploy-oneclick.sh         # ワンクリック再デプロイ
│
└── sample-app/                     # サンプルアプリケーション
    ├── pom.xml                     # 親POM（マルチモジュール）
    ├── .gitlab-ci.yml              # CI/CDパイプライン定義
    ├── .ci-settings.xml.template   # Maven設定テンプレート
    │
    ├── common/                     # 共通モジュール（DTO）
    │   ├── pom.xml
    │   └── src/main/java/com/example/common/dto/
    │
    ├── backend/                    # Spring Bootバックエンド
    │   ├── pom.xml
    │   └── src/
    │       ├── main/
    │       │   ├── java/com/example/backend/
    │       │   │   ├── entity/          # JPAエンティティ
    │       │   │   ├── repository/      # Spring Data JPA
    │       │   │   ├── service/         # ビジネスロジック
    │       │   │   └── controller/      # REST API
    │       │   └── resources/
    │       │       ├── application.yml
    │       │       └── db/migration/    # Flyway SQLスクリプト
    │       └── test/                    # JUnit 5テスト
    │
    └── frontend/                   # Reactフロントエンド
        ├── package.json
        ├── vite.config.js
        └── src/
            ├── components/
            ├── pages/
            └── api/
```

---

## ✨ 主な機能

### CI/CD環境

- **GitLab CE**: Git リポジトリ管理、CI/CD、コンテナレジストリ、Mattermost
- **Nexus Repository**: Maven/npm/Dockerアーティファクト管理
- **SonarQube**: 静的コード解析、品質ゲート、技術的負債管理
- **PostgreSQL 16**: 統合データベース（GitLab、SonarQube、sample-app）
- **pgAdmin 4**: データベースGUI管理ツール
- **GitLab Runner**: Shell executor によるCI/CD実行

### サンプルアプリケーション（組織管理システム）

- **バックエンド**: Spring Boot 3.2 + Java 17 + Maven
- **フロントエンド**: React + Vite
- **データベース**: PostgreSQL + Flyway マイグレーション
- **テスト**: JUnit 5 + Mockito + JaCoCo（80%カバレッジ達成）
- **機能**: 組織・部署・ユーザーのCRUD操作、階層管理

### 運用機能

- **パスワード管理**: 環境変数による一元管理、対話的設定
- **完全バックアップ**: 設定、データベース、リポジトリの一括バックアップ
- **スクラッチビルド**: ゼロからの完全環境再構築
- **ワンクリックデプロイ**: バックアップ → クリーンアップ → 再構築の自動化

---

## 🛠️ 技術スタック

### インフラストラクチャ

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| コンテナ | Podman / Docker | Latest |
| オーケストレーション | Docker Compose | v2.x |
| OS | RHEL 9 / Amazon Linux 2023 | - |
| CI/CD | GitLab CE + GitLab Runner | Latest |
| アーティファクト管理 | Sonatype Nexus | 3.x |
| 静的解析 | SonarQube Community | 10.x |
| データベース | PostgreSQL | 16 |
| DB GUI | pgAdmin | 4.x |

### バックエンド

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| 言語 | Java | 17 |
| フレームワーク | Spring Boot | 3.2.x |
| ビルドツール | Maven | 3.9.x |
| ORM | Spring Data JPA + Hibernate | - |
| マイグレーション | Flyway | 9.x |
| テストフレームワーク | JUnit 5 + Mockito | - |
| カバレッジ | JaCoCo | 0.8.11 |
| ユーティリティ | Lombok | 1.18.30 |

### フロントエンド

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| 言語 | JavaScript | ES6+ |
| フレームワーク | React | 18.x |
| ビルドツール | Vite | 5.x |
| HTTP クライアント | Axios | 1.x |
| ルーティング | React Router | 6.x |
| テスト | Jest + Playwright | - |

---

## 🏗️ アーキテクチャ

### サービス構成

| サービス | ポート | 用途 | 依存関係 |
|---------|-------|------|---------|
| **PostgreSQL** | 5001 | 統合データベース | - |
| **pgAdmin** | 5002 | DB GUI管理 | PostgreSQL |
| **GitLab CE** | 5003 (HTTP)<br>5005 (SSH)<br>5004 (Mattermost) | Git、CI/CD、チャット | PostgreSQL |
| **GitLab Runner** | - | CI/CD実行 | GitLab |
| **Nexus** | 8082 (UI/Maven)<br>8083 (Docker) | アーティファクト管理 | - |
| **SonarQube** | 8000 | 静的解析 | PostgreSQL |
| **Backend API** | 8501 | REST API | PostgreSQL |
| **Frontend** | 3000 | React UI | Backend API |

### ネットワーク構成

```
┌─────────────────────────────────────────────────────────┐
│                    cicd-network (bridge)                 │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ GitLab   │  │  Nexus   │  │SonarQube │              │
│  │ :5003    │  │  :8082   │  │  :8000   │              │
│  └────┬─────┘  └──────────┘  └────┬─────┘              │
│       │                            │                     │
│       └─────────┬──────────────────┘                     │
│                 │                                        │
│         ┌───────▼────────┐     ┌──────────┐             │
│         │   PostgreSQL   │     │ pgAdmin  │             │
│         │     :5001      │◄────┤  :5002   │             │
│         └────────────────┘     └──────────┘             │
│                 ▲                                        │
│                 │                                        │
│         ┌───────┴────────┐                               │
│         │  Sample App    │                               │
│         │  Backend:8501  │                               │
│         └────────────────┘                               │
└─────────────────────────────────────────────────────────┘
```

### データベーススキーマ（sample-app）

```sql
-- 組織テーブル
organizations (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    established_date DATE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- 部署テーブル（階層構造対応）
departments (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT → organizations(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    parent_department_id BIGINT → departments(id),
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (organization_id, code)
)

-- ユーザーテーブル
users (
    id BIGSERIAL PRIMARY KEY,
    department_id BIGINT → departments(id),
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    position VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

---

## 📋 前提条件

### システム要件

- **OS**: RHEL 9 / Amazon Linux 2023 / CentOS Stream 9
- **メモリ**: 最低 8GB、推奨 16GB
- **ディスク**: 最低 20GB、推奨 50GB
- **CPU**: 最低 2コア、推奨 4コア

### 必要なソフトウェア

```bash
# RHEL 9 / Amazon Linux 2023
sudo yum install -y \
  git \
  podman \
  podman-compose \
  maven \
  java-17-openjdk-devel \
  python3 \
  curl \
  wget
```

### その他

- **外部アクセス**: EC2インスタンスのセキュリティグループで以下のポートを開放
  - 5003 (GitLab HTTP)
  - 5005 (GitLab SSH)
  - 8082 (Nexus)
  - 8000 (SonarQube)
  - 5002 (pgAdmin)

---

## 🚀 クイックスタート

### 1. ゼロからセットアップ

```bash
# リポジトリをクローン（または既存ディレクトリに移動）
cd /root/aws.git/container/claudecode/CICD

# スクリプトに実行権限を付与
chmod +x scripts/*.sh

# セットアップ実行（対話的にパスワード設定）
./scripts/setup-from-scratch.sh
```

**セットアップ内容（11ステップ）**:
1. システムパッケージのインストール
2. SELinux設定の調整
3. Podmanソケットの有効化
4. ディレクトリ構造の作成
5. **管理者パスワードの設定**（対話的入力）
6. 環境変数ファイル（.env）の生成
7. Docker Compose設定の確認
8. コンテナの起動
9. GitLab Runnerのインストール
10. Maven設定の配置
11. セットアップ完了チェック

### 2. サービス状態確認

```bash
# コンテナ起動確認
podman ps

# サービス接続確認
curl http://localhost:5003/  # GitLab
curl http://localhost:8082/  # Nexus
curl http://localhost:8000/  # SonarQube
curl http://localhost:5002/  # pgAdmin

# PostgreSQL接続確認
psql -h localhost -p 5001 -U cicduser -d cicddb
```

### 3. GitLab Runnerの登録

```bash
# GitLabのSettings → CI/CD → Runnersからトークンを取得
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runnerの起動
sudo systemctl enable --now gitlab-runner
sudo systemctl status gitlab-runner
```

### 4. サンプルアプリケーションのプッシュ

```bash
cd sample-app

# リモートURLの設定（初回のみ）
git remote set-url origin http://YOUR_IP:5003/root/sample-app.git

# プッシュしてCI/CDパイプライン起動
git push -u origin master
```

---

## 🔑 初回ログイン情報

### パスワード管理

このプロジェクトでは、セキュリティとメンテナンス性を考慮し、**すべてのパスワードを環境変数で一元管理**しています。

#### パスワード設定方法

1. **初回セットアップ時**:
   - `setup-from-scratch.sh` 実行時に対話的にパスワードを入力
   - 最低8文字、英数字記号を推奨
   - 確認入力で誤入力を防止

2. **既存環境の場合**:
   - `.env` ファイルを直接編集
   ```bash
   vi .env

   # 以下の変数を変更
   GITLAB_ROOT_PASSWORD=your_password
   NEXUS_ADMIN_PASSWORD=your_password
   SONARQUBE_ADMIN_PASSWORD=your_password
   ```

3. **CI/CDパイプラインでの使用**:
   - GitLab CI/CD環境変数に `NEXUS_ADMIN_PASSWORD` を設定
   - パイプライン実行時に自動的に `.ci-settings.xml.template` から設定ファイルを生成

### サービス別ログイン情報

#### 1. GitLab
```
URL: http://YOUR_IP:5003
ユーザー名: root
パスワード: ${GITLAB_ROOT_PASSWORD} (デフォルト: Degital2026!)
```

#### 2. Nexus Repository
```
URL: http://YOUR_IP:8082
ユーザー名: admin
パスワード: ${NEXUS_ADMIN_PASSWORD} (デフォルト: Degital2026!)
```
- **初回ログイン後の対応**:
  - "Sign in with the default credentials" をクリック
  - セットアップウィザードが表示された場合、パスワード変更を求められることがあります
  - その場合は `.env` ファイルの `NEXUS_ADMIN_PASSWORD` も同じ値に更新してください

#### 3. SonarQube
```
URL: http://YOUR_IP:8000
デフォルト: admin / admin
```
- **初回ログイン後の対応**:
  - 必ずパスワード変更を求められます
  - 新しいパスワードを設定したら、`.env` ファイルの `SONARQUBE_ADMIN_PASSWORD` を更新
  - GitLab CI/CD環境変数 `SONAR_TOKEN` も再生成して更新してください

#### 4. pgAdmin
```
URL: http://YOUR_IP:5002
Email: admin@example.com
パスワード: pgadmin_pass_2026
```

#### 5. PostgreSQL
```
ホスト: localhost
ポート: 5001
ユーザー名: cicduser
パスワード: cicd_postgres_pass_2026
データベース: cicddb
```

### SonarQubeトークンの生成（初回のみ）

```bash
# 1. SonarQubeにログイン後、右上のユーザーアイコン → My Account → Security

# 2. "Generate Token" でトークンを生成
#    Name: gitlab-ci
#    Type: Project Analysis Token or Global Analysis Token

# 3. 生成されたトークンを .env ファイルに設定
vi .env
# SONAR_TOKEN=sqa_xxxxxxxxxxxxxxxxxxxxx

# 4. GitLab CI/CD環境変数にも設定
#    GitLab → Settings → CI/CD → Variables
#    Key: SONAR_TOKEN
#    Value: sqa_xxxxxxxxxxxxxxxxxxxxx
#    Flags: Masked
```

---

## 📦 サンプルアプリケーション

### 概要

組織管理システム - Spring Boot + Reactによる3階層CRUD アプリケーション

### 機能一覧

#### 1. 組織管理（Organizations）
- 組織の作成、参照、更新、削除
- 組織コード、名称、設立日、説明の管理
- アクティブ/非アクティブステータス

#### 2. 部署管理（Departments）
- 部署の作成、参照、更新、削除
- 組織への所属管理
- 階層構造（親部署-子部署）
- 部署コード、名称、説明の管理

#### 3. ユーザー管理（Users）
- ユーザーの作成、参照、更新、削除
- 部署への所属管理
- 社員番号、ユーザー名、メール、氏名、電話番号、役職の管理
- アクティブ/非アクティブステータス

### REST API エンドポイント

#### Organizations API
```
GET    /api/organizations         # 全組織取得
GET    /api/organizations/{id}    # 組織詳細取得
POST   /api/organizations         # 組織作成
PUT    /api/organizations/{id}    # 組織更新
DELETE /api/organizations/{id}    # 組織削除
GET    /api/organizations/code/{code}  # コードで組織検索
```

#### Departments API
```
GET    /api/departments           # 全部署取得
GET    /api/departments/{id}      # 部署詳細取得
POST   /api/departments           # 部署作成
PUT    /api/departments/{id}      # 部署更新
DELETE /api/departments/{id}      # 部署削除
GET    /api/departments/organization/{orgId}  # 組織別部署一覧
```

#### Users API
```
GET    /api/users                 # 全ユーザー取得
GET    /api/users/{id}            # ユーザー詳細取得
POST   /api/users                 # ユーザー作成
PUT    /api/users/{id}            # ユーザー更新
DELETE /api/users/{id}            # ユーザー削除
GET    /api/users/department/{deptId}  # 部署別ユーザー一覧
GET    /api/users/employee/{employeeNumber}  # 社員番号検索
```

### ローカル開発

#### バックエンド
```bash
cd sample-app
mvn clean install

cd backend
mvn spring-boot:run

# アクセス
# http://localhost:8501
# Swagger UI: http://localhost:8501/swagger-ui.html
```

#### フロントエンド
```bash
cd sample-app/frontend
npm install
npm run dev

# アクセス
# http://localhost:3000
```

#### テスト実行
```bash
# バックエンドテスト
cd sample-app
mvn clean test

# カバレッジレポート生成
mvn jacoco:report
open backend/target/site/jacoco/index.html

# フロントエンドテスト
cd frontend
npm test
npm test -- --coverage
```

---

## 🔄 CI/CDパイプライン

### パイプライン構成（6ステージ）

`.gitlab-ci.yml` で定義された自動化パイプライン:

```
build → test → coverage → sonarqube → package → deploy
```

#### 1. Build ステージ
```yaml
- Maven コンパイル（テストスキップ）
- 成果物: target/classes
- 実行時間: ~1分
```

#### 2. Test ステージ
```yaml
- JUnit 5 単体テスト実行
- テストレポート生成（JUnit XML）
- JaCoCo カバレッジ測定
- 成果物: surefire-reports, jacoco
- 実行時間: ~2分
```

#### 3. Coverage ステージ
```yaml
- JaCoCo レポート生成
- カバレッジ集計（行カバレッジ/ブランチカバレッジ）
- 成果物: jacoco HTML/XML レポート
- 実行時間: ~30秒
```

#### 4. SonarQube ステージ
```yaml
- 静的コード解析実行
- 品質ゲートチェック
- バグ、脆弱性、コードスメル検出
- カバレッジレポート送信
- ブランチ: master のみ
- 実行時間: ~1-2分
```

#### 5. Package ステージ
```yaml
- Maven パッケージング（JAR生成）
- テストスキップ（既に実行済み）
- 成果物: backend-1.0.0.jar
- ブランチ: master のみ
- 実行時間: ~1分
```

#### 6. Deploy ステージ
```yaml
- Nexus Repository へデプロイ
- .ci-settings.xml.template から動的設定生成
- Maven アーティファクトアップロード
- ブランチ: master のみ
- 実行時間: ~1分
```

### パイプライン実行

#### 自動実行
```bash
# コミット＆プッシュで自動実行
cd sample-app
git add .
git commit -m "feat: 新機能追加"
git push origin master
```

#### 手動実行
```
GitLab UI → CI/CD → Pipelines → Run Pipeline
```

### 品質ゲート基準

SonarQubeで設定された品質基準:

| メトリクス | 基準値 |
|----------|--------|
| 行カバレッジ | ≥ 80% |
| ブランチカバレッジ | ≥ 70% |
| 重大バグ | 0件 |
| 脆弱性（高リスク） | 0件 |
| コード重複率 | ≤ 3% |
| 保守性レーティング | A |

### パイプライン最適化

- **キャッシュ**: Maven `.m2/repository` をキャッシュして依存関係ダウンロード時間短縮
- **並列化**: 各ステージを順次実行、依存関係を明示
- **条件付き実行**: master ブランチのみデプロイステージを実行
- **アーティファクト**: テストレポートとカバレッジレポートを1週間保持

---

## 🛠️ 運用管理

### 運用スクリプト一覧

| スクリプト | 説明 | 用途 |
|----------|------|------|
| `setup-from-scratch.sh` | ゼロから完全環境構築（11ステップ） | 新規環境セットアップ |
| `backup-all.sh` | 完全バックアップ | 定期バックアップ、移行前 |
| `restore-all.sh` | バックアップから復元 | 災害復旧、環境移行 |
| `cleanup-all.sh` | 全リソース削除 | 環境クリーンアップ |
| `deploy-oneclick.sh` | ワンクリック再デプロイ | 環境リフレッシュ |

### 1. バックアップ

```bash
# 完全バックアップ実行
./scripts/backup-all.sh

# バックアップ内容
# - 全設定ファイル（docker-compose.yml、.env、config/）
# - GitLab データベース（gitlab-backup.tar）
# - GitLab リポジトリ（sample-app.bundle）
# - GitLab Runner 設定
# - Maven 設定
# - 環境情報

# バックアップ先
# backup-YYYYMMDD-HHMMSS/       # ディレクトリ
# backup-YYYYMMDD-HHMMSS.tar.gz # アーカイブ（約4-10MB）
```

### 2. 復元

```bash
# バックアップアーカイブの展開
tar xzf backup-20260110-075148.tar.gz

# 復元実行
./scripts/restore-all.sh backup-20260110-075148

# 復元内容
# - コンテナ停止＆削除
# - 設定ファイル復元
# - コンテナ再起動
# - GitLab データベース復元
# - GitLab リポジトリ復元
# - GitLab Runner 設定復元
# - Maven 設定復元
```

### 3. クリーンアップ

```bash
# 全リソース削除（確認プロンプトあり）
./scripts/cleanup-all.sh

# 削除対象
# - 全コンテナ（cicd-*）
# - 全ボリューム（cicd-*）
# - ネットワーク（cicd-network）
# - GitLab Runner 設定（オプション）
# - Maven 設定（オプション）
```

### 4. ワンクリック再デプロイ

```bash
# バックアップ → クリーンアップ → セットアップを一括実行
./scripts/deploy-oneclick.sh

# 処理フロー
# 1. 現在の環境を完全バックアップ
# 2. 全リソースをクリーンアップ
# 3. バックアップから復元
# 4. サービス起動確認
```

### 5. 定期バックアップの自動化

```bash
# cronで毎日午前3時にバックアップ
sudo tee /etc/cron.d/cicd-backup > /dev/null <<'EOF'
0 3 * * * ec2-user /root/aws.git/container/claudecode/CICD/scripts/backup-all.sh
EOF

# 古いバックアップの削除（30日以前）
# 以下を cron に追加
0 4 * * * find /root/aws.git/container/claudecode/CICD/backup-* -type f -name "*.tar.gz" -mtime +30 -delete
```

### 6. サービス管理

```bash
# 全サービス起動
cd /root/aws.git/container/claudecode/CICD
podman-compose up -d

# 全サービス停止
podman-compose down

# 特定サービスの再起動
podman-compose restart gitlab
podman-compose restart nexus
podman-compose restart sonarqube

# ログ確認
podman-compose logs -f gitlab
podman-compose logs -f nexus
podman-compose logs -f sonarqube

# リソース使用状況
podman stats
```

---

## 🔍 トラブルシューティング

### 1. コンテナが起動しない

**症状**: `podman-compose up -d` 後、コンテナがすぐに停止する

**原因と対策**:

#### SELinux問題
```bash
# SELinuxの状態確認
getenforce

# Permissive に設定
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
```

#### ポート競合
```bash
# ポート使用状況確認
sudo ss -tuln | grep -E '5001|5002|5003|8000|8082'

# 競合している場合、docker-compose.yml のポート番号を変更
```

#### メモリ不足
```bash
# メモリ使用状況確認
free -h

# SonarQube用のvm.max_map_count設定
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 2. GitLab にアクセスできない

**症状**: `curl http://localhost:5003` でエラー

**対策**:
```bash
# コンテナの状態確認
podman ps -a | grep gitlab

# GitLab初期化完了まで待機（5-10分）
podman logs -f cicd-gitlab

# "gitlab Reconfigured!" が表示されるまで待つ

# 初期パスワード確認（24時間以内）
podman exec -it cicd-gitlab cat /etc/gitlab/initial_root_password
```

### 3. CI/CDパイプラインが失敗する

#### ステージ別トラブルシューティング

##### Build ステージ失敗
```bash
# Maven依存関係の問題
cd sample-app
mvn clean install -U  # 依存関係を強制更新

# Nexusプロキシ設定確認
curl http://localhost:8082/repository/maven-public/
```

##### Test ステージ失敗
```bash
# テストをローカル実行して詳細確認
cd sample-app
mvn clean test -X  # デバッグモード

# テストケース個別実行
mvn test -Dtest=OrganizationServiceTest
```

##### SonarQube ステージ失敗
```bash
# SonarQubeトークン確認
# GitLab → Settings → CI/CD → Variables → SONAR_TOKEN

# SonarQube接続確認
curl http://localhost:8000/api/system/status

# SonarQubeログ確認
podman logs cicd-sonarqube
```

##### Deploy ステージ失敗（401 Unauthorized）
```bash
# Nexusパスワード確認
cat .env | grep NEXUS_ADMIN_PASSWORD

# GitLab CI/CD環境変数確認
# GitLab → Settings → CI/CD → Variables → NEXUS_ADMIN_PASSWORD

# Nexusログイン確認
curl -u admin:YOUR_PASSWORD http://localhost:8082/service/rest/v1/status
```

### 4. GitLab Runner が動作しない

```bash
# Runner状態確認
sudo systemctl status gitlab-runner

# Runner再起動
sudo systemctl restart gitlab-runner

# Runner登録確認
sudo gitlab-runner list

# Runner未登録の場合、再登録
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runnerログ確認
sudo journalctl -u gitlab-runner -f
```

### 5. データベース接続エラー

```bash
# PostgreSQL起動確認
podman ps | grep postgres

# PostgreSQL接続テスト
psql -h localhost -p 5001 -U cicduser -d cicddb

# パスワードは .env ファイルから確認
cat .env | grep POSTGRES_PASSWORD

# データベース一覧確認
psql -h localhost -p 5001 -U cicduser -d cicddb -c "\l"

# テーブル一覧確認
psql -h localhost -p 5001 -U cicduser -d cicddb -c "\dt"
```

### 6. SonarQube品質ゲート失敗

```bash
# SonarQubeプロジェクト確認
# http://YOUR_IP:8000/dashboard?id=sample-app-backend

# カバレッジ不足の場合
cd sample-app
mvn clean test jacoco:report

# カバレッジレポート確認
open backend/target/site/jacoco/index.html

# コードスメルやバグの場合
# SonarQube Issues タブで詳細を確認し、コードを修正
```

### 7. ディスク容量不足

```bash
# ディスク使用状況確認
df -h

# Podman未使用イメージ削除
podman image prune -a

# Podman未使用ボリューム削除
podman volume prune

# 古いバックアップ削除
find backup-* -type f -mtime +30 -delete

# Nexus古いアーティファクト削除
# Nexus UI → Repository → maven-snapshots → Cleanup Policies
```

---

## 🔐 セキュリティ

### パスワード管理

#### 1. 環境変数による管理
```bash
# .envファイルでパスワードを一元管理
GITLAB_ROOT_PASSWORD=your_strong_password
NEXUS_ADMIN_PASSWORD=your_strong_password
SONARQUBE_ADMIN_PASSWORD=your_strong_password

# .envファイルは .gitignore に含まれている
# Gitリポジトリにコミットされない
```

#### 2. 初回セットアップ時の設定
```bash
# setup-from-scratch.sh 実行時に対話的入力
# - 最低8文字
# - 確認入力による誤入力防止
# - 英数字記号の組み合わせ推奨
```

#### 3. CI/CDでの取り扱い
```bash
# GitLab CI/CD環境変数（Masked）
# Settings → CI/CD → Variables
SONAR_TOKEN=sqa_xxxxx...  (Masked)
NEXUS_ADMIN_PASSWORD=xxx  (Masked)

# .gitlab-ci.yml では環境変数を参照
# パスワードはログに出力されない
```

### 推奨事項

#### 1. パスワードポリシー
- 最低12文字以上
- 大文字、小文字、数字、記号を組み合わせる
- 辞書に載っている単語を避ける
- 定期的に変更する（90日ごと）

#### 2. アクセス制限
```bash
# ファイアウォール設定（必要なポートのみ開放）
sudo firewall-cmd --permanent --add-port=5003/tcp  # GitLab
sudo firewall-cmd --permanent --add-port=8082/tcp  # Nexus
sudo firewall-cmd --permanent --add-port=8000/tcp  # SonarQube
sudo firewall-cmd --reload

# .env ファイルのパーミッション
chmod 600 .env
```

#### 3. バックアップの暗号化
```bash
# バックアップアーカイブを暗号化
gpg --symmetric --cipher-algo AES256 backup-20260110-075148.tar.gz

# 復号化
gpg --decrypt backup-20260110-075148.tar.gz.gpg > backup-20260110-075148.tar.gz
```

#### 4. 監査ログ
```bash
# GitLabアクセスログ
podman exec cicd-gitlab cat /var/log/gitlab/nginx/gitlab_access.log

# Nexusログ
podman logs cicd-nexus

# SonarQubeログ
podman logs cicd-sonarqube
```

---

## 📚 参考資料

### 公式ドキュメント

- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Repository Manager Documentation](https://help.sonatype.com/repomanager3)
- [SonarQube Documentation](https://docs.sonarqube.org/latest/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [React Documentation](https://react.dev/)

### プロジェクト関連

- **GitLab**: http://34.205.156.203:5003
- **Nexus**: http://34.205.156.203:8082
- **SonarQube**: http://34.205.156.203:8000
- **pgAdmin**: http://34.205.156.203:5002

### Issue管理

このプロジェクトは **Issue #115** の一環として実装されました。

---

## 📝 ライセンス

このプロジェクトは学習・評価目的で作成されています。

---

## 👥 貢献者

- 初期実装: Claude Code (Claude Sonnet 4.5)
- プロジェクト管理: Issue #115

---

## 📞 サポート

問題が発生した場合:

1. [トラブルシューティング](#トラブルシューティング)セクションを確認
2. ログを確認（`podman logs <container_name>`）
3. GitLabプロジェクトのIssuesに報告

---

**最終更新日**: 2026-01-10
**バージョン**: 2.0.0
