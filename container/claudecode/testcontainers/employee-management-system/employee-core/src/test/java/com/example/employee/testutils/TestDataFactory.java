package com.example.employee.testutils;

import com.example.employee.entity.Department;
import com.example.employee.entity.Employee;
import com.example.employee.repository.DepartmentRepository;
import com.example.employee.repository.EmployeeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.IntStream;

/**
 * Factory for creating and persisting test data.
 *
 * Provides methods to create complete test data sets with proper
 * relationships between entities. Manages data persistence and
 * cleanup for different test scenarios.
 */
@Component
@Transactional
public class TestDataFactory {

    @Autowired
    private DepartmentRepository departmentRepository;

    @Autowired
    private EmployeeRepository employeeRepository;

    /**
     * Create and persist a complete test data set with departments and employees.
     */
    public TestDataSet createCompleteDataSet() {
        // Create departments
        List<Department> departments = createAndSaveDepartments();

        // Create employees and assign to departments
        List<Employee> employees = createAndSaveEmployees(departments);

        return new TestDataSet(departments, employees);
    }

    /**
     * Create a basic test data set for simple testing scenarios.
     */
    public TestDataSet createBasicDataSet() {
        List<Department> departments = Arrays.asList(
                createAndSaveDepartment("HR", "HR", new BigDecimal("1000000")),
                createAndSaveDepartment("IT", "IT", new BigDecimal("2000000"))
        );

        List<Employee> employees = Arrays.asList(
                createAndSaveEmployee("John", "Doe", "john.doe@test.com", LocalDate.of(2023, 1, 15), departments.get(0)),
                createAndSaveEmployee("Jane", "Smith", "jane.smith@test.com", LocalDate.of(2023, 2, 20), departments.get(1)),
                createAndSaveEmployee("Bob", "Johnson", "bob.johnson@test.com", LocalDate.of(2023, 3, 10), departments.get(1))
        );

        return new TestDataSet(departments, employees);
    }

    /**
     * Create a medium-sized test data set for more complex scenarios.
     */
    public TestDataSet createMediumDataSet() {
        List<Department> departments = createAndSaveDepartments();
        List<Employee> employees = new ArrayList<>();

        // Create employees with various hire dates and statuses
        Random random = new Random(42); // Fixed seed for reproducible tests

        for (int i = 0; i < 20; i++) {
            Department dept = departments.get(i % departments.size());
            Employee employee = TestDataBuilder.employee()
                    .withFirstName("Employee" + i)
                    .withLastName("Test" + i)
                    .withEmail("employee" + i + "@test.com")
                    .withHireDate(LocalDate.now().minusDays(random.nextInt(1000)))
                    .withDepartment(dept)
                    .withActive(random.nextBoolean() || i < 15) // Ensure most are active
                    .buildEntity();

            employees.add(employeeRepository.save(employee));
        }

        return new TestDataSet(departments, employees);
    }

    /**
     * Create a large test data set for performance testing.
     */
    public TestDataSet createLargeDataSet() {
        List<Department> departments = createAndSaveDepartments();
        List<Employee> employees = new ArrayList<>();

        Random random = new Random(42);

        // Create 100 employees
        for (int i = 0; i < 100; i++) {
            Department dept = departments.get(i % departments.size());
            Employee employee = TestDataBuilder.employee()
                    .withFirstName("Employee" + i)
                    .withLastName("Test" + i)
                    .withEmail("employee" + i + "@test.com")
                    .withHireDate(LocalDate.of(2020 + (i % 4), 1 + (i % 12), 1 + (i % 28)))
                    .withDepartment(dept)
                    .withActive(i < 90) // 90% active
                    .buildEntity();

            employees.add(employeeRepository.save(employee));
        }

        return new TestDataSet(departments, employees);
    }

    /**
     * Create test data for specific scenarios.
     */
    public TestDataSet createScenarioDataSet(String scenario) {
        return switch (scenario.toLowerCase()) {
            case "empty" -> new TestDataSet(List.of(), List.of());
            case "departments-only" -> new TestDataSet(createAndSaveDepartments(), List.of());
            case "employees-without-departments" -> createEmployeesWithoutDepartments();
            case "inactive-departments" -> createInactiveDepartments();
            case "veteran-employees" -> createVeteranEmployees();
            case "new-employees" -> createNewEmployees();
            default -> createBasicDataSet();
        };
    }

    // Private helper methods

    private List<Department> createAndSaveDepartments() {
        List<Department> departments = Arrays.asList(
                TestDataBuilder.department().hr().buildEntity(),
                TestDataBuilder.department().it().buildEntity(),
                TestDataBuilder.department().finance().buildEntity(),
                TestDataBuilder.department().marketing().buildEntity(),
                TestDataBuilder.department()
                        .withName("Operations")
                        .withCode("OPS")
                        .withBudget(1200000.00)
                        .withDescription("Operations Department")
                        .buildEntity()
        );

        return departments.stream()
                .map(departmentRepository::save)
                .toList();
    }

