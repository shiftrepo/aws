import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="Patent Analysis MCP Server", 
              description="MCP server for patent application trend analysis",
              version="1.0.0")

# Define request models for OpenAPI
class PatentAnalysisRequest(BaseModel):
    applicant_name: str
    db_type: Optional[str] = "sqlite"

class MCPToolRequest(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]

# Output directory for generated files
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "message": "Patent Analysis MCP Server is running in simple mode",
        "system_info": {
            "python_path": os.environ.get("PYTHONPATH", "Not set"),
            "current_working_directory": os.getcwd(),
            "output_dir": OUTPUT_DIR
        }
    }

@app.post("/api/v1/mcp")
async def mcp_endpoint(request: MCPToolRequest):
    """MCP compatible endpoint that handles tool requests"""
    try:
        tool_name = request.tool_name
        tool_input = request.tool_input
        
        if tool_name == "analyze_patent_trends":
            applicant_name = tool_input.get("applicant_name")
            
            if not applicant_name:
                return {"success": False, "error": "applicant_name is required"}
            
            # Simple response for debugging
            result = {
                "summary": f"Patent trend analysis for {applicant_name} would appear here.",
                "system_info": {}
            }
            
            # Try to safely get directory listings
            try:
                if os.path.exists("/app"):
                    result["system_info"]["directory_listing"] = os.listdir("/app")
            except Exception as e:
                result["system_info"]["directory_error"] = str(e)
                
            try:
                if os.path.exists("/app/app"):
                    result["system_info"]["app_directory"] = os.listdir("/app/app")
            except Exception as e:
                result["system_info"]["app_directory_error"] = str(e)
                
            try:
                if os.path.exists("/app/app/patent_system"):
                    result["system_info"]["patent_system_directory"] = os.listdir("/app/app/patent_system")
            except Exception as e:
                result["system_info"]["patent_system_directory_error"] = str(e)
            
            return {"success": True, "response": result}
        else:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting simple server on {host}:{port}")
    uvicorn.run("patent_analysis_simple:app", host=host, port=port, reload=True)
