package com.example.employee.testconfig;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;

/**
 * テスト用データベース設定
 *
 * 実装戦略:
 * - DB状態検証: DB直接クエリの実装
 * - JdbcTemplateによる生SQLアクセス
 */
@TestConfiguration
public class TestDatabaseConfig {

    /**
     * テスト用JdbcTemplate
     * - 直接SQLクエリ実行用
     * - 制約検証、パフォーマンス測定に使用
     */
    @Bean
    @Primary
    public JdbcTemplate testJdbcTemplate(DataSource dataSource) {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        jdbcTemplate.setQueryTimeout(30); // 30秒タイムアウト
        return jdbcTemplate;
    }
}