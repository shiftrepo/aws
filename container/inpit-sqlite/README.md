# Inpit SQLite データベースシステム

このシステムはS3からの特許データをダウンロードし、データの閲覧と検索のためのSQLiteデータベースを作成します。HTTP APIも提供しています。

## 機能

- 指定されたS3バケットからの特許データの自動ダウンロード
- CSVヘッダーに基づく動的なスキーマ作成
- データの閲覧と検索のためのWebベースUI
- 高度なデータ分析のためのSQLクエリインターフェース
- RESTful API（出願番号検索、出願人検索、SQLクエリ）

## 要件

- Docker または Podman
- S3アクセス権限を持つAWS認証情報

## セットアップ

1. 指定されたS3バケットにアクセスできるAWS認証情報が適切に設定されていることを確認します：
   ```
   export AWS_ACCESS_KEY_ID=あなたのアクセスキー
   export AWS_SECRET_ACCESS_KEY=あなたのシークレットキー
   ```

2. システムを起動します：
   ```
   podman-compose -f docker-compose.yml up -d
   ```

3. Webインターフェースには http://localhost:5001 でアクセスできます

## 動作原理

1. 起動時、システムはS3バケットから特許データファイルをダウンロードします
2. システムはCSVヘッダーを読み取り、動的にデータベーススキーマを作成します
3. すべてのデータがSQLiteデータベースにインポートされます
4. データの閲覧と検索のためのWebインターフェースが提供されます

## データ処理

システムは以下の手順を実行します：

1. **データのダウンロード**: `download_data.py`スクリプトがS3からCSVファイルをダウンロードします
2. **スキーマ作成**: `schema.py`スクリプトが：
   - CSVヘッダーを読み取り、カラム構造を決定します
   - 適切なカラムを持つデータベーステーブルを作成します
   - 元のCSVカラムヘッダーからSQL対応の名前へのマッピングを保持します
   - すべてのデータをデータベースにインポートします
   - 重要なカラムにインデックスを作成します

## ファイル

- `download_data.py`: S3からデータをダウンロードします
- `schema.py`: データベーススキーマを作成し、データをインポートします
- `app.py`: データの閲覧と検索のためのFlaskウェブアプリケーション
- `entrypoint.sh`: コンテナ起動スクリプト

## 環境変数

- `AWS_ACCESS_KEY_ID`: S3認証のためのAWSアクセスキー
- `AWS_SECRET_ACCESS_KEY`: S3認証のためのAWSシークレットキー
- `AWS_DEFAULT_REGION`: AWSリージョン（デフォルト: ap-northeast-1）

## 注意事項

- システムが正しく機能するためには、S3からのデータダウンロードが成功する必要があります
- データはサンプルデータ処理なしで、ダウンロードしたCSVファイルから直接インポートされます
- データベーステーブルはCSVヘッダーに基づいて動的に作成されます

## サンプルSQLクエリ

データベース内のデータを閲覧・分析するためのサンプルSQLクエリです。大量のデータを扱う場合は、`LIMIT`句を使用して結果を制限することをお勧めします。

### 基本的なデータ閲覧クエリ（最大100件）

```sql
-- 全てのレコードを表示（100件まで）
SELECT * FROM inpit_data LIMIT 100;

-- 特定の出願人のデータを表示（50件まで）
SELECT * FROM inpit_data WHERE 出願人 LIKE '%株式会社%' LIMIT 50;

-- 特定の登録者のデータを表示（20件まで）
SELECT * FROM inpit_data WHERE 登録者名称 LIKE '%田中%' LIMIT 20;
```

### 集計・分析クエリ

```sql
-- 出願人別の出願数（上位30件）
SELECT 出願人, COUNT(*) as application_count 
FROM inpit_data 
GROUP BY 出願人 
ORDER BY application_count DESC 
LIMIT 30;

-- 出願日別の出願数（最大100件）
SELECT 出願日, COUNT(*) as count 
FROM inpit_data 
GROUP BY 出願日 
ORDER BY 出願日 DESC 
LIMIT 100;

-- IPC分類別の出願数（上位20件）
SELECT 国際特許分類_IPC_, COUNT(*) as count 
FROM inpit_data 
GROUP BY 国際特許分類_IPC_ 
ORDER BY count DESC 
LIMIT 20;
```

### 複合検索クエリ

```sql
-- タイトルと技術概要で複合検索（最大30件）
SELECT * FROM inpit_data 
WHERE タイトル LIKE '%AI%' OR 技術概要 LIKE '%人工知能%' 
LIMIT 30;

-- 特定の期間と出願人による検索（最大25件）
SELECT * FROM inpit_data 
WHERE 出願日 BETWEEN '2022-01-01' AND '2022-12-31' 
AND 出願人 LIKE '%テック%' 
LIMIT 25;
```

上記のクエリは、Webインターフェースの「SQL Query」タブで実行できます。実際のデータベース構造に合わせてクエリを調整してください。

## API

問い合わせに対応するためのHTTP APIを提供しています。すべてのAPIエンドポイントはJSONレスポンスを返します。

### API エンドポイント

#### API ステータスと情報

```
GET /api/status
```

システムの状態、データベース接続状況、レコード数、利用可能なエンドポイント、およびデータベーススキーマ情報を返します。

#### 出願番号による検索

```
GET /api/application/{出願番号}
```

指定された出願番号に一致するレコードを検索します。部分一致も可能です。

例:
```
GET /api/application/2022-123456
```

#### 出願人による検索

```
GET /api/applicant/{出願人名}
```

指定された出願人に関するレコードを検索します。部分一致も可能です。

例:
```
GET /api/applicant/テック株式会社
```

#### SQL直接クエリ

```
POST /api/sql-query
Content-Type: application/json

{
  "query": "SELECT * FROM inpit_data WHERE 出願日 BETWEEN '2022-01-01' AND '2022-12-31' LIMIT 10"
}
```

SQLクエリを直接実行します。セキュリティ上の理由から、SELECT文のみが許可されています。

### API レスポンス形式

成功時のレスポンス例:

```json
{
  "success": true,
  "columns": ["id", "application_number", "applicant_name", "title", ...],
  "results": [
    [1, "2022-123456", "テック株式会社", "AIを用いた特許検索システム", ...],
    ...
  ],
  "record_count": 10
}
```

エラー時のレスポンス例:

```json
{
  "error": "クエリの実行中にエラーが発生しました"
}
```

### 使用例（curl）

出願番号での検索例:
```bash
curl http://localhost:5001/api/application/2022-123456
```

出願人での検索例:
```bash
curl http://localhost:5001/api/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE
```

SQLクエリの例:
```bash
curl -X POST http://localhost:5001/api/sql-query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 出願人, COUNT(*) as count FROM inpit_data GROUP BY 出願人 ORDER BY count DESC LIMIT 10"}'
```
