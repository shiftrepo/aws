package com.example.employee.dto;

import jakarta.validation.constraints.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;

/**
 * Data Transfer Object for Employee entity.
 *
 * Used for API requests/responses and demonstrates validation,
 * computed properties, and data transformation for testing scenarios.
 */
public class EmployeeDto {

    private Long id;

    @NotBlank(message = "First name is required")
    @Size(min = 1, max = 50, message = "First name must be between 1 and 50 characters")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Size(min = 1, max = 50, message = "Last name must be between 1 and 50 characters")
    private String lastName;

    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    @Size(max = 100, message = "Email must not exceed 100 characters")
    private String email;

    @NotNull(message = "Hire date is required")
    @PastOrPresent(message = "Hire date cannot be in the future")
    private LocalDate hireDate;

    @Size(max = 15, message = "Phone number must not exceed 15 characters")
    @Pattern(regexp = "^[+]?[0-9\\-\\s\\(\\)]*$", message = "Invalid phone number format")
    private String phoneNumber;

    @Size(max = 200, message = "Address must not exceed 200 characters")
    private String address;

    private Boolean active;

    private Long departmentId;

    private String departmentName;

    private String departmentCode;

    private LocalDateTime createdAt;

    private LocalDateTime modifiedAt;

    // Computed properties (for testing calculated fields)
    private String fullName;

    private Integer yearsOfService;

    private Boolean isNewEmployee;

    private Boolean isVeteranEmployee;

    // Constructors
    public EmployeeDto() {}

    public EmployeeDto(String firstName, String lastName, String email, LocalDate hireDate) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.hireDate = hireDate;
        this.active = true;
        computeFields();
    }

    public EmployeeDto(Long id, String firstName, String lastName, String email, LocalDate hireDate,
                      String phoneNumber, String address, Boolean active, Long departmentId,
                      String departmentName, String departmentCode) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.hireDate = hireDate;
        this.phoneNumber = phoneNumber;
        this.address = address;
        this.active = active;
        this.departmentId = departmentId;
        this.departmentName = departmentName;
        this.departmentCode = departmentCode;
        computeFields();
    }

    // Business methods
    private void computeFields() {
        this.fullName = (firstName != null ? firstName : "") + " " + (lastName != null ? lastName : "");
        this.yearsOfService = hireDate != null ? Period.between(hireDate, LocalDate.now()).getYears() : 0;
        this.isNewEmployee = yearsOfService < 1;
        this.isVeteranEmployee = yearsOfService >= 5;
    }

    public void updateComputedFields() {
        computeFields();
    }

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
        computeFields();
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
        computeFields();
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public LocalDate getHireDate() {
        return hireDate;
    }

    public void setHireDate(LocalDate hireDate) {
        this.hireDate = hireDate;
        computeFields();
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public Boolean getActive() {
        return active;
    }

    public void setActive(Boolean active) {
        this.active = active;
    }

    public Long getDepartmentId() {
        return departmentId;
    }

    public void setDepartmentId(Long departmentId) {
        this.departmentId = departmentId;
    }

    public String getDepartmentName() {
        return departmentName;
    }

    public void setDepartmentName(String departmentName) {
        this.departmentName = departmentName;
    }

    public String getDepartmentCode() {
        return departmentCode;
    }

    public void setDepartmentCode(String departmentCode) {
        this.departmentCode = departmentCode;
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

    public String getFullName() {
        return fullName;
    }

    public Integer getYearsOfService() {
        return yearsOfService;
    }

    public Boolean getIsNewEmployee() {
        return isNewEmployee;
    }

    public Boolean getIsVeteranEmployee() {
        return isVeteranEmployee;
    }

    @Override
    public String toString() {
        return "EmployeeDto{" +
               "id=" + id +
               ", firstName='" + firstName + '\'' +
               ", lastName='" + lastName + '\'' +
               ", email='" + email + '\'' +
               ", hireDate=" + hireDate +
               ", phoneNumber='" + phoneNumber + '\'' +
               ", address='" + address + '\'' +
               ", active=" + active +
               ", departmentId=" + departmentId +
               ", departmentName='" + departmentName + '\'' +
               ", departmentCode='" + departmentCode + '\'' +
               ", fullName='" + fullName + '\'' +
               ", yearsOfService=" + yearsOfService +
               ", isNewEmployee=" + isNewEmployee +
               ", isVeteranEmployee=" + isVeteranEmployee +
               '}';
    }
}