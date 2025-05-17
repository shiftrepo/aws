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

#### 1. ヘルスチェック（GET /health）

サービスが正常に動作しているか確認します。

```bash
curl -X GET http://localhost:5003/health
```

応答例：
```json
{
  "status": "ok",
  "service": "database-api",
  "version": "1.0.0",
  "databases": {
    "inpit": true,
    "bigquery": true
  },
  "timestamp": "2025-05-15T12:34:56Z"
}
```

#### 2. 利用可能なデータベースの取得（GET /databases）

システムで利用可能なすべてのデータベースを取得します。

```bash
curl -X GET http://localhost:5003/databases
```

応答例：
```json
{
  "databases": ["inpit", "bigquery"],
  "default": "bigquery",
  "available_count": 2,
  "status": "ok"
}
```

#### 3. データベーススキーマの取得（GET /schema/{db_name}）

指定したデータベースのテーブル構造とカラム情報を取得します。

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
  },
  "table_count": 2,
  "database": "bigquery"
}
```

```bash
# inpitデータベースのスキーマを取得する例
curl -X GET http://localhost:5003/schema/inpit
```

#### 4. SQLクエリの実行（POST /execute/{db_name}）

データベースに対してSQLクエリを実行します。

```bash
curl -X POST http://localhost:5003/execute/bigquery \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT publication_number, title FROM publications LIMIT 5"
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

```bash
# 複雑なSQLクエリの例（国別の特許公開件数を取得）
curl -X POST http://localhost:5003/execute/bigquery \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT country_code, COUNT(*) AS count FROM publications GROUP BY country_code ORDER BY count DESC LIMIT 10"
  }'
```

```bash
# 日付範囲を指定したSQLクエリの例
curl -X POST http://localhost:5003/execute/inpit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT publication_number, title, publication_date FROM publications WHERE publication_date BETWEEN \"2020-01-01\" AND \"2020-12-31\" LIMIT 10"
  }'
```

#### 5. サンプルクエリの取得（GET /sample_queries/{db_name}）

指定したデータベースのサンプルSQLクエリを取得します。

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
  ],
  "count": 7
}
```

```bash
# inpitデータベースのサンプルクエリを取得する例
curl -X GET http://localhost:5003/sample_queries/inpit
```

### 自然言語クエリサービスAPI

#### 1. ヘルスチェック（GET /health）

自然言語クエリサービスの稼働状況を確認します。

```bash
curl -X GET http://localhost:5004/health
```

応答例：
```json
{
  "status": "ok",
  "service": "nl-query-api",
  "version": "1.0.0",
  "bedrock_status": "connected",
  "database_api_status": "connected",
  "supported_languages": ["ja", "en"],
  "timestamp": "2025-05-15T12:34:56Z"
}
```

#### 2. 自然言語クエリの処理（POST /query/{db_name}）

自然言語の質問をSQLに変換し、結果を取得します（日本語または英語で質問できます）。

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

```bash
# 英語での自然言語クエリ例
curl -X POST http://localhost:5004/query/bigquery \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the top 5 companies with the most patent applications in the last 5 years"
  }'
```

```bash
# 特定の技術分野に関する日本語クエリ例
curl -X POST http://localhost:5004/query/inpit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工知能に関連する特許で、過去3年間で最も出願が増えた企業を教えて"
  }'
