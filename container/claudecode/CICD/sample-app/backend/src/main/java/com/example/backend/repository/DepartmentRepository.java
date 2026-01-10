package com.example.backend.repository;

import com.example.backend.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Department Repository
 * 部門リポジトリ
 */
@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {

    /**
     * 組織IDで部門一覧を取得
     */
    List<Department> findByOrganizationIdOrderByName(Long organizationId);

    /**
     * 親部門IDで子部門一覧を取得
     */
    List<Department> findByParentDepartmentIdOrderByName(Long parentDepartmentId);

    /**
     * トップレベル部門一覧を取得（親部門がnull）
     */
    List<Department> findByOrganizationIdAndParentDepartmentIdIsNullOrderByName(Long organizationId);

    /**
     * 組織内の部門名で検索
     */
    Optional<Department> findByOrganizationIdAndName(Long organizationId, String name);

    /**
     * 組織内での部門名の重複チェック
     */
    boolean existsByOrganizationIdAndName(Long organizationId, String name);

    /**
     * 組織内での部門名の重複チェック（更新時用）
     */
    boolean existsByOrganizationIdAndNameAndIdNot(Long organizationId, String name, Long id);

    /**
     * 階層構造を考慮した部門一覧取得（組織ID指定）
     */
    @Query("SELECT d FROM Department d LEFT JOIN FETCH d.organization LEFT JOIN FETCH d.parentDepartment WHERE d.organizationId = :organizationId ORDER BY d.name")
    List<Department> findDepartmentsWithDetailsBy​OrganizationId(@Param("organizationId") Long organizationId);
}