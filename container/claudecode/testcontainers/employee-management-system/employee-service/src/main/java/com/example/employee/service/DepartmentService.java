package com.example.employee.service;

import com.example.employee.dto.DepartmentDto;
import com.example.employee.entity.Department;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Service interface for Department business logic.
 *
 * Defines the contract for department operations and business rules.
 * Provides methods for comprehensive testing of service layer functionality.
 */
public interface DepartmentService {

    // Basic CRUD operations
    DepartmentDto createDepartment(DepartmentDto departmentDto);

    Optional<DepartmentDto> getDepartmentById(Long id);

    Optional<DepartmentDto> getDepartmentByCode(String code);

    List<DepartmentDto> getAllDepartments();

    List<DepartmentDto> getActiveDepartments();

    DepartmentDto updateDepartment(Long id, DepartmentDto departmentDto);

    boolean deleteDepartment(Long id);

    // Business operations
    boolean activateDepartment(Long id);

    boolean deactivateDepartment(Long id);

    boolean transferAllEmployees(Long fromDepartmentId, Long toDepartmentId);

    List<DepartmentDto> getDepartmentsWithEmployeeCount();

    List<DepartmentDto> getDepartmentsWithMinEmployees(int minEmployees);

    List<DepartmentDto> getDepartmentsWithBudgetRange(BigDecimal minBudget, BigDecimal maxBudget);

    // Search operations
    List<DepartmentDto> searchDepartmentsByName(String namePattern);

    List<DepartmentDto> getDepartmentsWithAboveAverageBudget();

    // Statistics operations
    long getActiveDepartmentCount();

    BigDecimal getTotalActiveBudget();

    BigDecimal getAverageActiveBudget();

    // Validation operations
    boolean isDepartmentCodeUnique(String code);

    boolean isDepartmentCodeUnique(String code, Long excludeId);

    boolean canDeleteDepartment(Long id);

    boolean hasActiveEmployees(Long id);

    // Batch operations
    int activateDepartments(List<Long> departmentIds);

    int deactivateDepartments(List<Long> departmentIds);

    int deleteInactiveDepartmentsWithoutEmployees();
}