package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import java.time.LocalDateTime;

/**
 * DTO for Organization entity
 * 組織情報のデータ転送オブジェクト
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrganizationDto {

    /**
     * 組織ID
     */
    private Long id;

    /**
     * 組織名
     */
    @NotBlank(message = "組織名は必須です")
    @Size(max = 100, message = "組織名は100文字以内で入力してください")
    private String name;

    /**
     * 組織説明
     */
    @Size(max = 500, message = "説明は500文字以内で入力してください")
    private String description;

    /**
     * 作成日時
     */
    private LocalDateTime createdAt;

    /**
     * 更新日時
     */
    private LocalDateTime updatedAt;
}