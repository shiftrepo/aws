# Patent Analysis Container

このコンテナは特許出願動向分析ツールを実行するためのものです。

## 概要

特許出願動向分析コンテナは、特許のデータベースから特定の出願人の特許出願動向を分析し、以下を生成します：

1. 特許分類別の出願トレンドチャート
2. 出願動向の分析レポート
3. マークダウン形式の総合レポート

## 必要条件

- Docker および Docker Compose
- patentDWH サービス (データベースとMCPサービス)
- AWS認証情報（環境変数経由での提供）

## セットアップ方法

### 1. 環境変数の設定

AWS認証情報を環境変数として設定します：

```bash
export AWS_ACCESS_KEY_ID="your_aws_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_REGION="us-east-1"  # 必要に応じて変更
```

### 2. コンテナのビルド

```bash
cd patent_analysis_container
docker-compose build
```

## 使用方法

### patentDWHサービスの起動

先に patentDWH サービスを起動しておく必要があります：

```bash
cd patentDWH
docker-compose -f docker-compose.enhanced.yml up -d
```

### 特許分析の実行

出願人名を指定して特許分析を実行します：

```bash
cd patent_analysis_container
docker-compose run patent-analysis "出願人名" [db_type]
```

パラメータ：
- `出願人名`: 分析対象の出願人名（例：「トヨタ」）
- `db_type`: データベースタイプ（オプション、デフォルトは "inpit"）
  - 指定可能な値: "inpit", "google_patents_gcp", "google_patents_s3"

例：
```bash
docker-compose run patent-analysis "トヨタ" inpit
```

### 結果の取得

分析結果は `output` ディレクトリに保存されます：
- `[出願人名]_classification_trend.png`: 特許分類別トレンドチャート
- `[出願人名]_patent_analysis.md`: マークダウン形式の分析レポート

## 注意事項

- このコンテナは patentDWH サービスのネットワークに接続する必要があります。
- AWS認証情報を直接コードやコンテナ内に埋め込まず、常に環境変数として提供してください。
- 出力ディレクトリは `output` フォルダにマウントされるため、コンテナが削除されても分析結果は保持されます。

## トラブルシューティング

接続エラーが発生する場合：
1. patentDWH サービスが起動していることを確認
2. ネットワーク設定が正しいことを確認
3. ログを確認: `docker-compose logs patent-analysis`
