package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.DepartmentDTO;
import com.example.orgmgmt.entity.Department;
import com.example.orgmgmt.entity.Organization;
import com.example.orgmgmt.exception.DuplicateResourceException;
import com.example.orgmgmt.exception.ResourceNotFoundException;
import com.example.orgmgmt.repository.DepartmentRepository;
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
public class DepartmentService {

    private final DepartmentRepository departmentRepository;
    private final OrganizationRepository organizationRepository;
    private final EntityMapper entityMapper;

    public DepartmentDTO createDepartment(Department department) {
        if (department.getOrganization() == null || department.getOrganization().getId() == null) {
            throw new IllegalArgumentException("Organization is required");
        }

        Organization organization = organizationRepository.findById(department.getOrganization().getId())
            .orElseThrow(() -> new ResourceNotFoundException("Organization not found with id: " + department.getOrganization().getId()));

        if (departmentRepository.findByCodeAndOrganizationId(department.getCode(), organization.getId()).isPresent()) {
            throw new DuplicateResourceException("Department with code " + department.getCode() + " already exists in this organization");
        }

        department.setOrganization(organization);

        if (department.getParentDepartment() != null && department.getParentDepartment().getId() != null) {
            Department parent = departmentRepository.findById(department.getParentDepartment().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Parent department not found with id: " + department.getParentDepartment().getId()));
            department.setParentDepartment(parent);
        }

        Department saved = departmentRepository.save(department);
        return entityMapper.toDTO(saved);
    }

    @Transactional(readOnly = true)
    public DepartmentDTO getDepartmentById(Long id) {
        Department department = departmentRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Department not found with id: " + id));
        return entityMapper.toDTO(department);
    }

    @Transactional(readOnly = true)
    public List<DepartmentDTO> getAllDepartments() {
        return departmentRepository.findAll().stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<DepartmentDTO> getAllDepartments(Pageable pageable) {
        return departmentRepository.findAll(pageable)
            .map(entityMapper::toDTO);
    }

    @Transactional(readOnly = true)
    public List<DepartmentDTO> getDepartmentsByOrganization(Long organizationId) {
        return departmentRepository.findByOrganizationId(organizationId).stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<DepartmentDTO> getRootDepartments(Long organizationId) {
        return departmentRepository.findByOrganizationIdAndParentDepartmentIsNull(organizationId).stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<DepartmentDTO> getChildDepartments(Long parentId) {
        return departmentRepository.findByParentDepartmentId(parentId).stream()
            .map(entityMapper::toDTO)
            .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<DepartmentDTO> searchDepartments(Long organizationId, String search, Pageable pageable) {
        return departmentRepository.searchDepartments(organizationId, search, pageable)
            .map(entityMapper::toDTO);
    }

    public DepartmentDTO updateDepartment(Long id, Department departmentDetails) {
        Department department = departmentRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Department not found with id: " + id));

        department.setCode(departmentDetails.getCode());
        department.setName(departmentDetails.getName());
        department.setDescription(departmentDetails.getDescription());
        department.setActive(departmentDetails.getActive());

        if (departmentDetails.getParentDepartment() != null && departmentDetails.getParentDepartment().getId() != null) {
            Department parent = departmentRepository.findById(departmentDetails.getParentDepartment().getId())
                .orElseThrow(() -> new ResourceNotFoundException("Parent department not found"));
            department.setParentDepartment(parent);
        }

        Department updated = departmentRepository.save(department);
        return entityMapper.toDTO(updated);
    }

    public void deleteDepartment(Long id) {
        Department department = departmentRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Department not found with id: " + id));
        departmentRepository.delete(department);
    }

    public DepartmentDTO deactivateDepartment(Long id) {
        Department department = departmentRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Department not found with id: " + id));
        department.setActive(false);
        Department updated = departmentRepository.save(department);
        return entityMapper.toDTO(updated);
    }
}
