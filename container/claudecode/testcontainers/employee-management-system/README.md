# 職員管理システム

Spring BootとPostgreSQLデータベース統合による包括的なコンテナ化職員管理システムです。広範囲なテスト戦略を実演しています。

## 🚀 クイックスタート

```bash
# 完全な環境を起動
podman-compose up -d

# サービスが実行中であることを確認
podman-compose ps

# アプリケーションにアクセス
curl http://localhost:8080/api/v1/employees
```

## 📋 概要

このプロジェクトは、**包括的データベーステスト教育**を目的とした完全な職員・部署管理システムを実装しています。以下を実演します：

- **コンテナ化開発環境**: PostgreSQL + pgAdmin + Java開発コンテナ
- **三階層テスト戦略**: Repository → Service → Controller テストレベル
- **保守可能テストデータ**: コード変更不要で修正可能なYAMLベーステストデータ
- **実世界シナリオ**: 複雑クエリ、トランザクション、ビジネスロジックテスト

## 🏗️ アーキテクチャ

### 技術スタック
- **バックエンド**: Spring Boot 3.x with Spring Data JPA
- **データベース**: PostgreSQL 15 with 全文検索機能
- **テスト**: JUnit 5 + TestContainers + 包括的テストユーティリティ
- **コンテナ管理**: 完全環境オーケストレーション用podman-compose
- **ビルドツール**: 統合テスト・カバレッジレポート付きMaven

### システムコンポーネント
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   REST API      │    │   Service Layer  │    │  Repository     │
│   Controllers   │◄──►│  Business Logic  │◄──►│  Data Access    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   PostgreSQL    │
                                                │    Database     │
                                                └─────────────────┘
```

## 🎯 テスト戦略

### 三階層テストアプローチ

#### 1. **Repository層テスト** (初級レベル)
- 基本CRUD操作のテスト
- JPAクエリメソッドの検証
- カスタムクエリの検証
- データベース制約のテスト

#### 2. **Service層テスト** (中級レベル)
- ビジネスロジックの検証
- トランザクション管理のテスト
- エラーハンドリングの検証
- モック統合テスト

#### 3. **Controller層テスト** (上級レベル)
- REST APIエンドポイントのテスト
- JSON シリアル化/デシリアル化
- HTTPステータスコードの検証
- 統合テストシナリオ

### テストデータ管理
- **YAMLベース設定**: コード変更不要でテストデータを修正
- **シナリオ固有データセット**: 異なるテストタイプ用の異なるデータセット
- **自動クリーンアップ**: テストが自動的にクリーンアップ
- **回帰テスト**: 結果をベースラインデータと比較

> 📚 **詳細ガイド**: テストプロファイル設定、TestContainersの使い方、カスタムテスト環境の作成方法については、[テストプロファイル・TestContainers詳細ガイド](docs/TEST_PROFILES_GUIDE.md)をご覧ください。

## 🛠️ セットアップとインストール

### 前提条件
- **podman** と **podman-compose** がインストール済み
- **Java 21+** (ローカル開発用)
- **Maven 3.6+** (ローカル開発用)

### 環境セットアップ

1. **クローンと移動**
   ```bash
   git clone <repository-url>
   cd employee-management-system
   ```

2. **全サービス開始**
   ```bash
   podman-compose up -d
   ```

3. **インストール検証**
   ```bash
   # 全サービスが実行中であることを確認
   podman-compose ps

   # データベース接続をテスト
   podman-compose exec postgres pg_isready -U postgres

   # pgAdminにアクセス (http://localhost:5050)
   # Email: admin@example.com, Password: admin
   ```

### サービスエンドポイント
- **アプリケーション**: http://localhost:8080
- **pgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432

## 🧪 テスト実行

### 基本テスト実行
```bash
# 全テスト
podman-compose exec app mvn test

# 特定のテストレベル
podman-compose exec app mvn test -Dtest="*Repository*"  # Repositoryテスト
podman-compose exec app mvn test -Dtest="*Service*"    # Serviceテスト
podman-compose exec app mvn test -Dtest="*Controller*" # Controllerテスト
```

### 高度なテストシナリオ
```bash
# 特定のデータプロファイルでテスト
podman-compose exec app mvn test -Dtestdata.profile=medium

# 回帰テストを実行
podman-compose exec app mvn test -Dtest.suite=regression

# カバレッジレポートを生成
podman-compose exec app mvn test jacoco:report
```

### テストデータプロファイル
- **`basic`**: 迅速テスト用最小データセット
- **`medium`**: 包括的テスト用中程度データセット
- **`large`**: パフォーマンステスト用大規模データセット
- **`integration`**: エンドツーエンドテスト用完全データセット

> 🔧 **プロファイル詳細**: 各プロファイルの詳細設定と新規プロファイル作成方法については、[TEST_PROFILES_GUIDE.md](docs/TEST_PROFILES_GUIDE.md#新しいテストプロファイルの追加方法)をご参照ください。

## 📊 データベーススキーマ

### コアエンティティ

#### 部署テーブル
```sql
CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    budget DECIMAL(12,2) NOT NULL,
    description VARCHAR(500),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0
);
```

#### 職員テーブル
```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hire_date DATE NOT NULL,
    phone_number VARCHAR(15),
    address VARCHAR(200),
    active BOOLEAN NOT NULL DEFAULT true,
    department_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT fk_employee_department FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## 🔧 開発ワークフロー

