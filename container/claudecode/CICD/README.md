# CICD完全環境構築プロジェクト

グローバルスタンダードに準拠した、完全なCI/CD環境とサンプルアプリケーション（フロントエンド/バックエンド分離構成）の統合パッケージです。GitLab、Nexus、SonarQube、PostgreSQLを使用した本格的な開発環境を、スクラッチビルドから完全復元まで対応します。

---

## 🎯 リポジトリの目的と用途

### このリポジトリ (`/root/aws.git/container/claudecode/CICD/`)

**これがマスタリポジトリ（本体）です。**

- **目的**: CI/CD環境を構築するための環境構築プロジェクト
- **対象**: ホストEC2のスクラッチビルド（ゼロからの完全構築）に対応
- **役割**:
  - GitLab、Nexus、SonarQube、PostgreSQL等のCI/CDインフラを提供
  - `sample-app/` ディレクトリに**マスタのサンプルアプリケーション**を保持
  - 環境構築スクリプト、設定ファイル、ドキュメントを管理

### GitLab上のサンプルプロジェクト（フロントエンド/バックエンド分離）

**これらはCI/CD試行用の作業コピーです。マスタではありません。**

- **作成方法**: `setup-sample-app-split.sh` により、以下の2つの独立プロジェクトを作成
  - **フロントエンドプロジェクト**: `/tmp/gitlab-sample-app-frontend-YYYYMMDD-HHMMSS/`
  - **バックエンドプロジェクト**: `/tmp/gitlab-sample-app-backend-YYYYMMDD-HHMMSS/`
- **GitLabプロジェクト名**: 実行時刻でユニーク化
  - `sample-app-frontend-YYYYMMDD-HHMMSS`
  - `sample-app-backend-YYYYMMDD-HHMMSS`
- **目的**: 構築したGitLab環境でCI/CDパイプラインを試行・検証する
- **用途**:
  - 独立したCI/CDパイプラインの動作確認
  - 修正・実験・テストの実施
  - 品質ゲート、カバレッジ、デプロイの検証
- **重要な原則**:
  - ⚠️ **これらのディレクトリはマスタではありません**
  - ✅ CI/CDを実現できたら、必ず `/root/aws.git/container/claudecode/CICD/sample-app/` に反映
  - ✅ 問題や不具合の対策を実施したら、必ずコピー元のマスタに反映
  - ✅ `setup-sample-app-split.sh` を実行するだけでCI/CDを確認できる
  - ✅ 繰り返し実行しても問題なく動作する（タイムスタンプで別プロジェクト作成）

### ワークフロー（フロントエンド/バックエンド分離構成）

```
┌─────────────────────────────────────────────────────────────────┐
│  /root/aws.git/container/claudecode/CICD/                       │
│  (マスタリポジトリ - 本体)                                       │
│                                                                  │
│  ├── sample-app/                                                 │
│  │   ├── frontend/          ← フロントエンドマスタ              │
│  │   ├── backend/           ← バックエンドマスタ                │
│  │   ├── common/            ← 共通モジュール                     │
│  │   ├── .gitlab-ci.yml.frontend  ← フロントエンドCI/CD定義    │
│  │   └── .gitlab-ci.yml.backend   ← バックエンドCI/CD定義      │
│  │                                                               │
│  └── scripts/                                                    │
│      └── setup-sample-app-split.sh  ← 分割プロジェクト自動化   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │ setup-sample-app-split.sh 実行
                          │ (フロントエンド/バックエンドを分離コピー)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  GitLab上の2つの独立プロジェクト                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ sample-app-frontend-20260113-135159                       │  │
│  │ - /tmp/gitlab-sample-app-frontend-20260113-135159/       │  │
│  │ - React + Vite + Jest                                     │  │
│  │ - 5ステージパイプライン                                   │  │
│  │ - SonarQube (LCOV coverage)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ sample-app-backend-20260113-135159                        │  │
│  │ - /tmp/gitlab-sample-app-backend-20260113-135159/        │  │
│  │ - Spring Boot + Maven + JUnit                             │  │
│  │ - 7ステージパイプライン                                   │  │
│  │ - SonarQube (Maven plugin) + Nexus + Container Deploy    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │ パイプライン成功後、手動で反映
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  /root/aws.git/container/claudecode/CICD/sample-app/            │
│  (マスタに反映 → GitHub push)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### setup-sample-app-split.sh スクリプトの役割

**最新の推奨セットアップ方法です。**

- **機能**: マスタリポジトリから2つの独立GitLabプロジェクトを自動作成
  - フロントエンド: `sample-app/frontend/` → GitLab
  - バックエンド: `sample-app/backend/`, `common/`, `pom.xml` → GitLab
- **自動化内容**:
  1. ✅ **GitLab Personal Access Token自動生成** - API操作に必要なトークン
  2. ✅ **GitLabプロジェクト自動作成** - API経由で2プロジェクト作成
  3. ✅ **SonarQubeトークン自動生成** - プロジェクトごとに専用トークン
  4. ✅ **CI/CD Variables自動設定** - pushの前に環境変数を設定
  5. ✅ **Git初期化とpush** - 各プロジェクトをGitLabへ自動push
- **タイムスタンプ付与**: 実行時刻でプロジェクト名をユニーク化（複数サンプル共存可能）
- **利便性**: ユーザーは `./scripts/setup-sample-app-split.sh` を実行するだけで、完全自動化
- **安全性**: 繰り返し実行しても問題なく動作（新しいプロジェクトが作成される）

---

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
2. **サンプルアプリケーション（フロントエンド/バックエンド分離）** - React + Spring Boot組織管理システム
3. **独立した2つのCI/CDパイプライン** - フロントエンド5ステージ、バックエンド7ステージ
4. **完全自動化セットアップ** - トークン生成、CI/CD Variables設定、プロジェクト作成
5. **品質保証基盤** - 90%カバレッジ、SonarQube品質ゲート
6. **運用スクリプト** - ゼロからのセットアップ、バックアップ、復元、クリーンアップ
7. **スクラッチビルド対応** - 完全な環境再構築が可能

### ディレクトリ構成

```
/root/aws.git/container/claudecode/CICD/
├── docker-compose.yml              # 全サービス統合定義
├── .env                            # 環境変数（パスワード含む、Git除外）
├── .gitignore                      # Git除外設定（credentials.txt、.env.backup.*含む）
├── README.md                       # 本ドキュメント
├── CREDENTIALS.md                  # 認証情報管理ガイド
├── QUICKSTART.md                   # クイックスタートガイド
├── CLAUDE.md                       # Claude Code向けプロジェクトガイド
│
├── config/                         # サービス設定ファイル
│   ├── gitlab/
│   ├── nexus/
│   ├── sonarqube/
│   ├── postgres/
│   ├── pgadmin/
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
│   ├── setup-from-scratch.sh      # ゼロからセットアップ（パスワード設定、EC2ドメイン入力、トークン保持）
│   ├── setup-sample-app-split.sh  # 【推奨】フロントエンド/バックエンド分離プロジェクト自動作成
│   ├── utils/
│   │   ├── show-credentials.sh        # 全サービスの認証情報表示・ファイル出力
│   │   ├── update-passwords.sh        # パスワード・トークン・EC2ホスト更新
│   │   ├── backup-all.sh              # 完全バックアップ
│   │   ├── restore-all.sh             # バックアップから復元
│   │   └── deploy-oneclick.sh         # ワンクリック再デプロイ
│   └── cleanup-all.sh             # 全リソース削除
│
└── sample-app/                     # サンプルアプリケーション（マスタ）
    ├── pom.xml                     # 親POM（バックエンドマルチモジュール）
    ├── .gitlab-ci.yml.frontend     # フロントエンドCI/CD定義（5ステージ）
    ├── .gitlab-ci.yml.backend      # バックエンドCI/CD定義（7ステージ）
    │
    ├── frontend/                   # Reactフロントエンド
    │   ├── package.json
    │   ├── vite.config.js
    │   ├── sonar-project.properties  # SonarQube設定（LCOV専用）
    │   ├── Dockerfile
    │   └── src/
    │       ├── components/
    │       ├── pages/
    │       └── api/
    │
    ├── common/                     # 共通モジュール（DTO）
    │   ├── pom.xml
    │   └── src/main/java/com/example/common/dto/
    │
    └── backend/                    # Spring Bootバックエンド
        ├── pom.xml
        ├── Dockerfile
        └── src/
            ├── main/
            │   ├── java/com/example/backend/
            │   │   ├── entity/          # JPAエンティティ
            │   │   ├── repository/      # Spring Data JPA
            │   │   ├── service/         # ビジネスロジック
            │   │   └── controller/      # REST API
            │   └── resources/
            │       ├── application.yml
            │       └── db/migration/    # Flyway SQLスクリプト
            └── test/                    # JUnit 5テスト
