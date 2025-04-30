# Inpit SQLite データベースシステム

このシステムはS3からの特許データをダウンロードし、データの閲覧と検索のためのSQLiteデータベースを作成します。

## 機能

- 指定されたS3バケットからの特許データの自動ダウンロード
- CSVヘッダーに基づく動的なスキーマ作成
- データの閲覧と検索のためのWebベースUI
- 高度なデータ分析のためのSQLクエリインターフェース

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
   podman-compose up -d
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
SELECT * FROM inpit_data WHERE applicant_name LIKE '%株式会社%' LIMIT 50;

-- 特定の発明者のデータを表示（20件まで）
SELECT * FROM inpit_data WHERE inventor_name LIKE '%田中%' LIMIT 20;
```

### 集計・分析クエリ

```sql
-- 出願人別の出願数（上位30件）
SELECT applicant_name, COUNT(*) as application_count 
FROM inpit_data 
GROUP BY applicant_name 
ORDER BY application_count DESC 
LIMIT 30;

-- 出願日別の出願数（最大100件）
SELECT application_date, COUNT(*) as count 
FROM inpit_data 
GROUP BY application_date 
ORDER BY application_date DESC 
LIMIT 100;

-- IPC分類別の出願数（上位20件）
SELECT ipc_classification, COUNT(*) as count 
FROM inpit_data 
GROUP BY ipc_classification 
ORDER BY count DESC 
LIMIT 20;
```

### 複合検索クエリ

```sql
-- タイトルと要約で複合検索（最大30件）
SELECT * FROM inpit_data 
WHERE title LIKE '%AI%' OR abstract LIKE '%人工知能%' 
LIMIT 30;

-- 特定の期間と出願人による検索（最大25件）
SELECT * FROM inpit_data 
WHERE application_date BETWEEN '2022-01-01' AND '2022-12-31' 
AND applicant_name LIKE '%テック%' 
LIMIT 25;
```

上記のクエリは、Webインターフェースの「SQL Query」タブで実行できます。実際のデータベース構造に合わせてクエリを調整してください。
