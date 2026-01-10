package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import java.time.LocalDateTime;

/**
 * DTO for User entity
 * ユーザー情報のデータ転送オブジェクト
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {

    /**
     * ユーザーID
     */
    private Long id;

    /**
     * ユーザー名
     */
    @NotBlank(message = "ユーザー名は必須です")
    @Size(max = 100, message = "ユーザー名は100文字以内で入力してください")
    private String name;

    /**
     * メールアドレス
     */
    @NotBlank(message = "メールアドレスは必須です")
    @Email(message = "有効なメールアドレスを入力してください")
    @Size(max = 200, message = "メールアドレスは200文字以内で入力してください")
    private String email;

    /**
     * 所属部門ID
     */
    @NotNull(message = "所属部門は必須です")
    private Long departmentId;

    /**
     * 部門名 (表示用)
     */
    private String departmentName;

    /**
     * 組織ID (表示用)
     */
    private Long organizationId;

    /**
     * 組織名 (表示用)
     */
    private String organizationName;

    /**
     * 役職
     */
    @Size(max = 100, message = "役職は100文字以内で入力してください")
    private String position;

    /**
     * 作成日時
     */
    private LocalDateTime createdAt;

    /**
     * 更新日時
     */
    private LocalDateTime updatedAt;
}