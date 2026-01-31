# テストプロファイル・TestContainers実践ガイド

## 🎯 このガイドについて

このガイドでは、職員管理システムにおける効率的なデータベーステスト戦略について、目的別に最適な手法を解説します。

## 📋 テスト戦略マトリクス

| 目的 | 推奨手段 | 適用場面 |
|------|----------|----------|
| **DBの初期化** | コンテナ再生成 / トランザクションロールバック | テスト環境のクリーンな状態確保 |
| **テストケース毎のデータ投入** | @Sql / Flyway / Liquibase | 特定テスト用データの準備 |
| **パターンデータの切替** | SQLファイル分離 / ParameterizedTest | 複数シナリオの効率的テスト |
| **大量パターン回帰** | JUnit5 ParameterizedTest | 組み合わせテストの自動化 |
| **DB状態検証** | AssertJ / Repository / DB直接クエリ | テスト結果の多角的検証 |
| **高速化** | コンテナ共有＋データリセット | テスト実行時間の最適化 |

---

## 🔄 1. DBの初期化戦略

### 1.1 コンテナ再生成による初期化

**用途**: 完全にクリーンな状態が必要な統合テスト

```java
@SpringBootTest
@Testcontainers
@TestMethodOrder(OrderAnnotation.class)
class DatabaseInitializationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("fresh_db")
            .withUsername("test")
            .withPassword("test");

    @Test
    @Order(1)
    void shouldStartWithCleanDatabase() {
        // 完全にクリーンな状態でテスト開始
        long count = employeeRepository.count();
        assertThat(count).isZero();
    }

    @Test
    @Order(2)
    void shouldReinitializeForSecondTest() {
        // 前のテストの影響を受けない独立した環境
        long count = departmentRepository.count();
        assertThat(count).isZero();
    }
}
```

### 1.2 トランザクションロールバック

**用途**: 高速な単体テスト、リソース効率重視

```java
@DataJpaTest
@Transactional
@Rollback  // テスト後に自動ロールバック
class TransactionalTestExample {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private EmployeeRepository employeeRepository;

    @Test
    void shouldRollbackAfterTest() {
        // Given: テストデータを投入
        Department dept = new Department("テスト部署", "TEST", new BigDecimal("1000000"));
        entityManager.persistAndFlush(dept);

        Employee emp = new Employee("太郎", "テスト", "test@example.com",
                                   LocalDate.now(), dept);
        entityManager.persistAndFlush(emp);

        // When: ビジネスロジックを実行
        List<Employee> employees = employeeRepository.findByDepartment(dept);

        // Then: 検証
        assertThat(employees).hasSize(1);
        // テスト終了後、データは自動的にロールバックされる
    }
}
```

### 1.3 使い分けの指針

```java
@TestConfiguration
public class DatabaseInitializationStrategy {

    /**
     * コンテナ再生成が適している場合
     */
    public boolean shouldUseContainerRecreation(TestContext context) {
        return context.hasAnnotation(IntegrationTest.class) ||
               context.requiresSchemaChanges() ||
               context.needsCompleteIsolation();
    }

    /**
     * トランザクションロールバックが適している場合
     */
    public boolean shouldUseTransactionalRollback(TestContext context) {
        return context.hasAnnotation(DataJpaTest.class) ||
               context.focusesOnSingleEntity() ||
               context.prioritizesSpeed();
    }
}
```

---

## 📥 2. テストケース毎のデータ投入

### 2.1 @Sql アノテーションによるデータ投入

**用途**: 特定テスト用の簡潔なデータ準備

```java
@SpringBootTest
@Testcontainers
class SqlBasedDataLoadingTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired
    private EmployeeService employeeService;

    @Test
    @Sql("/testdata/departments-basic.sql")
    @Sql("/testdata/employees-engineering.sql")
    void shouldFindEngineeringEmployees() {
        // SQL files have already populated the database
        List<EmployeeDto> engineers = employeeService.findByDepartmentCode("ENG");

        assertThat(engineers)
            .hasSize(5)
            .allMatch(emp -> emp.getDepartmentCode().equals("ENG"));
    }

    @Test
    @Sql(scripts = "/testdata/large-dataset.sql",
         executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
    @Sql(scripts = "/testdata/cleanup.sql",
         executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
    void shouldHandleLargeDataset() {
        // Before: large-dataset.sql executed
        long count = employeeService.getTotalCount();
        assertThat(count).isGreaterThan(1000);

        // Test logic here

        // After: cleanup.sql will be executed
    }
}
```