```

### トレンド分析サービスAPI

#### 1. ヘルスチェック（GET /health）

トレンド分析サービスの稼働状況を確認します。

```bash
curl -X GET http://localhost:5006/health
```

応答例：
```json
{
  "status": "ok",
  "service": "trend-analysis-api",
  "version": "1.0.0",
  "database_connection": true,
  "pdf_generation": true,
  "timestamp": "2025-05-15T12:34:56Z"
}
```

#### 2. 出願人別・分類別の特許トレンド分析（POST /analyze）

指定した出願人の特許分類別トレンドを分析します。

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
    "2012": {"A": 15, "B": 11, "C": 8, "G": 30, "H": 54},
    "2013": {"A": 16, "B": 13, "C": 9, "G": 33, "H": 59},
    "2014": {"A": 18, "B": 15, "C": 10, "G": 36, "H": 65}
    // 他の年も同様...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA_HERE",
  "assessment": "テック株式会社の特許出願分析:\n\n1. 全体的な特許活動: 2010年から2023年にかけて特許出願は着実に増加傾向にあります。\n\n2. 主要技術分野:\n   - H（電気）: 全出願の約45%を占める主要分野\n   - G（物理学）: 全出願の約30%を占める第二の主要分野\n   - A（生活必需品）: 全出願の約12%を占める成長分野\n\n3. 最大出願年: 2021年に最も多くの出願（168件）がありました。\n\n4. 技術多様化: 技術領域は2010年の4分野から2023年の6分野へと拡大し、研究開発の幅が広がっていることを示しています。",
  "analysis_period": "2010-2023",
  "total_applications": 1245
}
```

```bash
# 期間を指定しない例（デフォルトでは全期間が分析される）
curl -X POST http://localhost:5006/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "電子システム株式会社"
  }'
```

#### 3. 出願人別特許分析のPDFレポート生成（POST /analyze_pdf）

指定した出願人の分析レポートをPDF形式で生成します。

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
- 競合他社との比較分析
- 技術ポートフォリオのヒートマップ

```bash
# 英語名の企業分析例
curl -X POST http://localhost:5006/analyze_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Future Tech Corporation",
    "start_year": 2015,
    "end_year": 2025
  }' \
  --output FutureTech_Patent_Analysis.pdf
```

#### 4. 特許分類別・出願人別のトレンド分析（POST /analyze_classification）

特定のIPC分類コードについて、主要出願人のトレンドを分析します。

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
  "classification_name": "物理学",
  "yearly_applicant_counts": {
    "2010": {"テック株式会社": 23, "電子システム株式会社": 18, "ABC Technologies": 15, "XYZ研究所": 12, "Future Systems Inc": 10},
    "2011": {"テック株式会社": 28, "電子システム株式会社": 22, "ABC Technologies": 19, "Future Systems Inc": 14, "サイエンス株式会社": 11},
    "2012": {"テック株式会社": 30, "電子システム株式会社": 25, "ABC Technologies": 22, "サイエンス株式会社": 18, "Future Systems Inc": 15}
    // 他の年も同様...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA_HERE",
  "assessment": "IPC分類 G（物理学）の特許出願分析:\n\n1. 全体的な傾向: 物理学分野の特許出願は2010年から2023年にかけて着実に増加傾向にあります。\n\n2. 主要出願人:\n   - テック株式会社: 全出願の約22%を占める主要出願人\n   - 電子システム株式会社: 全出願の約18%を占める第二の主要出願人\n   - ABC Technologies: 全出願の約15%を占める主要国際出願人\n\n3. 最大出願年: 2022年に最も多くの出願（245件）がありました。\n\n4. 出願人多様化: この分類における出願人数は2010年の12社から2023年の25社へと増加し、この技術分野での競争が激化していることを示しています。",
  "analysis_period": "2010-2023",
  "total_applications": 875,
  "top_applicants": ["テック株式会社", "電子システム株式会社", "ABC Technologies", "サイエンス株式会社", "Future Systems Inc"]
}
```

```bash
# H分類（電気）のトレンド分析例
curl -X POST http://localhost:5006/analyze_classification \
  -H "Content-Type: application/json" \
  -d '{
    "classification_code": "H",
    "start_year": 2015,
    "end_year": 2023
  }'
