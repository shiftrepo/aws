# Inpit SQLite

このシステムは、Inpit SQLite APIをデータソースとして使用し、特許データの分析を行うツールセットです。

## 概要

このシステムは以下の機能を提供します：

- Inpit SQLiteからのデータの取得と分析
- 特許技術トレンドの分析
- 出願人競合分析
- 特許ランドスケープ分析
- 包括的な分析レポートの生成
- MCPサーバーを通じたClaude AIとの連携

## 前提条件

- Python 3.8以上
- Inpit SQLiteサービス（通常は`http://localhost:5001`で実行）
- MCP互換のClaude AI（VSCode Claude拡張機能またはClaude Desktop App）

## セットアップ手順

### 1. データベース構造の初期化

以下のコマンドを実行して、ローカルSQLiteデータベースの構造を初期化します：

```bash
python -m app.patent_system.init_db
```

このコマンドは：
- ローカルSQLiteデータベースのテーブルを作成します（実際のデータは含まれません）

### オプション：

- `--skip-init`: データベース構造の初期化をスキップする
- `--api-url URL`: Inpit SQLite APIのURLを指定する（デフォルト: http://localhost:5001）

例：
```bash
python -m app.patent_system.init_db --api-url http://192.168.1.100:5001
```

## 使用方法

### 特許データの分析

直接Inpit SQLiteのデータを使用して分析を行います：

```bash
python -m app.patent_system.patent_analyzer_inpit
```

### MCPサーバー経由でのClaude AIとの連携

MCPサーバーを起動して、Claude AIからInpit SQLiteデータにアクセスできるようにします：

```bash
# 環境変数でInpit SQLite APIのURLを指定（オプション）
export INPIT_API_URL=http://localhost:5001

# MCPサーバーの起動
python -m app.patent_system.mcp_patent_server
```

これにより、Claude AIは以下のようなMCPツールを使用できるようになります：

- `query_patents`: 出願番号による特許の検索
- `search_patents_by_applicant`: 出願人名による特許の検索
- `execute_sql_query`: SQLクエリによる特許データの検索
- `analyze_technology_trends`: 技術トレンドの分析
- `analyze_applicant_competition`: 出願人競合分析
- `analyze_patent_landscape`: 特許ランドスケープ分析
- `generate_analysis_report`: 包括的な分析レポートの生成
- その他

## MCP設定

MCPサーバーの設定は `app/patent_system/mcp_config.json` ファイルに定義されています。
必要に応じて、サーバー名や設定を変更できます。

```json
{
"servers": [
    {
      "name": "inpit-patent-analytics",
      "version": "1.0.0",
      "description": "Tools for patent analytics using Inpit SQLite data...",
      "module_path": "app.patent_system.mcp_patent_server",
      "enabled": true,
      "auth": {
        "type": "none"
      },
      "config": {
        "api_url": "http://localhost:5001"
      }
    }
  ]
}
```

## ファイル構成

- `app/patent_system/init_db.py` - データベース構造初期化スクリプト
- `app/patent_system/inpit_sqlite_connector.py` - Inpit SQLite接続モジュール
- `app/patent_system/patent_analyzer_inpit.py` - 特許分析モジュール（Inpit SQLite版）
- `app/patent_system/mcp_patent_server.py` - MCP統合サーバー
- `app/patent_system/mcp_config.json` - MCP設定ファイル
- `app/patent_system/models_sqlite.py` - SQLiteデータベースモデル

## 注意事項

- このシステムはInpit SQLite APIが正常に動作している環境が必要です
- システムはデータの保存に外部のInpit SQLite APIを直接使用します
