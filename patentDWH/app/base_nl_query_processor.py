#!/usr/bin/env python3
"""
Base Natural Language Query Processor for patentDWH

This module provides the basic NLQueryProcessor functionality that other modules extend.
"""

import os
import json
import logging
import boto3
from typing import Dict, List, Any, Optional
import httpx

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Bedrock settings
CLAUDE_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Patent DB API URL from environment variable
PATENT_DB_URL = os.environ.get("PATENT_DB_URL", "http://patentdwh-db:5002")

class NLQueryProcessor:
    """
    Base Natural Language Query Processor for patentDWH
    
    This class provides the original NL query processing functionality.
    """

    def __init__(self):
        """Initialize the NL query processor."""
        self.bedrock_runtime = None
        self.schemas = {}
        self.is_aws_configured = False
        
        # Setup AWS Bedrock client
        self._setup_bedrock()
        
        # Load database schemas
        self.schemas = self._get_database_schemas()
        
    def _setup_bedrock(self):
        """Setup AWS Bedrock client."""
        try:
            # Check for AWS credentials
            aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
            aws_region = os.environ.get("AWS_DEFAULT_REGION")
            
            if not aws_access_key_id or not aws_secret_access_key or not aws_region:
                logger.warning("AWS credentials or region not set")
                self.is_aws_configured = False
                return
                
            # Log AWS credentials found (but don't log the actual values)
            logger.info("Found credentials in environment variables.")
            
            # Initialize Bedrock client
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime", 
                region_name=aws_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            
            self.is_aws_configured = True
            logger.info("Successfully initialized AWS Bedrock client")
            
        except Exception as e:
            logger.error(f"Error setting up Bedrock client: {e}")
            self.is_aws_configured = False
    
    def _get_database_schemas(self):
        """Get database schema information for all databases."""
        schemas = {}
        db_types = ["inpit", "google_patents_gcp", "google_patents_s3"]
        
        # Retry mechanism for network issues
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get schema info for each database
                for db_type in db_types:
                    try:
                        response = httpx.get(f"{PATENT_DB_URL}/api/status")
                        if response.status_code == 200:
                            db_info = response.json().get("databases", {}).get(db_type, {})
                            
                            if "tables" in db_info:
                                schemas[db_type] = {
                                    "tables": {}
                                }
                                
                                # Execute SQL queries to get table columns
                                for table_name in db_info.get("tables", []):
                                    table_query = f"PRAGMA table_info({table_name})"
                                    response = httpx.post(
                                        f"{PATENT_DB_URL}/api/sql-query",
                                        json={"query": table_query, "db_type": db_type}
                                    )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        columns = [row[1] for row in result.get("results", [])]
                                        
                                        schemas[db_type]["tables"][table_name] = {
                                            "columns": columns
                                        }
                    except Exception as db_error:
                        logger.warning(f"Error getting schema for {db_type}: {db_error}")
                
                # If we have at least some schema information, break out of the retry loop
                if schemas:
                    break
                    
            except Exception as e:
                retry_count += 1
                logger.warning(f"Error retrieving database schemas (attempt {retry_count}/{max_retries}): {e}")
                
                # Wait before retrying
                import time
                time.sleep(3)
        
        return schemas
    
    async def _generate_sql(self, query: str, db_type: str) -> str:
        """
        Generate SQL from a natural language query.
        
        Args:
            query: Natural language query
            db_type: Database type
            
        Returns:
            Generated SQL query
        """
        try:
            if not self.is_aws_configured or not self.bedrock_runtime:
                logger.error("Bedrock client not available")
                return ""
            
            # Get schema information for this database type
            schema_info = self.schemas.get(db_type, {})
            
            # Format schema information for the prompt
            schema_text = "テーブル一覧:\n"
            for table_name, table_info in schema_info.get("tables", {}).items():
                columns = table_info.get("columns", [])
                if not columns:
                    continue
                
                schema_text += f"\nテーブル: {table_name}\n"
                schema_text += "カラム:\n"
                for col in columns:
                    schema_text += f"- {col}\n"
            
            # Create a prompt for SQL generation
            prompt = f"""あなたは特許データベースのSQLクエリ生成の専門家です。
次のSQL問い合わせを生成してください。

### データベースの種類: SQLite

### データベーススキーマ情報:
{schema_text}

### 質問:
{query}

### 応答:
SQLクエリのみを出力してください。説明は不要です。バックティック(```)やSQL識別子も含めないでください。
"""

            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=CLAUDE_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0,
                    "system": "あなたは特許データベースのSQLクエリ生成専門AIアシスタントです。ユーザーの質問に対して必ずSQLクエリのみを返します。",
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            # Parse response
            response_body = json.loads(response.get("body").read())
            sql_query = response_body.get("content", [{}])[0].get("text", "")
            
            # Clean up the SQL query
            if "```sql" in sql_query:
                sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
            elif "```" in sql_query:
                sql_query = sql_query.split("```")[1].split("```")[0].strip()
                
            logger.info(f"Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return ""
    
    async def _generate_response(self, query: str, sql_result: Dict, db_type: str) -> str:
        """
        Generate a natural language response from SQL results.
        
        Args:
            query: Original natural language query
            sql_result: SQL query execution results
            db_type: Database type
            
        Returns:
            Natural language response
        """
        try:
            if not self.is_aws_configured or not self.bedrock_runtime:
                return "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。"
            
            # Prepare SQL results for the prompt
            columns = sql_result.get("columns", [])
            results = sql_result.get("results", [])
            record_count = len(results)
            
            # Format results
            if record_count == 0:
                results_text = "結果は0件でした。"
            else:
                results_text = f"結果 ({record_count}件):\n\n"
                
                # Convert results to a table format
                header_row = "| " + " | ".join(columns) + " |"
                separator = "| " + " | ".join(["---" for _ in columns]) + " |"
                
                results_text += header_row + "\n" + separator + "\n"
                
                # Add up to 10 rows
                for row in results[:10]:
                    row_text = "| " + " | ".join([str(cell) for cell in row]) + " |"
                    results_text += row_text + "\n"
                    
                if record_count > 10:
                    results_text += f"...(他 {record_count - 10} 件省略)...\n"
            
            # Create a prompt for response generation
            prompt = f"""あなたは特許データベース検索結果のわかりやすい解説を行う専門家です。
次のSQL検索結果を、日本語で要約し説明してください。

### ユーザーの質問:
{query}

### SQL検索結果:
{results_text}

### 応答:
検索結果について、簡潔かつわかりやすく説明してください。
"""

            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=CLAUDE_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "temperature": 0,
                    "system": "あなたは特許データベース検索結果を日本語で簡潔に要約する専門家です。",
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            # Parse response
            response_body = json.loads(response.get("body").read())
            nl_response = response_body.get("content", [{}])[0].get("text", "")
            
            return nl_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"結果の説明生成中にエラーが発生しました: {str(e)}"
    
    async def process_query(self, query: str, db_type: str = "inpit") -> Dict:
        """
        Process a natural language query about patents.
        
        Args:
            query: Natural language query string
            db_type: Database to query against
            
        Returns:
            Dict containing query results and generated response
        """
        try:
            # Check if AWS is configured
            if not self.is_aws_configured:
                return {
                    "success": False,
                    # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
                    "error": "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_DEFAULT_REGIONが適切に設定されていることを確認してください。"
                }
            
            # Generate SQL from the query
            sql_query = await self._generate_sql(query, db_type)
            
            if not sql_query or not sql_query.strip().upper().startswith(("SELECT", "WITH")):
                logger.error(f"Failed to generate valid SQL: {sql_query}")
                return {
                    "success": False,
                    "error": "SQLクエリの生成に失敗しました。別のクエリを試してください。"
                }
            
            # Execute the SQL query against the database
            response = httpx.post(
                f"{PATENT_DB_URL}/api/sql-query",
                json={"query": sql_query, "db_type": db_type}
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"SQL実行エラー: {response.text}"
                }
                
            sql_result = response.json()
            
            # Generate natural language response from the SQL results
            nl_response = await self._generate_response(query, sql_result, db_type)
            
            # Return the combined result
            return {
                "success": True,
                "query": query,
                "sql": sql_query,
                "db_type": db_type,
                "sql_result": sql_result,
                "response": nl_response
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": f"クエリ処理エラー: {str(e)}"
            }

# Singleton instance for reuse
_base_instance = None

def get_base_nl_processor():
    """Get a singleton instance of the NLQueryProcessor."""
    global _base_instance
    if _base_instance is None:
        _base_instance = NLQueryProcessor()
    return _base_instance
