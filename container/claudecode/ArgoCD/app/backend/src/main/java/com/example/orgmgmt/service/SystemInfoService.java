package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.SystemInfoDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.Flyway;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.time.Instant;

/**
 * Service for gathering system information including pod name,
 * Flyway version, and database connectivity status.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class SystemInfoService {

    private final DataSource dataSource;
    private final Flyway flyway;

    /**
     * Retrieves current system information.
     *
     * @param sessionId Current HTTP session ID
     * @return SystemInfoDTO containing pod name, session ID, Flyway version, DB status, and timestamp
     */
    public SystemInfoDTO getSystemInfo(String sessionId) {
        return SystemInfoDTO.builder()
                .podName(getPodName())
                .sessionId(sessionId)
                .flywayVersion(getFlywayVersion())
                .databaseStatus(checkDatabaseConnectivity())
                .timestamp(Instant.now())
                .build();
    }

    /**
     * Gets the pod/container name from environment variables.
     * Checks POD_NAME first (Kubernetes downward API), then HOSTNAME,
     * finally falls back to local hostname.
     */
    private String getPodName() {
        String podName = System.getenv("POD_NAME");
        if (podName != null && !podName.isEmpty()) {
            return podName;
        }

        String hostname = System.getenv("HOSTNAME");
        if (hostname != null && !hostname.isEmpty()) {
            return hostname;
        }

        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (UnknownHostException e) {
            log.warn("Failed to get hostname", e);
            return "unknown";
        }
    }

    /**
     * Retrieves the current Flyway migration version from the database.
     * Queries flyway_schema_history for the latest installed migration.
     */
    private String getFlywayVersion() {
        try {
            JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
            String version = jdbcTemplate.queryForObject(
                    "SELECT version FROM flyway_schema_history WHERE success = true ORDER BY installed_rank DESC LIMIT 1",
                    String.class
            );
            return version != null ? version : "unknown";
        } catch (Exception e) {
            log.error("Failed to retrieve Flyway version", e);
            return "error";
        }
    }

    /**
     * Checks database connectivity by querying the organizations table.
     * Returns "OK" if successful, otherwise returns error message.
     */
    private String checkDatabaseConnectivity() {
        try {
            JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
            jdbcTemplate.queryForObject("SELECT COUNT(*) FROM organizations", Integer.class);
            return "OK";
        } catch (Exception e) {
            log.error("Database connectivity check failed", e);
            return "Error: " + e.getMessage();
        }
    }
}
