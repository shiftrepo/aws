package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;

/**
 * DTO for Department entity
 * 部門情報のデータ転送オブジェクト
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DepartmentDto {

    /**
     * 部門ID
     */
    private Long id;

    /**
     * 部門名
     */
    @NotBlank(message = "部門名は必須です")
    @Size(max = 100, message = "部門名は100文字以内で入力してください")
    private String name;

    /**
     * 部門説明
     */
    @Size(max = 500, message = "説明は500文字以内で入力してください")
    private String description;

    /**
     * 所属組織ID
     */
    @NotNull(message = "所属組織は必須です")
    private Long organizationId;

    /**
     * 組織名 (表示用)
     */
    private String organizationName;

    /**
     * 親部門ID (階層構造のため、nullの場合はトップレベル部門)
     */
    private Long parentDepartmentId;

    /**
     * 親部門名 (表示用)
     */
    private String parentDepartmentName;

    /**
     * 作成日時
     */
    private LocalDateTime createdAt;

    /**
     * 更新日時
     */
    private LocalDateTime updatedAt;
}