package com.example.employee.config;

import com.example.employee.testutils.TestDataFactory;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.core.env.Environment;

/**
 * Configuration for test data management.
 *
 * Provides beans for loading and managing test data across different
 * test scenarios. Supports YAML-based test data configuration and
 * automatic test data cleanup.
 */
@TestConfiguration
@Import({TestDataFactory.class})
public class TestDataConfig {

    /**
     * Test data profile resolver.
     * Determines which test data profile to use based on system properties
     * and environment configuration.
     */
    @Bean
    public TestDataProfileResolver testDataProfileResolver(Environment environment) {
        return new TestDataProfileResolver(environment);
    }

    /**
     * Test data profile resolver implementation.
     */
    public static class TestDataProfileResolver {
        private final Environment environment;

        public TestDataProfileResolver(Environment environment) {
            this.environment = environment;
        }

        public String getActiveProfile() {
            // Check system property first
            String profile = System.getProperty("testdata.profile");
            if (profile != null && !profile.isEmpty()) {
                return profile;
            }

            // Check environment property
            profile = environment.getProperty("testdata.profile");
            if (profile != null && !profile.isEmpty()) {
                return profile;
            }

            // Check Spring profiles
            String[] activeProfiles = environment.getActiveProfiles();
            for (String activeProfile : activeProfiles) {
                if (activeProfile.startsWith("testdata-")) {
                    return activeProfile.substring("testdata-".length());
                }
            }

            // Default profile
            return "basic";
        }

        public boolean isValidationOnly() {
            return "true".equals(System.getProperty("testdata.validate-only", "false"));
        }

        public boolean isRefreshEnabled() {
            return "true".equals(System.getProperty("testdata.refresh", "false"));
        }

        public String getDataSource() {
            return System.getProperty("testdata.source", "yaml");
        }

        public String getCustomFile() {
            return System.getProperty("testdata.file");
        }
    }
}