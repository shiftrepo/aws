package com.example.orgmgmt.controller;

import com.example.orgmgmt.dto.OrganizationDTO;
import com.example.orgmgmt.entity.Organization;
import com.example.orgmgmt.service.OrganizationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/organizations")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class OrganizationController {

    private final OrganizationService organizationService;

    @PostMapping
    public ResponseEntity<OrganizationDTO> createOrganization(@Valid @RequestBody Organization organization) {
        OrganizationDTO created = organizationService.createOrganization(organization);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<Page<OrganizationDTO>> getAllOrganizations(Pageable pageable) {
        Page<OrganizationDTO> organizations = organizationService.getAllOrganizations(pageable);
        return ResponseEntity.ok(organizations);
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrganizationDTO> getOrganizationById(@PathVariable Long id) {
        OrganizationDTO organization = organizationService.getOrganizationById(id);
        return ResponseEntity.ok(organization);
    }

    @GetMapping("/code/{code}")
    public ResponseEntity<OrganizationDTO> getOrganizationByCode(@PathVariable String code) {
        OrganizationDTO organization = organizationService.getOrganizationByCode(code);
        return ResponseEntity.ok(organization);
    }

    @GetMapping("/active")
    public ResponseEntity<List<OrganizationDTO>> getActiveOrganizations() {
        List<OrganizationDTO> organizations = organizationService.getActiveOrganizations();
        return ResponseEntity.ok(organizations);
    }

    @GetMapping("/search")
    public ResponseEntity<Page<OrganizationDTO>> searchOrganizations(
            @RequestParam("q") String search,
            Pageable pageable) {
        Page<OrganizationDTO> organizations = organizationService.searchOrganizations(search, pageable);
        return ResponseEntity.ok(organizations);
    }

    @PutMapping("/{id}")
    public ResponseEntity<OrganizationDTO> updateOrganization(
            @PathVariable Long id,
            @Valid @RequestBody Organization organization) {
        OrganizationDTO updated = organizationService.updateOrganization(id, organization);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrganization(@PathVariable Long id) {
        organizationService.deleteOrganization(id);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{id}/deactivate")
    public ResponseEntity<OrganizationDTO> deactivateOrganization(@PathVariable Long id) {
        OrganizationDTO deactivated = organizationService.deactivateOrganization(id);
        return ResponseEntity.ok(deactivated);
    }
}
