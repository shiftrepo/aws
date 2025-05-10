# patentDWHにおけるSQL生成のためのLangChainフォールバック機能

## 概要

この実装では、主要なSQL生成手法が有効なSQLを生成しない場合にLangChainのDatabaseChainを使用するフォールバックメカニズムを追加しています。これにより、元のアプローチが失敗した場合でも、システムはLangChainの機能を利用して有効なSQLクエリを生成することができます。

## 動作の仕組み

1. 自然言語クエリが処理されると、システムはまず元のAWS Bedrock APIを使用したSQL生成方法を試みます。
2. この主要な方法が有効なSQLを生成しない場合（空または非SQL文字列を返す場合）、システムは自動的にLangChainのDatabaseChainにフォールバックします。
3. DatabaseChainは、ターゲットデータベースのスキーマを反映した一時的なSQLiteデータベースと、日本語クエリに最適化されたカスタムプロンプトテンプレートを使用します。
4. 結果には、フォールバックメカニズムが使用されたかどうかを示すフラグ（`used_langchain`）が含まれます。

## 実装の詳細

### 主要なコンポーネント

1. **一時的なデータベース作成**:
   - 各データベースタイプ（inpit、google_patents_gcp、google_patents_s3）に対して、同じスキーマを持つ一時的なSQLiteデータベースが作成されます。
   - 元のデータベースからのサンプルデータが含まれており、LangChainがデータ構造をより理解しやすくなっています。

2. **LangChainのセットアップ**:
   - アプリケーションの他の部分との一貫性を保つために、AWS Bedrockを介して同じClaude 3 Haikuモデルを使用しています。
   - 日本語クエリに最適化された、カスタムSQL生成プロンプトが使用されています。

3. **シームレスな統合**:
   - フォールバックメカニズムは完全に自動化され、ユーザーに透過的です。
   - APIインターフェイスは変更されておらず、既存のクライアントコードとの互換性が保たれています。

### ファイル構造

- `patched_nl_query_processor.py` - LangChainフォールバック機能を備えた拡張NLQueryProcessorクラスが含まれています
- `server.py` - すでにパッチを適用したプロセッサを使用するよう構成されています
- `requirements.txt` - LangChainの依存関係が追加されています

## 依存関係

LangChain統合には以下のパッケージが必要です：

```
langchain>=0.0.267
langchain-community>=0.0.5
sqlalchemy>=2.0.0
```

## 重要な修正点（2025年5月10日更新）

- SQLDatabaseChainは最新バージョンのLangChainでは`langchain.chains`から`langchain_community.chains`に移動されました
- インポート文を修正：`from langchain_community.chains import SQLDatabaseChain`

## 使用方法

APIの使用方法に変更は必要ありません。システムは主要なSQL生成方法の結果に基づいてLangChainフォールバックメカニズムを使用するかどうかを自動的に決定します。

LangChainフォールバックを使用したレスポンスの例：

```json
{
  "success": true,
  "query": "2020年以降に出願された人工知能関連の特許を表示して",
  "sql": "SELECT * FROM inpit_data WHERE application_date >= '2020-01-01' AND (title LIKE '%人工知能%' OR title LIKE '%AI%' OR title LIKE '%機械学習%') ORDER BY application_date DESC LIMIT 50;",
  "db_type": "inpit",
  "sql_result": { ... },
  "response": "2020年以降に出願された人工知能関連の特許は以下の通りです...",
  "used_langchain": true
}
```

## カスタマイズ方法

LangChainフォールバックメカニズムをカスタマイズする必要がある場合：

1. **SQL生成プロンプトを変更する**: `_setup_langchain()`メソッド内の`sql_prompt` PromptTemplateを編集します。
2. **フォールバック条件を変更する**: LangChainにフォールバックするタイミングを決定する`process_query()`内の条件を調整します。
3. **追加のデータベースタイプを追加する**: 新しいデータベースタイプをサポートするために`_setup_database_connections()`内のデータベース作成を拡張します。
