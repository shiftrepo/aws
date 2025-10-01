# Claude Code実行環境

このディレクトリには、Claude Codeを実行するためのDockerコンテナ環境のファイルが含まれています。
GitLabをMCPサーバーとして導入し、GitHub MCPからGitLab MCPへの変更を行っています。

## ディレクトリ構成

```
forpasipde/
├── amazonlinux.Dockerfile    # Claude Code用のDockerfile
├── docker-compose.yml        # Docker Compose設定ファイル
├── add_gitlab_mcp.json       # GitLab MCP設定用JSONファイル
├── add_mcp.json              # MCP設定用JSONファイル
├── setup.sh                  # セットアップスクリプト
├── .env.example              # 環境変数設定例
├── run.sh                    # 起動スクリプト
└── workdir/                  # 作業ディレクトリ（ボリュームマウント用）
```

## セットアップ方法

1. 環境変数の設定
   ```bash
   cp .env.example .env
   # .envファイルを編集して必要な設定を行う
   ```

2. コンテナの起動
   ```bash
   ./run.sh
   ```

## 主な機能

- Claude Codeの実行環境（Node.js 22、nvm）
- GitLabコンテナの導入とMCPサーバーとしての設定
- SELinux対応の:z共有モードによるボリュームマウント
- GitHub MCPからGitLab MCPへの変更

## 環境変数

- `CLAUDE_CODE_USE_BEDROCK` - Amazon Bedrockを使用するかどうか
- `ANTHROPIC_MODEL` - 使用するメインモデル
- `ANTHROPIC_SMALL_FAST_MODEL` - 使用する小型高速モデル
- `AWS_ACCESS_KEY_ID` - AWSアクセスキー
- `AWS_SECRET_ACCESS_KEY` - AWSシークレットキー
- `AWS_REGION` - AWSリージョン
- `GITLAB_API_TOKEN` - GitLab APIトークン

## 環境変数

- 1.0.1 MCPサーバの追加
- 1.0.2 Agentsの追加

