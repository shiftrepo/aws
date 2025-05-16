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
                              │
                              │
                      ┌───────┴───────┐
                      │ Trend Analysis│
                      │   (Port 5006) │
                      │               │
                      └───────────────┘
```

各サービスはローカルのDockerfileからビルドされます：
- データベースサービス: ./db/Dockerfileからビルド
- 自然言語クエリサービス: ./app/nl-query/Dockerfileからビルド
- Web UIサービス: ./app/webui/Dockerfileからビルド
- トレンド分析サービス: ./app/trend-analysis/Dockerfileからビルド

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

### トレンド分析サービス（ポート5006）

このサービスは特許出願のトレンド分析を行います：

- `/health` - ヘルスチェックエンドポイント
- `/analyze` - 出願人別の特許分類トレンド分析（年別・分類別の出願件数）
- `/analyze_pdf` - 出願人別の分析レポートをPDF形式で生成
- `/analyze_classification` - 特許分類別のトレンド分析（年別・出願人別の出願件数）
- `/analyze_classification_pdf` - 特許分類別の分析レポートをPDF形式で生成
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

### トレンド分析サービスAPI

#### 1. 出願人別・分類別の特許トレンド分析

```bash
curl -X POST http://localhost:5006/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "テック株式会社",
    "start_year": 2010,
    "end_year": 2023
  }'
```

応答例：
```json
{
  "applicant_name": "テック株式会社",
  "yearly_classification_counts": {
    "2010": {"A": 12, "B": 8, "C": 5, "G": 23, "H": 45},
    "2011": {"A": 14, "B": 10, "C": 7, "G": 28, "H": 52},
    "2012": {"A": 15, "B": 11, "C": 8, "G": 30, "H": 54}
    // 他の年も同様...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA_HERE",
  "assessment": "テック株式会社の特許出願分析:\n\n1. 全体的な特許活動: 2010年から2023年にかけて特許出願は着実に増加傾向にあります。\n\n2. 主要技術分野:\n   - H（電気）: 全出願の約45%を占める主要分野\n   - G（物理学）: 全出願の約30%を占める第二の主要分野\n   - A（生活必需品）: 全出願の約12%を占める成長分野\n\n3. 最大出願年: 2021年に最も多くの出願（168件）がありました。\n\n4. 技術多様化: 技術領域は2010年の4分野から2023年の6分野へと拡大し、研究開発の幅が広がっていることを示しています。"
}
```

#### 2. 出願人別特許分析のPDFレポート生成

```bash
curl -X POST http://localhost:5006/analyze_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "テック株式会社",
    "start_year": 2010,
    "end_year": 2023
  }' \
  --output テック株式会社_特許分析.pdf
```

応答: PDF形式のレポートファイルが生成され、指定した出力ファイルに保存されます。

PDFレポートには以下が含まれます:
- 会社名と分析期間
- 特許出願トレンドの詳細評価
- 棒グラフによる分類別・年別の特許出願件数の可視化
- 主要な技術分野と注目すべきパターンの解説

#### 3. 特許分類別・出願人別のトレンド分析

```bash
curl -X POST http://localhost:5006/analyze_classification \
  -H "Content-Type: application/json" \
  -d '{
    "classification_code": "G",
    "start_year": 2010,
    "end_year": 2023
  }'
```

応答例：
```json
{
  "classification_code": "G",
  "yearly_applicant_counts": {
    "2010": {"テック株式会社": 23, "電子システム株式会社": 18, "ABC Technologies": 15, "XYZ研究所": 12, "Future Systems Inc": 10},
    "2011": {"テック株式会社": 28, "電子システム株式会社": 22, "ABC Technologies": 19, "Future Systems Inc": 14, "サイエンス株式会社": 11},
    "2012": {"テック株式会社": 30, "電子システム株式会社": 25, "ABC Technologies": 22, "サイエンス株式会社": 18, "Future Systems Inc": 15}
    // 他の年も同様...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA_HERE",
  "assessment": "IPC分類 G（物理学）の特許出願分析:\n\n1. 全体的な傾向: 物理学分野の特許出願は2010年から2023年にかけて着実に増加傾向にあります。\n\n2. 主要出願人:\n   - テック株式会社: 全出願の約22%を占める主要出願人\n   - 電子システム株式会社: 全出願の約18%を占める第二の主要出願人\n   - ABC Technologies: 全出願の約15%を占める主要国際出願人\n\n3. 最大出願年: 2022年に最も多くの出願（245件）がありました。\n\n4. 出願人多様化: この分類における出願人数は2010年の12社から2023年の25社へと増加し、この技術分野での競争が激化していることを示しています。"
}
```

#### 4. 特許分類別分析のPDFレポート生成

```bash
curl -X POST http://localhost:5006/analyze_classification_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "classification_code": "G",
    "start_year": 2010,
    "end_year": 2023
  }' \
  --output G分類_特許分析.pdf
