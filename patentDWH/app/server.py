#!/usr/bin/env python3
"""
Patent DWH MCP Server - FastAPI implementation of the Model Context Protocol for patent data warehousing
"""

import os
import json
import logging
import httpx
import pandas as pd
from typing import Dict, List, Any, Optional
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
async def patent_sql_query(params: SQLQueryParams) -> Dict[str, Any]:
    """Execute a SQL query on the patent database."""
    try:
        # Basic validation - only SELECT queries allowed for security
        if not params.query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed for security reasons")

        # Make request to the patent database API
        async with httpx.AsyncClient() as client:
            logger.info(f"Executing query on {params.db_type} database: {params.query}")
            response = await client.post(
                f"{PATENT_DB_URL}/api/sql-query",
                json={"query": params.query, "db_type": params.db_type}
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

# Register MCP routes using the registry
app = registry.mount_to_app(app)

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
        # Check connection to the patent database
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PATENT_DB_URL}/health", timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy", "message": "MCP Server is running and can connect to the patent database"}
            else:
                return {"status": "degraded", "message": f"MCP Server is running but cannot connect to the patent database: {response.text}"}
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "degraded", "message": f"MCP Server is running but cannot connect to the patent database: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
