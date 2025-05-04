# Inpit SQLite MCP サーバー

このMCP（Model Context Protocol）サーバーは、ClaudeがInpit SQLiteデータベースサービスとHTTP APIを通じて対話することを可能にします。これにより、Claudeは特許データの照会、出願番号や出願人名での検索、データベースに対するSQLクエリの実行が可能になります。

## 機能

- 出願番号による特許の照会
- 出願人名による特許の検索
- Inpit SQLiteデータベースに対するSQLクエリの実行
- システムステータスとデータベース情報の取得

## 前提条件

- Python 3.8以上（または Docker）
- Inpit SQLiteサービスが実行中（通常はhttp://localhost:5001）
- MCP互換のClaudeインターフェース（VSCode内のClaudeまたはClaude Desktop App）
- Difyでの使用の場合、Claude APIにアクセスできるDifyインスタンス

## セットアップ方法

### 方法1: スクリプトを使用したセットアップ

1. Inpit SQLiteサービスがドキュメントに従って実行されていることを確認します

2. セットアップスクリプトを実行します：

```bash
chmod +x setup.sh
./setup.sh
```

3. MCP サーバーを起動します:

```bash
cd app
python server.py
```

### 方法2: Docker Composeを使用したセットアップ

1. 必要な環境変数を設定します（S3からデータをダウンロードするため）:

```bash
export AWS_ACCESS_KEY_ID=あなたのアクセスキー
export AWS_SECRET_ACCESS_KEY=あなたのシークレットキー
export AWS_DEFAULT_REGION=ap-northeast-1  # 必要に応じて変更
```

2. Docker Composeを使用してサービスを起動します:

```bash
docker-compose up -d
```

これにより、Inpit SQLiteサービス（ポート5001）とMCPサーバー（ポート8000）の両方が起動します。

## Claude統合

### VSCode Claude拡張機能の場合

以下を `~/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` に追加します：

```json
{
  "mcpServers": {
    "inpit-sqlite": {
      "command": "python",
      "args": ["/path/to/inpit-sqlite-mcp/app/server.py"],
      "env": {
        "INPIT_API_URL": "http://localhost:5001"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Claude Desktop Appの場合

適切な設定ファイルに同様の設定を追加します。

## Difyとの統合

このMCPサーバーをDifyで使用するには：

### 1. MCP設定ファイルをDify用に準備

Difyを実行しているサーバーで、このMCPサーバーを実行し、Difyの設定でClaudeがこのMCPサーバーにアクセスできるようにします。

### 2. Dify設定手順

1. Difyにログインし、新しいアプリケーションを作成するか、既存のアプリケーションを編集します
2. モデルプロバイダーとしてClaudeを選択します
3. Claudeの設定で、MCPサーバーの設定を追加します：
   - サーバー名: `inpit-sqlite`
   - サーバーURL: `http://localhost:8000`（MCPサーバーが実行されているURL）
   - 有効化: チェックを入れる

### 3. Dify TOOLS LIST の設定方法

Difyでは、MCPサーバーが提供するツールをClaudeで利用できるようにするために、TOOLS LISTを設定する必要があります。以下の手順で設定します：

1. Difyダッシュボードで、アプリケーションの「モデル」設定に移動します
2. 「MCP統合」セクションで、追加したMCPサーバー（inpit-sqlite）の詳細を開きます
3. 「ツール一覧」の編集ボタンをクリックします
4. 以下のツールを追加します：

