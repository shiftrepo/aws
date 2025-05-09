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
import fastapi
from fastapi import FastAPI, HTTPException, Form, Body, Depends
from urllib.parse import unquote
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import ssl

# Import our custom middleware for URL encoding
from encoding_middleware import URLEncodingMiddleware

# Import the patents API router
from patents_api import router as patents_router

# Import the MCP modules
try:
    from inpit_sqlite_mcp import (
        get_tools as get_inpit_tools,
        get_resources as get_inpit_resources,
        execute_tool as execute_inpit_tool,
        access_resource as access_inpit_resource
    )
    print("Successfully imported Inpit SQLite MCP module")
except ImportError as e:
    print(f"Failed to import Inpit SQLite MCP module: {e}")
    sys.exit(1)

# Import natural language query MCP modules
try:
    from nl_query_mcp import (
        get_tools as get_nl_tools,
        get_resources as get_nl_resources,
        execute_tool as execute_nl_tool,
        access_resource as access_nl_resource
    )
    print("Successfully imported Natural Language Query MCP module")
except ImportError as e:
    print(f"Failed to import Natural Language Query MCP module: {e}")
    # Continue without rule-based NL query support

# Import Bedrock natural language query MCP module
try:
    from bedrock_nl_query_mcp import (
        get_tools as get_bedrock_nl_tools,
        get_resources as get_bedrock_nl_resources,
        execute_tool as execute_bedrock_nl_tool,
        access_resource as access_bedrock_nl_resource
    )
    print("Successfully imported Bedrock Natural Language Query MCP module")
except ImportError as e:
    print(f"Failed to import Bedrock Natural Language Query MCP module: {e}")
    # Continue without Bedrock NL query support

# Combined tools and resources functions
def get_tools():
    """Get all available tools from imported modules"""
    tools = get_inpit_tools()
    
    # Add rule-based NL query tools
    try:
        nl_tools = get_nl_tools()
        tools.extend(nl_tools)
    except Exception as e:
        print(f"Error getting rule-based NL query tools: {e}")
    
    # Add Bedrock NL query tools
    try:
        bedrock_nl_tools = get_bedrock_nl_tools()
        tools.extend(bedrock_nl_tools)
    except Exception as e:
        print(f"Error getting Bedrock NL query tools: {e}")
        
    return tools

def get_resources():
    """Get all available resources from imported modules"""
    resources = get_inpit_resources()
    
    # Add rule-based NL query resources
    try:
        nl_resources = get_nl_resources()
        resources.extend(nl_resources)
    except Exception as e:
        print(f"Error getting rule-based NL query resources: {e}")
    
    # Add Bedrock NL query resources
    try:
        bedrock_nl_resources = get_bedrock_nl_resources()
        resources.extend(bedrock_nl_resources)
    except Exception as e:
        print(f"Error getting Bedrock NL query resources: {e}")
        
    return resources

def execute_tool(tool_name, arguments):
    """Execute a tool from any of the available modules"""
    # Rule-based natural language query tools
    if tool_name in ["nl_query_inpit_database", "nl_query_google_patents_database"]:
        try:
            return execute_nl_tool(tool_name, arguments)
        except Exception as e:
            print(f"Error executing rule-based NL query tool {tool_name}: {e}")
            return {"error": str(e)}
    
    # Bedrock natural language query tools
    if tool_name in ["bedrock_nl_query_inpit_database", "bedrock_nl_query_google_patents_database"]:
        try:
            return execute_bedrock_nl_tool(tool_name, arguments)
        except Exception as e:
            print(f"Error executing Bedrock NL query tool {tool_name}: {e}")
            return {"error": str(e)}
    
    # Default to inpit_sqlite_mcp tools
    return execute_inpit_tool(tool_name, arguments)

def access_resource(uri):
    """Access a resource from any of the available modules"""
    # Rule-based natural language query resources
    if uri.startswith("nl-query://"):
        try:
            return access_nl_resource(uri)
        except Exception as e:
            print(f"Error accessing rule-based NL query resource {uri}: {e}")
            return {"error": str(e)}
    
    # Bedrock natural language query resources
    if uri.startswith("bedrock-nl-query://"):
        try:
            return access_bedrock_nl_resource(uri)
        except Exception as e:
            print(f"Error accessing Bedrock NL query resource {uri}: {e}")
            return {"error": str(e)}
    
    # Default to inpit_sqlite_mcp resources
    return access_inpit_resource(uri)

