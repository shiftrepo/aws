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
curl -X GET http://localhost:5003/schema/inpit
```

応答例：
```json
{
  "schema": {
    "tables": [
      {
        "name": "patents",
        "columns": [
          {"name": "patent_id", "type": "TEXT"},
          {"name": "title", "type": "TEXT"},
          {"name": "abstract", "type": "TEXT"},
          {"name": "filing_date", "type": "DATE"},
          {"name": "grant_date", "type": "DATE"}
        ]
      },
      {
        "name": "inventors",
        "columns": [
          {"name": "inventor_id", "type": "TEXT"},
          {"name": "patent_id", "type": "TEXT"},
          {"name": "name", "type": "TEXT"},
          {"name": "country", "type": "TEXT"}
        ]
      }
    ]
  }
}
```

#### 3. SQLクエリの実行

```bash
curl -X POST http://localhost:5003/execute/inpit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT patent_id, title FROM patents LIMIT 5"
  }'
```

応答例：
```json
{
  "results": {
    "columns": ["patent_id", "title"],
    "rows": [
      ["US123456A", "改良された半導体デバイス"],
      ["US234567A", "効率的な太陽光発電パネル"],
      ["US345678A", "新規な電気自動車のバッテリー管理システム"],
      ["US456789A", "機械学習を用いた画像認識方法"],
      ["US567890A", "高効率熱交換器"]
    ]
  }
}
```

#### 4. サンプルクエリの取得

```bash
curl -X GET http://localhost:5003/sample_queries/inpit
```

応答例：
```json
{
  "sample_queries": [
    {
      "title": "最新の特許5件を表示",
      "query": "SELECT patent_id, title, grant_date FROM patents ORDER BY grant_date DESC LIMIT 5"
    },
    {
      "title": "日本人発明者の特許",
      "query": "SELECT p.patent_id, p.title, i.name FROM patents p JOIN inventors i ON p.patent_id = i.patent_id WHERE i.country = 'JP' LIMIT 10"
    }
  ]
}
```

### 自然言語クエリサービスAPI

#### 1. 自然言語クエリの処理

```bash
curl -X POST http://localhost:5004/query/inpit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2020年以降に申請された人工知能関連の特許を5件表示して"
  }'
```

応答例：
```json
{
  "natural_language_query": "2020年以降に申請された人工知能関連の特許を5件表示して",
  "sql_query": "SELECT patent_id, title, abstract, filing_date FROM patents WHERE filing_date >= '2020-01-01' AND (abstract LIKE '%人工知能%' OR abstract LIKE '%AI%' OR abstract LIKE '%機械学習%' OR title LIKE '%人工知能%' OR title LIKE '%AI%' OR title LIKE '%機械学習%') ORDER BY filing_date DESC LIMIT 5",
  "results": {
    "columns": ["patent_id", "title", "abstract", "filing_date"],
    "rows": [
      ["US987654A", "深層学習を用いた音声認識システム", "本発明は深層学習アルゴリズムを使用して...", "2023-03-15"],
      ["US876543A", "AIによる画像処理の方法", "本発明は人工知能技術を用いて...", "2022-11-02"],
      ["US765432A", "自動運転車両のための機械学習システム", "自動運転車両の判断能力を向上させるための...", "2022-05-18"],
      ["US654321A", "医療診断のためのAIアシスタント", "医療画像の解析と診断を支援するための...", "2021-08-23"],
      ["US543210A", "自然言語処理による文書要約システム", "大量のテキストデータから重要な情報を抽出し...", "2020-12-10"]
    ]
  },
  "explanation": "このクエリでは、filing_date（申請日）が2020年1月1日以降で、タイトルまたは概要に「人工知能」「AI」「機械学習」というキーワードを含む特許を検索しました。結果は申請日の新しい順に並べられ、上位5件を表示しています。"
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
