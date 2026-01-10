-- V3: Create users table
-- ユーザーテーブル作成

CREATE TABLE users (
    id            BIGSERIAL       PRIMARY KEY,
    name          VARCHAR(100)    NOT NULL,
    email         VARCHAR(200)    NOT NULL UNIQUE,
    department_id BIGINT          NOT NULL,
    position      VARCHAR(100),
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 外部キー制約
    CONSTRAINT fk_users_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
        ON DELETE CASCADE
);

-- インデックス作成
CREATE INDEX idx_users_department_id ON users(department_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_created_at ON users(created_at);

-- コメント追加
COMMENT ON TABLE users IS 'ユーザーマスタテーブル';
COMMENT ON COLUMN users.id IS 'ユーザーID（主キー）';
COMMENT ON COLUMN users.name IS 'ユーザー名';
COMMENT ON COLUMN users.email IS 'メールアドレス（重複不可）';
COMMENT ON COLUMN users.department_id IS '所属部門ID';
COMMENT ON COLUMN users.position IS '役職';
COMMENT ON COLUMN users.created_at IS '作成日時';
COMMENT ON COLUMN users.updated_at IS '更新日時';