app = FastAPI(title="Inpit SQLite MCP Server")

# Add middleware for handling URL encoding of non-ASCII characters
app.add_middleware(URLEncodingMiddleware)

# Include the patents API router
app.include_router(patents_router)

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

@app.get("/application/{application_number:path}")
async def get_patent_by_app_number(application_number: str):
    """
    Get patent information by application number.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_number = unquote(application_number)
        args = {"application_number": decoded_number}
        result = execute_tool("get_patent_by_application_number", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patent by application number: {str(e)}")

@app.get("/applicant/{applicant_name:path}")
async def get_patents_by_applicant(applicant_name: str):
    """
    Get patent information by applicant name.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("get_patents_by_applicant", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patents by applicant: {str(e)}")

@app.post("/applicant")
async def post_patents_by_applicant(request: fastapi.Request):
    """
    Get patent information by applicant name using POST method.
    
    This endpoint demonstrates handling URL-encoded Japanese text in form data.
    
    Form data:
    - name: The applicant name (can include Japanese characters and spaces)
    """
    try:
        # Get form data
        form_data = await request.form()
        applicant_name = form_data.get("name")
        
        if not applicant_name:
            raise HTTPException(status_code=400, detail="Name parameter is required")
        
        # Form data should already be decoded by FastAPI
        args = {"applicant_name": applicant_name}
        result = execute_tool("get_patents_by_applicant", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patents by applicant: {str(e)}")

@app.get("/applicant-summary/{applicant_name:path}")
async def get_applicant_summary(applicant_name: str):
    """
    Get comprehensive summary for a specific patent applicant.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("get_applicant_summary", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applicant summary: {str(e)}")

@app.get("/visual-report/{applicant_name:path}")
async def generate_visual_report(applicant_name: str):
    """
    Generate a visual report with charts and statistics for the specified applicant.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("generate_visual_report", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visual report: {str(e)}")

@app.get("/assessment/{applicant_name:path}")
async def analyze_assessment_ratios(applicant_name: str):
    """
    Analyze patent assessment ratios for the specified applicant.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("analyze_assessment_ratios", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing assessment ratios: {str(e)}")

@app.get("/technical/{applicant_name:path}")
async def analyze_technical_fields(applicant_name: str):
    """
    Analyze technical field distribution for the specified applicant.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("analyze_technical_fields", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing technical fields: {str(e)}")

@app.get("/compare/{applicant_name:path}")
async def compare_with_competitors(applicant_name: str, num_competitors: int = 3):
    """
    Compare the specified applicant with competitors.
    
    Non-ASCII characters are automatically handled.
    
    Optional query parameter:
    - num_competitors: Number of competitors to compare with (default: 3)
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {
            "applicant_name": decoded_name,
            "num_competitors": num_competitors
        }
        result = execute_tool("compare_with_competitors", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing with competitors: {str(e)}")

@app.get("/pdf-report/{applicant_name:path}")
async def generate_pdf_report(applicant_name: str):
    """
    Generate a PDF report for the specified applicant.
    
    Non-ASCII characters are automatically handled.
    """
    try:
        # 受け取ったパスパラメータをデコードして処理
        decoded_name = unquote(applicant_name)
        args = {"applicant_name": decoded_name}
        result = execute_tool("generate_pdf_report", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")

@app.post("/nl-query/inpit")
async def nl_query_inpit(request: fastapi.Request):
    """
    Execute a natural language query against the Inpit database.
    
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
        result = execute_tool("nl_query_inpit_database", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {str(e)}")

@app.post("/nl-query/inpit/json")
async def nl_query_inpit_json(query: str = Body(..., embed=True)):
    """
    Execute a natural language query against the Inpit database using JSON request.
    
    JSON body:
    - query: The natural language query text
    """
    try:
        args = {"query": query}
        result = execute_tool("nl_query_inpit_database", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing natural language query: {str(e)}")

@app.post("/nl-query/google-patents")
async def nl_query_google_patents(request: fastapi.Request):
    """
    Execute a natural language query against the Google Patents database.
    
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
        result = execute_tool("nl_query_google_patents_database", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing natural language query: {str(e)}")

@app.post("/nl-query/google-patents/json")
async def nl_query_google_patents_json(query: str = Body(..., embed=True)):
    """
    Execute a natural language query against the Google Patents database using JSON request.
    
    JSON body:
    - query: The natural language query text
    """
    try:
        args = {"query": query}
        result = execute_tool("nl_query_google_patents_database", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing natural language query: {str(e)}")

@app.get("/nl-query/help/inpit")
async def nl_query_help_inpit():
    """
    Get help information for natural language querying of INPIT database.
    """
    try:
        result = access_resource("nl-query://inpit/help")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting NL query help: {str(e)}")

@app.get("/nl-query/help/google-patents")
async def nl_query_help_google_patents():
    """
    Get help information for natural language querying of Google Patents database.
    """
    try:
        result = access_resource("nl-query://google-patents/help")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting NL query help: {str(e)}")

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

@app.post("/bedrock-nl-query/inpit/json")
async def bedrock_nl_query_inpit_json(query: str = Body(..., embed=True)):
    """
    Execute a natural language query against the Inpit database using AWS Bedrock and JSON request.
    
    JSON body:
    - query: The natural language query text
    """
    try:
        args = {"query": query}
        result = execute_tool("bedrock_nl_query_inpit_database", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing Bedrock natural language query: {str(e)}")

@app.post("/bedrock-nl-query/google-patents")
async def bedrock_nl_query_google_patents(request: fastapi.Request):
    """
    Execute a natural language query against the Google Patents database using AWS Bedrock.
    
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
        result = execute_tool("bedrock_nl_query_google_patents_database", args)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing Bedrock natural language query: {str(e)}")

@app.post("/bedrock-nl-query/google-patents/json")
async def bedrock_nl_query_google_patents_json(query: str = Body(..., embed=True)):
    """
    Execute a natural language query against the Google Patents database using AWS Bedrock and JSON request.
    
    JSON body:
    - query: The natural language query text
    """
    try:
        args = {"query": query}
        result = execute_tool("bedrock_nl_query_google_patents_database", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing Bedrock natural language query: {str(e)}")

@app.get("/bedrock-nl-query/help/inpit")
async def bedrock_nl_query_help_inpit():
    """
    Get help information for Bedrock-powered natural language querying of INPIT database.
    """
    try:
        result = access_resource("bedrock-nl-query://inpit/help")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Bedrock NL query help: {str(e)}")

@app.get("/bedrock-nl-query/help/google-patents")
async def bedrock_nl_query_help_google_patents():
    """
    Get help information for Bedrock-powered natural language querying of Google Patents database.
    """
    try:
        result = access_resource("bedrock-nl-query://google-patents/help")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Bedrock NL query help: {str(e)}")

@app.post("/sql")
async def execute_sql(request: fastapi.Request):
    """
    Execute an SQL query against the Inpit SQLite database.
    Only SELECT queries are allowed.
    
    Form data:
    - query: The SQL query to execute (must be a SELECT statement)
    """
    try:
        # Get form data
        form_data = await request.form()
        query = form_data.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        args = {"query": query}
        result = execute_tool("execute_sql_query", args)
        return result
    except HTTPException as e:
        raise e
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

@app.post("/sql/json")
async def execute_sql_json(query: str = Body(..., embed=True)):
    """
    Execute an SQL query against the Inpit SQLite database using JSON request.
    Only SELECT queries are allowed.
    
    JSON body:
    - query: The SQL query to execute (must be a SELECT statement)
    """
    try:
        args = {"query": query}
        result = execute_tool("execute_sql_query", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Print server startup information
    print(f"Starting Inpit SQLite MCP Server on port {port}")
    print(f"API URL: {os.environ.get('INPIT_API_URL', 'http://localhost:5001')}")
    
    # Log available tools
    try:
        tools = get_tools()
        print(f"Available tools: {', '.join([t['name'] for t in tools])}")
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Run the server
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
