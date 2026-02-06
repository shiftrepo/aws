package com.example.orgmgmt.controller;

import com.example.orgmgmt.dto.SystemInfoDTO;
import com.example.orgmgmt.service.SystemInfoService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller for system information endpoints.
 * Provides runtime metadata about the application instance.
 */
@RestController
@RequestMapping("/api/system")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class SystemInfoController {

    private final SystemInfoService systemInfoService;

    /**
     * Retrieves current system information including pod name, session ID,
     * Flyway version, database status, and timestamp.
     *
     * @param session Current HTTP session (managed by Spring Session)
     * @return SystemInfoDTO with all system metadata
     */
    @GetMapping("/info")
    public SystemInfoDTO getSystemInfo(HttpSession session) {
        String sessionId = session.getId();
        return systemInfoService.getSystemInfo(sessionId);
    }
}
