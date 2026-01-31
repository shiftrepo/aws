# テストプロファイル・TestContainers詳細ガイド

## 🎯 このガイドについて

このガイドでは、職員管理システムにおけるテストプロファイルの管理方法とTestContainersの活用について、初学者でも理解できるよう詳しく解説します。

## 📖 基本概念の理解

### テストプロファイルとは？

**テストプロファイル**は、異なるテスト環境や条件でアプリケーションを実行するための設定の組み合わせです。

```
🏠 本番環境     ← production profile
🔧 開発環境     ← development profile
🧪 テスト環境   ← test profile
```

#### なぜテストプロファイルが必要？

1. **環境の分離**: 開発・テスト・本番で異なる設定を使用
2. **データ保護**: 本番データをテストで誤って変更することを防ぐ
3. **効率化**: テスト専用の軽量設定でテスト実行を高速化
4. **再現性**: 同じテスト条件を確実に再現

### TestContainersとは？

**TestContainers**は、テスト実行時に一時的にDockerコンテナを起動し、テスト終了後に自動で削除するライブラリです。

```
テスト開始 → コンテナ起動 → テスト実行 → コンテナ削除 → テスト終了
```

#### TestContainersの利点

✅ **本物のデータベース**: H2などの軽量DBではなく、本番と同じPostgreSQLでテスト
✅ **環境の一貫性**: 開発者全員が同じテスト環境を使用
✅ **自動クリーンアップ**: テスト終了後の環境掃除が自動化
✅ **隔離性**: 各テストが独立したコンテナで実行

## 🏗️ 現在のテストプロファイル構成

### プロファイル一覧

| プロファイル名 | 用途 | データベース | データ量 | 実行時間 |
|---------------|------|-------------|----------|----------|
| `test` | 基本テスト | H2 (メモリ) | 最小限 | 高速 |
| `integration` | 統合テスト | PostgreSQL | 中程度 | 中程度 |
| `performance` | パフォーマンステスト | PostgreSQL | 大量 | 低速 |

### 設定ファイルの場所

```
src/test/resources/
├── application-test.yml          # 基本テストプロファイル
├── application-integration.yml   # 統合テストプロファイル
├── application-performance.yml   # パフォーマンステストプロファイル
└── testdata/
    ├── test/                     # 基本テスト用データ
    ├── integration/              # 統合テスト用データ
    └── performance/              # パフォーマンステスト用データ
```

## 🔧 現在の設定詳細

### 基本テストプロファイル (`test`)

**ファイル**: `src/test/resources/application-test.yml`

```yaml
spring:
  profiles:
    active: test
  datasource:
    # H2インメモリデータベースを使用（高速）
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop  # テスト開始時にテーブル作成、終了時に削除
    show-sql: true          # SQLクエリをログ出力
  h2:
    console:
      enabled: true         # デバッグ用のH2コンソールを有効化

# テスト専用設定
test:
  data:
    profile: basic          # 基本的なテストデータを使用
    cleanup: true           # テスト後のデータクリーンアップを有効
  logging:
    level: DEBUG            # 詳細なログを出力
```

**特徴**:
- ⚡ **高速実行**: メモリ内データベースで最速
- 🧪 **単体テスト向け**: Repository層テストに最適
- 🔄 **自動クリーンアップ**: テスト間でデータが干渉しない

### 統合テストプロファイル (`integration`)

**ファイル**: `src/test/resources/application-integration.yml`

```yaml
spring:
  profiles:
    active: integration
  datasource:
    # TestContainersでPostgreSQLコンテナを起動
    url: jdbc:tc:postgresql:15:///testdb
    driver-class-name: org.testcontainers.jdbc.ContainerDatabaseDriver
    username: test
    password: test
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: false         # 統合テストでは不要なログを削減
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect

# TestContainers設定
testcontainers:
  reuse:
    enable: true           # コンテナの再利用で実行時間短縮
  containers:
    postgres:
      image: postgres:15   # 本番環境と同じバージョン
      init-script: init-integration.sql  # 初期データ投入スクリプト

# 統合テスト専用設定
test:
  data:
    profile: integration   # より豊富なテストデータ
    load-sample-data: true # サンプルデータの自動投入
  integration:
    timeout: 30s          # 統合テストのタイムアウト設定
```

**特徴**:
- 🐘 **本物のPostgreSQL**: 本番環境と同じデータベース
- 🔗 **統合テスト向け**: サービス間の連携をテスト
- 📊 **豊富なデータ**: 複雑なシナリオをテスト可能

### パフォーマンステストプロファイル (`performance`)

