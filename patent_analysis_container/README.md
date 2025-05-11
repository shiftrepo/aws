# Patent Analysis Container

このコンテナは特許出願動向分析ツールを実行するためのものです。

## 概要

特許出願動向分析コンテナは、特許のデータベースから特定の出願人の特許出願動向を分析し、以下を生成します：

1. 特許分類別の出願トレンドチャート
2. 出願動向の分析レポート
3. マークダウン形式の総合レポート

また、MCPサーバー機能も提供しており、AIアシスタントからのAPIリクエストを通じて特許分析機能を利用できます。

## 必要条件

- Docker/Podman および Docker Compose/Podman Compose
- patentDWH サービス (データベースとMCPサービス)
- AWS認証情報（環境変数経由での提供）

## セットアップ方法

### 1. 環境変数の設定

AWS認証情報を環境変数として設定します：

```bash
export AWS_ACCESS_KEY_ID="your_aws_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_DEFAULT_REGION="us-east-1"  # 必要に応じて変更（REGIONではなくDEFAULT_REGIONを使用）
```

### 2. コンテナのビルド

```bash
cd patent_analysis_container
podman-compose build
```

## 使用方法

### patentDWHサービスの起動（推奨方法）

統合起動スクリプトを使用してすべてのサービスを一括で起動できます：

```bash
cd patentDWH
./start_all_services.sh
```

または個別に起動する場合：

```bash
cd patentDWH
podman-compose -f docker-compose.consolidated.yml up -d
```

### 特許分析の実行

出願人名を指定して特許分析を実行します：

```bash
cd patent_analysis_container
podman-compose run patent-analysis "出願人名" [db_type]
```

パラメータ：
- `出願人名`: 分析対象の出願人名（例：「トヨタ」）
- `db_type`: データベースタイプ（オプション、デフォルトは "inpit"）
  - 指定可能な値: "inpit", "google_patents_gcp", "google_patents_s3"

例：
```bash
podman-compose run patent-analysis "トヨタ" inpit
```

### 結果の取得

分析結果は `output` ディレクトリに保存されます：
- `[出願人名]_classification_trend.png`: 特許分類別トレンドチャート
- `[出願人名]_patent_analysis.md`: マークダウン形式の分析レポート

## 特許分析MCPサーバーの利用

### サーバーの起動

```bash
cd patent_analysis_container
./start_mcp_server.sh
```

または

```bash
podman-compose -f docker-compose.mcp.yml up -d
```

### APIエンドポイント

サーバーは以下のエンドポイントを提供します：

- `GET /`: ヘルスチェック
- `GET /docs`: Swagger API ドキュメント
- `GET /openapi.json`: OpenAPI スキーマ（Dify統合用）
- `POST /api/v1/mcp`: MCP互換エンドポイント
- `POST /api/tools/execute`: Dify互換エンドポイント
- `POST /api/analyze`: 特許傾向を分析してJSON結果を返す
- `GET /api/report/{applicant_name}`: マークダウン形式でレポートを取得
- `GET /api/report/{applicant_name}/zip`: ZIPファイル形式でレポートを取得

### 使用例

```bash
# 特許傾向の分析
curl -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "analyze_patent_trends",
    "tool_input": {
      "applicant_name": "トヨタ"
    }
  }'

# ZIPレポートのダウンロード
curl -X GET http://localhost:8000/api/report/トヨタ/zip -o toyota_report.zip
```

## 注意事項

- このコンテナは patentDWH サービスのネットワークに接続する必要があります。
- AWS認証情報を直接コードやコンテナ内に埋め込まず、常に環境変数として提供してください。
- 出力ディレクトリは `output` フォルダにマウントされるため、コンテナが削除されても分析結果は保持されます。
- AWS_REGIONではなく、AWS_DEFAULT_REGIONを使用してください。

## トラブルシューティング

### 一般的な問題

接続エラーが発生する場合：
1. patentDWH サービスが起動していることを確認
2. ネットワーク設定が正しいことを確認
3. ログを確認: `podman-compose logs patent-analysis`

### ネットワークの問題

コンテナが「Created」状態で停止する場合、またはコンテナ間通信に問題がある場合：

1. 修正スクリプトを実行:
   ```bash
   ./fix_mcp_container.sh
   ```

2. コンテナ間の通信をテスト:
   ```bash
   ./test_container_connectivity.sh
   ```

詳細な対応方法は `NETWORK_TROUBLESHOOTING.md` を参照してください。
