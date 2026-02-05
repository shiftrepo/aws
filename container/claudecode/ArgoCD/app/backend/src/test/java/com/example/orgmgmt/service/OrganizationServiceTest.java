package com.example.orgmgmt.service;

import com.example.orgmgmt.dto.OrganizationDTO;
import com.example.orgmgmt.entity.Organization;
import com.example.orgmgmt.exception.DuplicateResourceException;
import com.example.orgmgmt.exception.ResourceNotFoundException;
import com.example.orgmgmt.mapper.EntityMapper;
import com.example.orgmgmt.repository.OrganizationRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrganizationServiceTest {

    @Mock
    private OrganizationRepository organizationRepository;

    @Mock
    private EntityMapper entityMapper;

    @InjectMocks
    private OrganizationService organizationService;

    private Organization testOrganization;
    private OrganizationDTO testOrganizationDTO;

    @BeforeEach
    void setUp() {
        testOrganization = new Organization();
        testOrganization.setId(1L);
        testOrganization.setCode("TEST001");
        testOrganization.setName("Test Organization");
        testOrganization.setDescription("Test description");
        testOrganization.setEstablishedDate(LocalDate.of(2020, 1, 1));
        testOrganization.setActive(true);

        testOrganizationDTO = new OrganizationDTO();
        testOrganizationDTO.setId(1L);
        testOrganizationDTO.setCode("TEST001");
        testOrganizationDTO.setName("Test Organization");
        testOrganizationDTO.setDescription("Test description");
        testOrganizationDTO.setEstablishedDate(LocalDate.of(2020, 1, 1));
        testOrganizationDTO.setActive(true);
    }

    @Test
    void testCreateOrganization_Success() {
        // Given
        when(organizationRepository.existsByCode("TEST001")).thenReturn(false);
        when(entityMapper.toEntity(any(OrganizationDTO.class))).thenReturn(testOrganization);
        when(organizationRepository.save(any(Organization.class))).thenReturn(testOrganization);
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        OrganizationDTO result = organizationService.createOrganization(testOrganizationDTO);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getCode()).isEqualTo("TEST001");
        assertThat(result.getName()).isEqualTo("Test Organization");

        verify(organizationRepository).existsByCode("TEST001");
        verify(organizationRepository).save(any(Organization.class));
        verify(entityMapper).toEntity(any(OrganizationDTO.class));
        verify(entityMapper).toDTO(any(Organization.class));
    }

    @Test
    void testCreateOrganization_DuplicateCode() {
        // Given
        when(organizationRepository.existsByCode("TEST001")).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> organizationService.createOrganization(testOrganizationDTO))
            .isInstanceOf(DuplicateResourceException.class)
            .hasMessageContaining("Organization with code TEST001 already exists");

        verify(organizationRepository).existsByCode("TEST001");
        verify(organizationRepository, never()).save(any(Organization.class));
    }

    @Test
    void testGetOrganizationById_Success() {
        // Given
        when(organizationRepository.findById(1L)).thenReturn(Optional.of(testOrganization));
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        OrganizationDTO result = organizationService.getOrganizationById(1L);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getCode()).isEqualTo("TEST001");

        verify(organizationRepository).findById(1L);
        verify(entityMapper).toDTO(any(Organization.class));
    }

    @Test
    void testGetOrganizationById_NotFound() {
        // Given
        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> organizationService.getOrganizationById(999L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Organization not found with id: 999");

        verify(organizationRepository).findById(999L);
        verify(entityMapper, never()).toDTO(any(Organization.class));
    }

    @Test
    void testGetOrganizationByCode_Success() {
        // Given
        when(organizationRepository.findByCode("TEST001")).thenReturn(Optional.of(testOrganization));
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        OrganizationDTO result = organizationService.getOrganizationByCode("TEST001");

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getCode()).isEqualTo("TEST001");

        verify(organizationRepository).findByCode("TEST001");
        verify(entityMapper).toDTO(any(Organization.class));
    }

    @Test
    void testUpdateOrganization_Success() {
        // Given
        OrganizationDTO updateDTO = new OrganizationDTO();
        updateDTO.setCode("TEST001");
        updateDTO.setName("Updated Organization");
        updateDTO.setDescription("Updated description");
        updateDTO.setActive(true);

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(testOrganization));
        when(organizationRepository.save(any(Organization.class))).thenReturn(testOrganization);
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        OrganizationDTO result = organizationService.updateOrganization(1L, updateDTO);

        // Then
        assertThat(result).isNotNull();
        verify(organizationRepository).findById(1L);
        verify(organizationRepository).save(any(Organization.class));
        verify(entityMapper).toDTO(any(Organization.class));
    }

    @Test
    void testUpdateOrganization_NotFound() {
        // Given
        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> organizationService.updateOrganization(999L, testOrganizationDTO))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Organization not found with id: 999");

        verify(organizationRepository).findById(999L);
        verify(organizationRepository, never()).save(any(Organization.class));
    }

    @Test
    void testDeleteOrganization_Success() {
        // Given
        when(organizationRepository.findById(1L)).thenReturn(Optional.of(testOrganization));
        doNothing().when(organizationRepository).delete(any(Organization.class));

        // When
        organizationService.deleteOrganization(1L);

        // Then
        verify(organizationRepository).findById(1L);
        verify(organizationRepository).delete(testOrganization);
    }

    @Test
    void testDeleteOrganization_NotFound() {
        // Given
        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> organizationService.deleteOrganization(999L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Organization not found with id: 999");

        verify(organizationRepository).findById(999L);
        verify(organizationRepository, never()).delete(any(Organization.class));
    }

    @Test
    void testGetAllOrganizations() {
        // Given
        List<Organization> organizations = Arrays.asList(testOrganization);
        Page<Organization> organizationPage = new PageImpl<>(organizations);
        Pageable pageable = PageRequest.of(0, 10);

        when(organizationRepository.searchOrganizations(null, null, null, null, pageable))
            .thenReturn(organizationPage);
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        Page<OrganizationDTO> result = organizationService.searchOrganizations(null, null, null, null, pageable);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        verify(organizationRepository).searchOrganizations(null, null, null, null, pageable);
    }

    @Test
    void testGetActiveOrganizations() {
        // Given
        List<Organization> organizations = Arrays.asList(testOrganization);
        when(organizationRepository.findByActiveTrue()).thenReturn(organizations);
        when(entityMapper.toDTO(any(Organization.class))).thenReturn(testOrganizationDTO);

        // When
        List<OrganizationDTO> result = organizationService.getActiveOrganizations();

        // Then
        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        verify(organizationRepository).findByActiveTrue();
    }
}
