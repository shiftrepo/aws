# Inpit SQLite MCP Server

このサーバーは、特許情報を検索・分析するための MCP (Model Context Protocol) インターフェースを提供します。

## 主な特徴

- 特許情報の検索（出願番号、出願人など）
- 出願人の特許分析（サマリー、視覚的レポート、審査状況分析など）
- SQLクエリによる柔軟なデータ検索
- 日本語を含むURLの直接サポート（URLエンコーディング不要）
- Google Patents Public Dataからの日本国特許データの取得
- ファミリー出願（関連出願）の検索と関係性分析
- 自然言語による特許検索クエリ

## URL エンコーディング機能について

このバージョンでは、URLに日本語などの非ASCII文字や空白を含める場合、明示的なURLエンコーディングが不要になりました。また、POSTリクエストでの`--data-urlencode`を使った日本語パラメータ送信もサポートしています。

### GET リクエストの例

以下のように直接日本語を含むURLでアクセスできます：

```
curl http://localhost:8000/applicant/テック株式会社
```

スペースを含む名前の場合：

```
curl 'http://localhost:8000/applicant/テック 株式会社'
```

### POST リクエストの例

日本語とスペースを含むデータを`--data-urlencode`オプションで安全に送信できます：

```
curl -X POST "http://localhost:8000/applicant" --data-urlencode "name=テック 株式会社"
```

フォームデータでの送信も可能です：

```
curl -X POST -F "name=テック 株式会社" http://localhost:8000/applicant
```

### 対応しているエンドポイント

以下の全てのエンドポイントは日本語を含むパスを直接サポートします：

- `GET /applicant/{applicant_name}`
- `GET /application/{application_number}`
- `GET /applicant-summary/{applicant_name}`
- `GET /visual-report/{applicant_name}`
- `GET /assessment/{applicant_name}`
- `GET /technical/{applicant_name}`
- `GET /compare/{applicant_name}`
- `GET /pdf-report/{applicant_name}`
- `POST /applicant` (フォームデータの"name"パラメータで出願人を指定)

## コンテナを使った実行方法

このプロジェクトはコンテナ（Docker/Podman）を使って簡単に実行できます。コンテナベースの実行では、環境構築の手間を省き、異なるプラットフォーム間での一貫した動作を保証します。

### 前提条件

コンテナを使用する場合は、以下のソフトウェアがインストールされている必要があります：

- Docker または Podman
- Docker Compose または Podman Compose

### 環境変数の設定

コンテナを起動する前に、必要な環境変数を設定する必要があります：

```bash
# AWS認証情報（S3からのGoogle Cloud認証情報取得に必要）
export AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID"
export AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットアクセスキー"
export AWS_DEFAULT_REGION="ap-northeast-1"  # または必要なリージョン

# オプション：S3上のGoogle Cloud認証情報のカスタムパス（デフォルトから変更する場合のみ）
export GCP_CREDENTIALS_S3_BUCKET="あなたのバケット名"  # デフォルト: ndi-3supervision
export GCP_CREDENTIALS_S3_KEY="認証情報JSONファイルのパス"  # デフォルト: MIT/GCPServiceKey/tosapi-bf0ac4918370.json
```

### Podmanでの起動手順

Podmanを使用してコンテナを起動する詳細な手順：

```bash
# 1. プロジェクトディレクトリに移動
cd /root/aws.git/inpit-sqlite-mcp/

# 2. AWS認証情報が設定されていることを確認
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION

# 3. Podmanでコンテナをビルドして起動（バックグラウンド実行）
podman-compose -f podman-compose.yml up -d

# 4. コンテナの状態確認
podman ps

# 5. コンテナのログを確認（問題が発生した場合）
podman logs inpit-sqlite-mcp
```

コマンド一行で環境変数を設定して起動する場合：

```bash
AWS_ACCESS_KEY_ID="あなたのアクセスキーID" \
AWS_SECRET_ACCESS_KEY="あなたのシークレットキー" \
AWS_DEFAULT_REGION="ap-northeast-1" \
podman-compose -f podman-compose.yml up -d
```

### Dockerでの起動手順

Docker Composeを使用してコンテナを起動する詳細な手順：

```bash
# 1. プロジェクトディレクトリに移動
cd /root/aws.git/inpit-sqlite-mcp/

# 2. AWS認証情報が設定されていることを確認
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION

# 3. Docker Composeでコンテナをビルドして起動（バックグラウンド実行）
docker-compose up -d

# 4. コンテナの状態確認
docker ps

# 5. コンテナのログを確認（問題が発生した場合）
docker logs inpit-sqlite-mcp
```

