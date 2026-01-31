package com.example.employee;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Main entry point for the Employee Management System.
 *
 * This containerized application demonstrates comprehensive testing strategies
 * for PostgreSQL database integration with Spring Boot.
 */
@SpringBootApplication
@EnableJpaAuditing
@EnableTransactionManagement
public class EmployeeManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(EmployeeManagementApplication.class, args);
    }
}