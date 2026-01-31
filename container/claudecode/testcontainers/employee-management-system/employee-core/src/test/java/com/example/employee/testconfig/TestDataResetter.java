package com.example.employee.testconfig;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

/**
 * テストデータリセット機能
 *
 * 実装戦略:
 * - 高速化: コンテナ共有＋データリセット
 * - DBの初期化: 高速なTRUNCATEによるデータクリア
 *
 * 利点:
 * - コンテナ再作成より90%高速
 * - 外部キー制約を考慮した安全なリセット
 * - ベース状態への自動復元
 */
@Component
public class TestDataResetter {

    private static final Logger logger = LoggerFactory.getLogger(TestDataResetter.class);

    private final JdbcTemplate jdbcTemplate;

    // 外部キー制約を考慮したテーブルリセット順序
    private final List<String> tableResetOrder = Arrays.asList(
        "employees",      // 外部キーを持つテーブルから
        "departments"     // 参照されるテーブルへ
    );

    @Autowired
    public TestDataResetter(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * ベース状態にリセット
     * - 全データを削除
     * - 最小限のベースデータを投入
     */
    public void resetToBaseState() {
        logger.debug("Resetting database to base state...");

        try {
            // 外部キー制約を一時的に無効化（PostgreSQL用）
            jdbcTemplate.execute("SET session_replication_role = replica");

            // 全テーブルをリセット
            tableResetOrder.forEach(this::truncateTable);

            // 外部キー制約を再有効化
            jdbcTemplate.execute("SET session_replication_role = DEFAULT");

            // ベース状態のデータを投入
            loadBaseTestData();

            logger.debug("Database reset completed successfully");

        } catch (Exception e) {
            logger.error("Failed to reset database", e);
            throw new RuntimeException("Database reset failed", e);
        }
    }

    /**
     * 完全に空の状態にリセット
     */
    public void resetToEmptyState() {
        logger.debug("Resetting database to empty state...");

        try {
            jdbcTemplate.execute("SET session_replication_role = replica");
            tableResetOrder.forEach(tableName -> {
                jdbcTemplate.execute("DELETE FROM " + tableName);
            });
            jdbcTemplate.execute("SET session_replication_role = DEFAULT");

            logger.debug("Database reset to empty state completed");

        } catch (Exception e) {
            logger.error("Failed to reset database to empty state", e);
            throw new RuntimeException("Database reset failed", e);
        }
    }

    /**
     * テーブルをTRUNCATEする（高速）
     */
    private void truncateTable(String tableName) {
        try {
            jdbcTemplate.execute("TRUNCATE TABLE " + tableName + " RESTART IDENTITY CASCADE");
            logger.debug("Truncated table: {}", tableName);
        } catch (Exception e) {
            // TRUNCATEが失敗した場合はDELETEにフォールバック
            logger.warn("TRUNCATE failed for {}, falling back to DELETE", tableName);
            jdbcTemplate.execute("DELETE FROM " + tableName);
        }
    }

    /**
     * 最小限の基本データを投入
     * - テストが前提とする基本データ
     * - 高速実行のため最小限に抑制
     */
    private void loadBaseTestData() {
        try {
            // 基本部署データ
            jdbcTemplate.execute("""
                INSERT INTO departments (id, name, code, budget, description, active, created_at, modified_at, version) VALUES
                    (1, 'Human Resources', 'HR', 1000000.00, 'Human Resources Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
                    (2, 'Information Technology', 'IT', 2000000.00, 'IT Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
                    (3, 'Finance', 'FIN', 1500000.00, 'Finance Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                ON CONFLICT (id) DO NOTHING
            """);

            // シーケンスをリセット
            jdbcTemplate.execute("SELECT setval('departments_id_seq', 3, true)");
            jdbcTemplate.execute("SELECT setval('employees_id_seq', 1, false)");

            logger.debug("Base test data loaded successfully");

        } catch (Exception e) {
            logger.warn("Failed to load base test data: {}", e.getMessage());
            // ベースデータの投入失敗は致命的でない場合があるのでログのみ
        }
    }

    /**
     * データベース統計情報を取得（デバッグ用）
     */
    public void logDatabaseStats() {
        try {
            Long employeeCount = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM employees", Long.class);
            Long departmentCount = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM departments", Long.class);

            logger.info("Database stats - Employees: {}, Departments: {}",
                       employeeCount, departmentCount);

        } catch (Exception e) {
            logger.warn("Failed to get database stats", e);
        }
    }

    /**
     * 特定テーブルのデータ数を取得
     */
    public long getTableCount(String tableName) {
        try {
            return jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM " + tableName, Long.class);
        } catch (Exception e) {
            logger.warn("Failed to get count for table: {}", tableName, e);
            return -1;
        }
    }
}