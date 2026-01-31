package com.example.employee;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Test Spring Boot application configuration for employee-core module.
 *
 * This class provides the necessary @SpringBootApplication configuration
 * for running tests in the employee-core module independently.
 */
@SpringBootApplication
@EnableJpaAuditing
@EnableTransactionManagement
public class TestApplication {

    public static void main(String[] args) {
        SpringApplication.run(TestApplication.class, args);
    }
}