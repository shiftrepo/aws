package com.example.employee.integration;

import com.example.employee.entity.Department;
import com.example.employee.entity.Employee;
import com.example.employee.repository.DepartmentRepository;
import com.example.employee.repository.EmployeeRepository;
import com.example.employee.testconfig.SharedContainerBaseTest;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvFileSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.jdbc.Sql;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

/**
 * 高度な統合テスト - 全テスト戦略を実装
 *
 * 実装戦略:
 * ✅ DBの初期化: コンテナ再生成 / トランザクションロールバック
 * ✅ テストケース毎のデータ投入: @Sql / Flyway / Liquibase
 * ✅ パターンデータの切替: SQLファイル分離 / ParameterizedTest
 * ✅ 大量パターン回帰: JUnit5 ParameterizedTest
 * ✅ DB状態検証: AssertJ / Repository / DB直接クエリ
 * ✅ 高速化: コンテナ共有＋データリセット
 */
class AdvancedEmployeeIntegrationTest extends SharedContainerBaseTest {

    @Autowired
    private EmployeeRepository employeeRepository;

    @Autowired
    private DepartmentRepository departmentRepository;

    // ============================================================================
    // 戦略1: DBの初期化 - コンテナ再生成 (SharedContainerBaseTest)
    // 戦略6: 高速化 - コンテナ共有＋データリセット (SharedContainerBaseTest)
    // ============================================================================

    @Test
    @Order(1)
    void shouldStartWithCleanDatabase() {
        // Given: SharedContainerBaseTest による自動リセット
        long employeeCount = employeeRepository.count();
        long departmentCount = departmentRepository.count();

        // Then: ベース状態になっている
        assertThat(employeeCount).isZero();
        assertThat(departmentCount).isEqualTo(3);  // ベースデータ: HR, IT, Finance
    }

    // ============================================================================
    // 戦略2: テストケース毎のデータ投入 - @Sql
    // ============================================================================

    @Test
    @Order(2)
    @Sql("/sql/departments-basic.sql")
    @Sql("/sql/employees-engineering.sql")
    void shouldLoadDataUsingSqlAnnotation() {
        // Given: @Sqlアノテーションでデータが投入済み

        // When: エンジニアリング部署の従業員を検索
        List<Employee> engineers = employeeRepository.findByDepartment_Code("ENG");

        // Then: SQLファイルからロードされたデータを確認
        assertThat(engineers)
            .hasSize(5)  // employees-engineering.sqlで定義
            .extracting(Employee::getFirstName)
            .containsExactlyInAnyOrder("Alice", "Bob", "Carol", "David", "Eva");

        // And: 部署データも正しく投入されている
        List<Department> departments = departmentRepository.findAll();
        assertThat(departments)
            .hasSize(5)  // departments-basic.sqlで定義
            .extracting(Department::getCode)
            .containsExactlyInAnyOrder("ENG", "SALES", "MKT", "HR", "FIN");
    }

    // ============================================================================
    // 戦略3: パターンデータの切替 - SQLファイル分離 / ParameterizedTest
    // ============================================================================

    @ParameterizedTest(name = "企業規模: {0}")
    @ValueSource(strings = {"small-company", "large-enterprise"})
    @Order(3)
    void shouldSwitchDataPatternsBasedOnCompanySize(String companyType) {
        // Given: 企業タイプに基づいてデータパターンを切り替え
        loadDataPattern(companyType);

        // When: 組織構造を分析
        long totalEmployees = employeeRepository.count();
        long totalDepartments = departmentRepository.count();

        // Then: 企業タイプに応じた検証
        switch (companyType) {
            case "small-company":
                assertThat(totalEmployees).isBetween(10L, 50L);
                assertThat(totalDepartments).isBetween(3L, 7L);
                break;
            case "large-enterprise":
                assertThat(totalEmployees).isGreaterThan(500L);
                assertThat(totalDepartments).isGreaterThan(10L);
                break;
        }

        // And: データ整合性を確認
        List<Employee> orphanedEmployees = findOrphanedEmployees();
        assertThat(orphanedEmployees).isEmpty();
    }

    // ============================================================================
    // 戦略4: 大量パターン回帰 - JUnit5 ParameterizedTest
    // ============================================================================

