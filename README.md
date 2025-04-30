# 特許データ分析システム (Patent Analysis System)

このシステムは、Inpit SQLite APIをデータソースとして使用し、特許データの高度な分析と可視化を行うための総合的なツールセットです。

## 概要

特許データ分析システムは、Inpit SQLiteデータベースAPIからリアルタイムにデータを取得・分析し、技術トレンド、競合状況、特許ランドスケープに関する詳細な洞察を提供します。サンプルデータやデモデータは使用せず、常に最新のAPIデータを直接利用します。

### 主要機能

- **特許データのクエリと取得**: 出願番号、出願人名、SQLクエリなどによる特許データの検索
- **技術トレンド分析**: 国際特許分類（IPC）に基づく技術トレンドの時系列分析
- **出願人競合分析**: 主要出願者の特許活動と技術的な重複の分析
- **特許ランドスケープ可視化**: 技術領域の広がりと集中度の分析
- **包括的レポート生成**: Markdown形式の詳細な分析レポート作成
- **MCP統合**: Claude AIなどのツールとの連携機能

## 前提条件

- Python 3.8以上
- Inpit SQLiteサービス（デフォルト: `http://localhost:5001`）
- 必要なPythonパッケージ（requirements.txt参照）
- MCP統合を使用する場合はClaude拡張機能など

## インストール方法

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/patent-analysis-system.git
cd patent-analysis-system
```

2. 必要なパッケージをインストール:
```bash
pip install -r app/patent_system/requirements.txt
```

3. Inpit SQLiteサービスが実行中であることを確認:
```bash
curl http://localhost:5001/api/status
```

## 実行方法

### 1. データベース構造の初期化

最初に、ローカルSQLiteデータベースの構造を初期化します（実際のデータはInpit SQLite APIから取得）:

```bash
python -m app.patent_system.init_db
```

#### オプション:
- `--skip-init`: データベース初期化をスキップ
- `--api-url URL`: Inpit SQLite APIのURLを指定（デフォルト: http://localhost:5001）

実行例:
```bash
# カスタムAPIエンドポイントを使用
python -m app.patent_system.init_db --api-url http://192.168.1.100:5001
```

### 2. 特許データの分析

直接Inpit SQLiteデータを使用した分析を実行:

```bash
python -m app.patent_system.patent_analyzer_inpit
```

実行例（出力例）:
```
2025-04-30 13:25:38,193 - app.patent_system.inpit_sqlite_connector - INFO - Initialized Inpit SQLite connector with URL: http://localhost:5001

Analysis Report Preview:

# 特許分析レポート

## 概要
- **総特許数**: 17396
- **出願者数**: 1455
- **発明者数**: 0
- **期間**: N/A から N/A

## 技術トレンド分析

過去5年間の主要技術分野の推移:

- **None**: 説明が利用できません
- **G06Q50/02**: 計算、計数
- **A01G7/00,G06Q50/02**: 人間の必需品
...
```

### 3. MCPサーバーの起動

Claude AIなどのツールと連携するためのMCPサーバーを起動:

```bash
# 環境変数でInpit SQLite APIのURLを指定（オプション）
export INPIT_API_URL=http://localhost:5001

# MCPサーバーの起動
python -m app.patent_system.mcp_patent_server
```

実行例:
```
2025-04-30 13:25:50,989 - app.patent_system.inpit_sqlite_connector - INFO - Initialized Inpit SQLite connector with URL: http://localhost:5001
...
```

### 4. データアクセス機能の直接利用

コマンドラインからデータにアクセス:

```bash
python -m app.patent_system.data_importer
```

実行例:
```
Successfully connected to Inpit SQLite API
Database contains 17396 records
API URL: http://localhost:5001
```

## ソースコード構成

下記はシステムの主要ファイルの行数統計です:

| ファイル名                   | 合計行数 | コード行数（推定） | コメント行数（推定） | 空白行数（推定） |
|------------------------------|----------|-------------------|---------------------|-----------------|
| init_db.py                   | 56       | 38                | 10                  | 8               |
| inpit_sqlite_connector.py    | 231      | 175               | 36                  | 20              |
| patent_analyzer_inpit.py     | 714      | 540               | 105                 | 69              |
| data_importer.py             | 182      | 140               | 28                  | 14              |
| mcp_patent_server.py         | 452      | 365               | 50                  | 37              |
| models_sqlite.py             | 178      | 135               | 28                  | 15              |
| **合計**                     | **1813** | **1393**          | **257**             | **163**         |

## 主要ファイルの役割

- **init_db.py**: データベース構造初期化スクリプト
- **inpit_sqlite_connector.py**: Inpit SQLite APIとの接続とデータ取得を管理
- **patent_analyzer_inpit.py**: 特許データの分析機能を提供
- **data_importer.py**: データアクセス機能（直接APIから取得）
- **mcp_patent_server.py**: MCP統合サーバー（Claude AIなどと連携）
- **models_sqlite.py**: ローカルデータベースのモデル定義

## API機能一覧

MCPサーバーを通じて以下の機能が利用可能:

1. **query_patents**: 出願番号による特許検索
2. **search_patents_by_applicant**: 出願人名による特許検索
3. **execute_sql_query**: カスタムSQLクエリによるデータ取得
4. **analyze_technology_trends**: 技術トレンド分析
5. **analyze_applicant_competition**: 出願人競合分析
6. **analyze_patent_landscape**: 特許ランドスケープ分析
7. **generate_analysis_report**: 包括的な分析レポート生成

## 使用例

### Pythonコードからの利用例:

```python
from app.patent_system.inpit_sqlite_connector import get_connector
from app.patent_system.patent_analyzer_inpit import PatentAnalyzerInpit

# コネクタの初期化
connector = get_connector("http://localhost:5001")

# 特定の出願番号で特許を検索
result = connector.get_patent_by_application_number("特願2020-123456")
print(f"Found {len(result.get('results', []))} patents")

# アナライザーの初期化と分析の実行
analyzer = PatentAnalyzerInpit("http://localhost:5001")
trends = analyzer.analyze_technology_trends(years=5, top_n=10)
print(f"Analyzed {len(trends.get('top_technologies', []))} technology trends")
```

### SQLクエリ例:

```sql
-- 最近5年間の出願数の推移
SELECT
  SUBSTR(出願日, 1, 4) AS year,
  COUNT(*) AS patent_count
FROM inpit_data
WHERE 出願日 IS NOT NULL
GROUP BY year
ORDER BY year DESC
LIMIT 5;

-- 特定の技術分野（例：AIに関連する）の特許検索
SELECT
  出願番号,
  発明の名称,
  出願人,
  出願日
FROM inpit_data
WHERE 技術概要 LIKE '%人工知能%' OR 技術概要 LIKE '%AI%'
ORDER BY 出願日 DESC
LIMIT 10;
```

## 制限事項と注意点

- このシステムはInpit SQLite APIが正常に動作している環境が必要です
- データ取得はAPIの制約に依存します
- 一度に大量のデータを取得すると、パフォーマンスに影響する可能性があります

## トラブルシューティング

- **API接続エラー**: Inpit SQLiteサービスが実行中で、指定したURLで利用可能であることを確認してください
- **データ取得エラー**: API接続のタイムアウト値を調整するか、より小さなデータセットで再試行してください
- **分析エラー**: SQLクエリ内のカラム名が実際のデータベーススキーマと一致していることを確認してください

## ライセンス

Copyright (C) 2025
