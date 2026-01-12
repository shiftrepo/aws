package com.example.backend.service;

import com.example.backend.entity.Department;
import com.example.backend.entity.User;
import com.example.backend.repository.DepartmentRepository;
import com.example.backend.repository.UserRepository;
import com.example.common.dto.UserDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.stream.Collectors;

/**
 * User Service
 * ユーザーサービス
 */
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final DepartmentRepository departmentRepository;

    /**
     * 全ユーザー一覧取得
     */
    @Transactional(readOnly = true)
    public List<UserDto> findAll() {
        log.debug("全ユーザー一覧を取得開始");
        List<User> users = userRepository.findAll();
        return users.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * ユーザーID指定取得
     */
    @Transactional(readOnly = true)
    public UserDto findById(Long id) {
        log.debug("ユーザーID: {} のユーザーを取得開始", id);
        User user = userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("ユーザーが見つかりません。ID: " + id));
        return convertToDto(user);
    }

    /**
     * 部門IDでユーザー一覧を取得
     */
    @Transactional(readOnly = true)
    public List<UserDto> findByDepartmentId(Long departmentId) {
        log.debug("部門ID: {} のユーザー一覧を取得開始", departmentId);
        List<User> users = userRepository.findByDepartmentIdOrderByName(departmentId);
        return users.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * 組織IDでユーザー一覧を取得
     */
    @Transactional(readOnly = true)
    public List<UserDto> findByOrganizationId(Long organizationId) {
        log.debug("組織ID: {} のユーザー一覧を取得開始", organizationId);
        List<User> users = userRepository.findByOrganizationId(organizationId);
        return users.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * ユーザー作成
     */
    public UserDto create(UserDto dto) {
        log.debug("ユーザー作成開始: {}", dto.getName());

        // 部門存在確認
        Department department = departmentRepository.findById(dto.getDepartmentId())
                .orElseThrow(() -> new EntityNotFoundException("部門が見つかりません。ID: " + dto.getDepartmentId()));

        // メールアドレスの重複チェック
        if (userRepository.existsByEmail(dto.getEmail())) {
            throw new IllegalArgumentException("メールアドレスが既に存在します: " + dto.getEmail());
        }

        User user = User.builder()
                .name(dto.getName())
                .email(dto.getEmail())
                .departmentId(dto.getDepartmentId())
                .position(dto.getPosition())
                .build();

        User saved = userRepository.save(user);
        log.debug("ユーザー作成完了: ID={}", saved.getId());

        return convertToDto(saved, department);
    }

    /**
     * ユーザー更新
     */
    public UserDto update(Long id, UserDto dto) {
        log.debug("ユーザー更新開始: ID={}", id);

        User user = userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("ユーザーが見つかりません。ID: " + id));

        // 部門存在確認
        Department department = departmentRepository.findById(dto.getDepartmentId())
                .orElseThrow(() -> new EntityNotFoundException("部門が見つかりません。ID: " + dto.getDepartmentId()));

        // メールアドレスの重複チェック（自分以外）
        if (userRepository.existsByEmailAndIdNot(dto.getEmail(), id)) {
            throw new IllegalArgumentException("メールアドレスが既に存在します: " + dto.getEmail());
        }

        user.setName(dto.getName());
        user.setEmail(dto.getEmail());
        user.setDepartmentId(dto.getDepartmentId());
        user.setPosition(dto.getPosition());

        User updated = userRepository.save(user);
        log.debug("ユーザー更新完了: ID={}", id);

        return convertToDto(updated, department);
    }

    /**
     * ユーザー削除
     */
    public void delete(Long id) {
        log.debug("ユーザー削除開始: ID={}", id);

        if (!userRepository.existsById(id)) {
            throw new EntityNotFoundException("ユーザーが見つかりません。ID: " + id);
        }

        userRepository.deleteById(id);
        log.debug("ユーザー削除完了: ID={}", id);
    }

    /**
     * Entity → DTO変換（既に取得済みの関連エンティティを使用）
     */
    private UserDto convertToDto(User user, Department department) {
        String departmentName = department != null ? department.getName() : null;
        Long organizationId = department != null ? department.getOrganizationId() : null;
        String organizationName = null;
        if (department != null && department.getOrganization() != null) {
            organizationName = department.getOrganization().getName();
        }

        return UserDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .departmentId(user.getDepartmentId())
                .departmentName(departmentName)
                .organizationId(organizationId)
                .organizationName(organizationName)
                .position(user.getPosition())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }

    /**
     * Entity → DTO変換（従来版 - findAll等で使用）
     */
    private UserDto convertToDto(User user) {
        // 部門情報を取得
        String departmentName = null;
        Long organizationId = null;
        String organizationName = null;

        if (user.getDepartment() != null) {
            Department dept = user.getDepartment();
            departmentName = dept.getName();
            organizationId = dept.getOrganizationId();
            if (dept.getOrganization() != null) {
                organizationName = dept.getOrganization().getName();
            }
        } else if (user.getDepartmentId() != null) {
            // 部門情報を取得して設定
            Department dept = departmentRepository.findById(user.getDepartmentId()).orElse(null);
            if (dept != null) {
                departmentName = dept.getName();
                organizationId = dept.getOrganizationId();
                if (dept.getOrganization() != null) {
                    organizationName = dept.getOrganization().getName();
                }
            }
        }

        return UserDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .departmentId(user.getDepartmentId())
                .departmentName(departmentName)
                .organizationId(organizationId)
                .organizationName(organizationName)
                .position(user.getPosition())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}
