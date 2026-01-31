package com.example.employee.service;

import com.example.employee.dto.EmployeeDto;
import com.example.employee.entity.Employee;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Service interface for Employee business logic.
 *
 * Defines the contract for employee operations and business rules.
 * Provides comprehensive methods for testing service layer functionality
 * including transaction management and business logic validation.
 */
public interface EmployeeService {

    // Basic CRUD operations
    EmployeeDto createEmployee(EmployeeDto employeeDto);

    Optional<EmployeeDto> getEmployeeById(Long id);

    Optional<EmployeeDto> getEmployeeByEmail(String email);

    List<EmployeeDto> getAllEmployees();

    List<EmployeeDto> getActiveEmployees();

    EmployeeDto updateEmployee(Long id, EmployeeDto employeeDto);

    boolean deleteEmployee(Long id);

    // Department-related operations
    EmployeeDto assignEmployeeToDepartment(Long employeeId, Long departmentId);

    EmployeeDto removeEmployeeFromDepartment(Long employeeId);

    List<EmployeeDto> getEmployeesByDepartment(Long departmentId);

    List<EmployeeDto> getEmployeesByDepartmentCode(String departmentCode);

    List<EmployeeDto> getEmployeesWithoutDepartment();

    boolean transferEmployee(Long employeeId, Long newDepartmentId);

    // Status operations
    boolean activateEmployee(Long id);

    boolean deactivateEmployee(Long id);

    // Search and filter operations
    List<EmployeeDto> searchEmployees(String searchTerm);

    List<EmployeeDto> getEmployeesHiredBetween(LocalDate startDate, LocalDate endDate);

    List<EmployeeDto> getEmployeesHiredInYear(int year);

    List<EmployeeDto> getNewEmployees();

    List<EmployeeDto> getVeteranEmployees();

    List<EmployeeDto> getEmployeesWithMinYearsOfService(int years);

    // Statistics operations
    long getActiveEmployeeCount();

    long getEmployeeCountByDepartment(Long departmentId);

    List<Object[]> getHiringStatisticsByYear();

    List<Object[]> getDepartmentEmployeeCounts();

    // Validation operations
    boolean isEmailUnique(String email);

    boolean isEmailUnique(String email, Long excludeId);

    boolean isEmployeeActive(Long id);

    boolean canDeleteEmployee(Long id);

    // Business rules validation
    boolean canAssignToDepartment(Long employeeId, Long departmentId);

    boolean canTransferEmployee(Long employeeId, Long newDepartmentId);

    // Batch operations
    int activateEmployees(List<Long> employeeIds);

    int deactivateEmployees(List<Long> employeeIds);

    int transferEmployees(List<Long> employeeIds, Long newDepartmentId);

    int removeAllFromDepartment(Long departmentId);

    // Complex business operations
    List<EmployeeDto> getEmployeesInActiveDepartments();

    List<EmployeeDto> getEmployeesInDepartmentsWithMinBudget(java.math.BigDecimal minBudget);

    // Full-text search operations (for advanced testing)
    List<EmployeeDto> searchEmployeesFullText(String searchText);
}