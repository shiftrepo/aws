#!/usr/bin/env python3
"""
Patent DWH MCP Server - FastAPI implementation of the Model Context Protocol for patent data warehousing
with natural language query support using AWS Bedrock
"""

import os
import json
import logging
import httpx
import pandas as pd
from typing import Dict, List, Any, Optional
# Import the patched NL query processor instead of the original one
from patched_nl_query_processor import get_nl_processor
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# MCP関連のクラスとインターフェースを代替実装
class Tool:
    """MCP Toolクラスの簡易実装"""
    def __init__(self, name, description, param_schema=None):
        self.name = name
        self.description = description
        self.param_schema = param_schema

class Resource:
    """MCP Resourceクラスの簡易実装"""
    def __init__(self, uri, content_type, content):
        self.uri = uri
        self.content_type = content_type
        self.content = content

class CompletionInfo:
    """CompletionInfoクラスの簡易実装"""
    def __init__(self, completion_id, model, created):
        self.completion_id = completion_id
        self.model = model
        self.created = created

class ToolCall:
    """ToolCallクラスの簡易実装"""
    def __init__(self, tool_name, parameters):
        self.tool_name = tool_name
        self.parameters = parameters

DEFAULT_TOOL_TYPE = "function"

class Registry:
    """MCP Registryクラスの簡易実装"""
    def __init__(self):
        self.tools = {}
    
    def tool(self, name, description, param_schema=None):
        """Toolデコレータの簡易実装"""
        def decorator(func):
            self.tools[name] = {
                "function": func,
                "description": description,
                "param_schema": param_schema
            }
            return func
        return decorator
    
    def mount_to_app(self, app):
        """FastAPIアプリにMCP用のルートを追加する簡易実装"""
        # MCPのstatusエンドポイント
        @app.get("/api/status")
        async def mcp_status():
            """MCP status endpoint - returns information about the available tools"""
            tools = []
            for name, tool_info in self.tools.items():
                tools.append({
                    "name": name,
                    "type": DEFAULT_TOOL_TYPE,
                    "description": tool_info["description"],
                    "param_schema": tool_info["param_schema"]
                })
            
            return {
                "status": "available",
                "tools": tools,
                "resources": []  # リソースは今回の実装では使用しない
            }
        
        # MCPのメインエンドポイント
        @app.post("/api/v1/mcp")
        async def mcp_endpoint(request: Request):
            """MCP main endpoint - handles tool calls"""
            try:
                # リクエストのJSONを取得
                data = await request.json()
                logger.info(f"MCP request received: {data}")
                
                # ツール名とパラメータの抽出
                tool_name = data.get("tool_name")
                tool_input = data.get("tool_input", {})
                
                # ツールが存在するか確認
                if tool_name not in self.tools:
                    logger.error(f"Tool not found: {tool_name}")
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"Tool '{tool_name}' not found"}
                    )
                
                # ツール関数の実行
                tool_func = self.tools[tool_name]["function"]
                result = await tool_func(tool_input)
                
                # 結果を返す
                logger.info(f"Tool execution result: {result}")
                return JSONResponse(content=result)
                
            except Exception as e:
                logger.error(f"Error in MCP endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
        
        return app

class FSResourceEngine:
    """FSResourceEngineの代替クラス"""
    pass

class SimpleToolEngine:
    """SimpleToolEngineの代替クラス"""
    pass

class SimpleReadWriteResourceEngine:
    """SimpleReadWriteResourceEngineの代替クラス"""
    pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Patent DB API URL from environment variable
PATENT_DB_URL = os.environ.get("PATENT_DB_URL", "http://patentdwh-db:5002")

# Create FastAPI app
app = FastAPI(
    title="patentDWH MCP Server",
    description="MCP Server for accessing patent databases via SQLite",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create MCP registry
registry = Registry()

# Schema for SQL query tool
class SQLQueryParams(BaseModel):
    query: str
    db_type: str = "inpit"  # Default to inpit database

# Schema for natural language query
class NLQueryParams(BaseModel):
    query: str
    db_type: str = "inpit"  # Default to inpit database

# Schema for database info
class DatabaseInfoParams(BaseModel):
    db_type: Optional[str] = None  # Optional, if None, returns info for all databases

# SQL Query Tool implementation
@registry.tool(
    name="patent_sql_query",
    description="Execute a SQL query on the patent database",
    param_schema="""
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute (SELECT queries only)"
            },
            "db_type": {
                "type": "string",
                "description": "Database to query: 'inpit', 'google_patents_gcp', or 'google_patents_s3'",
                "enum": ["inpit", "google_patents_gcp", "google_patents_s3"],
                "default": "inpit"
            }
        },
        "required": ["query"]
    }
    """
)
async def patent_sql_query(params) -> Dict[str, Any]:
    """Execute a SQL query on the patent database."""
    try:
        # Handle both dictionary and SQLQueryParams object
        # For dictionary access (MCPサーバー経由の呼び出し)
        if isinstance(params, dict):
            query = params.get('query')
            db_type = params.get('db_type', 'inpit')
        # For SQLQueryParams object (直接的なAPIアクセス)
        else:
            query = params.query
            db_type = params.db_type
            
        # Basic validation - only SELECT queries allowed for security
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed for security reasons")

        # Make request to the patent database API
        async with httpx.AsyncClient() as client:
            logger.info(f"Executing query on {db_type} database: {query}")
            response = await client.post(
                f"{PATENT_DB_URL}/api/sql-query",
                json={"query": query, "db_type": db_type}
            )
            
            # Handle API response
            if response.status_code != 200:
                error_msg = f"Database API error: {response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=response.status_code, detail=error_msg)
            
            # Parse the database results
            result = response.json()
            if "error" in result:
                raise ValueError(f"Query error: {result['error']}")
            
            # Format the response
            return {
                "success": True,
                "columns": result.get("columns", []),
                "results": result.get("results", []),
                "record_count": result.get("record_count", len(result.get("results", [])))
            }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        return {"success": False, "error": f"Error executing SQL query: {str(e)}"}

# Database Info Tool implementation
@registry.tool(
    name="get_database_info",
    description="Get information about the available patent databases",
    param_schema="""
    {
        "type": "object",
        "properties": {
            "db_type": {
                "type": "string",
                "description": "Specific database to get info for (or all if not specified)",
                "enum": ["inpit", "google_patents_gcp", "google_patents_s3"],
                "default": null
            }
        }
    }
    """
)
async def get_database_info(params: DatabaseInfoParams) -> Dict[str, Any]:
    """Get information about the available patent databases."""
    try:
        # Make request to the patent database API status endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PATENT_DB_URL}/api/status")
            
            # Handle API response
            if response.status_code != 200:
                error_msg = f"Database API error: {response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=response.status_code, detail=error_msg)
            
            # Parse the database results
            result = response.json()
            
            # Filter by specific database if requested
            if params.db_type:
                if "databases" in result and params.db_type in result["databases"]:
                    return {
                        "success": True,
                        "database_info": {
                            params.db_type: result["databases"][params.db_type]
                        }
                    }
                else:
                    return {
                        "success": False, 
                        "error": f"Database '{params.db_type}' not found"
                    }
            
            # Otherwise return all database info
            return {
                "success": True,
                "database_info": result.get("databases", {}),
                "api_endpoints": result.get("endpoints", {})
            }
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        return {"success": False, "error": f"Error getting database info: {str(e)}"}

# Check AWS Credentials Tool
@registry.tool(
    name="check_aws_credentials",
    description="Check if AWS credentials are properly configured for Bedrock services",
    param_schema="""
    {
        "type": "object",
        "properties": {}
    }
    """
)
async def check_aws_credentials(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if AWS credentials are properly configured for Bedrock services."""
    try:
        # Get NL processor to check AWS configuration
        nl_processor = get_nl_processor()
        
        # Check if AWS is configured properly
        if nl_processor.is_aws_configured:
            return {
                "success": True,
                "message": "AWS credentials are correctly configured for Bedrock services",
                "aws_region": os.environ.get("AWS_REGION", "us-east-1")
            }
        else:
            # Check which credentials are missing
            missing_creds = []
            if not os.environ.get("AWS_ACCESS_KEY_ID"):
                missing_creds.append("AWS_ACCESS_KEY_ID")
            if not os.environ.get("AWS_SECRET_ACCESS_KEY"):
                missing_creds.append("AWS_SECRET_ACCESS_KEY")
            
            return {
                "success": False,
                "message": "AWS credentials are not properly configured for Bedrock services",
                "missing_credentials": missing_creds,
                "aws_region": os.environ.get("AWS_REGION", "not set")
            }
    except Exception as e:
        logger.error(f"Error checking AWS credentials: {str(e)}")
        return {
            "success": False,
            "error": f"Error checking AWS credentials: {str(e)}"
        }

# Get SQL examples tool
@registry.tool(
    name="get_sql_examples",
    description="Get example SQL queries for the patent databases",
    param_schema="""
    {
        "type": "object",
        "properties": {
            "db_type": {
                "type": "string",
                "description": "Database to get examples for",
                "enum": ["inpit", "google_patents_gcp", "google_patents_s3"],
                "default": "inpit"
            }
        }
    }
    """
)
async def get_sql_examples(params: Dict[str, str]) -> Dict[str, Any]:
    """Get example SQL queries for the specified patent database."""
    db_type = params.get("db_type", "inpit")
    
    examples = {
        "inpit": {
            "basic": "SELECT * FROM inpit_data LIMIT 10;",
            "applicant": "SELECT * FROM inpit_data WHERE applicant_name LIKE '%テック%' ORDER BY application_date DESC LIMIT 20;",
            "date": "SELECT * FROM inpit_data WHERE application_date BETWEEN '2022-01-01' AND '2023-12-31' ORDER BY application_date DESC LIMIT 20;",
            "count": "SELECT strftime('%Y', application_date) as year, COUNT(*) as application_count FROM inpit_data GROUP BY strftime('%Y', application_date) ORDER BY year DESC;"
        },
        "google_patents_gcp": {
            "basic": "SELECT publication_number, title_ja, publication_date, assignee_harmonized FROM publications LIMIT 10;",
            "title": "SELECT publication_number, title_ja, abstract_ja, assignee_harmonized, publication_date FROM publications WHERE title_ja LIKE '%人工知能%' OR title_ja LIKE '%AI%' ORDER BY publication_date DESC LIMIT 15;",
            "family": "SELECT p.publication_number, p.title_ja, p.publication_date, p.assignee_harmonized, p.family_id, COUNT(pf.publication_number) as family_size FROM publications p JOIN patent_families pf ON p.family_id = pf.family_id GROUP BY p.family_id HAVING family_size > 2 ORDER BY family_size DESC LIMIT 15;",
            "year": "SELECT substr(publication_date, 1, 4) as year, COUNT(*) as patent_count FROM publications GROUP BY substr(publication_date, 1, 4) ORDER BY year DESC;"
        },
        "google_patents_s3": {
            "basic": "SELECT publication_number, title_ja, abstract_ja, publication_date, assignee_harmonized FROM publications WHERE country_code = 'JP' ORDER BY publication_date DESC LIMIT 10;",
            "ai": "SELECT publication_number, title_ja, abstract_ja, publication_date, assignee_harmonized FROM publications WHERE (title_ja LIKE '%AI%' OR title_ja LIKE '%人工知能%' OR title_ja LIKE '%機械学習%') AND country_code = 'JP' ORDER BY publication_date DESC LIMIT 15;",
            "ipc": "SELECT p.publication_number, p.title_ja, p.ipc_code, p.publication_date, p.assignee_harmonized FROM publications p WHERE p.ipc_code LIKE 'G06N%' ORDER BY p.publication_date DESC LIMIT 15;",
            "trend": "SELECT substr(publication_date, 1, 4) as year, CASE WHEN ipc_code LIKE 'G06N%' THEN 'AI/機械学習' WHEN ipc_code LIKE 'H04L%' THEN 'ネットワーク通信' ELSE 'その他' END as technology_field, COUNT(*) as count FROM publications WHERE publication_date IS NOT NULL GROUP BY year, technology_field ORDER BY year DESC, count DESC;"
        }
    }
    
    if db_type in examples:
        return {
            "success": True,
            "db_type": db_type,
            "examples": examples[db_type]
        }
    else:
        return {
            "success": False,
            "error": f"No examples found for database type '{db_type}'"
        }

# Natural Language Query Tool implementation
@registry.tool(
    name="patent_nl_query",
    description="Execute a natural language query against the patent database using AWS Bedrock LLM",
    param_schema="""
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language question about patents in Japanese or English"
            },
            "db_type": {
                "type": "string",
                "description": "Database to query: 'inpit', 'google_patents_gcp', or 'google_patents_s3'",
                "enum": ["inpit", "google_patents_gcp", "google_patents_s3"],
                "default": "inpit"
            }
        },
        "required": ["query"]
    }
    """
)
async def patent_nl_query(params) -> Dict[str, Any]:
    """Execute a natural language query against the patent database using AWS Bedrock LLM."""
    try:
        # Handle both dictionary and NLQueryParams object
        # For dictionary access (MCPサーバー経由の呼び出し)
        if isinstance(params, dict):
            query = params.get('query')
            db_type = params.get('db_type', 'inpit')
        # For NLQueryParams object (直接的なAPIアクセス)
        else:
            query = params.query
            db_type = params.db_type
            
        logger.info(f"Executing natural language query: {query} on {db_type}")
        
        # Get NL processor
        nl_processor = get_nl_processor()
        
        # Check if AWS is configured first
        if not nl_processor.is_aws_configured:
            return {
                "success": False,
                "error": "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_REGIONが適切に設定されていることを確認してください。"
            }
            
        # Process the query
        result = await nl_processor.process_query(query, db_type)
        
        # Return the result
        return result
    except Exception as e:
        logger.error(f"Error executing natural language query: {str(e)}")
        return {
            "success": False,
            "error": f"Error executing natural language query: {str(e)}"
        }

# Direct REST API endpoint for natural language queries
@app.post("/api/nl-query")
async def nl_query(params: NLQueryParams):
    """Direct REST API endpoint for natural language queries."""
    return await patent_nl_query(params)

# Register MCP routes using the registry
app = registry.mount_to_app(app)

# Direct REST API endpoint for checking AWS credentials
@app.get("/api/aws-status")
async def aws_status():
    """Check AWS credential status."""
    return await check_aws_credentials({})

# Default route
@app.get("/")
async def root():
    """Root endpoint for the Patent DWH MCP server."""
    return {
        "name": "patentDWH MCP Server",
        "description": "MCP Server for accessing patent databases via SQLite",
        "version": "1.0.0",
        "tools": [
            {
                "name": "patent_sql_query",
                "description": "Execute a SQL query on the patent database"
            },
            {
                "name": "patent_nl_query",
                "description": "Execute a natural language query against the patent database using AWS Bedrock LLM"
            },
            {
                "name": "check_aws_credentials",
                "description": "Check if AWS credentials are properly configured for Bedrock services"
            },
            {
                "name": "get_database_info", 
                "description": "Get information about the available patent databases"
            },
            {
                "name": "get_sql_examples",
                "description": "Get example SQL queries for the patent databases"
            }
        ]
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for the Patent DWH MCP server."""
    try:
        # Get AWS credential status
        aws_creds = await check_aws_credentials({})
        
        # Check connection to the patent database
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PATENT_DB_URL}/health", timeout=5.0)
            if response.status_code == 200:
                status = {
                    "status": "healthy", 
                    "message": "MCP Server is running and can connect to the patent database",
                    "aws_status": aws_creds
                }
                
                # Check if AWS credentials are configured properly
                if not aws_creds.get("success", False):
                    status["status"] = "degraded"
                    status["message"] += ", but AWS Bedrock services are not available"
                    
                return status
            else:
                return {
                    "status": "degraded", 
                    "message": f"MCP Server is running but cannot connect to the patent database: {response.text}",
                    "aws_status": aws_creds
                }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "degraded", 
            "message": f"MCP Server is running but cannot connect to the patent database: {str(e)}",
            "aws_credentials": {
                "success": False,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
