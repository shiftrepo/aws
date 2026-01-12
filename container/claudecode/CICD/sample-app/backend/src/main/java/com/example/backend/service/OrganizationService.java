package com.example.backend.service;

import com.example.backend.entity.Organization;
import com.example.backend.repository.OrganizationRepository;
import com.example.backend.repository.DepartmentRepository;
import com.example.common.dto.OrganizationTreeDto;
import com.example.common.dto.DepartmentTreeNode;
import com.example.backend.entity.Department;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import com.example.common.dto.OrganizationDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Organization Service
 * 組織サービス
 */
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class OrganizationService {

    private final OrganizationRepository organizationRepository;
    private final DepartmentRepository departmentRepository;

    /**
     * 全組織一覧取得
     */
    @Transactional(readOnly = true)
    public List<OrganizationDto> findAll() {
        log.debug("全組織一覧を取得開始");
        List<Organization> organizations = organizationRepository.findAll();
        return organizations.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * 組織ID指定取得
     */
    @Transactional(readOnly = true)
    public OrganizationDto findById(Long id) {
        log.debug("組織ID: {} の組織を取得開始", id);
        Organization organization = organizationRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("組織が見つかりません。ID: " + id));
        return convertToDto(organization);
    }

    /**
     * 組織作成
     */
    public OrganizationDto create(OrganizationDto dto) {
        log.debug("組織作成開始: {}", dto.getName());

        // 名前の重複チェック
        if (organizationRepository.existsByName(dto.getName())) {
            throw new IllegalArgumentException("組織名が既に存在します: " + dto.getName());
        }

        Organization organization = Organization.builder()
                .name(dto.getName())
                .description(dto.getDescription())
                .build();

        Organization saved = organizationRepository.save(organization);
        log.debug("組織作成完了: ID={}", saved.getId());

        return convertToDto(saved);
    }

    /**
     * 組織更新
     */
    public OrganizationDto update(Long id, OrganizationDto dto) {
        log.debug("組織更新開始: ID={}", id);

        Organization organization = organizationRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("組織が見つかりません。ID: " + id));

        // 名前の重複チェック（自分以外）
        if (organizationRepository.existsByNameAndIdNot(dto.getName(), id)) {
            throw new IllegalArgumentException("組織名が既に存在します: " + dto.getName());
        }

        organization.setName(dto.getName());
        organization.setDescription(dto.getDescription());

        Organization updated = organizationRepository.save(organization);
        log.debug("組織更新完了: ID={}", id);

        return convertToDto(updated);
    }

    /**
     * 組織削除
     */
    public void delete(Long id) {
        log.debug("組織削除開始: ID={}", id);

        if (!organizationRepository.existsById(id)) {
            throw new EntityNotFoundException("組織が見つかりません。ID: " + id);
        }

        organizationRepository.deleteById(id);
        log.debug("組織削除完了: ID={}", id);
    }

    /**
     * Entity → DTO変換
     */
    private OrganizationDto convertToDto(Organization organization) {
        return OrganizationDto.builder()
                .id(organization.getId())
                .name(organization.getName())
                .description(organization.getDescription())
                .createdAt(organization.getCreatedAt())
                .updatedAt(organization.getUpdatedAt())
                .build();
    }

    /**
     * 組織の階層構造取得
     * @param organizationId 組織ID
     * @return 組織階層構造
     */
    public OrganizationTreeDto getOrganizationTree(Long organizationId) {
        log.debug("組織階層構造取得開始: organizationId={}", organizationId);

        // 組織存在確認
        Organization organization = organizationRepository.findById(organizationId)
                .orElseThrow(() -> new IllegalArgumentException("組織が見つかりません: ID=" + organizationId));

        // 組織配下の全部門取得
        List<Department> departments = departmentRepository.findByOrganizationId(organizationId);
        log.debug("部門数: {}", departments.size());

        // 階層構造構築
        List<DepartmentTreeNode> rootNodes = buildDepartmentTree(departments);

        // DTOに変換
        OrganizationTreeDto treeDto = OrganizationTreeDto.builder()
                .id(organization.getId())
                .name(organization.getName())
                .description(organization.getDescription())
                .createdAt(organization.getCreatedAt())
                .updatedAt(organization.getUpdatedAt())
                .departments(rootNodes)
                .build();

        log.debug("組織階層構造取得完了: ルート部門数={}", rootNodes.size());
        return treeDto;
    }

    /**
     * 部門の階層構造を構築
     * @param departments 部門リスト
     * @return ルート部門ノードリスト
     */
    private List<DepartmentTreeNode> buildDepartmentTree(List<Department> departments) {
        // 全部門をMapに格納（高速アクセス用）
        Map<Long, DepartmentTreeNode> nodeMap = new HashMap<>();
        for (Department dept : departments) {
            DepartmentTreeNode node = DepartmentTreeNode.builder()
                    .id(dept.getId())
                    .name(dept.getName())
                    .description(dept.getDescription())
                    .organizationId(dept.getOrganizationId())
                    .parentDepartmentId(dept.getParentDepartmentId())
                    .createdAt(dept.getCreatedAt())
                    .updatedAt(dept.getUpdatedAt())
                    .children(new ArrayList<>())
                    .build();
            nodeMap.put(dept.getId(), node);
        }

        // 親子関係を構築
        List<DepartmentTreeNode> rootNodes = new ArrayList<>();
        for (DepartmentTreeNode node : nodeMap.values()) {
            if (node.getParentDepartmentId() == null) {
                // ルートノード
                rootNodes.add(node);
            } else {
                // 子ノード
                DepartmentTreeNode parent = nodeMap.get(node.getParentDepartmentId());
                if (parent != null) {
                    parent.addChild(node);
                }
            }
        }

        return rootNodes;
    }
}