    @ParameterizedTest(name = "部署パターン#{index}: {0}部署, 予算{2}, 管理者{3} -> {4}")
    @CsvFileSource(resources = "/testdata/regression/department-combinations.csv", numLinesToSkip = 1)
    @Order(4)
    void shouldHandleMassiveDepartmentCombinations(
            String departmentType,
            int employeeCount,
            BigDecimal budget,
            boolean hasManager,
            String expectedStatus,
            String description) {

        // Given: パラメータに基づいて部署とemployeeを作成
        Department dept = createDepartmentByType(departmentType, budget);
        createEmployeesForDepartment(dept, employeeCount, hasManager);

        // When: 部署の状態を評価
        DepartmentStatus actualStatus = evaluateDepartmentStatus(dept);

        // Then: 期待された状態と一致することを確認
        assertThat(actualStatus.toString()).isEqualTo(expectedStatus);

        // And: ビジネスルールが適用されていることを確認
        validateBusinessRules(dept, employeeCount, budget, hasManager);
    }

    // ============================================================================
    // 戦略5: DB状態検証 - AssertJ / Repository / DB直接クエリ
    // ============================================================================

    @Test
    @Order(5)
    @Sql("/sql/departments-basic.sql")
    @Sql("/sql/employees-engineering.sql")
    void shouldVerifyDatabaseStateWithMultipleStrategies() {
        // 検証戦略1: AssertJによる流暢な検証
        List<Department> departments = departmentRepository.findAll();
        assertThat(departments)
            .hasSize(5)
            .extracting(Department::getName, Department::getBudget, Department::getActive)
            .containsExactlyInAnyOrder(
                tuple("Engineering", new BigDecimal("5000000.00"), true),
                tuple("Sales", new BigDecimal("3000000.00"), true),
                tuple("Marketing", new BigDecimal("2000000.00"), true),
                tuple("Human Resources", new BigDecimal("1500000.00"), true),
                tuple("Finance", new BigDecimal("2500000.00"), true)
            );

        // 検証戦略2: Repository経由での検証
        List<Employee> activeEmployees = employeeRepository.findByActiveTrue();
        assertThat(activeEmployees)
            .hasSize(5)
            .allMatch(emp -> emp.getDepartment() != null)
            .allMatch(emp -> emp.getDepartment().getCode().equals("ENG"));

        // 検証戦略3: DB直接クエリによる検証
        Integer orphanedEmployeeCount = jdbcTemplate.queryForObject(
            """
            SELECT COUNT(*) FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.department_id IS NOT NULL AND d.id IS NULL
            """, Integer.class
        );
        assertThat(orphanedEmployeeCount).isZero();

        // 集約クエリでの検証
        List<Map<String, Object>> departmentStats = jdbcTemplate.queryForList(
            """
            SELECT d.code, d.name, COUNT(e.id) as employee_count,
                   ROUND(d.budget::numeric / NULLIF(COUNT(e.id), 0), 2) as budget_per_employee
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id AND e.active = true
            GROUP BY d.id, d.code, d.name, d.budget
            ORDER BY d.code
            """
        );

        assertThat(departmentStats)
            .hasSize(5)
            .extracting(row -> row.get("code"))
            .containsExactly("ENG", "FIN", "HR", "MKT", "SALES");

        // エンジニアリング部署の詳細検証
        Map<String, Object> engStats = departmentStats.stream()
            .filter(row -> "ENG".equals(row.get("code")))
            .findFirst()
            .orElseThrow();

        assertThat(engStats.get("employee_count")).isEqualTo(5L);
        BigDecimal budgetPerEmployee = (BigDecimal) engStats.get("budget_per_employee");
        assertThat(budgetPerEmployee).isEqualByComparingTo(new BigDecimal("1000000.00"));
    }

    @Test
    @Order(6)
    void shouldVerifyDatabaseConstraintsAndPerformance() {
        // Given: 制約テスト用データを準備
        testDataResetter.resetToEmptyState();
        setupConstraintTestData();

        // 制約検証1: Email一意性
        List<Map<String, Object>> duplicateEmails = jdbcTemplate.queryForList(
            """
            SELECT email, COUNT(*) as count
            FROM employees
            GROUP BY email
            HAVING COUNT(*) > 1
            """
        );
        assertThat(duplicateEmails).isEmpty();

        // 制約検証2: 部署コード一意性
        List<Map<String, Object>> duplicateCodes = jdbcTemplate.queryForList(
            """
            SELECT code, COUNT(*) as count
            FROM departments
            GROUP BY code
            HAVING COUNT(*) > 1
            """
        );
        assertThat(duplicateCodes).isEmpty();

        // パフォーマンス検証: クエリ実行計画
        List<Map<String, Object>> executionPlan = jdbcTemplate.queryForList(
            """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT d.name, COUNT(e.id) as employee_count
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id
            WHERE e.active = true
            GROUP BY d.id, d.name
            ORDER BY employee_count DESC
            """
        );

        String planText = executionPlan.stream()
            .map(row -> row.get("QUERY PLAN").toString())
            .reduce("", (a, b) -> a + "\n" + b);

        // 基本的なパフォーマンス要件の確認
        assertThat(planText).contains("ms");  // 実行時間が測定されている
    }