コマンド一行で環境変数を設定して起動する場合：

```bash
AWS_ACCESS_KEY_ID="あなたのアクセスキーID" \
AWS_SECRET_ACCESS_KEY="あなたのシークレットキー" \
AWS_DEFAULT_REGION="ap-northeast-1" \
docker-compose up -d
```

### コンテナの管理

構築したコンテナの管理コマンド：

```bash
# Podmanの場合：
# コンテナの停止
podman-compose -f podman-compose.yml stop

# コンテナの再起動
podman-compose -f podman-compose.yml restart

# コンテナの停止と削除
podman-compose -f podman-compose.yml down

# コンテナのログを表示（リアルタイムで追跡）
podman logs -f inpit-sqlite-mcp

# Dockerの場合：
# コンテナの停止
docker-compose stop

# コンテナの再起動
docker-compose restart

# コンテナの停止と削除
docker-compose down

# コンテナのログを表示（リアルタイムで追跡）
docker logs -f inpit-sqlite-mcp
```

### Google Cloud認証情報の流れ

コンテナ内でのGoogle Cloud認証情報の取得フローは以下の通りです：

1. コンテナの起動時に設定されたAWS認証情報を使用
2. 指定されたS3バケット（デフォルト: ndi-3supervision）から認証情報JSONファイルを取得
3. 取得したJSONファイルを使用してGoogle Cloud BigQueryクライアントを初期化
4. 一時ファイルとして保存された認証情報は使用後に自動削除

このフローにより、コンテナ内で安全にBigQueryへの接続を確立します。S3からの取得に失敗した場合は、環境変数 `GOOGLE_APPLICATION_CREDENTIALS` を使用したフォールバックメカニズムも実装されています。

## Google Patents Public Data 機能

このバージョンでは、Google Patents Public Data のデータを利用する機能が追加されました。認証はコンテナ内からS3バケット上のGoogle Cloud Platformの資格情報ファイルを使用して行われます。

### AWS認証情報とGoogle Cloud認証の設定

Google Patents Public DataにアクセスするためのGoogle Cloud Platform認証情報は、指定したS3バケットから自動的に取得されます。そのため、以下のAWS認証情報環境変数が必要です：

```bash
# AWS認証情報を設定
export AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID"
export AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットアクセスキー"
export AWS_DEFAULT_REGION="ap-northeast-1"  # または必要なリージョン
```

デフォルトでは、次のS3パスから認証情報が取得されます：
- バケット: `ndi-3supervision`
- キー: `MIT/GCPServiceKey/tosapi-bf0ac4918370.json`

必要に応じて別のS3パスを指定することもできます：

```bash
# 環境変数で別のS3パスを指定する場合
export GCP_CREDENTIALS_S3_BUCKET="あなたのバケット名"
export GCP_CREDENTIALS_S3_KEY="認証情報JSONファイルのパス"
```

### BigQuery接続の確認方法

提供されているテストスクリプトを使用して、環境変数から認証情報を取得し、BigQueryに正しく接続できるか確認できます。

```bash
# テストスクリプトを実行
cd /root/aws.git/inpit-sqlite-mcp/app
./test_run_bigquery.sh
```

テスト結果に基づいて、設定方法や問題解決のヒントが表示されます。接続が成功した場合は、同じ環境変数を使用してDocker Composeを起動できます。

```bash
# 成功した環境変数設定を使用してDockerコンテナを起動
cd /root/aws.git/inpit-sqlite-mcp
docker-compose up -d
```

### 日本国特許データの取得

```bash
# 日本国特許データ（約10,000件）を取得
curl -X POST -H "Content-Type: application/json" -d '{"limit": 10000}' http://localhost:8000/patents/import
```

### 自然言語クエリによる特許検索

```bash
# 自然言語による特許検索（GET）
curl "http://localhost:8000/patents/query/Show%20me%20patents%20about%20electric%20vehicles%20from%20Toyota"

# 自然言語による特許検索（POST）
curl -X POST -H "Content-Type: application/json" -d '{"query": "Show me patents about electric vehicles from Toyota"}' http://localhost:8000/patents/query
```

### 特許ファミリーの検索

```bash
# 指定した出願番号のファミリーメンバー（関連出願）を取得
curl http://localhost:8000/patents/family/JP2020123456
```

### データベースのステータス確認

```bash
# Google Patentsデータベースの状態を確認
curl http://localhost:8000/patents/status
```

## API エンドポイント

### 特許検索

- `GET /applicant/{applicant_name}` - 出願人名での特許検索
  ```bash
  # 例: 特定の出願人の特許を検索
  curl http://localhost:8000/applicant/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE

  # スペースを含む出願人名での検索
  curl 'http://localhost:8000/applicant/テック 株式会社'
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%20%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
  ```

