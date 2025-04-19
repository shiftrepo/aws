import json
import boto3
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, State

# データベーススキーマ定義
DB_SCHEMA = """
テーブル: sales
  - id (integer, primary key)
  - date (date)
  - product_id (integer, foreign key)
  - customer_id (integer, foreign key)
  - quantity (integer)
  - unit_price (decimal)
  - total_price (decimal)

テーブル: products
  - id (integer, primary key)
  - name (varchar)
  - category (varchar)
  - subcategory (varchar)
  - cost (decimal)

テーブル: customers
  - id (integer, primary key)
  - name (varchar)
  - segment (varchar)
  - region (varchar)
  - join_date (date)
"""

# 状態の型定義
class GraphState(TypedDict):
    user_request: str
    db_schema: str
    generated_sql: str
    query_result: str
    final_report: str
    error: str

# AWS Bedrock クライアントの設定
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"  # 適切なリージョンに変更
)

# データベース接続設定
def get_db_connection():
    # 実際の接続情報に置き換え
    return create_engine("postgresql://username:password@localhost:5432/analytics_db")

# Bedrock APIを使用してClaudeモデルを呼び出す関数
def invoke_bedrock_model(prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229") -> str:
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

# ノード1: SQLクエリ生成
def generate_sql(state: GraphState) -> GraphState:
    try:
        prompt = f"""
        あなたはSQLエキスパートです。以下のデータベース構造に基づいて、
        ユーザーのリクエストを満たすSQLクエリを作成してください。

        {state["db_schema"]}
        
        ユーザーリクエスト: {state["user_request"]}
        
        SQLクエリのみを返してください。コードブロック、説明、追加コメントは不要です。
        """
        
        sql_query = invoke_bedrock_model(prompt)
        
        # SQLコメントや余分なマークダウン記号を削除
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1]
        if sql_query.endswith("```"):
            sql_query = sql_query.rsplit("```", 1)[0]
        sql_query = sql_query.strip()
        
        # 行ごとの処理
        lines = sql_query.split('\n')
        clean_lines = []
        for line in lines:
            # コメント行や不要な行を除外
            if not line.strip().startswith('--') and line.strip():
                clean_lines.append(line)
        
        clean_sql = '\n'.join(clean_lines)
        
        return {"generated_sql": clean_sql, **state}
    except Exception as e:
        return {"error": f"SQL生成エラー: {str(e)}", **state}

# ノード2: SQLクエリ実行
def execute_sql(state: GraphState) -> GraphState:
    if state.get("error"):
        return state
    
    try:
        engine = get_db_connection()
        df = pd.read_sql(state["generated_sql"], engine)
        csv_data = df.to_csv(index=False)
        return {"query_result": csv_data, **state}
    except Exception as e:
        return {"error": f"SQL実行エラー: {str(e)}", **state}

# ノード3: レポート生成
def generate_report(state: GraphState) -> GraphState:
    if state.get("error"):
        return state
    
    try:
        prompt = f"""
        以下のデータは「{state["user_request"]}」という依頼に基づいて取得された結果です。
        このデータを分析し、重要なインサイトを含む包括的なビジネスレポートを作成してください。
        
        データ:
        ```csv
        {state["query_result"]}
        ```
        
        マークダウン形式で読みやすく構造化されたレポートを作成してください。
        適切な見出し、箇条書き、そして必要に応じて簡潔な説明を含めてください。
        """
        
        report = invoke_bedrock_model(prompt)
        state["final_report"] = report
        
        return state
    except Exception as e:
        return {"error": f"レポート生成エラー: {str(e)}", **state}

# エラーハンドリングノード
def handle_error(state: GraphState) -> GraphState:
    error_message = state.get("error", "不明なエラーが発生しました")
    
    prompt = f"""
    以下のエラーが発生しました:
    
    {error_message}
    
    このエラーについて以下の内容を含む説明を作成してください:
    1. エラーの考えられる原因
    2. 修正するための提案
    3. ユーザーへのアドバイス
    
    ユーザーリクエスト: {state["user_request"]}
    """
    
    error_report = invoke_bedrock_model(prompt)
    
    return {"final_report": f"## エラーレポート\n\n{error_report}", **state}

# 決定ノード: エラーがあるかどうかを確認
def check_for_errors(state: GraphState) -> str:
    if state.get("error"):
        return "error"
    return "continue"

# グラフの構築
workflow = StateGraph(GraphState)

# ノードを追加
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_report", generate_report)
workflow.add_node("handle_error", handle_error)

# エッジを定義
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_report")
workflow.add_edge("generate_report", "END")
workflow.add_edge("handle_error", "END")

# 条件付きエッジを追加
workflow.add_conditional_edges(
    "generate_sql",
    check_for_errors,
    {
        "continue": "execute_sql",
        "error": "handle_error"
    }
)

workflow.add_conditional_edges(
    "execute_sql",
    check_for_errors,
    {
        "continue": "generate_report",
        "error": "handle_error"
    }
)

# グラフをコンパイル
app = workflow.compile()

# 使用例
def run_report_workflow(user_request: str) -> Dict[str, Any]:
    # 初期状態を設定
    initial_state = {
        "user_request": user_request,
        "db_schema": DB_SCHEMA,
        "generated_sql": "",
        "query_result": "",
        "final_report": "",
        "error": ""
    }
    
    # ワークフローを実行
    result = app.invoke(initial_state)
    return result

# 実行例
if __name__ == "__main__":
    request = "過去3ヶ月間の製品カテゴリ別の売上推移と、最も成長率の高いカテゴリTOP3を特定してください。"
    result = run_report_workflow(request)
    
    print("=== 最終レポート ===")
    if result.get("error"):
        print(f"エラー: {result['error']}")
    else:
        print("生成されたSQL:")
        print("-------------")
        print(result["generated_sql"])
        print("\nレポート:")
        print("--------")
        print(result["final_report"])
        
        # レポートをファイルに保存
        with open("analysis_report.md", "w") as f:
            f.write(result["final_report"])
