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
