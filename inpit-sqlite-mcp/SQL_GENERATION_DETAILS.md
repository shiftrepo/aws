# 自然言語からSQLへの変換処理の詳細

このドキュメントでは、自然言語クエリからSQLクエリを生成するための具体的な処理の流れと実装箇所について説明します。

> **更新情報**: システムは現在、2種類の自然言語からSQLへの変換方法をサポートしています：
> 1. 従来の正規表現とルールベースのアプローチ
> 2. 新しいAWS Bedrock（Claude 3.7 SonnetとTitan Embeddings）を使用したNLtoSQL変換

## 処理の概要

### 方法1: ルールベースアプローチ

ルールベースの自然言語からSQLへの変換は以下のステップで行われます：

1. 自然言語クエリを受け取る
2. 正規表現とルールに基づいてパースし、条件を抽出
3. 抽出した条件からSQL WHERE句を構築
4. ソート順や制限数を決定してORDER BYやLIMIT句を追加
5. 最終的なSQLクエリを生成

### 方法2: AWS Bedrockを使用したLLMベースアプローチ

AWS Bedrockを利用した自然言語からSQLへの変換は以下のステップで行われます：

1. データベーススキーマ情報を抽出し、コンテキストとして保持
2. 自然言語クエリを受け取る
3. Claude 3.7 Sonnet LLMにスキーマ情報とクエリを送信
4. LLMがデータベース構造を理解した上でSQLクエリを生成
5. 生成されたSQLクエリをクリーンアップして実行
6. エラーが発生した場合、エラー情報をLLMにフィードバックして再生成を試みる

## 主要なコード実装箇所

### 1. INPIT SQLiteデータベース向けの処理

**ファイル**: `inpit-sqlite-mcp/app/inpit_nl_query_processor.py`

- **クラス**: `InpitNLQueryProcessor`
- **メソッド**: 
  - `process_query(query_text)`: 自然言語クエリからSQLへの変換のメインメソッド
  - `_extract_conditions(query_text)`: 自然言語クエリから検索条件を抽出するメソッド
  - `_generate_fallback_query(query_text)`: 主処理が失敗した場合のフォールバック処理

```python
def process_query(self, query_text: str) -> Dict[str, Any]:
    """
    自然言語クエリをSQLに変換
    
    Args:
        query_text: 自然言語クエリテキスト
            
    Returns:
        SQLクエリとメタデータを含む辞書
    """
    try:
        # クエリを正規化
        query_text = query_text.strip()
        
        # クエリからキーエンティティと条件を抽出
        table_name = "inpit_data"
        conditions, limit, order_by = self._extract_conditions(query_text)
        
        # SQLクエリを構築
        sql_query = f"SELECT * FROM {table_name}"
        
        # WHERE句の追加（条件がある場合）
        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        
        # ORDER BY句の追加
        if order_by:
            sql_query += f" ORDER BY {order_by}"
        
        # LIMIT句の追加
        sql_query += f" LIMIT {limit}"
        
        return {
            "natural_language_query": query_text,
            "sql_query": sql_query,
            "conditions": conditions,
            "order_by": order_by,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"クエリ処理エラー: {e}")
        return {
            "error": str(e),
            "natural_language_query": query_text,
            "sql_query": None
        }
```

### 2. 条件抽出の詳細実装

**ファイル**: `inpit-sqlite-mcp/app/inpit_nl_query_processor.py`

`_extract_conditions`メソッドは自然言語クエリから以下のような要素を抽出します：

1. **時間・日付の参照**:
   ```python
   year_pattern = r'\b(19|20)\d{2}\b'
   years = re.findall(year_pattern, query_text)
   # 年の前後の文脈を分析して、以前/以降などの条件を判断
   ```

2. **出願人/企業の参照**:
   ```python
   company_patterns = [
       r'(?:会社|企業|出願人|申請者)(?:は|が|の)「([^」]+)」', 
       r'(?:会社|企業|出願人|申請者)(?:は|が|の)([^\s,。]+)',
       # その他のパターン
   ]
   ```

3. **発明者の参照**:
   ```python
   inventor_patterns = [
       r'(?:発明者|考案者|inventor)(?:は|が|の)「([^」]+)」',
       r'(?:発明者|考案者|inventor)(?:は|が|の)([^\s,。]+)',
   ]
   ```

4. **IPC分類の参照**:
   ```python
   ipc_pattern = r'(?:IPC|分類)\s*[が|は|の]\s*([A-H]\d{2}[A-Z](?:\d{1,6})?(?:/\d{2,6})?)'
   ```

