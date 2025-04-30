# Inpit SQLite MCP サーバー

このMCP（Model Context Protocol）サーバーは、ClaudeがInpit SQLiteデータベースサービスとHTTP APIを通じて対話することを可能にします。これにより、Claudeは特許データの照会、出願番号や出願人名での検索、データベースに対するSQLクエリの実行が可能になります。

## 機能

- 出願番号による特許の照会
- 出願人名による特許の検索
- Inpit SQLiteデータベースに対するSQLクエリの実行
- システムステータスとデータベース情報の取得

## 前提条件

- Python 3.8以上
- Inpit SQLiteサービスが実行中（通常はhttp://localhost:5001）
- MCP互換のClaudeインターフェース（VSCode内のClaudeまたはClaude Desktop App）

## インストール

1. Inpit SQLiteサービスがドキュメントに従って実行されていることを確認します
2. セットアップスクリプトを実行します：

```bash
cd inpit-sqlite-mcp
chmod +x setup.sh
./setup.sh
```

3. ClaudeクライアントがこのMCPサーバーを使用するよう設定します：

VSCode Claude拡張機能の場合、以下を `~/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` に追加します：

```json
{
  "mcpServers": {
    "inpit-sqlite": {
      "command": "python",
      "args": ["/path/to/inpit-sqlite-mcp/server.py"],
      "env": {
        "INPIT_API_URL": "http://localhost:5001"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Claude Desktop Appの場合、適切な設定ファイルに同様の設定を追加します。

## 利用可能なツール

### 1. get_patent_by_application_number

出願番号で特許を検索します（部分一致もサポート）。

**パラメータ：**
- `application_number`（文字列）：検索する出願番号

**例：**
```
GET http://localhost:5001/api/application/2022-123456
```

### 2. get_patents_by_applicant

出願人名で特許を検索します（部分一致もサポート）。

**パラメータ：**
- `applicant_name`（文字列）：検索する出願人名

**例：**
```
GET http://localhost:5001/api/applicant/テック株式会社
```

### 3. execute_sql_query

データベースに対して直接SQLクエリを実行します。

**パラメータ：**
- `query`（文字列）：実行するSQLクエリ（SELECT文のみ）

**例：**
```
POST http://localhost:5001/api/sql-query
Content-Type: application/json

{
  "query": "SELECT 出願人, COUNT(*) as count FROM inpit_data GROUP BY 出願人 ORDER BY count DESC LIMIT 10"
}
```

## リソース

### Inpit SQLite API ステータス

URI: `inpit-sqlite://status`

データベースのステータス、レコード数、スキーマ情報などを返します。

## Difyとの統合

このMCPサーバーをDifyで使用するには：

1. Inpit SQLiteサービスとこのMCPサーバーの両方が実行されていることを確認します
2. Difyアプリケーション設定で：
   - アプリケーションがClaudeをLLMプロバイダーとして使用するよう設定します
   - ClaudeインスタンスがこのMCPサーバーを有効にしていることを確認します
3. DifyのAPIを通じてClaudeを使用する際に、これらのツールが利用可能になります

### Dify API クエリの例

以下は、DifyのHTTP APIを通じて行うことができる、ClaudeのMCP機能を利用したクエリの例です：

#### 特定の出願番号で特許を検索

```
POST https://your-dify-instance/api/chat-messages
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "query": "出願番号2022-123456の特許を検索して",
  "conversation_id": "optional-conversation-id",
  "user": "optional-user-id",
  "inputs": {}
}
```

#### 特定の会社による全ての特許を検索

```
POST https://your-dify-instance/api/chat-messages
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "query": "テック株式会社が出願した全ての特許をリストアップして",
  "conversation_id": "optional-conversation-id",
  "user": "optional-user-id",
  "inputs": {}
}
```

#### SQLクエリ分析の実行

```
POST https://your-dify-instance/api/chat-messages
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "query": "特許出願人トップ10とそれぞれが出願した特許数を表示して",
  "conversation_id": "optional-conversation-id",
  "user": "optional-user-id",
  "inputs": {}
}
```

## トラブルシューティング

- **接続の問題**：Inpit SQLiteサービスが設定されたURLで実行されていることを確認してください
- **データが見つからない**：データベースが特許データで適切に構築されていることを確認してください
- **権限エラー**：サーバーが実行に必要な権限を持っていることを確認してください
- **MCP設定**：ClaudeクライアントがこのMCPサーバーを使用するよう適切に設定されていることを確認してください

問題や質問がある場合は、`/tmp/inpit-sqlite-mcp.log`にあるログファイルを確認してください。