```

---

## ✨ 主な機能

### CI/CD環境

- **GitLab CE**: Git リポジトリ管理、CI/CD、コンテナレジストリ
- **Nexus Repository**: Maven/npm/Dockerアーティファクト管理
- **SonarQube**: 静的コード解析、品質ゲート、技術的負債管理
- **PostgreSQL 16**: 統合データベース（GitLab、SonarQube、sample-app）
- **pgAdmin 4**: データベースGUI管理ツール
- **GitLab Runner**: Shell executor によるCI/CD実行

### サンプルアプリケーション（組織管理システム - フロントエンド/バックエンド分離）

#### フロントエンド
- **技術スタック**: React 18 + Vite 5.x + Jest
- **テスト**: Jest + @testing-library/react
- **カバレッジ**: LCOV形式（SonarQube連携）
- **CI/CD**: 5ステージパイプライン（install → lint → test → sonarqube → build）
- **デプロイ**: Dockerコンテナ化（Nginx）

#### バックエンド
- **技術スタック**: Spring Boot 3.2 + Java 17 + Maven
- **データベース**: PostgreSQL + Flyway マイグレーション
- **テスト**: JUnit 5 + Mockito + JaCoCo（90%カバレッジ達成）
- **CI/CD**: 7ステージパイプライン（build → test → coverage → sonar → package → nexus-deploy → container-deploy）
- **機能**: 組織・部署・ユーザーのCRUD操作、階層管理

### 完全自動化機能（v2.6.0）

#### setup-sample-app-split.sh による自動化
1. **GitLab Personal Access Token自動生成**
   - GitLab Rails Console経由でAPI操作用トークン作成
   - スコープ: api, read_api, write_repository
   - 有効期限: 365日

2. **GitLabプロジェクト自動作成（API経由）**
   - フロントエンドプロジェクト: `sample-app-frontend-YYYYMMDD-HHMMSS`
   - バックエンドプロジェクト: `sample-app-backend-YYYYMMDD-HHMMSS`
   - タイムスタンプによるユニーク化

3. **SonarQubeトークン自動生成**
   - SonarQube API (`/api/user_tokens/generate`) 経由
   - プロジェクトごとに専用トークン（frontend-ci-token-*, backend-ci-token-*）
   - 自動的にCI/CD Variablesへ登録

4. **CI/CD Variables自動設定（pushの前）**
   - `EC2_PUBLIC_IP` - サービスURL用
   - `SONAR_TOKEN` - SonarQube認証（Masked）
   - パイプライン実行時に変数が確実に存在

5. **Git初期化と自動push**
   - 各プロジェクトでGit初期化
   - GitLabリモート設定
   - 自動push → パイプライン自動起動

### 運用機能

- **パスワード管理**: 環境変数による一元管理、対話的設定
- **完全バックアップ**: 設定、データベース、リポジトリの一括バックアップ
- **スクラッチビルド**: ゼロからの完全環境再構築
- **ワンクリックデプロイ**: バックアップ → クリーンアップ → 再構築の自動化

---

## 🛠️ 技術スタック

### システム環境（検証済み構成）

| カテゴリ | 技術 | 厳密バージョン | 備考 |
|---------|------|-------------|------|
| OS | Red Hat Enterprise Linux | **9.7** | RHEL 9.7 (Plow) |
| コンテナ | Podman | **5.6.0** | Docker互換ランタイム |
| オーケストレーション | Docker Compose | **v3.8** | Podman Compose |
| Java Runtime | OpenJDK | **17.0.17 LTS** | Red Hat build |
| ビルドツール | Apache Maven | **3.6.3** | Red Hat 3.6.3-22 |

### CI/CDサービス（コンテナ）

| サービス | イメージ | 厳密バージョン | 用途 |
|---------|---------|-------------|------|
| **GitLab CE** | `gitlab/gitlab-ce` | **latest** | Git、CI/CD、レジストリ |
| **GitLab Runner** | `gitlab/gitlab-runner` | **latest** | CI/CD実行（Shell executor） |
| **Nexus Repository** | `sonatype/nexus3` | **latest** | Maven/npm/Docker アーティファクト管理 |
| **SonarQube** | `sonarqube` | **10-community** | 静的コード解析 |
| **PostgreSQL** | `postgres` | **16-alpine** | 統合データベース |
| **pgAdmin** | `dpage/pgadmin4` | **latest** | データベースGUI |

### アプリケーション技術スタック

#### フロントエンド

| カテゴリ | 技術 | 厳密バージョン | 設定箇所 |
|---------|------|-------------|---------|
| **フレームワーク** | React | **18.3.1** | package.json |
| **ビルドツール** | Vite | **5.4.11** | package.json |
| **テスト** | Jest | **29.7.0** | package.json |
| **テストライブラリ** | @testing-library/react | **16.0.1** | package.json |
| **UI** | React Router | **7.1.1** | package.json |

#### バックエンド

| カテゴリ | 技術 | 厳密バージョン | 設定箇所 |
|---------|------|-------------|---------|
| **Java** | OpenJDK | **17.0.17 LTS** | `maven.compiler.source/target` |
| **Spring Boot** | Spring Boot Starter Parent | **3.2.1** | 親POM `spring-boot.version` |
| **ORM** | Spring Data JPA + Hibernate | **3.2.1系** | Spring Boot依存 |
| **マイグレーション** | Flyway | **9.x系** | Spring Boot依存 |
| **ユーティリティ** | Lombok | **1.18.30** | 親POM `lombok.version` |

### テスト・品質管理

#### フロントエンド品質管理

| カテゴリ | 技術 | 設定 |
|---------|------|------|
| **カバレッジ形式** | LCOV | `jest.config.js` |
| **SonarQube連携** | sonar-scanner | `sonar-project.properties` |
| **カバレッジ閾値** | 90% 行カバレッジ | SonarQube Quality Gate |

#### バックエンド品質管理

| カテゴリ | 技術 | 厳密バージョン | 設定箇所 |
|---------|------|-------------|---------|
| **テストフレームワーク** | JUnit | **5.10.1** | 親POM `junit.version` |
| **モッキング** | Mockito | **5.8.0** | 親POM `mockito.version` |
| **カバレッジ** | JaCoCo Maven Plugin | **0.8.11** | 親POM `jacoco.version` |
| **SonarQube Scanner** | SonarQube Maven Plugin | **3.10.0.2594** | 親POM `sonar.version` |

### 品質ゲート基準

| プロジェクト | メトリクス | 設定値 | 設定箇所 |
|------------|----------|--------|---------|
| **フロントエンド** | 行カバレッジ | **≥ 90%** | SonarQube Quality Gate |
| **フロントエンド** | SonarQubeキー | `sample-app-frontend` | sonar-project.properties |
| **バックエンド** | 行カバレッジ | **≥ 90%** | 親POM `jacoco.line.ratio` |
| **バックエンド** | ブランチカバレッジ | **≥ 90%** | 親POM `jacoco.branch.ratio` |
| **バックエンド** | SonarQubeキー | `sample-app-backend` | 親POM `sonar.projectKey` |

---

## 🏗️ アーキテクチャ

### サービス構成

| サービス | ポート | 用途 | 依存関係 |
|---------|-------|------|---------|
| **PostgreSQL** | 5001 | 統合データベース | - |
| **pgAdmin** | 5002 | DB GUI管理 | PostgreSQL |
| **GitLab CE** | 5003 (HTTP)<br>2223 (SSH) | Git、CI/CD | PostgreSQL |
| **Nexus** | 8082 (UI/Maven)<br>8083 (Docker) | アーティファクト管理 | - |
| **SonarQube** | 8000 | 静的解析 | PostgreSQL |
| **Backend API** | 8501 | REST API | PostgreSQL |
| **Frontend** | 8500 | React UI | Backend API |

### GitLab プロジェクト構成（フロントエンド/バックエンド分離）

```
┌─────────────────────────────────────────────────────────────┐
│                    GitLab CE (:5003)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ sample-app-frontend-20260113-135159                    │ │
│  │ - React + Vite + Jest                                  │ │
│  │ - CI/CD: 5ステージ                                     │ │
│  │ - SonarQube: LCOV coverage                             │ │
│  │ - Deploy: Docker (Nginx)                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ sample-app-backend-20260113-135159                     │ │
│  │ - Spring Boot + Maven + JUnit                          │ │
│  │ - CI/CD: 7ステージ                                     │ │
│  │ - SonarQube: Maven plugin                              │ │
│  │ - Deploy: Nexus + Docker                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

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
│         │  Frontend:8500 │                               │
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
  - 2223 (GitLab SSH)
  - 8082 (Nexus)
  - 8000 (SonarQube)
  - 5002 (pgAdmin)
  - 8500 (Frontend)
  - 8501 (Backend API)