5. **技術分野キーワード**:
   ```python
   tech_terms = {
       "カメラ": ["カメラ", "撮影", "写真"],
       "camera": ["camera", "photograph", "image", "imaging"],
       # その他の技術分野
   }
   ```

6. **ソート順の参照**:
   ```python
   if any(term in query_lower for term in ["新しい", "最新", "newest", "latest", "recent"]):
       date_col = self.common_columns.get("出願日", "filing_date")
       order_by = f"{date_col} DESC"
   ```

### 3. Google Patents GCPデータベース向けの処理

**ファイル**: `inpit-sqlite-mcp/app/nl_query_processor.py`

- **クラス**: `PatentNLQueryProcessor`
- **メソッド**: 
  - `process_query(query_text)`: 自然言語クエリからSQLへの変換のメインメソッド
  - `_extract_conditions(query_text)`: 自然言語クエリから検索条件を抽出するメソッド

Google Patents向けのクエリ処理も基本的には同様のアプローチですが、データベースのスキーマの違いに合わせて条件抽出のパターンとカラム名が調整されています。

### 4. MCPサーバーとの統合

**ファイル**: `inpit-sqlite-mcp/app/nl_query_mcp.py`

- **メソッド**:
  - `_nl_query_inpit_database(arguments)`: INPIT DBへのNLクエリを処理
  - `_nl_query_google_patents_database(arguments)`: Google Patents DBへのNLクエリを処理

このファイルでは、MCPツールのインターフェースを提供し、適切なNLクエリプロセッサにクエリを渡して結果を整形します。

```python
def _nl_query_inpit_database(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    INPITデータベースに対して自然言語クエリを実行
    """
    query = arguments.get("query")
    if not query:
        return {"error": "query is required"}
    
    if not self.inpit_processor:
        return {
            "error": "INPIT database is not available",
            "detail": f"Database file not found at {INPIT_DB_PATH}"
        }
    
    try:
        # 自然言語クエリを処理して実行
        result = self.inpit_processor.process_and_execute(query)
        
        # レスポンスを拡張
        if result.get("success"):
            enhanced_result = {
                "success": True,
                "query": query,
                "sql_query": result.get("sql_query"),
                "count": result.get("count", 0),
                "results": result.get("results", [])[:20],
                "total_results": result.get("count", 0),
                "database": "INPIT SQLite (inpit.db)"
            }
            
            if result.get("count", 0) > 20:
                enhanced_result["note"] = f"Only showing 20 of {result.get('count')} total results"
            
            return enhanced_result
        else:
            return {
                "success": False,
                "query": query,
                "error": result.get("error", "Unknown error processing natural language query"),
                "database": "INPIT SQLite (inpit.db)"
            }
    except Exception as e:
        error_msg = f"Error processing natural language query: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
```

### 5. API統合

**ファイル**: `inpit-sqlite-mcp/app/server.py`

自然言語クエリのAPIエンドポイントを提供します：

```python
@app.post("/nl-query/inpit")
async def nl_query_inpit(request: fastapi.Request):
    """
    Execute a natural language query against the Inpit database.
    """
    try:
        # Get form data
        form_data = await request.form()
        query = form_data.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        args = {"query": query}
        result = execute_tool("nl_query_inpit_database", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing natural language query: {str(e)}")
```

## 処理フローの詳細

### ルールベースアプローチの処理フロー

1. **ユーザーがAPIエンドポイントに自然言語クエリを送信**
   - `/nl-query/inpit` または `/nl-query/google-patents` にPOST

2. **サーバー（server.py）がクエリを受け取りMCPツールを呼び出す**
   - `nl_query_inpit_database` または `nl_query_google_patents_database` ツールを実行

3. **MCPサーバー（nl_query_mcp.py）が対応するクエリプロセッサにクエリを渡す**
   - `InpitNLQueryProcessor` または `PatentNLQueryProcessor` のインスタンスを使用

4. **クエリプロセッサが自然言語をSQLに変換**
   - `process_query` メソッドを呼び出し
   - `_extract_conditions` でクエリ条件を抽出
   - SQLクエリを構築

5. **構築されたSQLクエリがデータベースに対して実行される**
   - `execute_query` メソッドがSQLiteクエリを実行

6. **結果がユーザーに返される**
   - 検索結果とメタデータ（使用されたSQLクエリなど）を含むJSON形式

