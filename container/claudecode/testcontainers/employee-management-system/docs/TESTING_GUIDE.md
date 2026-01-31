# テストガイド - 職員管理システム

PostgreSQL統合による三階層データベーステストの包括的テスト戦略を実演します。

## 🎯 テスト哲学

このシステムは、データベーステスト戦略を学習するための**段階的複雑度テストアプローチ**を実装しています：

1. **Repository層（初級）**: データベースアクセスパターンとJPA機能
2. **Service層（中級）**: ビジネスロジック、トランザクション、エラーハンドリング
3. **Controller層（上級）**: REST API統合とエンドツーエンドシナリオ

## 🏗️ テストアーキテクチャ

### テスティングスタック
- **テストフレームワーク**: JUnit 5 with Spring Boot Test
- **データベース**: TestContainers with PostgreSQL
- **テストデータ**: YAMLベース設定（コード変更不要で編集可能）
- **カバレッジ**: JaCoCo with ベースライン比較
- **アサーション**: AssertJ for fluent assertions

### テストデータ管理
```yaml
# src/test/resources/testdata/employees.yml
employees:
  - firstName: "山田"
    lastName: "太郎"
    email: "yamada.taro@test.com"
    hireDate: "2023-01-15"
    departmentId: 1
```

**主要メリット**: YAMLファイルを編集してテストデータを変更 - コード変更不要！

## 🧪 テスト実行

### 基本テストコマンド

#### 全テスト実行
```bash
# 完全テストスイート
podman-compose exec app mvn test

# カバレッジレポート付き
podman-compose exec app mvn test jacoco:report
```

#### テストレベル別実行
```bash
# Repository層テスト（初級）
podman-compose exec app mvn test -Dtest="*Repository*"

# Service層テスト（中級）
podman-compose exec app mvn test -Dtest="*Service*"

# Controller層テスト（上級）
podman-compose exec app mvn test -Dtest="*Controller*"

# 統合テスト（上級）
podman-compose exec app mvn test -Dtest="*Integration*"
```

### テストデータプロファイル

#### 利用可能なプロファイル
```bash
# 基本データセット（職員5名、部署3つ）
podman-compose exec app mvn test -Dtestdata.profile=basic

# 中規模データセット（職員20名、部署5つ）
podman-compose exec app mvn test -Dtestdata.profile=medium

# 大規模データセット（職員100名以上、複数部署）
podman-compose exec app mvn test -Dtestdata.profile=large

# 統合データセット（リアルな関係性）
podman-compose exec app mvn test -Dtestdata.profile=integration
```

#### カスタムテストデータ
```bash
# カスタムCSVファイルを使用
podman-compose exec app mvn test -Dtestdata.source=csv -Dtestdata.file=my-data.csv

# テストデータの検証のみ
podman-compose exec app mvn test -Dtestdata.validate-only=true
```

## 📊 テストレベル詳細説明

### レベル1: Repository層テスト（初級）

**目的**: データベースアクセスパターンとJPAクエリテストを学習

#### 主要テストシナリオ
```java
@DataJpaTest
class EmployeeRepositoryTest {

    // 基本CRUD操作
    @Test
    void shouldSaveAndFindEmployee() {
        // 基本的な保存/検索操作のテスト
    }

    // クエリメソッドテスト
    @Test
    void shouldFindEmployeesByDepartment() {
        // 派生クエリメソッドのテスト
    }

    // カスタムクエリテスト
    @Test
    void shouldFindEmployeesWithComplexCriteria() {
        // @Queryアノテーションのテスト
    }
}
```

#### 学習内容
- JPAエンティティマッピングと関係性
- Repositoryクエリメソッドテスト
- データベース制約検証
- カスタムクエリ検証
- トランザクション境界

#### テスト例
```bash
# repositoryテストの実行
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest"
podman-compose exec app mvn test -Dtest="DepartmentRepositoryTest"
```

### レベル2: Service層テスト（中級）

**目的**: ビジネスロジック、トランザクション、サービス協調をテスト

#### 主要テストシナリオ
```java
@SpringBootTest
@Transactional
class EmployeeServiceTest {

    // ビジネスロジックテスト
    @Test
    void shouldCalculateEmployeeYearsOfService() {
        // ビジネス計算のテスト
    }

    // トランザクションテスト
    @Test
    @Rollback(false)
    void shouldHandleTransactionalOperations() {
        // トランザクション管理のテスト
    }

    // エラーハンドリング
    @Test
    void shouldThrowExceptionForInvalidData() {
        // エラーシナリオのテスト
    }
}
```

