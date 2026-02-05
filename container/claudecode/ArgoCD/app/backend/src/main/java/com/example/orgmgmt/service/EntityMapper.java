package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.DepartmentDTO;
import com.example.orgmgmt.dto.OrganizationDTO;
import com.example.orgmgmt.dto.UserDTO;
import com.example.orgmgmt.entity.Department;
import com.example.orgmgmt.entity.Organization;
import com.example.orgmgmt.entity.User;
import org.springframework.stereotype.Component;

@Component
public class EntityMapper {

    public OrganizationDTO toDTO(Organization org) {
        if (org == null) return null;

        OrganizationDTO dto = new OrganizationDTO();
        dto.setId(org.getId());
        dto.setCode(org.getCode());
        dto.setName(org.getName());
        dto.setDescription(org.getDescription());
        dto.setEstablishedDate(org.getEstablishedDate());
        dto.setActive(org.getActive());
        dto.setCreatedAt(org.getCreatedAt());
        dto.setUpdatedAt(org.getUpdatedAt());
        return dto;
    }

    public DepartmentDTO toDTO(Department dept) {
        if (dept == null) return null;

        DepartmentDTO dto = new DepartmentDTO();
        dto.setId(dept.getId());
        dto.setOrganizationId(dept.getOrganization() != null ? dept.getOrganization().getId() : null);
        dto.setOrganizationName(dept.getOrganization() != null ? dept.getOrganization().getName() : null);
        dto.setParentDepartmentId(dept.getParentDepartment() != null ? dept.getParentDepartment().getId() : null);
        dto.setParentDepartmentName(dept.getParentDepartment() != null ? dept.getParentDepartment().getName() : null);
        dto.setCode(dept.getCode());
        dto.setName(dept.getName());
        dto.setDescription(dept.getDescription());
        dto.setActive(dept.getActive());
        dto.setCreatedAt(dept.getCreatedAt());
        dto.setUpdatedAt(dept.getUpdatedAt());
        return dto;
    }

    public UserDTO toDTO(User user) {
        if (user == null) return null;

        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setDepartmentId(user.getDepartment() != null ? user.getDepartment().getId() : null);
        dto.setDepartmentName(user.getDepartment() != null ? user.getDepartment().getName() : null);
        dto.setEmployeeNumber(user.getEmployeeNumber());
        dto.setUsername(user.getUsername());
        dto.setEmail(user.getEmail());
        dto.setFirstName(user.getFirstName());
        dto.setLastName(user.getLastName());
        dto.setActive(user.getActive());
        dto.setCreatedAt(user.getCreatedAt());
        dto.setUpdatedAt(user.getUpdatedAt());
        return dto;
    }
}