このように、ルールベースの自然言語からSQLへの変換は`inpit_nl_query_processor.py`と`nl_query_processor.py`の中で主に行われ、正規表現によるパターンマッチングとルールベースの条件抽出を組み合わせて実現しています。

### AWS Bedrock LLMアプローチの処理フロー

1. **ユーザーがAPIエンドポイントに自然言語クエリを送信**
   - `/bedrock-nl-query/inpit` または `/bedrock-nl-query/google-patents` にPOST

2. **サーバー（server.py）がクエリを受け取りMCPツールを呼び出す**
   - `bedrock_nl_query_inpit_database` または `bedrock_nl_query_google_patents_database` ツールを実行

3. **MCPサーバー（bedrock_nl_query_mcp.py）が対応するクエリプロセッサにクエリを渡す**
   - `BedrockNLQueryProcessor` のインスタンスを使用

4. **データベーススキーマ情報をLLMのコンテキストとして用意**
   - 初期化時に自動的にデータベースから抽出されたスキーマ情報（テーブル、カラム、データ型など）

5. **BedrockのLLM（Claude 3.7 Sonnet）を使用して自然言語クエリからSQLを生成**
   - スキーマ情報とユーザーのクエリを含むプロンプトをLLMに送信
   - LLMがデータベース構造を理解した上で適切なSQLクエリを生成

6. **生成されたSQLクエリをクリーンアップ**
   - マークダウンフォーマットの除去などのクリーニング処理
   - SQLの構文要素（WHERE、ORDER BY、LIMIT）の抽出

7. **SQLクエリの実行と結果処理**
   - `execute_query` メソッドでSQLiteクエリを実行
   - クエリが失敗した場合、エラー情報をLLMにフィードバックし、修正されたクエリを再生成

8. **結果がユーザーに返される**
   - 検索結果とメタデータ（使用されたSQLクエリなど）を含むJSON形式

この新しいBedrock LLMアプローチでは、`bedrock_nl_query_processor.py`が中心となり、データベースのスキーマ情報を効果的に活用して、ルールベースのアプローチでは難しかった複雑な自然言語クエリに対応できるようになっています。

## AWS Bedrock実装の詳細

### 1. Bedrockを使用した自然言語クエリプロセッサ

**ファイル**: `inpit-sqlite-mcp/app/bedrock_nl_query_processor.py`

- **クラス**: `BedrockNLQueryProcessor`
- **主要メソッド**:
  - `__init__`: データベース接続とAWS Bedrockクライアントの初期化
  - `_get_schema_info`: データベースのスキーマ情報を抽出
  - `_generate_schema_context`: LLMのプロンプトのためのスキーマコンテキストを生成
  - `_invoke_bedrock_llm`: BedrockのClaudeモデルを呼び出してSQL生成
  - `process_query`: 自然言語クエリからSQLへの変換のメインメソッド
  - `_generate_robust_sql`: エラー時の再試行のためのロバストなSQL生成

```python
def process_query(self, query_text: str) -> Dict[str, Any]:
    """
    Process a natural language query and convert it to SQL using Bedrock
    
    Args:
        query_text: The natural language query text
        
    Returns:
        Dictionary containing the SQL query and metadata
    """
    try:
        # Normalize query
        query_text = query_text.strip()
        
        # Prepare system prompt with schema context
        system_prompt = f"""You are a helpful SQL assistant that converts natural language questions to SQL queries. 
You are connected to a database with the following schema:

{self.schema_context}

Given a natural language query, your task is to convert it into a valid SQL query that will retrieve the requested information.
Only return the SQL query, with no additional explanation or comments."""

        # Prepare user query
        user_query = f"Generate an SQL query for the following question: {query_text}"
        
        # Call LLM to generate SQL
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        sql_query = self._invoke_bedrock_llm(messages)
        
        # Clean up the generated SQL
        sql_query = self._clean_sql_query(sql_query)
        
        return {
            "natural_language_query": query_text,
            "sql_query": sql_query,
            "conditions": self._parse_sql_components(sql_query)[0],
            "order_by": self._parse_sql_components(sql_query)[2],
            "limit": self._parse_sql_components(sql_query)[1]
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "error": str(e),
            "natural_language_query": query_text,
            "sql_query": None
        }
```

### 2. Bedrock NL Query MCP統合

**ファイル**: `inpit-sqlite-mcp/app/bedrock_nl_query_mcp.py`