```

応答: PDF形式のレポートファイルが生成され、指定した出力ファイルに保存されます。

PDFレポートには以下が含まれます:
- 分類コードと分類名（例：G - 物理学）
- 分類における特許出願トレンドの詳細評価
- 棒グラフによる主要出願人別・年別の特許出願件数の可視化
- 分類における市場状況と競争環境の解説
- 年による出願人多様性の変化

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

## OpenAPI仕様とDify統合

各APIサービスは、Difyやその他のAIプラットフォームとの統合を容易にするために、OpenAPI 3.1.0仕様を提供しています。これらの仕様は `openapi-specs` ディレクトリに格納されています。

### OpenAPI仕様ファイル

以下のOpenAPI仕様ファイルが利用可能です：

1. **データベースAPI** (`database-api-spec.json`) - SQLクエリの実行とデータベーススキーマへのアクセス用
2. **自然言語クエリAPI** (`nl-query-api-spec.json`) - AWS Bedrockを使用した自然言語クエリ処理用
3. **トレンド分析API** (`trend-analysis-api-spec.json`) - 特許トレンド分析とレポート生成用

### Difyでの使用方法

Difyダッシュボードでこれらの仕様ファイルをインポートして、カスタムツールプロバイダーとして設定できます：

1. Difyダッシュボードで「モデルプロバイダー」>「ツールプロバイダー」>「カスタムツールプロバイダーを追加」を選択
2. 名前を入力（例：「SQLiteデータベースAPI」）
3. 対応するOpenAPI仕様ファイルの内容をアップロードまたは貼り付け
4. 必要に応じて認証を設定（デフォルトでは認証なし）
5. プロバイダーを保存

### データベースAPI設定例

```json
{
  "name": "SQLite Database API",
  "description": "特許データを含むSQLiteデータベースとやり取りするためのAPI",
  "base_url": "http://localhost:5003",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "executeQuery",
      "description": "指定されたデータベースでSQLクエリを実行する"
    },
    {
      "name": "getSchema",
      "description": "指定されたデータベースのスキーマを取得する"
    },
    {
      "name": "getSampleQueries",
      "description": "データベース用のサンプルSQLクエリを取得する"
    },
    {
      "name": "listDatabases",
      "description": "利用可能なすべてのデータベースを一覧表示する"
    }
  ]
}
```

### 自然言語クエリAPI設定例

```json
{
  "name": "Natural Language Query API",
  "description": "AWS Bedrockモデルを使用して自然言語クエリを処理するためのAPI",
  "base_url": "http://localhost:5004",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "processNaturalLanguageQuery",
      "description": "自然言語クエリを処理してSQLに変換する"
    }
  ]
}
```

### トレンド分析API設定例

```json
{
  "name": "Patent Trend Analysis API",
  "description": "出願人別の特許分類トレンドを分析しレポートを生成するためのAPI",
  "base_url": "http://localhost:5006",
  "auth": {
    "type": "none"
  },
  "tools": [
    {
      "name": "analyzePatentTrends",
      "description": "特定の出願人の分類別・年別特許トレンドを分析する"
    },
    {
      "name": "generatePatentTrendsPDF",
      "description": "特定の出願人の分類別特許トレンドのPDFレポートを生成する"
    },
    {
      "name": "analyzeClassificationTrends",
      "description": "特定の特許分類の出願人別・年別トレンドを分析する"
    },
    {
      "name": "generateClassificationTrendsPDF",
      "description": "特定の特許分類の出願人別トレンドのPDFレポートを生成する"
    }
  ]
}
```

### Difyアプリケーションでのツールの使用例

Difyアプリケーションでこれらのツールを使用する際のプロンプト例：

#### データベースAPIの例
```
bigqueryデータベースに次のクエリを実行してください：
SELECT publication_number, title FROM publications WHERE title LIKE '%artificial intelligence%' LIMIT 10
```

#### 自然言語クエリAPIの例
```
bigqueryデータベースに対して次の質問を処理してください：
米国と日本の特許公開件数を比較して
```

#### トレンド分析APIの例
```
テック株式会社の2015年から2023年の特許トレンドを分析してください
```

### 既存のMCP設定例

旧来のMCP設定もまだサポートされています：

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

```yaml
name: Trend Analysis MCP Server
description: 特許出願トレンド分析（出願人名別・分類別）
base_url: http://localhost:5006
auth:
  type: none
tools:
  - name: analyze_patent_trends
    description: 出願人名を基に特許出願の分類別トレンドを分析し、可視化と評価を提供
    parameters:
      type: object
      required:
        - applicant_name
      properties:
        applicant_name:
          type: string
          description: 分析対象の出願人/企業名
        start_year:
          type: integer
          description: 分析期間の開始年（例：2010）
        end_year:
          type: integer
          description: 分析期間の終了年（例：2023）
  - name: generate_patent_report_pdf
    description: 出願人名を基に特許出願分析レポートをPDF形式で生成
    parameters:
      type: object
      required:
        - applicant_name
      properties:
        applicant_name:
          type: string
          description: レポート対象の出願人/企業名
        start_year:
          type: integer
          description: 分析期間の開始年
        end_year:
          type: integer
          description: 分析期間の終了年
  - name: analyze_classification_trends
    description: 特許分類コードを基に出願人別トレンドを分析し、可視化と評価を提供
    parameters:
      type: object
      required:
        - classification_code
      properties:
        classification_code:
          type: string
          description: 分析対象のIPC特許分類コード（例：A, B, C, G, H）
        start_year:
          type: integer
          description: 分析期間の開始年（例：2010）
        end_year:
          type: integer
          description: 分析期間の終了年（例：2023）
  - name: generate_classification_report_pdf
    description: 特許分類コードを基に分析レポートをPDF形式で生成
    parameters:
      type: object
      required:
        - classification_code
      properties:
        classification_code:
          type: string
          description: レポート対象のIPC特許分類コード（例：A, B, C, G, H）
        start_year:
          type: integer
          description: 分析期間の開始年
        end_year:
          type: integer
          description: 分析期間の終了年
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
