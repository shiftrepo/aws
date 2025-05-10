# LangChainフォールバック機能テスト用コマンド例

このドキュメントでは、patentDWHのLangChainフォールバック機能をテストするためのコマンド例を紹介します。これらの例を使用して、自然言語クエリからSQLが生成される過程と、必要に応じてLangChainフォールバックが機能することを確認できます。

## 注意事項（2025年5月10日更新）

最新のLangChainパッケージでは、`SQLDatabaseChain`が`langchain.chains`から`langchain_community.chains`に移動されました。これに対応するため、インポート文を以下のように修正しています：

```python
from langchain_community.chains import SQLDatabaseChain
```

この変更により、最新バージョンのLangChainでもフォールバック機能が正常に動作します。

## テスト方法

以下のcurlコマンドを使用して、APIエンドポイントに対して自然言語クエリをリクエストします。レスポンスに`"used_langchain": true`が含まれている場合、LangChainフォールバックが使用されたことを示します。

**注意**: 以下のコマンドはサーバーが`localhost:8080`で実行されていることを前提としています。実際の環境に合わせてURLを調整してください。

## テスト例1: 人工知能関連特許の検索

このクエリは、2020年以降の人工知能関連特許を検索します。複雑な自然言語クエリでフォールバックが発生する可能性があります。

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2020年以降に出願された人工知能に関する特許で、外国企業が出願人になっているものを教えてください",
    "db_type": "inpit"
  }' | jq
```

## テスト例2: 特許出願のトレンド分析

このクエリは、複数年にわたる特許出願のトレンドを分析し、グルーピングが必要な複雑なクエリです。

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "過去5年間の通信技術分野における特許出願数の推移を年別に集計してください",
    "db_type": "google_patents_gcp"
  }' | jq
```

## テスト例3: 特定企業の特許ポートフォリオ

このクエリは、特定の企業の特許ポートフォリオを分析する複雑な検索です。

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "テック株式会社が過去10年間に出願した特許を技術分野ごとに分類し、各分野の特許数をカウントしてください",
    "db_type": "inpit"
  }' | jq
```

## テスト例4: 複合条件を含む特許検索

このクエリは複数の条件を含み、原文で条件を正確に解析できない可能性のあるケースです。

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "エネルギー効率または省エネルギーに関する特許で、2022年以降に公開され、少なくとも3カ国で特許ファミリーを持つものを検索してください",
    "db_type": "google_patents_s3"
  }' | jq
```

## MCP APIを使用したテスト

MCPプロトコル経由でも同様のクエリをテストできます：

```bash
curl -X POST http://localhost:8080/api/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_nl_query",
    "tool_input": {
      "query": "再生可能エネルギーに関する特許で、日本と米国の両方で出願されているものを探してください",
      "db_type": "google_patents_gcp"
    }
  }' | jq
```

## 結果の解釈

各レスポンスには以下の主要な情報が含まれています：

1. **success**: リクエストが成功したかどうか
2. **query**: 送信された自然言語クエリ
3. **sql**: 生成されたSQLクエリ
4. **db_type**: クエリ対象のデータベース
5. **sql_result**: SQLクエリの結果（列、結果のレコード、総レコード数など）
6. **response**: 自然言語による回答
7. **used_langchain**: LangChainフォールバックが使用されたかどうか

例えば、次のような結果が得られます：

```json
{
  "success": true,
  "query": "2020年以降に出願された人工知能に関する特許で、外国企業が出願人になっているものを教えてください",
  "sql": "SELECT * FROM inpit_data WHERE application_date >= '2020-01-01' AND (title LIKE '%人工知能%' OR title LIKE '%AI%' OR title LIKE '%機械学習%') AND applicant_name NOT LIKE '%株式会社%' AND applicant_name NOT LIKE '%有限会社%' ORDER BY application_date DESC LIMIT 50;",
  "db_type": "inpit",
  "sql_result": {
    "columns": ["id", "application_number", "application_date", "title", "abstract", "applicant_name", "inventor_name", "status"],
    "results": [
      ["12345", "2020-123456", "2020-04-15", "人工知能を用いた画像認識システム", "本発明は...", "ABC Technologies Inc.", "John Smith", "審査中"],
      ...
    ],
    "record_count": 28
  },
  "response": "2020年以降に出願された人工知能関連の特許で外国企業が出願人になっているものは28件あります。主な出願としては、ABC Technologies Inc.による「人工知能を用いた画像認識システム」（2020年4月15日出願）などがあります...",
  "used_langchain": true
}
```

`"used_langchain": true`の場合、元のSQL生成メソッドが有効なSQLを生成できず、LangChainのDatabaseChainがフォールバックとして使用されたことを示します。
