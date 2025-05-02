# 特許データ分析システム (Patent Analysis System)

このシステムは、特許データの高度な分析と可視化を行うための総合的なツールセットです。複数のコンテナとアプリケーションを組み合わせて、さまざまな特許分析機能を提供します。

## システム概要

特許データ分析システムは、複数のコンポーネントで構成され、各コンポーネントが特定の役割を果たしています。データの取得・保存から分析、レポート生成まで、特許データを効果的に活用するための総合的なソリューションです。

## コンテナとアプリケーション構成

システムは以下の主要なコンテナとアプリケーションで構成されています：

### 1. データソースコンテナ

#### Inpit SQLiteコンテナ (`container/inpit-sqlite/`)
- **機能**: 特許データを保存・提供するSQLiteデータベースサービス
- **エンドポイント**: http://localhost:5001
- **主な機能**:
  - 特許データのAPI提供
  - SQLクエリによるデータアクセス
- **起動方法**:
  ```bash
  cd container/inpit-sqlite/
  docker-compose up -d
  ```

#### JPLATPATコンテナ (`container/jplatpat/`)
- **機能**: 日本特許情報プラットフォームからのデータアクセス
- **主な機能**:
  - 特許データの外部取得と変換
  - SQLクエリツールの提供
- **起動方法**:
  ```bash
  cd container/jplatpat/
  docker-compose up -d
  ```

### 2. MCPサーバー

#### Inpit SQLite MCP サーバー (`inpit-sqlite-mcp/`)
- **機能**: SQLiteデータベースAPIをClaudeなどのAIツールに接続
- **エンドポイント**: http://localhost:8000
- **提供ツール**:
  - 出願番号による特許検索
  - 出願人名による特許検索
  - SQLクエリ実行
- **起動方法**:
  ```bash
  cd inpit-sqlite-mcp/
  ./start_server.sh
  ```

#### Patent MCP サーバー (`patent-mcp-server/`)
- **機能**: 高度な特許分析機能をMCPプロトコル経由で提供
- **エンドポイント**: http://localhost:8000
- **提供ツール**:
  - 出願人サマリー生成
  - 視覚的レポート作成
  - 競合他社比較分析
  - 技術分野分析
- **起動方法**:
  ```bash
  cd patent-mcp-server/
  ./start_server.sh
  ```

### 3. 分析アプリケーション

#### GraphRAG システム (`app/graphRAG/`)
- **機能**: グラフベースのRAG（検索拡張生成）システム
- **主な機能**:
  - Neo4jデータベースとの連携
  - 特許文書の意味的検索
  - PDFドキュメント分析

#### Langgraph システム (`app/langgraph/`)
- **機能**: LangChainベースのグラフフロー処理
- **主な機能**:
  - 特許分析ワークフローの自動化
  - ドキュメント処理
  - Langfuse統合による分析ログ

#### 特許分析システム (`app/patent_system/`)
- **機能**: コアとなる特許データ分析システム
- **主要コンポーネント**:
  - `init_db.py`: データベース構造初期化
  - `inpit_sqlite_connector.py`: データ取得・接続管理
  - `patent_analyzer_inpit.py`: 特許データ分析エンジン
  - `mcp_patent_server.py`: MCP統合サーバー

### 4. 補助コンテナとツール

#### Amazonlinux-Python (`container/amazonlinux-python/`)
- **機能**: Amazon Linux環境でのPython実行環境

#### Python3.12-AWSCLI (`container/python3.12-awscli/`)
- **機能**: Python 3.12とAWS CLIを含む実行環境

#### Langfuse (`container/langfuse/`)
- **機能**: LLMアプリケーションのモニタリングと分析

#### Gemma3 (`container/gemma3/`)
- **機能**: Gemmaモデル実行環境

#### Bedrock MCP サーバー (`bedrock-mcp-server/`)
- **機能**: AWS Bedrockサービス連携用MCPサーバー

