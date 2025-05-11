# Patent Analysis MCP Server - Dify Integration Guide

このガイドでは、特許分析MCPサーバーをDifyプラットフォームで利用する方法について説明します。

## 概要

特許分析MCPサーバーは、OpenAPIに基づいたHTTPのAPIエンドポイントを提供し、SQLiteデータベースとLLMを利用して特許出願傾向の分析とレポート生成を行います。生成されるマークダウンレポートは、ZIP圧縮形式でダウンロード可能です。

## MCPサーバーのセットアップ

### 前提条件

- Docker
- docker-compose
- SQLiteデータベース（特許データ）

### サーバーの起動

1. リポジトリのクローンやダウンロード後、以下のコマンドを実行します：

```bash
cd patent_analysis_container
chmod +x start_mcp_server.sh
./start_mcp_server.sh
```

スクリプトが実行されると、必要なDockerコンテナがビルドされ、MCPサーバーが起動します。サーバーは `http://localhost:8000` でアクセスできます。

## API エンドポイント

特許分析MCPサーバーは以下のエンドポイントを提供しています：

- `GET /`: ヘルスチェック
- `GET /docs`: Swagger API ドキュメント
- `GET /openapi.json`: OpenAPI スキーマ（Dify統合用）
- `POST /api/v1/mcp`: MCP互換エンドポイント
- `POST /api/tools/execute`: Dify互換エンドポイント
- `POST /api/analyze`: 特許傾向を分析してJSON結果を返す
- `GET /api/report/{applicant_name}`: マークダウン形式でレポートを取得
- `GET /api/report/{applicant_name}/zip`: ZIPファイル形式でレポートを取得

## Difyとの統合

### OpenAPIの設定

1. Difyダッシュボードで、新しいアプリケーションを作成または既存のアプリケーションを開きます。
2. 「ツール」セクションに移動し、「OpenAPIツールの追加」を選択します。
3. 以下の情報を入力します：
   - **名前**: Patent Analysis
   - **説明**: 特許出願傾向の分析とレポート生成
   - **API Base URL**: MCPサーバーのURL（例: `http://localhost:8000`）
   - **OpenAPI スキーマ**: `http://localhost:8000/openapi.json` を使用するか、OpenAPI JSONをコピー＆ペースト

4. 「ツールの追加」をクリックして保存します。

### Difyでのツール使用例

Difyのプロンプト設定で、以下のような指示を使用できます：

```
特許分析ツールを使用して、[会社名]の特許出願傾向を分析し、レポートを生成してください。
生成されたレポートのZIPファイルをダウンロードするURLを提供してください。
```

## APIの使用例

### cURLを使用した例

#### MCP互換エンドポイントの使用

```bash
curl -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "analyze_patent_trends",
    "tool_input": {
      "applicant_name": "トヨタ"
    }
  }'
```

#### Dify互換エンドポイントの使用

```bash
curl -X POST http://localhost:8000/api/tools/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "analyze_patent_trends",
    "arguments": {
      "applicant_name": "トヨタ"
    }
  }'
```

#### ZIPレポートのダウンロード

```bash
curl -X GET http://localhost:8000/api/report/トヨタ/zip -o toyota_report.zip
```

## SQLiteデータベース

このサーバーはSQLiteデータベースを使用して特許データを保存・管理します。データベースファイルは docker-compose 設定でボリュームとしてマウントされます。

データベースには以下のテーブルが含まれています：
- patents: 特許基本情報
- applicants: 出願人情報
- inventors: 発明者情報
- ipc_classifications: IPC分類情報
- claims: 請求項
- descriptions: 説明文

## レポート生成プロセス

1. SQLiteデータベースから特許データを取得
2. 年度別・IPC分類別に集計
3. LLMを使用してデータを分析し、傾向をまとめる
4. レポート用の可視化グラフ生成
5. マークダウン形式でレポート作成
6. すべてのファイルをZIPアーカイブとして提供

## レポート内容

生成されるZIPファイルには以下の内容が含まれています：

1. `{applicant_name}_patent_analysis.md`: マークダウン形式の分析レポート
2. `{applicant_name}_classification_trend.png`: 特許分類別の出願動向グラフ

## トラブルシューティング

サーバー起動に問題がある場合は、以下のコマンドでログを確認できます：

```bash
docker-compose -f docker-compose.mcp.yml logs
```

## 注意事項

- 非ASCII文字（日本語など）を含むapplicant_nameをURLで使用する場合は、適切にURLエンコードしてください。
- サーバー起動前に特許データがSQLiteデータベースに登録されていることを確認してください。

## 高度な設定

サーバーの設定は環境変数を通じて変更可能です。`docker-compose.mcp.yml`ファイルの`environment`セクションで以下の変数をカスタマイズできます：

- `HOST`: サーバーのホスト（デフォルト: 0.0.0.0）
- `PORT`: サーバーのポート（デフォルト: 8000）
- `OUTPUT_DIR`: 出力ディレクトリ（デフォルト: /app/output）
- `LLM_SERVICE_URL`: LLM APIのURL
- `DB_URL`: データベースAPIのURL
- `DATABASE_PATH`: SQLiteデータベースのパス
