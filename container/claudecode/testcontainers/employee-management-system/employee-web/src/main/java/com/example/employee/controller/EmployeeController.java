package com.example.employee.controller;

import com.example.employee.dto.EmployeeDto;
import com.example.employee.service.EmployeeService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * REST Controller for Employee operations.
 *
 * Provides comprehensive CRUD operations, search functionality,
 * and business operations for employees. Demonstrates advanced
 * REST API patterns, validation, and error handling for testing.
 */
@RestController
@RequestMapping("/api/v1/employees")
@Validated
@CrossOrigin(origins = "*", maxAge = 3600)
public class EmployeeController {

    private final EmployeeService employeeService;

    @Autowired
    public EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }

    // Basic CRUD Operations

    @PostMapping
    public ResponseEntity<EmployeeDto> createEmployee(@Valid @RequestBody EmployeeDto employeeDto) {
        try {
            EmployeeDto created = employeeService.createEmployee(employeeDto);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<EmployeeDto> getEmployeeById(@PathVariable @Min(1) Long id) {
        return employeeService.getEmployeeById(id)
                .map(employee -> ResponseEntity.ok().body(employee))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/email/{email}")
    public ResponseEntity<EmployeeDto> getEmployeeByEmail(@PathVariable @NotBlank String email) {
        return employeeService.getEmployeeByEmail(email)
                .map(employee -> ResponseEntity.ok().body(employee))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<EmployeeDto>> getAllEmployees(
            @RequestParam(defaultValue = "false") boolean activeOnly) {
        List<EmployeeDto> employees = activeOnly ?
                employeeService.getActiveEmployees() :
                employeeService.getAllEmployees();
        return ResponseEntity.ok(employees);
    }

    @PutMapping("/{id}")
    public ResponseEntity<EmployeeDto> updateEmployee(
            @PathVariable @Min(1) Long id,
            @Valid @RequestBody EmployeeDto employeeDto) {
        try {
            EmployeeDto updated = employeeService.updateEmployee(id, employeeDto);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteEmployee(@PathVariable @Min(1) Long id) {
        try {
            boolean deleted = employeeService.deleteEmployee(id);
            return deleted ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // Department Operations

    @PatchMapping("/{id}/department/{departmentId}")
    public ResponseEntity<EmployeeDto> assignEmployeeToDepartment(
            @PathVariable @Min(1) Long id,
            @PathVariable @Min(1) Long departmentId) {
        try {
            EmployeeDto updated = employeeService.assignEmployeeToDepartment(id, departmentId);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PatchMapping("/{id}/remove-department")
    public ResponseEntity<EmployeeDto> removeEmployeeFromDepartment(@PathVariable @Min(1) Long id) {
        try {
            EmployeeDto updated = employeeService.removeEmployeeFromDepartment(id);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/{id}/transfer/{newDepartmentId}")
    public ResponseEntity<Map<String, Object>> transferEmployee(
            @PathVariable @Min(1) Long id,
            @PathVariable @Min(1) Long newDepartmentId) {
        boolean success = employeeService.transferEmployee(id, newDepartmentId);
        Map<String, Object> result = Map.of("success", success);
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    // Status Operations

    @PatchMapping("/{id}/activate")
    public ResponseEntity<Void> activateEmployee(@PathVariable @Min(1) Long id) {
        boolean activated = employeeService.activateEmployee(id);
        return activated ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    @PatchMapping("/{id}/deactivate")
    public ResponseEntity<Void> deactivateEmployee(@PathVariable @Min(1) Long id) {
        boolean deactivated = employeeService.deactivateEmployee(id);
        return deactivated ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    // Search Operations

    @GetMapping("/search")
    public ResponseEntity<List<EmployeeDto>> searchEmployees(
            @RequestParam(required = false) String term,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hiredAfter,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hiredBefore,
            @RequestParam(required = false) @Min(1900) Integer hiredInYear,
            @RequestParam(required = false) @Min(0) Integer minYearsOfService,
            @RequestParam(required = false) BigDecimal minDepartmentBudget,
            @RequestParam(defaultValue = "false") boolean fullText) {

        List<EmployeeDto> results;

        if (term != null && !term.trim().isEmpty()) {
            results = fullText ?
                    employeeService.searchEmployeesFullText(term) :
                    employeeService.searchEmployees(term);
        } else if (hiredAfter != null && hiredBefore != null) {
            results = employeeService.getEmployeesHiredBetween(hiredAfter, hiredBefore);
        } else if (hiredAfter != null) {
            results = employeeService.getEmployeesHiredBetween(hiredAfter, LocalDate.now());
        } else if (hiredBefore != null) {
            results = employeeService.getEmployeesHiredBetween(LocalDate.of(1900, 1, 1), hiredBefore);
        } else if (hiredInYear != null) {
            results = employeeService.getEmployeesHiredInYear(hiredInYear);
        } else if (minYearsOfService != null) {
            results = employeeService.getEmployeesWithMinYearsOfService(minYearsOfService);
        } else if (minDepartmentBudget != null) {
            results = employeeService.getEmployeesInDepartmentsWithMinBudget(minDepartmentBudget);
        } else {
            results = employeeService.getAllEmployees();
        }

        return ResponseEntity.ok(results);
    }

    // Department-Based Queries

    @GetMapping("/department/{departmentId}")
    public ResponseEntity<List<EmployeeDto>> getEmployeesByDepartment(
            @PathVariable @Min(1) Long departmentId) {
        List<EmployeeDto> employees = employeeService.getEmployeesByDepartment(departmentId);
        return ResponseEntity.ok(employees);
    }

    @GetMapping("/department/code/{departmentCode}")
    public ResponseEntity<List<EmployeeDto>> getEmployeesByDepartmentCode(
            @PathVariable @NotBlank String departmentCode) {
        List<EmployeeDto> employees = employeeService.getEmployeesByDepartmentCode(departmentCode);
        return ResponseEntity.ok(employees);
    }

    @GetMapping("/without-department")
    public ResponseEntity<List<EmployeeDto>> getEmployeesWithoutDepartment() {
        List<EmployeeDto> employees = employeeService.getEmployeesWithoutDepartment();
        return ResponseEntity.ok(employees);
    }

    @GetMapping("/in-active-departments")
    public ResponseEntity<List<EmployeeDto>> getEmployeesInActiveDepartments() {
        List<EmployeeDto> employees = employeeService.getEmployeesInActiveDepartments();
        return ResponseEntity.ok(employees);
    }

    // Special Categories

    @GetMapping("/new-employees")
    public ResponseEntity<List<EmployeeDto>> getNewEmployees() {
        List<EmployeeDto> employees = employeeService.getNewEmployees();
        return ResponseEntity.ok(employees);
    }

    @GetMapping("/veteran-employees")
    public ResponseEntity<List<EmployeeDto>> getVeteranEmployees() {
        List<EmployeeDto> employees = employeeService.getVeteranEmployees();
        return ResponseEntity.ok(employees);
    }

    // Statistics Operations

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getEmployeeStatistics() {
        Map<String, Object> stats = Map.of(
                "totalActiveEmployees", employeeService.getActiveEmployeeCount(),
                "hiringStatisticsByYear", employeeService.getHiringStatisticsByYear(),
                "departmentEmployeeCounts", employeeService.getDepartmentEmployeeCounts()
        );
        return ResponseEntity.ok(stats);
    }

    @GetMapping("/statistics/department/{departmentId}")
    public ResponseEntity<Map<String, Object>> getDepartmentEmployeeStatistics(
            @PathVariable @Min(1) Long departmentId) {
        Map<String, Object> stats = Map.of(
                "employeeCount", employeeService.getEmployeeCountByDepartment(departmentId)
        );
        return ResponseEntity.ok(stats);
    }

    // Validation Operations

    @GetMapping("/email/{email}/unique")
    public ResponseEntity<Map<String, Boolean>> checkEmailUniqueness(
            @PathVariable @NotBlank String email,
            @RequestParam(required = false) Long excludeId) {
        boolean isUnique = employeeService.isEmailUnique(email, excludeId);
        Map<String, Boolean> result = Map.of("unique", isUnique);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}/active")
    public ResponseEntity<Map<String, Boolean>> checkEmployeeActive(@PathVariable @Min(1) Long id) {
        boolean isActive = employeeService.isEmployeeActive(id);
        Map<String, Boolean> result = Map.of("active", isActive);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}/can-delete")
    public ResponseEntity<Map<String, Boolean>> checkCanDelete(@PathVariable @Min(1) Long id) {
        boolean canDelete = employeeService.canDeleteEmployee(id);
        Map<String, Boolean> result = Map.of("canDelete", canDelete);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{employeeId}/can-assign/{departmentId}")
    public ResponseEntity<Map<String, Boolean>> checkCanAssignToDepartment(
            @PathVariable @Min(1) Long employeeId,
            @PathVariable @Min(1) Long departmentId) {
        boolean canAssign = employeeService.canAssignToDepartment(employeeId, departmentId);
        Map<String, Boolean> result = Map.of("canAssign", canAssign);
        return ResponseEntity.ok(result);
    }

    // Batch Operations

    @PatchMapping("/batch/activate")
    public ResponseEntity<Map<String, Integer>> activateEmployees(
            @RequestBody List<Long> employeeIds) {
        int count = employeeService.activateEmployees(employeeIds);
        Map<String, Integer> result = Map.of("activated", count);
        return ResponseEntity.ok(result);
    }

    @PatchMapping("/batch/deactivate")
    public ResponseEntity<Map<String, Integer>> deactivateEmployees(
            @RequestBody List<Long> employeeIds) {
        int count = employeeService.deactivateEmployees(employeeIds);
        Map<String, Integer> result = Map.of("deactivated", count);
        return ResponseEntity.ok(result);
    }

    @PatchMapping("/batch/transfer/{newDepartmentId}")
    public ResponseEntity<Map<String, Integer>> transferEmployees(
            @PathVariable @Min(1) Long newDepartmentId,
            @RequestBody List<Long> employeeIds) {
        int count = employeeService.transferEmployees(employeeIds, newDepartmentId);
        Map<String, Integer> result = Map.of("transferred", count);
        return ResponseEntity.ok(result);
    }

    @PatchMapping("/department/{departmentId}/remove-all")
    public ResponseEntity<Map<String, Integer>> removeAllFromDepartment(
            @PathVariable @Min(1) Long departmentId) {
        int count = employeeService.removeAllFromDepartment(departmentId);
        Map<String, Integer> result = Map.of("removed", count);
        return ResponseEntity.ok(result);
    }

    // Exception Handlers

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> handleIllegalArgumentException(
            IllegalArgumentException e) {
        Map<String, String> error = Map.of(
                "error", "Bad Request",
                "message", e.getMessage()
        );
        return ResponseEntity.badRequest().body(error);
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, String>> handleIllegalStateException(
            IllegalStateException e) {
        Map<String, String> error = Map.of(
                "error", "Conflict",
                "message", e.getMessage()
        );
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleGenericException(Exception e) {
        Map<String, String> error = Map.of(
                "error", "Internal Server Error",
                "message", "An unexpected error occurred"
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}