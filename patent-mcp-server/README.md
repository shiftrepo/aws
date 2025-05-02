# Patent MCP Server

特許分析のための専門MCP（Model Context Protocol）サーバー。日本の出願人データに特化しています。

## 概要

このサーバーは、特許審査官や研究者向けに、出願人データの分析、レポート生成、出願人の比較などの機能を提供します。MCPプロトコルと統合することで、これらの機能を互換性のあるクライアントで利用できるようにしています。

## 特徴

- 包括的な出願人サマリー
- チャートや統計を含む視覚的レポート
- 審査比率分析
- 技術分野分布分析
- 競合他社との比較
- PDFレポート生成

## インストールと設定

### 前提条件

- DockerとDocker Compose
- Python 3.9以上

### Dockerでの実行方法

```bash
cd patent-mcp-server
docker-compose up -d
```

サーバーは `http://localhost:8000` で利用可能になります。

## API使用方法

サーバーは特許分析のための複数のREST APIエンドポイントを提供しています：

- `/applicant/{applicant_name}` - 出願人の包括的なサマリーを取得
- `/report/{applicant_name}` - 出願人の視覚的レポートを生成
- `/assessment/{applicant_name}` - 出願人の審査比率を分析
- `/technical/{applicant_name}` - 出願人の技術分野を分析
- `/compare/{applicant_name}` - 出願人を競合他社と比較

### 重要：日本語文字のURLエンコーディング

非ASCII文字（日本語の企業名など）でAPIを使用する場合、パラメータを適切にURLエンコードする必要があります。例えば、「テック株式会社」のデータを照会するには：

```bash
# 誤った例 - "Invalid HTTP request received"エラーが発生します
curl "http://localhost:8000/applicant/テック株式会社"

# 正しい例 - 適切にURLエンコードされています
curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
```

URLエンコーディングを支援するツールが用意されています：

1. `curl_examples.sh` - エンコーディングを使用した適切なcurlコマンドを示すシェルスクリプト
   ```bash
   ./curl_examples.sh "テック株式会社"  # 特定の出願人用のエンコードされたcurlコマンドを生成
   ```

2. `url_encode_demo.py` - コード内でURLエンコーディングを示すPythonスクリプト
   ```bash
   python url_encode_demo.py
   ```

3. `test_url_encoding.py` - URLエンコーディングが正しく機能することを検証するテストスクリプト
   ```bash
   python test_url_encoding.py "テック株式会社"
   ```

詳細については、[handling_non_ascii_characters.md](./docs/handling_non_ascii_characters.md)を参照してください。

## MCP統合

このサーバーはModel Context Protocolを実装し、MCPクライアントで利用できるツールとリソースを提供しています。主要なMCPエンドポイント：

- `/tools` - 利用可能なツールを一覧表示
- `/tools/execute` - ツールを実行
- `/resources` - 利用可能なリソースを一覧表示
- `/resources/access` - リソースにアクセス

## 開発

サーバーを変更または拡張するには：

1. `app/patent_system/mcp_patent_server.py`でツールとリソースの実装を更新
2. 自動再読み込みのために開発モードでサーバーを実行
   ```bash
   cd app
   python server.py
   ```

## ライセンス

Copyright © 2025
