# 特許分析システム

このシステムは、特許データを分析し、有用なインサイトを抽出するための総合的なツールセットです。

## 最新の変更

このシステムは、データ取得先をInpit SQLiteに完全に移行しました。サンプルデータや静的なデモデータは使用せず、すべてのデータをInpit SQLiteデータベースAPIから直接取得します。

## 主要機能

- 特許データの取得と管理
- 技術トレンドの分析
- 出願人競合分析
- 特許ランドスケープの可視化
- 包括的な分析レポートの生成

## データソース

- **Inpit SQLiteデータベースAPI**: すべての特許データはInpit SQLite APIを通じて取得されます（デフォルトでは `http://localhost:5001` で実行）

## システム要件

- Python 3.8以上
- Inpit SQLiteサービス
- SQLAlchemyおよび関連パッケージ
- 必要に応じてMCP対応のAIツール（Claude等）

## セットアップおよび使用方法

詳細な設定手順と使用方法は以下のドキュメントを参照してください：

- [Inpit SQLite版特許分析システム](app/patent_system/README_INPIT_SQLITE.md)

## クイックスタート

```bash
# データベースの初期化とInpit SQLiteからのデータインポート
python -m app.patent_system.init_db

# 直接Inpit SQLiteデータを使用した分析の実行
python -m app.patent_system.patent_analyzer_inpit

# MCPサーバーの起動（Claudeなどのツールと統合する場合）
python -m app.patent_system.mcp_patent_server
```

## システム構成

- `app/patent_system/` - 特許分析システムのコアコード
  - `inpit_sqlite_connector.py` - Inpit SQLite APIとの接続モジュール
  - `patent_analyzer_inpit.py` - Inpit SQLiteを使用した特許分析機能
  - `data_importer.py` - データインポートツール
  - `init_db.py` - データベース初期化スクリプト
  - `mcp_patent_server.py` - MCP統合サーバー

## ライセンス

Copyright (C) 2025
