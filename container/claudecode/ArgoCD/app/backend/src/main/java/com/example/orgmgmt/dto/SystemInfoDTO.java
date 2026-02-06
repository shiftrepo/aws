package com.example.orgmgmt.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

/**
 * Data Transfer Object for system information.
 * Contains runtime metadata about the application instance.
 */
@Data
@Builder
public class SystemInfoDTO {

    /**
     * Name of the pod/container running this instance.
     * Sourced from POD_NAME or HOSTNAME environment variable.
     */
    private String podName;

    /**
     * Current HTTP session ID for tracking user sessions.
     */
    private String sessionId;

    /**
     * Current Flyway database migration version.
     * Retrieved from flyway_schema_history table.
     */
    private String flywayVersion;

    /**
     * Database connectivity status.
     * "OK" if database is reachable, otherwise error message.
     */
    private String databaseStatus;

    /**
     * Timestamp when this information was collected.
     */
    private Instant timestamp;
}