**ファイル**: `src/test/resources/application-performance.yml`

```yaml
spring:
  profiles:
    active: performance
  datasource:
    url: jdbc:tc:postgresql:15:///perfdb
    driver-class-name: org.testcontainers.jdbc.ContainerDatabaseDriver
    username: test
    password: test
    hikari:
      maximum-pool-size: 20      # 本番相当のコネクションプール
      minimum-idle: 10
  jpa:
    hibernate:
      ddl-auto: validate         # スキーマ検証のみ（パフォーマンス重視）
    show-sql: false
    properties:
      hibernate:
        generate_statistics: true # パフォーマンス統計を取得

# TestContainers設定（パフォーマンス最適化）
testcontainers:
  containers:
    postgres:
      image: postgres:15
      tmpfs:
        /var/lib/postgresql/data: rw,noexec,nosuid,size=1g  # tmpfsで高速化
      command: |
        postgres
        -c shared_buffers=256MB
        -c max_connections=100
        -c work_mem=4MB

# パフォーマンステスト専用設定
test:
  data:
    profile: performance
    size: large              # 大量データでテスト
  performance:
    warmup-iterations: 5     # JVMウォームアップ
    measurement-iterations: 10
    timeout: 300s           # 長時間実行を許可
```

**特徴**:
- 📈 **パフォーマンス測定**: 実際の負荷でテスト
- 🎯 **最適化設定**: 本番相当の設定でテスト
- 📊 **大量データ**: スケーラビリティをテスト

## 🛠️ TestContainersの実装詳細

### 基本的な使用方法

#### 1. 依存関係の追加 (`pom.xml`)

```xml
<dependencies>
    <!-- TestContainers Core -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers</artifactId>
        <version>1.19.3</version>
        <scope>test</scope>
    </dependency>

    <!-- PostgreSQL TestContainer -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <version>1.19.3</version>
        <scope>test</scope>
    </dependency>

    <!-- JUnit5 Integration -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>1.19.3</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

#### 2. テストクラスでの使用例

**Repository層テスト** (`src/test/java/.../EmployeeRepositoryTest.java`)

```java
@DataJpaTest
@Testcontainers  // TestContainers機能を有効化
class EmployeeRepositoryTest {

    // PostgreSQLコンテナを定義
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test")
            .withInitScript("test-schema.sql");  // 初期化スクリプト

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private EmployeeRepository employeeRepository;

    @DynamicPropertySource  // Spring設定を動的に更新
    static void configureProperties(DynamicPropertyRegistry registry) {
        // TestContainerから取得した接続情報をSpringに設定
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldFindEmployeesByDepartment() {
        // Given: テストデータを準備
        Department dept = new Department("Engineering", "ENG", new BigDecimal("1000000"));
        entityManager.persistAndFlush(dept);

        Employee emp = new Employee("太郎", "山田", "taro@example.com",
                                   LocalDate.of(2023, 1, 15), dept);
        entityManager.persistAndFlush(emp);

        // When: リポジトリメソッドを実行
        List<Employee> employees = employeeRepository.findByDepartment(dept);

        // Then: 結果を検証
        assertThat(employees)
            .hasSize(1)
            .extracting(Employee::getFirstName)
            .containsExactly("太郎");
    }
}
```

**統合テスト** (`src/test/java/.../EmployeeServiceIntegrationTest.java`)

```java
@SpringBootTest
@Testcontainers
@Transactional
class EmployeeServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("integration_test")
            .withUsername("test")
            .withPassword("test")
            // 複数の初期化スクリプトを順序実行
            .withInitScript("schema.sql")
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("testdata/integration/"),
                "/docker-entrypoint-initdb.d/"
            );

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        // TestContainers専用の設定も追加
        registry.add("testcontainers.reuse.enable", () -> "true");
    }

    @Autowired
    private EmployeeService employeeService;

    @Autowired
    private DepartmentService departmentService;

    @Test
    void shouldTransferEmployeeBetweenDepartments() {
        // Given: 部署とemployeeが既存データとして存在
        Long employeeId = 1L;  // 初期化スクリプトで作成済み
        Long newDepartmentId = 2L;  // 初期化スクリプトで作成済み

        // When: 部署異動を実行
        EmployeeDto transferredEmployee = employeeService.transferToDepartment(
            employeeId, newDepartmentId
        );

        // Then: 異動が正しく実行されたことを確認
        assertThat(transferredEmployee.getDepartmentId()).isEqualTo(newDepartmentId);

        // データベースに永続化されていることも確認
        Employee persistedEmployee = employeeService.findById(employeeId);
        assertThat(persistedEmployee.getDepartment().getId()).isEqualTo(newDepartmentId);
    }
}
```

### TestContainersの高度な設定

#### 共有TestContainerクラス

**`src/test/java/.../testconfig/SharedPostgreSQLContainer.java`**

```java
@TestConfiguration
public class SharedPostgreSQLContainer {

