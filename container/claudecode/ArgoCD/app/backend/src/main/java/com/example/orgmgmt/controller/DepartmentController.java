package com.example.orgmgmt.controller;

import com.example.orgmgmt.dto.DepartmentDTO;
import com.example.orgmgmt.entity.Department;
import com.example.orgmgmt.service.DepartmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/departments")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DepartmentController {

    private final DepartmentService departmentService;

    @PostMapping
    public ResponseEntity<DepartmentDTO> createDepartment(@Valid @RequestBody Department department) {
        DepartmentDTO created = departmentService.createDepartment(department);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<Page<DepartmentDTO>> getAllDepartments(Pageable pageable) {
        Page<DepartmentDTO> departments = departmentService.getAllDepartments(pageable);
        return ResponseEntity.ok(departments);
    }

    @GetMapping("/{id}")
    public ResponseEntity<DepartmentDTO> getDepartmentById(@PathVariable Long id) {
        DepartmentDTO department = departmentService.getDepartmentById(id);
        return ResponseEntity.ok(department);
    }

    @GetMapping("/organization/{orgId}")
    public ResponseEntity<List<DepartmentDTO>> getDepartmentsByOrganization(@PathVariable Long orgId) {
        List<DepartmentDTO> departments = departmentService.getDepartmentsByOrganization(orgId);
        return ResponseEntity.ok(departments);
    }

    @GetMapping("/organization/{orgId}/root")
    public ResponseEntity<List<DepartmentDTO>> getRootDepartments(@PathVariable Long orgId) {
        List<DepartmentDTO> departments = departmentService.getRootDepartments(orgId);
        return ResponseEntity.ok(departments);
    }

    @GetMapping("/{id}/children")
    public ResponseEntity<List<DepartmentDTO>> getChildDepartments(@PathVariable Long id) {
        List<DepartmentDTO> departments = departmentService.getChildDepartments(id);
        return ResponseEntity.ok(departments);
    }

    @GetMapping("/search")
    public ResponseEntity<Page<DepartmentDTO>> searchDepartments(
            @RequestParam("orgId") Long orgId,
            @RequestParam("q") String search,
            Pageable pageable) {
        Page<DepartmentDTO> departments = departmentService.searchDepartments(orgId, search, pageable);
        return ResponseEntity.ok(departments);
    }

    @PutMapping("/{id}")
    public ResponseEntity<DepartmentDTO> updateDepartment(
            @PathVariable Long id,
            @Valid @RequestBody Department department) {
        DepartmentDTO updated = departmentService.updateDepartment(id, department);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDepartment(@PathVariable Long id) {
        departmentService.deleteDepartment(id);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{id}/deactivate")
    public ResponseEntity<DepartmentDTO> deactivateDepartment(@PathVariable Long id) {
        DepartmentDTO deactivated = departmentService.deactivateDepartment(id);
        return ResponseEntity.ok(deactivated);
    }
}
