package com.example.employee.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Database configuration for the Employee Management System.
 *
 * Configures JPA repositories and transaction management for PostgreSQL integration.
 * Supports both development and test environments with appropriate connection pooling.
 */
@Configuration
@EnableJpaRepositories(basePackages = "com.example.employee.repository")
@EnableJpaAuditing
@EnableTransactionManagement
public class DatabaseConfig {

    // Additional database configuration can be added here if needed
    // For now, relying on Spring Boot auto-configuration with application properties
}