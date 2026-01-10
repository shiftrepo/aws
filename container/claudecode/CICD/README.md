# CICD完全環境構築ガイド

完全なCI/CD環境（GitLab、Nexus、SonarQube、PostgreSQL、GitLab Runner）をDocker Composeで構築し、スクラップビルドから完全復元まで対応します。

## 📋 目次

- [環境概要](#環境概要)
- [前提条件](#前提条件)
- [クイックスタート](#クイックスタート)
- [バックアップと復元](#バックアップと復元)

## 🌟 環境概要

### サービス構成

| サービス | ポート | 用途 |
|---------|-------|------|
| GitLab CE | 5003 (HTTP), 5005 (SSH) | Git リポジトリ、CI/CD |
| Nexus | 8082 (UI), 8083 (Docker) | アーティファクト管理 |
| SonarQube | 8000 | 静的コード解析 |
| PostgreSQL | 5001 | データベース |
| pgAdmin | 5002 | DB GUI管理 |

## 🚀 クイックスタート

### ゼロからセットアップ
\`\`\`bash
cd /root/aws.git/container/claudecode/CICD
chmod +x scripts/*.sh
./scripts/setup-from-scratch.sh
\`\`\`

## 💾 バックアップと復元

### バックアップ
\`\`\`bash
./scripts/backup-all.sh
\`\`\`

### 復元
\`\`\`bash
./scripts/restore-all.sh backup-20260110-073000
\`\`\`

### クリーンアップ
\`\`\`bash
./scripts/cleanup-all.sh
\`\`\`
