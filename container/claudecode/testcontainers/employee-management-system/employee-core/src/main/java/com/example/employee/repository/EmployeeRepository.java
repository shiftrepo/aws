package com.example.employee.repository;

import com.example.employee.entity.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for Employee entity operations.
 *
 * Demonstrates comprehensive query methods for testing different scenarios:
 * - Basic CRUD operations
 * - Query derivation methods
 * - Named queries (defined in Employee entity)
 * - Custom JPQL queries
 * - Native SQL queries
 * - Complex joins and aggregations
 */
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Query derivation methods (for beginner-level testing)
    Optional<Employee> findByEmail(String email);

    List<Employee> findByActiveTrue();

    List<Employee> findByActiveFalse();

    List<Employee> findByFirstNameIgnoreCase(String firstName);

    List<Employee> findByLastNameIgnoreCase(String lastName);

    List<Employee> findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(
        String firstName, String lastName);

    List<Employee> findByHireDateAfter(LocalDate date);

    List<Employee> findByHireDateBefore(LocalDate date);

    List<Employee> findByHireDateBetween(LocalDate startDate, LocalDate endDate);

    List<Employee> findByDepartmentId(Long departmentId);

    List<Employee> findByDepartment_Code(String departmentCode);

    List<Employee> findByDepartment_Name(String departmentName);

    List<Employee> findByDepartment_ActiveTrue();

    boolean existsByEmail(String email);

    long countByActiveTrue();

    long countByDepartmentId(Long departmentId);

    // Named queries (defined in Employee entity) - using entity-defined named queries

    // Custom JPQL queries (for intermediate-level testing)
    @Query("SELECT e FROM Employee e WHERE e.active = :active ORDER BY e.lastName, e.firstName")
    List<Employee> findByActiveStatus(@Param("active") Boolean active);

    @Query("SELECT e FROM Employee e WHERE e.department.active = true AND e.active = true")
    List<Employee> findActiveEmployeesInActiveDepartments();

    @Query("SELECT e FROM Employee e WHERE e.department IS NULL AND e.active = true")
    List<Employee> findActiveEmployeesWithoutDepartment();

    @Query("SELECT e FROM Employee e WHERE YEAR(e.hireDate) = :year")
    List<Employee> findEmployeesHiredInYear(@Param("year") int year);

    @Query("SELECT e FROM Employee e WHERE " +
           "YEAR(CURRENT_DATE) - YEAR(e.hireDate) >= :years")
    List<Employee> findEmployeesWithMinYearsOfService(@Param("years") int years);

    // Complex queries with joins (for advanced-level testing)
    @Query("SELECT e FROM Employee e JOIN e.department d WHERE " +
           "d.budget > :minBudget AND e.active = true AND d.active = true")
    List<Employee> findEmployeesInDepartmentsWithMinBudget(@Param("minBudget") java.math.BigDecimal minBudget);

    @Query("SELECT e, d.name, d.budget FROM Employee e JOIN e.department d WHERE e.active = true")
    List<Object[]> findActiveEmployeesWithDepartmentInfo();

    @Query("SELECT d.name, COUNT(e) FROM Department d LEFT JOIN d.employees e " +
           "WHERE d.active = true GROUP BY d.id, d.name " +
           "HAVING COUNT(e) > :minEmployees")
    List<Object[]> findDepartmentsWithMinEmployeeCount(@Param("minEmployees") long minEmployees);

    // Aggregation queries (for advanced testing scenarios)
    @Query("SELECT COUNT(e) FROM Employee e WHERE e.active = true GROUP BY e.department")
    List<Long> getEmployeeCountsByDepartment();

    @Query("SELECT YEAR(e.hireDate), COUNT(e) FROM Employee e WHERE e.active = true " +
           "GROUP BY YEAR(e.hireDate) ORDER BY YEAR(e.hireDate)")
    List<Object[]> getHiringStatisticsByYear();

    @Query("SELECT d.name, COUNT(e) as employeeCount FROM Department d LEFT JOIN d.employees e " +
           "WHERE d.active = true AND (e.active = true OR e.active IS NULL) " +
           "GROUP BY d.id, d.name ORDER BY employeeCount DESC")
    List<Object[]> getDepartmentEmployeeCountsOrdered();

    // Native SQL queries (for advanced testing with PostgreSQL-specific features)
    @Query(value = "SELECT e.* FROM employees e WHERE " +
                   "EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) >= ?1 " +
                   "AND e.active = true",
           nativeQuery = true)
    List<Employee> findEmployeesWithMinYearsOfServiceNative(int years);

    @Query(value = "SELECT e.*, d.name as department_name, d.budget as department_budget " +
                   "FROM employees e LEFT JOIN departments d ON e.department_id = d.id " +
                   "WHERE e.active = true AND (d.active IS NULL OR d.active = true) " +
                   "ORDER BY d.name NULLS LAST, e.last_name, e.first_name",
           nativeQuery = true)
    List<Object[]> findAllActiveEmployeesWithDepartmentDetailsNative();

    @Query(value = "SELECT " +
                   "DATE_PART('year', e.hire_date) as hire_year, " +
                   "COUNT(*) as total_hired, " +
                   "COUNT(CASE WHEN e.active = true THEN 1 END) as currently_active " +
                   "FROM employees e " +
                   "GROUP BY DATE_PART('year', e.hire_date) " +
                   "ORDER BY hire_year",
           nativeQuery = true)
    List<Object[]> getDetailedHiringStatisticsNative();

    // Full-text search (PostgreSQL-specific for advanced testing)
    @Query(value = "SELECT e.* FROM employees e WHERE " +
                   "to_tsvector('english', CONCAT(e.first_name, ' ', e.last_name, ' ', COALESCE(e.email, ''))) " +
                   "@@ plainto_tsquery('english', ?1) AND e.active = true",
           nativeQuery = true)
    List<Employee> searchEmployeesFullText(String searchText);

    // Batch operations (for performance testing)
    @Query("UPDATE Employee e SET e.active = :active WHERE e.department.id = :departmentId")
    int updateActiveStatusByDepartmentId(@Param("active") Boolean active, @Param("departmentId") Long departmentId);

    @Query("UPDATE Employee e SET e.department = null WHERE e.department.id = :departmentId")
    int removeDepartmentAssignment(@Param("departmentId") Long departmentId);
}