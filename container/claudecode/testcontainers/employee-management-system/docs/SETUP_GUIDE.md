# 職員管理システム - セットアップガイド

PostgreSQLと包括的なテスト機能を備えたコンテナ化された職員管理システムの完全セットアップガイドです。

## 📋 前提条件

### システム要件
- **オペレーティングシステム**: Linux、macOS、またはWSL2対応のWindows
- **メモリ**: 最低4GB RAM、推奨8GB以上
- **ストレージ**: コンテナとデータ用に最低2GBの空き容量
- **ネットワーク**: コンテナイメージダウンロード用のインターネット接続

### 必要なソフトウェア

#### 1. コンテナランタイム
**オプションA: podman（推奨）**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y podman podman-compose

# CentOS/RHEL/Fedora
sudo dnf install -y podman podman-compose

# macOS with Homebrew
brew install podman podman-compose

# podman machineを起動 (macOS/Windows)
podman machine init
podman machine start
```

**オプションB: Docker（代替手段）**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Dockerサービスを開始
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # ユーザーをdockerグループに追加
```

#### 2. Java開発キット（オプション - ローカル開発用）
```bash
# Ubuntu/Debian
sudo apt-get install -y openjdk-21-jdk

# CentOS/RHEL/Fedora
sudo dnf install -y java-21-openjdk-devel

# macOS with Homebrew
brew install openjdk@21

# インストールを確認
java -version
```

#### 3. Maven（オプション - ローカル開発用）
```bash
# Ubuntu/Debian
sudo apt-get install -y maven

# CentOS/RHEL/Fedora
sudo dnf install -y maven

# macOS with Homebrew
brew install maven

# インストールを確認
mvn -version
```

## 🚀 インストール手順

### ステップ1: プロジェクトの取得

#### オプションA: リポジトリのクローン
```bash
git clone https://github.com/shiftrepo/aws.git
cd aws/container/claudecode/testcontainers/employee-management-system
```

#### オプションB: アーカイブのダウンロード
```bash
# プロジェクトアーカイブをダウンロードして展開
wget https://github.com/shiftrepo/aws/archive/main.zip
unzip main.zip
cd aws-main/container/claudecode/testcontainers/employee-management-system
```

### ステップ2: 環境設定

#### 環境ファイルの作成
```bash
# 既存の.envファイルを確認
cat .env

# 必要に応じて環境変数を編集
nano .env
```

#### デフォルト環境変数
```env
# データベース設定
DB_HOST=postgres
DB_PORT=5432
DB_NAME=employee_db
DB_USERNAME=postgres
DB_PASSWORD=password

# pgAdmin設定
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin

# アプリケーション設定
SPRING_PROFILES_ACTIVE=dev
SERVER_PORT=8080
```

### ステップ3: コンテナのセットアップ

#### サービスのビルドと開始
```bash
# すべてのコンテナをプルしてビルド
podman-compose build

# すべてのサービスをデタッチモードで開始
podman-compose up -d

# 代替方法: ライブログ付きで開始
podman-compose up
```

#### サービスが実行中であることを確認
```bash
# サービス状態を確認
podman-compose ps

# 期待される出力:
# NAME                  COMMAND                  SERVICE             STATUS
# employee_postgres     "docker-entrypoint.s…"   postgres            Up
# employee_pgladmin      "/entrypoint.sh"         pgladmin             Up
# employee_app          "tail -f /dev/null"      app                 Up
```

#### サービスの稼働状態確認
```bash
# PostgreSQL接続をテスト
podman-compose exec postgres pg_isready -U postgres

# アプリケーションコンテナをテスト
podman-compose exec app java -version

# サービスログを表示
podman-compose logs postgres
podman-compose logs pgadmin
podman-compose logs app
```

## 🔧 設定オプション

### データベース設定

#### データベース設定のカスタマイズ
```yaml
# podman-compose.yml内で
services:
  postgres:
    environment:
      POSTGRES_DB: カスタムデータベース名
      POSTGRES_USER: ユーザー名
      POSTGRES_PASSWORD: セキュアなパスワード
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
```

