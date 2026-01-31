package com.example.employee.repository;

import com.example.employee.entity.Department;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Repository layer tests for Department entity (Beginner Level).
 *
 * Demonstrates basic database operations, custom queries, and
 * aggregation functions for department management.
 */
@DataJpaTest
@ActiveProfiles("test")
class DepartmentRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private DepartmentRepository departmentRepository;

    @Test
    void shouldSaveAndFindDepartment() {
        // Given: Create a department
        Department department = createTestDepartment("Human Resources", "HR", new BigDecimal("1000000"));

        // When: Save the department
        Department savedDepartment = departmentRepository.save(department);

        // Then: Department should be saved with ID
        assertThat(savedDepartment.getId()).isNotNull();
        assertThat(savedDepartment.getName()).isEqualTo("Human Resources");
        assertThat(savedDepartment.getCode()).isEqualTo("HR");
        assertThat(savedDepartment.getBudget()).isEqualByComparingTo(new BigDecimal("1000000"));

        // And: Should be findable by ID
        Optional<Department> found = departmentRepository.findById(savedDepartment.getId());
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Human Resources");
    }

    @Test
    void shouldFindByCode() {
        // Given: Save a department
        Department department = createTestDepartment("Information Technology", "IT", new BigDecimal("2000000"));
        departmentRepository.save(department);
        entityManager.flush();

        // When: Find by code
        Optional<Department> found = departmentRepository.findByCode("IT");

        // Then: Department should be found
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Information Technology");
        assertThat(found.get().getBudget()).isEqualByComparingTo(new BigDecimal("2000000"));
    }

    @Test
    void shouldNotFindByNonExistentCode() {
        // When: Search for non-existent code
        Optional<Department> found = departmentRepository.findByCode("NONEXISTENT");

        // Then: Should not be found
        assertThat(found).isEmpty();
    }

    @Test
    void shouldFindActiveDepartments() {
        // Given: Create active and inactive departments
        Department activeDept = createTestDepartment("Active Dept", "ACTIVE", new BigDecimal("1000000"));
        activeDept.setActive(true);

        Department inactiveDept = createTestDepartment("Inactive Dept", "INACTIVE", new BigDecimal("500000"));
        inactiveDept.setActive(false);

        departmentRepository.save(activeDept);
        departmentRepository.save(inactiveDept);
        entityManager.flush();

        // When: Find active departments
        List<Department> activeDepartments = departmentRepository.findByActiveTrue();

        // Then: Should only find active department
        assertThat(activeDepartments).hasSize(1);
        assertThat(activeDepartments.get(0).getName()).isEqualTo("Active Dept");
        assertThat(activeDepartments.get(0).getActive()).isTrue();
    }

    @Test
    void shouldFindDepartmentsByBudgetRange() {
        // Given: Create departments with different budgets
        Department lowBudget = createTestDepartment("Low Budget", "LOW", new BigDecimal("500000"));
        Department medBudget = createTestDepartment("Med Budget", "MED", new BigDecimal("1500000"));
        Department highBudget = createTestDepartment("High Budget", "HIGH", new BigDecimal("3000000"));

        departmentRepository.save(lowBudget);
        departmentRepository.save(medBudget);
        departmentRepository.save(highBudget);
        entityManager.flush();

        // When: Find departments with budget between 1M and 2M
        BigDecimal minBudget = new BigDecimal("1000000");
        BigDecimal maxBudget = new BigDecimal("2000000");
        List<Department> departments = departmentRepository.findByBudgetBetween(minBudget, maxBudget);

        // Then: Should find only medium budget department
        assertThat(departments).hasSize(1);
        assertThat(departments.get(0).getName()).isEqualTo("Med Budget");
    }

    @Test
    void shouldFindDepartmentsWithBudgetGreaterThan() {
        // Given: Create departments with different budgets
        Department dept1 = createTestDepartment("Small Dept", "SMALL", new BigDecimal("800000"));
        Department dept2 = createTestDepartment("Large Dept", "LARGE", new BigDecimal("2500000"));

        departmentRepository.save(dept1);
        departmentRepository.save(dept2);
        entityManager.flush();

        // When: Find departments with budget greater than 1M
        BigDecimal threshold = new BigDecimal("1000000");
        List<Department> departments = departmentRepository.findByBudgetGreaterThan(threshold);

        // Then: Should find only large department
        assertThat(departments).hasSize(1);
        assertThat(departments.get(0).getName()).isEqualTo("Large Dept");
    }

    @Test
    void shouldSearchDepartmentsByNamePattern() {
        // Given: Create departments with similar names
        Department techDept = createTestDepartment("Technology Department", "TECH", new BigDecimal("2000000"));
        Department itDept = createTestDepartment("Information Technology", "IT", new BigDecimal("1800000"));
        Department hrDept = createTestDepartment("Human Resources", "HR", new BigDecimal("1200000"));

        departmentRepository.save(techDept);
        departmentRepository.save(itDept);
        departmentRepository.save(hrDept);
        entityManager.flush();

        // When: Search for departments containing "Tech"
        List<Department> techDepts = departmentRepository.findByNameContainingIgnoreCase("tech");

        // Then: Should find both technology departments
        assertThat(techDepts).hasSize(2);
        assertThat(techDepts).extracting(Department::getName)
                             .containsExactlyInAnyOrder("Technology Department", "Information Technology");
    }

    @Test
    void shouldCheckCodeUniqueness() {
        // Given: Save a department
        Department department = createTestDepartment("Finance", "FIN", new BigDecimal("1500000"));
        departmentRepository.save(department);
        entityManager.flush();

        // When: Check if code exists
        boolean exists = departmentRepository.existsByCode("FIN");
        boolean notExists = departmentRepository.existsByCode("MARKETING");

        // Then: Should return correct existence status
        assertThat(exists).isTrue();
        assertThat(notExists).isFalse();
    }

    @Test
    void shouldCountActiveDepartments() {
        // Given: Create active and inactive departments
        for (int i = 1; i <= 4; i++) {
            Department dept = createTestDepartment("Active Dept " + i, "ACTIVE" + i, new BigDecimal("1000000"));
            dept.setActive(true);
            departmentRepository.save(dept);
        }

        Department inactive = createTestDepartment("Inactive Dept", "INACTIVE", new BigDecimal("500000"));
        inactive.setActive(false);
        departmentRepository.save(inactive);
        entityManager.flush();

        // When: Count active departments
        long activeCount = departmentRepository.countByActiveTrue();

        // Then: Should count only active departments
        assertThat(activeCount).isEqualTo(4);
    }

    @Test
    void shouldCalculateTotalActiveBudget() {
        // Given: Create active departments with known budgets
        Department dept1 = createTestDepartment("Dept1", "D1", new BigDecimal("1000000"));
        dept1.setActive(true);
        Department dept2 = createTestDepartment("Dept2", "D2", new BigDecimal("2000000"));
        dept2.setActive(true);
        Department dept3 = createTestDepartment("Inactive", "D3", new BigDecimal("500000"));
        dept3.setActive(false);

        departmentRepository.save(dept1);
        departmentRepository.save(dept2);
        departmentRepository.save(dept3);
        entityManager.flush();

        // When: Calculate total active budget
        BigDecimal totalBudget = departmentRepository.getTotalActiveDepartmentsBudget();

        // Then: Should sum only active departments' budgets
        assertThat(totalBudget).isEqualByComparingTo(new BigDecimal("3000000"));
    }

    @Test
    void shouldCalculateAverageActiveBudget() {
        // Given: Create active departments
        Department dept1 = createTestDepartment("Dept1", "D1", new BigDecimal("1000000"));
        dept1.setActive(true);
        Department dept2 = createTestDepartment("Dept2", "D2", new BigDecimal("3000000"));
        dept2.setActive(true);

        departmentRepository.save(dept1);
        departmentRepository.save(dept2);
        entityManager.flush();

        // When: Calculate average active budget
        BigDecimal avgBudget = departmentRepository.getAverageActiveDepartmentBudget();

        // Then: Should return average of active budgets
        assertThat(avgBudget).isEqualByComparingTo(new BigDecimal("2000000"));
    }

    @Test
    void shouldFindActiveStatusDepartments() {
        // Given: Create departments with different statuses
        Department active = createTestDepartment("Active", "ACT", new BigDecimal("1000000"));
        active.setActive(true);
        Department inactive = createTestDepartment("Inactive", "INACT", new BigDecimal("500000"));
        inactive.setActive(false);

        departmentRepository.save(active);
        departmentRepository.save(inactive);
        entityManager.flush();

        // When: Find departments by active status
        List<Department> activeDepts = departmentRepository.findByActiveStatus(true);
        List<Department> inactiveDepts = departmentRepository.findByActiveStatus(false);

        // Then: Should find departments by status
        assertThat(activeDepts).hasSize(1);
        assertThat(activeDepts.get(0).getName()).isEqualTo("Active");

        assertThat(inactiveDepts).hasSize(1);
        assertThat(inactiveDepts.get(0).getName()).isEqualTo("Inactive");
    }

    // Helper method
    private Department createTestDepartment(String name, String code, BigDecimal budget) {
        Department department = new Department();
        department.setName(name);
        department.setCode(code);
        department.setBudget(budget);
        department.setDescription("Test department for " + name);
        department.setActive(true);
        return department;
    }
}