- **クラス**: `BedrockNLQueryMCPServer`
- **主要メソッド**:
  - `__init__`: BedrockNLQueryProcessorインスタンスの初期化
  - `get_tools`: 提供するMCPツールのリストを返す
  - `get_resources`: 提供するMCPリソースのリストを返す
  - `_bedrock_nl_query_inpit_database`: INPIT DBへの問い合わせを処理
  - `_bedrock_nl_query_google_patents_database`: Google Patents DBへの問い合わせを処理

```python
def _bedrock_nl_query_inpit_database(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query the Inpit database using natural language with Bedrock
    
    Args:
        arguments: Arguments containing the natural language query
        
    Returns:
        Query results
    """
    query = arguments.get("query")
    if not query:
        return {"error": "query is required"}
    
    if not self.inpit_processor:
        return {
            "error": "INPIT database is not available",
            "detail": f"Database file not found at {INPIT_DB_PATH}"
        }
    
    try:
        result = self.inpit_processor.process_and_execute(query)
        
        # Enhance the response with additional information
        if result.get("success"):
            enhanced_result = {
                "success": True,
                "query": query,
                "sql_query": result.get("sql_query"),
                "count": result.get("count", 0),
                "results": result.get("results", [])[:20],
                "total_results": result.get("count", 0),
                "database": "INPIT SQLite (inpit.db)",
                "model": MODEL_ID
            }
            
            # If there are more than 20 results, note that some are omitted
            if result.get("count", 0) > 20:
                enhanced_result["note"] = f"Only showing 20 of {result.get('count')} total results"
            
            return enhanced_result
        else:
            return {
                "success": False,
                "query": query,
                "error": result.get("error", "Unknown error processing natural language query"),
                "database": "INPIT SQLite (inpit.db)"
            }
    except Exception as e:
        error_msg = f"Error processing natural language query: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
```

### 3. FastAPI エンドポイント

**ファイル**: `inpit-sqlite-mcp/app/server.py`

- Bedrockを使用した自然言語クエリのためのAPIエンドポイントを提供します:

```python
@app.post("/bedrock-nl-query/inpit")
async def bedrock_nl_query_inpit(request: fastapi.Request):
    """
    Execute a natural language query against the Inpit database using AWS Bedrock.
    
    Form data:
    - query: The natural language query text
    """
    try:
        # Get form data
        form_data = await request.form()
        query = form_data.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        args = {"query": query}
        result = execute_tool("bedrock_nl_query_inpit_database", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing Bedrock natural language query: {str(e)}")
```

## 2つのアプローチの比較

| 機能 | ルールベースアプローチ | AWS Bedrock LLMアプローチ |
|------|-------------------|--------------------------|
| 実装の複雑さ | 多数の正規表現と条件分岐 | スキーマ情報とLLMプロンプトのみ |
| 対応言語 | 主に日本語と英語の特定パターン | 日本語と英語の両方に幅広く対応 |
| クエリの複雑さ | 単純な条件のみ対応 | 複雑な条件や結合クエリにも対応可能 |
| エラーハンドリング | フォールバック用の単純なクエリ生成 | エラー情報をLLMに渡して修正案を生成 |
| データベーススキーマ適応 | 手動でコード修正が必要 | スキーマを自動抽出して適応 |
| 実行コスト | 低コスト（計算リソースのみ） | 中～高コスト（AWS Bedrock API料金発生） |

## 使用方法

### ルールベース自然言語クエリ

```bash
curl -X POST "http://localhost:8000/nl-query/inpit" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=トヨタの自動車関連の特許を5件見せて"
```

### AWS Bedrock自然言語クエリ

```bash
curl -X POST "http://localhost:8000/bedrock-nl-query/inpit" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=トヨタの自動車関連の特許を5件見せて"
```

## まとめ

このシステムでは、2つの異なるアプローチで自然言語からSQLへの変換を提供しています：

1. **ルールベースアプローチ**: 正規表現と条件抽出を使用した従来のアプローチで、特定のパターンに対しては高速かつ低コストで結果を提供します。

2. **AWS Bedrock LLMアプローチ**: AWS BedrockのClaude 3.7 SonnetとTitan Embeddingsを利用した最新のアプローチで、データベーススキーマを自動的に理解し、複雑なクエリに対応できます。特に、ユーザーが自由な形式で質問できる柔軟性が大きな利点です。

実際の使用においては、単純なクエリには従来のルールベースアプローチを、複雑なクエリやスキーマ依存の質問にはAWS Bedrockアプローチを使い分けることで、コストパフォーマンスとユーザー体験のバランスを最適化できます。