    // ============================================================================
    // Helper Methods
    // ============================================================================

    private void loadDataPattern(String patternName) {
        String sqlPath = "sql/patterns/" + patternName + ".sql";
        try {
            jdbcTemplate.execute(loadSqlFromClasspath(sqlPath));
        } catch (Exception e) {
            throw new RuntimeException("Failed to load pattern: " + patternName, e);
        }
    }

    private String loadSqlFromClasspath(String path) {
        try {
            return new String(getClass().getClassLoader()
                .getResourceAsStream(path).readAllBytes());
        } catch (Exception e) {
            throw new RuntimeException("Failed to load SQL file: " + path, e);
        }
    }

    private List<Employee> findOrphanedEmployees() {
        return jdbcTemplate.query(
            """
            SELECT e.id FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.department_id IS NOT NULL AND d.id IS NULL
            """,
            (rs, rowNum) -> {
                Employee emp = new Employee();
                emp.setId(rs.getLong("id"));
                return emp;
            }
        );
    }

    private Department createDepartmentByType(String type, BigDecimal budget) {
        Department dept = new Department();
        dept.setName(type.substring(0, 1).toUpperCase() + type.substring(1) + " Department");
        dept.setCode(type.toUpperCase().substring(0, Math.min(3, type.length())));
        dept.setBudget(budget);
        dept.setDescription("Test department for " + type);
        dept.setActive(true);
        return departmentRepository.save(dept);
    }

    private void createEmployeesForDepartment(Department dept, int count, boolean hasManager) {
        for (int i = 1; i <= count; i++) {
            Employee emp = new Employee();
            emp.setFirstName("Employee" + i);
            emp.setLastName(dept.getName().split(" ")[0]);
            emp.setEmail("emp" + i + "@" + dept.getCode().toLowerCase() + ".com");
            emp.setHireDate(java.time.LocalDate.now().minusDays(i * 30));
            emp.setActive(true);
            emp.setDepartment(dept);

            if (i == 1 && hasManager) {
                emp.setFirstName("Manager");
                emp.setLastName(dept.getName().split(" ")[0]);
            }

            employeeRepository.save(emp);
        }
    }

    private DepartmentStatus evaluateDepartmentStatus(Department dept) {
        long empCount = employeeRepository.countByDepartmentId(dept.getId());
        BigDecimal budgetPerEmployee = dept.getBudget().divide(BigDecimal.valueOf(Math.max(1, empCount)));

        if (empCount == 0) return DepartmentStatus.UNDERSTAFFED;
        if (empCount > 100) return DepartmentStatus.OVERSTAFFED;
        if (budgetPerEmployee.compareTo(new BigDecimal("200000")) > 0) return DepartmentStatus.OVER_BUDGET;
        if (budgetPerEmployee.compareTo(new BigDecimal("50000")) < 0) return DepartmentStatus.UNDER_FUNDED;
        if (empCount >= 40) return DepartmentStatus.HIGH_PERFORMANCE;
        if (budgetPerEmployee.compareTo(new BigDecimal("150000")) > 0) return DepartmentStatus.WELL_FUNDED;

        return DepartmentStatus.OPTIMAL;
    }

    private void validateBusinessRules(Department dept, int employeeCount, BigDecimal budget, boolean hasManager) {
        // ビジネスルール検証
        if (employeeCount > 10) {
            assertThat(hasManager)
                .as("10人以上の部署には管理者が必要")
                .isTrue();
        }

        BigDecimal budgetPerEmployee = budget.divide(BigDecimal.valueOf(Math.max(1, employeeCount)));
        assertThat(budgetPerEmployee)
            .as("従業員一人あたりの予算は妥当な範囲内")
            .isBetween(new BigDecimal("30000"), new BigDecimal("500000"));
    }

    private void setupConstraintTestData() {
        // 制約テスト用の基本データ
        jdbcTemplate.execute(
            """
            INSERT INTO departments (name, code, budget, active) VALUES
                ('Test Dept 1', 'TD1', 1000000.00, true),
                ('Test Dept 2', 'TD2', 2000000.00, true);

            INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id)
            VALUES
                ('Test', 'Employee1', 'test1@company.com', CURRENT_DATE, true, 1),
                ('Test', 'Employee2', 'test2@company.com', CURRENT_DATE, true, 2);
            """
        );
    }

    // Status enum for department evaluation
    private enum DepartmentStatus {
        HEALTHY, OPTIMAL, UNDERSTAFFED, OVERSTAFFED, OVER_BUDGET, UNDER_FUNDED,
        HIGH_PERFORMANCE, WELL_FUNDED, COST_EFFECTIVE
    }
}