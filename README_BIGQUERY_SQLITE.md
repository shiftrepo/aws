# BigQueryとSQLiteを使用した特許データ分析システム

このプロジェクトでは、Google BigQueryから特許データを取得し、SQLiteデータベースに格納して、自然言語クエリによる検索を可能にするシステムを構築しています。

## 目次

- [概要](#概要)
- [システム要件](#システム要件)
- [セットアップ](#セットアップ)
  - [Google Cloud認証情報の設定](#google-cloud認証情報の設定)
  - [AWS認証情報の設定](#aws認証情報の設定)
- [使用方法](#使用方法)
  - [BigQuery接続テスト](#bigquery接続テスト)
  - [特許データのインポート](#特許データのインポート)
  - [自然言語クエリの実行](#自然言語クエリの実行)
- [スクリプト説明](#スクリプト説明)
- [トラブルシューティング](#トラブルシューティング)

## 概要

このシステムでは以下の機能を提供します：

1. Google BigQuery `patents-public-data.patents.publications` データセットからの特許データ取得
2. 取得したデータをローカルのSQLiteデータベースに格納
3. 格納されたデータに対する自然言語クエリの実行
4. SQLite機能のデモンストレーション

## システム要件

- Python 3.7以上
- 必要なPythonパッケージ:
  - google-cloud-bigquery
  - google-auth
  - boto3 (S3からの認証情報取得を使用する場合)
  - sqlite3 (Pythonの標準ライブラリ)

## セットアップ

### Google Cloud認証情報の設定

BigQueryにアクセスするには、Google Cloud認証情報が必要です。このプロジェクトでは以下の方法でコンテナ内からBigQueryにアクセスします：

#### コンテナ使用時: S3バケットから認証情報を自動取得

コンテナベースの実行では、Google Cloud認証情報ファイルを指定のAWS S3バケットから自動的に取得します。この方法を使用するには以下のAWS認証情報を設定する必要があります：

```bash
# AWS認証情報を設定
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=ap-northeast-1  # または適切なリージョン
```

デフォルトでは、以下のS3パスから認証情報を取得します：
- バケット: `ndi-3supervision`
- キー: `MIT/GCPServiceKey/tosapi-bf0ac4918370.json`

環境変数を使って異なるS3パスを指定することもできます：

```bash
export GCP_CREDENTIALS_S3_BUCKET=your_bucket_name
export GCP_CREDENTIALS_S3_KEY=path/to/your/credentials.json
```

#### 直接実行時: ローカルの認証情報ファイルを使用

コンテナを使わずにスクリプトを直接実行する場合は、従来通り環境変数でローカルの認証情報ファイルを指定できます：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

### 依存関係のインストール

必要なパッケージをインストールします：

```bash
pip install google-cloud-bigquery google-auth boto3
```

## 使用方法

### BigQuery接続テスト

BigQueryへの接続をテストするには、以下のスクリプトを実行します：

```bash
./test_run_bigquery.sh
```

または直接Pythonスクリプトを実行します：

```bash
python test_bigquery_connection.py
```

### 特許データのインポート

BigQueryから特許データを取得してSQLiteデータベースに格納するには以下を実行します：

#### 方法1: 提供されたスクリプトを使用

```bash
./test_import_patents.sh
```

#### 方法2: カスタムスクリプトを使用

```bash
python bigquery_sqlite_test.py
```

#### 方法3: 自然言語クエリデモスクリプトでインポート

```bash
python nl_query_demo.py --import_data --limit 50
```

パラメータ:
- `--import_data`: BigQueryからデータをインポートします
- `--limit <数値>`: インポートする特許データの件数を指定します（デフォルト: 20）
- `--db <パス>`: SQLiteデータベースのパスを指定します

### 自然言語クエリの実行

SQLiteに格納された特許データに対して自然言語クエリを実行するには：

#### インタラクティブモード

```bash
python nl_query_demo.py
```

プロンプトが表示されたら、自然言語クエリを入力できます。例:
- 「最新の特許を5件表示」
- 「電気自動車に関する特許を検索」
- 「カメラ技術についての特許」

#### コマンドラインでの単一クエリ実行

```bash
python nl_query_demo.py --query "半導体に関する特許を表示"
```

#### データベースの情報表示

```bash
python nl_query_demo.py --show_info
```

## スクリプト説明

本プロジェクトには以下のスクリプトが含まれています：

1. **bigquery_sqlite_test.py**: BigQueryへの接続と特許データの取得、SQLiteへの格納を行うスクリプト
2. **pure_sqlite_demo.py**: SQLiteの基本機能を示すシンプルなデモスクリプト
3. **sqlite_programmatic_demo.py**: SQLiteのプログラム的な操作を示すデモスクリプト
4. **nl_query_demo.py**: 自然言語クエリをSQLに変換して特許データを検索するスクリプト

## トラブルシューティング

### BigQuery接続エラー

1. 認証情報が正しく設定されているか確認してください
2. 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` が正しいファイルパスを指しているか確認してください
3. サービスアカウントに BigQuery 読み取り権限があるか確認してください

### SQLiteエラー

1. ディスク空き容量が十分あるか確認してください
2. ディレクトリに書き込み権限があるか確認してください

### インポートエラー

1. Pythonのパスが正しく設定されているか確認してください
2. 必要なモジュールがインストールされているか確認してください