## 主要機能

- **特許データのクエリと取得**: 出願番号、出願人名、SQLクエリなどによる特許データの検索
- **技術トレンド分析**: 国際特許分類（IPC）に基づく技術トレンドの時系列分析
- **出願人競合分析**: 主要出願者の特許活動と技術的な重複の分析
- **特許ランドスケープ可視化**: 技術領域の広がりと集中度の分析
- **包括的レポート生成**: Markdown形式の詳細な分析レポート作成
- **MCP統合**: Claude AIなどのツールとの連携機能
- **グラフベース分析**: Neo4jを活用した特許関係の視覚化と分析
- **AWS連携**: Amazon BedrockやAWS CLIとの連携機能

## 前提条件

- Python 3.8以上
- Docker および Docker Compose
- 必要なPythonパッケージ（各コンポーネントのrequirements.txt参照）
- MCP統合を使用する場合はClaude拡張機能など
- AWS連携機能を使用する場合はAWSアカウントとアクセス権限

## インストール方法

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/patent-analysis-system.git
cd patent-analysis-system
```

2. 使用するコンポーネントに応じて必要なサービスを起動（以下は例）:

```bash
# Inpit SQLiteサービスの起動
cd container/inpit-sqlite/
docker-compose up -d

# Inpit SQLite MCPサーバーの起動
cd inpit-sqlite-mcp/
./start_server.sh
```

## 実行方法

### 1. データベース構造の初期化

最初に、ローカルSQLiteデータベースの構造を初期化します:

```bash
python -m app.patent_system.init_db
```

#### オプション:
- `--skip-init`: データベース初期化をスキップ
- `--api-url URL`: Inpit SQLite APIのURLを指定（デフォルト: http://localhost:5001）

### 2. 特許データの分析

直接Inpit SQLiteデータを使用した分析を実行:

```bash
python -m app.patent_system.patent_analyzer_inpit
```

### 3. MCPサーバーの起動

Claude AIなどのツールと連携するためのMCPサーバーを起動:

```bash
# 環境変数でInpit SQLite APIのURLを指定（オプション）
export INPIT_API_URL=http://localhost:5001

# MCPサーバーの起動
python -m app.patent_system.mcp_patent_server
```

### 4. データアクセス機能の直接利用

コマンドラインからデータにアクセス:

```bash
python -m app.patent_system.data_importer
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

## API機能一覧

MCPサーバーを通じて以下の機能が利用可能:

### Inpit SQLite MCP サーバー

1. **query_patents**: 出願番号による特許検索
2. **search_patents_by_applicant**: 出願人名による特許検索
3. **execute_sql_query**: カスタムSQLクエリによるデータ取得

### Patent MCP サーバー

1. **get_applicant_summary**: 出願人の包括的なサマリーを取得
2. **generate_visual_report**: 出願人の視覚的レポートを生成
3. **analyze_examination_ratio**: 出願人の審査比率を分析
4. **analyze_technical_fields**: 出願人の技術分野を分析
5. **compare_with_competitors**: 出願人を競合他社と比較

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

- このシステムは各種コンテナサービスが正常に動作している環境が必要です
- 日本語などの非ASCII文字をAPIで使用する場合は、適切なURLエンコーディングが必要です
- 一度に大量のデータを取得すると、パフォーマンスに影響する可能性があります

## トラブルシューティング

- **API接続エラー**: 各種サービスが実行中で、指定したURLで利用可能であることを確認してください
- **データ取得エラー**: API接続のタイムアウト値を調整するか、より小さなデータセットで再試行してください
- **分析エラー**: SQLクエリ内のカラム名が実際のデータベーススキーマと一致していることを確認してください
- **URLエンコーディングエラー**: 日本語などの非ASCII文字をAPIで使用する場合は、適切にURLエンコードしてください

## ライセンス

Copyright (C) 2025