**SQLファイル例** (`src/test/resources/testdata/departments-basic.sql`):

```sql
-- departments-basic.sql
INSERT INTO departments (name, code, budget, active) VALUES
    ('エンジニアリング部', 'ENG', 5000000.00, true),
    ('営業部', 'SALES', 3000000.00, true),
    ('人事部', 'HR', 2000000.00, true);
```

### 2.2 Flyway Migrationによるデータ投入

**用途**: バージョン管理されたデータマイグレーション

```java
@SpringBootTest
@Testcontainers
@TestPropertySource(properties = {
    "spring.flyway.locations=classpath:db/migration,classpath:db/testdata"
})
class FlywayDataLoadingTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("db/"),
                "/docker-entrypoint-initdb.d/"
            );

    @Test
    void shouldLoadDataViaMigration() {
        // Flyway migrations have run automatically
        // V1__Create_schema.sql
        // V2__Insert_departments.sql
        // V999__Insert_test_data.sql (test-specific migration)

        List<DepartmentDto> departments = departmentService.findAll();
        assertThat(departments).hasSizeGreaterThan(3);
    }
}
```

**Migrationファイル** (`src/test/resources/db/testdata/V999__Insert_test_data.sql`):

```sql
-- V999__Insert_test_data.sql
-- テスト専用データ投入（本番では実行されない）

INSERT INTO departments (name, code, budget, description, active) VALUES
    ('テストエンジニアリング部', 'T-ENG', 2500000.00, 'テスト専用部署', true),
    ('テスト営業部', 'T-SALES', 1500000.00, 'テスト専用営業', true);

INSERT INTO employees (first_name, last_name, email, hire_date, department_id, active)
SELECT
    'テスト太郎' || generate_series,
    'サンプル' || generate_series,
    'test' || generate_series || '@example.com',
    CURRENT_DATE - INTERVAL '1 day' * generate_series,
    (SELECT id FROM departments WHERE code = 'T-ENG'),
    true
FROM generate_series(1, 50);
```

### 2.3 Liquibase Changesetによるデータ投入

**用途**: 複雑なデータ変換、環境別データ管理

```java
@SpringBootTest
@Testcontainers
@TestPropertySource(properties = {
    "spring.liquibase.change-log=classpath:db/changelog/test-master.xml"
})
class LiquibaseDataLoadingTest {

    @Test
    void shouldLoadDataViaChangeset() {
        // Liquibase changesets have been applied
        List<EmployeeDto> employees = employeeService.findActiveEmployees();
        assertThat(employees).isNotEmpty();
    }
}
```

