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
  -d '{"database": "inpit", "query": "SELECT * FROM patents LIMIT 5"}' \
  http://localhost:8080/api/v1/query

# Google Patents GCPデータベースに対するクエリ例
curl -X POST -H "Content-Type: application/json" \
  -d '{"database": "google_patents_gcp", "query": "SELECT publication_number, title_ja FROM patents LIMIT 5"}' \
  http://localhost:8080/api/v1/query

# Google Patents S3データベースに対するクエリ例
curl -X POST -H "Content-Type: application/json" \
  -d '{"database": "google_patents_s3", "query": "SELECT id, title FROM patents LIMIT 5"}' \
  http://localhost:8080/api/v1/query
```

#### MCP APIの使用例

```bash
# 利用可能なデータベース情報の取得
curl http://localhost:8080/api/v1/databases

# SQLクエリ例の取得
curl http://localhost:8080/api/v1/examples/inpit
curl http://localhost:8080/api/v1/examples/google_patents_gcp
curl http://localhost:8080/api/v1/examples/google_patents_s3

# MCP APIを使用したクエリの実行
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_sql_query",
    "tool_input": {
      "database": "inpit",
      "query": "SELECT * FROM patents WHERE title LIKE '%AI%' LIMIT 10"
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

### MCPサーバー

MCPサーバーはhttp://localhost:8080/ で動作し、以下のツールを提供します：

1. **patent_sql_query**：任意の特許データベースに対してSQLクエリを実行します。
2. **get_database_info**：利用可能な特許データベースに関する情報を取得します。
3. **get_sql_examples**：特定のデータベースタイプのSQLクエリ例を取得します。

ClaudeやMCPをサポートする他のAIアシスタントで使用するための設定：

```json
{
  "serverName": "patentDWH",
  "description": "Patent DWH MCPサーバー",
  "url": "http://localhost:8080/api/v1/mcp"
}
```

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
   ```

## ライセンス

[ライセンス情報を含める]