    private static final String IMAGE_VERSION = "postgres:15";

    @Bean
    @Primary
    @TestScope
    public PostgreSQLContainer<?> postgreSQLContainer() {
        PostgreSQLContainer<?> container = new PostgreSQLContainer<>(IMAGE_VERSION)
                .withDatabaseName("shared_test_db")
                .withUsername("test_user")
                .withPassword("test_pass")
                // ログレベルを設定
                .withLogConsumer(new Slf4jLogConsumer(LoggerFactory.getLogger("PostgreSQL")))
                // ヘルスチェックを設定
                .waitingFor(Wait.forLogMessage(".*database system is ready to accept connections.*", 1))
                // タイムアウトを設定
                .withStartupTimeout(Duration.ofMinutes(2))
                // 環境変数を追加
                .withEnv("POSTGRES_INITDB_ARGS", "--encoding=UTF-8 --locale=C")
                // カスタム設定ファイルをマウント
                .withFileSystemBind(
                    "src/test/resources/postgresql.conf",
                    "/etc/postgresql/postgresql.conf"
                );

        container.start();  // 明示的に開始
        return container;
    }

    @EventListener
    @Order(Ordered.HIGHEST_PRECEDENCE)
    public void onApplicationEvent(ContextClosedEvent event) {
        // アプリケーション終了時にコンテナも停止
        postgreSQLContainer().stop();
    }
}
```

#### カスタムTestProfile設定クラス

**`src/test/java/.../testconfig/TestProfileConfiguration.java`**

```java
@Configuration
public class TestProfileConfiguration {

    @Bean
    @Profile("integration")
    public TestDataLoader integrationTestDataLoader() {
        return new TestDataLoader("testdata/integration/");
    }

    @Bean
    @Profile("performance")
    public TestDataLoader performanceTestDataLoader() {
        return new TestDataLoader("testdata/performance/");
    }

    @Component
    @Profile("integration")
    static class IntegrationTestDataInitializer implements CommandLineRunner {

        @Autowired
        private TestDataLoader testDataLoader;

        @Override
        public void run(String... args) throws Exception {
            // 統合テスト用のサンプルデータを自動投入
            testDataLoader.loadEmployees("employees-integration.yml");
            testDataLoader.loadDepartments("departments-integration.yml");
        }
    }
}
```

## 📋 新しいテストプロファイルの追加方法

### ステップ1: 設定ファイルを作成

新しいプロファイル（例：`staging`）を追加する場合：

```bash
# 設定ファイルを作成
touch src/test/resources/application-staging.yml
```

**`application-staging.yml`の内容例**:

```yaml
spring:
  profiles:
    active: staging
  datasource:
    # 本番に近い環境でテスト
    url: jdbc:tc:postgresql:15:///staging_db?TC_TMPFS=/var/lib/postgresql/data:rw
    driver-class-name: org.testcontainers.jdbc.ContainerDatabaseDriver
    username: staging_user
    password: staging_pass
    hikari:
      maximum-pool-size: 15
      connection-timeout: 20000
  jpa:
    hibernate:
      ddl-auto: validate  # 本番相当の制約
    show-sql: false
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true

# TestContainers設定
testcontainers:
  reuse:
    enable: true
  containers:
    postgres:
      image: postgres:15
      init-scripts:
        - schema-staging.sql
        - data-staging.sql
      tmpfs:
        /var/lib/postgresql/data: rw,size=500m

# ステージング専用設定
test:
  data:
    profile: staging
    load-sample-data: true
    cleanup-after-test: false  # デバッグのためデータを残す
  staging:
    enable-monitoring: true    # メトリクス収集を有効化
    slow-query-threshold: 1000 # 1秒以上のクエリを警告
```

### ステップ2: テストデータを準備

```bash
# テストデータディレクトリを作成
mkdir -p src/test/resources/testdata/staging

# 初期化スクリプトを作成
touch src/test/resources/schema-staging.sql
touch src/test/resources/data-staging.sql
```

**`schema-staging.sql`の例**:

```sql
-- ステージング環境用のスキーマ初期化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 本番相当のインデックス
CREATE INDEX IF NOT EXISTS idx_employees_email_staging
    ON employees(email) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_employees_department_hire_date
    ON employees(department_id, hire_date);