#### 永続データストレージ
```yaml
# データの永続化を保証
volumes:
  postgres_data:
    driver: local
  pgadmin_data:
    driver: local
```

### アプリケーション設定

#### 開発プロファイル
```yaml
# src/main/resources/application-dev.yml
spring:
  jpa:
    hibernate:
      ddl-auto: update  # スキーマの自動作成/更新
    show-sql: true      # SQLクエリをログに表示

logging:
  level:
    com.example.employee: DEBUG
    org.hibernate.SQL: DEBUG
```

#### 本番プロファイル
```yaml
# src/main/resources/application-prod.yml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # スキーマの検証のみ
    show-sql: false

logging:
  level:
    com.example.employee: INFO
```

## 🌐 サービスへのアクセス

### Web インターフェース

#### pgAdmin データベースマネージャー
- **URL**: http://localhost:5050
- **Email**: admin@example.com
- **Password**: admin

**初期セットアップ**:
1. pgAdminにログイン
2. PostgreSQLサーバーが自動的に設定されているはずです
3. 設定されていない場合は、以下の情報でサーバーを追加:
   - **Host**: postgres
   - **Port**: 5432
   - **Database**: employee_db
   - **Username**: postgres
   - **Password**: password

#### アプリケーション API
- **Base URL**: http://localhost:8080/api/v1
- **ヘルスチェック**: http://localhost:8080/actuator/health
- **API ドキュメント**: http://localhost:8080/swagger-ui.html（有効な場合）

### データベースへの直接アクセス

#### コマンドラインアクセス
```bash
# PostgreSQLに直接接続
podman-compose exec postgres psql -U postgres -d employee_db

# SQLコマンドの実行
\dt                    # テーブル一覧
\d employees          # employeesテーブルの詳細
SELECT COUNT(*) FROM employees;
```

#### 外部データベースツール
- **Host**: localhost
- **Port**: 5432
- **Database**: employee_db
- **Username**: postgres
- **Password**: password

## 🧪 テスト環境セットアップ

### テスト環境設定

#### 初期テストの実行
```bash
# アプリケーションをビルド
podman-compose exec app mvn clean compile

# すべてのテストを実行
podman-compose exec app mvn test

# 特定のテストカテゴリを実行
podman-compose exec app mvn test -Dtest="*Repository*"
podman-compose exec app mvn test -Dtest="*Service*"
podman-compose exec app mvn test -Dtest="*Controller*"
```

#### テストデータ設定
```bash
# 異なるデータプロファイルでテスト
podman-compose exec app mvn test -Dtestdata.profile=basic
podman-compose exec app mvn test -Dtestdata.profile=medium
podman-compose exec app mvn test -Dtestdata.profile=large
```

### カバレッジレポート
```bash
# テストカバレッジレポートを生成
podman-compose exec app mvn test jacoco:report

# レポートをローカルマシンにコピー
podman cp $(podman-compose ps -q app):/workspace/target/site/jacoco ./coverage-report
```

## 🛠️ 開発ワークフロー

### ローカル開発環境セットアップ

#### IDE統合
```bash
# IntelliJ IDEAまたはEclipse用
# Mavenプロジェクトとしてインポート
# Java SDKを21+に設定
# データベース接続を設定:
# URL: jdbc:postgresql://localhost:5432/employee_db
# Username: postgres
# Password: password
```

#### ホットリロード開発
```bash
# devプロファイルでアプリケーションを開始
podman-compose exec app mvn spring-boot:run -Dspring-boot.run.profiles=dev

# または開発用オーバーライドを使用
podman-compose -f podman-compose.yml -f podman-compose.dev.yml up
```

### コード変更ワークフロー
```bash
# 1. IDEでコードを変更
# 2. 変更をテスト
podman-compose exec app mvn clean test

# 3. アプリケーションをビルド
podman-compose exec app mvn clean package

# 4. アプリケーションを再起動（必要に応じて）
podman-compose restart app
```

