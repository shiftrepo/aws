# GitHub MCPからGitLab MCPへの移行ガイド

このドキュメントでは、GitHub MCPからGitLab MCPへの移行手順を説明します。

## 前提条件

- Node.jsとnpmがインストールされていること
- Claude Codeがインストールされていること
- GitLabアカウントとAPIアクセストークンが準備されていること

## GitLabアクセストークンの取得

1. GitLabにログインします
2. 右上のプロフィールアイコンをクリックし、「設定」を選択
3. 左側のメニューから「アクセストークン」を選択
4. 以下の設定でトークンを作成します:
   - 名前: `Claude Code MCP` (任意)
   - 有効期限: 必要に応じて設定
   - スコープ: `api`, `read_repository`, `write_repository` を選択
5. 「アクセストークンを作成」をクリック
6. 表示されたトークンをコピーして保存（このトークンは再表示されないので注意）

## 環境変数の設定

以下のコマンドで環境変数を設定します：

```bash
export GITLAB_API_TOKEN="your-gitlab-token"
```

永続的に設定する場合は、.bashrcや.zshrcに追加します：

```bash
echo 'export GITLAB_API_TOKEN="your-gitlab-token"' >> ~/.bashrc
# または
echo 'export GITLAB_API_TOKEN="your-gitlab-token"' >> ~/.zshrc
```

## GitLab MCPのインストールと設定

### 1. パッケージのインストール

```bash
npm install -g @modelcontextprotocol/server-gitlab
```

### 2. MCPの設定ファイルの作成

以下の内容の`add_gitlab_mcp.json`ファイルを作成します：

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-gitlab"],
  "env": {
    "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_API_TOKEN}"
  }
}
```

### 3. Claude CodeへのMCP追加

```bash
envsubst < add_gitlab_mcp.json > add_token_gitlab_mcp.json
claude mcp add-json gitlab-org "$(cat add_token_gitlab_mcp.json)" --verbose
rm -f add_token_gitlab_mcp.json
```

### 4. 設定の確認

```bash
claude mcp list
```

出力に`gitlab-org`が表示されていることを確認します。

## GitHub MCPの削除（オプション）

もしGitHub MCPが不要になった場合は、以下のコマンドで削除できます：

```bash
claude mcp remove github-org
```

## GitLab MCPの使用

Claude Codeを起動する際、GitLab関連のタスクを実行することで、GitLab MCPが自動的に使用されます。

## GitHub MCPとGitLab MCPの主な違い

| 項目 | GitHub MCP | GitLab MCP |
|------|------------|------------|
| 環境変数 | GITHUB_PERSONAL_ACCESS_TOKEN | GITLAB_PERSONAL_ACCESS_TOKEN |
| APIエンドポイント | api.github.com | gitlab.comのAPI |
| 機能 | リポジトリ操作、Issue、PR管理など | リポジトリ操作、Issue、MR管理など |
| プルリクエスト名 | Pull Request (PR) | Merge Request (MR) |

## トラブルシューティング

- **認証エラー**: 環境変数`GITLAB_PERSONAL_ACCESS_TOKEN`が正しく設定されているか確認してください
- **アクセス権限エラー**: GitLabトークンに適切なスコープが設定されているか確認してください
- **MCP登録エラー**: `claude mcp list`を実行して、現在の登録状況を確認してください

## 参考リソース

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitLab API Documentation](https://docs.gitlab.com/ee/api/)
- [@modelcontextprotocol/server-gitlab](https://www.npmjs.com/package/@modelcontextprotocol/server-gitlab)