- `POST /applicant` - 出願人名での特許検索（フォームデータ使用）
  ```bash
  # 例: POSTリクエストで出願人名を指定して検索（自動URLエンコードあり）
  curl -X POST "http://localhost:8000/applicant" --data-urlencode "name=テック 株式会社"

  # 同上（手動でURLエンコード済み）
  curl -X POST "http://localhost:8000/applicant" --data "name=%E3%83%86%E3%83%83%E3%82%AF%20%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"

  # フォームデータとして送信する例
  curl -X POST -F "name=テック 株式会社" http://localhost:8000/applicant
  ```

- `GET /application/{application_number}` - 出願番号による特許検索
  ```bash
  # 例: 特定の出願番号で検索
  curl http://localhost:8000/application/特願2022-123456
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/application/%E7%89%B9%E9%A1%982022-123456
  ```

### 特許分析

- `GET /applicant-summary/{applicant_name}` - 出願人のサマリー情報
  ```bash
  # 例: 出願人のサマリー情報を取得
  curl http://localhost:8000/applicant-summary/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/applicant-summary/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
  ```

- `GET /visual-report/{applicant_name}` - 視覚的レポートの生成
  ```bash
  # 例: 出願人の視覚的レポートを生成
  curl http://localhost:8000/visual-report/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/visual-report/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
  ```

- `GET /assessment/{applicant_name}` - 審査状況の分析
  ```bash
  # 例: 出願人の審査状況分析
  curl http://localhost:8000/assessment/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/assessment/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
  ```

- `GET /technical/{applicant_name}` - 技術分野の分析
  ```bash
  # 例: 出願人の技術分野分析
  curl http://localhost:8000/technical/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/technical/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
  ```

- `GET /compare/{applicant_name}` - 競合他社との比較
  ```bash
  # 例: 出願人と競合他社を比較（デフォルトでは上位3社と比較）
  curl http://localhost:8000/compare/テック株式会社
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/compare/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE

  # 比較する競合他社の数を指定
  curl http://localhost:8000/compare/テック株式会社?num_competitors=5
  
  # 同上（URLエンコード済み）
  curl http://localhost:8000/compare/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE?num_competitors=5
  ```

### SQLクエリ

- `POST /sql` - SQLクエリの実行（フォーム形式）
  ```bash
  # 例: SQLクエリを実行
  curl -X POST -d "query=SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック%' LIMIT 5" http://localhost:8000/sql

  # 日本語を含むSQLクエリをURLエンコード（自動）
  curl -X POST "http://localhost:8000/sql" --data-urlencode "query=SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック 株式会社%' LIMIT 5"
  
  # 日本語を含むSQLクエリ（手動URLエンコード）
  curl -X POST "http://localhost:8000/sql" --data "query=SELECT+*+FROM+inpit_data+WHERE+%E5%87%BA%E9%A1%98%E4%BA%BA+LIKE+%27%25%E3%83%86%E3%83%83%E3%82%AF+%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE%25%27+LIMIT+5"
  ```

- `POST /sql/json` - SQLクエリの実行（JSON形式）
  ```bash
  # 例: JSONでSQLクエリを実行
  curl -X POST -H "Content-Type: application/json" -d '{"query": "SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック%' LIMIT 5"}' http://localhost:8000/sql/json
  
  # 同上（URLエンコード済みJSON）
  curl -X POST -H "Content-Type: application/json" -d '{"query": "SELECT * FROM inpit_data WHERE \u51fa\u9858\u4eba LIKE \"%\u30c6\u30c3\u30af%\" LIMIT 5"}' http://localhost:8000/sql/json
  ```

### システム情報

- `GET /status` - データベースの状態確認
  ```bash
  # 例: データベースの状態を確認
  curl http://localhost:8000/status
  ```

- `GET /tools` - 利用可能なツール一覧
  ```bash
  # 例: 利用可能なツールを一覧表示
  curl http://localhost:8000/tools
  ```

- `GET /resources` - 利用可能なリソース一覧
  ```bash
  # 例: 利用可能なリソースを一覧表示
  curl http://localhost:8000/resources
  ```

## 技術情報

このサーバーは以下の技術を使用しています：

- FastAPI - 高速なWebフレームワーク
- Model Context Protocol (MCP) - AI モデルとの連携インターフェース
- SQLite - 軽量データベース
- Google BigQuery - 特許データのソース
- AWS S3 - 認証情報の保存
- Docker/Podman - コンテナ化

## ライセンス

Apache License 2.0
