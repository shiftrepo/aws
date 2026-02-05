package com.example.orgmgmt.controller;

import com.example.orgmgmt.dto.OrganizationDTO;
import com.example.orgmgmt.exception.DuplicateResourceException;
import com.example.orgmgmt.exception.ResourceNotFoundException;
import com.example.orgmgmt.service.OrganizationService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OrganizationController.class)
class OrganizationControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrganizationService organizationService;

    @Autowired
    private ObjectMapper objectMapper;

    private OrganizationDTO testOrganizationDTO;

    @BeforeEach
    void setUp() {
        testOrganizationDTO = new OrganizationDTO();
        testOrganizationDTO.setId(1L);
        testOrganizationDTO.setCode("TEST001");
        testOrganizationDTO.setName("Test Organization");
        testOrganizationDTO.setDescription("Test description");
        testOrganizationDTO.setEstablishedDate(LocalDate.of(2020, 1, 1));
        testOrganizationDTO.setActive(true);
    }

    @Test
    void testCreateOrganization_Success() throws Exception {
        // Given
        when(organizationService.createOrganization(any(OrganizationDTO.class)))
            .thenReturn(testOrganizationDTO);

        // When & Then
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganizationDTO)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.code").value("TEST001"))
            .andExpect(jsonPath("$.name").value("Test Organization"))
            .andExpect(jsonPath("$.description").value("Test description"))
            .andExpect(jsonPath("$.active").value(true));

        verify(organizationService).createOrganization(any(OrganizationDTO.class));
    }

    @Test
    void testCreateOrganization_DuplicateCode() throws Exception {
        // Given
        when(organizationService.createOrganization(any(OrganizationDTO.class)))
            .thenThrow(new DuplicateResourceException("Organization with code TEST001 already exists"));

        // When & Then
        mockMvc.perform(post("/api/organizations")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganizationDTO)))
            .andExpect(status().isConflict());

        verify(organizationService).createOrganization(any(OrganizationDTO.class));
    }

    @Test
    void testGetOrganizationById_Success() throws Exception {
        // Given
        when(organizationService.getOrganizationById(1L))
            .thenReturn(testOrganizationDTO);

        // When & Then
        mockMvc.perform(get("/api/organizations/{id}", 1L))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.code").value("TEST001"))
            .andExpect(jsonPath("$.name").value("Test Organization"));

        verify(organizationService).getOrganizationById(1L);
    }

    @Test
    void testGetOrganizationById_NotFound() throws Exception {
        // Given
        when(organizationService.getOrganizationById(999L))
            .thenThrow(new ResourceNotFoundException("Organization not found with id: 999"));

        // When & Then
        mockMvc.perform(get("/api/organizations/{id}", 999L))
            .andExpect(status().isNotFound());

        verify(organizationService).getOrganizationById(999L);
    }

    @Test
    void testGetOrganizationByCode_Success() throws Exception {
        // Given
        when(organizationService.getOrganizationByCode("TEST001"))
            .thenReturn(testOrganizationDTO);

        // When & Then
        mockMvc.perform(get("/api/organizations/code/{code}", "TEST001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value("TEST001"))
            .andExpect(jsonPath("$.name").value("Test Organization"));

        verify(organizationService).getOrganizationByCode("TEST001");
    }

    @Test
    void testUpdateOrganization_Success() throws Exception {
        // Given
        OrganizationDTO updatedDTO = new OrganizationDTO();
        updatedDTO.setId(1L);
        updatedDTO.setCode("TEST001");
        updatedDTO.setName("Updated Organization");
        updatedDTO.setActive(true);

        when(organizationService.updateOrganization(eq(1L), any(OrganizationDTO.class)))
            .thenReturn(updatedDTO);

        // When & Then
        mockMvc.perform(put("/api/organizations/{id}", 1L)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updatedDTO)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.name").value("Updated Organization"));

        verify(organizationService).updateOrganization(eq(1L), any(OrganizationDTO.class));
    }

    @Test
    void testUpdateOrganization_NotFound() throws Exception {
        // Given
        when(organizationService.updateOrganization(eq(999L), any(OrganizationDTO.class)))
            .thenThrow(new ResourceNotFoundException("Organization not found with id: 999"));

        // When & Then
        mockMvc.perform(put("/api/organizations/{id}", 999L)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testOrganizationDTO)))
            .andExpect(status().isNotFound());

        verify(organizationService).updateOrganization(eq(999L), any(OrganizationDTO.class));
    }

    @Test
    void testDeleteOrganization_Success() throws Exception {
        // Given
        doNothing().when(organizationService).deleteOrganization(1L);

        // When & Then
        mockMvc.perform(delete("/api/organizations/{id}", 1L))
            .andExpect(status().isNoContent());

        verify(organizationService).deleteOrganization(1L);
    }

    @Test
    void testDeleteOrganization_NotFound() throws Exception {
        // Given
        doThrow(new ResourceNotFoundException("Organization not found with id: 999"))
            .when(organizationService).deleteOrganization(999L);

        // When & Then
        mockMvc.perform(delete("/api/organizations/{id}", 999L))
            .andExpect(status().isNotFound());

        verify(organizationService).deleteOrganization(999L);
    }

    @Test
    void testSearchOrganizations() throws Exception {
        // Given
        List<OrganizationDTO> organizations = Arrays.asList(testOrganizationDTO);
        Page<OrganizationDTO> organizationPage = new PageImpl<>(organizations, PageRequest.of(0, 10), 1);

        when(organizationService.searchOrganizations(
            any(), any(), any(), any(), any()))
            .thenReturn(organizationPage);

        // When & Then
        mockMvc.perform(get("/api/organizations")
                .param("page", "0")
                .param("size", "10")
                .param("name", "Test"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content", hasSize(1)))
            .andExpect(jsonPath("$.content[0].code").value("TEST001"))
            .andExpect(jsonPath("$.totalElements").value(1));

        verify(organizationService).searchOrganizations(any(), any(), any(), any(), any());
    }

    @Test
    void testGetActiveOrganizations() throws Exception {
        // Given
        List<OrganizationDTO> activeOrganizations = Arrays.asList(testOrganizationDTO);
        when(organizationService.getActiveOrganizations()).thenReturn(activeOrganizations);

        // When & Then
        mockMvc.perform(get("/api/organizations/active"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(1)))
            .andExpect(jsonPath("$[0].code").value("TEST001"))
            .andExpect(jsonPath("$[0].active").value(true));

        verify(organizationService).getActiveOrganizations();
    }

    @Test
    void testGetOrganizationStatistics() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/organizations/{id}/statistics", 1L))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.organizationId").value(1))
            .andExpect(jsonPath("$.departmentCount").exists())
            .andExpect(jsonPath("$.userCount").exists());
    }
}
