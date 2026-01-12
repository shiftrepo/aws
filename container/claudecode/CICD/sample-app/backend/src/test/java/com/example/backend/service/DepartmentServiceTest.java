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
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * DepartmentService のテストクラス
 * JaCoCo カバレッジ 100% を目標
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

    private Organization sampleOrganization;
    private Department sampleDepartment;
    private Department sampleParentDepartment;
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

        sampleParentDepartment = Department.builder()
                .id(1L)
                .name("親部門")
                .description("親部門の説明")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(now)
                .updatedAt(now)
                .build();
        sampleParentDepartment.setOrganization(sampleOrganization);

        sampleDepartment = Department.builder()
                .id(2L)
                .name("テスト部門")
                .description("テスト用の部門です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .createdAt(now)
                .updatedAt(now)
                .build();
        sampleDepartment.setOrganization(sampleOrganization);
        sampleDepartment.setParentDepartment(sampleParentDepartment);

        sampleDto = DepartmentDto.builder()
                .id(2L)
                .name("テスト部門")
                .description("テスト用の部門です")
                .organizationId(1L)
                .organizationName("テスト組織")
                .parentDepartmentId(1L)
                .parentDepartmentName("親部門")
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
        assertThat(result.get(0).getOrganizationName()).isEqualTo("テスト組織");
        assertThat(result.get(0).getParentDepartmentName()).isEqualTo("親部門");
        verify(departmentRepository).findAll();
    }

    @Test
    @DisplayName("全部門一覧取得 - 空のリスト")
    void findAll_EmptyList() {
        // Given
        when(departmentRepository.findAll()).thenReturn(Collections.emptyList());

        // When
        List<DepartmentDto> result = departmentService.findAll();

        // Then
        assertThat(result).isEmpty();
        verify(departmentRepository).findAll();
    }

    @Test
    @DisplayName("部門ID指定取得 - 正常系")
    void findById_Success() {
        // Given
        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));

        // When
        DepartmentDto result = departmentService.findById(2L);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("テスト部門");
        assertThat(result.getOrganizationId()).isEqualTo(1L);
        assertThat(result.getOrganizationName()).isEqualTo("テスト組織");
        assertThat(result.getParentDepartmentId()).isEqualTo(1L);
        assertThat(result.getParentDepartmentName()).isEqualTo("親部門");
        verify(departmentRepository).findById(2L);
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
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.findByOrganizationIdOrderByName(1L))
                .thenReturn(Arrays.asList(sampleDepartment));

        // When
        List<DepartmentDto> result = departmentService.findByOrganizationId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テスト部門");
        assertThat(result.get(0).getOrganizationId()).isEqualTo(1L);
        verify(organizationRepository).existsById(1L);
        verify(departmentRepository).findByOrganizationIdOrderByName(1L);
    }

    @Test
    @DisplayName("組織IDで部門一覧取得 - 組織が存在しない")
    void findByOrganizationId_OrganizationNotFound() {
        // Given
        when(organizationRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> departmentService.findByOrganizationId(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(organizationRepository).existsById(999L);
        verify(departmentRepository, never()).findByOrganizationIdOrderByName(anyLong());
    }

    @Test
    @DisplayName("部門作成 - 正常系（親部門なし）")
    void create_Success_WithoutParent() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department savedDepartment = Department.builder()
                .id(3L)
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
        assertThat(result.getId()).isEqualTo(3L);
        assertThat(result.getName()).isEqualTo("新規部門");
        assertThat(result.getOrganizationId()).isEqualTo(1L);
        assertThat(result.getParentDepartmentId()).isNull();
        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "新規部門");
        verify(departmentRepository).save(any(Department.class));
    }

    @Test
    @DisplayName("部門作成 - 正常系（親部門あり）")
    void create_Success_WithParent() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("子部門")
                .description("子部門の説明")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department savedDepartment = Department.builder()
                .id(4L)
                .name("子部門")
                .description("子部門の説明")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        savedDepartment.setOrganization(sampleOrganization);
        savedDepartment.setParentDepartment(sampleParentDepartment);

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "子部門")).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleParentDepartment));
        when(departmentRepository.save(any(Department.class))).thenReturn(savedDepartment);

        // When
        DepartmentDto result = departmentService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(4L);
        assertThat(result.getName()).isEqualTo("子部門");
        assertThat(result.getParentDepartmentId()).isEqualTo(1L);
        assertThat(result.getParentDepartmentName()).isEqualTo("親部門");
        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "子部門");
        verify(departmentRepository).findById(1L);
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
        verify(departmentRepository, never()).save(any(Department.class));
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
                .hasMessage("組織内に同名の部門が既に存在します: 重複部門");

        verify(organizationRepository).findById(1L);
        verify(departmentRepository).existsByOrganizationIdAndName(1L, "重複部門");
        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門作成 - 親部門が存在しない")
    void create_ParentDepartmentNotFound() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(1L)
                .parentDepartmentId(999L)
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "新規部門")).thenReturn(false);
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.create(createDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("親部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門作成 - 親部門が異なる組織に属している")
    void create_ParentDepartmentDifferentOrganization() {
        // Given
        DepartmentDto createDto = DepartmentDto.builder()
                .name("新規部門")
                .description("新しい部門です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department parentDeptDifferentOrg = Department.builder()
                .id(1L)
                .name("他組織の親部門")
                .organizationId(2L) // 異なる組織ID
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(sampleOrganization));
        when(departmentRepository.existsByOrganizationIdAndName(1L, "新規部門")).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(parentDeptDifferentOrg));

        // When & Then
        assertThatThrownBy(() -> departmentService.create(createDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("親部門は同じ組織に属している必要があります");

        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 正常系（親部門なし）")
    void update_Success_WithoutParent() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department updatedDepartment = Department.builder()
                .id(2L)
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(sampleDepartment.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L)).thenReturn(false);
        when(departmentRepository.save(any(Department.class))).thenReturn(updatedDepartment);

        // When
        DepartmentDto result = departmentService.update(2L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("更新部門");
        assertThat(result.getParentDepartmentId()).isNull();
        verify(departmentRepository).findById(2L);
        verify(organizationRepository).existsById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L);
        verify(departmentRepository).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 正常系（親部門あり）")
    void update_Success_WithParent() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department updatedDepartment = Department.builder()
                .id(2L)
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .createdAt(sampleDepartment.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();
        updatedDepartment.setOrganization(sampleOrganization);
        updatedDepartment.setParentDepartment(sampleParentDepartment);

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L)).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleParentDepartment));
        when(departmentRepository.save(any(Department.class))).thenReturn(updatedDepartment);

        // When
        DepartmentDto result = departmentService.update(2L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("更新部門");
        assertThat(result.getParentDepartmentId()).isEqualTo(1L);
        assertThat(result.getParentDepartmentName()).isEqualTo("親部門");
        verify(departmentRepository).findById(2L);
        verify(departmentRepository).findById(1L);
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
        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 組織が存在しない")
    void update_OrganizationNotFound() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(999L)
                .build();

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> departmentService.update(2L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("組織が見つかりません。ID: 999");

        verify(departmentRepository).findById(2L);
        verify(organizationRepository).existsById(999L);
        verify(departmentRepository, never()).save(any(Department.class));
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

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "重複部門", 2L)).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> departmentService.update(2L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("組織内に同名の部門が既に存在します: 重複部門");

        verify(departmentRepository).findById(2L);
        verify(organizationRepository).existsById(1L);
        verify(departmentRepository).existsByOrganizationIdAndNameAndIdNot(1L, "重複部門", 2L);
        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 自分自身を親部門に設定しようとする")
    void update_SelfAsParent() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(2L) // 自分自身のID
                .build();

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> departmentService.update(2L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("自分自身を親部門に設定することはできません");

        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 親部門が存在しない")
    void update_ParentDepartmentNotFound() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(999L)
                .build();

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L)).thenReturn(false);
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> departmentService.update(2L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("親部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門更新 - 親部門が異なる組織に属している")
    void update_ParentDepartmentDifferentOrganization() {
        // Given
        DepartmentDto updateDto = DepartmentDto.builder()
                .name("更新部門")
                .description("更新された部門です")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department parentDeptDifferentOrg = Department.builder()
                .id(1L)
                .name("他組織の親部門")
                .organizationId(2L) // 異なる組織ID
                .build();

        when(departmentRepository.findById(2L)).thenReturn(Optional.of(sampleDepartment));
        when(organizationRepository.existsById(1L)).thenReturn(true);
        when(departmentRepository.existsByOrganizationIdAndNameAndIdNot(1L, "更新部門", 2L)).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(parentDeptDifferentOrg));

        // When & Then
        assertThatThrownBy(() -> departmentService.update(2L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("親部門は同じ組織に属している必要があります");

        verify(departmentRepository, never()).save(any(Department.class));
    }

    @Test
    @DisplayName("部門削除 - 正常系")
    void delete_Success() {
        // Given
        when(departmentRepository.existsById(2L)).thenReturn(true);
        when(departmentRepository.findByParentDepartmentIdOrderByName(2L)).thenReturn(Collections.emptyList());

        // When
        departmentService.delete(2L);

        // Then
        verify(departmentRepository).existsById(2L);
        verify(departmentRepository).findByParentDepartmentIdOrderByName(2L);
        verify(departmentRepository).deleteById(2L);
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
        verify(departmentRepository, never()).deleteById(anyLong());
    }

    @Test
    @DisplayName("部門削除 - 子部門が存在する")
    void delete_HasChildDepartments() {
        // Given
        Department childDepartment = Department.builder()
                .id(3L)
                .name("子部門")
                .parentDepartmentId(2L)
                .build();

        when(departmentRepository.existsById(2L)).thenReturn(true);
        when(departmentRepository.findByParentDepartmentIdOrderByName(2L))
                .thenReturn(Arrays.asList(childDepartment));

        // When & Then
        assertThatThrownBy(() -> departmentService.delete(2L))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("子部門が存在するため削除できません。先に子部門を削除してください。");

        verify(departmentRepository).existsById(2L);
        verify(departmentRepository).findByParentDepartmentIdOrderByName(2L);
        verify(departmentRepository, never()).deleteById(anyLong());
    }

    @Test
    @DisplayName("Entity → DTO変換 - 組織情報がnullの場合")
    void convertToDto_OrganizationNull() {
        // Given
        Department deptWithoutOrg = Department.builder()
                .id(5L)
                .name("組織情報なし部門")
                .description("説明")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        // organization は null

        when(departmentRepository.findById(5L)).thenReturn(Optional.of(deptWithoutOrg));

        // When
        DepartmentDto result = departmentService.findById(5L);

        // Then
        assertThat(result.getId()).isEqualTo(5L);
        assertThat(result.getName()).isEqualTo("組織情報なし部門");
        assertThat(result.getOrganizationName()).isNull();
    }

    @Test
    @DisplayName("Entity → DTO変換 - 親部門情報がnullの場合")
    void convertToDto_ParentDepartmentNull() {
        // Given
        Department deptWithoutParent = Department.builder()
                .id(6L)
                .name("親部門なし部門")
                .description("説明")
                .organizationId(1L)
                .parentDepartmentId(null)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        deptWithoutParent.setOrganization(sampleOrganization);
        // parentDepartment は null

        when(departmentRepository.findById(6L)).thenReturn(Optional.of(deptWithoutParent));

        // When
        DepartmentDto result = departmentService.findById(6L);

        // Then
        assertThat(result.getId()).isEqualTo(6L);
        assertThat(result.getName()).isEqualTo("親部門なし部門");
        assertThat(result.getOrganizationName()).isEqualTo("テスト組織");
        assertThat(result.getParentDepartmentName()).isNull();
    }
}
