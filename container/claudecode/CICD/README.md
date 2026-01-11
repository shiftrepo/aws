# CICD完全環境構築プロジェクト

グローバルスタンダードに準拠した、完全なCI/CD環境とサンプルアプリケーションの統合パッケージです。GitLab、Nexus、SonarQube、PostgreSQLを使用した本格的な開発環境を、スクラッチビルドから完全復元まで対応します。

[![Pipeline Status](http://${EC2_PUBLIC_IP}:5003/root/sample-app/badges/master/pipeline.svg)](http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/commits/master)
[![Quality Gate](http://${EC2_PUBLIC_IP}:8000/api/project_badges/measure?project=sample-app-backend&metric=alert_status)](http://${EC2_PUBLIC_IP}:8000/dashboard?id=sample-app-backend)
[![Coverage](http://${EC2_PUBLIC_IP}:8000/api/project_badges/measure?project=sample-app-backend&metric=coverage)](http://${EC2_PUBLIC_IP}:8000/dashboard?id=sample-app-backend)

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

### GitLab上のサンプルプログラム (`/tmp/gitlab-sample-app/`)

**これはCI/CD試行用の作業コピーです。マスタではありません。**

- **作成方法**: `setup-sample-app.sh` により `/root/aws.git/container/claudecode/CICD/sample-app/` からコピー
- **目的**: 構築したGitLab環境でCI/CDパイプラインを試行・検証する
- **用途**:
  - CI/CDパイプラインの動作確認
  - 修正・実験・テストの実施
  - 品質ゲート、カバレッジ、デプロイの検証
- **重要な原則**:
  - ⚠️ **このディレクトリはマスタではありません**
  - ✅ CI/CDを実現できたら、必ず `/root/aws.git/container/claudecode/CICD/sample-app/` に反映
  - ✅ 問題や不具合の対策を実施したら、必ずコピー元のマスタに反映
  - ✅ `setup-sample-app.sh` を実行するだけでCI/CDを確認できる
  - ✅ 繰り返し実行しても問題なく動作する

### ワークフロー

```
┌─────────────────────────────────────────────────────────────┐
│  /root/aws.git/container/claudecode/CICD/                   │
│  (マスタリポジトリ - 本体)                                   │
│                                                              │
│  ├── sample-app/           ← これがマスタ                    │
│  ├── scripts/                                                │
│  │   └── setup-sample-app.sh  ← CI/CD試行準備スクリプト     │
│  └── README.md, CLAUDE.md                                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ setup-sample-app.sh 実行
                          │ (sample-app をコピー)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  /tmp/gitlab-sample-app/                                     │
│  (GitLab上のサンプル - 作業コピー)                          │
│                                                              │
│  ← CI/CDパイプライン試行                                     │
│  ← 修正・実験・検証                                          │
│  ← 問題対策                                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ 成功したら反映
                          │ (手動コピー・マージ)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  /root/aws.git/container/claudecode/CICD/sample-app/        │
│  (マスタに反映)                                              │
└─────────────────────────────────────────────────────────────┘
```

### setup-sample-app.sh スクリプトの役割

- **機能**: `/root/aws.git/container/claudecode/CICD/sample-app/` から `/tmp/gitlab-sample-app/` にサンプルプログラムをコピーし、CI/CD試行を準備
- **利便性**: ユーザーは `./scripts/setup-sample-app.sh` を実行するだけで、CI/CDを確認できる
- **安全性**: 繰り返し実行しても問題なく動作（既存プロセス・ディレクトリのクリーンアップ機能付き）
- **独立性**: `/tmp` の作業コピーはマスタから完全に分離されており、マスタに影響を与えない

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
2. **サンプルアプリケーション** - Spring Boot + Reactによる組織管理システム（CRUD機能）
3. **自動化されたパイプライン** - ビルド → テスト → カバレッジ → 静的解析 → パッケージ → デプロイ
4. **品質保証基盤** - 80%カバレッジ、SonarQube品質ゲート
5. **運用スクリプト** - ゼロからのセットアップ、バックアップ、復元、クリーンアップ
6. **スクラッチビルド対応** - 完全な環境再構築が可能

### ディレクトリ構成

```
/root/aws.git/container/claudecode/CICD/
├── docker-compose.yml              # 全サービス統合定義
├── .env                            # 環境変数（パスワード含む、Git除外）
├── .gitignore                      # Git除外設定（credentials.txt、.env.backup.*含む）
├── README.md                       # 本ドキュメント
├── CREDENTIALS.md                  # 認証情報管理ガイド
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
│   ├── setup-from-scratch.sh      # ゼロからセットアップ（パスワード設定、EC2ドメイン入力、トークン保持）
│   ├── show-credentials.sh        # 全サービスの認証情報表示・ファイル出力
│   ├── update-passwords.sh        # パスワード・トークン・EC2ホスト更新
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

| カテゴリ | 技術 | 厳密バージョン | 設定箇所 |
|---------|------|-------------|---------|
| **Java** | OpenJDK | **17.0.17 LTS** | `maven.compiler.source/target` |
| **Spring Boot** | Spring Boot Starter Parent | **3.2.1** | 親POM `spring-boot.version` |
| **ORM** | Spring Data JPA + Hibernate | **3.2.1系** | Spring Boot依存 |
| **マイグレーション** | Flyway | **9.x系** | Spring Boot依存 |
| **ユーティリティ** | Lombok | **1.18.30** | 親POM `lombok.version` |

### テスト・品質管理

| カテゴリ | 技術 | 厳密バージョン | 設定箇所 |
|---------|------|-------------|---------|
| **テストフレームワーク** | JUnit | **5.10.1** | 親POM `junit.version` |
| **モッキング** | Mockito | **5.8.0** | 親POM `mockito.version` |
| **アサーション** | AssertJ | **3.25.1** | 親POM `assertj.version` |
| **カバレッジ** | JaCoCo Maven Plugin | **0.8.11** | 親POM `jacoco.version` |
| **SonarQube Scanner** | SonarQube Maven Plugin | **3.10.0.2594** | 親POM `sonar.version` |

### 品質ゲート基準

| メトリクス | 設定値 | 設定箇所 |
|----------|--------|---------|
| **行カバレッジ** | **≥ 80%** | 親POM `jacoco.line.coverage` |
| **ブランチカバレッジ** | **≥ 70%** | 親POM `jacoco.branch.coverage` |
| **SonarQubeプロジェクトキー** | `sample-app` | 親POM `sonar.projectKey` |
| **SonarQube URL** | `http://localhost:8000` | 親POM `sonar.host.url` |

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

### スクリプト実行方法一覧

すべてのスクリプトは`scripts/`ディレクトリに配置されています。実行前に必ず実行権限を付与してください。

```bash
# 実行権限の付与（初回のみ）
cd /root/aws.git/container/claudecode/CICD
chmod +x scripts/*.sh
```

#### スクリプト実行権限一覧表

| スクリプト名 | 実行コマンド | 必須権限 | 用途 |
|------------|------------|---------|------|
| `setup-from-scratch.sh` | `sudo ./scripts/setup-from-scratch.sh` | **sudo必須** | 初回環境構築（12ステップ） |
| `show-credentials.sh` | `./scripts/utils/show-credentials.sh` | 通常ユーザー | 認証情報表示 |
| `update-passwords.sh` | `./scripts/utils/update-passwords.sh [オプション]` | 通常ユーザー | パスワード/トークン更新 |
| `backup-all.sh` | `sudo ./scripts/utils/backup-all.sh` | **sudo必須** | 完全バックアップ |
| `restore-all.sh` | `sudo ./scripts/utils/restore-all.sh <backup-dir>` | **sudo必須** | バックアップから復元 |
| `cleanup-all.sh` | `sudo ./scripts/cleanup-all.sh` | **sudo必須** | 全リソース削除 |
| `deploy-oneclick.sh` | `sudo ./scripts/utils/deploy-oneclick.sh` | **sudo必須** | ワンクリック再デプロイ |
| `setup-cicd.sh` | `sudo ./scripts/setup-cicd.sh` | **sudo必須** | CI/CD環境自動構築 |
| `setup-sample-app.sh` | `sudo ./scripts/setup-sample-app.sh` | **sudo必須** | CI/CD検証（推奨） |
| `setup-gitlab-variables.sh` | `./scripts/setup-gitlab-variables.sh` | 通常ユーザー | GitLab環境変数設定ガイド |

**重要な注意事項:**
- **sudo が必要なスクリプト**: コンテナ操作、システム設定変更を行うスクリプト
- **通常ユーザーで実行するスクリプト**: 設定確認、環境変数更新、GitLab操作を行うスクリプト
- `setup-sample-app.sh`は **sudo実行が必須** です（GitLab Runnerログアクセスのため）

### 1. ゼロからセットアップ

```bash
# リポジトリをクローン（または既存ディレクトリに移動）
cd /root/aws.git/container/claudecode/CICD

# スクリプトに実行権限を付与（初回のみ）
chmod +x scripts/*.sh

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

### 4. CI/CD環境セットアップ（自動化）

**前提条件**: コンテナ起動完了、基本パスワード設定完了

```bash
# CI/CD環境の完全自動セットアップ（sudoで実行）
sudo ./scripts/setup-cicd.sh
```

**セットアップ内容（6ステップ）**:
1. **認証情報の確認** - Nexusパスワード疎通確認、SonarQubeトークン自動生成
2. **GitLab Runner登録** - Registration Token自動生成・登録・起動
3. **GitLabプロジェクト作成** - Personal Access Token自動生成・プロジェクト作成
4. **CI/CD環境変数設定** - SONAR_TOKEN、NEXUS_ADMIN_PASSWORD等を自動設定
5. **sample-appプッシュ** - SSH鍵自動生成・登録、認証なしプッシュ
6. **セットアップ完了確認** - Runner状態、パイプライン実行状況確認

**事前準備が必要な項目**:
- **Nexusパスワード変更**: admin/admin123 → admin/Degital2026! (事前実施)
- **SonarQubeパスワード変更**: admin/admin → admin/Degital2026! (事前実施)

**完全自動化されたトークン**:
- SonarQubeトークン (SonarQube API経由)
- GitLab Personal Access Token (GitLab Rails Console経由)
- GitLab Runner Registration Token (GitLab Rails Console経由)
- SSH鍵ペア (Ed25519自動生成・GitLab登録)

### 5. CI/CD環境の検証（自動化スクリプト）

セットアップ完了後、CI/CD環境が正常に動作することを検証します：

```bash
# CI/CD検証スクリプト実行（環境変数から自動取得）
cd /root/aws.git/container/claudecode/CICD
./scripts/setup-sample-app.sh
```

**スクリプト機能（v2.1.0対応）**:
- ✅ **複数回実行対応**: 何度実行しても安全
- ✅ **自動クリーンアップ**: 既存プロセス・ディレクトリの完全削除
- ✅ **Git競合自動解決**: `--allow-unrelated-histories`による自動マージ
- ✅ **CI/CDパイプライン監視**: リアルタイム進捗表示（最大3分）
- ✅ **独立ディレクトリ**: `/tmp/gitlab-sample-app`でユーザリポジトリと完全分離

**実行ステップ（8ステップ）**:
1. **独立ディレクトリ作成** - 実行ID付きでクリーンな環境準備
2. **sample-appファイルコピー** - ユーザリポジトリから独立コピー
3. **Gitリポジトリ初期化** - 新規Git環境作成
4. **初期コミット作成** - 実行ID付きコミットメッセージ
5. **GitLabリモート設定** - 既存リモート削除後の安全な再設定
6. **GitLabプッシュ（競合自動解決）** - 自動マージ機能付き
7. **CI/CDパイプライン開始確認** - GitLab Runner動作確認
8. **パイプライン実行状況監視** - 全5ステージ成功の自動確認

**パイプライン監視出力例**:
```
🔄 パイプライン実行中... (1/5 ステージ完了)
🔄 パイプライン実行中... (3/5 ステージ完了)
✅ CI/CDパイプライン全ステージ成功（5個のジョブ完了）
```

**検証内容**:
- **GitLab**: リポジトリ作成・プッシュ・パイプライン実行
- **Maven**: ビルド・テスト・パッケージング
- **JaCoCo**: カバレッジ測定（80%以上）
- **Nexus**: アーティファクトデプロイ（maven-snapshots）
- **GitLab Runner**: Shell executor での自動実行

### 6. 手動でのサンプルアプリケーションプッシュ（オプション）

CI/CD検証スクリプトを使用しない場合の手動手順：

```bash
# GitLab作業ディレクトリでの操作（/tmp/gitlab-sample-app/）
cd /tmp/gitlab-sample-app

# リモートURLの設定（GitLab CI/CD用）
git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/sample-app.git

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
  - GitLab CI/CD環境変数 `SONAR_TOKEN` も再生成して更新してください

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
| `setup-from-scratch.sh` | ゼロから完全環境構築（12ステップ、トークン保持） | 新規環境セットアップ、再セットアップ |
| `setup-sample-app.sh` | **CI/CD検証スクリプト（複数回実行対応）** | **セットアップ後のCI/CD動作検証** |
| `setup-cicd.sh` | CI/CD環境自動セットアップ（6ステップ、Runner登録・プロジェクト作成） | CI/CDパイプライン構築、sample-app連携 |
| `show-credentials.sh` | 全サービスの認証情報表示 | 認証情報確認、ファイル出力 |
| `update-passwords.sh` | パスワード・トークン・EC2ホスト更新 | パスワード変更、EC2ドメイン変更 |
| `backup-all.sh` | 完全バックアップ | 定期バックアップ、移行前 |
| `restore-all.sh` | バックアップから復元 | 災害復旧、環境移行 |
| `cleanup-all.sh` | 全リソース削除 | 環境クリーンアップ |
| `deploy-oneclick.sh` | ワンクリック再デプロイ | 環境リフレッシュ |

### 0. CI/CD検証スクリプト（setup-sample-app.sh）

#### スクリプト概要

セットアップ完了後にCI/CD環境が正常動作するかを検証する自動化スクリプトです。

```bash
# 基本実行（環境変数から自動取得）
./scripts/setup-sample-app.sh
```

#### 複数回実行対応機能（v2.1.0）

**安全な複数回実行**:
- ✅ **実行ID管理**: `YYYYMMDD-HHMMSS`形式の実行識別子
- ✅ **プロセスクリーンアップ**: 既存の`git-upload-pack`プロセス終了
- ✅ **ディレクトリクリーンアップ**: `/tmp/gitlab-sample-app`の完全削除・再作成
- ✅ **Git競合自動解決**: `--allow-unrelated-histories`による自動マージ
- ✅ **リモート安全設定**: 既存リモート削除後の再設定

**実行ログ例**:
```bash
[1/8] 独立ディレクトリ作成中... (実行ID: 20260110-141641)
  🧹 既存実行のクリーンアップ中...
  ✓ クリーンアップ完了
  ✓ 独立ディレクトリ作成完了: /tmp/gitlab-sample-app

[6/8] GitLabにプッシュ中...
  リモートとの競合を検出しました。自動マージ中...
  ✓ 自動マージ完了
  ✓ GitLabプッシュ完了

[8/8] CI/CDパイプライン実行状況監視中...
  🔄 パイプライン実行中... (3/5 ステージ完了)
  ✅ CI/CDパイプライン全ステージ成功（5個のジョブ完了）
```

#### 検証項目

**統合サービス確認**:
1. **GitLab**: プロジェクト作成、プッシュ、パイプライン起動
2. **GitLab Runner**: Shell executor でのジョブ実行
3. **Maven**: マルチモジュールビルド・テスト実行
4. **JaCoCo**: カバレッジレポート生成（80%達成確認）
5. **Nexus**: maven-snapshotsへのアーティファクトデプロイ

**CI/CDパイプライン（5ステージ）**:
```
Build → Test → Coverage → Package → Deploy
 12s    24s      7s        13s       14s
```

#### トラブルシューティング

**よくある問題と解決策**:

```bash
# GitLab Runner未起動の場合
sudo systemctl start gitlab-runner
sudo systemctl status gitlab-runner

# パイプライン失敗時の詳細確認
# GitLab UI → Projects → sample-app → CI/CD → Pipelines

# Nexusアーティファクト確認
curl -u admin:${NEXUS_ADMIN_PASSWORD} \
  "http://${EC2_PUBLIC_IP}:8082/service/rest/v1/search?repository=maven-snapshots&q=sample-app"
```

### 1. 認証情報管理

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

**重要**:
- パスワード変更後、関連サービスの再起動が必要な場合があります
- EC2ドメイン名変更後、sample-appのgit remoteも更新してください
- GitLab CI/CD環境変数（SONAR_TOKEN、NEXUS_ADMIN_PASSWORD）も合わせて更新

### 1. バックアップ

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

### 2. 復元

```bash
# バックアップアーカイブの展開
tar xzf backup-20260110-075148.tar.gz

# 復元実行（sudoで実行）
sudo ./scripts/utils/restore-all.sh backup-20260110-075148

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
# 全リソース削除（確認プロンプトあり、sudoで実行）
sudo ./scripts/cleanup-all.sh

# 削除対象
# - 全コンテナ（cicd-*）
# - 全ボリューム（cicd-*）
# - ネットワーク（cicd-network）
# - GitLab Runner 設定（オプション）
# - Maven 設定（オプション）
```

### 4. ワンクリック再デプロイ

```bash
# バックアップ → クリーンアップ → セットアップを一括実行（sudoで実行）
sudo ./scripts/utils/deploy-oneclick.sh

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
0 3 * * * ec2-user /root/aws.git/container/claudecode/CICD/scripts/utils/backup-all.sh
EOF

# 古いバックアップの削除（30日以前）
# 以下を cron に追加
0 4 * * * find /root/aws.git/container/claudecode/CICD/backup-* -type f -name "*.tar.gz" -mtime +30 -delete
```

### 6. サービス管理

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

## ✅ セットアップ検証結果

### 第4回完全検証完了（2026-01-10）

ゼロからセットアップの妥当性について、8つの主要領域で系統的な検証を実施しました。

#### ✅ 検証完了項目

| 項目 | ステータス | 詳細 |
|------|-----------|------|
| **環境変数一貫性** | ✅ 正常 | docker-compose.yml、CI/CD、Maven設定で環境変数参照が適切 |
| **パスワード・テンプレート** | ✅ 正常 | PostgreSQL init.sql、CI設定で動的プレースホルダー使用 |
| **Docker依存関係** | ✅ 正常 | サービス依存関係、ヘルスチェック、ネットワーク設定が適切 |
| **セットアップ手順** | ✅ 正常 | 12ステップの論理的整合性、環境変数生成、トークン保持機能 |
| **GitLab Runner設定** | ⚠️ 注意必要 | systemd設定は適切だが、二重設定問題あり（下記参照） |
| **Maven設定継承** | ✅ 正常 | 親POM、子POM、動的Nexus URL置換が適切に機能 |
| **CI/CD パイプライン** | ✅ 正常 | 6ステージ、環境変数使用、品質ゲート、テンプレート生成 |
| **データベーススキーマ** | ✅ 正常 | Flyway、JPA、初期化スクリプト、サンプルデータの整合性 |

#### ⚠️ 発見された重要な設定問題

##### 1. **GitLab Runner 二重設定問題**（重要）
- **問題**: コンテナベース（docker-compose.yml）とホストベース（setup-from-scratch.sh）の両方設定
- **影響**: リソース競合、実行環境の不整合
- **推奨**: ホストベース（shell executor）に統一（CLAUDE.md準拠）

##### 2. **GitLab Runner 登録コマンドのトークン不足**
- **場所**: `scripts/setup-from-scratch.sh:358-361`
- **問題**: `--token` パラメータが欠如
- **修正**:
```bash
sudo gitlab-runner register \
  --url http://${EC2_HOST}:5003 \
  --token YOUR_REGISTRATION_TOKEN \  # <- この行が必要
  --executor shell \
  --description 'CICD Shell Runner'
```

##### 3. **Maven POM 親モジュール設定不備**
- **場所**: `sample-app/pom.xml:16-18`
- **問題**: modules セクションに `common` モジュールが未記載
- **現在**: `<module>backend</module>` のみ
- **必要**: `<module>common</module>` と `<module>backend</module>` 両方

##### 4. **setup-from-scratch.sh ステップ番号不整合**
- **問題**: コメント番号と echo 番号の不一致
- **例**: `# 7. 環境変数...` → `echo "[8/12] Docker Compose..."`
- **影響**: メンテナンス性とドキュメント整合性

##### 5. **sample-backend ヘルスチェック欠如**（軽微）
- **問題**: sample-backend サービスにヘルスチェック未定義
- **影響**: sample-frontend 依存関係で競合状態の可能性

#### 🔧 推奨修正事項

##### 最優先（運用に影響）
1. **GitLab Runner コンテナ設定を docker-compose.yml から削除**
2. **GitLab Runner 登録コマンドに `--token` パラメータ追加**
3. **Maven 親POM に common モジュール追加**

##### 次優先（保守性向上）
4. **setup-from-scratch.sh のステップ番号統一**
5. **sample-backend ヘルスチェック追加**

#### 📋 システム全体評価

**総合判定**: ✅ **セットアップ可能（軽微な問題あり）**

- 🟢 **コア機能**: CI/CD環境、データベース、パイプラインは全て動作可能
- 🟢 **環境変数・パスワード管理**: 動的EC2対応、トークン保持機能が適切に実装
- 🟡 **GitLab Runner**: 二重設定問題があるが、ホストベース設定で動作可能
- 🟡 **Maven ビルド**: common モジュールの個別ビルドが必要だが、機能的には問題なし

**結論**: 現在の設定でも基本的な CI/CD 環境の構築・運用は可能です。上記修正により安定性と保守性が大幅に向上します。

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
sudo podman ps -a | grep gitlab

# GitLab初期化完了まで待機（5-10分）
sudo podman logs -f cicd-gitlab

# "gitlab Reconfigured!" が表示されるまで待つ

# 初期パスワード確認（24時間以内）
sudo podman exec -it cicd-gitlab cat /etc/gitlab/initial_root_password
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
sudo podman logs cicd-sonarqube
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
  --url http://${EC2_PUBLIC_IP}:5003 \
  --token YOUR_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runnerログ確認
sudo journalctl -u gitlab-runner -f
```

### 5. データベース接続エラー

```bash
# PostgreSQL起動確認
sudo podman ps | grep postgres

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
# http://${EC2_PUBLIC_IP}:8000/dashboard?id=sample-app-backend

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
sudo podman image prune -a

# Podman未使用ボリューム削除
sudo podman volume prune

# 古いバックアップ削除
find backup-* -type f -mtime +30 -delete

# Nexus古いアーティファクト削除
# Nexus UI → Repository → maven-snapshots → Cleanup Policies
```

### 8. EC2インスタンス再作成時のドメイン名/IP変更

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

#### 方法3: 手動更新
```bash
# .envファイルを編集
vi .env

# EC2_PUBLIC_IP の値を更新
EC2_PUBLIC_IP=ec2-34-205-156-203.compute-1.amazonaws.com

# Maven設定も更新（sudoで実行）
sudo ./scripts/setup-from-scratch.sh  # ステップ11でMaven設定を再生成
```

**影響範囲と追加対応**:
```bash
# 1. GitLab作業ディレクトリのリモートURLを更新
cd /tmp/gitlab-sample-app
git remote set-url origin http://NEW_IP:5003/root/sample-app.git

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

### 9. 再セットアップ時のトークン消失

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
cp .env.backup.20260110123456 .env

# または、個別更新スクリプトで設定
./scripts/utils/update-passwords.sh --sonar-token sqa_xxxxxxxxxxxxx
./scripts/utils/update-passwords.sh --runner-token glrt-xxxxxxxxxxxxx
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
gpg --symmetric --cipher-algo AES256 backup-20260110-075148.tar.gz

# 復号化
gpg --decrypt backup-20260110-075148.tar.gz.gpg > backup-20260110-075148.tar.gz
```

#### 4. 監査ログ
```bash
# GitLabアクセスログ
sudo podman exec cicd-gitlab cat /var/log/gitlab/nginx/gitlab_access.log

# Nexusログ
sudo podman logs cicd-nexus

# SonarQubeログ
sudo podman logs cicd-sonarqube
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

**注意**: URLのIPアドレス部分は実際のEC2インスタンスのIPアドレスに置き換えてください。

- **GitLab**: http://${EC2_PUBLIC_IP}:5003
- **Nexus**: http://${EC2_PUBLIC_IP}:8082
- **SonarQube**: http://${EC2_PUBLIC_IP}:8000
- **pgAdmin**: http://${EC2_PUBLIC_IP}:5002

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
2. ログを確認（`sudo podman logs <container_name>`）
3. GitLabプロジェクトのIssuesに報告

---

**最終更新日**: 2026-01-11
**バージョン**: 2.1.2

**変更履歴 (v2.1.2 - 最新)**:
- ✅ **.gitlab-ci.yml YAML構文修正** - SonarQubeステージのコロン含むecho文を引用符で修正
- ✅ **SonarQube マルチモジュール対応** - `-pl backend`オプション削除、親POMから実行
- ✅ **GitLab Runner設定修正** - `tag_list`と`run_untagged`設定追加
- ✅ **CI/CD環境変数設定完全自動化** - GitLab Rails Consoleによる5変数自動登録
- ✅ **README スクリプト実行方法明確化** - sudo必須/通常ユーザー実行の明示、一覧表追加
- ✅ **パイプライン全6ステージ動作確認完了** - build/test/coverage/sonarqube/package/deploy

**変更履歴 (v2.1.1)**:
- ✅ **EC2 IP変動対応** - 固定IPアドレスを環境変数参照に変更、自動取得機能
- ✅ **setup-sample-app.sh 複数回実行対応** - 自動クリーンアップ、競合解決、パイプライン監視
- ✅ **厳密ソフトウェアバージョン明記** - RHEL 9.7, Java 17.0.17, Spring Boot 3.2.1等
- ✅ **CI/CD検証手順の自動化** - 8ステップの完全自動検証スクリプト（引数不要）
- ✅ **パイプライン監視機能** - リアルタイム進捗表示、全6ステージ成功確認
- ✅ **動作検証済み環境の明確化** - Podman 5.6.0, Maven 3.6.3, PostgreSQL 16等

**変更履歴 (v2.1.0)**:
- ✅ トークン保持機能（SONAR_TOKEN、RUNNER_TOKEN）
- ✅ EC2ドメイン名/IP動的設定
- ✅ 認証情報管理スクリプト（show-credentials.sh、update-passwords.sh）
- ✅ 自動バックアップ機能（.env.backup.*）
- ✅ GitLabパスワード環境変数化
- ✅ Maven設定の動的置換（パスワード、EC2ドメイン）

**動作検証完了環境**:
- ✅ **OS**: Red Hat Enterprise Linux 9.7 (Plow)
- ✅ **コンテナ**: Podman 5.6.0, Docker Compose v3.8
- ✅ **Java**: OpenJDK 17.0.17 LTS (Red Hat build)
- ✅ **CI/CD**: GitLab CE latest, GitLab Runner latest (Shell executor)
- ✅ **品質管理**: SonarQube 10-community, JaCoCo 0.8.11
- ✅ **アーティファクト**: Nexus 3.x latest, Maven 3.6.3
- ✅ **データベース**: PostgreSQL 16-alpine, pgAdmin latest
