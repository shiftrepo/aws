# patentDWH 強化版LangChain機能の使用ガイド

## 概要

この拡張機能により、patentDWHシステムで自然言語クエリを処理する際に、LangChainを優先的に使用するオプションが追加されました。これにより、従来のBedrockによるSQL生成とは異なるアプローチでSQLクエリを生成できるため、特定のタイプのクエリでより良い結果が得られる可能性があります。

## 主な機能

1. **LangChain優先モード**: 自然言語クエリからSQLを生成する際に、LangChainを最初に試すオプションが追加されました。
2. **3段階のフォールバックメカニズム**: 
   - オリジナルのSQL生成メソッド
   - Bedrockによる直接フォールバック（patched_nl_query_processorで実装）
   - LangChainによるフォールバック（最後の手段として）
3. **詳細なフラグ**: レスポンスには以下のフラグが含まれ、どの方法が使用されたかを示します:
   - `used_langchain`: LangChainが使用された場合はtrue
   - `used_fallback`: Bedrockによる直接フォールバックが使用された場合はtrue
4. **コンテナ対応**: すべての機能はコンテナ内で実行され、スタンドアロンの環境でも使用可能です

## 使用方法

### コンテナ化された強化版サービスの起動

強化版LangChain機能を使用するには、新しいコンテナセットアップスクリプトを使用します:

```bash
# AWS認証情報を設定
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# セットアップスクリプトを実行（コンテナをビルドして起動）
./patentDWH/setup_enhanced_container.sh
```

### API呼び出し例

#### LangChainを優先的に使用する自然言語クエリ

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2020年以降に出願された人工知能に関する特許で、外国企業が出願人になっているものを教えてください",
    "db_type": "inpit",
    "use_langchain_first": true
  }' | jq
```

#### MCP APIでのLangChain優先使用

```bash
curl -X POST http://localhost:8080/api/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "patent_nl_query",
    "tool_input": {
      "query": "再生可能エネルギーに関する特許で、日本と米国の両方で出願されているものを探してください",
      "db_type": "google_patents_gcp",
      "use_langchain_first": true
    }
  }' | jq
```

### 標準セットアップからの切り替え

すでに標準セットアップを使用している場合は、まず既存のコンテナを停止してから強化版コンテナを起動します：

```bash
# 標準コンテナを停止
cd patentDWH
podman-compose down  # または docker compose down