-- 統計情報更新
ANALYZE employees;
ANALYZE departments;
```

**`data-staging.sql`の例**:

```sql
-- ステージング用サンプルデータ
INSERT INTO departments (name, code, budget, active) VALUES
    ('ステージング開発部', 'STG-DEV', 5000000.00, true),
    ('ステージング運用部', 'STG-OPS', 3000000.00, true),
    ('ステージング品質保証部', 'STG-QA', 2000000.00, true);

INSERT INTO employees (first_name, last_name, email, hire_date, department_id, active) VALUES
    ('太郎', 'ステージング', 'staging-taro@company.com', '2023-01-01', 1, true),
    ('花子', 'テスト', 'test-hanako@company.com', '2023-02-01', 2, true),
    ('次郎', 'サンプル', 'sample-jiro@company.com', '2023-03-01', 3, true);
```

### ステップ3: 専用テストクラスを作成

**`src/test/java/.../StagingIntegrationTest.java`**

```java
@SpringBootTest
@ActiveProfiles("staging")  // stagingプロファイルを有効化
@Testcontainers
@TestMethodOrder(OrderAnnotation.class)  // テスト実行順序を制御
class StagingIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("staging_test")
            .withUsername("staging_user")
            .withPassword("staging_pass")
            .withInitScript("schema-staging.sql")
            .withFileSystemBind(
                "src/test/resources/data-staging.sql",
                "/docker-entrypoint-initdb.d/data.sql"
            )
            // ステージング専用のコンテナ設定
            .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=500m"))
            .withCommand("postgres", "-c", "log_statement=all")  // 全クエリをログ出力
            .withLogConsumer(new Slf4jLogConsumer(LoggerFactory.getLogger("StagingPostgreSQL")));

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        // ステージング専用プロパティ
        registry.add("test.environment", () -> "staging");
        registry.add("logging.level.org.hibernate.SQL", () -> "DEBUG");
    }

    @Autowired
    private EmployeeService employeeService;

    @Test
    @Order(1)
    @DisplayName("ステージング環境でのemployee検索テスト")
    void shouldFindEmployeesInStagingEnvironment() {
        // ステージング特有のテストロジック
        List<EmployeeDto> employees = employeeService.findAllActiveEmployees();

        assertThat(employees)
            .hasSize(3)  // data-staging.sqlで投入した3名
            .extracting(EmployeeDto::getEmail)
            .allMatch(email -> email.contains("@company.com"));
    }

    @Test
    @Order(2)
    @DisplayName("ステージング環境でのパフォーマンステスト")
    void shouldPerformWellInStagingEnvironment() {
        // パフォーマンス測定
        StopWatch stopWatch = new StopWatch();
        stopWatch.start();

        // 重い処理を実行
        List<EmployeeDto> result = employeeService.searchEmployeesWithComplexCriteria(
            "ステージング", null, true
        );

        stopWatch.stop();

        // パフォーマンス検証
        assertThat(stopWatch.getTotalTimeMillis())
            .as("検索処理は1秒以内に完了する必要があります")
            .isLessThan(1000);

        assertThat(result).isNotEmpty();
    }
}
```

### ステップ4: プロファイル実行コマンドを追加

**Maven実行コマンドを追加**:

```bash
# stagingプロファイルでテスト実行
podman-compose exec app mvn test -Dspring.profiles.active=staging

# 特定のテストクラスのみ実行
podman-compose exec app mvn test -Dtest="StagingIntegrationTest" -Dspring.profiles.active=staging

# stagingプロファイル + 詳細ログ
podman-compose exec app mvn test -Dspring.profiles.active=staging -Dlogging.level.org.hibernate.SQL=DEBUG
```

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. TestContainerが起動しない

**症状**:
```
org.testcontainers.containers.ContainerLaunchException: Container startup failed
```

**診断**:
```bash
# Dockerデーモンが実行中かを確認
podman info

# TestContainerログを有効化
export TESTCONTAINERS_LOG_LEVEL=DEBUG
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest"
```

**解決方法**:
```java
// より具体的なエラー情報を取得
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withLogConsumer(new Slf4jLogConsumer(logger))
        .waitingFor(Wait.forLogMessage(".*ready to accept connections.*", 2))
        .withStartupTimeout(Duration.ofMinutes(3));  // タイムアウトを延長
```

#### 2. テストが遅い

**症状**:
テストの実行時間が長すぎる

**解決方法**:
```bash
# コンテナ再利用を有効化
export TESTCONTAINERS_REUSE_ENABLE=true