---

## 🚀 クイックスタート

### スクリプト実行方法一覧

すべてのスクリプトは`scripts/`ディレクトリに配置されています。実行前に必ず実行権限を付与してください。

```bash
# 実行権限の付与（初回のみ）
cd /root/aws.git/container/claudecode/CICD
chmod +x scripts/*.sh scripts/utils/*.sh
```

#### スクリプト実行権限一覧表

| スクリプト名 | 実行コマンド | 必須権限 | 用途 |
|------------|------------|---------|------|
| `setup-from-scratch.sh` | `sudo ./scripts/setup-from-scratch.sh` | **sudo必須** | 初回環境構築（12ステップ） |
| `setup-sample-app-split.sh` | `./scripts/setup-sample-app-split.sh` | 通常ユーザー | **【推奨】フロントエンド/バックエンド分離CI/CD検証** |
| `show-credentials.sh` | `./scripts/utils/show-credentials.sh` | 通常ユーザー | 認証情報表示 |
| `update-passwords.sh` | `./scripts/utils/update-passwords.sh [オプション]` | 通常ユーザー | パスワード/トークン更新 |
| `backup-all.sh` | `sudo ./scripts/utils/backup-all.sh` | **sudo必須** | 完全バックアップ |
| `restore-all.sh` | `sudo ./scripts/utils/restore-all.sh <backup-dir>` | **sudo必須** | バックアップから復元 |
| `cleanup-all.sh` | `sudo ./scripts/cleanup-all.sh` | **sudo必須** | 全リソース削除 |
| `deploy-oneclick.sh` | `sudo ./scripts/utils/deploy-oneclick.sh` | **sudo必須** | ワンクリック再デプロイ |

