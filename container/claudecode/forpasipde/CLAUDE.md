# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## コンテナ環境の構成

このリポジトリはClaude Codeを実行するための複数ベースイメージに対応したDockerコンテナ環境を提供します。主な構成要素：

- 複数のベースイメージサポート（Node.js slim、Debian slim、Amazon Linux 2023）
- GitLabをMCPサーバーとして導入
- SELinux対応のボリュームマウント（:z共有モード）
- 段階的実装計画による優先順位対応

## コマンド一覧

### 環境のセットアップと起動

```bash
# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な値を設定

# ベースイメージを指定してコンテナを起動
./run.sh           # Node.js slim版を起動（デフォルト）
./run.sh node      # Node.js slim版を起動
./run.sh debian    # Debian slim版を起動
./run.sh amazonlinux # Amazon Linux版を起動

# 従来のdocker-compose直接実行
docker-compose up -d                           # 現在のdocker-compose.yml使用
docker-compose -f docker-compose-node.yml up -d    # Node.js版（予定）
docker-compose -f docker-compose-debian.yml up -d  # Debian版（予定）

# コンテナのログを確認
docker-compose logs -f

# 起動中のコンテナに接続
docker-compose exec claudecode bash
```

### Claude Codeの設定と実行

```bash
# GitLab MCPのセットアップ（コンテナ内で実行）
./setup_gitlab_mcp.sh

# Claude Codeのバージョン確認
claude --version

# MCPの設定確認
claude mcp list

# GitLab MCPの追加
envsubst < add_gitlab_mcp.json > add_token_gitlab_mcp.json
claude mcp add-json gitlab-org "$(cat add_token_gitlab_mcp.json)" --verbose
rm -f add_token_gitlab_mcp.json

# GitHub MCPの追加（必要な場合）
envsubst < add_mcp.json > add_token_github_mcp.json
claude mcp add-json github-org "$(cat add_token_github_mcp.json)" --verbose
rm -f add_token_github_mcp.json

# Claude Codeの実行
claude code
```

## アーキテクチャ概要

この環境は複数のベースイメージをサポートし、以下の主要コンポーネントで構成されています：

### 1. **Claude Code コンテナ（複数バリアント）**:

#### Node.js slim版（最優先実装）:
   - `node:18-slim`をベースイメージとして使用
   - Node.jsが既にインストール済み（nvmは基本不要）
   - 最小限の設定で高速起動
   - GitLab CLIとMCPサーバーパッケージを導入

#### Debian slim版（中優先実装）:
   - Debian slimをベースイメージとして使用
   - APTパッケージマネージャーによる軽量構成
   - Node.jsとnvmを手動インストール

#### Amazon Linux 2023版（低優先実装）:
   - Amazon Linux 2023をベースイメージとして使用
   - DNFパッケージマネージャーによるAWS親和性重視
   - Node.js 22とnvmをインストール

### 2. **GitLabコンテナ**:
   - GitLabのCEエディションを使用
   - MCPサーバーとして機能し、GitLabのAPIを通じてリポジトリアクセスを提供
   - ボリュームを使用して設定と永続データを保存
   - APIレート制限設定（300リクエスト/時間）

### 3. **マルチコンテナ構成管理**:
   - 複数のdocker-compose.ymlファイルによるバリアント管理
   - 統一された環境変数管理
   - SELinux対応の:z共有モードボリュームマウント

### 4. **環境変数管理**:
   - AWS BedrockとAnthropicモデルの設定
   - GitLab API認証用のトークン管理
   - 秘匿情報は.envファイルで管理（gitignore対象）

## 必須環境変数

以下の環境変数は.envファイルに設定する必要があります：

- `CLAUDE_CODE_USE_BEDROCK` - Amazon Bedrockを使用するかどうか
- `ANTHROPIC_MODEL` - 使用するメインモデル
- `ANTHROPIC_SMALL_FAST_MODEL` - 使用する小型高速モデル
- `AWS_ACCESS_KEY_ID` - AWSアクセスキー
- `AWS_SECRET_ACCESS_KEY` - AWSシークレットキー
- `AWS_REGION` - AWSリージョン
- `GITLAB_API_TOKEN` - GitLab APIトークン

## 開発ワークフロー

### ベースイメージ選択指針

1. **Node.js slim**: 最もシンプル、Node.js環境が既に整っている場合
2. **Debian slim**: 軽量性重視、カスタマイズ性が必要な場合
3. **Amazon Linux**: AWS環境との親和性、エンタープライズ用途

### 実装優先順位

current issue #72の要件により、以下の順序で実装：
1. Node.js slim版（最優先）
2. Debian slim版（中優先）
3. Amazon Linux版（低優先）

## GitHubからGitLabへの移行について

このリポジトリでは、GitHub MCPからGitLab MCPへの移行を実施中です：

### 主な変更点:
1. 環境変数: `GITHUB_PERSONAL_ACCESS_TOKEN` → `GITLAB_PERSONAL_ACCESS_TOKEN`
2. プルリクエスト名: Pull Request (PR) → Merge Request (MR)
3. MCPパッケージ: `@modelcontextprotocol/server-github` → `@modelcontextprotocol/server-gitlab`

### 移行手順:
1. GitLabアカウントでAPIトークンを生成
2. `GITLAB_API_TOKEN`環境変数を設定
3. `./setup_gitlab_mcp.sh`でGitLab MCPをセットアップ

詳細は`github_to_gitlab_mcp_migration.md`と`gitlab_mcp_implementation_plan.md`を参照してください。

## Issue #72 対応メモ

- Issue #72に関連する実装要件の追加
- Node.js slim版を最優先で対応
- コンテナ環境の優先順位を明確化
- 実装詳細は各コンポーネントの設定に反映