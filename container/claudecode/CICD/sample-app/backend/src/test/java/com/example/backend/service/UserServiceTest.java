package com.example.backend.service;

import com.example.backend.entity.Department;
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
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * UserService のテストクラス
 * JaCoCo カバレッジ 50% 以上を目標
 * ifの分岐を網羅するテストケースを含む
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

    private User sampleUser;
    private Department sampleDepartment;
    private UserDto sampleDto;

    @BeforeEach
    void setUp() {
        LocalDateTime now = LocalDateTime.now();

        sampleDepartment = Department.builder()
                .id(1L)
                .name("テスト部門")
                .description("テスト用の部門です")
                .organizationId(1L)
                .createdAt(now)
                .updatedAt(now)
                .build();

        sampleUser = User.builder()
                .id(1L)
                .name("テストユーザー")
                .email("test@example.com")
                .departmentId(1L)
                .position("一般社員")
                .createdAt(now)
                .updatedAt(now)
                .build();

        sampleDto = UserDto.builder()
                .id(1L)
                .name("テストユーザー")
                .email("test@example.com")
                .departmentId(1L)
                .position("一般社員")
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
        List<User> users = Arrays.asList(sampleUser);
        when(userRepository.findByDepartmentIdOrderByName(1L)).thenReturn(users);

        // When
        List<UserDto> result = userService.findByDepartmentId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テストユーザー");
        verify(userRepository).findByDepartmentIdOrderByName(1L);
    }

    @Test
    @DisplayName("組織IDでユーザー一覧取得 - 正常系")
    void findByOrganizationId_Success() {
        // Given
        List<User> users = Arrays.asList(sampleUser);
        when(userRepository.findByOrganizationId(1L)).thenReturn(users);

        // When
        List<UserDto> result = userService.findByOrganizationId(1L);

        // Then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("テストユーザー");
        verify(userRepository).findByOrganizationId(1L);
    }

    @Test
    @DisplayName("ユーザー作成 - 正常系")
    void create_Success() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("newuser@example.com")
                .departmentId(1L)
                .position("課長")
                .build();

        User savedUser = User.builder()
                .id(2L)
                .name("新規ユーザー")
                .email("newuser@example.com")
                .departmentId(1L)
                .position("課長")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(userRepository.existsByEmail("newuser@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        // When
        UserDto result = userService.create(createDto);

        // Then
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("新規ユーザー");
        assertThat(result.getEmail()).isEqualTo("newuser@example.com");
        verify(departmentRepository).findById(1L);
        verify(userRepository).existsByEmail("newuser@example.com");
        verify(userRepository).save(any(User.class));
    }

    @Test
    @DisplayName("ユーザー作成 - 部門が存在しない")
    void create_DepartmentNotFound() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("newuser@example.com")
                .departmentId(999L)
                .position("課長")
                .build();

        when(departmentRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.create(createDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(departmentRepository).findById(999L);
    }

    @Test
    @DisplayName("ユーザー作成 - メールアドレス重複エラー")
    void create_DuplicateEmail() {
        // Given
        UserDto createDto = UserDto.builder()
                .name("新規ユーザー")
                .email("duplicate@example.com")
                .departmentId(1L)
                .position("課長")
                .build();

        when(departmentRepository.findById(1L)).thenReturn(Optional.of(sampleDepartment));
        when(userRepository.existsByEmail("duplicate@example.com")).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.create(createDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("メールアドレスが既に存在します: duplicate@example.com");

        verify(departmentRepository).findById(1L);
        verify(userRepository).existsByEmail("duplicate@example.com");
    }

    @Test
    @DisplayName("ユーザー更新 - 正常系")
    void update_Success() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(1L)
                .position("部長")
                .build();

        User updatedUser = User.builder()
                .id(1L)
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(1L)
                .position("部長")
                .createdAt(sampleUser.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(userRepository.existsByEmailAndIdNot("updated@example.com", 1L)).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(updatedUser);

        // When
        UserDto result = userService.update(1L, updateDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("更新ユーザー");
        assertThat(result.getEmail()).isEqualTo("updated@example.com");
        verify(userRepository).findById(1L);
        verify(departmentRepository).existsById(1L);
        verify(userRepository).existsByEmailAndIdNot("updated@example.com", 1L);
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
                .position("部長")
                .build();

        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.update(999L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("ユーザーが見つかりません。ID: 999");

        verify(userRepository).findById(999L);
    }

    @Test
    @DisplayName("ユーザー更新 - 部門が存在しない")
    void update_DepartmentNotFound() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("updated@example.com")
                .departmentId(999L)
                .position("部長")
                .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(departmentRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThatThrownBy(() -> userService.update(1L, updateDto))
                .isInstanceOf(EntityNotFoundException.class)
                .hasMessage("部門が見つかりません。ID: 999");

        verify(userRepository).findById(1L);
        verify(departmentRepository).existsById(999L);
    }

    @Test
    @DisplayName("ユーザー更新 - メールアドレス重複エラー")
    void update_DuplicateEmail() {
        // Given
        UserDto updateDto = UserDto.builder()
                .name("更新ユーザー")
                .email("duplicate@example.com")
                .departmentId(1L)
                .position("部長")
                .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(sampleUser));
        when(departmentRepository.existsById(1L)).thenReturn(true);
        when(userRepository.existsByEmailAndIdNot("duplicate@example.com", 1L)).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.update(1L, updateDto))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("メールアドレスが既に存在します: duplicate@example.com");

        verify(userRepository).findById(1L);
        verify(departmentRepository).existsById(1L);
        verify(userRepository).existsByEmailAndIdNot("duplicate@example.com", 1L);
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
    }
}