### 1. ゼロからセットアップ

```bash
# リポジトリをクローン（または既存ディレクトリに移動）
cd /root/aws.git/container/claudecode/CICD

# スクリプトに実行権限を付与（初回のみ）
chmod +x scripts/*.sh scripts/utils/*.sh

# セットアップ実行（sudoで実行）
sudo ./scripts/setup-from-scratch.sh
```

**セットアップ内容（12ステップ）**:
1. システムパッケージのインストール
2. SELinux設定の調整
3. Podmanソケットの有効化
4. ディレクトリ構造の作成
5. **管理者パスワードの設定**（対話的入力、確認入力で誤入力防止）
6. **EC2ドメイン名/IPアドレスの設定**（対話的入力、自動検出対応）
7. 環境変数ファイル（.env）の生成・更新（既存トークンを自動保持）
8. Docker Compose設定の確認
9. コンテナの起動
10. GitLab Runnerのインストール
11. Maven設定の配置（EC2ドメイン名とパスワードを動的置換）
12. セットアップ完了チェック

**重要な機能**:
- **トークン保持**: 既存の `.env` ファイルがある場合、SONAR_TOKEN と RUNNER_TOKEN を自動保持
- **バックアップ作成**: .env 更新時、自動的にバックアップ（.env.backup.YYYYMMDDHHMMSS）を作成
- **EC2ドメイン対応**: 入力なしの場合、EC2メタデータサービスから自動検出（169.254.169.254）

### 2. サービス状態確認

```bash
# コンテナ起動確認
sudo podman ps

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
  --url http://${EC2_PUBLIC_IP}:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runnerの起動
sudo systemctl enable --now gitlab-runner
sudo systemctl status gitlab-runner
```

### 4. フロントエンド/バックエンド分離CI/CD検証（自動化）

**前提条件**: コンテナ起動完了、GitLab Runner登録完了

```bash
# フロントエンド/バックエンド分離プロジェクト自動作成（通常ユーザーで実行）
cd /root/aws.git/container/claudecode/CICD
./scripts/setup-sample-app-split.sh
```

**スクリプト機能（完全自動化）**:
- ✅ **GitLab Personal Access Token自動生成** - API操作用トークン
- ✅ **2プロジェクト自動作成** - フロントエンド/バックエンド独立
- ✅ **SonarQubeトークン自動生成** - プロジェクトごとに専用トークン
- ✅ **CI/CD Variables自動設定** - pushの前に環境変数設定
- ✅ **タイムスタンプ付与** - 実行時刻でプロジェクト名ユニーク化
- ✅ **自動Git初期化とpush** - 2プロジェクトを並行処理

**実行ステップ（自動化）**:
1. **環境変数読み込み** - .envからEC2_PUBLIC_IP取得
2. **実行ID生成** - YYYYMMDD-HHMMSS形式
3. **作業ディレクトリクリーンアップ** - 既存 /tmp ファイル削除
4. **GitLab Personal Access Token作成** - GitLab Rails Console経由
5. **GitLabプロジェクト作成（API）** - フロントエンド/バックエンド
6. **CI/CD Variables設定（フロントエンド）** - EC2_PUBLIC_IP, SONAR_TOKEN
7. **GitLabリモート設定とpush（フロントエンド）**
8. **CI/CD Variables設定（バックエンド）** - EC2_PUBLIC_IP, SONAR_TOKEN
9. **GitLabリモート設定とpush（バックエンド）**
10. **セットアップ完了表示** - プロジェクトURL、パイプラインURL

**パイプライン自動実行**:
```
フロントエンド (5ステージ):
  install → lint → test → sonarqube → build

バックエンド (7ステージ):
  build → test → coverage → sonarqube → package → nexus-deploy → container-deploy
```

**確認URL**:
```bash
# フロントエンドプロジェクト
http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-YYYYMMDD-HHMMSS

# バックエンドプロジェクト
http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-YYYYMMDD-HHMMSS

# SonarQubeダッシュボード
http://${EC2_PUBLIC_IP}:8000/dashboard?id=sample-app-frontend
http://${EC2_PUBLIC_IP}:8000/dashboard?id=sample-app-backend

# デプロイ済みアプリケーション
http://${EC2_PUBLIC_IP}:8500  # フロントエンド
http://${EC2_PUBLIC_IP}:8501  # バックエンドAPI
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
   - GitLab CI/CD環境変数に `SONAR_TOKEN` を設定（setup-sample-app-split.shで自動設定）
   - パイプライン実行時に自動的に環境変数を参照

### サービス別ログイン情報

#### 1. GitLab
```
URL: http://${EC2_PUBLIC_IP}:5003
ユーザー名: root
パスワード: ${GITLAB_ROOT_PASSWORD} (デフォルト: Degital2026!)
```

#### 2. Nexus Repository
```
URL: http://${EC2_PUBLIC_IP}:8082
ユーザー名: admin
初期パスワード: admin123 (固定)
```
- **初回ログイン後の対応**:
  - **必須**: 初回ログイン時にパスワード変更が求められます
  - 新しいパスワードを設定（推奨: Degital2026!）
  - セットアップウィザードに従って初期設定を完了
  - **重要**: パスワード変更後、`.env` ファイルの `NEXUS_ADMIN_PASSWORD` を更新:
    ```bash
    ./scripts/utils/update-passwords.sh --nexus 新しいパスワード
    ```

#### 3. SonarQube
```
URL: http://${EC2_PUBLIC_IP}:8000
デフォルト: admin / admin
```
- **初回ログイン後の対応**:
  - 必ずパスワード変更を求められます
  - 新しいパスワードを設定したら、`.env` ファイルの `SONARQUBE_ADMIN_PASSWORD` を更新
  - **SonarQubeトークンは setup-sample-app-split.sh で自動生成されます**

#### 4. pgAdmin
```
URL: http://${EC2_PUBLIC_IP}:5002
Email: admin@example.com
パスワード: ${PGADMIN_PASSWORD}
```

#### 5. PostgreSQL
```
ホスト: localhost
ポート: 5001
ユーザー名: cicduser
パスワード: ${POSTGRES_PASSWORD}
データベース: cicddb
```

---

## 📦 サンプルアプリケーション

### 概要

組織管理システム - Spring Boot + Reactによる3階層CRUD アプリケーション（フロントエンド/バックエンド分離構成）

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

**バックエンド**:
```bash
cd sample-app
mvn clean test