    private List<Employee> createAndSaveEmployees(List<Department> departments) {
        List<Employee> employees = new ArrayList<>();

        // Create employees for each department
        for (int i = 0; i < departments.size(); i++) {
            Department dept = departments.get(i);

            // 2-4 employees per department
            int employeeCount = 2 + (i % 3);

            for (int j = 0; j < employeeCount; j++) {
                Employee employee = TestDataBuilder.employee()
                        .withFirstName("Employee" + i + j)
                        .withLastName("Dept" + i)
                        .withEmail("employee" + i + j + "@dept" + i + ".com")
                        .withHireDate(LocalDate.now().minusDays(30 * (i * employeeCount + j)))
                        .withDepartment(dept)
                        .buildEntity();

                employees.add(employeeRepository.save(employee));
            }
        }

        // Add some employees without departments
        for (int i = 0; i < 3; i++) {
            Employee employee = TestDataBuilder.employee()
                    .withFirstName("Unassigned" + i)
                    .withLastName("Employee")
                    .withEmail("unassigned" + i + "@company.com")
                    .buildEntity();

            employees.add(employeeRepository.save(employee));
        }

        return employees;
    }

    private Department createAndSaveDepartment(String name, String code, BigDecimal budget) {
        Department department = TestDataBuilder.department()
                .withName(name)
                .withCode(code)
                .withBudget(budget)
                .buildEntity();
        return departmentRepository.save(department);
    }

    private Employee createAndSaveEmployee(String firstName, String lastName, String email,
                                         LocalDate hireDate, Department department) {
        Employee employee = TestDataBuilder.employee()
                .withName(firstName, lastName)
                .withEmail(email)
                .withHireDate(hireDate)
                .withDepartment(department)
                .buildEntity();
        return employeeRepository.save(employee);
    }

    private TestDataSet createEmployeesWithoutDepartments() {
        List<Department> departments = List.of();
        List<Employee> employees = IntStream.range(0, 5)
                .mapToObj(i -> TestDataBuilder.employee()
                        .withFirstName("Unassigned" + i)
                        .withEmail("unassigned" + i + "@company.com")
                        .buildEntity())
                .map(employeeRepository::save)
                .toList();

        return new TestDataSet(departments, employees);
    }

    private TestDataSet createInactiveDepartments() {
        List<Department> departments = Arrays.asList(
                TestDataBuilder.department().hr().inactive().buildEntity(),
                TestDataBuilder.department().it().inactive().buildEntity()
        ).stream()
        .map(departmentRepository::save)
        .toList();

        return new TestDataSet(departments, List.of());
    }

    private TestDataSet createVeteranEmployees() {
        List<Department> departments = List.of(
                departmentRepository.save(TestDataBuilder.department().hr().buildEntity())
        );

        List<Employee> employees = IntStream.range(0, 5)
                .mapToObj(i -> TestDataBuilder.employee()
                        .veteran()
                        .withFirstName("Veteran" + i)
                        .withEmail("veteran" + i + "@company.com")
                        .withDepartment(departments.get(0))
                        .buildEntity())
                .map(employeeRepository::save)
                .toList();

        return new TestDataSet(departments, employees);
    }

    private TestDataSet createNewEmployees() {
        List<Department> departments = List.of(
                departmentRepository.save(TestDataBuilder.department().it().buildEntity())
        );

        List<Employee> employees = IntStream.range(0, 5)
                .mapToObj(i -> TestDataBuilder.employee()
                        .newHire()
                        .withFirstName("NewHire" + i)
                        .withEmail("newhire" + i + "@company.com")
                        .withDepartment(departments.get(0))
                        .buildEntity())
                .map(employeeRepository::save)
                .toList();

        return new TestDataSet(departments, employees);
    }

    /**
     * Container for test data sets.
     */
    public static class TestDataSet {
        private final List<Department> departments;
        private final List<Employee> employees;

        public TestDataSet(List<Department> departments, List<Employee> employees) {
            this.departments = List.copyOf(departments);
            this.employees = List.copyOf(employees);
        }

        public List<Department> getDepartments() {
            return departments;
        }

        public List<Employee> getEmployees() {
            return employees;
        }

        public Department getFirstDepartment() {
            return departments.isEmpty() ? null : departments.get(0);
        }

        public Employee getFirstEmployee() {
            return employees.isEmpty() ? null : employees.get(0);
        }

        public int getDepartmentCount() {
            return departments.size();
        }

        public int getEmployeeCount() {
            return employees.size();
        }

        public Map<String, Object> getStatistics() {
            return Map.of(
                    "departmentCount", getDepartmentCount(),
                    "employeeCount", getEmployeeCount(),
                    "activeDepartments", departments.stream().mapToInt(d -> d.getActive() ? 1 : 0).sum(),
                    "activeEmployees", employees.stream().mapToInt(e -> e.getActive() ? 1 : 0).sum()
            );
        }
    }
}