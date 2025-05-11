#!/usr/bin/env python3
"""
Enhanced Natural Language Query Processor for patentDWH

This module provides an enhanced version of the NL query processor with the option
to use LangChain as the primary SQL generation method or as a fallback.
"""

import os
import json
import logging
import sqlite3
import boto3
import tempfile
import httpx
from typing import Dict, List, Any, Optional, Tuple

# Import from the original NLQueryProcessor
from patched_nl_query_processor import NLQueryProcessor as PatchedNLQueryProcessor

# Import LangChain components - minimal imports to avoid dependency issues
from langchain_community.llms.bedrock import Bedrock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AWS Bedrock settings
CLAUDE_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Patent DB API URL from environment variable
PATENT_DB_URL = os.environ.get("PATENT_DB_URL", "http://patentdwh-db:5002")

class EnhancedNLQueryProcessor(PatchedNLQueryProcessor):
    """
    Enhanced Natural Language Query Processor with option to use LangChain as primary method

    This class extends the patched NLQueryProcessor to allow using LangChain
    as the primary SQL generation method rather than just as a fallback.
    """

    def __init__(self):
        """Initialize the enhanced NL query processor."""
        super().__init__()  # Initialize parent class
        self._setup_langchain()

    def _setup_langchain(self):
        """Setup LangChain components for SQL generation."""
        if not self.is_aws_configured or not self.bedrock_runtime:
            logger.error("AWS Bedrock not available, LangChain setup skipped")
            return

        try:
            # Configure the LLM to use with LangChain
            self.langchain_llm = Bedrock(
                model_id=CLAUDE_MODEL_ID,
                client=self.bedrock_runtime,
                model_kwargs={
                    "temperature": 0,
                    "max_tokens": 1000,
                    "anthropic_version": "bedrock-2023-05-31"
                }
            )
            logger.info("LangChain LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up LangChain: {e}")

    async def _generate_sql_with_langchain(self, query: str, db_type: str) -> Tuple[str, bool]:
        """
        Generate SQL using LangChain by directly querying the LLM.
        
        Args:
            query: Natural language query
            db_type: Database type
            
        Returns:
            Tuple of (generated SQL, success flag)
        """
        try:
            if not hasattr(self, 'langchain_llm'):
                logger.error(f"LangChain LLM not configured")
                return "", False
                
            # Get schema info for this database with retry/refresh if needed
            schema_info = self.schemas.get(db_type, {})
            if not schema_info or "tables" not in schema_info or not schema_info["tables"]:
                logger.warning(f"No schema info available for {db_type}, attempting to refresh schemas")
                # Try to refresh schemas
                self.schemas = self._get_database_schemas()
                schema_info = self.schemas.get(db_type, {})
                if not schema_info or "tables" not in schema_info or not schema_info["tables"]:
                    logger.error(f"Could not retrieve schema info for {db_type} even after refresh")
                    return "", False
                
            # Create a descriptive prompt for the LLM
            tables_info = ""
            for table_name, table_info in schema_info.get("tables", {}).items():
                columns = table_info.get("columns", [])
                tables_info += f"Table: {table_name}\n"
                tables_info += f"Columns: {', '.join(columns)}\n\n"
            
            prompt = f"""あなたは日本語の自然言語から正確なSQLクエリを生成する特許データベースの専門家です。
ユーザーからの質問に対して、適切なSQLクエリを生成してください。

### 使用するデータベースの情報 ###
SQLタイプ: SQLite
テーブル情報:
{tables_info}

### ユーザーからの質問 ###
{query}

### SQLクエリ ###
以下のSQLクエリを生成します:
"""
            
            # Generate SQL with LangChain
            result = await self.langchain_llm.ainvoke(prompt)
            
            # Clean up the result to get just the SQL
            sql = result.strip()
            
            # Extract SQL if it's embedded in a code block
            if "```sql" in sql:
                parts = sql.split("```sql")
                if len(parts) > 1:
                    sql_parts = parts[1].split("```")
                    if sql_parts:
                        sql = sql_parts[0].strip()
            
            # Remove trailing semicolon if present
            if sql.endswith(";"):
                sql = sql[:-1]
                
            logger.info(f"LangChain generated SQL: {sql}")
            return sql, True
                
        except Exception as e:
            logger.error(f"Error generating SQL with LangChain: {e}")
            return "", False

    async def process_query(self, query: str, db_type: str = "inpit", use_langchain_first: bool = False) -> Dict:
        """
        Process a natural language query about patents with option to use LangChain first.
        
        Args:
            query: Natural language query string
            db_type: Database to query against
            use_langchain_first: Whether to use LangChain as the primary SQL generation method
            
        Returns:
            Dict containing query results and generated response
        """
        try:
            # Check if AWS is configured
            if not self.is_aws_configured:
                return {
                    "success": False,
                    "error": "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_REGIONが適切に設定されていることを確認してください。"
                }
            
            sql_query = ""
            used_langchain = False
            used_fallback = False
            
            # Choose SQL generation method based on use_langchain_first parameter
            if use_langchain_first:
                # Try LangChain first
                logger.info("Using LangChain as primary SQL generation method")
                sql_query, success = await self._generate_sql_with_langchain(query, db_type)
                if success and sql_query and sql_query.strip().upper().startswith(("SELECT", "WITH")):
                    used_langchain = True
                    logger.info("Successfully generated SQL with LangChain")
                else:
                    # If LangChain fails, fall back to original method
                    logger.info("LangChain SQL generation failed, falling back to original method")
                    sql_query = await self._generate_sql(query, db_type)
            else:
                # Use original method first, then fallback to direct Bedrock as in patched processor
                sql_query = await self._generate_sql(query, db_type)
                
                # If original method failed, try direct Bedrock fallback
                if not sql_query or not sql_query.strip().upper().startswith(("SELECT", "WITH")):
                    logger.info("Original SQL generation failed or produced invalid SQL. Using fallback method.")
                    fallback_sql = await self._generate_fallback_sql(query, db_type)
                    
                    if fallback_sql and fallback_sql.strip().upper().startswith(("SELECT", "WITH")):
                        sql_query = fallback_sql
                        used_fallback = True
                        logger.info(f"Using fallback generated SQL: {sql_query}")
                    else:
                        # If both original and fallback failed, try LangChain as last resort
                        logger.info("Both original and fallback SQL generation failed. Trying LangChain as last resort.")
                        langchain_sql, success = await self._generate_sql_with_langchain(query, db_type)
                        
                        if success and langchain_sql and langchain_sql.strip().upper().startswith(("SELECT", "WITH")):
                            sql_query = langchain_sql
                            used_langchain = True
                            logger.info(f"Using LangChain generated SQL: {sql_query}")
                        else:
                            logger.error("All SQL generation methods failed")
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
            
            # Return the combined result with method flags
            return {
                "success": True,
                "query": query,
                "sql": sql_query,
                "db_type": db_type,
                "sql_result": sql_result,
                "response": nl_response,
                "used_langchain": used_langchain,
                "used_fallback": used_fallback
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": f"クエリ処理エラー: {str(e)}"
            }

# Singleton instance for reuse
_enhanced_instance = None

def get_enhanced_nl_processor():
    """Get a singleton instance of the EnhancedNLQueryProcessor."""
    global _enhanced_instance
    if _enhanced_instance is None:
        _enhanced_instance = EnhancedNLQueryProcessor()
    return _enhanced_instance
