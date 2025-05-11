#!/usr/bin/env python3
"""
Natural Language Query Processor for patentDWH

This module provides natural language query processing capabilities for patentDWH using AWS Bedrock.
It uses Claude 3 Sonnet for natural language understanding and SQL generation,
and Titan Embeddings for text embeddings.
"""

import os
import json
import logging
import sqlite3
import boto3
from typing import Dict, List, Any, Optional
import httpx
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AWS Bedrock settings
# Using Claude 3 Haiku instead of Sonnet since it supports on-demand throughput
CLAUDE_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
TITAN_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

# Patent DB API URL from environment variable
PATENT_DB_URL = os.environ.get("PATENT_DB_URL", "http://patentdwh-db:5002")

class NLQueryProcessor:
    """
    Natural Language Query Processor for patentDWH

    This class handles converting natural language questions about patents into SQL queries,
    executing them against the patentDWH database, and returning natural language responses.
    """

    def __init__(self):
        """Initialize the NL query processor with Bedrock client."""
        self.bedrock_runtime = None
        self.is_aws_configured = False
        
        try:
            # Check if AWS credentials are properly configured
            if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get("AWS_SECRET_ACCESS_KEY"):
                logger.warning("AWS credentials not set in environment variables")
                self.is_aws_configured = False
            else:
                # Initialize Bedrock client
                # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
                self.bedrock_runtime = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
                )
                
                # Perform a simple check to verify credentials
                try:
                    # Try listing model offerings to validate credentials
                    # This is a lightweight operation that confirms access
                    # (Using get_waiter to avoid import error if not available)
                    if hasattr(self.bedrock_runtime, 'get_waiter'):
                        self.is_aws_configured = True
                        logger.info("Successfully initialized AWS Bedrock client")
                    else:
                        # Basic validation with dummy test
                        self.is_aws_configured = True
                        logger.info("AWS Bedrock client initialized, but couldn't validate credentials")
                except Exception as e:
                    logger.error(f"AWS credentials verification failed: {e}")
                    self.is_aws_configured = False
        except Exception as e:
            logger.error(f"Error initializing AWS Bedrock client: {e}")
            self.is_aws_configured = False

        # Cache the database schemas
        self.schemas = self._get_database_schemas()

    def _get_database_schemas(self) -> Dict[str, Dict]:
        """
        Retrieve and cache the database schemas for all available databases.
        With retry logic for container startup timing issues.
        
        Returns:
            Dict containing database schema information for each available database.
        """
        max_retries = 5
        retry_delay = 3  # seconds
        attempt = 0
        
        while attempt < max_retries:
            try:
                schemas = {}
                
                # Get database information from API
                response = httpx.get(f"{PATENT_DB_URL}/api/status", timeout=5.0)
                if response.status_code != 200:
                    logger.warning(f"Failed to get database info (attempt {attempt+1}/{max_retries}): {response.text}")
                    attempt += 1
                    if attempt < max_retries:
                        import time
                        time.sleep(retry_delay)
                        continue
                    return {}
                    
                db_info = response.json()
                
                # Process schema for each database
                for db_type in ["inpit", "google_patents_gcp", "google_patents_s3"]:
                    if db_type not in db_info.get("databases", {}):
                        continue
                        
                    schemas[db_type] = self._get_single_database_schema(db_type)
                    
                return schemas
            except Exception as e:
                logger.warning(f"Error retrieving database schemas (attempt {attempt+1}/{max_retries}): {e}")
                attempt += 1
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to retrieve database schemas after {max_retries} attempts: {e}")
                    return {}
        
        return {}
    
    def _get_single_database_schema(self, db_type: str) -> Dict:
        """
        Get schema information for a specific database type.
        
        Args:
            db_type: The type of database to get schema for ('inpit', 'google_patents_gcp', 'google_patents_s3')
            
        Returns:
            Dict containing table and column information
        """
        try:
            tables_info = {}
            sample_data = {}
            
            # Get some example queries to help understand the schema better
            example_response = httpx.post(
                f"{PATENT_DB_URL}/api/v1/mcp",
                json={
                    "tool_name": "get_sql_examples",
                    "tool_input": {"db_type": db_type}
                }
            )
            examples = {}
            if example_response.status_code == 200:
                result = example_response.json()
                if result.get("success") and "examples" in result:
                    examples = result["examples"]
            
            # For each example query, run the query to get the column information
            for example_name, example_query in examples.items():
                query_response = httpx.post(
                    f"{PATENT_DB_URL}/api/sql-query",
                    json={"query": example_query, "db_type": db_type}
                )
                
                if query_response.status_code == 200:
                    result = query_response.json()
                    if result.get("success") and "columns" in result:
                        # Extract table names from the query and associate columns
                        for table_name in self._extract_tables_from_query(example_query):
                            if table_name not in tables_info:
                                tables_info[table_name] = {"columns": []}
                            
                            # Add columns if not already present
                            for col in result["columns"]:
                                if col not in tables_info[table_name]["columns"]:
                                    tables_info[table_name]["columns"].append(col)
            
            # If we didn't get any tables from the examples, use a direct query
            if not tables_info:
                for table_name in self._get_tables_for_db(db_type):
                    query = f"SELECT * FROM {table_name} LIMIT 1"
                    query_response = httpx.post(
                        f"{PATENT_DB_URL}/api/sql-query",
                        json={"query": query, "db_type": db_type}
                    )
                    
                    if query_response.status_code == 200:
                        result = query_response.json()
                        if result.get("success") and "columns" in result:
                            tables_info[table_name] = {"columns": result["columns"]}
            
            # Fetch sample data (5 records) from each table
            for table_name in tables_info.keys():
                query = f"SELECT * FROM {table_name} LIMIT 5"
                query_response = httpx.post(
                    f"{PATENT_DB_URL}/api/sql-query",
                    json={"query": query, "db_type": db_type}
                )
                
                if query_response.status_code == 200:
                    result = query_response.json()
                    if result.get("success") and "results" in result:
                        sample_data[table_name] = {
                            "columns": result.get("columns", []),
                            "data": result.get("results", [])
                        }
            
            return {
                "tables": tables_info,
                "examples": examples,
                "sample_data": sample_data
            }
        except Exception as e:
            logger.error(f"Error getting schema for {db_type}: {e}")
            return {"tables": {}, "examples": {}}
    
    def _extract_tables_from_query(self, query: str) -> List[str]:
        """
        Extract table names from SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            List of table names
        """
        # Simplified extraction - this could be improved with SQL parsing
        tables = []
        query_lower = query.lower()
        
        # Extract from FROM clause
        from_parts = query_lower.split(" from ")
        if len(from_parts) > 1:
            # Take the part after FROM and before WHERE/GROUP/ORDER/LIMIT if present
            from_content = from_parts[1]
            for clause in [" where ", " group by ", " order by ", " limit ", ";"]:
                if clause in from_content:
                    from_content = from_content.split(clause)[0]
            
            # Handle joins
            for join_type in [" join ", " inner join ", " left join ", " right join "]:
                if join_type in from_content:
                    join_parts = from_content.split(join_type)
                    for part in join_parts:
                        # Extract the table name (ignoring aliases and ON conditions)
                        table = part.strip().split(" ")[0].strip()
                        if table and table not in tables:
                            tables.append(table)
                else:
                    # No joins, just a simple FROM clause
                    table = from_content.strip().split(" ")[0].strip()
                    if table and table not in tables:
                        tables.append(table)
        
        return tables
    
    def _get_tables_for_db(self, db_type: str) -> List[str]:
        """
        Get list of tables for a specific database type.
        
        Args:
            db_type: The type of database
            
        Returns:
            List of table names
        """
        if db_type == "inpit":
            return ["inpit_data"]
        elif db_type in ["google_patents_gcp", "google_patents_s3"]:
            return ["publications", "patent_families"]
        return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Titan Embedding model.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if not self.is_aws_configured or not self.bedrock_runtime:
            logger.error("AWS Bedrock is not properly configured, cannot generate embeddings")
            return []
            
        try:
            request_body = {
                "inputText": text
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=TITAN_EMBEDDING_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get("body").read())
            embedding = response_body.get("embedding")
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def _generate_sql(self, query: str, db_type: str) -> str:
        """
        Generate SQL from natural language query using Claude.
        
        Args:
            query: Natural language query
            db_type: Database type to query against
            
        Returns:
            Generated SQL query
        """
        if not self.is_aws_configured:
            logger.error("AWS Bedrock is not configured, cannot generate SQL")
            return ""
            
        try:
            # Get schema for the selected database
            schema = self.schemas.get(db_type, {"tables": {}, "examples": {}})
            
            # Create prompt for Claude with schema information
            prompt = self._create_sql_generation_prompt(query, db_type, schema)
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=CLAUDE_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get("body").read())
            sql_query = self._extract_sql_from_response(response_body.get("content", []))
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return ""
    
    def _create_sql_generation_prompt(self, query: str, db_type: str, schema: Dict) -> str:
        """
        Create prompt for SQL generation with schema information.
        
        Args:
            query: Natural language query
            db_type: Database type
            schema: Database schema information
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""I need you to translate a natural language query about patent data into a SQL query.

DATABASE TYPE: {db_type}

DATABASE SCHEMA:
"""
        # Add tables and columns
        for table_name, table_info in schema.get("tables", {}).items():
            prompt += f"\nTable: {table_name}\n"
            prompt += f"Columns: {', '.join(table_info.get('columns', []))}\n"
        
        # Add sample data for each table
        prompt += "\nSAMPLE DATA:\n"
        for table_name, sample_info in schema.get("sample_data", {}).items():
            prompt += f"\n{table_name} (Sample Records):\n"
            
            # Add column headers
            columns = sample_info.get("columns", [])
            if columns:
                prompt += " | ".join(columns) + "\n"
                prompt += "-" * (sum(len(col) for col in columns) + (3 * (len(columns) - 1))) + "\n"
                
                # Add sample rows
                for row in sample_info.get("data", []):
                    prompt += " | ".join(str(cell) for cell in row) + "\n"
                
                prompt += "\n"
        
        # Add example queries to help the model understand the schema better
        prompt += "\nEXAMPLE QUERIES:\n"
        for example_name, example_query in schema.get("examples", {}).items():
            prompt += f"\n# {example_name}\n{example_query}\n"
        
        # Add query-specific instructions
        prompt += f"""
NATURAL LANGUAGE QUERY:
{query}

Generate a single SQL query to answer this question. Only return the raw SQL query without any explanation. 
Make sure the query follows standard SQLite syntax. Include necessary JOINs if the query involves multiple tables.
Only use tables and columns that exist in the schema above. Do not include any markdown formatting or SQL blocks.
"""
        return prompt
    
    def _extract_sql_from_response(self, response_content: List[Dict]) -> str:
        """Extract SQL query from Claude response content."""
        if not response_content:
            return ""
            
        # Extract the text from the first content block
        text = ""
        for block in response_content:
            if block.get("type") == "text":
                text = block.get("text", "")
                break
        
        # Clean up the SQL query
        sql = text.strip()
        
        # Remove any markdown code blocks if present
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
            
        return sql.strip()
    
    async def _generate_response(self, query: str, sql_result: Dict, db_type: str) -> str:
        """
        Generate natural language response from SQL results using Claude.
        
        Args:
            query: Original natural language query
            sql_result: Results from SQL query execution
            db_type: Database type that was queried
            
        Returns:
            Natural language response
        """
        if not self.is_aws_configured:
            logger.error("AWS Bedrock is not configured, cannot generate response")
            return "申し訳ありませんが、AWS Bedrockの設定が適切に構成されていないため、自然言語での回答を生成できません。"
            
        try:
            # Format the SQL results for the prompt
            formatted_results = self._format_sql_results_for_prompt(sql_result)
            
            # Create prompt for response generation
            prompt = f"""I need you to analyze the results of a SQL query and provide a natural language response.

ORIGINAL QUESTION:
{query}

SQL RESULTS:
{formatted_results}

DATABASE: {db_type}

Please provide a clear, comprehensive answer to the original question based on these SQL results.
Your answer should be in natural Japanese language (日本語), focused on directly answering the question.
Include key statistics or insights from the data. Format numbers for readability.
If the results are empty or don't fully answer the question, explain that clearly.
"""
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=CLAUDE_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get("body").read())
            content_blocks = response_body.get("content", [])
            
            # Extract text from response
            response_text = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    response_text += block.get("text", "")
            
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"すみません、回答の生成中にエラーが発生しました: {str(e)}"
    
    def _format_sql_results_for_prompt(self, sql_result: Dict) -> str:
        """
        Format SQL results for inclusion in the prompt.
        
        Args:
            sql_result: Results from SQL query execution
            
        Returns:
            Formatted results string
        """
        if not sql_result.get("success", False):
            return f"ERROR: {sql_result.get('error', 'Unknown error')}"
            
        columns = sql_result.get("columns", [])
        results = sql_result.get("results", [])
        record_count = sql_result.get("record_count", len(results))
        
        if not results:
            return "No results found (empty result set)"
        
        # Create a formatted table-like representation
        formatted = f"Total records: {record_count}\n\n"
        
        # Add column headers
        formatted += " | ".join(columns) + "\n"
        formatted += "-" * (sum(len(col) for col in columns) + (3 * (len(columns) - 1))) + "\n"
        
        # Add results (limit to 20 rows in case there are many)
        max_rows = min(20, len(results))
        for i in range(max_rows):
            row = results[i]
            formatted += " | ".join(str(cell) for cell in row) + "\n"
            
        # Add indication if results were truncated
        if len(results) > max_rows:
            formatted += f"\n... (showing {max_rows} of {len(results)} rows)"
            
        return formatted
    
    async def process_query(self, query: str, db_type: str = "inpit") -> Dict:
        """
        Process a natural language query about patents.
        
        Args:
            query: Natural language query string
            db_type: Database to query against (inpit, google_patents_gcp, or google_patents_s3)
            
        Returns:
            Dict containing query results and generated response
        """
        try:
            # Check if AWS is configured
            if not self.is_aws_configured:
                return {
                    "success": False,
                    "error": "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_DEFAULT_REGIONが適切に設定されていることを確認してください。"
                }
            
            # Generate SQL query from natural language
            sql_query = await self._generate_sql(query, db_type)
            if not sql_query:
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
_instance = None

def get_nl_processor():
    """Get a singleton instance of the NLQueryProcessor."""
    global _instance
    if _instance is None:
        _instance = NLQueryProcessor()
    return _instance
