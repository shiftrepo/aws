package com.example.employee.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

import java.time.LocalDate;
import java.time.Period;

/**
 * Employee entity representing company employees.
 *
 * Demonstrates JPA entity relationships, validation, custom queries,
 * and business logic for comprehensive testing scenarios.
 */
@Entity
@Table(name = "employees")
@NamedQueries({
    @NamedQuery(
        name = "Employee.findByDepartment_Code",
        query = "SELECT e FROM Employee e JOIN e.department d WHERE d.code = :departmentCode"
    ),
    @NamedQuery(
        name = "Employee.findByHireDateBetween",
        query = "SELECT e FROM Employee e WHERE e.hireDate BETWEEN :startDate AND :endDate ORDER BY e.hireDate"
    )
})
public class Employee extends BaseEntity {

    @NotBlank(message = "First name is required")
    @Size(min = 1, max = 50, message = "First name must be between 1 and 50 characters")
    @Column(name = "first_name", nullable = false, length = 50)
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Size(min = 1, max = 50, message = "Last name must be between 1 and 50 characters")
    @Column(name = "last_name", nullable = false, length = 50)
    private String lastName;

    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    @Size(max = 100, message = "Email must not exceed 100 characters")
    @Column(name = "email", nullable = false, unique = true, length = 100)
    private String email;

    @NotNull(message = "Hire date is required")
    @PastOrPresent(message = "Hire date cannot be in the future")
    @Column(name = "hire_date", nullable = false)
    private LocalDate hireDate;

    @Size(max = 15, message = "Phone number must not exceed 15 characters")
    @Pattern(regexp = "^[+]?[0-9\\-\\s\\(\\)]*$", message = "Invalid phone number format")
    @Column(name = "phone_number", length = 15)
    private String phoneNumber;

    @Size(max = 200, message = "Address must not exceed 200 characters")
    @Column(name = "address", length = 200)
    private String address;

    @Column(name = "active", nullable = false)
    private Boolean active = true;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id", foreignKey = @ForeignKey(name = "fk_employee_department"))
    private Department department;

    // Constructors
    public Employee() {}

    public Employee(String firstName, String lastName, String email, LocalDate hireDate) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.hireDate = hireDate;
    }

    public Employee(String firstName, String lastName, String email, LocalDate hireDate, Department department) {
        this(firstName, lastName, email, hireDate);
        this.department = department;
    }

    // Business methods
    public String getFullName() {
        return firstName + " " + lastName;
    }

    public int getYearsOfService() {
        if (hireDate == null) {
            return 0;
        }
        return Period.between(hireDate, LocalDate.now()).getYears();
    }

    public boolean isNewEmployee() {
        return getYearsOfService() < 1;
    }

    public boolean isVeteranEmployee() {
        return getYearsOfService() >= 5;
    }

    public String getDepartmentName() {
        return department != null ? department.getName() : "No Department";
    }

    public String getDepartmentCode() {
        return department != null ? department.getCode() : null;
    }

    // Getters and setters
    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
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

    public Department getDepartment() {
        return department;
    }

    public void setDepartment(Department department) {
        this.department = department;
    }

    @Override
    public String toString() {
        return "Employee{" +
               "id=" + getId() +
               ", firstName='" + firstName + '\'' +
               ", lastName='" + lastName + '\'' +
               ", email='" + email + '\'' +
               ", hireDate=" + hireDate +
               ", phoneNumber='" + phoneNumber + '\'' +
               ", address='" + address + '\'' +
               ", active=" + active +
               ", department=" + (department != null ? department.getName() : "null") +
               ", yearsOfService=" + getYearsOfService() +
               '}';
    }
}