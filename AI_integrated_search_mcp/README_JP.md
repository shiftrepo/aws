# AI Integrated Search MCP

AWS Bedrockを活用したSQLiteデータベースと自然言語クエリを組み合わせたシステムで、Dify統合用のMCPサーバーとして設計されています。

## 概要

このシステムは、直接SQLクエリと自然言語クエリの両方を通してSQLiteデータベースと対話するための総合的なソリューションを提供します。主要な3つのコンポーネントから構成されています：

1. **データベースサービス**: S3からSQLiteデータベースをダウンロードし、それらと対話するためのAPIを提供するサービス
2. **自然言語クエリサービス**: AWS Bedrockモデルを使用して自然言語クエリをSQLに変換するサービス
3. **Web UI**: ユーザーがウェブブラウザを通して両方のサービスと対話できるユーザーインターフェース

## アーキテクチャ

システムはコンテナ化されたマイクロサービスアーキテクチャを使用して構築されています。すべてのコンテナはDockerfile からローカルでビルドされ、Docker Hubからプルされることはありません：

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │
│    Web UI     │◄────►│  Database API │◄────►│     AWS S3    │
│   (Port 5002) │      │   (Port 5003) │      │               │
│               │      │               │      └───────────────┘
└───────┬───────┘      └───────┬───────┘
        │                      │
        │                      │
        │              ┌───────┴───────┐      ┌───────────────┐
        │              │  NL Query API │      │  AWS Bedrock  │
        └──────────────►   (Port 5004) │◄────►│     Claude    │
                       │               │      │               │
                       └───────────────┘      └───────────────┘
```

各サービスはローカルのDockerfileからビルドされます：
- データベースサービス: ./db/Dockerfileからビルド
- 自然言語クエリサービス: ./app/nl-query/Dockerfileからビルド
- Web UIサービス: ./app/webui/Dockerfileからビルド

## 前提条件

- podman と podman-compose
- AWS認証情報の設定（AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION）
- AWS Bedrockサービスへのアクセス（Claude、Titan Embedding、Rerankモデル）

## 使い始め方

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd AI_integrated_search_mcp
```

### 2. AWS認証情報の設定

環境変数にAWS認証情報を設定します：

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=your_aws_region
```

### 3. サービスの起動

```bash
./scripts/start_services.sh
```

スクリプトは以下のことを行います：
- AWS認証情報の確認
- Dockerfileからすべてのサービスをローカルでビルド（Docker Hubからのプルなし）
- podman-composeを使用して全サービスを起動
- すべてのサービスが実行されていることを確認
- サービスにアクセスするためのURLを表示

**重要な注意**: すべてのコンテナイメージはリポジトリ内のDockerfileを使用してローカルでビルドされ、Docker Hubからプルされることはありません。これにより、コンテナに対する完全な制御が確保され、外部依存関係が防止されます。

### 4. Web UIへのアクセス

ウェブブラウザを開き、以下のURLにアクセスします：
```
http://localhost:5002
```

## サービス

### データベースサービス（ポート5003）

このサービスはS3からSQLiteデータベースをダウンロードし、それらと対話するためのAPIを提供します：

- `/health` - ヘルスチェックエンドポイント
- `/databases` - 利用可能なデータベースの一覧表示
- `/schema/{db_name}` - 特定のデータベースのスキーマ取得
- `/execute/{db_name}` - データベース上でSQLクエリを実行
- `/sample_queries/{db_name}` - データベースのサンプルクエリ取得
- `/docs` - API ドキュメント

### 自然言語クエリサービス（ポート5004）

このサービスは自然言語クエリをSQLに変換します：

- `/health` - ヘルスチェックエンドポイント
- `/query/{db_name}` - 自然言語クエリの処理
- `/docs` - API ドキュメント

### Web UI（ポート5002）

Webインターフェースでは、ユーザーは以下のことができます：
- 利用可能なデータベースの表示
- シンタックスハイライトを使用したSQLクエリの実行
- データベースに関する自然言語での質問
- データベーススキーマの表示
- テンプレートとしてのサンプルクエリの使用
- クエリ結果のCSVエクスポート

## HTTPAPIの使用例

### データベースサービスAPI

#### 1. 利用可能なデータベースの取得

```bash
curl -X GET http://localhost:5003/databases
```

応答例：
```json
{
  "databases": ["inpit", "bigquery"]
}
```

#### 2. データベーススキーマの取得

```bash
curl -X GET http://localhost:5003/schema/bigquery
```

応答例：
```json
{
  "schema": {
    "publications": [
      {
        "cid": 0,
        "name": "publication_number",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 1,
        "name": "title",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 2,
        "name": "abstract",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 3,
        "name": "publication_date",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 4,
        "name": "country_code",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 5,
        "name": "family_id",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      }
    ],
    "patent_families": [
      {
        "cid": 0,
        "name": "family_id",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 1,
        "name": "family_size",
        "type": "INTEGER",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      },
      {
        "cid": 2,
        "name": "earliest_filing_date",
        "type": "TEXT",
        "notnull": 0,
        "dflt_value": null,
        "pk": 0
      }
    ]
  }
}
```

#### 3. SQLクエリの実行

```bash
curl -X POST http://localhost:5003/execute/bigquery \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT publication_number, title_ja FROM publications LIMIT 5"
  }'
