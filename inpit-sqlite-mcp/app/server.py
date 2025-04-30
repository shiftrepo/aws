#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inpit SQLite MCP Server

This server provides MCP (Model Context Protocol) functionality for interacting with
the Inpit SQLite database service. It enables Claude to query patent data directly.
"""

import os
import sys
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Import the MCP module
try:
    from inpit_sqlite_mcp import (
        get_tools,
        get_resources,
        execute_tool,
        access_resource
    )
    print("Successfully imported Inpit SQLite MCP module")
except ImportError as e:
    print(f"Failed to import Inpit SQLite MCP module: {e}")
    sys.exit(1)

app = FastAPI(title="Inpit SQLite MCP Server")

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ResourceRequest(BaseModel):
    uri: str

@app.get("/")
async def root():
    """Root endpoint to check server status"""
    return {
        "status": "ok", 
        "message": "Inpit SQLite MCP Server is running",
        "service": "Inpit SQLite Database API"
    }

@app.get("/tools")
async def list_tools():
    """List available Inpit SQLite tools"""
    try:
        tools = get_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

@app.get("/resources")
async def list_resources():
    """List available Inpit SQLite resources"""
    try:
        resources = get_resources()
        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing resources: {str(e)}")

@app.post("/tools/execute")
async def execute_inpit_tool(request: ToolRequest):
    """Execute an Inpit SQLite tool"""
    try:
        tool_name = request.tool_name
        arguments = request.arguments
        
        # Convert arguments to JSON string if needed by the MCP module
        args_json = json.dumps(arguments)
        
        result = execute_tool(tool_name, args_json)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

@app.post("/resources/access")
async def access_inpit_resource(request: ResourceRequest):
    """Access an Inpit SQLite resource"""
    try:
        uri = request.uri
        result = access_resource(uri)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing resource: {str(e)}")

# Convenience endpoints for specific tools

@app.get("/application/{application_number}")
async def get_patent_by_app_number(application_number: str):
    """
    Get patent information by application number.
    
    When using non-ASCII characters, ensure the URL is properly encoded.
    """
    try:
        args = {"application_number": application_number}
        result = execute_tool("get_patent_by_application_number", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patent by application number: {str(e)}")

@app.get("/applicant/{applicant_name}")
async def get_patents_by_applicant(applicant_name: str):
    """
    Get patent information by applicant name.
    
    When using non-ASCII characters, ensure the URL is properly encoded.
    """
    try:
        args = {"applicant_name": applicant_name}
        result = execute_tool("get_patents_by_applicant", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patents by applicant: {str(e)}")

@app.post("/sql")
async def execute_sql(query: str):
    """
    Execute an SQL query against the Inpit SQLite database.
    Only SELECT queries are allowed.
    """
    try:
        args = {"query": query}
        result = execute_tool("execute_sql_query", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {str(e)}")

@app.get("/status")
async def get_status():
    """
    Get the status and schema information of the Inpit SQLite database.
    """
    try:
        result = access_resource("inpit-sqlite://status")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting database status: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Print server startup information
    print(f"Starting Inpit SQLite MCP Server on port {port}")
    print(f"API URL: {os.environ.get('INPIT_API_URL', 'http://localhost:5001')}")
    
    # Run the server
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
