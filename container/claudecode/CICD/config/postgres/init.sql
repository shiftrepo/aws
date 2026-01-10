-- PostgreSQL初期化スクリプト
-- 複数のデータベースとユーザーを作成

-- SonarQube用データベース
CREATE DATABASE sonardb;
CREATE USER sonaruser WITH ENCRYPTED PASSWORD 'sonar_db_pass_2026';
GRANT ALL PRIVILEGES ON DATABASE sonardb TO sonaruser;

-- サンプルアプリケーション用データベース
CREATE DATABASE sampledb;
CREATE USER sampleuser WITH ENCRYPTED PASSWORD 'sample_app_pass_2026';
GRANT ALL PRIVILEGES ON DATABASE sampledb TO sampleuser;

-- sampledb に接続して権限設定
\c sampledb;
GRANT ALL ON SCHEMA public TO sampleuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sampleuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sampleuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sampleuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sampleuser;

-- sonardb に接続して権限設定
\c sonardb;
GRANT ALL ON SCHEMA public TO sonaruser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sonaruser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sonaruser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sonaruser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sonaruser;

-- Mattermost用データベース
CREATE DATABASE mattermostdb;
CREATE USER mattermostuser WITH ENCRYPTED PASSWORD 'mattermost_pass_2026';
GRANT ALL PRIVILEGES ON DATABASE mattermostdb TO mattermostuser;

-- mattermostdb に接続して権限設定
\c mattermostdb;
GRANT ALL ON SCHEMA public TO mattermostuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mattermostuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mattermostuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mattermostuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mattermostuser;
