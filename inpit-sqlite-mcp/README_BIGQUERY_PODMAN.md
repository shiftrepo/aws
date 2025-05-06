# inpit-sqlite-mcp でのBigQuery統合

このREADMEファイルでは、podmanを使用してinpit-sqlite-mcpコンテナを起動し、BigQueryから特許データを自動的に取得する方法について説明します。

## 特徴

- コンテナ起動時にBigQueryからJP特許データを自動的に取得
- S3から認証情報を自動的に取得し、BigQueryに接続
- データの永続化により、再起動時に再インポートが不要
- エラー処理と再試行メカニズム

## 前提条件

- podmanがインストールされていること
- podman-composeがインストールされていること
- AWS認証情報が環境変数に設定されていること
- GCPサービスアカウントの認証情報がS3に保存されていること

## 使用方法

### 1. AWSの認証情報を設定する

```bash
export AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID"
export AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットアクセスキー"
export AWS_DEFAULT_REGION="ap-northeast-1"
```

### 2. コンテナを起動する

```bash
cd /root/aws.git/inpit-sqlite-mcp/
podman-compose -f podman-compose.yml up -d
```

または環境変数をインラインで指定:

```bash
AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID" \
AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットキー" \
AWS_DEFAULT_REGION="ap-northeast-1" \
podman-compose -f podman-compose.yml up -d
```

### 3. ログを確認する

```bash
podman logs -f inpit-sqlite-mcp
```

## データの保存場所

特許データは以下の場所に保存されます:

- inpit-sqlite-mcp/data/google_patents.db

このディレクトリはコンテナに永続化されます。

## カスタマイズ

### S3からの認証情報の取得先を変更する

以下の環境変数を変更することで、S3からの認証情報の取得先をカスタマイズできます:

```bash
export GCP_CREDENTIALS_S3_BUCKET="あなたのバケット名"
export GCP_CREDENTIALS_S3_KEY="認証情報JSONファイルのパス"
```

これらを podman-compose.yml に追加することもできます。

### BigQueryから取得する特許数を変更する

entrypoint.sh内の以下の部分を変更すると、取得する特許の数を変更できます:

```bash
python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
```

`limit=10000` の値を変更して、取得する特許の数を調整してください。

## トラブルシューティング

### S3から認証情報が取得できない場合

AWS認証情報が正しく設定されているか確認してください。また、S3バケットと認証情報ファイルのパスが正しいか確認してください。

### BigQueryからデータが取得できない場合

GCPサービスアカウントの認証情報が有効で、BigQueryへのアクセス権があるか確認してください。また、BigQueryのAPIが利用可能であることを確認してください。