```

#### 5. 特許分類別分析のPDFレポート生成（POST /analyze_classification_pdf）

特定の特許分類の分析レポートをPDF形式で生成します。

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
- 技術サブ分類の分布ヒートマップ

```bash
# A分類（生活必需品）のPDF分析レポート
curl -X POST http://localhost:5006/analyze_classification_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "classification_code": "A",
    "start_year": 2018,
    "end_year": 2023
  }' \
  --output A分類_特許分析.pdf
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
  "schema": {
    "openapi": "3.1.0",
    "info": {
      "title": "SQLite Database API",
      "description": "API for interacting with SQLite databases containing patent data",
      "version": "v1.0.0"
    },
    "servers": [
      {
        "url": "http://localhost:5003"
      }
    ],
    "paths": { ... }
  }
}
```

### 自然言語クエリAPI設定例

```json
{
  "name": "Natural Language Query API",
  "description": "自然言語クエリをSQLに変換してデータベースを検索するためのAPI",
  "schema": {
    "openapi": "3.1.0",
    "info": {
      "title": "Natural Language Query API",
      "description": "API for processing natural language queries using AWS Bedrock models to convert them to SQL",
      "version": "v1.0.0"
    },
    "servers": [
      {
        "url": "http://localhost:5004"
      }
    ],
    "paths": { ... }
  }
}
```

### トレンド分析API設定例

```json
{
  "name": "Patent Trend Analysis API",
  "description": "特許出願のトレンド分析を行い、視覚的レポートを生成するためのAPI",
  "schema": {
    "openapi": "3.1.0",
    "info": {
      "title": "Patent Trend Analysis API",
      "description": "API for analyzing patent classification trends by applicant and generating reports",
      "version": "v1.0.0"
    },
    "servers": [
      {
        "url": "http://localhost:5006"
      }
    ],
    "paths": { ... }
  }
}
```

## OpenAPIエンドポイントの詳細使用例

以下は、各OpenAPIエンドポイントの詳細な使用例です。これらのエンドポイントは、HTTPクライアント（curl、Postman、Python requests等）またはDifyプラットフォームから直接アクセスできます。

### データベースAPI（localhost:5003）のエンドポイント

#### 1. SQLクエリ実行 (POST /execute/{db_name})

**URLパラメータ:**
- db_name: データベース名（"input", "inpit", "bigquery"のいずれか）

**リクエスト本文:**
```json
{
  "query": "SELECT COUNT(*) AS total_patents FROM publications"
}
```

**レスポンス例:**
```json
{
  "database": "bigquery",
  "query": "SELECT COUNT(*) AS total_patents FROM publications",
  "columns": ["total_patents"],
  "rows": [
    {"total_patents": 125784}
  ],
  "row_count": 1,
  "execution_time_ms": 3.25
}
```

**複雑なクエリ例:**
```json
{
  "query": "SELECT p.publication_number, p.title, p.publication_date, p.country_code, pf.family_size FROM publications p JOIN patent_families pf ON p.family_id = pf.family_id WHERE p.publication_date >= '2020-01-01' AND p.title LIKE '%artificial intelligence%' ORDER BY pf.family_size DESC LIMIT 10"
}
```

#### 2. データベーススキーマ取得 (GET /schema/{db_name})

**URLパラメータ:**
- db_name: データベース名（"input", "inpit", "bigquery"のいずれか）

**レスポンス例:**
```json
{
  "schema": {
    "publications": [
      {"name": "publication_number", "type": "TEXT", ...},
      {"name": "title", "type": "TEXT", ...},
      {"name": "abstract", "type": "TEXT", ...},
      {"name": "publication_date", "type": "TEXT", ...},
      ...
    ],
    "patent_families": [
      {"name": "family_id", "type": "TEXT", ...},
      {"name": "family_size", "type": "INTEGER", ...},
      {"name": "earliest_filing_date", "type": "TEXT", ...},
      ...
    ],
    ...
  },
  "table_count": 5,
  "database": "bigquery"
}
```

#### 3. サンプルクエリ取得 (GET /sample_queries/{db_name})

**URLパラメータ:**
- db_name: データベース名（"input", "inpit", "bigquery"のいずれか）

**レスポンス例:**
```json
{
  "database": "inpit",
  "sample_queries": [
    {
      "name": "出願人TOP10",
      "query": "SELECT applicant_name, COUNT(*) AS application_count FROM applicants GROUP BY applicant_name ORDER BY application_count DESC LIMIT 10"
    },
    {
      "name": "分類別出願件数",
      "query": "SELECT classification_code, COUNT(*) AS count FROM classifications GROUP BY classification_code ORDER BY count DESC"
    },
    ...
  ],
  "count": 12
}
```

#### 4. 利用可能なデータベース一覧 (GET /databases)

**レスポンス例:**
```json
{
  "databases": ["inpit", "bigquery"],
  "default": "bigquery",
  "available_count": 2,
  "status": "ok"
}
```

#### 5. ヘルスチェック (GET /health)

**レスポンス例:**
```json
{
  "status": "ok",
  "service": "database-api",
  "version": "1.0.0",
  "databases": {
    "inpit": true,
    "bigquery": true
  },
  "timestamp": "2025-05-17T21:15:00Z"
}
```

### 自然言語クエリAPI（localhost:5004）のエンドポイント

#### 1. 自然言語クエリ処理 (POST /query/{db_name})

**URLパラメータ:**
- db_name: データベース名（"input", "inpit", "bigquery"のいずれか）

**リクエスト本文:**
```json
{
  "query": "2020年以降に出願された人工知能に関する特許のうち、最も出願件数の多い5社を教えて"
}
```

**レスポンス例:**
```json
{
  "user_query": "2020年以降に出願された人工知能に関する特許のうち、最も出願件数の多い5社を教えて",
  "sql_query": "SELECT applicant_name, COUNT(*) AS application_count FROM publications p JOIN applicants a ON p.publication_number = a.publication_number WHERE p.publication_date >= '2020-01-01' AND (p.title LIKE '%人工知能%' OR p.title LIKE '%AI%' OR p.title LIKE '%artificial intelligence%') GROUP BY applicant_name ORDER BY application_count DESC LIMIT 5",
  "results": [
    {"applicant_name": "テック株式会社", "application_count": 156},
    {"applicant_name": "Samsung Electronics Co., Ltd.", "application_count": 134},
    {"applicant_name": "IBM Corporation", "application_count": 128},
    {"applicant_name": "電子システム株式会社", "application_count": 102},
    {"applicant_name": "Google LLC", "application_count": 98}
  ],
  "row_count": 5,
  "columns": ["applicant_name", "application_count"],
  "explanation": "このクエリでは2020年1月1日以降に公開された特許から、タイトルに「人工知能」「AI」または「artificial intelligence」を含む特許を検索し、出願人ごとの出願件数を集計しました。その結果、テック株式会社が156件と最も多く、次いでSamsung Electronics、IBM、電子システム株式会社、Google LLCという順になっています。この結果から、日本企業とグローバル企業の両方が人工知能分野で積極的な特許活動を行っていることが分かります。"
}
```

**英語の自然言語クエリ例:**
```json
{
  "query": "What is the trend of patent applications in the field of renewable energy over the last decade?"
}
```

#### 2. ヘルスチェック (GET /health)

**レスポンス例:**
```json
{
  "status": "ok",
  "service": "nl-query-api",
  "version": "1.0.0",
  "bedrock_status": "connected",
  "database_api_status": "connected",
  "supported_languages": ["ja", "en"],
  "timestamp": "2025-05-17T21:15:00Z"
}
```

### トレンド分析API（localhost:5006）のエンドポイント

#### 1. 出願人別・分類別トレンド分析 (POST /analyze)

**リクエスト本文:**
```json
{
  "applicant_name": "テック株式会社",
  "start_year": 2015,
  "end_year": 2023
}
```

**レスポンス例:**
```json
{
  "applicant_name": "テック株式会社",
  "yearly_classification_counts": {
    "2015": {"A": 15, "B": 12, "C": 8, "G": 35, "H": 67},
    "2016": {"A": 18, "B": 14, "C": 9, "G": 38, "H": 72},
    "2017": {"A": 22, "B": 16, "C": 11, "G": 42, "H": 78},
    ...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA",
  "assessment": "テック株式会社の特許出願分析...",
  "analysis_period": "2015-2023",
  "total_applications": 1457
}
```

#### 2. 出願人別PDF分析レポート生成 (POST /analyze_pdf)

**リクエスト本文:**
```json
{
  "applicant_name": "テック株式会社",
  "start_year": 2015,
  "end_year": 2023
}
```

**レスポンス:** PDF形式のレポートファイルが返されます。

#### 3. 特許分類別・出願人別トレンド分析 (POST /analyze_classification)

**リクエスト本文:**
```json
{
  "classification_code": "G06N",
  "start_year": 2015,
  "end_year": 2023
}
```

**レスポンス例:**
```json
{
  "classification_code": "G06N",
  "classification_name": "コンピュータシステムに基づく特定の計算モデル",
  "yearly_applicant_counts": {
    "2015": {"テック株式会社": 18, "IBM Corporation": 22, "Microsoft Corporation": 15, ...},
    "2016": {"テック株式会社": 25, "IBM Corporation": 26, "Google LLC": 19, ...},
    ...
  },
  "chart_image": "BASE64ENCODED_IMAGE_DATA",
  "assessment": "G06N分類（コンピュータシステムに基づく特定の計算モデル）の分析...",
  "analysis_period": "2015-2023",
  "total_applications": 2354,
  "top_applicants": ["IBM Corporation", "テック株式会社", "Google LLC", "Microsoft Corporation", "電子システム株式会社"]
}
```

#### 4. 特許分類別PDF分析レポート生成 (POST /analyze_classification_pdf)

**リクエスト本文:**
```json
{
  "classification_code": "G06N",
  "start_year": 2015,
  "end_year": 2023
}
```

**レスポンス:** PDF形式のレポートファイルが返されます。

#### 5. ヘルスチェック (GET /health)

**レスポンス例:**
```json
{
  "status": "ok",
  "service": "trend-analysis-api",
  "version": "1.0.0",
  "database_connection": true,
  "pdf_generation": true,
  "timestamp": "2025-05-17T21:15:00Z"
}
```

## Dify統合の詳細手順

DifyプラットフォームでこれらのAPIをツールとして統合する手順は以下の通りです：

### 1. Dify管理画面へのログイン

Difyの管理ダッシュボードにログインします。

### 2. ツールプロバイダーの追加

1. 左メニューの「モデル」→「ツールプロバイダー」に移動します
2. 「+ツールプロバイダー」ボタンをクリックします
3. 「OpenAPI仕様からインポート」を選択します

### 3. データベースAPIの追加

1. プロバイダー名に「SQLite Database API」と入力します
2. 「OpenAPIのURL」または「OpenAPI仕様を入力」から、`database-api-spec.json`の内容を貼り付けます
3. 「インポート」をクリックし、正常に読み込まれたことを確認します
4. 「保存」をクリックします

### 4. 自然言語クエリAPIの追加

1. 同様の手順で、プロバイダー名に「Natural Language Query API」と入力します
2. `nl-query-api-spec.json`の内容を貼り付けます
3. インポートして保存します

### 5. トレンド分析APIの追加

1. 同様の手順で、プロバイダー名に「Patent Trend Analysis API」と入力します
2. `trend-analysis-api-spec.json`の内容を貼り付けます
3. インポートして保存します

### 6. アプリケーションでのツール有効化

1. Difyで使用したいアプリケーションに移動します
2. 「開発」→「ツール」タブに移動します
3. 先ほど追加した3つのAPIを検索して有効にします

### 7. ツールの構成

各ツールの説明を編集し、AIがそのツールを適切に使用できるようにすることができます。

### 8. プロンプト設定

AIが適切なタイミングでこれらのツールを使うよう、プロンプトに説明を追加します。例：

```
あなたは特許データ分析アシスタントです。データベースAPI、自然言語クエリAPI、トレンド分析APIを使って、特許情報の検索や分析を支援します。
...
```

### 9. 動作確認

テストパネルで様々な質問をして、AIがツールを適切に使用できるかをテストします。例：

- 「テック株式会社の過去5年間の特許出願傾向を教えて」
- 「G分類の特許で最も出願の多い企業は？」
- 「人工知能に関する特許でトップ出願人を教えて」

これらの質問に対して、AIが適切なAPIを呼び出し、結果を分かりやすく説明することを確認します。
