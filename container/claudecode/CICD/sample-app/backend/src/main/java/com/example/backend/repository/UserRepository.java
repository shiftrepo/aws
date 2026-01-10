package com.example.backend.repository;

import com.example.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * User Repository
 * ユーザーリポジトリ
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * 部門IDでユーザー一覧を取得
     */
    List<User> findByDepartmentIdOrderByName(Long departmentId);

    /**
     * メールアドレスでユーザーを検索
     */
    Optional<User> findByEmail(String email);

    /**
     * メールアドレスの重複チェック
     */
    boolean existsByEmail(String email);

    /**
     * メールアドレスの重複チェック（更新時用）
     */
    boolean existsByEmailAndIdNot(String email, Long id);

    /**
     * 組織IDでユーザー一覧を取得（部門経由）
     */
    @Query("SELECT u FROM User u JOIN u.department d WHERE d.organizationId = :organizationId ORDER BY u.name")
    List<User> findByOrganizationId(@Param("organizationId") Long organizationId);

    /**
     * 部門とその詳細を含むユーザー情報を取得
     */
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.department d LEFT JOIN FETCH d.organization WHERE u.id = :userId")
    Optional<User> findUserWithDetailsById(@Param("userId") Long userId);

    /**
     * 部門とその詳細を含むユーザー一覧を取得（部門ID指定）
     */
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.department d LEFT JOIN FETCH d.organization WHERE u.departmentId = :departmentId ORDER BY u.name")
    List<User> findUsersWithDetailsByDepartmentId(@Param("departmentId") Long departmentId);
}