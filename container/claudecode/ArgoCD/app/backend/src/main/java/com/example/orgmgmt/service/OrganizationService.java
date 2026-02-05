package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.OrganizationDTO;
import com.example.orgmgmt.entity.Organization;
import com.example.orgmgmt.exception.DuplicateResourceException;
import com.example.orgmgmt.exception.ResourceNotFoundException;
import com.example.orgmgmt.repository.OrganizationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class OrganizationService {

    private final OrganizationRepository organizationRepository;
    private final EntityMapper entityMapper;

    public OrganizationDTO createOrganization(Organization organization) {
        if (organizationRepository.existsByCode(organization.getCode())) {
            throw new DuplicateResourceException("Organization with code " + organization.getCode() + " already exists");
        }

        Organization saved = organizationRepository.save(organization);
        return entityMapper.toDTO(saved);
    }

    @Transactional(readOnly = true)
    public OrganizationDTO getOrganizationById(Long id) {
        Organization organization = organizationRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with id: " + id));
        return entityMapper.toDTO(organization);
    }

    @Transactional(readOnly = true)
    public OrganizationDTO getOrganizationByCode(String code) {
        Organization organization = organizationRepository.findByCode(code)
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with code: " + code));
        return entityMapper.toDTO(organization);
    }

    @Transactional(readOnly = true)
    public List<OrganizationDTO> getAllOrganizations() {
        return organizationRepository.findAll().stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<OrganizationDTO> getAllOrganizations(Pageable pageable) {
        return organizationRepository.findAll(pageable)
            .map(entityMapper::toDTO);
    }

    @Transactional(readOnly = true)
    public List<OrganizationDTO> getActiveOrganizations() {
        return organizationRepository.findByActiveTrue().stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<OrganizationDTO> searchOrganizations(String search, Pageable pageable) {
        return organizationRepository.searchOrganizations(search, pageable)
            .map(entityMapper::toDTO);
    }

    public OrganizationDTO updateOrganization(Long id, Organization organizationDetails) {
        Organization organization = organizationRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with id: " + id));

        if (!organization.getCode().equals(organizationDetails.getCode()) &&
            organizationRepository.existsByCode(organizationDetails.getCode())) {
            throw new DuplicateResourceException("Organization with code " + organizationDetails.getCode() + " already exists");
        }

        organization.setCode(organizationDetails.getCode());
        organization.setName(organizationDetails.getName());
        organization.setDescription(organizationDetails.getDescription());
        organization.setEstablishedDate(organizationDetails.getEstablishedDate());
        organization.setActive(organizationDetails.getActive());

        Organization updated = organizationRepository.save(organization);
        return entityMapper.toDTO(updated);
    }

    public void deleteOrganization(Long id) {
        Organization organization = organizationRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with id: " + id));
        organizationRepository.delete(organization);
    }

    public OrganizationDTO deactivateOrganization(Long id) {
        Organization organization = organizationRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with id: " + id));
        organization.setActive(false);
        Organization updated = organizationRepository.save(organization);
        return entityMapper.toDTO(updated);
    }
}