```json
[
  {
    "name": "get_patent_by_application_number",
    "description": "出願番号で特許を検索します。部分一致もサポートしています。",
    "parameters": {
      "type": "object",
      "properties": {
        "application_number": {
          "type": "string",
          "description": "検索する出願番号（例: 2022-123456）"
        }
      },
      "required": ["application_number"]
    }
  },
  {
    "name": "get_patents_by_applicant",
    "description": "出願人名で特許を検索します。部分一致もサポートしています。",
    "parameters": {
      "type": "object",
      "properties": {
        "applicant_name": {
          "type": "string",
          "description": "検索する出願人名（例: テック株式会社）"
        }
      },
      "required": ["applicant_name"]
    }
  },
  {
    "name": "execute_sql_query",
    "description": "Inpit SQLiteデータベースに対してSQLクエリを実行します。SELECT文のみサポートしています。",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "実行するSQLクエリ（例: SELECT 出願人, COUNT(*) as count FROM inpit_data GROUP BY 出願人 ORDER BY count DESC LIMIT 10）"
        }
      },
      "required": ["query"]
    }
  }
]
```

5. 「保存」をクリックして設定を適用します

### 4. リソース設定

同様に「リソース一覧」も設定できます：

```json
[
  {
    "name": "Inpit SQLite API Status",
    "uri": "inpit-sqlite://status",
    "description": "データベースのステータス、レコード数、スキーマ情報などを提供します。"
  }
]
```

### 5. Dify API クエリの例

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

## OpenAPI 仕様を用いたDify統合

MCPサーバーをDifyに統合する別の方法として、OpenAPI仕様を使用する方法があります。以下のペットストア例のような形式で、より詳細にAPIを定義できます。

### inpit-mcp-server用 OpenAPI 仕様

以下のOpenAPI仕様を使用して、Difyにinpit-mcp-serverを統合できます：

```yaml
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Inpit SQLite MCP API
  description: 特許データベースに対する検索・クエリAPIを提供します
  license:
    name: MIT
servers:
  - url: http://localhost:8000
    description: ローカル開発サーバー
paths:
  /application/{application_number}:
    get:
      summary: 出願番号で特許を検索
      operationId: get_patent_by_application_number
      tags:
        - patents
      parameters:
        - name: application_number
          in: path
          description: 検索する出願番号
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 特許情報の取得に成功
          content:
            application/json:    
              schema:
                $ref: "#/components/schemas/Patent"
        default:
          description: 予期しないエラー
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
  /applicant/{applicant_name}:
    get:
      summary: 出願人名で特許を検索
      operationId: get_patents_by_applicant
      tags:
        - patents
      parameters:
        - name: applicant_name
          in: path
          description: 検索する出願人名
          required: true
          schema:
            type: string
        - name: limit
          in: query
          description: 返却する特許の最大数（最大100）
          required: false
          schema:
            type: integer
            maximum: 100
            format: int32
      responses:
        '200':
          description: 特許のリストの取得に成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Patents"
        default:
          description: 予期しないエラー
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
  /sql:
    post:
      summary: SQLクエリを実行
      operationId: execute_sql_query
      tags:
        - database
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: 実行するSQLクエリ（SELECT文のみ）
              required:
                - query
      responses:
        '200':
          description: クエリ実行成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/QueryResult"
        default:
          description: 予期しないエラー
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
  /status:
    get:
      summary: システム状態を取得
      operationId: get_system_status
      tags:
        - system
      responses:
        '200':
          description: システム状態の取得に成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/SystemStatus"
        default:
          description: 予期しないエラー
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
components:
  schemas:
    Patent:
      type: object
      required:
        - 出願番号
        - 出願日
        - 出願人
      properties:
        出願番号:
          type: string
          description: 特許の出願番号
        出願日:
          type: string
          description: 特許の出願日
        出願人:
          type: string
          description: 特許の出願人
        発明の名称:
          type: string
          description: 発明のタイトル
        要約:
          type: string
          description: 発明の要約
        IPC分類:
          type: string
          description: 国際特許分類
        審査状況:
          type: string
          description: 特許の審査状況
    Patents:
      type: object
      required:
        - patents
        - count
      properties:
        patents:
          type: array
          maxItems: 100
          items:
            $ref: "#/components/schemas/Patent"
        count:
          type: integer
          description: 検索結果の総数
    QueryResult:
      type: object
      required:
        - results
        - columns
      properties:
        results:
          type: array
          description: クエリの結果行
          items:
            type: object
        columns:
          type: array
          description: 結果のカラム名
          items:
            type: string
    SystemStatus:
      type: object
      required:
        - status
        - database
      properties:
        status:
          type: string
          description: サーバーの状態
        database:
          type: object
          properties:
            connected:
              type: boolean
              description: データベース接続状態
            record_count:
              type: integer
              description: データベースのレコード数
            schema:
              type: array
              items:
                type: string
              description: データベースのスキーマ
        version:
          type: string
          description: APIのバージョン
    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: integer
          format: int32
        message:
          type: string
```

