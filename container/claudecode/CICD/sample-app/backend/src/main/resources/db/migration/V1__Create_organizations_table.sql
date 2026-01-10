-- V1: Create organizations table
-- 組織テーブル作成

CREATE TABLE organizations (
    id          BIGSERIAL       PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL UNIQUE,
    description VARCHAR(500),
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_created_at ON organizations(created_at);

-- コメント追加
COMMENT ON TABLE organizations IS '組織マスタテーブル';
COMMENT ON COLUMN organizations.id IS '組織ID（主キー）';
COMMENT ON COLUMN organizations.name IS '組織名（重複不可）';
COMMENT ON COLUMN organizations.description IS '組織説明';
COMMENT ON COLUMN organizations.created_at IS '作成日時';
COMMENT ON COLUMN organizations.updated_at IS '更新日時';