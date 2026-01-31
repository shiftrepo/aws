package com.example.employee.testutils;

import com.example.employee.entity.Department;
import com.example.employee.entity.Employee;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Builder utility for creating test data objects.
 *
 * Provides fluent API for building test entities and DTOs with
 * sensible defaults and easy customization. Uses the Builder pattern
 * to create consistent test data across different test scenarios.
 */
public class TestDataBuilder {

    // Counters for generating unique values
    private static final AtomicLong departmentCounter = new AtomicLong(1);
    private static final AtomicLong employeeCounter = new AtomicLong(1);

    /**
     * Builder for Department entities.
     */
    public static class DepartmentBuilder {
        private Long id;
        private String name;
        private String code;
        private BigDecimal budget;
        private String description;
        private Boolean active = true;

        public DepartmentBuilder() {
            long counter = departmentCounter.getAndIncrement();
            this.name = "Department " + counter;
            this.code = "DEPT" + counter;
            this.budget = new BigDecimal("1000000.00");
            this.description = "Test department " + counter;
        }

        public DepartmentBuilder withId(Long id) {
            this.id = id;
            return this;
        }

        public DepartmentBuilder withName(String name) {
            this.name = name;
            return this;
        }

        public DepartmentBuilder withCode(String code) {
            this.code = code;
            return this;
        }

        public DepartmentBuilder withBudget(BigDecimal budget) {
            this.budget = budget;
            return this;
        }

        public DepartmentBuilder withBudget(double budget) {
            this.budget = BigDecimal.valueOf(budget);
            return this;
        }

        public DepartmentBuilder withDescription(String description) {
            this.description = description;
            return this;
        }

        public DepartmentBuilder withActive(Boolean active) {
            this.active = active;
            return this;
        }

        public DepartmentBuilder inactive() {
            this.active = false;
            return this;
        }

        public DepartmentBuilder hr() {
            return withName("Human Resources")
                    .withCode("HR")
                    .withBudget(1200000.00)
                    .withDescription("Human Resources Department");
        }

        public DepartmentBuilder it() {
            return withName("Information Technology")
                    .withCode("IT")
                    .withBudget(2500000.00)
                    .withDescription("Information Technology Department");
        }

        public DepartmentBuilder finance() {
            return withName("Finance")
                    .withCode("FIN")
                    .withBudget(1800000.00)
                    .withDescription("Finance Department");
        }

        public DepartmentBuilder marketing() {
            return withName("Marketing")
                    .withCode("MKT")
                    .withBudget(900000.00)
                    .withDescription("Marketing Department");
        }

        public Department buildEntity() {
            Department department = new Department(name, code, budget, description);
            if (id != null) {
                // Note: In real scenarios, you might use reflection or
                // a test-specific constructor to set the ID
            }
            department.setActive(active);
            return department;
        }

    }

    /**
     * Builder for Employee entities.
     */
    public static class EmployeeBuilder {
        private Long id;
        private String firstName;
        private String lastName;
        private String email;
        private LocalDate hireDate;
        private String phoneNumber;
        private String address;
        private Boolean active = true;
        private Department department;
        private Long departmentId;

        public EmployeeBuilder() {
            long counter = employeeCounter.getAndIncrement();
            this.firstName = "FirstName" + counter;
            this.lastName = "LastName" + counter;
            this.email = "employee" + counter + "@company.com";
            this.hireDate = LocalDate.now().minusDays(counter * 30);
            this.phoneNumber = "+1-555-" + String.format("%04d", counter);
            this.address = counter + " Test Street, Test City, TS";
        }

        public EmployeeBuilder withId(Long id) {
            this.id = id;
            return this;
        }

        public EmployeeBuilder withFirstName(String firstName) {
            this.firstName = firstName;
            return this;
        }

        public EmployeeBuilder withLastName(String lastName) {
            this.lastName = lastName;
            return this;
        }

        public EmployeeBuilder withName(String firstName, String lastName) {
            this.firstName = firstName;
            this.lastName = lastName;
            return this;
        }

        public EmployeeBuilder withEmail(String email) {
            this.email = email;
            return this;
        }

        public EmployeeBuilder withHireDate(LocalDate hireDate) {
            this.hireDate = hireDate;
            return this;
        }

        public EmployeeBuilder withPhoneNumber(String phoneNumber) {
            this.phoneNumber = phoneNumber;
            return this;
        }

        public EmployeeBuilder withAddress(String address) {
            this.address = address;
            return this;
        }

        public EmployeeBuilder withActive(Boolean active) {
            this.active = active;
            return this;
        }

        public EmployeeBuilder inactive() {
            this.active = false;
            return this;
        }

        public EmployeeBuilder withDepartment(Department department) {
            this.department = department;
            this.departmentId = department != null ? department.getId() : null;
            return this;
        }

        public EmployeeBuilder withDepartmentId(Long departmentId) {
            this.departmentId = departmentId;
            return this;
        }

        public EmployeeBuilder newHire() {
            return withHireDate(LocalDate.now().minusDays(30));
        }

        public EmployeeBuilder veteran() {
            return withHireDate(LocalDate.now().minusYears(10));
        }

        public EmployeeBuilder hiredInYear(int year) {
            return withHireDate(LocalDate.of(year, 6, 15));
        }

        public EmployeeBuilder johnDoe() {
            return withName("John", "Doe")
                    .withEmail("john.doe@company.com")
                    .withPhoneNumber("+1-555-0101")
                    .withAddress("123 Main St, City, State");
        }

        public EmployeeBuilder janeSmith() {
            return withName("Jane", "Smith")
                    .withEmail("jane.smith@company.com")
                    .withPhoneNumber("+1-555-0102")
                    .withAddress("456 Oak Ave, City, State");
        }

        public Employee buildEntity() {
            Employee employee = new Employee(firstName, lastName, email, hireDate);
            if (id != null) {
                // Note: In real scenarios, you might use reflection to set the ID
            }
            employee.setPhoneNumber(phoneNumber);
            employee.setAddress(address);
            employee.setActive(active);
            employee.setDepartment(department);
            return employee;
        }

    }

    // Factory methods for builders
    public static DepartmentBuilder department() {
        return new DepartmentBuilder();
    }

    public static EmployeeBuilder employee() {
        return new EmployeeBuilder();
    }

    // Preset configurations for common test scenarios
    public static DepartmentBuilder hrDepartment() {
        return department().hr();
    }

    public static DepartmentBuilder itDepartment() {
        return department().it();
    }

    public static DepartmentBuilder financeDepartment() {
        return department().finance();
    }

    public static EmployeeBuilder johnDoe() {
        return employee().johnDoe();
    }

    public static EmployeeBuilder janeSmith() {
        return employee().janeSmith();
    }

    public static EmployeeBuilder newEmployee() {
        return employee().newHire();
    }

    public static EmployeeBuilder veteranEmployee() {
        return employee().veteran();
    }

    // Reset counters (useful for test isolation)
    public static void resetCounters() {
        departmentCounter.set(1);
        employeeCounter.set(1);
    }

    // Bulk creation methods
    public static Department[] createDepartments(int count) {
        Department[] departments = new Department[count];
        for (int i = 0; i < count; i++) {
            departments[i] = department().buildEntity();
        }
        return departments;
    }

    public static Employee[] createEmployees(int count) {
        Employee[] employees = new Employee[count];
        for (int i = 0; i < count; i++) {
            employees[i] = employee().buildEntity();
        }
        return employees;
    }

}