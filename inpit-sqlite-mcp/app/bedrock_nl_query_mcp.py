#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AWS Bedrock-powered Natural Language Query MCP Module

This module provides MCP tools and resources for natural language querying of
patent databases using AWS Bedrock LLM and embedding capabilities.
"""

import os
import json
import logging
from typing import Dict, List, Any

# Import Bedrock NL query processor
from bedrock_nl_query_processor import BedrockNLQueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database paths
INPIT_DB_PATH = "/app/data/inpit.db" 
GOOGLE_PATENTS_GCP_DB_PATH = "/app/data/google_patents_gcp.db"
COLUMN_MAPPING_PATH = "/app/data/column_mapping.json"

# AWS Bedrock configuration
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Schema definitions for MCP tools
SCHEMAS = {
    "bedrock_nl_query_inpit_database": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "自然言語によるINPITデータベースへの問い合わせ文"
            }
        },
        "required": ["query"]
    },
    "bedrock_nl_query_google_patents_database": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "自然言語によるGoogle Patents データベースへの問い合わせ文"
            }
        },
        "required": ["query"]
    }
}

class BedrockNLQueryMCPServer:
    """MCP Server for AWS Bedrock-powered natural language patent database querying"""
    
    def __init__(self):
        """
        Initialize the server with Bedrock-powered query processors
        """
        logger.info("Initializing Bedrock NL Query MCP Server")
        
        # Check if databases exist
        inpit_db_exists = os.path.exists(INPIT_DB_PATH)
        google_patents_db_exists = os.path.exists(GOOGLE_PATENTS_GCP_DB_PATH)
        
        logger.info(f"INPIT database exists: {inpit_db_exists} (Path: {INPIT_DB_PATH})")
        logger.info(f"Google Patents database exists: {google_patents_db_exists} (Path: {GOOGLE_PATENTS_GCP_DB_PATH})")
        
        # Initialize processors
        try:
            if inpit_db_exists:
                self.inpit_processor = BedrockNLQueryProcessor(
                    db_path=INPIT_DB_PATH,
                    column_mapping_path=COLUMN_MAPPING_PATH,
                    table_name="inpit_data",
                    model_id=MODEL_ID,
                    embedding_model_id=EMBEDDING_MODEL_ID,
                    region_name=AWS_REGION
                )
                logger.info("Successfully initialized Bedrock INPIT NL query processor")
            else:
                logger.warning(f"INPIT database not found at {INPIT_DB_PATH}, functionality will be limited")
                self.inpit_processor = None
        except Exception as e:
            logger.error(f"Error initializing Bedrock INPIT NL query processor: {e}")
            self.inpit_processor = None
        
        try:
            if google_patents_db_exists:
                self.google_processor = BedrockNLQueryProcessor(
                    db_path=GOOGLE_PATENTS_GCP_DB_PATH,
                    table_name="google_patents",
                    model_id=MODEL_ID,
                    embedding_model_id=EMBEDDING_MODEL_ID,
                    region_name=AWS_REGION
                )
                logger.info("Successfully initialized Bedrock Google Patents NL query processor")
            else:
                logger.warning(f"Google Patents database not found at {GOOGLE_PATENTS_GCP_DB_PATH}, functionality will be limited")
                self.google_processor = None
        except Exception as e:
            logger.error(f"Error initializing Bedrock Google Patents NL query processor: {e}")
            self.google_processor = None
            
        logger.info("Bedrock NL Query MCP Server initialization complete")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        tools = []
        
        # Add Inpit tool if processor is available
        if self.inpit_processor:
            tools.append({
                "name": "bedrock_nl_query_inpit_database",
                "description": "AWS Bedrockを使って自然言語でINPIT特許データベースに問い合わせを行います",
                "schema": SCHEMAS["bedrock_nl_query_inpit_database"]
            })
        
        # Add Google Patents tool if processor is available
        if self.google_processor:
            tools.append({
                "name": "bedrock_nl_query_google_patents_database",
                "description": "AWS Bedrockを使って自然言語でGoogle Patents特許データベースに問い合わせを行います",
                "schema": SCHEMAS["bedrock_nl_query_google_patents_database"]
            })
        
        return tools
    
    def get_resources(self) -> List[Dict[str, str]]:
        """Return list of available resources"""
        resources = []
        
        # Add resources based on available databases
        if self.inpit_processor:
            resources.append({
                "uri": "bedrock-nl-query://inpit/help",
                "description": "AWS Bedrockを使ったINPIT特許データベースへの自然言語問い合わせに関するヘルプ情報"
            })
        
        if self.google_processor:
            resources.append({
                "uri": "bedrock-nl-query://google-patents/help",
                "description": "AWS Bedrockを使ったGoogle Patents特許データベースへの自然言語問い合わせに関するヘルプ情報"
            })
        
        return resources
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with the given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
        
        try:
            if tool_name == "bedrock_nl_query_inpit_database":
                return self._bedrock_nl_query_inpit_database(arguments)
            elif tool_name == "bedrock_nl_query_google_patents_database":
                return self._bedrock_nl_query_google_patents_database(arguments)
            else:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def access_resource(self, uri: str) -> Dict[str, Any]:
        """
        Access a specific resource by URI
        
        Args:
            uri: URI of the resource to access
            
        Returns:
            Resource data
        """
        logger.info(f"Accessing resource: {uri}")
        
        try:
            if uri == "bedrock-nl-query://inpit/help":
                return self._get_bedrock_inpit_help()
            elif uri == "bedrock-nl-query://google-patents/help":
                return self._get_bedrock_google_patents_help()
            else:
                error_msg = f"Unknown resource URI: {uri}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error accessing resource {uri}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
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
                    "results": result.get("results", [])[:20],  # Limit to 20 results in the response
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
    
    def _bedrock_nl_query_google_patents_database(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the Google Patents database using natural language with Bedrock
        
        Args:
            arguments: Arguments containing the natural language query
            
        Returns:
            Query results
        """
        query = arguments.get("query")
        if not query:
            return {"error": "query is required"}
        
        if not self.google_processor:
            return {
                "error": "Google Patents database is not available",
                "detail": f"Database file not found at {GOOGLE_PATENTS_GCP_DB_PATH}"
            }
        
        try:
            result = self.google_processor.process_and_execute(query)
            
            # Enhance the response with additional information
            if result.get("success"):
                enhanced_result = {
                    "success": True,
                    "query": query,
                    "sql_query": result.get("sql_query"),
                    "count": result.get("count", 0),
                    "results": result.get("results", [])[:20],  # Limit to 20 results in the response
                    "total_results": result.get("count", 0),
                    "database": "Google Patents GCP (google_patents_gcp.db)",
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
                    "database": "Google Patents GCP (google_patents_gcp.db)"
                }
        except Exception as e:
            error_msg = f"Error processing natural language query: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_bedrock_inpit_help(self) -> Dict[str, Any]:
        """
        Get help information for Bedrock natural language querying of INPIT database
        
        Returns:
            Help information
        """
        return {
            "title": "AWS Bedrock INPIT特許データベース自然言語クエリヘルプ",
            "description": "AWS BedrockのLLM（Claude 3.7 Sonnet）とTitan Embeddingsを使用して、INPIT特許データベースに自然言語で問い合わせを行う方法についてのヘルプ情報です。",
            "database": "INPIT SQLite (inpit.db)",
            "model": MODEL_ID,
            "embedding_model": EMBEDDING_MODEL_ID,
            "query_types": [
                {
                    "type": "出願人検索",
                    "examples": [
                        "トヨタによる特許を5件表示して",
                        "出願人がソニーの特許はいくつありますか",
                        "パナソニックの2020年の特許を教えて"
                    ]
                },
                {
                    "type": "技術分野検索",
                    "examples": [
                        "自動車に関する特許を検索",
                        "半導体技術の特許を10件表示",
                        "カメラ技術に関する日立の特許"
                    ]
                },
                {
                    "type": "期間検索",
                    "examples": [
                        "2018年以降のトヨタの特許",
                        "2015年から2020年までのディスプレイ関連特許",
                        "最新の医療機器特許を5件"
                    ]
                },
                {
                    "type": "番号検索",
                    "examples": [
                        "出願番号2019-123456の特許情報",
                        "公開番号JP2020-000123の詳細"
                    ]
                },
                {
                    "type": "複雑な検索クエリ",
                    "examples": [
                        "2018年から2020年の間に出願されたトヨタとホンダのEV関連の特許を比較して",
                        "最近5年間の自動運転技術の特許数の推移を会社別に分析して",
                        "ディスプレイ技術に関する特許で最も引用されているものは？"
                    ]
                }
            ],
            "features": [
                "自然言語からSQLへの変換をAWS Bedrock（Claude 3.7 Sonnet）が実行",
                "複雑な検索条件や詳細な分析も自然言語で指示可能",
                "データベーススキーマを自動的に解析し、最適なクエリを生成",
                "クエリが失敗した場合、エラー情報を基に自動的に修正を試みる",
                "日本語・英語両方の自然言語クエリに対応"
            ],
            "available_fields": [
                "出願番号 (application_number)",
                "公開番号 (publication_number)",
                "出願人 (applicant_name)",
                "発明者 (inventor_name)",
                "タイトル/発明の名称 (title)",
                "要約 (abstract)",
                "出願日 (filing_date)",
                "公開日 (publication_date)",
                "IPC分類コード (ipc_code)"
            ],
            "note": "検索クエリは日本語または英語で入力できます。結果は最大100件まで取得されます（表示は最大20件）。"
        }
    
    def _get_bedrock_google_patents_help(self) -> Dict[str, Any]:
        """
        Get help information for Bedrock natural language querying of Google Patents database
        
        Returns:
            Help information
        """
        return {
            "title": "AWS Bedrock Google Patents特許データベース自然言語クエリヘルプ",
            "description": "AWS BedrockのLLM（Claude 3.7 Sonnet）とTitan Embeddingsを使用して、Google Patents特許データベースに自然言語で問い合わせを行う方法についてのヘルプ情報です。",
            "database": "Google Patents GCP (google_patents_gcp.db)",
            "model": MODEL_ID,
            "embedding_model": EMBEDDING_MODEL_ID,
            "query_types": [
                {
                    "type": "出願人検索",
                    "examples": [
                        "Show me 5 patents by Sony",
                        "How many patents does Toyota have",
                        "Find patents by Honda from 2019"
                    ]
                },
                {
                    "type": "技術分野検索",
                    "examples": [
                        "Patents about electric vehicles",
                        "Display technology patents",
                        "Find 10 patents related to machine learning"
                    ]
                },
                {
                    "type": "期間検索",
                    "examples": [
                        "Patents after 2020",
                        "Find patents from 2015 to 2018",
                        "Latest semiconductor patents"
                    ]
                },
                {
                    "type": "ファミリー検索",
                    "examples": [
                        "Find family members of US10123456",
                        "Patent family for JP2020-123456"
                    ]
                },
                {
                    "type": "複雑な検索クエリ",
                    "examples": [
                        "Compare patents filed by Samsung and Apple related to foldable displays between 2018-2022",
                        "Analyze trends in AI-related patents filed in the last decade by top 3 companies",
                        "Find most cited patents in quantum computing field"
                    ]
                }
            ],
            "features": [
                "AWS Bedrock (Claude 3.7 Sonnet) converts natural language to SQL",
                "Complex search conditions can be specified in natural language",
                "Database schema is automatically analyzed to generate optimal queries",
                "Automatic error recovery if initial query fails",
                "Supports both English and Japanese queries"
            ],
            "available_fields": [
                "publication_number",
                "application_number",
                "assignee_harmonized (出願人)",
                "title_ja (日本語タイトル)",
                "title_en (英語タイトル)",
                "abstract_ja (日本語要約)",
                "abstract_en (英語要約)",
                "filing_date (出願日)",
                "publication_date (公開日)",
                "ipc_code (IPC分類コード)",
                "family_id (特許ファミリーID)"
            ],
            "note": "クエリは英語または日本語で入力できます。結果は最大100件まで取得されます（表示は最大20件）。"
        }

# Create singleton instance
bedrock_nl_query_server = BedrockNLQueryMCPServer()

# MCP server functions that will be called by the MCP framework
def get_tools():
    """Return the tools provided by this server"""
    return bedrock_nl_query_server.get_tools()

def get_resources():
    """Return the resources provided by this server"""
    return bedrock_nl_query_server.get_resources()

def execute_tool(tool_name, arguments):
    """Execute a tool with the given arguments"""
    arguments_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
    return bedrock_nl_query_server.execute_tool(tool_name, arguments_dict)

def access_resource(uri):
    """Access a resource by URI"""
    return bedrock_nl_query_server.access_resource(uri)
