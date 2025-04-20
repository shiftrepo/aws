# J-PlatPat 特許クエリシステム

このプロジェクトは、J-PlatPatの特許データを軽量RDBに格納し、AWS Bedrockを利用して自然言語による検索を実現するシステムです。

## システム構成

1. **PostgreSQLデータベース**
   - 特許出願情報を構造化して格納
   - テーブル: patents, applicants, inventors, claims, descriptions など

2. **データインポートシステム**
   - J-PlatPatからスクレイピングしたデータを取り込み
   - PDFからのテキスト抽出機能
   - サンプルデータ生成機能

3. **AWS Bedrock MCPサーバー**
   - 自然言語による特許検索クエリを処理
   - 特許データに基づいた質問応答
   - 埋め込みベクトルによる類似特許検索

## セットアップ方法

### 必須環境

- Python 3.9+
- PostgreSQL
- AWS認証情報（Bedrockにアクセスするため）

### セットアップ手順

1. 必要なパッケージをインストール:
```bash
pip install psycopg2-binary numpy boto3
```

2. データベースの初期化とサンプルデータの投入:
```bash
python -m app.patent_system.init_and_demo
```

3. MCPサーバーを実行:
```bash
cd /home/ec2-user/Documents/Cline/MCP/bedrock-patent-query/
python src/index.py
```

## 使用方法

### MCP サーバーツールの使い方

特許に関する自然言語クエリを処理するには以下のようなフォーマットで利用します：

```
<use_mcp_tool>
<server_name>bedrock-patent-query</server_name>
<tool_name>query_patents</tool_name>
<arguments>
{
  "query": "AIを活用した特許管理システムについて教えてください"
}
</arguments>
</use_mcp_tool>
```

### 利用可能なMCPツール

1. **query_patents** - 特許情報に基づいて質問に回答
   - 引数: `query` (質問文), `limit` (参照する特許数、デフォルト5)

2. **search_patents** - 自然言語の類似性に基づいて特許を検索
   - 引数: `query` (検索クエリ), `limit` (結果数、デフォルト10)

3. **get_patent_stats** - データベース内の特許統計を取得
   - 引数: なし

## ファイル構成

- `app/patent_system/` - 特許データ管理システム
  - `models.py` - データベースモデル
  - `db_manager.py` - データベース操作
  - `j_platpat_scraper.py` - J-PlatPatスクレイパー
  - `data_importer.py` - データインポート
  - `init_and_demo.py` - 初期化とデモ

- `/home/ec2-user/Documents/Cline/MCP/bedrock-patent-query/` - MCPサーバー
  - `src/index.py` - Bedrock特許クエリサーバー

## 機能拡張

このシステムは以下のように拡張可能です：

1. 実際のJ-PlatPat認証情報を使用してリアルタイムデータ取得
2. 特許埋め込みベクトルのデータベース保存による検索高速化
3. 他の特許データベース（USPTO、EPOなど）との統合
4. 特許分析機能の追加（技術トレンド分析、競合分析など）
