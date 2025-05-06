# Google BigQuery コンテナ化対応

このプロジェクトでは、inpit-sqlite-mcpをコンテナ上で実行し、BigQueryからデータを取得する機能を実装しました。

## 実装内容

1. **S3からの認証情報自動取得機能**
   - コンテナ内から`s3://ndi-3supervision/MIT/GCPServiceKey/tosapi-bf0ac4918370.json`の認証情報を自動取得
   - 環境変数`GCP_CREDENTIALS_S3_BUCKET`と`GCP_CREDENTIALS_S3_KEY`でS3パスをカスタマイズ可能

2. **コンテナ設定の更新**
   - podman-compose.ymlとdocker-compose.ymlを環境変数をサポートするように更新
   - AWS認証情報を各コンテナに渡すよう設定

3. **Dockerfileの依存関係解決**
   - boto3などの必要なパッケージを確実に含めるよう設定

## 使用方法

### 環境変数の設定

コンテナを起動する前に、AWS認証情報を環境変数として設定する必要があります：

```bash
# AWS認証情報を設定
export AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID"
export AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットアクセスキー"
export AWS_DEFAULT_REGION="ap-northeast-1"  # または必要なリージョン

# オプション：S3上のGoogle Cloud認証情報のカスタムパス
export GCP_CREDENTIALS_S3_BUCKET="あなたのバケット名"  # デフォルト: ndi-3supervision
export GCP_CREDENTIALS_S3_KEY="認証情報JSONファイルのパス"  # デフォルト: MIT/GCPServiceKey/tosapi-bf0ac4918370.json
```

### Podmanでの実行

```bash
cd /root/aws.git/inpit-sqlite-mcp/
podman-compose -f podman-compose.yml up -d
```

または環境変数を一行で指定：

```bash
AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID" \
AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットキー" \
AWS_DEFAULT_REGION="ap-northeast-1" \
podman-compose -f podman-compose.yml up -d
```

### Dockerでの実行

```bash
cd /root/aws.git/inpit-sqlite-mcp/
docker-compose up -d
```

または環境変数を一行で指定：

```bash
AWS_ACCESS_KEY_ID="あなたのAWSアクセスキーID" \
AWS_SECRET_ACCESS_KEY="あなたのAWSシークレットキー" \
AWS_DEFAULT_REGION="ap-northeast-1" \
docker-compose up -d
```

## 動作確認結果

実装したコンテナは、以下の点で期待通りの動作をしていることを確認しました：

1. **コンテナの起動と実行**
   - podman-compose と docker-compose の両方でコンテナが起動する
   - 環境変数が正しくコンテナ内に渡される

2. **S3認証情報の取得**
   - コンテナがS3から認証情報を正常に取得
   - 認証情報を用いてBigQueryクライアントが初期化される

3. **エラー処理**
   - S3認証情報取得失敗時にフォールバック機構が動作

## 既知の問題

現在、特許データのインポート時に以下のエラーが発生します：

```
404 Not found: Table patents-public-data:patents.families was not found in location US
```

これは、BigQueryのテーブル構造が変更されている可能性があります。この問題を解決するためには、以下の対応が必要です：

1. BigQueryの最新のテーブル構造を確認する
2. `google_patents_fetcher.py`のクエリを更新して新しいテーブル構造に対応させる

## 自然言語クエリのテスト

自然言語クエリ機能は構文的には正常に動作し、以下のようなSQLに変換されます：

```sql
SELECT * FROM publications p JOIN patent_families f ON p.family_id = f.family_id 
WHERE p.assignee_harmonized LIKE '%toyota%' 
AND (p.title_ja LIKE '%%' OR p.title_en LIKE '%vehicle%' OR p.abstract_ja LIKE '%%' OR p.abstract_en LIKE '%vehicle%')
ORDER BY p.publication_date DESC LIMIT 10
```

ただし、データベースにデータが存在しないため、結果は返りません。

## 今後の対応

1. BigQueryのテーブル構造変更に対応したクエリの更新
2. データインポート機能のデバッグと修正
3. BigQueryテーブル構造のモニタリング機構の実装（変更があった場合に自動通知）

これらの対応により、コンテナ上でもS3から認証情報を取得し、BigQueryからデータを安定して取得できるようになります。
