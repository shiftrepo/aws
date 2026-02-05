package com.example.orgmgmt.repository;

import com.example.orgmgmt.entity.Organization;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface OrganizationRepository extends JpaRepository<Organization, Long> {

    Optional<Organization> findByCode(String code);

    boolean existsByCode(String code);

    List<Organization> findByActiveTrue();

    Page<Organization> findByActiveTrue(Pageable pageable);

    @Query("SELECT o FROM Organization o WHERE " +
           "LOWER(o.name) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           "LOWER(o.code) LIKE LOWER(CONCAT('%', :search, '%'))")
    Page<Organization> searchOrganizations(@Param("search") String search, Pageable pageable);
}