#### 学習内容
- ビジネスロジック検証
- トランザクション管理テスト
- エラーハンドリング戦略
- Service層のモッキング
- データ変換テスト

#### 高度なシナリオ
```bash
# モック依存関係を使ったテスト
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldHandleDepartmentTransfer"

# トランザクションロールバックテスト
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldRollbackOnError"
```

### レベル3: Controller層テスト（上級）

**目的**: REST APIエンドポイントとエンドツーエンド統合をテスト

#### 主要テストシナリオ
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class EmployeeControllerTest {

    // RESTエンドポイントテスト
    @Test
    void shouldCreateEmployeeViaRestAPI() {
        // JSONを使ったHTTP POSTのテスト
    }

    // 統合テスト
    @Test
    void shouldPerformCompleteEmployeeWorkflow() {
        // フルユーザーシナリオのテスト
    }

    // エラーレスポンステスト
    @Test
    void shouldReturn400ForInvalidData() {
        // エラーレスポンスのテスト
    }
}
```

#### 学習内容
- REST APIエンドポイントテスト
- JSONシリアル化/デシリアル化
- HTTPステータスコード検証
- エンドツーエンドワークフローテスト
- エラーレスポンスハンドリング

## 🎮 インタラクティブテストシナリオ

### シナリオ1: 基本職員管理
```bash
# 基本CRUD操作のテスト
podman-compose exec app mvn test -Dtest="*Repository*" -Dtestdata.profile=basic

# テスト結果の検査
cat target/surefire-reports/TEST-*.xml | grep -E "(testcase|failure)"
```

### シナリオ2: 部署異動
```bash
# 複雑なビジネスロジックのテスト
podman-compose exec app mvn test -Dtest="*Service*" -Dtestdata.profile=medium

# 詳細ログの表示
podman-compose exec app mvn test -Dtest="DepartmentServiceTest#shouldTransferAllEmployees" -X
```

### シナリオ3: API統合
```bash
# 完全なREST APIワークフローのテスト
podman-compose exec app mvn test -Dtest="*Controller*" -Dtestdata.profile=integration

# 特定のAPIエンドポイントテスト
podman-compose exec app mvn test -Dtest="EmployeeControllerTest#shouldSearchEmployees"
```

## 🔧 テストデータカスタマイズ

### テストデータファイルの編集

#### 職員テストデータ
```yaml
# src/test/resources/testdata/employees.yml
employees:
  - firstName: "佐藤"             # ← 直接編集
    lastName: "花子"              # ← コード変更不要
    email: "sato.hanako@company.com"  # ← YAMLを変更するだけ
    hireDate: "2024-01-15"        # ← 保存してテスト実行
    departmentId: 1
    active: true
```

#### 部署テストデータ
```yaml
# src/test/resources/testdata/departments.yml
departments:
  - name: "エンジニアリング部"       # ← 部署名を変更
    code: "ENG"                   # ← コードを変更
    budget: 2500000.00            # ← 予算を調整
    description: "ソフトウェア開発"
    active: true
```

### カスタムシナリオの作成
```yaml
# src/test/resources/testdata/scenarios/my-scenario.yml
departments:
  - name: "カスタム部署"
    code: "CUSTOM"
    budget: 1000000.00
    active: true

employees:
  - firstName: "テスト"
    lastName: "ユーザー"
    email: "test@example.com"
    hireDate: "2024-01-01"
    departmentId: 1
```

```bash
# カスタムシナリオで実行
podman-compose exec app mvn test -Dtestdata.profile=my-scenario
```

## 📈 カバレッジと品質メトリクス

### カバレッジレポートの生成
```bash
# カバレッジ付きテスト実行
podman-compose exec app mvn clean test jacoco:report

# レポートをホストにコピー（閲覧用）
podman cp $(podman-compose ps -q app):/workspace/target/site/jacoco ./coverage-report

# ブラウザで開く
open coverage-report/index.html
```

### カバレッジ目標
- **Repository層**: 95%以上のカバレッジ
- **Service層**: 90%以上のカバレッジ
- **Controller層**: 85%以上のカバレッジ
- **プロジェクト全体**: 90%以上のカバレッジ

### 品質ゲート
```bash
# 品質ゲート実行付きでテスト実行
podman-compose exec app mvn test -Dquality.gate=true

# カバレッジが目標値以下の場合、ビルドが失敗します
```

## 🎯 回帰テスト

### ベースライン比較
```bash
# ベースラインと比較してテスト実行
podman-compose exec app mvn test -Dregression.compare=true

# 新しいベースラインを生成（結果が正しいことを確認後）
podman-compose exec app mvn test -Dregression.update-baseline=true
```

### 自動回帰検出
```bash
# フル回帰テストスイートの実行
podman-compose exec app mvn test -Dtest.suite=regression