```

応答例：
```json
{
  "database": "bigquery",
  "query": "SELECT publication_number, title FROM publications LIMIT 5",
  "columns": ["publication_number", "title"],
  "rows": [
    {"publication_number": "US20210123456A1", "title": "Artificial Intelligence System for Autonomous Vehicles"},
    {"publication_number": "EP3987654A1", "title": "Method and Apparatus for Signal Processing"},
    {"publication_number": "CN112345678A", "title": "Deep Learning Model for Medical Image Analysis"},
    {"publication_number": "JP2021987654A", "title": "再生可能エネルギー管理システム"},
    {"publication_number": "WO2021123456A1", "title": "Improved Semiconductor Manufacturing Process"}
  ],
  "row_count": 5,
  "execution_time_ms": 4.57
}
```

#### 4. サンプルクエリの取得

```bash
curl -X GET http://localhost:5003/sample_queries/bigquery
```

応答例：
```json
{
  "database": "bigquery",
  "sample_queries": [
    {
      "name": "List all tables",
      "query": "SELECT name FROM sqlite_master WHERE type='table';"
    },
    {
      "name": "Count patent families",
      "query": "SELECT COUNT(*) AS family_count FROM patent_families;"
    },
    {
      "name": "Count publications",
      "query": "SELECT COUNT(*) AS publication_count FROM publications;"
    },
    {
      "name": "Publications by country",
      "query": "SELECT country_code, COUNT(*) AS publication_count FROM publications GROUP BY country_code ORDER BY publication_count DESC LIMIT 15;"
    },
    {
      "name": "Patent family sizes",
      "query": "SELECT family_id, COUNT(*) AS family_size FROM publications GROUP BY family_id ORDER BY family_size DESC LIMIT 20;"
    },
    {
      "name": "Search publications by keyword",
      "query": "SELECT publication_number, title FROM publications WHERE title LIKE '%artificial intelligence%' LIMIT 20;"
    },
    {
      "name": "Recent patent publications",
      "query": "SELECT publication_number, title, publication_date FROM publications ORDER BY publication_date DESC LIMIT 15;"
    }
  ]
}
```

### 自然言語クエリサービスAPI

#### 1. 自然言語クエリの処理

```bash
curl -X POST http://localhost:5004/query/bigquery \
  -H "Content-Type: application/json" \
  -d '{
    "query": "米国と日本の特許公開件数を比較して"
  }'