## 🔍 トラブルシューティング

### よくあるセットアップ問題

#### ポート競合
```bash
# ポートを使用しているプロセスを確認
sudo netstat -tulpn | grep :8080
sudo netstat -tulpn | grep :5432
sudo netstat -tulpn | grep :5050

# 必要に応じてpodman-compose.ymlでポートを変更
```

#### コンテナビルド問題
```bash
# クリーンアップして再ビルド
podman-compose down
podman system prune -f
podman-compose build --no-cache
podman-compose up -d
```

#### データベース接続問題
```bash
# PostgreSQLログを確認
podman-compose logs postgres

# データベースが接続を受け付けているかを確認
podman-compose exec postgres pg_isready -U postgres -d employee_db

# データベースをリセット（警告: データが削除されます）
podman-compose down -v
podman volume prune -f
podman-compose up -d
```

#### メモリ問題
```bash
# podman-compose.ymlでコンテナメモリ制限を増加
services:
  postgres:
    mem_limit: 1g
  app:
    mem_limit: 2g

# またはシステムリソースを調整
podman system info | grep -E "Memory|CPUs"
```

### パフォーマンス最適化

#### データベースパフォーマンス
```bash
# データベースパフォーマンスを監視
podman-compose exec postgres psql -U postgres -d employee_db \
  -c "SELECT * FROM pg_stat_activity;"

# クエリパフォーマンスを分析
podman-compose exec postgres psql -U postgres -d employee_db \
  -c "EXPLAIN ANALYZE SELECT * FROM employees JOIN departments ON employees.department_id = departments.id;"
```

#### アプリケーションパフォーマンス
```bash
# JVMメモリ使用量を監視
podman-compose exec app jps -v

# JVM監視を有効化（podman-compose.ymlに追加）
environment:
  - JAVA_OPTS=-XX:+UnlockExperimentalVMOptions -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0
```

## 🔄 メンテナンス

### 定期メンテナンスタスク

#### コンテナイメージの更新
```bash
# 最新イメージをプル
podman-compose pull

# 再ビルドして再起動
podman-compose down
podman-compose up -d --build
```

#### データベースバックアップ
```bash
# データベースバックアップを作成
podman-compose exec postgres pg_dump -U postgres employee_db > backup.sql

# バックアップから復元
podman-compose exec -T postgres psql -U postgres employee_db < backup.sql
```

#### リソースのクリーンアップ
```bash
# 未使用のコンテナとイメージを削除
podman system prune -a

# 未使用のボリュームを削除（警告: データが削除されます）
podman volume prune -f
```

### 監視とログ

#### ログの表示
```bash
# すべてのログを追跡
podman-compose logs -f

# 特定のサービスログを表示
podman-compose logs -f postgres
podman-compose logs -f app

# 最後のN行を表示
podman-compose logs --tail=50 app
```

#### システム監視
```bash
# コンテナリソース使用量を確認
podman stats $(podman-compose ps -q)

# システムディスク使用量を確認
df -h
```

## 📞 サポート

### ヘルプの取得

#### サポート用ログ収集
```bash
# システム情報を収集
./scripts/collect-debug-info.sh

# または手動で:
podman-compose ps > debug-info.txt
podman-compose logs >> debug-info.txt
podman system info >> debug-info.txt
```

#### よくあるサポートシナリオ
1. **アプリケーションが起動しない**: ログを確認し、すべてのサービスが実行中であることを検証
2. **データベース接続問題**: PostgreSQLサービスの稼働状態を確認
3. **テスト失敗**: テストデータベースが適切に初期化されていることを確認
4. **パフォーマンス問題**: リソース使用量を監視し、設定を最適化

---

**次のステップ**: セットアップが正常に完了したら、[テストガイド](TESTING_GUIDE.md)に進んで包括的なテスト戦略について学習してください。