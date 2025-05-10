# patentDWH（特許データウェアハウス）

patentDWHは、ユーザーフレンドリーなWebインターフェースとMCPサーバーを通じて、特許データのSQLiteベースのストレージと検索機能を提供する特許データウェアハウスシステムです。

## 概要

このシステムは主に2つのコンポーネントで構成されています：

1. **特許データベース（patentdwh-db）**：特許データを直接クエリするためのWebインターフェースを備えたSQLiteベースのデータベース。
2. **MCPサーバー（patentdwh-mcp）**：ClaudeなどのAIアシスタントが特許データベースとやり取りするためのModel Context Protocol（MCP）サーバー。

このシステムは3つの異なる特許データベースへのアクセスを提供します：

- **INPIT（特許庁）データベース**：日本特許庁からの特許データ。
- **Google Patents GCPデータベース**：BigQueryからのGoogle Patents特許データ。
- **Google Patents S3データベース**：S3に保存されているGoogle Patents特許データ。

## 機能

- **自然言語クエリ**：AWS Bedrock（Claude 3 Sonnet、Titan Embedding）を利用した特許データへの自然言語クエリ機能。詳細は[自然言語クエリドキュメント](./README_NATURAL_LANGUAGE_QUERY.md)を参照。
- **SQLクエリ用WebUI**：すべてのデータベースに対してSQLクエリを実行するための直接的なWebインターフェース。
- **SQLサンプル**：一般的な特許検索用の事前構築されたSQLクエリ例。
- **MCP統合**：AIアシスタント統合のための完全なMCPサーバー実装。
- **マルチデータベースサポート**：同じインターフェースで異なる特許データベースをクエリ。
- **RESTful API**：データベースへのプログラム的アクセスのためのAPIエンドポイント。

## 必要条件

- PodmanまたはDocker
- Podman ComposeまたはDocker Compose
- インターネット接続（初期データダウンロード用）

## インストール

1. リポジトリをクローンします：
   ```
   git clone <repository-url>
   cd patentDWH
   ```

2. セットアップスクリプトを実行します：
   ```
   ./setup.sh
   ```

3. セットアップスクリプトは以下を行います：
   - 必要な依存関係の確認
   - コンテナのビルドと起動
   - サービスが実行されていることの確認
   - 接続情報の表示

## 使用方法

### コマンドラインインターフェース例

#### サービスの起動と停止

```bash
# サービスを起動する
./setup.sh

# サービスの状態を確認する
curl http://localhost:5002/health
curl http://localhost:8080/health

# ログを確認する
podman-compose logs -f
# または
docker compose logs -f

# サービスを停止する
podman-compose down
# または
docker compose down
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

#### MCP APIの使用例

```bash
# 利用可能なデータベース情報の取得
curl http://localhost:8080/api/status

# MCP APIを使用したクエリの実行
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_sql_query",
    "tool_input": {
      "query": "SELECT * FROM inpit_data WHERE title LIKE \"%AI%\" LIMIT 10",
      "db_type": "inpit"
    }
  }' \
  http://localhost:8080/api/v1/mcp
