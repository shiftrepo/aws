package com.example.backend.service;

import com.example.backend.entity.Department;
import com.example.backend.entity.Organization;
import com.example.backend.repository.DepartmentRepository;
import com.example.backend.repository.OrganizationRepository;
import com.example.common.dto.DepartmentDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import jakarta.persistence.EntityNotFoundException;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;

/**
 * DepartmentService のテストクラス
 * JaCoCo カバレッジ 50% 以上を目標
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("DepartmentService のテスト")
class DepartmentServiceTest {

    @Mock
    private DepartmentRepository departmentRepository;

    @Mock
    private OrganizationRepository organizationRepository;

    @InjectMocks
    private DepartmentService departmentService;

    private Department sampleDepartment;
    private Organization sampleOrganization;
    private DepartmentDto sampleDto;

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

        sampleDepartment = Department.builder()
                .id(1L)
                .name("テスト部門")
                .description("テスト用の部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(now)
                .updatedAt(now)
                .build();

        sampleDto = DepartmentDto.builder()
                .id(1L)
                .name("テスト部門")
                .description("テスト用の部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    @DisplayName("全部門一覧取得 - 正常系")
    void findAll_Success() {
        // Given
        List<Department> departments = Arrays.asList(sampleDepartment);
        when(departmentRepository.findAll()).thenReturn(departments);

        // When
        List<DepartmentDto> result = departmentService.findAll();

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テスト部門");
        verify(departmentRepository).findAll();
    }

    @Test
    @DisplayName("部門ID指定取得 - 正常系")
    void findById_Success() {
        // Given
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));

        // When
        DepartmentDto result = departmentService.findById(1L);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("テスト部門");
        verify(departmentRepository).findById(1L);
    }

    @Test
    @DisplayName("部門ID指定取得 - 存在しない部門")
    void findById_NotFound() {
        // Given
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.findById(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
    }

    @Test
    @DisplayName("組織IDで部門一覧取得 - 正常系")
    void findByOrganizationId_Success() {
        // Given
        List<Department> departments = Arrays.asList(sampleDepartment);
        when(departmentRepository.findByOrganizationIdOrderByName(1L)).thenReturn(departments);

        // When
        List<DepartmentDto> result = departmentService.findByOrganizationId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テスト部門");
        verify(departmentRepository).findByOrganizationIdOrderByName(1L);
    }

    @Test
    @DisplayName("部門作成 - 正常系")
    void create_Success() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department savedDepartment = Department.builder()
                .id(2L)
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "新規部門")).thenReturn(false);
        when(departmentRepository.save(any(Department.class))).thenReturn(savedDepartment);

        // When
        DepartmentDto result = departmentService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("新規部門");
        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "新規部門");
        verify(departmentRepository).save(any(Department.class));
    }

    @Test
    @DisplayName("部門作成 - 組織が存在しない")
    void create_OrganizationNotFound() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(999L)
                .build();

        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.create(createDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(organizationRepository).findById(999L);
    }

    @Test
    @DisplayName("部門作成 - 名前重複エラー")
    void create_DuplicateName() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("重複部門")
                .description("重複する部門名です")
                .organizationId(1L)
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "重複部門")).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> departmentService.create(createDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("部門名が既に存在します: 重複部門");

        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "重複部門");
    }

    @Test
    @DisplayName("部門更新 - 正常系")
    void update_Success() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department updatedDepartment = Department.builder()
                .id(1L)
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(sampleDepartment.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L)).thenReturn(false);
        when(departmentRepository.save(any(Department.class))).thenReturn(updatedDepartment);

        // When
        DepartmentDto result = departmentService.update(1L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("更新部門");
        verify(departmentRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L);
        verify(departmentRepository).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 存在しない部門")
    void update_NotFound() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .build();

        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.update(999L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
    }

    @Test
    @DisplayName("部門更新 - 名前重複エラー")
    void update_DuplicateName() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("重複部門")
                .description("重複する部門名です")
                .organizationId(1L)
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "重複部門", 1L)).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> departmentService.update(1L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("部門名が既に存在します: 重複部門");

        verify(departmentRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "重複部門", 1L);
    }

    @Test
    @DisplayName("部門削除 - 正常系")
    void delete_Success() {
        // Given
        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.findByParentDepartmentIdOrderByName(1L)).thenReturn(Collections.emptyList());

        // When
        departmentService.delete(1L);

        // Then
        verify(departmentRepository).existsById(1L);
        verify(departmentRepository).findByParentDepartmentIdOrderByName(1L);
        verify(departmentRepository).deleteById(1L);
    }

    @Test
    @DisplayName("部門削除 - 存在しない部門")
    void delete_NotFound() {
        // Given
        when(departmentRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> departmentService.delete(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).existsById(999L);
    }

    @Test
    @DisplayName("部門削除 - 子部門が存在")
    void delete_HasChildren() {
        // Given
        Department childDepartment = Department.builder()
                .id(2L)
                .name("子部門")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.findByParentDepartmentIdOrderByName(1L))
                .thenReturn(Arrays.asList(childDepartment));

        // When & Then
        assertThatThrownBy(() -> departmentService.delete(1L))
                .isInstanceOf(IllegalStateException.class)
                .hasMessage("子部門が存在するため削除できません。まず子部門を削除してください。");

        verify(departmentRepository).existsById(1L);
        verify(departmentRepository).findByParentDepartmentIdOrderByName(1L);
        verify(departmentRepository, never()).deleteById(anyLong());
    }

    @Test
    @DisplayName("部門作成 - 親部門IDあり（正常系）")
    void create_WithParentDepartment() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("子部門")
                .description("親部門の配下です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department parentDepartment = Department.builder()
                .id(1L)
                .name("親部門")
                .organizationId(1L)
                .build();

        Department savedDepartment = Department.builder()
                .id(3L)
                .name("子部門")
                .description("親部門の配下です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "子部門")).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(parentDepartment));
        when(departmentRepository.save(any(Department.class))).thenReturn(savedDepartment);

        // When
        DepartmentDto result = departmentService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(3L);
        assertThat(result.getName()).isEqualTo("子部門");
        assertThat(result.getParentDepartmentId()).isEqualTo(1L);
        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "子部門");
        verify(departmentRepository).findById(1L);
        verify(departmentRepository).save(any(Department.class));
    }

    @Test
    @DisplayName("部門作成 - 親部門が存在しない")
    void create_ParentDepartmentNotFound() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("子部門")
                .description("親部門の配下です")
                .organizationId(1L)
                .parentDepartmentId(999L)
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "子部門")).thenReturn(false);
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.create(createDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("親部門が見つかりません。ID: 999");

        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "子部門");
        verify(departmentRepository).findById(999L);
    }

    @Test
    @DisplayName("部門更新 - 親部門IDを設定")
    void update_WithParentDepartmentId() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("親部門を設定します")
                .organizationId(1L)
                .parentDepartmentId(2L)
                .build();

        Department parentDepartment = Department.builder()
                .id(2L)
                .name("親部門")
                .organizationId(1L)
                .build();

        Department updatedDepartment = Department.builder()
                .id(1L)
                .name("更新部門")
                .description("親部門を設定します")
                .organizationId(1L)
                .parentDepartmentId(2L)
                .createdAt(sampleDepartment.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L)).thenReturn(false);
        when(departmentRepository.findById(2L)).thenReturn(Optional.of(parentDepartment));
        when(departmentRepository.save(any(Department.class))).thenReturn(updatedDepartment);
        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));

        // When
        DepartmentDto result = departmentService.update(1L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("更新部門");
        assertThat(result.getParentDepartmentId()).isEqualTo(2L);
        verify(departmentRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L);
        verify(departmentRepository).findById(2L);
        verify(departmentRepository).save(any(Department.class));
        verify(organizationRepository).findById(1L);
    }

    @Test
    @DisplayName("部門更新 - 自分自身を親に設定（循環参照）")
    void update_SelfAsParent() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("自分を親にする")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> departmentService.update(1L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("自分自身を親部門に設定できません");

        verify(departmentRepository, times(2)).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L);
    }

    @Test
    @DisplayName("部門更新 - 親部門が存在しない")
    void update_ParentDepartmentNotFound() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("存在しない親部門")
                .organizationId(1L)
                .parentDepartmentId(999L)
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L)).thenReturn(false);
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.update(1L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("親部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 1L);
        verify(departmentRepository, times(1)).findById(999L);
    }
}
