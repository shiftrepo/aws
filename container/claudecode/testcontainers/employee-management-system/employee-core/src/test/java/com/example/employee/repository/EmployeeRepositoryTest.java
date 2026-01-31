package com.example.employee.repository;

import com.example.employee.entity.Department;
import com.example.employee.entity.Employee;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Repository layer tests for Employee entity (Beginner Level).
 *
 * Demonstrates basic database operations and JPA query method testing.
 * Tests CRUD operations, query derivation, and basic database interactions.
 */
@DataJpaTest
@ActiveProfiles("test")
class EmployeeRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private EmployeeRepository employeeRepository;

    @Autowired
    private DepartmentRepository departmentRepository;

    @Test
    void shouldSaveAndFindEmployee() {
        // Given: Create and save an employee
        Employee employee = createTestEmployee("John", "Doe", "john.doe@test.com");

        // When: Save the employee
        Employee savedEmployee = employeeRepository.save(employee);

        // Then: Employee should be saved and findable
        assertThat(savedEmployee.getId()).isNotNull();
        assertThat(savedEmployee.getFirstName()).isEqualTo("John");
        assertThat(savedEmployee.getLastName()).isEqualTo("Doe");
        assertThat(savedEmployee.getEmail()).isEqualTo("john.doe@test.com");

        // And: Should be findable by ID
        Optional<Employee> found = employeeRepository.findById(savedEmployee.getId());
        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("John");
    }

    @Test
    void shouldFindByEmail() {
        // Given: Save an employee
        Employee employee = createTestEmployee("Jane", "Smith", "jane.smith@test.com");
        employeeRepository.save(employee);
        entityManager.flush();

        // When: Find by email
        Optional<Employee> found = employeeRepository.findByEmail("jane.smith@test.com");

        // Then: Employee should be found
        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("Jane");
        assertThat(found.get().getLastName()).isEqualTo("Smith");
    }

    @Test
    void shouldNotFindByNonExistentEmail() {
        // When: Search for non-existent email
        Optional<Employee> found = employeeRepository.findByEmail("nonexistent@test.com");

        // Then: Should not be found
        assertThat(found).isEmpty();
    }

    @Test
    void shouldFindActiveEmployees() {
        // Given: Create active and inactive employees
        Employee activeEmployee = createTestEmployee("Active", "User", "active@test.com");
        activeEmployee.setActive(true);

        Employee inactiveEmployee = createTestEmployee("Inactive", "User", "inactive@test.com");
        inactiveEmployee.setActive(false);

        employeeRepository.save(activeEmployee);
        employeeRepository.save(inactiveEmployee);
        entityManager.flush();

        // When: Find active employees
        List<Employee> activeEmployees = employeeRepository.findByActiveTrue();

        // Then: Should only find active employee
        assertThat(activeEmployees).hasSize(1);
        assertThat(activeEmployees.get(0).getFirstName()).isEqualTo("Active");
        assertThat(activeEmployees.get(0).getActive()).isTrue();
    }

    @Test
    void shouldFindEmployeesByDepartment() {
        // Given: Create department and employees
        Department department = createTestDepartment("IT", "IT", new BigDecimal("2000000"));
        department = departmentRepository.save(department);

        Employee emp1 = createTestEmployee("Employee1", "IT", "emp1@it.com");
        emp1.setDepartment(department);

        Employee emp2 = createTestEmployee("Employee2", "IT", "emp2@it.com");
        emp2.setDepartment(department);

        Employee emp3 = createTestEmployee("Employee3", "HR", "emp3@hr.com");
        // No department assigned

        employeeRepository.save(emp1);
        employeeRepository.save(emp2);
        employeeRepository.save(emp3);
        entityManager.flush();

        // When: Find employees by department
        List<Employee> itEmployees = employeeRepository.findByDepartmentId(department.getId());

        // Then: Should find 2 IT employees
        assertThat(itEmployees).hasSize(2);
        assertThat(itEmployees).extracting(Employee::getFirstName)
                                .containsExactlyInAnyOrder("Employee1", "Employee2");
    }

    @Test
    void shouldFindEmployeesByDepartmentCode() {
        // Given: Create department and employee
        Department department = createTestDepartment("Information Technology", "IT", new BigDecimal("2000000"));
        department = departmentRepository.save(department);

        Employee employee = createTestEmployee("Tech", "Guy", "tech@company.com");
        employee.setDepartment(department);
        employeeRepository.save(employee);
        entityManager.flush();

        // When: Find employees by department code
        List<Employee> employees = employeeRepository.findByDepartment_Code("IT");

        // Then: Should find the employee
        assertThat(employees).hasSize(1);
        assertThat(employees.get(0).getFirstName()).isEqualTo("Tech");
    }

    @Test
    void shouldFindEmployeesByHireDateRange() {
        // Given: Create employees with different hire dates
        Employee emp1 = createTestEmployee("Early", "Hire", "early@test.com");
        emp1.setHireDate(LocalDate.of(2022, 1, 15));

        Employee emp2 = createTestEmployee("Mid", "Hire", "mid@test.com");
        emp2.setHireDate(LocalDate.of(2023, 6, 15));

        Employee emp3 = createTestEmployee("Late", "Hire", "late@test.com");
        emp3.setHireDate(LocalDate.of(2024, 12, 15));

        employeeRepository.save(emp1);
        employeeRepository.save(emp2);
        employeeRepository.save(emp3);
        entityManager.flush();

        // When: Find employees hired in 2023
        LocalDate startDate = LocalDate.of(2023, 1, 1);
        LocalDate endDate = LocalDate.of(2023, 12, 31);
        List<Employee> employees2023 = employeeRepository.findByHireDateBetween(startDate, endDate);

        // Then: Should find only the mid hire
        assertThat(employees2023).hasSize(1);
        assertThat(employees2023.get(0).getFirstName()).isEqualTo("Mid");
    }

    @Test
    void shouldCheckEmailUniqueness() {
        // Given: Save an employee
        Employee employee = createTestEmployee("Unique", "User", "unique@test.com");
        employeeRepository.save(employee);
        entityManager.flush();

        // When: Check if email exists
        boolean exists = employeeRepository.existsByEmail("unique@test.com");
        boolean notExists = employeeRepository.existsByEmail("notexist@test.com");

        // Then: Should return correct existence status
        assertThat(exists).isTrue();
        assertThat(notExists).isFalse();
    }

    @Test
    void shouldCountActiveEmployees() {
        // Given: Create active and inactive employees
        for (int i = 1; i <= 3; i++) {
            Employee emp = createTestEmployee("Active" + i, "User", "active" + i + "@test.com");
            emp.setActive(true);
            employeeRepository.save(emp);
        }

        Employee inactive = createTestEmployee("Inactive", "User", "inactive@test.com");
        inactive.setActive(false);
        employeeRepository.save(inactive);
        entityManager.flush();

        // When: Count active employees
        long activeCount = employeeRepository.countByActiveTrue();

        // Then: Should count only active employees
        assertThat(activeCount).isEqualTo(3);
    }

    // Helper methods
    private Employee createTestEmployee(String firstName, String lastName, String email) {
        Employee employee = new Employee();
        employee.setFirstName(firstName);
        employee.setLastName(lastName);
        employee.setEmail(email);
        employee.setHireDate(LocalDate.of(2023, 6, 15));
        employee.setActive(true);
        return employee;
    }

    private Department createTestDepartment(String name, String code, BigDecimal budget) {
        Department department = new Department();
        department.setName(name);
        department.setCode(code);
        department.setBudget(budget);
        department.setDescription("Test department");
        department.setActive(true);
        return department;
    }
}