### Difyでの OpenAPI 設定手順

1. Difyダッシュボードで、アプリケーションの「モデル」設定に移動します
2. 「MCP統合」セクションで、「OpenAPI定義を追加」ボタンをクリックします（または既存のMCPサーバーの「OpenAPI定義を編集」）
3. 以下の方法のいずれかで定義を追加します:
   - 上記の仕様を`openapi.yaml`ファイルに保存してアップロード
   - OpenAPIの定義内容を直接テキストエリアに貼り付け
   - リモートURLで公開されているOpenAPIスキーマを指定
4. 「検証」ボタンをクリックして、定義に問題がないか確認します
5. 「保存」をクリックして設定を適用します

### OpenAPI使用時の利点

1. **標準化**: RESTfulなAPIをOpenAPI仕様という広く採用されている標準で定義できます
2. **自動ドキュメント生成**: OpenAPIからAPIドキュメントを自動生成できます
3. **クライアントコード生成**: 様々な言語のクライアントコードを自動生成できます
4. **詳細な設定**: リクエスト/レスポンスの形式や認証方法など、より詳細な設定が可能です
5. **統合の容易さ**: 既存のAPIをOpenAPI仕様さえあれば簡単にDifyと統合できます

### OpenAPIとTOOLS LIST併用のベストプラクティス

複数のサービスを統合する場合や、より複雑なAPIを定義する場合は、以下のアプローチを検討してください：

1. 基本的なツールはTOOLS LISTで定義（シンプルで直感的）
2. 複雑なAPIや詳細な設定が必要なものはOpenAPI仕様を使用
3. 新機能を追加する際は、まず簡易的にTOOLS LISTで試し、安定したらOpenAPI仕様に移行

### Difyエージェントのインストラクション設定

Difyでエージェントを設定する際に、以下のようなインストラクションプロンプトを「プロンプトエディタ」に設定することで、AIエージェントが特許データベースにより効果的にアクセスできるようになります：

```
あなたは特許情報アシスタントです。inpit-sqlite MCPサーバーを介して特許データベースにアクセスし、ユーザーの質問に答えます。

【使用可能なツール】
1. get_patent_by_application_number - 出願番号で特許を検索
2. get_patents_by_applicant - 出願人名で特許を検索
3. execute_sql_query - SQLクエリで詳細な分析を実行

【データベース構造】
特許データは主に以下のフィールドを含みます：
- 出願番号: 特許の一意識別子
- 出願日: 特許が出願された日付
- 出願人: 特許を出願した企業/個人
- 発明の名称: 特許のタイトル
- 要約: 発明の簡潔な説明
- IPC分類: 国際特許分類コード
- 審査状況: 審査中、特許成立、拒絶など

【応答の指針】
1. 出願番号による検索の場合: 
   - 出願番号が特定できる質問では、get_patent_by_application_number を使用
   - 例: "2022-123456の特許について教えて"

2. 出願人による検索の場合:
   - 企業名や発明者名が含まれる質問では、get_patents_by_applicant を使用
   - 日本語の出願人名は正しく処理される
   - 例: "テック株式会社の特許を検索して"

3. 分析クエリの場合:
   - 統計や傾向分析の質問では、execute_sql_query を使用
   - SQLを明示的に表示して何を検索しているか説明する
   - 例: "出願数の多い企業トップ10を教えて"

【応答形式】
- 簡潔かつ正確な情報提供を心がける
- 技術的な用語は必要に応じて平易に説明する
- 検索結果が多い場合は要約と代表例を提示
- 表形式のデータは読みやすく整形する
- 日本語での応答を基本とする

ユーザーの質問を理解し、適切なツールを選択して特許情報を検索・分析してください。
```