# カバレッジレポート生成
mvn jacoco:report
open backend/target/site/jacoco/index.html
```

**フロントエンド**:
```bash
cd sample-app/frontend
npm test
npm test -- --coverage
```

---

## 🔄 CI/CDパイプライン

### フロントエンドパイプライン構成（5ステージ）

`.gitlab-ci.yml.frontend` で定義された自動化パイプライン:

```
install → lint → test → sonarqube → build
```

#### 1. Install ステージ
```yaml
- npm ci でパッケージインストール
- 成果物: node_modules/
- 実行時間: ~30秒
```

#### 2. Lint ステージ
```yaml
- ESLint による静的解析
- コーディング規約チェック
- 実行時間: ~10秒
```

#### 3. Test ステージ
```yaml
- Jest + @testing-library/react によるユニットテスト
- カバレッジレポート生成（LCOV形式）
- 成果物: coverage/lcov.info
- 実行時間: ~20秒
```

#### 4. SonarQube ステージ
```yaml
- SonarQube Scanner による静的解析
- LCOV カバレッジレポート送信
- 品質ゲートチェック（90%カバレッジ）
- 実行時間: ~30秒
```

#### 5. Build ステージ
```yaml
- Vite による本番ビルド
- 成果物: dist/
- 実行時間: ~15秒
```

### バックエンドパイプライン構成（7ステージ）

`.gitlab-ci.yml.backend` で定義された自動化パイプライン:

```
build → test → coverage → sonarqube → package → nexus-deploy → container-deploy
```

#### 1. Build ステージ
```yaml
- Maven コンパイル
- 成果物: target/classes
- 実行時間: ~1分
```

#### 2. Test ステージ
```yaml
- JUnit 5 単体テスト実行
- JaCoCo カバレッジ測定
- 実行時間: ~2分
```

#### 3. Coverage ステージ
```yaml
- JaCoCo レポート生成
- カバレッジ集計（90%閾値）
- 成果物: backend/target/site/jacoco/
- 実行時間: ~30秒
```

#### 4. SonarQube ステージ
```yaml
- Maven sonar:sonar による静的解析
- 品質ゲートチェック
- バグ、脆弱性、コードスメル検出
- 実行時間: ~1-2分
```

#### 5. Package ステージ
```yaml
- Maven パッケージング（JAR生成）
- 成果物: backend/target/*.jar
- 実行時間: ~1分
```

#### 6. Nexus Deploy ステージ
```yaml
- Nexus Repository へデプロイ
- Maven アーティファクトアップロード
- Maven settings.xml 動的生成
- 実行時間: ~1分
```

#### 7. Container Deploy ステージ
```yaml
- Dockerコンテナビルド＆デプロイ
- バックエンドAPI起動
- ヘルスチェック確認
- 実行時間: ~2分
```

### パイプライン実行

#### 自動実行
```bash
# setup-sample-app-split.sh 実行時に自動的にpushされ、パイプライン起動
./scripts/setup-sample-app-split.sh
```

#### 手動実行
```
GitLab UI → CI/CD → Pipelines → Run Pipeline
```

### 品質ゲート基準

**フロントエンド**:
| メトリクス | 基準値 |
|----------|--------|
| 行カバレッジ | ≥ 90% |
| 重大バグ | 0件 |
| 脆弱性（高リスク） | 0件 |

**バックエンド**:
| メトリクス | 基準値 |
|----------|--------|
| 行カバレッジ | ≥ 90% |
| ブランチカバレッジ | ≥ 90% |
| 重大バグ | 0件 |
| 脆弱性（高リスク） | 0件 |
| コード重複率 | ≤ 3% |
| 保守性レーティング | A |

### パイプライン最適化

- **キャッシュ**: npm cache, Maven `.m2/repository` をキャッシュ
- **並列化**: 各ステージを順次実行、依存関係を明示
- **アーティファクト**: テストレポートとカバレッジレポートを1週間保持
- **タイムスタンプ**: プロジェクト名に実行時刻を付与し、複数サンプル共存可能

---

## 🛠️ 運用管理

### 運用スクリプト一覧

| スクリプト | 説明 | 用途 |
|----------|------|------|
| `setup-from-scratch.sh` | ゼロから完全環境構築（12ステップ、トークン保持） | 新規環境セットアップ、再セットアップ |
| `setup-sample-app-split.sh` | **【推奨】フロントエンド/バックエンド分離CI/CD検証（完全自動化）** | **セットアップ後のCI/CD動作検証** |
| `show-credentials.sh` | 全サービスの認証情報表示 | 認証情報確認、ファイル出力 |
| `update-passwords.sh` | パスワード・トークン・EC2ホスト更新 | パスワード変更、EC2ドメイン変更 |
| `backup-all.sh` | 完全バックアップ | 定期バックアップ、移行前 |
| `restore-all.sh` | バックアップから復元 | 災害復旧、環境移行 |
| `cleanup-all.sh` | 全リソース削除 | 環境クリーンアップ |
| `deploy-oneclick.sh` | ワンクリック再デプロイ | 環境リフレッシュ |

### フロントエンド/バックエンド分離CI/CD検証（setup-sample-app-split.sh）

#### スクリプト概要

セットアップ完了後にCI/CD環境が正常動作するかを検証する完全自動化スクリプトです。

```bash
# 基本実行（環境変数から自動取得）
./scripts/setup-sample-app-split.sh
```

#### 完全自動化機能（v2.6.0）

**自動化されている処理**:
1. ✅ **GitLab Personal Access Token自動生成** - GitLab Rails Console経由
2. ✅ **2プロジェクト自動作成（API）** - フロントエンド/バックエンド独立
3. ✅ **SonarQubeトークン自動生成** - SonarQube API経由、プロジェクトごとに専用
4. ✅ **CI/CD Variables自動設定** - pushの前に環境変数を設定
5. ✅ **タイムスタンプ付与** - 実行時刻でプロジェクト名ユニーク化
6. ✅ **自動Git初期化とpush** - 2プロジェクトを並行処理
7. ✅ **パイプライン自動起動** - push時に自動的にCI/CD開始

**実行ログ例**:
```bash
[1/7] 環境変数確認中...
  ✓ EC2_PUBLIC_IP: ec2-xx-xx-xx-xx.compute-1.amazonaws.com
  ✓ 実行ID: 20260113-135159

[4/7] GitLab Personal Access Token 作成中...
  ✓ Personal Access Token作成完了: glpat-xxxxxxxxxxxxxxxxxxxx

[5/7] GitLab API経由でプロジェクト作成中...
  ✓ フロントエンドプロジェクト作成完了: sample-app-frontend-20260113-135159
  ✓ バックエンドプロジェクト作成完了: sample-app-backend-20260113-135159

[6/7] CI/CD Variables 設定中（フロントエンド）...
  ✓ EC2_PUBLIC_IP設定完了
  🔍 SonarQubeトークン生成中...
  ✓ SonarQubeトークン生成完了: sqa_xxxxxxxxxxxxxxxxxxxx
  ✓ SONAR_TOKEN設定完了

[7/7] GitLabリモート設定とプッシュ中（フロントエンド）...
  ✓ GitLabプッシュ完了
  ✓ パイプライン自動起動

========================================
🎉 セットアップ完了
========================================
📁 作成されたGitLabプロジェクト:
  - フロントエンド: http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5003/root/sample-app-frontend-20260113-135159
  - バックエンド: http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5003/root/sample-app-backend-20260113-135159

🔍 パイプライン状況:
  - フロントエンド: http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5003/root/sample-app-frontend-20260113-135159/-/pipelines
  - バックエンド: http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5003/root/sample-app-backend-20260113-135159/-/pipelines
```

#### 検証項目

**統合サービス確認**:
1. **GitLab**: 2プロジェクト作成、プッシュ、パイプライン起動
2. **GitLab Runner**: Shell executor でのジョブ実行
3. **Maven**: マルチモジュールビルド・テスト実行（バックエンド）
4. **npm**: Viteビルド・Jestテスト実行（フロントエンド）
5. **JaCoCo**: カバレッジレポート生成（バックエンド、90%達成確認）
6. **Jest**: LCOVカバレッジレポート生成（フロントエンド、90%達成確認）
7. **SonarQube**: 2プロジェクトの静的解析（フロントエンド: LCOV、バックエンド: Maven plugin）
8. **Nexus**: maven-snapshotsへのアーティファクトデプロイ（バックエンド）
9. **Container Deploy**: Dockerコンテナビルド＆起動（バックエンド）

**CI/CDパイプライン**:
```
フロントエンド (5ステージ): install → lint → test → sonarqube → build
バックエンド (7ステージ): build → test → coverage → sonarqube → package → nexus-deploy → container-deploy
```

#### トラブルシューティング

**よくある問題と解決策**:

```bash
# GitLab Runner未起動の場合
sudo systemctl start gitlab-runner
sudo systemctl status gitlab-runner

# パイプライン失敗時の詳細確認
# GitLab UI → Projects → sample-app-frontend-* or sample-app-backend-* → CI/CD → Pipelines

# SonarQubeトークン確認
curl -u admin:${SONARQUBE_ADMIN_PASSWORD} \
  "http://${EC2_PUBLIC_IP}:8000/api/user_tokens/search"

# Nexusアーティファクト確認（バックエンド）
curl -u admin:${NEXUS_ADMIN_PASSWORD} \
  "http://${EC2_PUBLIC_IP}:8082/service/rest/v1/search?repository=maven-snapshots&q=sample-app"
```

### 認証情報管理

#### 認証情報の表示

```bash
# 全サービスの認証情報を表示
./scripts/utils/show-credentials.sh

# ファイルに出力（600パーミッション）
./scripts/utils/show-credentials.sh --file
# 出力先: /root/aws.git/container/claudecode/CICD/credentials.txt

# 表示内容:
# - CI/CDサービス（GitLab、Nexus、SonarQube、pgAdmin）
# - PostgreSQLスキーマ別認証情報（4データベース）
# - CI/CDトークン（SONAR_TOKEN、RUNNER_TOKEN）
# - 初回ログイン手順（パスワード変更が必要なサービス）
```

#### パスワード・設定の更新

```bash
# 現在の設定を表示
./scripts/utils/update-passwords.sh --show

# 個別更新
./scripts/utils/update-passwords.sh --gitlab NewPassword123!
./scripts/utils/update-passwords.sh --nexus NewPassword123!
./scripts/utils/update-passwords.sh --sonarqube NewPassword123!

# SonarQubeトークン更新
./scripts/utils/update-passwords.sh --sonar-token sqa_xxxxxxxxxxxxxxxx

# EC2ドメイン名/IPアドレス更新
./scripts/utils/update-passwords.sh --ec2-host ec2-34-205-156-203.compute-1.amazonaws.com
./scripts/utils/update-passwords.sh --ec2-host 192.168.1.100

# 全パスワード一括更新（トークンを除く）
./scripts/utils/update-passwords.sh --all Degital2026!

# 更新内容:
# - 自動バックアップ作成（.env.backup.YYYYMMDDHHMMSS）
# - .envファイルの該当項目を更新
# - 変更後の再起動が必要な場合は案内表示
```

### バックアップ＆復元

#### バックアップ

```bash
# 完全バックアップ実行（sudoで実行）
sudo ./scripts/utils/backup-all.sh

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

#### 復元

```bash
# バックアップアーカイブの展開
tar xzf backup-20260113-135159.tar.gz

# 復元実行（sudoで実行）
sudo ./scripts/utils/restore-all.sh backup-20260113-135159

# 復元内容
# - コンテナ停止＆削除
# - 設定ファイル復元
# - コンテナ再起動
# - GitLab データベース復元
# - GitLab リポジトリ復元
# - GitLab Runner 設定復元
# - Maven 設定復元
```

### クリーンアップ

```bash
# 全リソース削除（確認プロンプトあり、sudoで実行）
sudo ./scripts/cleanup-all.sh

# 削除対象
# - 全コンテナ（cicd-*）
# - 全ボリューム（cicd-*）
# - ネットワーク（cicd-network）
# - GitLab Runner 設定（オプション）
# - Maven 設定（オプション）
```

### サービス管理

```bash
# 全サービス起動
cd /root/aws.git/container/claudecode/CICD
sudo podman-compose up -d

# 全サービス停止
sudo podman-compose down

# 特定サービスの再起動
sudo podman-compose restart gitlab
sudo podman-compose restart nexus
sudo podman-compose restart sonarqube

# ログ確認
sudo podman-compose logs -f gitlab
sudo podman-compose logs -f nexus
sudo podman-compose logs -f sonarqube

# リソース使用状況
sudo podman stats
```

---

## 🔍 トラブルシューティング

### 1. コンテナが起動しない

**症状**: `sudo podman-compose up -d` 後、コンテナがすぐに停止する

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
sudo ss -tuln | grep -E '5001|5002|5003|8000|8082|8500|8501'

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
sudo podman ps -a | grep gitlab

# GitLab初期化完了まで待機（5-10分）
sudo podman logs -f cicd-gitlab

# "gitlab Reconfigured!" が表示されるまで待つ

# 初期パスワード確認（24時間以内）
sudo podman exec -it cicd-gitlab cat /etc/gitlab/initial_root_password
```

### 3. CI/CDパイプラインが失敗する

#### フロントエンドパイプライン失敗

##### SonarQube ステージ失敗（フロントエンド）
```bash
# SonarQubeトークン確認
# GitLab → Settings → CI/CD → Variables → SONAR_TOKEN

# SonarQube接続確認
curl http://${EC2_PUBLIC_IP}:8000/api/system/status

# test-report.xml エラーの場合
# → sonar-project.properties から sonar.testExecutionReportPaths 削除
# → React + Jest は LCOV のみ使用

# カバレッジ不足の場合
cd sample-app/frontend
npm test -- --coverage
```

#### バックエンドパイプライン失敗

##### Build ステージ失敗
```bash
# Maven依存関係の問題
cd sample-app
mvn clean install -U  # 依存関係を強制更新

# Nexusプロキシ設定確認
curl http://${EC2_PUBLIC_IP}:8082/repository/maven-public/
```

##### Test ステージ失敗
```bash
# テストをローカル実行して詳細確認
cd sample-app
mvn clean test -X  # デバッグモード

# テストケース個別実行
mvn test -Dtest=OrganizationServiceTest
```

##### SonarQube ステージ失敗（バックエンド）
```bash
# SonarQube接続確認
curl http://${EC2_PUBLIC_IP}:8000/api/system/status

# SonarQubeログ確認
sudo podman logs cicd-sonarqube

# カバレッジ不足の場合
cd sample-app
mvn clean test jacoco:report
open backend/target/site/jacoco/index.html
```

##### Nexus Deploy ステージ失敗（401 Unauthorized）
```bash
# Nexusパスワード確認
cat .env | grep NEXUS_ADMIN_PASSWORD

# Nexusログイン確認
curl -u admin:${NEXUS_ADMIN_PASSWORD} \
  "http://${EC2_PUBLIC_IP}:8082/service/rest/v1/status"

# Maven settings.xml 確認
# .gitlab-ci.yml.backend の before_script で自動生成される
```

##### Container Deploy ステージ失敗
```bash
# JARファイル確認
ls -lh /tmp/gitlab-sample-app-backend-*/backend/target/*.jar

# Dockerビルドログ確認
sudo podman logs sample-backend

# ヘルスチェック手動確認
curl http://${EC2_PUBLIC_IP}:8501/api/organizations
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
  --url http://${EC2_PUBLIC_IP}:5003 \
  --token YOUR_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runnerログ確認
sudo journalctl -u gitlab-runner -f
```

### 5. EC2インスタンス再作成時のドメイン名/IP変更

**症状**: EC2インスタンスを再作成したら、IPアドレスが変わってサービスにアクセスできない

**対策**:

#### 方法1: セットアップスクリプトで更新（推奨）
```bash
# セットアップ時にドメイン名/IPを再入力（sudoで実行）
sudo ./scripts/setup-from-scratch.sh

# ステップ6で新しいドメイン名/IPを入力
# 例: ec2-34-205-156-203.compute-1.amazonaws.com
# 例: 192.168.1.100

# 既存の.envファイルがある場合、トークンは自動保持されます
```

#### 方法2: 更新スクリプトを使用
```bash
# EC2ドメイン名/IPのみ更新
./scripts/utils/update-passwords.sh --ec2-host ec2-34-205-156-203.compute-1.amazonaws.com

# 自動でバックアップが作成されます
# .env.backup.YYYYMMDDHHMMSS
```

**影響範囲と追加対応**:
```bash
# 1. GitLabプロジェクトのリモートURLを更新
cd /tmp/gitlab-sample-app-frontend-*
git remote set-url origin http://NEW_IP:5003/root/sample-app-frontend-*/

