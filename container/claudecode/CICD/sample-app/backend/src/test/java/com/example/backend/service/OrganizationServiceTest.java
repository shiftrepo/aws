package com.example.backend.service;

import com.example.backend.entity.Organization;
import com.example.backend.repository.OrganizationRepository;
import com.example.common.dto.OrganizationDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import javax.persistence.EntityNotFoundException;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * OrganizationService のテストクラス
 * JaCoCo カバレッジ 80% 以上を目標
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("OrganizationService のテスト")
class OrganizationServiceTest {

    @Mock
    private OrganizationRepository organizationRepository;

    @InjectMocks
    private OrganizationService organizationService;

    private Organization sampleOrganization;
    private OrganizationDto sampleDto;

    @BeforeEach
    void setUp() {
        LocalDateTime now = LocalDateTime.now();

        sampleOrganization = Organization.builder()
                .id(1L)
                .name("テスト組織")
                .description("テスト用の組織です")
                .createdAt(now)
                .updatedAt(now)
                .build();

        sampleDto = OrganizationDto.builder()
                .id(1L)
                .name("テスト組織")
                .description("テスト用の組織です")
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    @DisplayName("全組織一覧取得 - 正常系")
    void findAll_Success() {
        // Given
        List<Organization> organizations = Arrays.asList(sampleOrganization);
        when(organizationRepository.findAll()).thenReturn(organizations);

        // When
        List<OrganizationDto> result = organizationService.findAll();

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テスト組織");
        verify(organizationRepository).findAll();
    }

    @Test
    @DisplayName("組織ID指定取得 - 正常系")
    void findById_Success() {
        // Given
        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));

        // When
        OrganizationDto result = organizationService.findById(1L);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("テスト組織");
        verify(organizationRepository).findById(1L);
    }

    @Test
    @DisplayName("組織ID指定取得 - 存在しない組織")
    void findById_NotFound() {
        // Given
        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> organizationService.findById(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(organizationRepository).findById(999L);
    }

    @Test
    @DisplayName("組織作成 - 正常系")
    void create_Success() {
        // Given
        OrganizationDto createDto = OrganizationDto.builder()
                .name("新規組織")
                .description("新しい組織です")
                .build();

        Organization savedOrganization = Organization.builder()
                .id(2L)
                .name("新規組織")
                .description("新しい組織です")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        when(organizationRepository.existsByName("新規組織")).thenReturn(false);
        when(organizationRepository.save(any(Organization.class))).thenReturn(savedOrganization);

        // When
        OrganizationDto result = organizationService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("新規組織");
        verify(organizationRepository).existsByName("新規組織");
        verify(organizationRepository).save(any(Organization.class));
    }

    @Test
    @DisplayName("組織作成 - 名前重複エラー")
    void create_DuplicateName() {
        // Given
        OrganizationDto createDto = OrganizationDto.builder()
                .name("重複組織")
                .description("重複する組織名です")
                .build();

        when(organizationRepository.existsByName("重複組織")).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> organizationService.create(createDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("組織名が既に存在します: 重複組織");

        verify(organizationRepository).existsByName("重複組織");
    }

    @Test
    @DisplayName("組織更新 - 正常系")
    void update_Success() {
        // Given
        OrganizationDto updateDto = OrganizationDto.builder()
                .name("更新組織")
                .description("更新された組織です")
                .build();

        Organization updatedOrganization = Organization.builder()
                .id(1L)
                .name("更新組織")
                .description("更新された組織です")
                .createdAt(sampleOrganization.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(organizationRepository.existsByNameAndIdNot("更新組織", 1L)).thenReturn(false);
        when(organizationRepository.save(any(Organization.class))).thenReturn(updatedOrganization);

        // When
        OrganizationDto result = organizationService.update(1L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("更新組織");
        verify(organizationRepository).findById(1L);
        verify(organizationRepository).existsByNameAndIdNot("更新組織", 1L);
        verify(organizationRepository).save(any(Organization.class));
    }

    @Test
    @DisplayName("組織更新 - 存在しない組織")
    void update_NotFound() {
        // Given
        OrganizationDto updateDto = OrganizationDto.builder()
                .name("更新組織")
                .description("更新された組織です")
                .build();

        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> organizationService.update(999L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(organizationRepository).findById(999L);
    }

    @Test
    @DisplayName("組織更新 - 名前重複エラー")
    void update_DuplicateName() {
        // Given
        OrganizationDto updateDto = OrganizationDto.builder()
                .name("重複組織")
                .description("重複する組織名です")
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(organizationRepository.existsByNameAndIdNot("重複組織", 1L)).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> organizationService.update(1L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("組織名が既に存在します: 重複組織");

        verify(organizationRepository).findById(1L);
        verify(organizationRepository).existsByNameAndIdNot("重複組織", 1L);
    }

    @Test
    @DisplayName("組織削除 - 正常系")
    void delete_Success() {
        // Given
        when(organizationRepository.existsById(1L)).thenReturn(true);

        // When
        organizationService.delete(1L);

        // Then
        verify(organizationRepository).existsById(1L);
        verify(organizationRepository).deleteById(1L);
    }

    @Test
    @DisplayName("組織削除 - 存在しない組織")
    void delete_NotFound() {
        // Given
        when(organizationRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> organizationService.delete(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(organizationRepository).existsById(999L);
    }
}