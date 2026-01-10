package com.example.backend.repository;

import com.example.backend.entity.Organization;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Organization Repository
 * 組織リポジトリ
 */
@Repository
public interface OrganizationRepository extends JpaRepository<Organization, Long> {

    /**
     * 組織名で検索
     */
    Optional<Organization> findByName(String name);

    /**
     * 組織名の重複チェック
     */
    boolean existsByName(String name);

    /**
     * 組織名の重複チェック（更新時用）
     */
    boolean existsByNameAndIdNot(String name, Long id);
}