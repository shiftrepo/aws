package com.example.employee.testutils;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.TestComponent;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.transaction.TestTransaction;
import org.springframework.transaction.annotation.Transactional;

import javax.sql.DataSource;
import java.util.List;
import java.util.Map;

/**
 * Database testing utilities for the Employee Management System.
 *
 * Provides helper methods for database operations, cleanup, and verification
 * during testing. Supports transaction management and data validation.
 */
@TestComponent
public class DatabaseTestUtils {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private DataSource dataSource;

    /**
     * Clean all test data from the database.
     * Maintains referential integrity by cleaning in the correct order.
     */
    @Transactional
    public void cleanDatabase() {
        // Clean in order to respect foreign key constraints
        jdbcTemplate.execute("DELETE FROM employees");
        jdbcTemplate.execute("DELETE FROM departments");

        // Reset sequences
        resetSequences();
    }

    /**
     * Reset database sequences to start from 1.
     */
    public void resetSequences() {
        jdbcTemplate.execute("ALTER SEQUENCE departments_id_seq RESTART WITH 1");
        jdbcTemplate.execute("ALTER SEQUENCE employees_id_seq RESTART WITH 1");
    }

    /**
     * Get the current count of records in a table.
     */
    public int getTableCount(String tableName) {
        return jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM " + tableName,
                Integer.class
        );
    }

    /**
     * Check if a table exists in the database.
     */
    public boolean tableExists(String tableName) {
        try {
            jdbcTemplate.queryForObject(
                    "SELECT 1 FROM " + tableName + " LIMIT 1",
                    Integer.class
            );
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Execute a custom SQL script.
     */
    public void executeScript(String sql) {
        jdbcTemplate.execute(sql);
    }

    /**
     * Execute SQL from a resource file.
     */
    public void executeScriptFromResource(String resourcePath) {
        try {
            String sql = readResourceAsString(resourcePath);
            jdbcTemplate.execute(sql);
        } catch (Exception e) {
            throw new RuntimeException("Failed to execute script from resource: " + resourcePath, e);
        }
    }

    /**
     * Get all records from a table as a list of maps.
     */
    public List<Map<String, Object>> getAllRecords(String tableName) {
        return jdbcTemplate.queryForList("SELECT * FROM " + tableName);
    }

    /**
     * Verify that a table has the expected number of records.
     */
    public boolean verifyTableCount(String tableName, int expectedCount) {
        return getTableCount(tableName) == expectedCount;
    }

    /**
     * Check if database connection is healthy.
     */
    public boolean isDatabaseHealthy() {
        try {
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Get database metadata information.
     */
    public Map<String, Object> getDatabaseInfo() {
        return Map.of(
                "employeeCount", getTableCount("employees"),
                "departmentCount", getTableCount("departments"),
                "databaseHealthy", isDatabaseHealthy(),
                "currentTimestamp", jdbcTemplate.queryForObject("SELECT CURRENT_TIMESTAMP", String.class)
        );
    }

    /**
     * Force commit the current transaction (useful for testing transaction behavior).
     */
    public void commitTransaction() {
        if (TestTransaction.isActive()) {
            TestTransaction.flagForCommit();
            TestTransaction.end();
            TestTransaction.start();
        }
    }

    /**
     * Force rollback the current transaction (useful for testing transaction behavior).
     */
    public void rollbackTransaction() {
        if (TestTransaction.isActive()) {
            TestTransaction.flagForRollback();
            TestTransaction.end();
            TestTransaction.start();
        }
    }

    /**
     * Create a savepoint in the current transaction.
     */
    public void createSavepoint(String name) {
        jdbcTemplate.execute("SAVEPOINT " + name);
    }

    /**
     * Rollback to a savepoint.
     */
    public void rollbackToSavepoint(String name) {
        jdbcTemplate.execute("ROLLBACK TO SAVEPOINT " + name);
    }

    /**
     * Insert test data using SQL.
     */
    public void insertTestData(String tableName, Map<String, Object> data) {
        StringBuilder columns = new StringBuilder();
        StringBuilder values = new StringBuilder();
        Object[] params = new Object[data.size()];

        int i = 0;
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            if (i > 0) {
                columns.append(", ");
                values.append(", ");
            }
            columns.append(entry.getKey());
            values.append("?");
            params[i] = entry.getValue();
            i++;
        }

        String sql = String.format("INSERT INTO %s (%s) VALUES (%s)",
                tableName, columns.toString(), values.toString());

        jdbcTemplate.update(sql, params);
    }

    /**
     * Update test data using SQL.
     */
    public void updateTestData(String tableName, Map<String, Object> data, String whereClause, Object... whereParams) {
        StringBuilder setClause = new StringBuilder();
        Object[] params = new Object[data.size() + whereParams.length];

        int i = 0;
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            if (i > 0) {
                setClause.append(", ");
            }
            setClause.append(entry.getKey()).append(" = ?");
            params[i] = entry.getValue();
            i++;
        }

        // Add where parameters
        System.arraycopy(whereParams, 0, params, data.size(), whereParams.length);

        String sql = String.format("UPDATE %s SET %s WHERE %s",
                tableName, setClause.toString(), whereClause);

        jdbcTemplate.update(sql, params);
    }

    /**
     * Delete test data using SQL.
     */
    public void deleteTestData(String tableName, String whereClause, Object... params) {
        String sql = String.format("DELETE FROM %s WHERE %s", tableName, whereClause);
        jdbcTemplate.update(sql, params);
    }

    // Private helper methods

    private String readResourceAsString(String resourcePath) throws Exception {
        // This would be implemented to read resource files
        // For now, returning a placeholder
        return "-- Placeholder for resource content";
    }
}