**Changesetファイル** (`src/test/resources/db/changelog/test-data.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                   http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd">

    <changeSet id="test-departments-1" author="test" context="test">
        <insert tableName="departments">
            <column name="name" value="テスト開発部"/>
            <column name="code" value="T-DEV"/>
            <column name="budget" value="3000000.00"/>
            <column name="active" value="true"/>
        </insert>
    </changeSet>

    <changeSet id="test-employees-bulk-1" author="test" context="test">
        <sql>
            INSERT INTO employees (first_name, last_name, email, hire_date, department_id, active)
            SELECT
                'Bulk' || row_number() OVER(),
                'Employee' || row_number() OVER(),
                'bulk' || row_number() OVER() || '@test.com',
                CURRENT_DATE - INTERVAL '30 days',
                (SELECT id FROM departments WHERE code = 'T-DEV'),
                true
            FROM generate_series(1, 100);
        </sql>
    </changeSet>
</databaseChangeLog>
```

---

## 🔀 3. パターンデータの切替

### 3.1 SQLファイル分離による管理

**ファイル構造**:
```
src/test/resources/testdata/
├── scenarios/
│   ├── small-company.sql      # 小規模企業シナリオ
│   ├── large-enterprise.sql   # 大企業シナリオ
│   ├── startup.sql           # スタートアップシナリオ
│   └── government.sql        # 官公庁シナリオ
├── departments/
│   ├── tech-focused.sql      # 技術系部署中心
│   ├── sales-heavy.sql       # 営業系部署中心
│   └── balanced.sql          # バランス型組織
└── employees/
    ├── junior-heavy.sql      # 若手中心
    ├── senior-heavy.sql      # ベテラン中心
    └── mixed-experience.sql  # 経験混在
```

### 3.2 ParameterizedTestによる効率的テスト

```java
@SpringBootTest
@Testcontainers
class ParameterizedDataPatternTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @ParameterizedTest(name = "企業タイプ: {0}")
    @ValueSource(strings = {"small-company", "large-enterprise", "startup", "government"})
    @Sql(scripts = "/testdata/cleanup.sql", executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
    void shouldHandleDifferentCompanyTypes(String companyType) {
        // Given: 企業タイプ別データを読み込み
        loadScenarioData(companyType);

        // When: 共通のビジネスロジックを実行
        OrganizationSummary summary = organizationService.generateSummary();

        // Then: 企業タイプに応じた検証
        switch (companyType) {
            case "small-company":
                assertThat(summary.getTotalEmployees()).isBetween(10, 50);
                assertThat(summary.getDepartmentCount()).isBetween(3, 7);
                break;
            case "large-enterprise":
                assertThat(summary.getTotalEmployees()).isGreaterThan(500);
                assertThat(summary.getDepartmentCount()).isGreaterThan(10);
                break;
            case "startup":
                assertThat(summary.getTotalEmployees()).isLessThan(30);
                assertThat(summary.getAverageAge()).isLessThan(35);
                break;
            case "government":
                assertThat(summary.getJobStability()).isGreaterThan(0.95);
                break;
        }
    }

    @ParameterizedTest
    @CsvSource({
        "tech-focused, 5, ENG",
        "sales-heavy, 8, SALES",
        "balanced, 6, HR"
    })
    void shouldValidateDepartmentFocus(String scenario, int expectedDepts, String dominantDept) {
        // Given: 部署構成シナリオを読み込み
        loadDepartmentScenario(scenario);

        // When: 部署分析を実行
        DepartmentAnalysis analysis = departmentService.analyzeDepartments();

        // Then: 想定通りの部署構成か検証
        assertThat(analysis.getTotalDepartments()).isEqualTo(expectedDepts);
        assertThat(analysis.getDominantDepartmentCode()).isEqualTo(dominantDept);
    }

    private void loadScenarioData(String scenarioName) {
        String sqlPath = "/testdata/scenarios/" + scenarioName + ".sql";
        executeSqlScript(sqlPath);
    }

    private void loadDepartmentScenario(String scenarioName) {
        String sqlPath = "/testdata/departments/" + scenarioName + ".sql";
        executeSqlScript(sqlPath);
    }
}
```

### 3.3 動的SQLファイル選択

```java
@Component
public class TestDataScenarioManager {

    private final JdbcTemplate jdbcTemplate;

    public TestDataScenarioManager(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public void loadScenario(String scenarioName, Map<String, Object> parameters) {
        String sqlContent = loadSqlTemplate(scenarioName);
        String processedSql = processTemplate(sqlContent, parameters);

        executeSql(processedSql);
    }

    public void loadCombinedScenario(List<String> scenarioComponents) {
        scenarioComponents.forEach(component -> {
            String sqlPath = "/testdata/components/" + component + ".sql";
            executeSqlScript(sqlPath);
        });
    }

    private String loadSqlTemplate(String scenarioName) {
        try {
            Resource resource = new ClassPathResource("/testdata/scenarios/" + scenarioName + ".sql");
            return new String(resource.getInputStream().readAllBytes());
        } catch (IOException e) {
            throw new RuntimeException("Failed to load scenario: " + scenarioName, e);
        }
    }
}
```

---

## 🔄 4. 大量パターン回帰テスト

### 4.1 JUnit5 ParameterizedTestによる大量パターンテスト

```java
@SpringBootTest
@Testcontainers
class MassiveRegressionTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @ParameterizedTest(name = "ケース#{index}: {0}部署, {1}名, 予算{2}")
    @CsvFileSource(resources = "/testdata/regression/department-combinations.csv", numLinesToSkip = 1)
    void shouldHandleVariousDepartmentCombinations(
            String departmentType,
            int employeeCount,
            BigDecimal budget,
            boolean hasManager,
            String expectedStatus) {

        // Given: パラメータに基づいてテストデータを生成
        Department dept = createDepartment(departmentType, budget);
        List<Employee> employees = createEmployees(dept, employeeCount, hasManager);

        // When: ビジネスロジックを実行
        DepartmentEvaluationResult result = departmentService.evaluateDepartment(dept.getId());

        // Then: 期待された結果と比較
        assertThat(result.getStatus().toString()).isEqualTo(expectedStatus);
        assertThat(result.getEmployeeCount()).isEqualTo(employeeCount);
        assertThat(result.getBudgetUtilization()).isNotNull();
    }

    @ParameterizedTest
    @MethodSource("generateSalaryCalculationTestCases")
    void shouldCalculateSalaryCorrectly(SalaryTestCase testCase) {
        // Given: テストケースに基づいてemployeeを作成
        Employee employee = createEmployeeFromTestCase(testCase);

        // When: 給与計算を実行
        SalaryCalculationResult result = salaryService.calculateMonthlySalary(
            employee.getId(), testCase.getTargetMonth()
        );

        // Then: 期待値と比較（許容誤差考慮）
        assertThat(result.getBaseSalary())
            .isCloseTo(testCase.getExpectedBaseSalary(), within(new BigDecimal("0.01")));
        assertThat(result.getTotalSalary())
            .isCloseTo(testCase.getExpectedTotalSalary(), within(new BigDecimal("0.01")));
    }

    static Stream<SalaryTestCase> generateSalaryCalculationTestCases() {
        return Stream.of(
            // 基本給のパターン
            SalaryTestCase.builder()
                .employeeLevel("junior")
                .baseAmount(new BigDecimal("250000"))
                .overtimeHours(10)
                .expectedBaseSalary(new BigDecimal("250000"))
                .expectedTotalSalary(new BigDecimal("281250"))
                .build(),

            // 管理職のパターン
            SalaryTestCase.builder()
                .employeeLevel("manager")
                .baseAmount(new BigDecimal("450000"))
                .managementAllowance(new BigDecimal("50000"))
                .expectedBaseSalary(new BigDecimal("450000"))
                .expectedTotalSalary(new BigDecimal("500000"))
                .build(),

            // 特殊ケース: 休職中
            SalaryTestCase.builder()
                .employeeLevel("senior")
                .baseAmount(new BigDecimal("380000"))
                .isOnLeave(true)
                .expectedBaseSalary(BigDecimal.ZERO)
                .expectedTotalSalary(BigDecimal.ZERO)
                .build()
        );
    }
}
```

**CSVテストデータ** (`src/test/resources/testdata/regression/department-combinations.csv`):

```csv
departmentType,employeeCount,budget,hasManager,expectedStatus
engineering,15,3000000.00,true,HEALTHY
engineering,3,3000000.00,false,UNDERSTAFFED
marketing,25,2000000.00,true,OVER_BUDGET
hr,8,1500000.00,true,OPTIMAL
sales,50,5000000.00,true,HIGH_PERFORMANCE
research,5,8000000.00,true,WELL_FUNDED
```

### 4.2 大量データ生成とテスト

```java
@SpringBootTest
@Testcontainers
class LargeScaleRegressionTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withJavaOpts("-Xmx1g")  // 大量データ処理用にメモリ増量
            .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=1g"));

    @Autowired
    private TestDataGenerator testDataGenerator;

    @ParameterizedTest
    @ValueSource(ints = {100, 1000, 10000, 50000})
    void shouldHandleLargeEmployeeDatasets(int employeeCount) {
        // Given: 大量のemployeeデータを生成
        testDataGenerator.generateEmployees(employeeCount);

        // When: 重い検索処理を実行
        StopWatch stopWatch = new StopWatch();
        stopWatch.start();

        List<EmployeeSummaryDto> summaries = employeeService.generateAllEmployeeSummaries();

        stopWatch.stop();

        // Then: 性能と正確性を検証
        assertThat(summaries).hasSize(employeeCount);
        assertThat(stopWatch.getTotalTimeMillis())
            .as("Employee count: %d should complete within acceptable time", employeeCount)
            .isLessThan(calculateAcceptableTimeLimit(employeeCount));

        // データ整合性も検証
        long actualCount = employeeRepository.count();
        assertThat(actualCount).isEqualTo(employeeCount);
    }

    private long calculateAcceptableTimeLimit(int employeeCount) {
        // 1000件あたり500ms以下の性能目標
        return (employeeCount / 1000) * 500 + 1000;  // Base time 1000ms
    }
}
```

---

## ✅ 5. DB状態検証

### 5.1 AssertJによる流暢な検証

```java
@DataJpaTest
@Testcontainers
class DatabaseStateVerificationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Test
    void shouldVerifyComplexDatabaseState() {
        // Given: 複雑なデータ構造を作成
        Department engineering = createDepartment("Engineering", "ENG", new BigDecimal("5000000"));
        Department sales = createDepartment("Sales", "SALES", new BigDecimal("3000000"));

        List<Employee> engineers = createEmployees(engineering, 10);
        List<Employee> salespeople = createEmployees(sales, 15);

        // When: データベース操作を実行
        departmentService.redistributeBudget();

        // Then: AssertJで複雑な状態を検証
        List<Department> allDepartments = departmentRepository.findAll();

        assertThat(allDepartments)
            .hasSize(2)
            .extracting(Department::getName, Department::getBudget, Department::getActive)
            .containsExactlyInAnyOrder(
                tuple("Engineering", new BigDecimal("4000000.00"), true),
                tuple("Sales", new BigDecimal("4000000.00"), true)
            );

        // Employee関連の複合検証
        assertThat(engineers)
            .allMatch(emp -> emp.getDepartment().getCode().equals("ENG"))
            .extracting(Employee::getFirstName)
            .allMatch(name -> name.startsWith("Engineer"));

        // 集約的検証
        assertThat(departmentRepository.findByCode("ENG"))
            .isPresent()
            .get()
            .extracting(Department::getEmployees)
            .asList()
            .hasSize(10)
            .allMatch(emp -> ((Employee)emp).isActive());
    }

    @Test
    void shouldVerifyTransactionalBehavior() {
        // Given: 初期状態
        long initialEmployeeCount = employeeRepository.count();
        long initialDepartmentCount = departmentRepository.count();

        // When: トランザクション操作（失敗が想定される）
        assertThatThrownBy(() -> {
            employeeService.performBulkTransfer(invalidTransferRequest());
        }).isInstanceOf(TransactionException.class);

        // Then: ロールバックにより状態が変わっていないことを確認
        assertThat(employeeRepository.count()).isEqualTo(initialEmployeeCount);
        assertThat(departmentRepository.count()).isEqualTo(initialDepartmentCount);

        // 個別レコードも検証
        List<Employee> allEmployees = employeeRepository.findAll();
        assertThat(allEmployees)
            .allMatch(emp -> emp.getDepartment() != null)  // 転送失敗で孤立していない
            .noneMatch(emp -> emp.getLastModified().isAfter(testStartTime));  // 変更されていない
    }
}
```

### 5.2 Repositoryを通じた検証

```java
@SpringBootTest
@Testcontainers
class RepositoryBasedVerificationTest {

    @Test
    void shouldVerifyBusinessRulesViaRepository() {
        // Given: 複雑なビジネスシナリオ
        setupComplexOrganizationStructure();

        // When: ビジネスロジック実行
        organizationService.performAnnualRestructuring();

        // Then: Repository経由で業務ルールを検証

        // 1. 部署階層の検証
        List<Department> topLevelDepartments = departmentRepository.findByParentIsNull();
        assertThat(topLevelDepartments)
            .hasSize(3)  // 最上位は3部署まで
            .allMatch(dept -> dept.getSubDepartments().size() <= 5);  // 配下は5部署まで

        // 2. 職員配置の検証
        List<Employee> managersWithoutTeam = employeeRepository.findManagersWithoutDirectReports();
        assertThat(managersWithoutTeam)
            .as("全管理職は部下を持つ必要がある")
            .isEmpty();

        // 3. 予算制約の検証
        List<Department> overBudgetDepartments = departmentRepository.findDepartmentsOverBudget();
        assertThat(overBudgetDepartments)
            .as("リストラ後は予算超過部署は存在しない")
            .isEmpty();

        // 4. カスタムクエリによる複合条件検証
        List<EmployeeSalaryProjection> salaryDistribution =
            employeeRepository.findSalaryDistributionByDepartment();

        assertThat(salaryDistribution)
            .extracting(EmployeeSalaryProjection::getDepartmentCode,
                       EmployeeSalaryProjection::getAverageSalary)
            .allMatch(tuple -> {
                String deptCode = (String) tuple.toArray()[0];
                BigDecimal avgSalary = (BigDecimal) tuple.toArray()[1];
                return avgSalary.compareTo(getExpectedSalaryRange(deptCode).getMinimum()) >= 0 &&
                       avgSalary.compareTo(getExpectedSalaryRange(deptCode).getMaximum()) <= 0;
            });
    }
}
```

### 5.3 DB直接クエリによる検証

```java
@SpringBootTest
@Testcontainers
class DirectDatabaseVerificationTest {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void shouldVerifyDatabaseConstraintsDirectly() {
        // Given: データベース制約をテストするデータ
        setupConstraintTestData();

        // When: 制約違反となる操作を実行
        employeeService.attemptInvalidDataModification();

        // Then: SQL直接クエリで制約状態を確認

        // 1. 外部キー制約の検証
        Integer orphanedEmployees = jdbcTemplate.queryForObject(
            """
            SELECT COUNT(*) FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.department_id IS NOT NULL AND d.id IS NULL
            """, Integer.class
        );
        assertThat(orphanedEmployees).isZero();

        // 2. 一意制約の検証
        List<Map<String, Object>> duplicateEmails = jdbcTemplate.queryForList(
            """
            SELECT email, COUNT(*) as count
            FROM employees
            GROUP BY email
            HAVING COUNT(*) > 1
            """
        );
        assertThat(duplicateEmails).isEmpty();

        // 3. チェック制約の検証
        Integer invalidBudgets = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM departments WHERE budget < 0", Integer.class
        );
        assertThat(invalidBudgets).isZero();

        // 4. 業務ルールの検証
        List<Map<String, Object>> anomalies = jdbcTemplate.queryForList(
            """
            SELECT d.name, d.budget, COUNT(e.id) as employee_count,
                   ROUND(d.budget::numeric / NULLIF(COUNT(e.id), 0), 2) as budget_per_employee
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id AND e.active = true
            GROUP BY d.id, d.name, d.budget
            HAVING d.budget::numeric / NULLIF(COUNT(e.id), 0) > 1000000  -- 一人あたり100万円超
            """
        );
        assertThat(anomalies)
            .as("一人当たり予算が100万円を超える部署は異常")
            .isEmpty();
    }

    @Test
    void shouldVerifyPerformanceWithExplainAnalyze() {
        // Given: 大量データでのクエリ性能テスト
        setupLargeDataset(10000);

        // When: 重いクエリを実行して実行計画を取得
        String query = """
            SELECT d.name, COUNT(e.id) as employee_count, AVG(e.hire_date)
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id
            WHERE e.active = true AND e.hire_date > '2020-01-01'
            GROUP BY d.id, d.name
            ORDER BY employee_count DESC
            """;

        // 実行計画の取得
        List<Map<String, Object>> executionPlan = jdbcTemplate.queryForList(
            "EXPLAIN (ANALYZE, BUFFERS) " + query
        );

        // Then: 性能要件を満たしているか検証
        String planText = executionPlan.stream()
            .map(row -> row.get("QUERY PLAN").toString())
            .collect(Collectors.joining("\n"));

        // インデックスが使用されているか
        assertThat(planText)
            .as("クエリでインデックススキャンが使用されている")
            .contains("Index Scan");

        // 実行時間が許容範囲内か
        Pattern executionTimePattern = Pattern.compile("Execution Time: ([\\d.]+) ms");
        Matcher matcher = executionTimePattern.matcher(planText);
        if (matcher.find()) {
            double executionTime = Double.parseDouble(matcher.group(1));
            assertThat(executionTime)
                .as("クエリ実行時間は1000ms以内である必要がある")
                .isLessThan(1000.0);
        }
    }
}
```

---

## ⚡ 6. 高速化戦略

### 6.1 コンテナ共有による高速化

```java
/**
 * 共有コンテナを使用するベーステストクラス
 */
@SpringBootTest
@Testcontainers
@TestMethodOrder(OrderAnnotation.class)
public abstract class SharedContainerBaseTest {

    // クラスレベルでコンテナを共有
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> sharedPostgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("shared_test_db")
            .withUsername("test")
            .withPassword("test")
            .withReuse(true)  // コンテナ再利用を有効化
            .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=1g"));

    @Autowired
    protected JdbcTemplate jdbcTemplate;

    @Autowired
    protected TestDataResetter testDataResetter;

    @BeforeEach
    void resetTestData() {
        // 各テスト前にデータをリセット（コンテナ再作成より高速）
        testDataResetter.resetToBaseState();
    }
}

/**
 * 共有コンテナを継承して使用
 */
class FastEmployeeServiceTest extends SharedContainerBaseTest {

    @Test
    @Order(1)
    void shouldProcessEmployeesQuickly() {
        // 共有コンテナなので起動時間ゼロ
        List<Employee> employees = employeeService.findAll();
        assertThat(employees).isNotNull();
    }

    @Test
    @Order(2)
    void shouldHandleDepartmentOperations() {
        // 前のテストの影響を受けない（データリセット済み）
        List<Department> departments = departmentService.findAll();
        assertThat(departments).isEmpty();  // リセットされている
    }
}
```

### 6.2 データリセット戦略

```java
@Component
public class TestDataResetter {

    private final JdbcTemplate jdbcTemplate;
    private final List<String> tableResetOrder;

    public TestDataResetter(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
        // 外部キー制約を考慮した順序でテーブルをリセット
        this.tableResetOrder = Arrays.asList(
            "employees",      // 外部キーを持つテーブルから
            "departments",    // 参照されるテーブルへ
            "audit_logs"      // 監査テーブル
        );
    }

    public void resetToBaseState() {
        // 高速なTRUNCATEを使用
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 0");

        tableResetOrder.forEach(tableName -> {
            jdbcTemplate.execute("TRUNCATE TABLE " + tableName + " RESTART IDENTITY");
        });

        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 1");

        // ベース状態のデータを投入
        loadBaseTestData();
    }

    public void resetToEmptyState() {
        // 完全に空の状態にリセット
        tableResetOrder.forEach(tableName -> {
            jdbcTemplate.execute("DELETE FROM " + tableName);
        });
    }

    private void loadBaseTestData() {
        // 最小限の基本データのみ投入（高速）
        jdbcTemplate.execute(
            """
            INSERT INTO departments (id, name, code, budget, active) VALUES
                (1, 'Default Department', 'DEFAULT', 1000000.00, true)
            """
        );
    }
}
```

### 6.3 パフォーマンス測定と最適化

```java
@SpringBootTest
@Testcontainers
class PerformanceOptimizationTest extends SharedContainerBaseTest {

    @Test
    void shouldMeasureTestExecutionPerformance() {
        // 異なる高速化戦略の効果を測定
        Map<String, Long> strategyPerformance = new HashMap<>();

        // 1. コンテナ再作成戦略（ベースライン）
        long containerRecreationTime = measureExecutionTime(() -> {
            // 新しいコンテナを作成してテスト実行
            try (PostgreSQLContainer<?> freshContainer = new PostgreSQLContainer<>("postgres:15")) {
                freshContainer.start();
                runStandardTestSuite(freshContainer);
            }
        });
        strategyPerformance.put("container-recreation", containerRecreationTime);

        // 2. 共有コンテナ + データリセット戦略
        long sharedContainerTime = measureExecutionTime(() -> {
            testDataResetter.resetToBaseState();
            runStandardTestSuite(sharedPostgres);
        });
        strategyPerformance.put("shared-container", sharedContainerTime);

        // 3. トランザクションロールバック戦略
        long transactionalTime = measureExecutionTime(() -> {
            runTransactionalTestSuite();
        });
        strategyPerformance.put("transactional", transactionalTime);

        // Then: パフォーマンス改善を検証
        logger.info("Performance comparison: {}", strategyPerformance);

        assertThat(sharedContainerTime)
            .as("共有コンテナ戦略はコンテナ再作成より高速")
            .isLessThan(containerRecreationTime * 0.3);  // 70%以上の改善

        assertThat(transactionalTime)
            .as("トランザクション戦略は最も高速")
            .isLessThan(sharedContainerTime * 0.5);  // 50%以上の改善
    }

    @Test
    void shouldOptimizeTestContainerConfiguration() {
        // TestContainer最適化設定の効果を測定
        Map<String, PostgreSQLContainer<?>> configurations = Map.of(
            "default", new PostgreSQLContainer<>("postgres:15"),

            "optimized", new PostgreSQLContainer<>("postgres:15")
                .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=500m"))
                .withCommand("postgres", "-c", "fsync=off", "-c", "synchronous_commit=off")
                .withJavaOpts("-Xmx512m"),

            "minimal", new PostgreSQLContainer<>("postgres:15-alpine")
                .withTmpFs(Collections.singletonMap("/var/lib/postgresql/data", "rw,size=200m"))
                .withCommand("postgres", "-c", "shared_buffers=128MB", "-c", "max_connections=20")
        );

        Map<String, Long> startupTimes = new HashMap<>();

        configurations.forEach((name, container) -> {
            long startupTime = measureExecutionTime(container::start);
            startupTimes.put(name, startupTime);
            container.stop();
        });

        logger.info("Container startup times: {}", startupTimes);

        // 最適化されたコンテナが高速に起動することを確認
        assertThat(startupTimes.get("optimized"))
            .isLessThan(startupTimes.get("default") * 0.8);
        assertThat(startupTimes.get("minimal"))
            .isLessThan(startupTimes.get("default") * 0.6);
    }

    private long measureExecutionTime(Runnable operation) {
        long startTime = System.currentTimeMillis();
        operation.run();
        return System.currentTimeMillis() - startTime;
    }
}
```

### 6.4 実行時間比較

**典型的な実行時間の改善例**:

| 戦略 | 初回実行 | 2回目以降 | 改善率 |
|------|----------|-----------|--------|
| コンテナ再作成 | 15秒 | 15秒 | ベースライン |
| 共有コンテナ + データリセット | 15秒 | 3秒 | 80%改善 |
| トランザクションロールバック | 2秒 | 1.5秒 | 90%改善 |

## 📋 まとめ

この実践ガイドで紹介した戦略を組み合わせることで、効率的で保守可能なデータベーステスト環境を構築できます。

### 推奨する実装順序

1. **基本的なTestContainers環境** → コンテナ共有設定
2. **@Sqlによるデータ投入** → Flyway/Liquibaseへの発展
3. **単純なParameterizedTest** → 複雑なパターンテスト
4. **AssertJによる基本検証** → Repository + 直接クエリの組み合わせ
5. **個別最適化** → 統合的な高速化戦略

### 選択の指針

- **高速性重視**: トランザクションロールバック + 共有コンテナ
- **独立性重視**: コンテナ再作成 + @Sql
- **複雑性対応**: Flyway/Liquibase + ParameterizedTest
- **大量テスト**: ParameterizedTest + 直接クエリ検証

各プロジェクトの特性に応じて、最適な組み合わせを選択してください。