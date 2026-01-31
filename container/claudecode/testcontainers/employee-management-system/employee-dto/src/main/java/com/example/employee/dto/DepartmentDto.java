package com.example.employee.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Data Transfer Object for Department entity.
 *
 * Used for API requests/responses and demonstrates validation
 * for testing REST endpoints and data serialization.
 */
public class DepartmentDto {

    private Long id;

    @NotBlank(message = "Department name is required")
    @Size(min = 2, max = 100, message = "Department name must be between 2 and 100 characters")
    private String name;

    @NotBlank(message = "Department code is required")
    @Size(min = 2, max = 10, message = "Department code must be between 2 and 10 characters")
    private String code;

    @NotNull(message = "Department budget is required")
    @Positive(message = "Department budget must be positive")
    private BigDecimal budget;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    private String description;

    private Boolean active;

    private Integer employeeCount;

    private LocalDateTime createdAt;

    private LocalDateTime modifiedAt;

    // Constructors
    public DepartmentDto() {}

    public DepartmentDto(String name, String code, BigDecimal budget) {
        this.name = name;
        this.code = code;
        this.budget = budget;
        this.active = true;
    }

    public DepartmentDto(Long id, String name, String code, BigDecimal budget, String description,
                        Boolean active, Integer employeeCount) {
        this.id = id;
        this.name = name;
        this.code = code;
        this.budget = budget;
        this.description = description;
        this.active = active;
        this.employeeCount = employeeCount;
    }

    // Business methods
    public BigDecimal getAverageBudgetPerEmployee() {
        if (employeeCount == null || employeeCount == 0 || budget == null) {
            return BigDecimal.ZERO;
        }
        return budget.divide(BigDecimal.valueOf(employeeCount), 2, BigDecimal.ROUND_HALF_UP);
    }

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

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

    public Integer getEmployeeCount() {
        return employeeCount;
    }

    public void setEmployeeCount(Integer employeeCount) {
        this.employeeCount = employeeCount;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getModifiedAt() {
        return modifiedAt;
    }

    public void setModifiedAt(LocalDateTime modifiedAt) {
        this.modifiedAt = modifiedAt;
    }

    @Override
    public String toString() {
        return "DepartmentDto{" +
               "id=" + id +
               ", name='" + name + '\'' +
               ", code='" + code + '\'' +
               ", budget=" + budget +
               ", description='" + description + '\'' +
               ", active=" + active +
               ", employeeCount=" + employeeCount +
               '}';
    }
}