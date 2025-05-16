# AI_integrated_search_mcp サービスで使用されるポート一覧

このドキュメントでは、AI_integrated_search_mcpシステムで使用されるすべてのポートを一覧表示します。これらのポートはDify統合やサービスアクセスに使用されます。

## サービス別ポート一覧

| サービス名 | ポート番号 | 環境変数名 | 用途 |
|------------|----------|------------|-----|
| Web UI | 5002 | WEBUI_PORT | ユーザーインターフェース用Webアプリケーション |
| Database API | 5003 | DATABASE_API_PORT | SQLiteデータベースとの対話用API |
| Natural Language Query API | 5004 | NL_QUERY_API_PORT | 自然言語クエリをSQL変換するAPI |
| LangChain Query API | 5005 | LANGCHAIN_QUERY_API_PORT | LangChainを使用した拡張クエリ処理API |
| Trend Analysis API | 5006 | TREND_ANALYSIS_API_PORT | 特許トレンド分析と可視化用API |

## OpenAPI仕様とDify統合

OpenAPI仕様ファイルは、上記のポート番号を反映しています：

1. `database-api-spec.json`: サーバーURLは `http://localhost:5003`
2. `nl-query-api-spec.json`: サーバーURLは `http://localhost:5004`
3. `trend-analysis-api-spec.json`: サーバーURLは `http://localhost:5006`

## 注意事項

- これらのポートは `.env` ファイルで設定されており、必要に応じて変更できます
- ポートを変更する場合は、対応するOpenAPI仕様ファイルの `servers.url` フィールドも更新する必要があります
- Difyに統合する場合は、サーバーURLにポート番号が正しく設定されていることを確認してください
- サービスへの外部アクセスを提供する場合は、これらのポートがファイアウォールで適切に開放されていることを確認してください
