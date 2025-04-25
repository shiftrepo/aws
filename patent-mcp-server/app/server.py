import os
import sys
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the MCP server module
try:
    from app.patent_system.mcp_patent_server import (
        get_tools,
        get_resources,
        execute_tool,
        access_resource
    )
    print("Successfully imported patent MCP server module")
except ImportError as e:
    print(f"Failed to import patent MCP server module: {e}")
    sys.exit(1)

app = FastAPI(title="Patent MCP Server")

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ResourceRequest(BaseModel):
    uri: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "Patent MCP Server is running"}

@app.get("/tools")
async def list_tools():
    """List available patent analysis tools"""
    try:
        tools = get_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

@app.get("/resources")
async def list_resources():
    """List available patent resources"""
    try:
        resources = get_resources()
        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing resources: {str(e)}")

@app.post("/tools/execute")
async def execute_patent_tool(request: ToolRequest):
    """Execute a patent analysis tool"""
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
async def access_patent_resource(request: ResourceRequest):
    """Access a patent resource"""
    try:
        uri = request.uri
        result = access_resource(uri)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing resource: {str(e)}")

# Convenience endpoints for specific tools

@app.get("/applicant/{applicant_name}")
async def get_applicant_summary(applicant_name: str):
    """
    Get a summary for the specified applicant.
    
    When using non-ASCII characters (like Japanese), ensure the URL is properly encoded.
    For example, to query for "テック株式会社" with curl, use:
    curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
    """
    try:
        args = {"applicant_name": applicant_name}
        result = execute_tool("get_applicant_summary", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applicant summary: {str(e)}")

@app.get("/report/{applicant_name}")
async def generate_report(applicant_name: str):
    """
    Generate a visual report for the specified applicant.
    
    When using non-ASCII characters (like Japanese), ensure the URL is properly encoded.
    For example, to query for "テック株式会社" with curl, use:
    curl "http://localhost:8000/report/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
    """
    try:
        args = {"applicant_name": applicant_name}
        result = execute_tool("generate_visual_report", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/assessment/{applicant_name}")
async def analyze_assessment(applicant_name: str):
    """
    Analyze assessment ratios for the specified applicant.
    
    When using non-ASCII characters (like Japanese), ensure the URL is properly encoded.
    For example, to query for "テック株式会社" with curl, use:
    curl "http://localhost:8000/assessment/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
    """
    try:
        args = {"applicant_name": applicant_name}
        result = execute_tool("analyze_assessment_ratios", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing assessment: {str(e)}")

@app.get("/technical/{applicant_name}")
async def analyze_technical(applicant_name: str):
    """
    Analyze technical fields for the specified applicant.
    
    When using non-ASCII characters (like Japanese), ensure the URL is properly encoded.
    For example, to query for "テック株式会社" with curl, use:
    curl "http://localhost:8000/technical/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
    """
    try:
        args = {"applicant_name": applicant_name}
        result = execute_tool("analyze_technical_fields", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing technical fields: {str(e)}")

@app.get("/compare/{applicant_name}")
async def compare_competitors(applicant_name: str, num_competitors: int = 3):
    """
    Compare the specified applicant with competitors.
    
    When using non-ASCII characters (like Japanese), ensure the URL is properly encoded.
    For example, to query for "テック株式会社" with curl, use:
    curl "http://localhost:8000/compare/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
    
    Optional query parameter:
    - num_competitors: Number of competitors to compare with (default: 3)
    """
    try:
        args = {"applicant_name": applicant_name, "num_competitors": num_competitors}
        result = execute_tool("compare_with_competitors", args)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing with competitors: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
