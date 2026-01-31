package com.example.employee.controller;

import com.example.employee.dto.DepartmentDto;
import com.example.employee.service.DepartmentService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * REST Controller for Department operations.
 *
 * Provides comprehensive CRUD operations and business functionality
 * for departments. Demonstrates REST API design, validation, error
 * handling, and JSON serialization for testing purposes.
 */
@RestController
@RequestMapping("/api/v1/departments")
@Validated
@CrossOrigin(origins = "*", maxAge = 3600)
public class DepartmentController {

    private final DepartmentService departmentService;

    @Autowired
    public DepartmentController(DepartmentService departmentService) {
        this.departmentService = departmentService;
    }

    // Basic CRUD Operations

    @PostMapping
    public ResponseEntity<DepartmentDto> createDepartment(@Valid @RequestBody DepartmentDto departmentDto) {
        try {
            DepartmentDto created = departmentService.createDepartment(departmentDto);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<DepartmentDto> getDepartmentById(@PathVariable @Min(1) Long id) {
        return departmentService.getDepartmentById(id)
                .map(department -> ResponseEntity.ok().body(department))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/code/{code}")
    public ResponseEntity<DepartmentDto> getDepartmentByCode(
            @PathVariable @NotBlank String code) {
        return departmentService.getDepartmentByCode(code)
                .map(department -> ResponseEntity.ok().body(department))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<DepartmentDto>> getAllDepartments(
            @RequestParam(defaultValue = "false") boolean activeOnly) {
        List<DepartmentDto> departments = activeOnly ?
                departmentService.getActiveDepartments() :
                departmentService.getAllDepartments();
        return ResponseEntity.ok(departments);
    }

    @GetMapping("/with-employee-count")
    public ResponseEntity<List<DepartmentDto>> getDepartmentsWithEmployeeCount() {
        List<DepartmentDto> departments = departmentService.getDepartmentsWithEmployeeCount();
        return ResponseEntity.ok(departments);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DepartmentDto> updateDepartment(
            @PathVariable @Min(1) Long id,
            @Valid @RequestBody DepartmentDto departmentDto) {
        try {
            DepartmentDto updated = departmentService.updateDepartment(id, departmentDto);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDepartment(@PathVariable @Min(1) Long id) {
        try {
            boolean deleted = departmentService.deleteDepartment(id);
            return deleted ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // Status Operations

    @PatchMapping("/{id}/activate")
    public ResponseEntity<Void> activateDepartment(@PathVariable @Min(1) Long id) {
        boolean activated = departmentService.activateDepartment(id);
        return activated ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    @PatchMapping("/{id}/deactivate")
    public ResponseEntity<Void> deactivateDepartment(@PathVariable @Min(1) Long id) {
        boolean deactivated = departmentService.deactivateDepartment(id);
        return deactivated ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    // Search Operations

    @GetMapping("/search")
    public ResponseEntity<List<DepartmentDto>> searchDepartments(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) BigDecimal minBudget,
            @RequestParam(required = false) BigDecimal maxBudget,
            @RequestParam(required = false) @Min(0) Integer minEmployees) {

        List<DepartmentDto> results;

        if (name != null && !name.trim().isEmpty()) {
            results = departmentService.searchDepartmentsByName(name);
        } else if (minBudget != null || maxBudget != null) {
            results = departmentService.getDepartmentsWithBudgetRange(minBudget, maxBudget);
        } else if (minEmployees != null) {
            results = departmentService.getDepartmentsWithMinEmployees(minEmployees);
        } else {
            results = departmentService.getAllDepartments();
        }

        return ResponseEntity.ok(results);
    }

    @GetMapping("/above-average-budget")
    public ResponseEntity<List<DepartmentDto>> getDepartmentsWithAboveAverageBudget() {
        List<DepartmentDto> departments = departmentService.getDepartmentsWithAboveAverageBudget();
        return ResponseEntity.ok(departments);
    }

    // Statistics Operations

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getDepartmentStatistics() {
        Map<String, Object> stats = Map.of(
                "totalActiveDepartments", departmentService.getActiveDepartmentCount(),
                "totalActiveBudget", departmentService.getTotalActiveBudget(),
                "averageActiveBudget", departmentService.getAverageActiveBudget()
        );
        return ResponseEntity.ok(stats);
    }

    // Business Operations

    @PostMapping("/{fromId}/transfer-employees/{toId}")
    public ResponseEntity<Map<String, Object>> transferAllEmployees(
            @PathVariable @Min(1) Long fromId,
            @PathVariable @Min(1) Long toId) {
        try {
            boolean success = departmentService.transferAllEmployees(fromId, toId);
            Map<String, Object> result = Map.of("success", success);
            return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // Validation Operations

    @GetMapping("/code/{code}/unique")
    public ResponseEntity<Map<String, Boolean>> checkCodeUniqueness(
            @PathVariable @NotBlank String code,
            @RequestParam(required = false) Long excludeId) {
        boolean isUnique = departmentService.isDepartmentCodeUnique(code, excludeId);
        Map<String, Boolean> result = Map.of("unique", isUnique);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}/can-delete")
    public ResponseEntity<Map<String, Boolean>> checkCanDelete(@PathVariable @Min(1) Long id) {
        boolean canDelete = departmentService.canDeleteDepartment(id);
        Map<String, Boolean> result = Map.of("canDelete", canDelete);
        return ResponseEntity.ok(result);
    }

    // Batch Operations

    @PatchMapping("/batch/activate")
    public ResponseEntity<Map<String, Integer>> activateDepartments(
            @RequestBody List<Long> departmentIds) {
        int count = departmentService.activateDepartments(departmentIds);
        Map<String, Integer> result = Map.of("activated", count);
        return ResponseEntity.ok(result);
    }

    @PatchMapping("/batch/deactivate")
    public ResponseEntity<Map<String, Integer>> deactivateDepartments(
            @RequestBody List<Long> departmentIds) {
        int count = departmentService.deactivateDepartments(departmentIds);
        Map<String, Integer> result = Map.of("deactivated", count);
        return ResponseEntity.ok(result);
    }

    @DeleteMapping("/cleanup/inactive-without-employees")
    public ResponseEntity<Map<String, Integer>> deleteInactiveDepartmentsWithoutEmployees() {
        int count = departmentService.deleteInactiveDepartmentsWithoutEmployees();
        Map<String, Integer> result = Map.of("deleted", count);
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