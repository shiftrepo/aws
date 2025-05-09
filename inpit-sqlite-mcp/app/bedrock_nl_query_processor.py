#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bedrock-powered Natural Language Query Processor for Database

This module provides functionality to process natural language queries against databases,
converting them to SQL queries using AWS Bedrock's LLM and embedding capabilities.
"""

import os
import json
import sqlite3
import logging
import boto3
from typing import Dict, List, Any, Optional, Tuple
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BedrockNLQueryProcessor:
    """
    Process natural language queries for database using AWS Bedrock
    """
    
    def __init__(self, db_path: str, 
                 column_mapping_path: Optional[str] = None,
                 table_name: str = "inpit_data",
                 model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                 embedding_model_id: str = "amazon.titan-embed-text-v2:0",
                 region_name: str = "us-east-1"):
        """
        Initialize the Bedrock-powered natural language query processor
        
        Args:
            db_path: Path to the SQLite database file
            column_mapping_path: Path to column mapping JSON file (optional)
            table_name: Name of the database table to query
            model_id: Bedrock model ID for LLM
            embedding_model_id: Bedrock model ID for embeddings
            region_name: AWS region name
        """
        self.db_path = db_path
        self.table_name = table_name
        self.model_id = model_id
        self.embedding_model_id = embedding_model_id
        
        # Initialize AWS clients
        try:
            logger.info(f"Initializing Bedrock clients in region {region_name}")
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
            logger.info("Bedrock clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock clients: {e}")
            raise
        
        # Load column mapping if provided
        self.column_map = {}
        if column_mapping_path:
            self.column_map = self._load_column_mapping(column_mapping_path)
        
        # Get database schema information
        self.schema_info = self._get_schema_info()
        
        # Cache schema context to avoid repeated extraction
        self.schema_context = self._generate_schema_context()
        logger.info("Schema context generated successfully")

    def _load_column_mapping(self, mapping_path: str) -> Dict[str, str]:
        """
        Load column mapping from JSON file
        
        Args:
            mapping_path: Path to the column mapping JSON file
            
        Returns:
            Dictionary of column mappings
        """
        try:
            if mapping_path:
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load column mapping from {mapping_path}: {e}")
        return {}
    
    def _get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information from the database
        
        Returns:
            Dictionary with table schema information
        """
        schema_info = {
            "tables": {},
            "relationships": []
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get schema for each table
            for table_name in tables:
                # Skip internal SQLite tables
                if table_name.startswith('sqlite_'):
                    continue
                    
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = []
                primary_keys = []
                
                for row in cursor.fetchall():
                    col_id, col_name, col_type, not_null, default_value, is_pk = row
                    columns.append({
                        "name": col_name,
                        "type": col_type,
                        "not_null": bool(not_null),
                        "default": default_value,
                        "is_primary_key": bool(is_pk)
                    })
                    
                    if is_pk:
                        primary_keys.append(col_name)
                
                # Get sample data (first row) to understand content
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample_row = cursor.fetchone()
                    sample_data = {}
                    if sample_row:
                        col_names = [description[0] for description in cursor.description]
                        sample_data = {col_names[i]: str(sample_row[i]) for i in range(len(col_names))}
                except Exception as e:
                    logger.warning(f"Could not get sample data for {table_name}: {e}")
                    sample_data = {}
                
                # Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                except Exception as e:
                    logger.warning(f"Could not get row count for {table_name}: {e}")
                    row_count = None
                
                # Store table schema
                schema_info["tables"][table_name] = {
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "sample_data": sample_data,
                    "row_count": row_count
                }
                
            # Add any display names from column_map
            for table_name, table_info in schema_info["tables"].items():
                for column in table_info["columns"]:
                    col_name = column["name"]
                    if col_name in self.column_map:
                        column["display_name"] = self.column_map[col_name]
            
            conn.close()
            logger.info(f"Successfully extracted schema for {len(schema_info['tables'])} tables")
            return schema_info
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return schema_info
    
    def _generate_schema_context(self) -> str:
        """
        Generate a textual representation of the schema for context
        
        Returns:
            String containing schema information for the LLM
        """
        context = ["DATABASE SCHEMA INFORMATION:"]
        
        for table_name, table_info in self.schema_info["tables"].items():
            context.append(f"\nTABLE: {table_name}")
            if table_info.get("row_count"):
                context.append(f"Row count: {table_info['row_count']}")
            
            # Columns
            context.append("\nCOLUMNS:")
            for column in table_info["columns"]:
                col_desc = f"- {column['name']} ({column['type']})"
                
                # Add display name if available
                if "display_name" in column:
                    col_desc += f" [Display name: {column['display_name']}]"
                
                # Add constraints
                constraints = []
                if column["is_primary_key"]:
                    constraints.append("PRIMARY KEY")
                if column["not_null"]:
                    constraints.append("NOT NULL")
                if column["default"] is not None:
                    constraints.append(f"DEFAULT {column['default']}")
                
                if constraints:
                    col_desc += f" {', '.join(constraints)}"
                
                context.append(col_desc)
            
            # Sample data
            if table_info["sample_data"]:
                context.append("\nSAMPLE DATA (first row):")
                for col, value in table_info["sample_data"].items():
                    if value is not None:
                        # Truncate very long values
                        if len(str(value)) > 50:
                            value = str(value)[:50] + "..."
                        context.append(f"- {col}: {value}")
        
        return "\n".join(context)

    def _invoke_bedrock_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for text using Bedrock Titan Embedding model
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.embedding_model_id,
                body=json.dumps({
                    "inputText": text
                })
            )
            
            response_body = json.loads(response.get('body').read())
            embedding = response_body.get('embedding')
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
            
    def _invoke_bedrock_llm(self, messages: List[Dict[str, str]], 
                           max_tokens: int = 1000, 
                           temperature: float = 0.0) -> str:
        """
        Generate text using Bedrock Claude model
        
        Args:
            messages: List of message dictionaries with role and content
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('content')[0].get('text')
        except Exception as e:
            logger.error(f"Error invoking Bedrock LLM: {e}")
            raise

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
            
            # Extract conditions, limit, order by (for metadata)
            conditions, limit, order_by = self._parse_sql_components(sql_query)
            
            return {
                "natural_language_query": query_text,
                "sql_query": sql_query,
                "conditions": conditions,
                "order_by": order_by,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": str(e),
                "natural_language_query": query_text,
                "sql_query": None
            }
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """
        Clean up the SQL query generated by the LLM
        
        Args:
            sql_query: The SQL query to clean
            
        Returns:
            Cleaned SQL query
        """
        # Remove markdown code block formatting if present
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:]
            
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        return sql_query.strip()
    
    def _parse_sql_components(self, sql_query: str) -> Tuple[List[str], int, Optional[str]]:
        """
        Parse SQL components from generated query for metadata
        
        Args:
            sql_query: The SQL query to parse
            
        Returns:
            Tuple of (list of WHERE conditions, limit, order by clause)
        """
        conditions = []
        limit = 100  # Default
        order_by = None
        
        # Simple parsing - this is just for metadata
        # Extract WHERE conditions
        if " WHERE " in sql_query:
            where_part = sql_query.split(" WHERE ", 1)[1]
            if " ORDER BY " in where_part:
                where_part = where_part.split(" ORDER BY ", 1)[0]
            if " LIMIT " in where_part:
                where_part = where_part.split(" LIMIT ", 1)[0]
                
            # Split by AND to get individual conditions
            where_conditions = where_part.split(" AND ")
            conditions = [cond.strip() for cond in where_conditions]
        
        # Extract ORDER BY
        if " ORDER BY " in sql_query:
            order_part = sql_query.split(" ORDER BY ", 1)[1]
            if " LIMIT " in order_part:
                order_part = order_part.split(" LIMIT ", 1)[0]
            order_by = order_part.strip()
        
        # Extract LIMIT
        if " LIMIT " in sql_query:
            limit_part = sql_query.split(" LIMIT ", 1)[1].strip()
            try:
                limit = int(limit_part)
            except (ValueError, IndexError):
                pass  # Keep default
        
        return conditions, limit, order_by

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute an SQL query against the database
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            Query results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return results as dictionaries
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            
            # Convert to list of dicts
            column_names = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                # Map to original column names if possible
                row_dict = {}
                for i, col in enumerate(column_names):
                    display_name = self.column_map.get(col, col)
                    row_dict[display_name] = row[i]
                results.append(row_dict)
            
            conn.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results,
                "columns": column_names
            }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": sql_query
            }
    
    def process_and_execute(self, query_text: str) -> Dict[str, Any]:
        """
        Process a natural language query and execute the resulting SQL query
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Query results
        """
        processed = self.process_query(query_text)
        
        if "error" in processed or not processed.get("sql_query"):
            return {
                "success": False,
                "error": processed.get("error", "Failed to process query"),
                "natural_language_query": query_text
            }
        
        sql_query = processed["sql_query"]
        results = self.execute_query(sql_query)
        
        if not results.get("success"):
            # If the query fails, try again with a more robust prompt
            fallback_result = self._generate_robust_sql(query_text, results.get("error"))
            if fallback_result and "sql_query" in fallback_result:
                fallback_sql = fallback_result["sql_query"]
                fallback_results = self.execute_query(fallback_sql)
                if fallback_results.get("success"):
                    return {
                        "success": True,
                        "natural_language_query": query_text,
                        "sql_query": fallback_sql,
                        "original_sql_query": sql_query,
                        "original_error": results.get("error"),
                        "note": "Used fallback query due to error in primary query",
                        "count": fallback_results.get("count", 0),
                        "results": fallback_results.get("results", []),
                        "columns": fallback_results.get("columns", [])
                    }
        
        return {
            "success": results.get("success", False),
            "natural_language_query": query_text,
            "sql_query": sql_query,
            "count": results.get("count", 0),
            "results": results.get("results", []),
            "columns": results.get("columns", [])
        }
    
    def _generate_robust_sql(self, query_text: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a more robust SQL query when the initial one fails
        
        Args:
            query_text: The original natural language query text
            error_message: The error message from the failed query
            
        Returns:
            Dictionary with robust SQL query
        """
        try:
            # Create a more detailed system prompt
            system_prompt = f"""You are an expert SQL assistant that converts natural language questions to SQL queries.
You are connected to a database with the following schema:

{self.schema_context}

Your task is to generate a valid SQL query that will work with this specific database schema.
Be very careful about column names and table names.
Only return the raw SQL query, with no additional explanation, markdown formatting, or comments."""

            # Create a more detailed user query with error feedback
            user_query = f"Generate a SQL query for the following question: {query_text}"
            if error_message:
                user_query += f"\n\nThe previous attempt failed with this error: {error_message}\nPlease fix the issue and generate a working query."
            
            # Call LLM with more detailed prompt
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
            
            sql_query = self._invoke_bedrock_llm(messages, temperature=0.2)  # Slightly higher temperature for diversity
            
            # Clean up the generated SQL
            sql_query = self._clean_sql_query(sql_query)
            
            return {
                "sql_query": sql_query
            }
        except Exception as e:
            logger.error(f"Error generating robust SQL: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    processor = BedrockNLQueryProcessor(db_path="/app/data/inpit.db", table_name="inpit_data")
    result = processor.process_and_execute("トヨタの自動車関連の特許を5件見せて")
    print(f"Found {result.get('count', 0)} results")
    for patent in result.get('results', [])[:3]:  # Show first 3 patents
        print(f"{patent.get('title', 'No title')} - {patent.get('application_number', 'No number')}")