# 強化版コンテナを起動
./patentDWH/setup_enhanced_container.sh
```

## レスポンス例

LangChainを最初に使用した場合のレスポンス例:

```json
{
  "success": true,
  "query": "2020年以降に出願された人工知能に関する特許で、外国企業が出願人になっているものを教えてください",
  "sql": "SELECT * FROM inpit_data WHERE application_date >= '2020-01-01' AND (title LIKE '%人工知能%' OR title LIKE '%AI%' OR title LIKE '%機械学習%') AND applicant_name NOT LIKE '%株式会社%' AND applicant_name NOT LIKE '%有限会社%' ORDER BY application_date DESC LIMIT 50;",
  "db_type": "inpit",
  "sql_result": {
    "columns": ["id", "application_number", "application_date", "title", "abstract", "applicant_name", "inventor_name", "status"],
    "results": [
      ["12345", "2020-123456", "2020-04-15", "人工知能を用いた画像認識システム", "本発明は...", "ABC Technologies Inc.", "John Smith", "審査中"],
      ...
    ],
    "record_count": 28
  },
  "response": "2020年以降に出願された人工知能関連の特許で外国企業が出願人になっているものは28件あります。主な出願としては、ABC Technologies Inc.による「人工知能を用いた画像認識システム」（2020年4月15日出願）などがあります...",
  "used_langchain": true,
  "used_fallback": false
}
```

## ログの確認

コンテナのログを確認して処理状況をモニタリングできます:

```bash
# 強化版MCPサービスのログを確認
cd patentDWH
podman-compose -f docker-compose.enhanced.yml logs -f patentdwh-mcp-enhanced
```

ログには以下の情報が含まれます:
- SQL生成プロセスの詳細
- どのSQL生成方法が使用されたか（LangChain、オリジナル、フォールバック）
- エラーや警告メッセージ

## 使用するケース

以下のような場合にLangChainを優先的に使用すると効果的です:

1. **複雑なクエリ**:
   - 複数の条件が組み合わされている場合
   - グルーピングや集計を必要とする分析クエリ
   - テーブル結合を必要とする複雑なリレーション

2. **特殊な表現**:
   - あいまいな表現や専門用語を含む場合
   - 通常のSQL生成が難しい特殊な構文

3. **高度な分析**:
   - トレンド分析
   - 比較分析
   - 時系列データの処理

## SQL生成方法の選択ガイドライン

| クエリタイプ | 推奨方法 |
|------------|---------|
| 単純な検索条件 | デフォルト（`use_langchain_first: false`） |
| 複雑な分析 | LangChain優先（`use_langchain_first: true`） |
| テーブル結合が必要 | LangChain優先（`use_langchain_first: true`） |
| 大量のフィルター条件 | ケースバイケース（両方試す） |

## 注意事項

1. LangChainを優先的に使用すると、最初のクエリ生成に少し時間がかかる場合があります。
2. どちらの方法も失敗した場合、もう一方の方法が自動的に試行されるため、最適な結果が得られる可能性が高まります。
3. 処理結果は一時的な内部SQLiteデータベースを使用してスキーマ情報を提供しているため、実際のデータベースとは若干の違いがある場合があります。

## 実装の詳細

拡張機能は以下のファイルで実装されています:

1. **enhanced_nl_query_processor.py**: 
   - PatchedNLQueryProcessorを拡張
   - LangChainを使用したSQL生成機能を追加
   - 優先順位付きフォールバックメカニズムを実装

2. **server_with_enhanced_nl.py**:
   - 新しいAPIパラメータ `use_langchain_first` を追加
   - 拡張されたNLプロセッサーを使用
   - 既存のAPIとの互換性を維持

3. **Dockerfile.enhanced**:
   - LangChainとその依存関係を含むコンテナをビルド
   - コンテナ化された環境でサーバーを実行

4. **docker-compose.enhanced.yml**:
   - 強化版コンテナと必要なサービスを定義
   - 標準セットアップとは別の構成を提供

## トラブルシューティング

1. **コンテナが起動しない場合**：
   - AWS認証情報が正しく設定されていることを確認
   - ポートが他のプロセスによって使用されていないことを確認
   - セットアップスクリプト内のエラーメッセージを確認

2. **データベース接続エラー**：
   - データベースサービスが実行中であることを確認
   - `docker-compose.enhanced.yml`の設定を確認

3. **LangChainが機能しない場合**：
   - コンテナのログを確認して詳細なエラーメッセージを取得
   - AWS Bedrock APIへのアクセス権があることを確認

## フィードバックとカスタマイズ

特定のクエリパターンでどちらの方法がより良い結果を生成するかのフィードバックは、今後の改善に役立ちます。また、以下のファイルを編集することで、LangChainのプロンプトテンプレートをカスタマイズできます:

```python
# enhanced_nl_query_processor.py内のSQL生成プロンプト
sql_prompt = PromptTemplate(
    input_variables=["input", "table_info", "dialect"],
    template="""あなたは日本語の自然言語から正確なSQLクエリを生成する特許データベースの専門家です。
ユーザーからの質問に対して、適切なSQLクエリを生成してください。

### 使用するデータベースの情報 ###
SQLタイプ: {dialect}
テーブル情報:
{table_info}

### ユーザーからの質問 ###
{input}

### SQLクエリ ###
以下のSQLクエリを生成します:
"""
)