```

応答例：
```json
{
  "user_query": "米国と日本の特許公開件数を比較して",
  "sql_query": "SELECT country_code, COUNT(*) AS publication_count FROM publications WHERE country_code IN ('US', 'JP') GROUP BY country_code ORDER BY publication_count DESC",
  "results": [
    {"country_code": "US", "publication_count": 12534},
    {"country_code": "JP", "publication_count": 8976}
  ],
  "row_count": 2,
  "columns": ["country_code", "publication_count"],
  "explanation": "このクエリでは、米国（US）と日本（JP）の特許公開件数を比較しました。データベースから各国のコードで絞り込み、国ごとの公開件数をカウントして降順に並べています。結果から、米国の特許公開件数が12,534件、日本が8,976件であることがわかります。この期間においては米国の方が日本よりも約40%多い特許を公開していることが示されています。"
}
```

## システムの使い方

### 直接SQLクエリ

1. http://localhost:5002 でWeb UIにアクセス
2. データベースを選択
3. SQLクエリタブを使用してSQLクエリを記述し実行
4. 結果をテーブル形式で表示

### 自然言語クエリ

1. http://localhost:5002 でWeb UIにアクセス
2. データベースを選択
3. 自然言語クエリタブに切り替え
4. 質問を日本語や英語などの自然言語で入力
5. 生成されたSQL、結果、AI生成の説明を表示

### データベーススキーマ

1. http://localhost:5002 でWeb UIにアクセス
2. データベースを選択
3. データベーススキーマタブに切り替え
4. テーブルとその列を閲覧

## データベース

システムは2つのデータベースで動作します：

1. **Inpitデータベース**: `s3://ndi-3supervision/MIT/demo/inpit/inpit.db`に配置
2. **BigQueryデータベース**: `s3://ndi-3supervision/MIT/demo/GCP/google_patents_gcp.db`に配置

## MCP統合

データベースAPIと自然言語クエリAPIの両方がDify統合用のMCPサーバーとして設計されています。`/openapi`エンドポイントでOpenAPI仕様を提供しています。

### Dify用のMCP設定例

```yaml
name: ai-integrated-search
server_url: http://localhost:5003
tools:
  - name: execute_sql
    description: Execute SQL query on a database
    parameters:
      - name: db_name
        description: Database name (input or bigquery)
        required: true
        type: string
        enum: [input, bigquery]
      - name: query
        description: SQL query to execute
        required: true
        type: string
resources:
  - name: get_schema
    description: Get database schema
    url: /schema/{db_name}
  - name: get_sample_queries
    description: Get sample SQL queries for a database
    url: /sample_queries/{db_name}
```

## 管理コマンド

### サービスの起動

```bash
./scripts/start_services.sh
```

### サービスの停止

```bash
./scripts/stop_services.sh
```

### ヘルスチェック

```bash
./scripts/check_health.sh
```

## トラブルシューティング

### コンテナ接続の問題

サービス同士が通信できない場合は、ネットワーク構成を確認してください：

```bash
podman network ls
podman inspect mcp-network
```

### データベースのダウンロード問題

データベースがダウンロードできない場合は、以下を確認してください：

1. AWS認証情報が正しく設定されている
2. S3バケットにアクセスできる
3. データベースサービスのログ：

```bash
podman logs sqlite-db
```

#### 不足しているデータベースの修正

ヘルスチェックでデータベースが不足していると報告された場合、提供されているスクリプトを使用して問題を解決できます：

```bash
# 不足しているデータベースを手動でダウンロードし、データベースサービスを再起動するには
./scripts/fix_missing_databases.sh
```

また、システムには起動プロセス中に自動的に呼び出される`download_databases.sh`スクリプトが含まれており、データベースが利用可能であることを確認します。

### サービスのヘルス問題

ヘルスチェックスクリプトを実行してください：

```bash
./scripts/check_health.sh
```

## セキュリティに関する注意

- AWS認証情報はコンテナまたはコードファイルに保存されることはありません
- 認証情報は環境変数から取得されます
- このシステムは内部使用向けに設計されており、適切なセキュリティ対策なしでインターネットに公開すべきではありません