cd /tmp/gitlab-sample-app-backend-*
git remote set-url origin http://NEW_IP:5003/root/sample-app-backend-*/

# 2. GitLab Runnerの再登録（必要に応じて）
sudo gitlab-runner unregister --all-runners
sudo gitlab-runner register \
  --url http://NEW_IP:5003 \
  --token YOUR_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# 3. 認証情報の確認
./scripts/utils/show-credentials.sh
```

### 6. 再セットアップ時のトークン消失

**症状**: setup-from-scratch.sh を再実行したら、SonarQubeトークンやGitLab Runnerトークンが消えた

**原因**: 旧バージョンでは .env ファイルが上書きされていました

**解決済み**:
- **最新版では自動的にトークンを保持します**
- 既存の .env ファイルがある場合、以下のトークンを自動保持:
  - `SONAR_TOKEN`
  - `RUNNER_TOKEN`
- 自動バックアップも作成されます: `.env.backup.YYYYMMDDHHMMSS`

**確認方法**:
```bash
# 再セットアップ前
cat .env | grep -E "SONAR_TOKEN|RUNNER_TOKEN"

# 再セットアップ実行（sudoで実行）
sudo ./scripts/setup-from-scratch.sh

# 再セットアップ後（トークンが保持されていることを確認）
cat .env | grep -E "SONAR_TOKEN|RUNNER_TOKEN"