```

### Webインターフェース

- **データベースUI**：http://localhost:5002/ でアクセス可能
- Webインターフェースは3つの主要なセクションを提供します：
  - INPIT SQLサンプル
  - Google Patents GCPサンプル
  - Google Patents S3サンプル
  - フリーSQLクエリツール

### 日本語から英語へのカラム名変換

特許データの日本語カラム名を英語に変換する機能が追加されました。この機能により、CSVファイルから読み込んだデータが、日本語のカラム名ではなく英語のカラム名でSQLiteデータベースに格納されます。主な機能は以下の通りです：

1. **カラム名マッピング定義**: システムは `/app/data/jp_to_en_mapping.json` ファイルを使用して、日本語のカラム名を英語のカラム名にマッピングします。
2. **透過的な変換**: CSVファイルからデータが読み込まれる際に、日本語のカラム名が自動的に英語に変換されます。
3. **マッピング履歴**: 変換に使用された実際のマッピングは `/app/data/jp_en_used_mapping.json` ファイルに保存されます。
4. **柔軟なフォールバック**: マッピングファイルが存在しない場合や、特定の日本語カラム名にマッピングが定義されていない場合、システムは従来通りSQL互換のカラム名に変換します。

#### カスタムマッピングの定義方法

独自の日本語から英語へのマッピングを定義するには：

1. `/app/data/jp_to_en_mapping.json` ファイルを編集します。
2. 次の形式でJSONオブジェクトを定義します：
   ```json
   {
     "日本語カラム名1": "english_column_name1",
     "日本語カラム名2": "english_column_name2",
     ...
   }
   ```
3. システムを再起動するか、CSVデータを再ロードして変更を適用します。

### MCPサーバー

MCPサーバーはhttp://localhost:8080/ で動作し、以下のツールを提供します：

1. **patent_sql_query**：任意の特許データベースに対してSQLクエリを実行します。（注意：カラム名は英語名を使用して検索します）
   ```json
   {
     "query": "SELECT * FROM inpit_data LIMIT 5",
     "db_type": "inpit"
   }
   ```
   結果例:
   ```json
   {
     "success": true,
     "columns": ["id", "application_number", "application_date", "publication_number", "publication_date", "registration_number", "registration_date", "applicant_name", "inventor_name", "title", "ipc_code", "application_status", "summary"],
     "results": [
       [1, "JP2022123456", "2022-01-15", "JP2023987654A", "2023-07-20", "特許第6789012号", "2023-12-05", "テック株式会社", "発明太郎", "AI特許分析システム", "G06N 20/00", "登録済み", "AIを用いて特許を分析するシステム"]
     ],
     "record_count": 1
   }
   ```

2. **patent_nl_query**：自然言語での質問を特許データベースに対して実行します。詳細は[自然言語クエリドキュメント](./README_NATURAL_LANGUAGE_QUERY.md)と[自然言語クエリ例](./NATURAL_LANGUAGE_QUERY_EXAMPLES.md)を参照。
   ```json
   {
     "query": "ソニーが出願した人工知能関連の特許を教えてください",
     "db_type": "google_patents_gcp"
   }
   ```
   結果例:
   ```json
   {
     "success": true,
     "query": "ソニーが出願した人工知能関連の特許を教えてください",
     "sql": "SELECT publication_number, title_ja, publication_date, assignee_harmonized FROM publications WHERE assignee_harmonized LIKE '%Sony%' AND (title_ja LIKE '%人工知能%' OR title_ja LIKE '%AI%' OR title_ja LIKE '%機械学習%') ORDER BY publication_date DESC LIMIT 20;",
     "db_type": "google_patents_gcp",
     "sql_result": {
       "success": true,
       "columns": ["publication_number", "title_ja", "publication_date", "assignee_harmonized"],
       "results": [
         // 結果データ
       ],
       "record_count": 15
     },
     "response": "ソニー（Sony）が出願した人工知能関連の特許として、データベースには15件の特許が見つかりました。これらの特許は公開日の新しい順に表示されています。..."
   }
   ```
   
3. **check_aws_credentials**：AWS Bedrockサービスの認証情報が正しく設定されているか確認します。
   ```json
   {}
   ```
   結果例:
   ```json
   {
     "success": true,
     "message": "AWS credentials are correctly configured for Bedrock services",
     "aws_region": "us-east-1"
   }
   ```

4. **get_database_info**：利用可能な特許データベースに関する情報を取得します。
   ```json
   {
     "db_type": null
   }
   ```
   結果例:
   ```json
   {
     "success": true,
     "database_info": {
       "inpit": { "record_count": 10000 },
       "google_patents_gcp": { "record_count": 5000 },
       "google_patents_s3": { "record_count": 8000 }
     }
   }
   ```

5. **get_sql_examples**：特定のデータベースタイプのSQLクエリ例を取得します。
   ```json
   {
     "db_type": "inpit"
   }
   ```
   結果例:
   ```json
   {
     "success": true,
     "db_type": "inpit",
     "examples": {
       "basic": "SELECT * FROM inpit_data LIMIT 10;",
       "applicant": "SELECT * FROM inpit_data WHERE applicant_name LIKE '%テック%' ORDER BY application_date DESC LIMIT 20;",
       "date": "SELECT * FROM inpit_data WHERE application_date BETWEEN '2022-01-01' AND '2023-12-31' ORDER BY application_date DESC LIMIT 20;",
       "count": "SELECT strftime('%Y', application_date) as year, COUNT(*) as application_count FROM inpit_data GROUP BY strftime('%Y', application_date) ORDER BY year DESC;"
     }
   }
   ```

### 自然言語クエリ

patentDWHシステムの自然言語クエリ機能を使用すると、複雑なSQLクエリを書かなくても、日本語や英語で直接特許データベースに質問することができます。この機能は、AWS Bedrockの Claude 3 Haikuモデルを使用してユーザーの質問をSQLに変換し、結果を自然言語で回答します。

**主な特徴**：

- 日本語と英語での質問をサポート
- 3種類のデータベース（INPIT、Google Patents GCP、Google Patents S3）に対応
- 特許の検索、統計分析、トレンド分析などの多様なクエリタイプをサポート
- 結果は分かりやすい自然言語で提供

**利用可能な質問例**：

詳細な質問例については、[自然言語クエリ例](./NATURAL_LANGUAGE_QUERY_EXAMPLES.md)を参照してください。以下はその一部です：

```
テック株式会社が出願した特許は何件ありますか？
ソニーが出願した人工知能関連の特許を教えてください
IPCコードG06Fに属する特許の国別出願数を比較してください
自動運転技術において、トヨタとテスラの特許ポートフォリオの違いを分析してください
```

技術的な詳細については、[自然言語クエリドキュメント](./README_NATURAL_LANGUAGE_QUERY.md)を参照してください。

ClaudeやMCPをサポートする他のAIアシスタントで使用するための設定：

```json
{
  "serverName": "patentDWH",
  "description": "Patent DWH MCPサーバー",
  "url": "http://localhost:8080/api/v1/mcp"
}
```

## テーブル構造

### INPITデータベース
主要テーブル: `inpit_data`

| カラム名 | 説明 |
|--------|------|
| id | 主キー |
| application_number | 出願番号 |
| application_date | 出願日 |
| publication_number | 公開番号 |
| publication_date | 公開日 |
| registration_number | 登録番号 |
| registration_date | 登録日 |
| applicant_name | 出願人名 |
| inventor_name | 発明者名 |
| title | 発明の名称 |
| ipc_code | 国際特許分類コード |
| application_status | 出願状況 |
| summary | 要約 |

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

その他のテーブル: `patent_families` (特許ファミリー情報)

| カラム名 | 説明 |
|--------|------|
| id | 主キー |
| family_id | 特許ファミリーID |
| application_number | 出願番号 |
| publication_number | 公開番号 |
| country_code | 国コード |

## データソース

システムは以下からデータをダウンロードして処理します：

1. INPIT CSVデータ：S3バケット `ndi-3supervision` からソース取得
2. Google Patents GCPデータ：BigQueryからソース取得
3. Google Patents S3データ：S3バケット `ndi-3supervision` からソース取得

## ディレクトリ構造

```
patentDWH/
├── app/                    # MCPサーバーファイル
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   └── server.py
├── data/                   # データストレージディレクトリ
│   └── db/                 # SQLiteデータベースファイル
├── db/                     # データベースサーバーファイル
│   ├── Dockerfile
│   ├── app.py
│   ├── download_data.py
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── static/
│   └── templates/
├── podman-compose.yml      # コンテナオーケストレーション
├── setup.sh                # セットアップスクリプト
└── README.md               # このファイル
```

## 詳細ログとエラー診断

patentDWHシステムには、コンテナ起動プロセスの詳細なログ機能が組み込まれています。これらのログは、システムの起動時に発生するエラーを診断するのに役立ちます。

### ログ機能の概要

- **タイムスタンプ付きログ**: すべてのログメッセージには日時情報が付加され、問題が発生した正確なタイミングを特定できます
- **エラーハイライト**: エラーメッセージは赤色で表示され、警告は黄色で表示されます
- **プロセス識別子**: ログには`[patentdwh-db]`や`[patentdwh-mcp]`などのプレフィックスが付き、どのサービスからのメッセージかが明確になります
- **詳細な環境情報**: システム情報、AWS認証情報の状態、ポート使用状況などが起動時に確認されます
- **データベースファイル検証**: 起動時に各データベースファイルの存在と大きさがチェックされます
- **コネクティビティチェック**: MCPサービスはデータベースサービスとの接続を自動的にテストし、問題が発生した場合は詳細を報告します

### トラブルシューティング

サービスが正常に起動しない場合：

1. 詳細なログを確認する (ログは自動的にコンテナの起動時に出力されます)：
   ```
   podman-compose logs -f
   ```

2. 特定のコンテナの詳細なログを確認する：
   ```
   podman-compose logs -f patentdwh-db
   podman-compose logs -f patentdwh-mcp
   ```

3. データベースファイルがダウンロードされていることを確認する：
   ```
   ls -la data/
   du -sh data/*.db
   ```

4. データベースサービスのヘルスチェックを実行する：
   ```
   curl http://localhost:5002/health
   curl http://localhost:8080/health
   ```

5. サービスを再起動する：
   ```
   podman-compose down
   podman-compose up -d
   ```

6. 特定のサービスのみを再起動する：
   ```
   podman-compose restart patentdwh-db
   podman-compose restart patentdwh-mcp
   ```

7. データのクリーンアップと再ダウンロード：
   ```
   rm -rf data/*.db
   podman-compose down
   podman-compose up -d
   ```

8. コンテナ内でデバッグを実行：
   ```
   podman-compose exec patentdwh-db /bin/bash
   # コンテナ内で以下を実行
   cd /app
   ls -la data/
   sqlite3 data/inpit.db ".tables"
   sqlite3 data/inpit.db "SELECT * FROM inpit_data LIMIT 5"
   ```

## ライセンス

[ライセンス情報を含める]
