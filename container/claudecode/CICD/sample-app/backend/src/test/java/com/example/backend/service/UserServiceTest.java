package com.example.backend.service;

import com.example.backend.entity.Department;
import com.example.backend.entity.Organization;
import com.example.backend.entity.User;
import com.example.backend.repository.DepartmentRepository;
import com.example.backend.repository.UserRepository;
import com.example.common.dto.UserDto;
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
 * UserService のテストクラス
 * JaCoCo カバレッジ 100% を目標
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("UserService のテスト")
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private DepartmentRepository departmentRepository;

    @InjectMocks
    private UserService userService;

    private Organization sampleOrganization;
    private Department sampleDepartment;
    private User sampleUser;
    private UserDto sampleDto;

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
                .createdAt(now)
                .updatedAt(now)
                .build();
        sampleDepartment.setOrganization(sampleOrganization);

        sampleUser = User.builder()
                .id(1L)
                .name("テストユーザー")
                .email("test@example.com")
                .departmentId(1L)
                .position("エンジニア")
                .createdAt(now)
                .updatedAt(now)
                .build();
        sampleUser.setDepartment(sampleDepartment);

        sampleDto = UserDto.builder()
                .id(1L)
                .name("テストユーザー")
                .email("test@example.com")
                .departmentId(1L)
                .departmentName("テスト部門")
                .organizationId(1L)
                .organizationName("テスト組織")
                .position("エンジニア")
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    @DisplayName("全ユーザー一覧取得 - 正常系")
    void findAll_Success() {
        // Given
        List<User> users = Arrays.asList(sampleUser);
        when(userRepository.findAll()).thenReturn(users);

        // When
        List<UserDto> result = userService.findAll();

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テストユーザー");
        assertThat(result.get(0).getEmail()).isEqualTo("test@example.com");
        assertThat(result.get(0).getDepartmentName()).isEqualTo("テスト部門");
        assertThat(result.get(0).getOrganizationName()).isEqualTo("テスト組織");
        verify(userRepository).findAll();
    }

    @Test
    @DisplayName("全ユーザー一覧取得 - 空のリスト")
    void findAll_EmptyList() {
        // Given
        when(userRepository.findAll()).thenReturn(Collections.emptyList());

        // When
        List<UserDto> result = userService.findAll();

        // Then
        assertThat(result).isEmpty();
        verify(userRepository).findAll();
    }

    @Test
    @DisplayName("ユーザーID指定取得 - 正常系")
    void findById_Success() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));

        // When
        UserDto result = userService.findById(1L);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("テストユーザー");
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        assertThat(result.getDepartmentId()).isEqualTo(1L);
        assertThat(result.getDepartmentName()).isEqualTo("テスト部門");
        assertThat(result.getOrganizationId()).isEqualTo(1L);
        assertThat(result.getOrganizationName()).isEqualTo("テスト組織");
        assertThat(result.getPosition()).isEqualTo("エンジニア");
        verify(userRepository).findById(1L);
    }

    @Test
    @DisplayName("ユーザーID指定取得 - 存在しないユーザー")
    void findById_NotFound() {
        // Given
        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.findById(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("ユーザーが見つかりません。ID: 999");

        verify(userRepository).findById(999L);
    }

    @Test
    @DisplayName("部門IDでユーザー一覧取得 - 正常系")
    void findByDepartmentId_Success() {
        // Given
        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(userRepository.findByDepartmentIdOrderByName(1L)).thenReturn(Arrays.asList(sampleUser));

        // When
        List<UserDto> result = userService.findByDepartmentId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テストユーザー");
        assertThat(result.get(0).getDepartmentId()).isEqualTo(1L);
        verify(departmentRepository).existsById(1L);
        verify(userRepository).findByDepartmentIdOrderByName(1L);
    }

    @Test
    @DisplayName("部門IDでユーザー一覧取得 - 部門が存在しない")
    void findByDepartmentId_DepartmentNotFound() {
        // Given
        when(departmentRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> userService.findByDepartmentId(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).existsById(999L);
        verify(userRepository, never()).findByDepartmentIdOrderByName(anyLong());
    }

    @Test
    @DisplayName("組織IDでユーザー一覧取得 - 正常系")
    void findByOrganizationId_Success() {
        // Given
        when(userRepository.findByOrganizationId(1L)).thenReturn(Arrays.asList(sampleUser));

        // When
        List<UserDto> result = userService.findByOrganizationId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テストユーザー");
        assertThat(result.get(0).getOrganizationId()).isEqualTo(1L);
        verify(userRepository).findByOrganizationId(1L);
    }

    @Test
    @DisplayName("組織IDでユーザー一覧取得 - 空のリスト")
    void findByOrganizationId_EmptyList() {
        // Given
        when(userRepository.findByOrganizationId(999L)).thenReturn(Collections.emptyList());

        // When
        List<UserDto> result = userService.findByOrganizationId(999L);

        // Then
        assertThat(result).isEmpty();
        verify(userRepository).findByOrganizationId(999L);
    }

    @Test
    @DisplayName("ユーザー作成 - 正常系")
    void create_Success() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("new@example.com")
                .departmentId(1L)
                .position("マネージャー")
                .build();

        User savedUser = User.builder()
                .id(2L)
                .name("新規ユーザー")
                .email("new@example.com")
                .departmentId(1L)
                .position("マネージャー")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        savedUser.setDepartment(sampleDepartment);

        when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        // When
        UserDto result = userService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("新規ユーザー");
        assertThat(result.getEmail()).isEqualTo("new@example.com");
        assertThat(result.getDepartmentId()).isEqualTo(1L);
        assertThat(result.getDepartmentName()).isEqualTo("テスト部門");
        assertThat(result.getPosition()).isEqualTo("マネージャー");
        verify(userRepository).existsByEmail("new@example.com");
        verify(departmentRepository).findById(1L);
        verify(userRepository).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー作成 - メールアドレス重複エラー")
    void create_DuplicateEmail() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("duplicate@example.com")
                .departmentId(1L)
                .position("マネージャー")
                .build();

        when(userRepository.existsByEmail("duplicate@example.com")).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.create(createDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("メールアドレスが既に使用されています: duplicate@example.com");

        verify(userRepository).existsByEmail("duplicate@example.com");
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー作成 - 部門が存在しない")
    void create_DepartmentNotFound() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("new@example.com")
                .departmentId(999L)
                .position("マネージャー")
                .build();

        when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.create(createDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー更新 - 正常系")
    void update_Success() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(1L)
                .position("シニアエンジニア")
                .build();

        User updatedUser = User.builder()
                .id(1L)
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(1L)
                .position("シニアエンジニア")
                .createdAt(sampleUser.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();
        updatedUser.setDepartment(sampleDepartment);

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(userRepository.existsByEmailAndIdNot("updated@example.com", 1L)).thenReturn(false);
        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(userRepository.save(any(User.class))).thenReturn(updatedUser);

        // When
        UserDto result = userService.update(1L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("更新ユーザー");
        assertThat(result.getEmail()).isEqualTo("updated@example.com");
        assertThat(result.getPosition()).isEqualTo("シニアエンジニア");
        verify(userRepository).findById(1L);
        verify(userRepository).existsByEmailAndIdNot("updated@example.com", 1L);
        verify(departmentRepository).existsById(1L);
        verify(userRepository).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー更新 - 存在しないユーザー")
    void update_NotFound() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(1L)
                .position("シニアエンジニア")
                .build();

        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.update(999L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("ユーザーが見つかりません。ID: 999");

        verify(userRepository).findById(999L);
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー更新 - メールアドレス重複エラー")
    void update_DuplicateEmail() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("duplicate@example.com")
                .departmentId(1L)
                .position("シニアエンジニア")
                .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(userRepository.existsByEmailAndIdNot("duplicate@example.com", 1L)).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.update(1L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("メールアドレスが既に使用されています: duplicate@example.com");

        verify(userRepository).findById(1L);
        verify(userRepository).existsByEmailAndIdNot("duplicate@example.com", 1L);
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー更新 - 部門が存在しない")
    void update_DepartmentNotFound() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(999L)
                .position("シニアエンジニア")
                .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(userRepository.existsByEmailAndIdNot("updated@example.com", 1L)).thenReturn(false);
        when(departmentRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> userService.update(1L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(userRepository).findById(1L);
        verify(userRepository).existsByEmailAndIdNot("updated@example.com", 1L);
        verify(departmentRepository).existsById(999L);
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー削除 - 正常系")
    void delete_Success() {
        // Given
        when(userRepository.existsById(1L)).thenReturn(true);

        // When
        userService.delete(1L);

        // Then
        verify(userRepository).existsById(1L);
        verify(userRepository).deleteById(1L);
    }

    @Test
    @DisplayName("ユーザー削除 - 存在しないユーザー")
    void delete_NotFound() {
        // Given
        when(userRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> userService.delete(999L))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("ユーザーが見つかりません。ID: 999");

        verify(userRepository).existsById(999L);
        verify(userRepository, never()).deleteById(anyLong());
    }

    @Test
    @DisplayName("Entity → DTO変換 - 部門情報がnullの場合")
    void convertToDto_DepartmentNull() {
        // Given
        User userWithoutDept = User.builder()
                .id(2L)
                .name("部門情報なしユーザー")
                .email("nodept@example.com")
                .departmentId(1L)
                .position("フリーランス")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        // department は null

        when(userRepository.findById(2L)).thenReturn(Optional.of(userWithoutDept));

        // When
        UserDto result = userService.findById(2L);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("部門情報なしユーザー");
        assertThat(result.getDepartmentName()).isNull();
        assertThat(result.getOrganizationId()).isNull();
        assertThat(result.getOrganizationName()).isNull();
    }

    @Test
    @DisplayName("Entity → DTO変換 - 部門の組織情報がnullの場合")
    void convertToDto_DepartmentOrganizationNull() {
        // Given
        Department deptWithoutOrg = Department.builder()
                .id(2L)
                .name("組織情報なし部門")
                .organizationId(1L)
                .build();
        // organization は null

        User userWithDeptNoOrg = User.builder()
                .id(3L)
                .name("組織情報なしユーザー")
                .email("noorg@example.com")
                .departmentId(2L)
                .position("コンサルタント")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        userWithDeptNoOrg.setDepartment(deptWithoutOrg);

        when(userRepository.findById(3L)).thenReturn(Optional.of(userWithDeptNoOrg));

        // When
        UserDto result = userService.findById(3L);

        // Then
        assertThat(result.getId()).isEqualTo(3L);
        assertThat(result.getName()).isEqualTo("組織情報なしユーザー");
        assertThat(result.getDepartmentName()).isEqualTo("組織情報なし部門");
        assertThat(result.getOrganizationId()).isNull();
        assertThat(result.getOrganizationName()).isNull();
    }

    @Test
    @DisplayName("Entity → DTO変換 - 完全な情報を持つユーザー")
    void convertToDto_CompleteInformation() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));

        // When
        UserDto result = userService.findById(1L);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("テストユーザー");
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        assertThat(result.getDepartmentId()).isEqualTo(1L);
        assertThat(result.getDepartmentName()).isEqualTo("テスト部門");
        assertThat(result.getOrganizationId()).isEqualTo(1L);
        assertThat(result.getOrganizationName()).isEqualTo("テスト組織");
        assertThat(result.getPosition()).isEqualTo("エンジニア");
        assertThat(result.getCreatedAt()).isNotNull();
        assertThat(result.getUpdatedAt()).isNotNull();
    }
}