# または設定で有効化
echo "testcontainers.reuse.enable=true" >> ~/.testcontainers.properties
```

```java
// テストクラスレベルでコンテナを共有
@Testcontainers
class EmployeeRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withReuse(true);  // コンテナの再利用を明示的に有効化
}
```

#### 3. テストデータの競合

**症状**:
テスト間でデータが干渉して不正な結果になる

**解決方法**:
```java
@Transactional
@Rollback  // 各テスト後にロールバック
class EmployeeServiceTest {

    @BeforeEach
    void setUp() {
        // 各テスト前にデータをクリーンアップ
        employeeRepository.deleteAll();
        departmentRepository.deleteAll();
    }
}
```

#### 4. プロファイル設定が反映されない

**診断**:
```bash
# アクティブプロファイルを確認
podman-compose exec app mvn test -Dspring.profiles.active=integration -Ddebug

# 設定値を確認
podman-compose exec app mvn test -Dspring.profiles.active=integration \
    -Dlogging.level.org.springframework.core.env=DEBUG
```

**解決方法**:
```java
@ActiveProfiles({"integration", "testcontainers"})  // 複数プロファイルを指定
class IntegrationTest {

    @Test
    void shouldUseIntegrationProfile(@Value("${spring.profiles.active}") String activeProfile) {
        // プロファイルが正しく設定されているかを確認
        assertThat(activeProfile).contains("integration");
    }
}
```

## 📊 パフォーマンス最適化

### TestContainerの最適化設定

```java
@Container
static PostgreSQLContainer<?> optimizedPostgres = new PostgreSQLContainer<>("postgres:15")
        // tmpfsを使用してI/Oを高速化
        .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=1g"))
        // 必要最小限の設定でPostgreSQLを起動
        .withCommand(
            "postgres",
            "-c", "fsync=off",                    // 安全性よりも速度を重視
            "-c", "synchronous_commit=off",
            "-c", "checkpoint_segments=32",
            "-c", "checkpoint_completion_target=0.9",
            "-c", "wal_buffers=16MB",
            "-c", "shared_buffers=256MB"
        )
        // 不要なログを削減
        .withLogConsumer(new ToStringConsumer().withRemoveAnsiCodes(false))
        // ヘルスチェックを最小化
        .waitingFor(Wait.forLogMessage(".*ready to accept connections.*", 1))
        .withStartupTimeout(Duration.ofSeconds(60));
```

### プロファイル別実行時間の目安

| プロファイル | 想定実行時間 | 用途 | 推奨頻度 |
|-------------|------------|------|----------|
| `test` | 1-5分 | 単体テスト | 各コミット時 |
| `integration` | 5-15分 | 統合テスト | Pull Request時 |
| `performance` | 15-60分 | 負荷テスト | リリース前 |
| `staging` | 10-30分 | 受け入れテスト | デプロイ前 |

## 🎯 ベストプラクティス

### 1. テストプロファイルの命名規則

```
test            # 基本単体テスト（H2使用）
integration     # 統合テスト（TestContainers使用）
performance     # パフォーマンステスト
staging         # ステージング環境テスト
e2e            # エンドツーエンドテスト
contract       # 契約テスト
```

### 2. TestContainer設定の共通化

```java
// 共通設定を抽象クラスで定義
public abstract class BaseIntegrationTest {

    @Container
    protected static final PostgreSQLContainer<?> postgres =
        PostgreSQLContainerFactory.createOptimizedContainer();

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        PostgreSQLContainerFactory.configureSpringProperties(registry, postgres);
    }
}

// 各テストクラスで継承
class EmployeeServiceIntegrationTest extends BaseIntegrationTest {
    // テストロジックのみに集中
}
```

### 3. テストデータ管理の統一

```java
@Component
public class TestDataManager {

    public void loadTestDataForProfile(String profile) {
        switch (profile) {
            case "integration":
                loadIntegrationData();
                break;
            case "performance":
                loadPerformanceData();
                break;
            case "staging":
                loadStagingData();
                break;
        }
    }

    private void loadIntegrationData() {
        // integration用データ投入ロジック
    }
}
```

## 📚 学習リソース

### 公式ドキュメント
- [TestContainers Official Documentation](https://www.testcontainers.org/)
- [Spring Boot Testing Guide](https://spring.io/guides/gs/testing-web/)

### 参考記事
- TestContainers実践ガイド
- Spring Profilesの効果的な使い方
- 統合テスト戦略とベストプラクティス

---

このガイドを参考に、プロジェクトに最適なテストプロファイル構成を設計し、TestContainersを効果的に活用してください。質問がある場合は、[TROUBLESHOOTING.md](TROUBLESHOOTING.md)も合わせてご確認ください。