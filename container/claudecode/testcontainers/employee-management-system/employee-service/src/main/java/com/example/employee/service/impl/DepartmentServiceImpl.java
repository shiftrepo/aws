package com.example.employee.service.impl;

import com.example.employee.dto.DepartmentDto;
import com.example.employee.entity.Department;
import com.example.employee.repository.DepartmentRepository;
import com.example.employee.repository.EmployeeRepository;
import com.example.employee.service.DepartmentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Implementation of DepartmentService interface.
 *
 * Provides business logic for department operations with comprehensive
 * error handling and transaction management for testing scenarios.
 */
@Service
@Transactional
public class DepartmentServiceImpl implements DepartmentService {

    private final DepartmentRepository departmentRepository;
    private final EmployeeRepository employeeRepository;

    @Autowired
    public DepartmentServiceImpl(DepartmentRepository departmentRepository,
                                EmployeeRepository employeeRepository) {
        this.departmentRepository = departmentRepository;
        this.employeeRepository = employeeRepository;
    }

    @Override
    public DepartmentDto createDepartment(DepartmentDto departmentDto) {
        validateDepartmentDto(departmentDto);

        if (!isDepartmentCodeUnique(departmentDto.getCode())) {
            throw new IllegalArgumentException("Department code already exists: " + departmentDto.getCode());
        }

        Department department = convertToEntity(departmentDto);
        if (department.getActive() == null) {
            department.setActive(true);
        }

        Department savedDepartment = departmentRepository.save(department);
        return convertToDto(savedDepartment);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<DepartmentDto> getDepartmentById(Long id) {
        if (id == null) {
            return Optional.empty();
        }
        return departmentRepository.findById(id)
                .map(this::convertToDto);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<DepartmentDto> getDepartmentByCode(String code) {
        if (code == null || code.trim().isEmpty()) {
            return Optional.empty();
        }
        return departmentRepository.findByCode(code.trim())
                .map(this::convertToDto);
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getAllDepartments() {
        return departmentRepository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getActiveDepartments() {
        return departmentRepository.findByActiveTrue().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    public DepartmentDto updateDepartment(Long id, DepartmentDto departmentDto) {
        if (id == null) {
            throw new IllegalArgumentException("Department ID cannot be null");
        }

        Department existingDepartment = departmentRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Department not found with ID: " + id));

        validateDepartmentDto(departmentDto);

        if (!isDepartmentCodeUnique(departmentDto.getCode(), id)) {
            throw new IllegalArgumentException("Department code already exists: " + departmentDto.getCode());
        }

        updateDepartmentFields(existingDepartment, departmentDto);
        Department savedDepartment = departmentRepository.save(existingDepartment);
        return convertToDto(savedDepartment);
    }

    @Override
    public boolean deleteDepartment(Long id) {
        if (id == null) {
            return false;
        }

        Optional<Department> department = departmentRepository.findById(id);
        if (department.isEmpty()) {
            return false;
        }

        if (!canDeleteDepartment(id)) {
            throw new IllegalStateException("Cannot delete department with active employees");
        }

        departmentRepository.deleteById(id);
        return true;
    }

    @Override
    public boolean activateDepartment(Long id) {
        if (id == null) {
            return false;
        }

        return departmentRepository.findById(id)
                .map(department -> {
                    department.setActive(true);
                    departmentRepository.save(department);
                    return true;
                })
                .orElse(false);
    }

    @Override
    public boolean deactivateDepartment(Long id) {
        if (id == null) {
            return false;
        }

        return departmentRepository.findById(id)
                .map(department -> {
                    department.setActive(false);
                    departmentRepository.save(department);
                    return true;
                })
                .orElse(false);
    }

    @Override
    public boolean transferAllEmployees(Long fromDepartmentId, Long toDepartmentId) {
        if (fromDepartmentId == null || toDepartmentId == null) {
            return false;
        }

        if (fromDepartmentId.equals(toDepartmentId)) {
            return false;
        }

        boolean fromExists = departmentRepository.existsById(fromDepartmentId);
        boolean toExists = departmentRepository.existsById(toDepartmentId);

        if (!fromExists || !toExists) {
            return false;
        }

        // This would be implemented with a bulk update query for better performance
        int updatedCount = employeeRepository.updateActiveStatusByDepartmentId(true, toDepartmentId);
        return updatedCount > 0;
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getDepartmentsWithEmployeeCount() {
        return departmentRepository.findAll().stream()
                .map(department -> {
                    DepartmentDto dto = convertToDto(department);
                    dto.setEmployeeCount(department.getEmployeeCount());
                    return dto;
                })
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getDepartmentsWithMinEmployees(int minEmployees) {
        return departmentRepository.findDepartmentsWithMinEmployees(minEmployees).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getDepartmentsWithBudgetRange(BigDecimal minBudget, BigDecimal maxBudget) {
        if (minBudget == null && maxBudget == null) {
            return getAllDepartments();
        }

        if (minBudget != null && maxBudget != null) {
            return departmentRepository.findByBudgetBetween(minBudget, maxBudget).stream()
                    .map(this::convertToDto)
                    .collect(Collectors.toList());
        }

        if (minBudget != null) {
            return departmentRepository.findByBudgetGreaterThan(minBudget).stream()
                    .map(this::convertToDto)
                    .collect(Collectors.toList());
        }

        return departmentRepository.findByBudgetLessThan(maxBudget).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> searchDepartmentsByName(String namePattern) {
        if (namePattern == null || namePattern.trim().isEmpty()) {
            return List.of();
        }

        return departmentRepository.findByNameContainingIgnoreCase(namePattern.trim()).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DepartmentDto> getDepartmentsWithAboveAverageBudget() {
        return departmentRepository.findDepartmentsWithAboveAverageBudget().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public long getActiveDepartmentCount() {
        return departmentRepository.countByActiveTrue();
    }

    @Override
    @Transactional(readOnly = true)
    public BigDecimal getTotalActiveBudget() {
        BigDecimal total = departmentRepository.getTotalActiveDepartmentsBudget();
        return total != null ? total : BigDecimal.ZERO;
    }

    @Override
    @Transactional(readOnly = true)
    public BigDecimal getAverageActiveBudget() {
        BigDecimal average = departmentRepository.getAverageActiveDepartmentBudget();
        return average != null ? average : BigDecimal.ZERO;
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isDepartmentCodeUnique(String code) {
        return isDepartmentCodeUnique(code, null);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isDepartmentCodeUnique(String code, Long excludeId) {
        if (code == null || code.trim().isEmpty()) {
            return false;
        }

        Optional<Department> existing = departmentRepository.findByCode(code.trim());
        return existing.isEmpty() || (excludeId != null && existing.get().getId().equals(excludeId));
    }

    @Override
    @Transactional(readOnly = true)
    public boolean canDeleteDepartment(Long id) {
        if (id == null) {
            return false;
        }

        return !hasActiveEmployees(id);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean hasActiveEmployees(Long id) {
        if (id == null) {
            return false;
        }

        return employeeRepository.countByDepartmentId(id) > 0;
    }

    @Override
    public int activateDepartments(List<Long> departmentIds) {
        if (departmentIds == null || departmentIds.isEmpty()) {
            return 0;
        }

        return departmentRepository.updateActiveStatusByIds(true, departmentIds);
    }

    @Override
    public int deactivateDepartments(List<Long> departmentIds) {
        if (departmentIds == null || departmentIds.isEmpty()) {
            return 0;
        }

        return departmentRepository.updateActiveStatusByIds(false, departmentIds);
    }

    @Override
    public int deleteInactiveDepartmentsWithoutEmployees() {
        return departmentRepository.deleteInactiveDepartmentsWithNoEmployees();
    }

    // Helper methods
    private void validateDepartmentDto(DepartmentDto dto) {
        if (dto == null) {
            throw new IllegalArgumentException("Department data cannot be null");
        }
        if (dto.getName() == null || dto.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("Department name is required");
        }
        if (dto.getCode() == null || dto.getCode().trim().isEmpty()) {
            throw new IllegalArgumentException("Department code is required");
        }
        if (dto.getBudget() == null || dto.getBudget().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Department budget must be positive");
        }
    }

    private Department convertToEntity(DepartmentDto dto) {
        Department department = new Department();
        department.setName(dto.getName().trim());
        department.setCode(dto.getCode().trim().toUpperCase());
        department.setBudget(dto.getBudget());
        department.setDescription(dto.getDescription());
        department.setActive(dto.getActive());
        return department;
    }

    private DepartmentDto convertToDto(Department department) {
        DepartmentDto dto = new DepartmentDto();
        dto.setId(department.getId());
        dto.setName(department.getName());
        dto.setCode(department.getCode());
        dto.setBudget(department.getBudget());
        dto.setDescription(department.getDescription());
        dto.setActive(department.getActive());
        dto.setEmployeeCount(department.getEmployeeCount());
        dto.setCreatedAt(department.getCreatedAt());
        dto.setModifiedAt(department.getModifiedAt());
        return dto;
    }

    private void updateDepartmentFields(Department department, DepartmentDto dto) {
        department.setName(dto.getName().trim());
        department.setCode(dto.getCode().trim().toUpperCase());
        department.setBudget(dto.getBudget());
        department.setDescription(dto.getDescription());
        if (dto.getActive() != null) {
            department.setActive(dto.getActive());
        }
    }
}