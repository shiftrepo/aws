package com.example.employee.repository;

import com.example.employee.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for Department entity operations.
 *
 * Demonstrates various query methods for testing scenarios:
 * - Basic CRUD operations (from JpaRepository)
 * - Query derivation methods
 * - Custom JPQL queries
 * - Native SQL queries
 * - Aggregation queries for complex testing scenarios
 */
@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {

    // Query derivation methods (for beginner-level testing)
    Optional<Department> findByCode(String code);

    List<Department> findByActiveTrue();

    List<Department> findByActiveFalse();

    List<Department> findByNameContainingIgnoreCase(String name);

    List<Department> findByBudgetGreaterThan(BigDecimal budget);

    List<Department> findByBudgetLessThan(BigDecimal budget);

    List<Department> findByBudgetBetween(BigDecimal minBudget, BigDecimal maxBudget);

    boolean existsByCode(String code);

    long countByActiveTrue();

    // Custom JPQL queries (for intermediate-level testing)
    @Query("SELECT d FROM Department d WHERE d.active = :active ORDER BY d.name")
    List<Department> findByActiveStatus(@Param("active") Boolean active);

    @Query("SELECT d FROM Department d WHERE SIZE(d.employees) > :minEmployees")
    List<Department> findDepartmentsWithMinEmployees(@Param("minEmployees") int minEmployees);

    @Query("SELECT d FROM Department d WHERE SIZE(d.employees) = 0 AND d.active = true")
    List<Department> findEmptyActiveDepartments();

    @Query("SELECT d.name, COUNT(e) FROM Department d LEFT JOIN d.employees e GROUP BY d.id, d.name")
    List<Object[]> findDepartmentEmployeeCounts();

    // Complex aggregation queries (for advanced-level testing)
    @Query("SELECT d FROM Department d WHERE d.budget > " +
           "(SELECT AVG(dept.budget) FROM Department dept WHERE dept.active = true) " +
           "AND d.active = true")
    List<Department> findDepartmentsWithAboveAverageBudget();

    @Query("SELECT SUM(d.budget) FROM Department d WHERE d.active = true")
    BigDecimal getTotalActiveDepartmentsBudget();

    @Query("SELECT AVG(d.budget) FROM Department d WHERE d.active = true")
    BigDecimal getAverageActiveDepartmentBudget();

    @Query("SELECT MAX(d.budget) FROM Department d WHERE d.active = true")
    BigDecimal getMaxActiveDepartmentBudget();

    @Query("SELECT MIN(d.budget) FROM Department d WHERE d.active = true")
    BigDecimal getMinActiveDepartmentBudget();

    // Native SQL queries (for advanced testing scenarios)
    @Query(value = "SELECT d.* FROM departments d WHERE " +
                   "EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)",
           nativeQuery = true)
    List<Department> findDepartmentsWithEmployeesNative();

    @Query(value = "SELECT d.name, COUNT(e.id) as employee_count, " +
                   "COALESCE(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))), 0) as avg_years_service " +
                   "FROM departments d LEFT JOIN employees e ON d.id = e.department_id " +
                   "WHERE d.active = true GROUP BY d.id, d.name " +
                   "ORDER BY employee_count DESC",
           nativeQuery = true)
    List<Object[]> getDepartmentStatisticsNative();

    // Batch operations (for performance testing)
    @Query("UPDATE Department d SET d.active = :active WHERE d.id IN :ids")
    int updateActiveStatusByIds(@Param("active") Boolean active, @Param("ids") List<Long> ids);

    @Query("DELETE FROM Department d WHERE d.active = false AND SIZE(d.employees) = 0")
    int deleteInactiveDepartmentsWithNoEmployees();
}