# バックアップも確認可能
ls -la .env.backup.*
```

**手動復元が必要な場合**:
```bash
# 最新のバックアップから復元
cp .env.backup.20260113135159 .env

# または、個別更新スクリプトで設定
./scripts/utils/update-passwords.sh --sonar-token sqa_xxxxxxxxxxxxx
./scripts/utils/update-passwords.sh --runner-token glrt_xxxxxxxxxxxxx
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

# 機密情報も .gitignore で保護
# - credentials.txt（認証情報ファイル）
# - .env.backup.*（自動バックアップ）
```

#### 2. 初回セットアップ時の設定
```bash
# setup-from-scratch.sh 実行時に対話的入力
# - 最低8文字
# - 確認入力による誤入力防止
# - 英数字記号の組み合わせ推奨

# 再セットアップ時の安全機能
# - 既存.envファイル検出時、トークンを自動保持
# - .env.backup.YYYYMMDDHHMMSS 形式でバックアップ
# - SONAR_TOKEN、RUNNER_TOKENは消失しない
```

#### 3. CI/CDでの取り扱い
```bash
# GitLab CI/CD環境変数（Masked）
# setup-sample-app-split.sh で自動設定
# Settings → CI/CD → Variables
EC2_PUBLIC_IP=ec2-xx-xx-xx-xx.compute-1.amazonaws.com
SONAR_TOKEN=sqa_xxxxx...  (Masked)

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
sudo firewall-cmd --permanent --add-port=8500/tcp  # Frontend
sudo firewall-cmd --permanent --add-port=8501/tcp  # Backend API
sudo firewall-cmd --reload

