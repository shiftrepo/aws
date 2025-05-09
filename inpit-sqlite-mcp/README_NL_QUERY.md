# 特許データベース自然言語検索機能

このドキュメントでは、INPIT SQLite（inpit.db）とGoogle Patents（google_patents_gcp.db）データベースに対する自然言語クエリ機能の使用方法を説明します。

## 概要

この機能強化により、SQLを知らなくても自然言語を使用して特許データベースに問い合わせができるようになりました。日本語と英語の両方の質問に対応しており、特許検索を簡素化します。

### サポートされているデータベース

- **INPIT SQLite (inpit.db)**: 日本特許情報の検索
- **Google Patents (google_patents_gcp.db)**: Google Patents Public Dataからのデータ検索

## 機能

- 自然言語での検索（日本語・英語）
- 出願人、発明者、技術分野、期間などの複数条件の組み合わせによる検索
- 詳細なヘルプ情報とサンプルクエリ
- APIエンドポイントを通じたアクセス

## MCP統合

この機能はMCP（Model Context Protocol）サーバー経由で使用できます。MCP連携により、自動化アシスタントが直接特許データにアクセスして自然言語で問い合わせができるようになります。

```
MCP Tools:
- nl_query_inpit_database: INPITデータベースへの自然言語クエリ
- nl_query_google_patents_database: Google Patentsデータベースへの自然言語クエリ

MCP Resources:
- nl-query://inpit/help: INPITデータベースの検索ヘルプ
- nl-query://google-patents/help: Google Patentsデータベースの検索ヘルプ
```

## 使用方法

### APIエンドポイント

以下のエンドポイントが利用可能です：

1. **ヘルプエンドポイント**:
   - GET `/nl-query/help/inpit` - INPITデータベースの検索ヘルプ
   - GET `/nl-query/help/google-patents` - Google Patentsデータベースの検索ヘルプ

2. **検索エンドポイント (フォーム形式)**:
   - POST `/nl-query/inpit` - INPITデータベースへの自然言語クエリ
   - POST `/nl-query/google-patents` - Google Patentsデータベースへの自然言語クエリ

3. **検索エンドポイント (JSON形式)**:
   - POST `/nl-query/inpit/json` - INPITデータベースへのJSON形式自然言語クエリ
   - POST `/nl-query/google-patents/json` - Google PatentsデータベースへのJSON形式自然言語クエリ

### クエリの例

#### INPITデータベース

**日本語クエリの例**:

- `トヨタによる特許を5件表示して`
- `ソニーの2020年以降のカメラに関する特許`
- `出願人がパナソニックの電池技術に関する特許を検索`
- `日立の最新の半導体特許10件を見せて`
- `2015年から2018年までの自動車関連の特許`
- `出願番号2019-123456の特許情報`

**英語クエリの例**:

- `Show me 5 patents by Toyota`
- `Find camera-related patents from Sony after 2020`
- `Search for battery technology patents by Panasonic`
- `Show latest 10 semiconductor patents from Hitachi`
- `Automobile patents from 2015 to 2018`
- `Patent information for application number 2019-123456`

#### Google Patentsデータベース

**英語クエリの例**:

- `Show me patents about electric vehicles`
- `Find 5 recent machine learning patents from IBM`
- `Patents related to camera technology after 2018`
- `Show me family members of US10123456`
- `Latest semiconductor patents from Samsung`

**日本語クエリの例**:

- `電気自動車に関する特許を表示`
- `IBMの機械学習特許を5件見せて`
- `2018年以降のカメラ技術に関する特許`
- `US10123456のファミリーメンバーを表示`
- `サムスンの最新の半導体特許`

### curlでのAPIテスト

提供されているスクリプトを使用してAPIをテストできます:

```bash
# スクリプトを実行可能にする
chmod +x inpit-sqlite-mcp/app/nl_query_examples.sh

# スクリプトを実行
./inpit-sqlite-mcp/app/nl_query_examples.sh
```

または、個別にcurlコマンドを実行:

```bash
# INPITデータベースのヘルプを取得
curl http://localhost:8000/nl-query/help/inpit | python -m json.tool

# 自然言語クエリを実行 (フォーム形式)
curl -X POST http://localhost:8000/nl-query/inpit \
  -d "query=トヨタの自動車関連の特許を5件表示して" | python -m json.tool

# 自然言語クエリを実行 (JSON形式)
curl -X POST http://localhost:8000/nl-query/inpit/json \
  -H "Content-Type: application/json" \
  -d '{"query": "ソニーの2019年以降のカメラ技術に関する特許"}' | python -m json.tool
```

## 応答フォーマット

APIは以下のようなJSONレスポンスを返します:

```json
{
  "success": true,
  "query": "トヨタの自動車関連の特許を5件表示して",
  "sql_query": "SELECT * FROM inpit_data WHERE applicant_name LIKE '%トヨタ%' AND (title LIKE '%自動車%' OR abstract LIKE '%自動車%') ORDER BY filing_date DESC LIMIT 5",
  "count": 5,
  "results": [
    {
      "id": 123,
      "出願番号": "2020-123456",
      "公開番号": "JP2020-123456",
      "出願人": "トヨタ自動車株式会社",
      "発明者": "山田太郎",
      "タイトル": "自動車の駆動制御装置",
      "要約": "本発明は、自動車の...",
      "出願日": "2020-01-15",
      "公開日": "2020-07-30"
    },
    // 他の結果...
  ],
  "total_results": 5,
  "database": "INPIT SQLite (inpit.db)"
}
```

## 実装の詳細

- **inpit_nl_query_processor.py**: INPIT SQLiteデータベースの自然言語クエリ処理
- **nl_query_processor.py**: Google Patentsデータベースの自然言語クエリ処理
- **nl_query_mcp.py**: MCPサーバー統合とAPIエンドポイント
- **server.py**: FastAPIサーバーの設定と統合ルート

## 制限事項

- 自然言語処理の精度は、入力されるクエリの明確さに依存します。
- より複雑なクエリでは、一部の条件が正確に解釈されない場合があります。
- 検索結果はデータベース内のデータに依存します。データベースに十分なデータがない場合、結果が限られる可能性があります。

## ライセンス

プロジェクトのライセンスに従います。
