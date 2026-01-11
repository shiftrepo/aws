package com.example.backend.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;

/**
 * Department Entity
 * 部門エンティティ (階層構造対応)
 */
@Entity
@Table(name = "departments")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    @NotBlank(message = "部門名は必須です")
    @Size(max = 100, message = "部門名は100文字以内で入力してください")
    private String name;

    @Column(length = 500)
    @Size(max = 500, message = "説明は500文字以内で入力してください")
    private String description;

    @Column(name = "organization_id", nullable = false)
    @NotNull(message = "所属組織は必須です")
    private Long organizationId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "organization_id", insertable = false, updatable = false)
    private Organization organization;

    @Column(name = "parent_department_id")
    private Long parentDepartmentId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_department_id", insertable = false, updatable = false)
    private Department parentDepartment;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}