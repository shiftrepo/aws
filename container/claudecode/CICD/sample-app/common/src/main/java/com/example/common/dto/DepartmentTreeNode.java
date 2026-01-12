package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Department Tree Node
 * 部門の階層構造ノード
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DepartmentTreeNode {
    private Long id;
    private String name;
    private String description;
    private Long organizationId;
    private Long parentDepartmentId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder.Default
    private List<DepartmentTreeNode> children = new ArrayList<>();

    /**
     * 子ノード追加
     */
    public void addChild(DepartmentTreeNode child) {
        if (this.children == null) {
            this.children = new ArrayList<>();
        }
        this.children.add(child);
    }
}
