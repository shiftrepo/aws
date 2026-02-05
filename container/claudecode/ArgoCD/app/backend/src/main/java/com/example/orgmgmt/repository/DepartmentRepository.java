package com.example.orgmgmt.repository;

import com.example.orgmgmt.entity.Department;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {

    Optional<Department> findByCodeAndOrganizationId(String code, Long organizationId);

    List<Department> findByOrganizationId(Long organizationId);

    List<Department> findByOrganizationIdAndActiveTrue(Long organizationId);

    List<Department> findByParentDepartmentId(Long parentDepartmentId);

    List<Department> findByOrganizationIdAndParentDepartmentIsNull(Long organizationId);

    Page<Department> findByActiveTrue(Pageable pageable);

    @Query("SELECT d FROM Department d WHERE d.organization.id = :orgId AND " +
           "(LOWER(d.name) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           "LOWER(d.code) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<Department> searchDepartments(@Param("orgId") Long organizationId,
                                       @Param("search") String search,
                                       Pageable pageable);
}
