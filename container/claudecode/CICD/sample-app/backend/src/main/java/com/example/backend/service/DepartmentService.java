package com.example.backend.service;

import com.example.backend.entity.Department;
import com.example.backend.entity.Organization;
import com.example.backend.repository.DepartmentRepository;
import com.example.backend.repository.OrganizationRepository;
import com.example.common.dto.DepartmentDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Department Service
 * 部門サービス
 */
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class DepartmentService {

    private final DepartmentRepository departmentRepository;
    private final OrganizationRepository organizationRepository;

    /**
     * 全部門一覧取得
     */
    @Transactional(readOnly = true)
    public List<DepartmentDto> findAll() {
        log.debug("全部門一覧を取得開始");
        List<Department> departments = departmentRepository.findAll();
        return departments.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * 部門ID指定取得
     */
    @Transactional(readOnly = true)
    public DepartmentDto findById(Long id) {
        log.debug("部門ID: {} の部門を取得開始", id);
        Department department = departmentRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("部門が見つかりません。ID: " + id));
        return convertToDto(department);
    }

    /**
     * 組織IDで部門一覧を取得
     */
    @Transactional(readOnly = true)
    public List<DepartmentDto> findByOrganizationId(Long organizationId) {
        log.debug("組織ID: {} の部門一覧を取得開始", organizationId);
        List<Department> departments = departmentRepository.findByOrganizationIdOrderByName(organizationId);
        return departments.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * 部門作成
     */
    public DepartmentDto create(DepartmentDto dto) {
        log.debug("部門作成開始: {}", dto.getName());

        // 組織存在確認
        Organization organization = organizationRepository.findById(dto.getOrganizationId())
                .orElseThrow(() -> new EntityNotFoundException("組織が見つかりません。ID: " + dto.getOrganizationId()));

        // 名前の重複チェック
        if (departmentRepository.existsByOrganizationIdAndName(dto.getOrganizationId(), dto.getName())) {
            throw new IllegalArgumentException("部門名が既に存在します: " + dto.getName());
        }

        // 親部門の存在確認
        if (dto.getParentDepartmentId() != null) {
            if (!departmentRepository.existsById(dto.getParentDepartmentId())) {
                throw new EntityNotFoundException("親部門が見つかりません。ID: " + dto.getParentDepartmentId());
            }
        }

        Department department = Department.builder()
                .name(dto.getName())
                .description(dto.getDescription())
                .organizationId(dto.getOrganizationId())
                .parentDepartmentId(dto.getParentDepartmentId())
                .build();

        Department saved = departmentRepository.save(department);
        log.debug("部門作成完了: ID={}", saved.getId());

        return convertToDto(saved);
    }

    /**
     * 部門更新
     */
    public DepartmentDto update(Long id, DepartmentDto dto) {
        log.debug("部門更新開始: ID={}", id);

        Department department = departmentRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("部門が見つかりません。ID: " + id));

        // 名前の重複チェック（自分以外）
        if (departmentRepository.existsByOrganizationIdAndNameAndIdNot(dto.getOrganizationId(), dto.getName(), id)) {
            throw new IllegalArgumentException("部門名が既に存在します: " + dto.getName());
        }

        // 親部門の存在確認
        if (dto.getParentDepartmentId() != null) {
            if (!departmentRepository.existsById(dto.getParentDepartmentId())) {
                throw new EntityNotFoundException("親部門が見つかりません。ID: " + dto.getParentDepartmentId());
            }
            // 循環参照チェック（自分自身を親にできない）
            if (dto.getParentDepartmentId().equals(id)) {
                throw new IllegalArgumentException("自分自身を親部門に設定できません");
            }
        }

        department.setName(dto.getName());
        department.setDescription(dto.getDescription());
        department.setParentDepartmentId(dto.getParentDepartmentId());

        Department updated = departmentRepository.save(department);
        log.debug("部門更新完了: ID={}", id);

        return convertToDto(updated);
    }

    /**
     * 部門削除
     */
    public void delete(Long id) {
        log.debug("部門削除開始: ID={}", id);

        if (!departmentRepository.existsById(id)) {
            throw new EntityNotFoundException("部門が見つかりません。ID: " + id);
        }

        // 子部門が存在する場合は削除不可
        List<Department> children = departmentRepository.findByParentDepartmentIdOrderByName(id);
        if (!children.isEmpty()) {
            throw new IllegalStateException("子部門が存在するため削除できません。まず子部門を削除してください。");
        }

        departmentRepository.deleteById(id);
        log.debug("部門削除完了: ID={}", id);
    }

    /**
     * Entity → DTO変換
     */
    private DepartmentDto convertToDto(Department department) {
        // 組織名を取得
        String organizationName = null;
        if (department.getOrganization() != null) {
            organizationName = department.getOrganization().getName();
        } else if (department.getOrganizationId() != null) {
            organizationName = organizationRepository.findById(department.getOrganizationId())
                    .map(Organization::getName)
                    .orElse(null);
        }

        // 親部門名を取得
        String parentDepartmentName = null;
        if (department.getParentDepartment() != null) {
            parentDepartmentName = department.getParentDepartment().getName();
        } else if (department.getParentDepartmentId() != null) {
            parentDepartmentName = departmentRepository.findById(department.getParentDepartmentId())
                    .map(Department::getName)
                    .orElse(null);
        }

        return DepartmentDto.builder()
                .id(department.getId())
                .name(department.getName())
                .description(department.getDescription())
                .organizationId(department.getOrganizationId())
                .organizationName(organizationName)
                .parentDepartmentId(department.getParentDepartmentId())
                .parentDepartmentName(parentDepartmentName)
                .createdAt(department.getCreatedAt())
                .updatedAt(department.getUpdatedAt())
                .build();
    }
}
