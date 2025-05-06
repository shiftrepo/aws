# Inpit SQLite MCP Server

このサーバーは、特許情報を検索・分析するための MCP (Model Context Protocol) インターフェースを提供します。

## 主な特徴

- 特許情報の検索（出願番号、出願人など）
- 出願人の特許分析（サマリー、視覚的レポート、審査状況分析など）
- SQLクエリによる柔軟なデータ検索
- 日本語を含むURLの直接サポート（URLエンコーディング不要）

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

## セットアップと実行

```bash
# サーバーの起動
docker-compose up -d

# または独自の環境変数を設定して起動
INPIT_API_URL=http://your-api-url docker-compose up -d
```

サーバーが起動すると、`http://localhost:8000` でアクセス可能になります。

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

## ライセンス

Apache License 2.0
