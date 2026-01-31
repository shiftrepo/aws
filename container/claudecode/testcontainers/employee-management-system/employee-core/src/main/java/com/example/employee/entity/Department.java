package com.example.employee.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Department entity representing organizational departments.
 *
 * Demonstrates JPA entity relationships, validation, and complex queries
 * for testing purposes. Each department can have multiple employees.
 */
@Entity
@Table(name = "departments")
public class Department extends BaseEntity {

    @NotBlank(message = "Department name is required")
    @Size(min = 2, max = 100, message = "Department name must be between 2 and 100 characters")
    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @NotBlank(message = "Department code is required")
    @Size(min = 2, max = 10, message = "Department code must be between 2 and 10 characters")
    @Column(name = "code", nullable = false, unique = true, length = 10)
    private String code;

    @NotNull(message = "Department budget is required")
    @Positive(message = "Department budget must be positive")
    @Column(name = "budget", nullable = false, precision = 12, scale = 2)
    private BigDecimal budget;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    @Column(name = "description", length = 500)
    private String description;

    @Column(name = "active", nullable = false)
    private Boolean active = true;

    @OneToMany(mappedBy = "department", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Employee> employees = new ArrayList<>();

    // Constructors
    public Department() {}

    public Department(String name, String code, BigDecimal budget) {
        this.name = name;
        this.code = code;
        this.budget = budget;
    }

    public Department(String name, String code, BigDecimal budget, String description) {
        this(name, code, budget);
        this.description = description;
    }

    // Business methods
    public int getEmployeeCount() {
        return employees != null ? employees.size() : 0;
    }

    public BigDecimal getAverageSalaryBudgetPerEmployee() {
        int count = getEmployeeCount();
        if (count == 0) {
            return BigDecimal.ZERO;
        }
        return budget.divide(BigDecimal.valueOf(count), 2, BigDecimal.ROUND_HALF_UP);
    }

    public void addEmployee(Employee employee) {
        if (employees == null) {
            employees = new ArrayList<>();
        }
        employees.add(employee);
        employee.setDepartment(this);
    }

    public void removeEmployee(Employee employee) {
        if (employees != null) {
            employees.remove(employee);
            employee.setDepartment(null);
        }
    }

    // Getters and setters
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public BigDecimal getBudget() {
        return budget;
    }

    public void setBudget(BigDecimal budget) {
        this.budget = budget;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean getActive() {
        return active;
    }

    public void setActive(Boolean active) {
        this.active = active;
    }

    public List<Employee> getEmployees() {
        return employees;
    }

    public void setEmployees(List<Employee> employees) {
        this.employees = employees;
    }

    @Override
    public String toString() {
        return "Department{" +
               "id=" + getId() +
               ", name='" + name + '\'' +
               ", code='" + code + '\'' +
               ", budget=" + budget +
               ", description='" + description + '\'' +
               ", active=" + active +
               ", employeeCount=" + getEmployeeCount() +
               '}';
    }
}