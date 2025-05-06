# Inpit SQLite MCP Server

このサーバーは、特許情報を検索・分析するための MCP (Model Context Protocol) インターフェースを提供します。

## 主な特徴

- 特許情報の検索（出願番号、出願人など）
- 出願人の特許分析（サマリー、視覚的レポート、審査状況分析など）
- SQLクエリによる柔軟なデータ検索
- 日本語を含むURLの直接サポート（URLエンコーディング不要）

## URL エンコーディング機能について

このバージョンでは、URLに日本語などの非ASCII文字や空白を含める場合、明示的なURLエンコーディングが不要になりました。

### 例

以下のように直接日本語を含むURLでアクセスできます：

```
curl http://localhost:8000/applicant/テック株式会社
```

スペースを含む名前の場合：

```
curl 'http://localhost:8000/applicant/テック 株式会社'
```

### 対応しているエンドポイント

以下の全てのエンドポイントは日本語を含むパスを直接サポートします：

- `/applicant/{applicant_name}`
- `/application/{application_number}`
- `/applicant-summary/{applicant_name}`
- `/visual-report/{applicant_name}`
- `/assessment/{applicant_name}`
- `/technical/{applicant_name}`
- `/compare/{applicant_name}`
- `/pdf-report/{applicant_name}`

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
- `GET /application/{application_number}` - 出願番号による特許検索

### 特許分析

- `GET /applicant-summary/{applicant_name}` - 出願人のサマリー情報
- `GET /visual-report/{applicant_name}` - 視覚的レポートの生成
- `GET /assessment/{applicant_name}` - 審査状況の分析
- `GET /technical/{applicant_name}` - 技術分野の分析
- `GET /compare/{applicant_name}` - 競合他社との比較

### SQLクエリ

- `POST /sql` - SQLクエリの実行（フォーム形式）
- `POST /sql/json` - SQLクエリの実行（JSON形式）

### システム情報

- `GET /status` - データベースの状態確認
- `GET /tools` - 利用可能なツール一覧
- `GET /resources` - 利用可能なリソース一覧

## 技術情報

このサーバーは以下の技術を使用しています：

- FastAPI - 高速なWebフレームワーク
- Model Context Protocol (MCP) - AI モデルとの連携インターフェース
- SQLite - 軽量データベース

## ライセンス

Apache License 2.0