### 1. テストデータ修正
YAMLファイルを直接編集 - コード変更不要：
```bash
# テストデータを編集
vi src/test/resources/testdata/employees.yml
vi src/test/resources/testdata/departments.yml

# 新データでテストを実行
podman-compose exec app mvn test
```

### 2. 新規テスト追加
```bash
# 新しいテストクラスを作成
vi src/test/java/com/example/employee/repository/MyNewRepositoryTest.java

# 特定のテストを実行
podman-compose exec app mvn test -Dtest="MyNewRepositoryTest"
```

### 3. データベース検査
```bash
# データベースに直接接続
podman-compose exec postgres psql -U postgres -d employee_db

# またはpgAdmin Webインターフェースを使用
# http://localhost:5050
```

## 📚 APIドキュメント

### 部署API

#### GET /api/v1/departments
```bash
# 全部署を取得
curl http://localhost:8080/api/v1/departments

# アクティブ部署のみ取得
curl "http://localhost:8080/api/v1/departments?activeOnly=true"
```

#### POST /api/v1/departments
```bash
curl -X POST http://localhost:8080/api/v1/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新規部署",
    "code": "NEW",
    "budget": 1000000.00,
    "description": "新しい部署です"
  }'
```

### 職員API

#### GET /api/v1/employees
```bash
# 全職員を取得
curl http://localhost:8080/api/v1/employees

# 職員を検索
curl "http://localhost:8080/api/v1/employees/search?term=太郎"

# 部署別職員を取得
curl http://localhost:8080/api/v1/employees/department/1
```

#### POST /api/v1/employees
```bash
curl -X POST http://localhost:8080/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "新規",
    "lastName": "職員",
    "email": "new.employee@company.com",
    "hireDate": "2024-01-15",
    "departmentId": 1
  }'
```

> 📖 **API詳細**: 全APIエンドポイントの詳細説明と認証方法については、[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)をご覧ください。

## 🐛 トラブルシューティング

### よくある問題

#### データベース接続問題
```bash
# PostgreSQLが実行中かを確認
podman-compose ps postgres

# データベースログを確認
podman-compose logs postgres

# 接続を手動でテスト
podman-compose exec postgres pg_isready -U postgres
```

#### テスト失敗
```bash
# 詳細ログでテストを実行
podman-compose exec app mvn test -Dtest.log.level=DEBUG

# テストデータベース状態を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "\dt"
```

#### コンテナ問題
```bash
# 全サービスを再起動
podman-compose down && podman-compose up -d

# コンテナを再ビルド
podman-compose build --no-cache

# ボリュームをクリーン（警告：全データが削除されます）
podman-compose down -v
```

> 🔧 **詳細トラブルシューティング**: より詳細な問題解決方法については、[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)をご覧ください。

## 📈 パフォーマンス監視

### JaCoCoカバレッジレポート
```bash
# カバレッジレポートを生成
podman-compose exec app mvn test jacoco:report

# レポートを表示
open target/site/jacoco/index.html
```

### データベースパフォーマンス
```bash
# データベース統計を確認
podman-compose exec postgres psql -U postgres -d employee_db \
  -c "SELECT * FROM pg_stat_user_tables;"

# アクティブ接続を監視
podman-compose exec postgres psql -U postgres -d employee_db \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🤝 貢献方法

1. **リポジトリをフォーク**
2. **機能ブランチを作成**: `git checkout -b feature/amazing-feature`
3. **変更を加えてテストを追加**
4. **全テストが通ることを確認**: `podman-compose exec app mvn test`
5. **変更をコミット**: `git commit -m 'Add amazing feature'`
6. **ブランチにプッシュ**: `git push origin feature/amazing-feature`
7. **プルリクエストを開く**

### テストガイドライン
- 新機能は全三レベル（Repository、Service、Controller）のテストを含める必要があります
- テストデータは適切なYAMLファイルに追加してください
- テストの分離を維持 - テスト間の依存関係は避けてください
- テストメソッドの既存命名規則に従ってください

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 🙏 謝辞

- **Spring Bootチーム** - 優れたフレームワークに感謝
- **TestContainers** - シームレスな統合テストの実現に感謝
- **PostgreSQLコミュニティ** - 堅牢なデータベースプラットフォームに感謝
- **podmanコミュニティ** - コンテナオーケストレーション機能に感謝

## 📚 関連ドキュメント

| ドキュメント | 説明 |
|------------|------|
| [セットアップガイド](docs/SETUP_GUIDE.md) | 詳細な環境構築手順 |
| [テストガイド](docs/TESTING_GUIDE.md) | 包括的テスト戦略とテスト実行方法 |
| [テストプロファイル詳細ガイド](docs/TEST_PROFILES_GUIDE.md) | TestContainersとプロファイル設定の詳細解説 |
| [APIドキュメント](docs/API_DOCUMENTATION.md) | 全REST APIエンドポイントの詳細仕様 |
| [トラブルシューティング](docs/TROUBLESHOOTING.md) | 問題解決とデバッグガイド |

---

**包括的データベーステスト教育と実世界開発実践のために構築されました。**