package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Organization Tree DTO
 * 組織の階層構造を表現するDTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrganizationTreeDto {
    private Long id;
    private String name;
    private String description;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<DepartmentTreeNode> departments;
}
