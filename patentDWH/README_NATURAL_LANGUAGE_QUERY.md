# patentDWH 自然言語クエリ機能

patentDWH システムは、AWS Bedrock を利用した自然言語クエリ機能を提供しています。これにより、ユーザーは特許データベースに対して自然言語（日本語や英語）で質問することができます。

## 概要

この自然言語クエリ機能は以下のコンポーネントによって実現されています：

1. **Claude 3 Sonnet (Anthropic)**：自然言語からSQLへの変換および結果の解釈に使用されます
2. **Titan Embedding Model (Amazon)**：テキスト埋め込み生成に使用されます
3. **RAG（検索拡張生成）**：データベーススキーマ情報をLLMに提供し、より正確なSQLクエリ生成を実現します

## 使用方法

### MCP API を通じた使用方法

```bash
# 自然言語クエリの実行例
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_nl_query",
    "tool_input": {
      "query": "ソニーが出願した人工知能関連の特許を教えてください",
      "db_type": "google_patents_gcp"
    }
  }' \
  http://localhost:8080/api/v1/mcp
```

### 直接 REST API を使用する方法

```bash
# 自然言語クエリの実行例
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "query": "トヨタが出願した自動運転技術に関する特許は何件ありますか？",
    "db_type": "google_patents_gcp"
  }' \
  http://localhost:8080/api/nl-query
```

## パラメータ

- **query**: 自然言語での質問（日本語または英語）
- **db_type**: 検索対象のデータベース（以下のいずれか）:
  - `inpit` - INPIT（特許庁）データベース（デフォルト）
  - `google_patents_gcp` - Google Patents GCP データベース
  - `google_patents_s3` - Google Patents S3 データベース

## レスポンス例

成功した場合、レスポンスには以下の情報が含まれます：

```json
{
  "success": true,
  "query": "ソニーが出願した人工知能関連の特許を教えてください",
  "sql": "SELECT publication_number, title_ja, publication_date, assignee_harmonized FROM publications WHERE assignee_harmonized LIKE '%Sony%' AND (title_ja LIKE '%人工知能%' OR title_ja LIKE '%AI%' OR title_ja LIKE '%機械学習%') ORDER BY publication_date DESC LIMIT 20;",
  "db_type": "google_patents_gcp",
  "sql_result": {
    "success": true,
    "columns": ["publication_number", "title_ja", "publication_date", "assignee_harmonized"],
    "results": [
      // ここに検索結果が表示されます
    ],
    "record_count": 15
  },
  "response": "ソニー（Sony）が出願した人工知能関連の特許として、データベースには15件の特許が見つかりました。これらの特許は公開日の新しい順に表示されています。特許には「画像認識アルゴリズム」や「自然言語処理システム」など、様々な種類の人工知能技術が含まれています。最新の特許は2023年に公開されたもので、主に画像処理と機械学習の組み合わせに関するものです。"
}
```

エラーが発生した場合：

```json
{
  "success": false,
  "error": "エラーメッセージがここに表示されます"
}
```

## 動作の仕組み

1. ユーザーが自然言語で質問を入力
2. Claude 3 Haiku がデータベーススキーマ情報と各テーブルの実データサンプル（5件程度）を参照しながら適切なSQLクエリを生成
3. 生成されたSQLクエリがデータベースに対して実行される
4. クエリ結果が再度Claude 3 Haikuに送られ、自然言語での回答が生成される
5. 最終的な結果（元の質問、生成されたSQL、SQLの実行結果、自然言語での回答）がユーザーに返される

LLMへの入力情報:
- 問い合わせの自然言語
- データベースの構造情報（テーブル名、カラム名）
- 全テーブルの5件程度のサンプルレコード（全項目を含む）

## AWS 設定要件

この機能を使用するには、以下の環境変数が設定されている必要があります：

- `AWS_REGION`: AWSリージョン（例：`us-east-1`）
- `AWS_ACCESS_KEY_ID`: AWS アクセスキー
- `AWS_SECRET_ACCESS_KEY`: AWS シークレットアクセスキー

AWS IAM ロールには以下のアクセス許可が必要です：

- `bedrock:InvokeModel` - Claude 3 Sonnet モデルを呼び出すための権限
- `bedrock:InvokeModel` - Titan Embedding モデルを呼び出すための権限

## パフォーマンスと制限事項

- 自然言語クエリの処理には、通常のSQLクエリよりも時間がかかります（LLM呼び出しが必要なため）
- 複雑な質問や特殊なデータベース機能を必要とするクエリは、適切に処理できない場合があります
- この機能はRAG（検索拡張生成）に基づいているため、データベーススキーマが変更された場合は再起動が必要です

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. AWS認証情報が正しく設定されているか
2. Bedrockモデル（Claude 3 Sonnet と Titan Embedding）が指定されたAWSリージョンで利用可能か
3. IAMポリシーが適切に設定されているか
4. データベース接続が正常に機能しているか（`/health` エンドポイントで確認可能）

詳細なログはpatentDWH MCPサーバーのログを参照してください。
