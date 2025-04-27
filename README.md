# AWS特許分析・GraphRAGシステム

このリポジトリはAWS環境で動作する特許分析システムとGraphRAG（検索拡張生成）機能を提供するコンテナリポジトリです。

## 主要コンポーネント

### 1. 特許分析システム (`app/patent_system/`)

J-PlatPatの特許データを軽量RDBに格納し、AWS Bedrockを利用して自然言語による検索を実現するシステムです。SQLiteデータベースを使用した実装も提供しています。

- **機能**:
  - 特許出願情報の構造化保存
  - J-PlatPatからのデータスクレイピング
  - PDFからのテキスト抽出
  - 特許分析・レポート生成
  - 技術トレンド分析、出願者競争分析、特許ランドスケープ分析
  - マークダウンレポート生成

- **主要ファイル**:
  - `models.py` - データベースモデル
  - `models_sqlite.py` - SQLiteデータベースのモデル定義とSession管理
  - `db_manager.py` - データベース操作
  - `db_sqlite.py` - SQLiteデータベース操作
  - `j_platpat_scraper.py` - J-PlatPatスクレイパー
  - `jplatpat_scraper.py` - J-PlatPat向けスクレイパー実装
  - `patent_analyzer.py` - 特許分析機能
  - `patent_analyzer_sqlite.py` - SQLite向け特許分析機能
  - `mock_analyzer.py` - 分析機能のモック
  - `demo_analysis.py` - デモ分析機能
  - `demo_jplatpat.py` - J-PlatPat連携コマンドラインツール
  - `sql_query_tool.py` - SQLデータベース検索コマンドラインツール
  - `sql_web_interface.py` - SQLデータベース検索Webインターフェース
  - `README_SQL_TOOLS.md` - SQLツールの使用方法ドキュメント

### 2. GraphRAGシステム (`app/graphRAG/`)

Neo4jグラフデータベースを活用したRAG（検索拡張生成）システムで、特許データや文書を効率的に検索・参照できます。

- **機能**:
  - Neo4jグラフデータベースとの統合
  - AWS Bedrock APIを活用した埋め込みベクトル生成
  - PDFやテキスト文書の解析とグラフ化
  - Streamlitによるチャットインターフェース

- **主要ファイル**:
  - `neo4j2GraphRAG.py` - Neo4jからGraphRAGへのデータ変換
  - `pdf_arg_bigdoc_graphRAG.py` - PDFドキュメントの解析
  - `langfuse/streamlit_chat_graph_langfuse_log_setting_files.py` - Streamlitチャットインターフェース

### 3. LangGraphシステム (`app/langgraph/`)

LangChainをベースにしたグラフRAGシステムの実装です。

- **主要ファイル**:
  - `langgraph_base.py` - LangGraphの基本実装
  - `4pdtlan/` - 特許データ向け実装

### 4. AWSテンプレート (`awstemplates/`)

AWS CloudFormationテンプレートを提供し、様々なコンポーネントのデプロイを自動化します。

- **主要テンプレート**:
  - `template-graphRAG.yaml` - GraphRAGシステムのデプロイ
  - `template-langfuse.yaml` - Langfuseモニタリングシステムのデプロイ
  - `template-VPC.yaml` - ネットワーク構成のセットアップ

### 5. コンテナ構成 (`container/`)

Docker関連の設定を提供し、コンテナ化されたデプロイをサポートします。

- **主要コンポーネント**:
  - `docker-compose.yml` - 複数コンテナの構成
  - `amazonlinux-python/` - Amazonlinux Pythonベースイメージ
  - `python3.12-awscli/` - Python 3.12 + AWS CLI環境
  - `langfuse/` - Langfuseモニタリングコンテナ

## セットアップと実行方法

### 必要条件

- Docker と Docker Compose
- AWS アカウントとアクセス権限
- Python 3.9+
- Neo4j (GraphRAG機能を使用する場合)

### 環境変数の設定

```bash
# AWS認証情報
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region

# Neo4j接続情報（GraphRAG用）
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=your_password
export NEO4J_URL=bolt://neo4jRAG:7687

# Langfuse（オプション）
export LANGFUSE_PUBLIC_KEY=your_public_key
export LANGFUSE_SECRET_KEY=your_secret_key
export LANGFUSE_HOST=your_host
```

### 特許分析システムのセットアップ

```bash
cd app/patent_system
pip install -r requirements.txt
python init_and_demo.py
```

### GraphRAGシステムの実行

```bash
cd app/graphRAG
pip install -r requierment.txt

# Neo4jにデータをロード
python neo4j2GraphRAG.py

# Streamlitインターフェースを起動
cd langfuse
streamlit run streamlit_chat_graph_langfuse_log_setting_files.py
```

### AWSへのデプロイ

```bash
# VPCの作成
aws cloudformation create-stack --stack-name vpc-stack --template-body file://awstemplates/template-VPC.yaml

# GraphRAGシステムのデプロイ
aws cloudformation create-stack --stack-name graphrag-stack --template-body file://awstemplates/template-graphRAG.yaml --parameters ParameterKey=VpcId,ParameterValue=vpc-xxxxx
```

## 機能拡張

このシステムは以下の機能拡張が計画されています：

1. 特許分析機能の強化（技術トレンド分析、競合分析）
2. 複数言語対応（英語、中国語など）
3. リアルタイム更新機能
4. より高度なグラフ分析アルゴリズムの追加

## ライセンス

このプロジェクトはLICENSEファイルに定義された条件の下で提供されています。