このテンプレートは必要に応じてカスタマイズできます。例えば、特定の業界や技術分野に焦点を当てたバージョンを作成したり、エージェントの「人格」や応答スタイルを調整したりすることができます。

#### プロンプト設定のコツ

1. **明確なツール選択基準の提供**: AIがどの状況でどのツールを使うべきか明確にする
2. **データ構造の説明**: 特許データの主要フィールドを説明して、適切なクエリ構築を支援する
3. **具体例の提示**: 典型的な質問パターンとそれに対応するツール使用例を示す
4. **応答形式の指定**: 一貫性のある読みやすいフォーマットを指定する
5. **日本語対応の強調**: 日本語での検索や応答がサポートされていることを明記する

#### カスタムプロンプトの例（特定業界向け）

```
あなたは医療技術特許の専門アシスタントです。inpit-sqlite MCPを活用して、医療機器・製薬・バイオテクノロジー関連の特許情報を提供します。

【医療特許分析の焦点】
- 新規医療機器の技術動向
- 製薬企業の研究開発パターン
- バイオテクノロジーの特許活動
- 医療技術のクロスライセンスと提携

特に以下のIPC分類に注目してください：
- A61K: 医薬品製剤
- A61B: 診断・手術用機器
- C12N: 微生物・酵素関連
- G01N: 材料の化学的・物理的分析

医療技術分野の専門用語を適切に説明しつつ、技術動向や企業戦略の洞察を提供してください。
```

## 利用可能なツール

### 1. get_patent_by_application_number

出願番号で特許を検索します（部分一致もサポート）。

**パラメータ：**
- `application_number`（文字列）：検索する出願番号

**例：**
```
GET http://localhost:8000/application/2022-123456
```

### 2. get_patents_by_applicant

出願人名で特許を検索します（部分一致もサポート）。

**パラメータ：**
- `applicant_name`（文字列）：検索する出願人名

**例：**
```
GET http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
```

**注意：** 日本語などの非ASCII文字を含むURLを使用する場合は、必ずURL エンコーディングを行う必要があります。上記の例では「テック株式会社」がURL エンコードされています。

### 3. execute_sql_query

データベースに対して直接SQLクエリを実行します。

**パラメータ：**
- `query`（文字列）：実行するSQLクエリ（SELECT文のみ）

**例：**
```
POST http://localhost:8000/sql
Content-Type: application/x-www-form-urlencoded

query=SELECT 出願人, COUNT(*) as count FROM inpit_data GROUP BY 出願人 ORDER BY count DESC LIMIT 10
```

## リソース

### Inpit SQLite API ステータス

URI: `inpit-sqlite://status`

データベースのステータス、レコード数、スキーマ情報などを返します。

## トラブルシューティング

- **接続の問題**：Inpit SQLiteサービスが設定されたURLで実行されていることを確認してください
- **データが見つからない**：データベースが特許データで適切に構築されていることを確認してください
- **権限エラー**：サーバーが実行に必要な権限を持っていることを確認してください
- **MCP設定**：ClaudeクライアントがこのMCPサーバーを使用するよう適切に設定されていることを確認してください
- **Dify統合の問題**：DifyがClaudeに適切なMCP設定を渡していることを確認してください
- **URLエンコーディングエラー**：日本語などの非ASCII文字を含むURLを使用する場合は、必ずURL エンコードを行ってください。例えば「テック」は「%E3%83%86%E3%83%83%E3%82%AF」としてエンコードします

問題や質問がある場合は、`/tmp/inpit-sqlite-mcp.log`にあるログファイルを確認してください。