# 機密ファイルのパーミッション
chmod 600 .env                  # 環境変数ファイル
chmod 600 .env.backup.*         # 自動バックアップ
chmod 600 credentials.txt       # 認証情報（show-credentials.sh --file で作成時）

# 使用後は認証情報ファイルを削除
rm -f credentials.txt
```

#### 3. バックアップの暗号化
```bash
# バックアップアーカイブを暗号化
gpg --symmetric --cipher-algo AES256 backup-20260113-135159.tar.gz

# 復号化
gpg --decrypt backup-20260113-135159.tar.gz.gpg > backup-20260113-135159.tar.gz
```

---

## 📚 参考資料

### 公式ドキュメント

- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Repository Manager Documentation](https://help.sonatype.com/repomanager3)
- [SonarQube Documentation](https://docs.sonarqube.org/latest/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Jest Documentation](https://jestjs.io/)

### プロジェクト関連

**注意**: URLのIPアドレス部分は実際のEC2インスタンスのIPアドレスに置き換えてください。

- **GitLab**: http://${EC2_PUBLIC_IP}:5003
- **Nexus**: http://${EC2_PUBLIC_IP}:8082
- **SonarQube**: http://${EC2_PUBLIC_IP}:8000
- **pgAdmin**: http://${EC2_PUBLIC_IP}:5002
- **Frontend**: http://${EC2_PUBLIC_IP}:8500
- **Backend API**: http://${EC2_PUBLIC_IP}:8501

### Issue管理

このプロジェクトは **Issue #115** および **Issue #116** の一環として実装されました。

---

## 📝 ライセンス

このプロジェクトは学習・評価目的で作成されています。

---

## 👥 貢献者

- 初期実装: Claude Code (Claude Sonnet 4.5)
- プロジェクト管理: Issue #115, #116

---

## 📞 サポート

問題が発生した場合:

1. [トラブルシューティング](#トラブルシューティング)セクションを確認
2. ログを確認（`sudo podman logs <container_name>`）
3. GitLabプロジェクトのIssuesに報告

---

**最終更新日**: 2026-01-13
**バージョン**: 2.6.0

**変更履歴 (v2.6.0 - 最新)**:
- ✅ **フロントエンド/バックエンド完全分離構成** - GitLab上で2つの独立プロジェクト
- ✅ **setup-sample-app-split.sh 実装** - 完全自動化セットアップスクリプト
- ✅ **GitLab Personal Access Token自動生成** - GitLab Rails Console経由
- ✅ **SonarQubeトークン自動生成** - SonarQube API経由、プロジェクトごとに専用
- ✅ **CI/CD Variables自動設定（pushの前）** - パイプライン実行時に変数確実存在
- ✅ **プロジェクト名タイムスタンプ付与** - 複数サンプル共存可能
- ✅ **React + Jest + SonarQube LCOV専用構成** - test-report.xml不要
- ✅ **2つの.gitlab-ci.ymlファイル** - フロントエンド5ステージ、バックエンド7ステージ
- ✅ **GitLabプロジェクトからマスタへ資源同期完了** - rsync完全コピー、GitHub反映

**変更履歴 (v2.5.1)**:
- ✅ バックエンドCI/CD成功、フロントエンド認証自動化対応中

**変更履歴 (v2.5.0)**:
- ✅ プロジェクト分割対応（暫定版）

**変更履歴 (v2.4.1)**:
- ✅ バックエンド完成版

**動作検証完了環境**:
- ✅ **OS**: Red Hat Enterprise Linux 9.7 (Plow)
- ✅ **コンテナ**: Podman 5.6.0, Docker Compose v3.8
- ✅ **Java**: OpenJDK 17.0.17 LTS (Red Hat build)
- ✅ **CI/CD**: GitLab CE latest, GitLab Runner latest (Shell executor)
- ✅ **品質管理**: SonarQube 10-community, JaCoCo 0.8.11, Jest 29.7.0
- ✅ **アーティファクト**: Nexus 3.x latest, Maven 3.6.3
- ✅ **データベース**: PostgreSQL 16-alpine, pgAdmin latest
- ✅ **フロントエンド**: React 18.3.1, Vite 5.4.11, Jest 29.7.0
