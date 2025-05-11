# patentDWH（特許データウェアハウス）

patentDWHは、特許データのSQLiteベースのストレージと検索機能に加え、ユーザーフレンドリーなWebインターフェースとMCPサーバーを組み合わせた特許データウェアハウスシステムです。本システムはSQLクエリ、自然言語問い合わせ、特許分析などの多様な機能を提供します。

## 目次

- [概要](#概要)
- [機能](#機能)
- [必要条件](#必要条件)
- [インストールと起動](#インストールと起動)
- [使用方法](#使用方法)
  - [WebUI](#webui)
  - [コマンドラインインターフェース例](#コマンドラインインターフェース例)
  - [MCPサーバー](#mcpサーバー)
  - [自然言語クエリ](#自然言語クエリ)
  - [特許分析サービス](#特許分析サービス)
  - [特許分析MCPサーバー](#特許分析mcpサーバー)
- [テーブル構造](#テーブル構造)
- [統合起動方法](#統合起動方法)
- [サービスの起動と停止](#サービスの起動と停止)
- [詳細ログとトラブルシューティング](#詳細ログとトラブルシューティング)
- [ソースコードSTEP数](#ソースコードstep数)

## 概要

このシステムは主に3つのコンポーネントで構成されています：

1. **特許データベース（patentdwh-db）**：特許データを直接クエリするためのWebインターフェースを備えたSQLiteベースのデータベース。
2. **MCPサーバー（patentdwh-mcp）**：ClaudeなどのAIアシスタントが特許データベースとやり取りするためのModel Context Protocol（MCP）サーバー。
3. **特許分析サービス（patent-analysis）**：特定の出願人の特許出願動向を分析し、視覚化とレポート生成を行います。

このシステムは3つの異なる特許データベースへのアクセスを提供します：

- **INPIT（特許庁）データベース**：日本特許庁からの特許データ。
- **Google Patents GCPデータベース**：BigQueryからのGoogle Patents特許データ。
- **Google Patents S3データベース**：S3に保存されているGoogle Patents特許データ。

## 機能

- **自然言語クエリ**：AWS Bedrock（Claude 3 Sonnet、Titan Embedding）を利用した特許データへの自然言語クエリ機能。
- **SQLクエリ用WebUI**：すべてのデータベースに対してSQLクエリを実行するための直接的なWebインターフェース。
- **SQLサンプル**：一般的な特許検索用の事前構築されたSQLクエリ例。
- **MCP統合**：AIアシスタント統合のための完全なMCPサーバー実装。
- **マルチデータベースサポート**：同じインターフェースで異なる特許データベースをクエリ。
- **RESTful API**：データベースへのプログラム的アクセスのためのAPIエンドポイント。
- **特許分析**：出願人別の特許分類トレンド分析とレポート生成。
- **Dify統合**：特許分析サービスをDifyプラットフォームと統合するためのOpenAPI。

## 必要条件

- Docker またはPodman
- Docker Compose またはPodman Compose
- インターネット接続（初期データダウンロード用）
- AWS認証情報（環境変数経由で提供）

## インストールと起動

### 環境変数の設定

AWS認証情報を環境変数として設定します:

```bash
export AWS_ACCESS_KEY_ID="your_aws_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_REGION="us-east-1"  # 必要に応じて変更
```

### 従来の方法（各サービス個別）

1. リポジトリをクローンします：
   ```bash
   git clone <repository-url>
   cd patentDWH
   ```

2. セットアップスクリプトを実行します：
   ```bash
   ./init_setup.sh
   ```

3. 特許分析サービスを使用する場合は、別途起動します：
   ```bash
   cd ../patent_analysis_container
   podman-compose build
   podman-compose run patent-analysis "出願人名" [db_type]
   ```

4. 特許分析MCPサーバーを起動する場合：
   ```bash
   cd ../patent_analysis_container
   chmod +x start_mcp_service.sh
   ./start_mcp_service.sh
   ```

### 統合方法（詳細は[統合起動方法](#統合起動方法)を参照）

1. 統合セットアップスクリプトを実行します：
   ```bash
   cd patentDWH
   ./init_consolidated_setup.sh
   ```

2. 特許分析を実行する場合：
   ```bash
   podman-compose -f docker-compose.consolidated.yml run patent-analysis "出願人名" [db_type]
   ```

## 使用方法

### WebUI

- **データベースUI**：http://localhost:5002/ でアクセス可能
- Webインターフェースは3つの主要なセクションを提供します：
  - INPIT SQLサンプル
  - Google Patents GCPサンプル
  - Google Patents S3サンプル
  - フリーSQLクエリツール

### コマンドラインインターフェース例

#### サービスの起動と停止

```bash
# サービスを起動する
./init_setup.sh
# または統合版
./init_consolidated_setup.sh

# すべてのサービスを一括で起動する（推奨）
./start_all_services.sh

# サービスの状態を確認する
curl http://localhost:5002/health
curl http://localhost:8080/health
curl http://localhost:8000/health  # 特許分析MCPサーバー

# ログを確認する
podman-compose logs -f
# または
podman-compose -f docker-compose.consolidated.yml logs -f

# サービスを停止する
podman-compose down
# または
podman-compose -f docker-compose.consolidated.yml down
# または（すべてのサービスを一括停止）
./stop_all_services.sh
```

#### SQLクエリの実行例

```bash
# INPITデータベースに対するクエリ例（curl使用）
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM inpit_data LIMIT 5", "db_type": "inpit"}' \
  http://localhost:5002/api/sql-query

# Google Patents GCPデータベースに対するクエリ例
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "SELECT publication_number, title_ja FROM publications LIMIT 5", "db_type": "google_patents_gcp"}' \
  http://localhost:5002/api/sql-query

# Google Patents S3データベースに対するクエリ例
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "SELECT publication_number, title_ja FROM publications LIMIT 5", "db_type": "google_patents_s3"}' \
  http://localhost:5002/api/sql-query
```

#### 自然言語クエリの実行例

```bash
# 自然言語クエリを直接実行
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "トヨタが出願した自動運転技術に関する特許は何件ありますか？", "db_type": "google_patents_gcp"}' \
  http://localhost:8080/api/nl-query

# MCP APIを使用した自然言語クエリの実行
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_nl_query",
    "tool_input": {
      "query": "ソニーが出願した人工知能関連の特許を教えてください",
      "db_type": "google_patents_gcp"
    }
  }' \
  http://localhost:8080/api/v1/mcp
```

#### 特許分析の実行例

```bash
# 特許分析の実行（通常方法）
cd patent_analysis_container
podman-compose run patent-analysis "トヨタ" inpit

# 特許分析の実行（統合方法）
cd patentDWH
podman-compose -f docker-compose.consolidated.yml run patent-analysis "トヨタ" inpit
```

#### 特許分析MCPサーバーの利用例

```bash
# 特許出願傾向の分析
curl -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "analyze_patent_trends",
    "tool_input": {
      "applicant_name": "トヨタ"
    }
  }'

# ZIPレポートのダウンロード
curl -X GET http://localhost:8000/api/report/トヨタ/zip -o toyota_report.zip
```

### MCPサーバー

MCPサーバーはhttp://localhost:8080/ で動作し、以下のツールを提供します：

1. **patent_sql_query**：任意の特許データベースに対してSQLクエリを実行します。
   ```json
   {
     "query": "SELECT * FROM inpit_data LIMIT 5",
     "db_type": "inpit"
   }
   ```

2. **patent_nl_query**：自然言語での質問を特許データベースに対して実行します。
   ```json
   {
     "query": "ソニーが出願した人工知能関連の特許を教えてください",
     "db_type": "google_patents_gcp"
   }
   ```
   
3. **check_aws_credentials**：AWS Bedrockサービスの認証情報が正しく設定されているか確認します。
   ```json
   {}
   ```

4. **get_database_info**：利用可能な特許データベースに関する情報を取得します。
   ```json
   {
     "db_type": null
   }
   ```

5. **get_sql_examples**：特定のデータベースタイプのSQLクエリ例を取得します。
   ```json
   {
     "db_type": "inpit"
   }
   ```

### 自然言語クエリ

patentDWHシステムの自然言語クエリ機能を使用すると、複雑なSQLクエリを書かなくても、日本語や英語で直接特許データベースに質問することができます。この機能は、AWS Bedrockの Claude 3 Sonnetモデルを使用してユーザーの質問をSQLに変換し、結果を自然言語で回答します。

**主な特徴**：

- 日本語と英語での質問をサポート
- 3種類のデータベース（INPIT、Google Patents GCP、Google Patents S3）に対応
- 特許の検索、統計分析、トレンド分析などの多様なクエリタイプをサポート
- 結果は分かりやすい自然言語で提供

**利用可能な質問例**：

```
テック株式会社が出願した特許は何件ありますか？
ソニーが出願した人工知能関連の特許を教えてください
IPCコードG06Fに属する特許の国別出願数を比較してください
自動運転技術において、トヨタとテスラの特許ポートフォリオの違いを分析してください
```

### 特許分析サービス（patent_analysis）

特許分析サービスは、特定の出願人の特許出願動向を分析し、以下を生成します：

1. 特許分類別の出願トレンドチャート
2. 出願動向の分析レポート
3. マークダウン形式の総合レポート

**patentDWHとの関係**：
patent_analysisは以下の方法でpatentDWHシステムと連携します：
- patentDWHが提供する特許データベースにアクセスして出願情報を取得します
- patentDWH MCPサービスのネットワークに接続する必要があります
- 統合版では、patentDWHの一部として同一の`docker-compose.consolidated.yml`ファイルで管理できます

**使用方法**：

```bash
# 方法1: 通常方法（patent_analysisを個別に実行）
cd patent_analysis_container
podman-compose run patent-analysis "トヨタ" inpit

# 方法2: 統合方法（patentDWHの一部として実行）
cd patentDWH
podman-compose -f docker-compose.consolidated.yml run patent-analysis "トヨタ" inpit

# 方法3: スクリプトを使用した実行（patentDWHディレクトリから）
./direct_run_analysis.sh "トヨタ" inpit
# または非対話モード
./run_patent_analysis_noninteractive.sh "トヨタ" inpit
```

**パラメータ**：
- `出願人名`: 分析対象の出願人名（例：「トヨタ」）
- `db_type`: データベースタイプ（オプション、デフォルトは "inpit"）
  - 指定可能な値: "inpit", "google_patents_gcp", "google_patents_s3"

**結果**：
分析結果は `output` ディレクトリに保存されます：
- `[出願人名]_classification_trend.png`: 特許分類別トレンドチャート
- `[出願人名]_patent_analysis.md`: マークダウン形式の分析レポート

**注意事項**：
1. patent_analysisを実行する前に、必ずpatentDWHサービスが起動していることを確認してください
2. AWS認証情報は環境変数として設定する必要があります
3. 分析結果は、patent_analysis_containerの`output`ディレクトリまたはpatentDWH内の対応するディレクトリに保存されます

### 特許分析MCPサーバー

特許分析MCPサーバーは、特許出願傾向の分析とレポート生成のためのAPIエンドポイントを提供します。サーバーは http://localhost:8000 でアクセスできます。

**patentDWHとの関係**：
特許分析MCPサーバーは、patentDWHシステムを拡張する形で動作します：
- patentDWHが提供するデータベースに接続してデータを取得します
- patentDWH MCPサーバーと連携して動作しますが、別のサーバーとして稼働します
- AIアシスタント（Claude等）に対してMCPプロトコルを通じて特許分析機能を提供します
- DifyプラットフォームとOpenAPI経由で統合することも可能です

**起動方法**：
```bash
# patent_analysis_containerディレクトリで起動する場合
cd patent_analysis_container
chmod +x start_mcp_service.sh
./start_mcp_service.sh

# または、Podmanコマンドで直接起動する場合
podman-compose -f docker-compose.mcp.yml up -d
```

**主要なエンドポイント**：

- `GET /`: ヘルスチェック
- `GET /docs`: Swagger API ドキュメント
- `GET /openapi.json`: OpenAPI スキーマ（Dify統合用）
- `POST /api/v1/mcp`: MCP互換エンドポイント
- `POST /api/tools/execute`: Dify互換エンドポイント
- `POST /api/analyze`: 特許傾向を分析してJSON結果を返す
- `GET /api/report/{applicant_name}`: マークダウン形式でレポートを取得
- `GET /api/report/{applicant_name}/zip`: ZIPファイル形式でレポートを取得

**使用例**：

```bash
# 特許傾向の分析
curl -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "analyze_patent_trends",
    "tool_input": {
      "applicant_name": "トヨタ"
    }
  }'

# ZIPレポートのダウンロード
curl -X GET http://localhost:8000/api/report/トヨタ/zip -o toyota_report.zip
```

**AIアシスタントでの使用方法**：
特許分析MCPサーバーをAIアシスタントから利用する場合、MCPプロトコルを通じて以下のツールが利用可能です：
- `analyze_patent_trends`: 特定の出願人の特許出願動向を分析します
- `get_report_markdown`: マークダウン形式のレポートを取得します
- `get_report_download_url`: レポートのダウンロードURLを取得します

## テーブル構造

### INPITデータベース
主要テーブル: `inpit_data`

| カラム名 | 説明 | English Field Name |
|--------|------|-------------------|
| id | 主キー | id |
| open_patent_info_number | 開放特許情報番号 | open_patent_info_number |
| title | タイトル | title |
| open_patent_info_registration_date | 開放特許情報登録日 | open_patent_info_registration_date |
| latest_update_date | 最新更新日 | latest_update_date |
| application_number | 出願番号 | application_number |
| application_date | 出願日 | application_date |
| applicant | 出願人 | applicant |
| publication_number | 公開番号 | publication_number |
| registration_number | 登録番号 | registration_number |
| patent_owner | 特許権者 | patent_owner |
| invention_name | 発明の名称 | invention_name |
| technical_field1 | 技術分野1 | technical_field1 |
| technical_field2 | 技術分野2 | technical_field2 |
| technical_field3 | 技術分野3 | technical_field3 |
| function1 | 機能1 | function1 |
| function2 | 機能2 | function2 |
| function3 | 機能3 | function3 |
| applicable_products | 適用製品 | applicable_products |
| purpose | 目的 | purpose |
| effect | 効果 | effect |
| technical_overview | 技術概要 | technical_overview |
| implementation_record_status | 実施実績：有無 | implementation_record_status |
| licensing_record_status | 許諾実績：有無 | licensing_record_status |
| international_patent_classification_ipc | 国際特許分類（IPC） | international_patent_classification_ipc |

### Google Patents データベース
主要テーブル: `publications`

| カラム名 | 説明 |
|--------|------|
| publication_number | 公開番号（主キー） |
| filing_date | 出願日 |
| publication_date | 公開日 |
| application_number | 出願番号 |
| assignee_harmonized | 標準化された権利者名 |
| assignee_original | 元の権利者名 |
| title_ja | タイトル（日本語） |
| title_en | タイトル（英語） |
| abstract_ja | 要約（日本語） |
| abstract_en | 要約（英語） |
| claims | 請求項 |
| ipc_code | 国際特許分類コード |
| family_id | 特許ファミリーID |
| country_code | 国コード |
| kind_code | 種別コード |

## 統合起動方法

patentDWHシステムの各コンポーネントを統合的に起動する方法です。これにより、データベース、MCPサーバー、特許分析サービスを一度に起動できます。

### すべてのコンテナを同時に起動する方法（推奨）

patentDWHとpatent_analysisを含むすべてのコンテナを一括で起動するには以下の手順に従ってください：

```bash
# 1. リポジトリのルートディレクトリに移動
cd patentDWH

# 2. AWS認証情報の設定（必要な場合）
export AWS_ACCESS_KEY_ID="your_aws_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_DEFAULT_REGION="us-east-1"  # 必要に応じて変更（REGIONではなくDEFAULT_REGIONを使用）

# 3. すべてのサービスを一括で起動
./start_all_services.sh
```

これにより、以下のすべてのサービスが起動します：
- **patentdwh-db**: 特許データベースサービス (ポート 5002)
- **patentdwh-mcp-enhanced**: 拡張MCP（LangChain機能付き） (ポート 8080)
- **patent-analysis-mcp**: 特許分析MCPサーバー (ポート 8000)

> **重要な変更点**: Patent Analysis Containerの機能をpatentDWH内に完全に統合しました。これにより、以前はpatent_analysis_containerディレクトリから独立して起動する必要があった特許分析MCPサーバーも、patentDWH内から一元管理できるようになりました。ネットワーク設定の冗長性を解消し、より簡単に全サービスを起動できるようになっています。

### 個別に起動する方法

#### 1. 統合Docker Composeファイルの使用

`docker-compose.consolidated.yml`ファイルには以下のサービスが含まれています：

1. **patentdwh-db**: 特許データベースサービス
2. **patentdwh-mcp-enhanced**: 拡張MCP（LangChain機能付き）
3. **patent-analysis**: 特許分析サービス

#### 2. 統合セットアップスクリプトの実行

```bash
cd patentDWH
./init_consolidated_setup.sh
```

このスクリプトは以下を実行します：
- 必要なコンテナをビルド
- patentdwh-dbとpatentdwh-mcp-enhancedサービスを起動
- サービスの健全性を確認

#### 3. 特許分析MCPサーバーの追加（オプション）

特許分析MCPサーバーも起動したい場合は、以下のコマンドを実行します：

```bash
cd patent_analysis_container
./start_mcp_service.sh
```

### 4. 動作確認

各サービスが正常に起動したことを確認します：

```bash
# データベースサービスの確認
curl http://localhost:5002/health

# MCPサービスの確認
curl http://localhost:8080/health

# 特許分析MCPサービスの確認（起動した場合）
curl http://localhost:8000/
```

### 5. 特許分析の実行

特定の出願人の特許分析を行うには：

```bash
podman-compose -f docker-compose.consolidated.yml run patent-analysis "トヨタ" inpit
```

### 6. すべてのサービスを停止

```bash
./stop_all_services.sh
```

## サービスの起動と停止

patentDWHシステムの起動と停止を簡素化するために、以下のスクリプトが用意されています：

### スクリプト一覧

| スクリプト名 | 用途 | 説明 |
|------------|------|------|
| **start_all_services.sh** | 全サービスの起動 | patentDWHの基本サービスと特許分析MCPサーバーを含む全てのサービスを起動します |
| **stop_all_services.sh** | 全サービスの停止 | 実行中のすべてのコンテナを安全に停止します |
| **init_setup.sh** | 基本セットアップ | 基本的なpatentDWHサービスをセットアップします（従来のsetup.sh） |
| **init_consolidated_setup.sh** | 統合セットアップ | 統合環境のセットアップを行います（従来のsetup_consolidated.sh） |
| **start_mcp_service.sh** | 特許分析サーバー起動 | patent_analysis_container内で特許分析MCPサーバーを起動します |

### 使用例

#### 全サービスの起動

全てのサービスを一度に起動するには：

```bash
cd patentDWH
./start_all_services.sh
```

このスクリプトは以下の処理を行います：
1. 前回のサービスをクリーンアップ
2. patentDWH基本サービス（DB、MCPサーバー）を起動
3. 特許分析MCPサーバーを起動
4. 各サービスの起動確認とヘルスチェック
5. 利用可能なサービスとそのURLを表示

#### 全サービスの停止

全てのサービスを一括で停止するには：

```bash
cd patentDWH
./stop_all_services.sh
```

このスクリプトは以下の処理を行います：
1. 特許分析MCPサーバーを停止
2. patentDWHの基本サービスを停止
3. 他のDocker Composeファイルで起動したサービスも念のため停止
4. 残っているコンテナがあればユーザーに通知し、オプションで強制停止

#### 注意事項

- `start_all_services.sh`と`stop_all_services.sh`は、`patentDWH`ディレクトリ内で実行する必要があります
- `start_mcp_service.sh`は、`patent_analysis_container`ディレクトリ内で実行する必要があります
- AWS認証情報が環境変数として設定されていない場合、`start_all_services.sh`スクリプトは警告を表示しますが、確認後に続行できます

## 詳細ログとトラブルシューティング

patentDWHシステムには、コンテナ起動プロセスの詳細なログ機能が組み込まれています。これらのログは、システムの起動時に発生するエラーを診断するのに役立ちます。

### ログ機能の概要

- **タイムスタンプ付きログ**: すべてのログメッセージには日時情報が付加され、問題が発生した正確なタイミングを特定できます
- **エラーハイライト**: エラーメッセージは赤色で表示され、警告は黄色で表示されます
- **プロセス識別子**: ログには`[patentdwh-db]`や`[patentdwh-mcp]`などのプレフィックスが付き、どのサービスからのメッセージかが明確になります

### トラブルシューティング

#### コンテナが正常に起動しない場合

1. 詳細なログを確認する (ログは自動的にコンテナの起動時に出力されます)：
   ```
   podman-compose -f docker-compose.consolidated.yml logs -f
   ```

2. 特定のコンテナの詳細なログを確認する：
   ```
   podman-compose -f docker-compose.consolidated.yml logs -f patentdwh-db
   podman-compose -f docker-compose.consolidated.yml logs -f patentdwh-mcp-enhanced
   podman-compose -f docker-compose.consolidated.yml logs -f patent-analysis
   ```

3. データベースファイルがダウンロードされていることを確認する：
   ```
   ls -la data/
   du -sh data/*.db
   ```

4. サービスの再起動：
   ```
   podman-compose -f docker-compose.consolidated.yml down
   podman-compose -f docker-compose.consolidated.yml up -d
   ```

#### 特許分析MCPコンテナが "Created" 状態で止まる場合

特許分析MCPコンテナ（patent-analysis-mcp）が "Created" 状態で止まり、実行状態に移行しない場合は、以下の修正スクリプトを実行してください：

1. patent_analysis_containerディレクトリに移動：
   ```
   cd patent_analysis_container
   ```

2. 修正スクリプトを実行：
   ```
   ./fix_mcp_container.sh
   ```

この問題は主に以下の原因で発生します：
- ネットワーク設定の問題 (patentdwh_defaultネットワークへの接続が適切に構成されていない)
- コンテナランタイムの互換性の問題 (podman使用時のDocker Compose設定のサポート)

詳細は `patent_analysis_container/README_CONTAINER_FIX.md` を参照してください。

5. より詳しい情報を得るためにネットワーク設定を確認する：
   ```
   podman network ls
   podman network inspect patentdwh_default
   ```
