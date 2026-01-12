package com.example.backend.controller;

import com.example.backend.service.DepartmentService;
import com.example.common.dto.DepartmentDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;

/**
 * Department REST Controller
 * 部門管理REST API
 */
@RestController
@RequestMapping("/api/departments")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class DepartmentController {

    private final DepartmentService departmentService;

    /**
     * 全部門一覧取得
     * GET /api/departments
     */
    @GetMapping
    public ResponseEntity<List<DepartmentDto>> getAllDepartments() {
        log.debug("全部門一覧取得API呼び出し");
        List<DepartmentDto> departments = departmentService.findAll();
        return ResponseEntity.ok(departments);
    }

    /**
     * 部門ID指定取得
     * GET /api/departments/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<DepartmentDto> getDepartmentById(@PathVariable Long id) {
        log.debug("部門取得API呼び出し: ID={}", id);
        DepartmentDto department = departmentService.findById(id);
        return ResponseEntity.ok(department);
    }

    /**
     * 組織IDで部門一覧取得
     * GET /api/departments/organization/{organizationId}
     */
    @GetMapping("/organization/{organizationId}")
    public ResponseEntity<List<DepartmentDto>> getDepartmentsByOrganizationId(@PathVariable Long organizationId) {
        log.debug("組織別部門一覧取得API呼び出し: organizationId={}", organizationId);
        List<DepartmentDto> departments = departmentService.findByOrganizationId(organizationId);
        return ResponseEntity.ok(departments);
    }

    /**
     * 部門作成
     * POST /api/departments
     */
    @PostMapping
    public ResponseEntity<DepartmentDto> createDepartment(@Valid @RequestBody DepartmentDto departmentDto) {
        log.debug("部門作成API呼び出し: {}", departmentDto.getName());
        DepartmentDto created = departmentService.create(departmentDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /**
     * 部門更新
     * PUT /api/departments/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<DepartmentDto> updateDepartment(
            @PathVariable Long id,
            @Valid @RequestBody DepartmentDto departmentDto) {
        log.debug("部門更新API呼び出し: ID={}", id);
        DepartmentDto updated = departmentService.update(id, departmentDto);
        return ResponseEntity.ok(updated);
    }

    /**
     * 部門削除
     * DELETE /api/departments/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDepartment(@PathVariable Long id) {
        log.debug("部門削除API呼び出し: ID={}", id);
        departmentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
