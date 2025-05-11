#!/usr/bin/env python3
"""
Enhanced patentDWH MCP server with LangChain prioritization option

This module provides a FastAPI server for patentDWH with Model Context Protocol (MCP)
integration and enhanced natural language processing capabilities with LangChain option.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
import urllib.parse

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import the enhanced NL query processor
from enhanced_nl_query_processor import get_enhanced_nl_processor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
PORT = int(os.environ.get("PORT", "8080"))
PATENT_DB_URL = os.environ.get("PATENT_DB_URL", "http://patentdwh-db:5002")

# Create FastAPI app
app = FastAPI(
    title="patentDWH MCP Server",
    description="MCP server providing patent database access with enhanced NL query capabilities",
    version="1.1.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the enhanced NL processor
nl_processor = None

# MCP Tool model
class MCPToolRequest(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]

# Models for NL query
class NLQueryRequest(BaseModel):
    query: str
    db_type: str = "inpit"
    use_langchain_first: bool = False

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint that verifies the server is running and can connect to the database."""
    global nl_processor
    
    # Initialize NL processor if not already done
    if nl_processor is None:
        nl_processor = get_enhanced_nl_processor()
        
    # Check database connection
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:  # Longer timeout
            response = await client.get(f"{PATENT_DB_URL}/health")
            db_connected = response.status_code == 200
    except Exception as e:
        logger.error(f"Health check error connecting to DB: {str(e)}")
        db_connected = False
    
    status = "healthy" if db_connected else "degraded"
    return {
        "status": status, 
        "service": "patentDWH-MCP", 
        "database_connected": db_connected,
        "aws_configured": nl_processor.is_aws_configured if nl_processor else False
    }

# Server status endpoint
@app.get("/api/status")
async def server_status():
    """Get server status and database information."""
    global nl_processor
    
    # Initialize NL processor if not already done
    if nl_processor is None:
        nl_processor = get_enhanced_nl_processor()
    
    # Check if AWS is configured
    aws_configured = nl_processor.is_aws_configured
    
    # Get database status
    try:
        import httpx
        response = await httpx.AsyncClient().get(f"{PATENT_DB_URL}/api/status")
        if response.status_code == 200:
            db_status = response.json()
        else:
            db_status = {"error": f"Failed to connect to database service: {response.text}"}
    except Exception as e:
        db_status = {"error": f"Error connecting to database service: {str(e)}"}
    
    return {
        "status": "running",
        "aws_configured": aws_configured,
        # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
        "aws_region": os.environ.get("AWS_DEFAULT_REGION", "not set"),
        "database_url": PATENT_DB_URL,
        "database_status": db_status,
        "enhanced_nl": True,
        "langchain_support": True
    }

# MCP API endpoint
@app.post("/api/v1/mcp")
async def mcp_endpoint(request: MCPToolRequest):
    """Model Context Protocol (MCP) endpoint for tool execution."""
    global nl_processor
    
    # Initialize NL processor if not already done
    if nl_processor is None:
        nl_processor = get_enhanced_nl_processor()
    
    tool_name = request.tool_name
    tool_input = request.tool_input
    
    try:
        # Handle different tools
        if tool_name == "patent_nl_query":
            # Natural language query tool
            query = tool_input.get("query", "")
            db_type = tool_input.get("db_type", "inpit")
            use_langchain_first = tool_input.get("use_langchain_first", False)
            
            if not query:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Query is required"}
                )
                
            result = await nl_processor.process_query(query, db_type, use_langchain_first)
            return result
            
        elif tool_name == "patent_sql_query":
            # Direct SQL query tool
            query = tool_input.get("query", "")
            db_type = tool_input.get("db_type", "inpit")
            
            if not query:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Query is required"}
                )
                
            # Forward the SQL query to the database service
            import httpx
            response = await httpx.AsyncClient().post(
                f"{PATENT_DB_URL}/api/sql-query",
                json={"query": query, "db_type": db_type}
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"success": False, "error": response.text}
                )
                
            return response.json()
            
        elif tool_name == "check_aws_credentials":
            # Check AWS credentials
            if nl_processor.is_aws_configured:
                return {
                    "success": True,
                    "message": "AWS credentials are correctly configured for Bedrock services",
                    # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
                    "aws_region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
                }
            else:
                return {
                    "success": False,
                    "message": "AWS credentials are not configured properly",
                    # Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
                    "error": "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, or AWS_DEFAULT_REGION environment variables are not set correctly"
                }
                
        elif tool_name == "get_database_info":
            # Get database info
            db_type = tool_input.get("db_type")
            
            import httpx
            response = await httpx.AsyncClient().get(f"{PATENT_DB_URL}/api/status")
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"success": False, "error": response.text}
                )
                
            db_info = response.json()
            
            if db_type and db_type in db_info.get("databases", {}):
                return {
                    "success": True,
                    "database_info": {db_type: db_info["databases"][db_type]}
                }
            else:
                return {
                    "success": True,
                    "database_info": db_info.get("databases", {})
                }
                
        elif tool_name == "get_sql_examples":
            # Get SQL examples for the specified database type
            db_type = tool_input.get("db_type")
            
            if not db_type:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Database type is required"}
                )
                
            import httpx
            response = await httpx.AsyncClient().post(
                f"{PATENT_DB_URL}/api/v1/mcp",
                json={
                    "tool_name": "get_sql_examples",
                    "tool_input": {"db_type": db_type}
                }
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"success": False, "error": response.text}
                )
                
            return response.json()
                
        else:
            # Unknown tool
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Unknown tool: {tool_name}"}
            )
            
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error executing tool: {str(e)}"}
        )

# Natural language query API endpoint
@app.post("/api/nl-query")
async def nl_query(request: NLQueryRequest):
    """Process a natural language query with optional LangChain prioritization."""
    global nl_processor
    
    # Initialize NL processor if not already done
    if nl_processor is None:
        nl_processor = get_enhanced_nl_processor()
        
    try:
        result = await nl_processor.process_query(
            request.query, 
            request.db_type, 
            request.use_langchain_first
        )
        return result
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing query: {str(e)}"}
        )

# Root path
@app.get("/")
async def root():
    """Root path that returns basic information about the server."""
    return {
        "service": "patentDWH MCP Server",
        "version": "1.1.0",
        "enhanced_nl": True,
        "langchain_support": True,
        "docs": "/docs"
    }

# Initialize the server using lifespan event handler instead of deprecated on_event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources when the application starts and handle cleanup when it shuts down."""
    global nl_processor
    try:
        # Initialize the enhanced NL processor
        nl_processor = get_enhanced_nl_processor()
        logger.info("Enhanced NL processor initialized")
    except Exception as e:
        logger.error(f"Error initializing NL processor: {e}")
    
    yield  # This is where FastAPI serves requests
    
    # Cleanup (if needed) when application shuts down
    # No specific cleanup needed for this application

# Apply the lifespan to the app
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=PORT)
