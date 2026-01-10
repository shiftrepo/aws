-- V2: Create departments table with hierarchical structure
-- 部門テーブル作成（階層構造対応）

CREATE TABLE departments (
    id                   BIGSERIAL       PRIMARY KEY,
    name                 VARCHAR(100)    NOT NULL,
    description          VARCHAR(500),
    organization_id      BIGINT          NOT NULL,
    parent_department_id BIGINT,
    created_at           TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 外部キー制約
    CONSTRAINT fk_departments_organization
        FOREIGN KEY (organization_id) REFERENCES organizations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_departments_parent
        FOREIGN KEY (parent_department_id) REFERENCES departments(id)
        ON DELETE CASCADE,

    -- 同一組織内での部門名重複を防ぐ
    CONSTRAINT uk_departments_name_per_organization
        UNIQUE (organization_id, name)
);

-- インデックス作成
CREATE INDEX idx_departments_organization_id ON departments(organization_id);
CREATE INDEX idx_departments_parent_department_id ON departments(parent_department_id);
CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_created_at ON departments(created_at);

-- コメント追加
COMMENT ON TABLE departments IS '部門マスタテーブル（階層構造対応）';
COMMENT ON COLUMN departments.id IS '部門ID（主キー）';
COMMENT ON COLUMN departments.name IS '部門名（組織内で重複不可）';
COMMENT ON COLUMN departments.description IS '部門説明';
COMMENT ON COLUMN departments.organization_id IS '所属組織ID';
COMMENT ON COLUMN departments.parent_department_id IS '親部門ID（階層構造、NULLはトップレベル）';
COMMENT ON COLUMN departments.created_at IS '作成日時';
COMMENT ON COLUMN departments.updated_at IS '更新日時';