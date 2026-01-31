package com.example.employee.config;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Profile;
import org.springframework.test.context.TestPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Test configuration for the Employee Management System.
 *
 * Provides test-specific beans and configuration for different testing scenarios.
 * Supports TestContainers integration and test data management.
 */
@TestConfiguration
@Profile("test")
@TestPropertySource(locations = "classpath:application-test.yml")
public class TestConfig {

    /**
     * PostgreSQL TestContainer for integration tests.
     * Shared across all test classes to improve performance.
     */
    @Bean
    public PostgreSQLContainer<?> postgreSQLContainer() {
        PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
                .withDatabaseName("employee_test_db")
                .withUsername("test_user")
                .withPassword("test_password")
                .withInitScript("sql/test-init.sql");

        postgres.start();

        // Set system properties for Spring Boot to use
        System.setProperty("spring.datasource.url", postgres.getJdbcUrl());
        System.setProperty("spring.datasource.username", postgres.getUsername());
        System.setProperty("spring.datasource.password", postgres.getPassword());

        return postgres;
    }
}