package com.example.backend.controller;

import com.example.backend.service.OrganizationService;
import com.example.common.dto.OrganizationDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Organization REST Controller
 * 組織管理REST API
 */
@RestController
@RequestMapping("/api/organizations")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class OrganizationController {

    private final OrganizationService organizationService;

    /**
     * 全組織一覧取得
     * GET /api/organizations
     */
    @GetMapping
    public ResponseEntity<List<OrganizationDto>> getAllOrganizations() {
        log.debug("全組織一覧取得API呼び出し");
        List<OrganizationDto> organizations = organizationService.findAll();
        return ResponseEntity.ok(organizations);
    }

    /**
     * 組織ID指定取得
     * GET /api/organizations/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<OrganizationDto> getOrganizationById(@PathVariable Long id) {
        log.debug("組織取得API呼び出し: ID={}", id);
        OrganizationDto organization = organizationService.findById(id);
        return ResponseEntity.ok(organization);
    }

    /**
     * 組織作成
     * POST /api/organizations
     */
    @PostMapping
    public ResponseEntity<OrganizationDto> createOrganization(@Valid @RequestBody OrganizationDto organizationDto) {
        log.debug("組織作成API呼び出し: {}", organizationDto.getName());
        OrganizationDto created = organizationService.create(organizationDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /**
     * 組織更新
     * PUT /api/organizations/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<OrganizationDto> updateOrganization(
            @PathVariable Long id,
            @Valid @RequestBody OrganizationDto organizationDto) {
        log.debug("組織更新API呼び出し: ID={}", id);
        OrganizationDto updated = organizationService.update(id, organizationDto);
        return ResponseEntity.ok(updated);
    }

    /**
     * 組織削除
     * DELETE /api/organizations/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrganization(@PathVariable Long id) {
        log.debug("組織削除API呼び出し: ID={}", id);
        organizationService.delete(id);
        return ResponseEntity.noContent().build();
    }
}