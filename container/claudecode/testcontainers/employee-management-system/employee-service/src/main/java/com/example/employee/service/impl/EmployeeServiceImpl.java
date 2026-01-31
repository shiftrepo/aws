package com.example.employee.service.impl;

import com.example.employee.dto.EmployeeDto;
import com.example.employee.entity.Department;
import com.example.employee.entity.Employee;
import com.example.employee.repository.DepartmentRepository;
import com.example.employee.repository.EmployeeRepository;
import com.example.employee.service.EmployeeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Implementation of EmployeeService interface.
 *
 * Provides comprehensive business logic for employee operations with
 * transaction management, validation, and error handling for testing scenarios.
 */
@Service
@Transactional
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;

    @Autowired
    public EmployeeServiceImpl(EmployeeRepository employeeRepository,
                              DepartmentRepository departmentRepository) {
        this.employeeRepository = employeeRepository;
        this.departmentRepository = departmentRepository;
    }

    @Override
    public EmployeeDto createEmployee(EmployeeDto employeeDto) {
        validateEmployeeDto(employeeDto);

        if (!isEmailUnique(employeeDto.getEmail())) {
            throw new IllegalArgumentException("Email already exists: " + employeeDto.getEmail());
        }

        Employee employee = convertToEntity(employeeDto);
        if (employee.getActive() == null) {
            employee.setActive(true);
        }

        // Set department if provided
        if (employeeDto.getDepartmentId() != null) {
            Department department = departmentRepository.findById(employeeDto.getDepartmentId())
                    .orElseThrow(() -> new IllegalArgumentException("Department not found with ID: " + employeeDto.getDepartmentId()));
            employee.setDepartment(department);
        }

        Employee savedEmployee = employeeRepository.save(employee);
        return convertToDto(savedEmployee);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<EmployeeDto> getEmployeeById(Long id) {
        if (id == null) {
            return Optional.empty();
        }
        return employeeRepository.findById(id)
                .map(this::convertToDto);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<EmployeeDto> getEmployeeByEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            return Optional.empty();
        }
        return employeeRepository.findByEmail(email.trim())
                .map(this::convertToDto);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getAllEmployees() {
        return employeeRepository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getActiveEmployees() {
        return employeeRepository.findByActiveTrue().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    public EmployeeDto updateEmployee(Long id, EmployeeDto employeeDto) {
        if (id == null) {
            throw new IllegalArgumentException("Employee ID cannot be null");
        }

        Employee existingEmployee = employeeRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Employee not found with ID: " + id));

        validateEmployeeDto(employeeDto);

        if (!isEmailUnique(employeeDto.getEmail(), id)) {
            throw new IllegalArgumentException("Email already exists: " + employeeDto.getEmail());
        }

        updateEmployeeFields(existingEmployee, employeeDto);
        Employee savedEmployee = employeeRepository.save(existingEmployee);
        return convertToDto(savedEmployee);
    }

    @Override
    public boolean deleteEmployee(Long id) {
        if (id == null) {
            return false;
        }

        Optional<Employee> employee = employeeRepository.findById(id);
        if (employee.isEmpty()) {
            return false;
        }

        if (!canDeleteEmployee(id)) {
            throw new IllegalStateException("Cannot delete employee due to business constraints");
        }

        employeeRepository.deleteById(id);
        return true;
    }

    @Override
    public EmployeeDto assignEmployeeToDepartment(Long employeeId, Long departmentId) {
        if (employeeId == null || departmentId == null) {
            throw new IllegalArgumentException("Employee ID and Department ID cannot be null");
        }

        Employee employee = employeeRepository.findById(employeeId)
                .orElseThrow(() -> new IllegalArgumentException("Employee not found with ID: " + employeeId));

        Department department = departmentRepository.findById(departmentId)
                .orElseThrow(() -> new IllegalArgumentException("Department not found with ID: " + departmentId));

        if (!canAssignToDepartment(employeeId, departmentId)) {
            throw new IllegalStateException("Cannot assign employee to department");
        }

        employee.setDepartment(department);
        Employee savedEmployee = employeeRepository.save(employee);
        return convertToDto(savedEmployee);
    }

    @Override
    public EmployeeDto removeEmployeeFromDepartment(Long employeeId) {
        if (employeeId == null) {
            throw new IllegalArgumentException("Employee ID cannot be null");
        }

        Employee employee = employeeRepository.findById(employeeId)
                .orElseThrow(() -> new IllegalArgumentException("Employee not found with ID: " + employeeId));

        employee.setDepartment(null);
        Employee savedEmployee = employeeRepository.save(employee);
        return convertToDto(savedEmployee);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesByDepartment(Long departmentId) {
        if (departmentId == null) {
            return List.of();
        }
        return employeeRepository.findByDepartmentId(departmentId).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesByDepartmentCode(String departmentCode) {
        if (departmentCode == null || departmentCode.trim().isEmpty()) {
            return List.of();
        }
        return employeeRepository.findByDepartment_Code(departmentCode.trim()).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesWithoutDepartment() {
        return employeeRepository.findActiveEmployeesWithoutDepartment().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    public boolean transferEmployee(Long employeeId, Long newDepartmentId) {
        if (employeeId == null || newDepartmentId == null) {
            return false;
        }

        if (!canTransferEmployee(employeeId, newDepartmentId)) {
            return false;
        }

        try {
            assignEmployeeToDepartment(employeeId, newDepartmentId);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public boolean activateEmployee(Long id) {
        if (id == null) {
            return false;
        }

        return employeeRepository.findById(id)
                .map(employee -> {
                    employee.setActive(true);
                    employeeRepository.save(employee);
                    return true;
                })
                .orElse(false);
    }

    @Override
    public boolean deactivateEmployee(Long id) {
        if (id == null) {
            return false;
        }

        return employeeRepository.findById(id)
                .map(employee -> {
                    employee.setActive(false);
                    employeeRepository.save(employee);
                    return true;
                })
                .orElse(false);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> searchEmployees(String searchTerm) {
        if (searchTerm == null || searchTerm.trim().isEmpty()) {
            return List.of();
        }

        String trimmedTerm = searchTerm.trim();
        return employeeRepository.findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(
                trimmedTerm, trimmedTerm).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesHiredBetween(LocalDate startDate, LocalDate endDate) {
        if (startDate == null || endDate == null) {
            return List.of();
        }
        return employeeRepository.findByHireDateBetween(startDate, endDate).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesHiredInYear(int year) {
        return employeeRepository.findEmployeesHiredInYear(year).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getNewEmployees() {
        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        return employeeRepository.findByHireDateAfter(oneYearAgo).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getVeteranEmployees() {
        return getEmployeesWithMinYearsOfService(5);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesWithMinYearsOfService(int years) {
        return employeeRepository.findEmployeesWithMinYearsOfService(years).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public long getActiveEmployeeCount() {
        return employeeRepository.countByActiveTrue();
    }

    @Override
    @Transactional(readOnly = true)
    public long getEmployeeCountByDepartment(Long departmentId) {
        if (departmentId == null) {
            return 0;
        }
        return employeeRepository.countByDepartmentId(departmentId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Object[]> getHiringStatisticsByYear() {
        return employeeRepository.getHiringStatisticsByYear();
    }

    @Override
    @Transactional(readOnly = true)
    public List<Object[]> getDepartmentEmployeeCounts() {
        return employeeRepository.getDepartmentEmployeeCountsOrdered();
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isEmailUnique(String email) {
        return isEmailUnique(email, null);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isEmailUnique(String email, Long excludeId) {
        if (email == null || email.trim().isEmpty()) {
            return false;
        }

        Optional<Employee> existing = employeeRepository.findByEmail(email.trim());
        return existing.isEmpty() || (excludeId != null && existing.get().getId().equals(excludeId));
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isEmployeeActive(Long id) {
        if (id == null) {
            return false;
        }

        return employeeRepository.findById(id)
                .map(Employee::getActive)
                .orElse(false);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean canDeleteEmployee(Long id) {
        if (id == null) {
            return false;
        }

        // Add business rules for employee deletion
        // For now, allow deletion if employee exists
        return employeeRepository.existsById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean canAssignToDepartment(Long employeeId, Long departmentId) {
        if (employeeId == null || departmentId == null) {
            return false;
        }

        boolean employeeExists = employeeRepository.existsById(employeeId);
        Optional<Department> department = departmentRepository.findById(departmentId);

        return employeeExists && department.isPresent() && department.get().getActive();
    }

    @Override
    @Transactional(readOnly = true)
    public boolean canTransferEmployee(Long employeeId, Long newDepartmentId) {
        return canAssignToDepartment(employeeId, newDepartmentId);
    }

    @Override
    public int activateEmployees(List<Long> employeeIds) {
        if (employeeIds == null || employeeIds.isEmpty()) {
            return 0;
        }

        int count = 0;
        for (Long id : employeeIds) {
            if (activateEmployee(id)) {
                count++;
            }
        }
        return count;
    }

    @Override
    public int deactivateEmployees(List<Long> employeeIds) {
        if (employeeIds == null || employeeIds.isEmpty()) {
            return 0;
        }

        int count = 0;
        for (Long id : employeeIds) {
            if (deactivateEmployee(id)) {
                count++;
            }
        }
        return count;
    }

    @Override
    public int transferEmployees(List<Long> employeeIds, Long newDepartmentId) {
        if (employeeIds == null || employeeIds.isEmpty() || newDepartmentId == null) {
            return 0;
        }

        int count = 0;
        for (Long id : employeeIds) {
            if (transferEmployee(id, newDepartmentId)) {
                count++;
            }
        }
        return count;
    }

    @Override
    public int removeAllFromDepartment(Long departmentId) {
        if (departmentId == null) {
            return 0;
        }

        return employeeRepository.removeDepartmentAssignment(departmentId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesInActiveDepartments() {
        return employeeRepository.findActiveEmployeesInActiveDepartments().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> getEmployeesInDepartmentsWithMinBudget(java.math.BigDecimal minBudget) {
        if (minBudget == null) {
            return List.of();
        }
        return employeeRepository.findEmployeesInDepartmentsWithMinBudget(minBudget).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmployeeDto> searchEmployeesFullText(String searchText) {
        if (searchText == null || searchText.trim().isEmpty()) {
            return List.of();
        }
        return employeeRepository.searchEmployeesFullText(searchText.trim()).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    // Helper methods
    private void validateEmployeeDto(EmployeeDto dto) {
        if (dto == null) {
            throw new IllegalArgumentException("Employee data cannot be null");
        }
        if (dto.getFirstName() == null || dto.getFirstName().trim().isEmpty()) {
            throw new IllegalArgumentException("First name is required");
        }
        if (dto.getLastName() == null || dto.getLastName().trim().isEmpty()) {
            throw new IllegalArgumentException("Last name is required");
        }
        if (dto.getEmail() == null || dto.getEmail().trim().isEmpty()) {
            throw new IllegalArgumentException("Email is required");
        }
        if (dto.getHireDate() == null) {
            throw new IllegalArgumentException("Hire date is required");
        }
        if (dto.getHireDate().isAfter(LocalDate.now())) {
            throw new IllegalArgumentException("Hire date cannot be in the future");
        }
    }

    private Employee convertToEntity(EmployeeDto dto) {
        Employee employee = new Employee();
        employee.setFirstName(dto.getFirstName().trim());
        employee.setLastName(dto.getLastName().trim());
        employee.setEmail(dto.getEmail().trim().toLowerCase());
        employee.setHireDate(dto.getHireDate());
        employee.setPhoneNumber(dto.getPhoneNumber());
        employee.setAddress(dto.getAddress());
        employee.setActive(dto.getActive());
        return employee;
    }

    private EmployeeDto convertToDto(Employee employee) {
        EmployeeDto dto = new EmployeeDto();
        dto.setId(employee.getId());
        dto.setFirstName(employee.getFirstName());
        dto.setLastName(employee.getLastName());
        dto.setEmail(employee.getEmail());
        dto.setHireDate(employee.getHireDate());
        dto.setPhoneNumber(employee.getPhoneNumber());
        dto.setAddress(employee.getAddress());
        dto.setActive(employee.getActive());
        dto.setCreatedAt(employee.getCreatedAt());
        dto.setModifiedAt(employee.getModifiedAt());

        // Set department information
        if (employee.getDepartment() != null) {
            dto.setDepartmentId(employee.getDepartment().getId());
            dto.setDepartmentName(employee.getDepartment().getName());
            dto.setDepartmentCode(employee.getDepartment().getCode());
        }

        // Ensure computed fields are updated
        dto.updateComputedFields();

        return dto;
    }

    private void updateEmployeeFields(Employee employee, EmployeeDto dto) {
        employee.setFirstName(dto.getFirstName().trim());
        employee.setLastName(dto.getLastName().trim());
        employee.setEmail(dto.getEmail().trim().toLowerCase());
        employee.setHireDate(dto.getHireDate());
        employee.setPhoneNumber(dto.getPhoneNumber());
        employee.setAddress(dto.getAddress());
        if (dto.getActive() != null) {
            employee.setActive(dto.getActive());
        }

        // Update department if provided
        if (dto.getDepartmentId() != null) {
            Department department = departmentRepository.findById(dto.getDepartmentId())
                    .orElseThrow(() -> new IllegalArgumentException("Department not found with ID: " + dto.getDepartmentId()));
            employee.setDepartment(department);
        } else if (dto.getDepartmentId() == null && employee.getDepartment() != null) {
            // If departmentId is explicitly set to null, remove the department assignment
            employee.setDepartment(null);
        }
    }
}