# パフォーマンス回帰のチェック
podman-compose exec app mvn test -Dtest.suite=performance
```

## 🐛 テストのデバッグ

### デバッグモード実行
```bash
# デバッグログ付きテスト実行
podman-compose exec app mvn test -X -Dtest.log.level=DEBUG

# SQLログ付きで特定テストを実行
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest" -DTEST_SHOW_SQL=true
```

### データベース状態の検査
```bash
# テスト実行中にテストデータベースに接続
podman-compose exec postgres psql -U postgres -d employee_db

# テストデータを表示
SELECT e.first_name, e.last_name, d.name as department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
```

### テスト失敗分析
```bash
# 詳細なテスト失敗レポート
cat target/surefire-reports/TEST-*.xml

# テスト実行タイムラインを表示
cat target/surefire-reports/*.txt | grep -E "(Test|FAILURE|ERROR)"
```

## 🎪 高度なテスト機能

### パフォーマンステスト
```bash
# パフォーマンステストスイートの実行
podman-compose exec app mvn test -Dtest="*Performance*" -Dtestdata.profile=large

# テスト中のデータベースパフォーマンス監視
podman-compose exec postgres psql -U postgres -d employee_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 並行テスト
```bash
# 並列テスト実行（高速実行）
podman-compose exec app mvn test -DforkCount=2 -DreuseForks=true

# 並行データベースアクセステスト
podman-compose exec app mvn test -Dtest="*Concurrent*"
```

### データマイグレーションテスト
```bash
# データベーススキーママイグレーションのテスト
podman-compose exec app mvn flyway:migrate
podman-compose exec app mvn test -Dtest="*Migration*"
```

## 📚 学習パス

### 初級トラック
1. Repository層テストから開始
2. JPAとデータベースマッピングを理解
3. クエリメソッドテストを学習
4. 基本テストデータで練習

```bash
# この順序で進行
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindByEmail"
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindActiveEmployees"
podman-compose exec app mvn test -Dtest="DepartmentRepositoryTest#shouldFindByCode"
```

### 中級トラック
1. Service層テストに移行
2. トランザクション管理を学習
3. ビジネスロジックテストを練習
4. エラーハンドリングを理解

```bash
# Service層の進行
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldCreateEmployee"
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldTransferEmployee"
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldHandleInvalidData"
```

### 上級トラック
1. Controller層テストをマスター
2. REST APIテストパターンを学習
3. 統合テストを練習
4. エンドツーエンドワークフローを理解

```bash
# 上級テストの進行
podman-compose exec app mvn test -Dtest="EmployeeControllerTest#shouldCreateEmployeeAPI"
podman-compose exec app mvn test -Dtest="EmployeeManagementIntegrationTest"
```

## 🔍 テストのトラブルシューティング

### よくあるテスト問題

#### テストデータ問題
```bash
# テストデータフォーマットの検証
podman-compose exec app mvn test -Dtestdata.validate-only=true

# テストデータの更新
podman-compose exec app mvn test -Dtestdata.refresh=true
```

#### データベース接続問題
```bash
# TestContainerデータベースステータスのチェック
podman-compose logs postgres

# テストデータベース接続の確認
podman-compose exec postgres pg_isready -U postgres
```

#### 不安定なテスト
```bash
# 不安定なテストを複数回実行
for i in {1..5}; do
  podman-compose exec app mvn test -Dtest="FlakyTest" || break
done

# テスト再試行を有効化
podman-compose exec app mvn test -Dsurefire.rerunFailingTestsCount=2
```

### パフォーマンス問題
```bash
# テスト実行のプロファイリング
podman-compose exec app mvn test -Dtest.profile=true

# TestContainer起動の最適化
export TESTCONTAINERS_REUSE_ENABLE=true
podman-compose exec app mvn test
```

## 📊 テストレポート

### 包括的レポートの生成
```bash
# 全テストレポート
podman-compose exec app mvn clean test site

# 個別レポート
podman-compose exec app mvn surefire-report:report      # テスト結果
podman-compose exec app mvn jacoco:report               # カバレッジ
podman-compose exec app mvn pmd:pmd                     # コード品質
```

### レポートの表示
```bash
# 全レポートをホストにコピー
podman cp $(podman-compose ps -q app):/workspace/target/site ./test-reports

# メインレポートを開く
open test-reports/index.html
```

---

**次のステップ**: テスト戦略をマスターした後は、[API ドキュメント](API_DOCUMENTATION.md)を探索して、テストされているRESTエンドポイントを理解してください。