import os
import logging
import json
import time
from typing import List, Dict, Any, Optional

import httpx
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SQLITE_API_URL = os.environ.get("SQLITE_API_URL", "http://localhost:5001")
MCP_API_URL = os.environ.get("MCP_API_URL", "http://localhost:8000")

# FastAPI app
app = FastAPI(
    title="SQLite Database UI",
    description="Web UI for SQLite database with natural language query support",
    version="1.0.0"
)

# Setup static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static directory mounted successfully")
except Exception as e:
    logger.error(f"Error mounting static directory: {e}")

# Setup templates
try:
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates directory setup successfully")
except Exception as e:
    logger.error(f"Error setting up templates: {e}")
    templates = None

# Models
class QueryRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None

class NLQueryRequest(BaseModel):
    query: str
    max_results: int = 20

# ------------------ Helper Functions ------------------

async def get_database_schema() -> dict:
    """Fetch database schema from SQLite API"""
    logger.info("Fetching database schema")
    try:
        async with httpx.AsyncClient() as client:
            # Fetch list of tables
            tables_resp = await client.get(f"{SQLITE_API_URL}/tables")
            tables_resp.raise_for_status()
            tables_data = tables_resp.json()
            
            schema = {}
            
            # Fetch details for each table
            for table_name in tables_data["tables"]:
                table_resp = await client.get(f"{SQLITE_API_URL}/tables/{table_name}")
                table_resp.raise_for_status()
                schema[table_name] = table_resp.json()
            
            logger.info(f"Retrieved schema for {len(schema)} tables")
            return schema
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database schema: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching schema: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")

async def get_sample_queries() -> List[Dict[str, str]]:
    """Fetch sample SQL queries from SQLite API"""
    logger.info("Fetching sample queries")
    try:
        async with httpx.AsyncClient() as client:
            sample_resp = await client.get(f"{SQLITE_API_URL}/sample_queries")
            sample_resp.raise_for_status()
            sample_data = sample_resp.json()
            
            logger.info(f"Retrieved {len(sample_data.get('sample_queries', []))} sample queries")
            return sample_data.get("sample_queries", [])
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching sample queries: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching sample queries: {e}")
        return []

async def get_nl_sample_queries() -> List[str]:
    """Fetch sample natural language queries from MCP API"""
    logger.info("Fetching NL sample queries")
    try:
        async with httpx.AsyncClient() as client:
            sample_resp = await client.get(f"{MCP_API_URL}/sample_queries")
            sample_resp.raise_for_status()
            sample_data = sample_resp.json()
            
            logger.info(f"Retrieved {len(sample_data.get('sample_queries', []))} NL sample queries")
            return sample_data.get("sample_queries", [])
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching NL sample queries: {e}")
        return ["Show all tables", "Count records in each table"]
    except Exception as e:
        logger.error(f"Unexpected error while fetching NL sample queries: {e}")
        return ["Show all tables", "Count records in each table"]

async def execute_sql_query(query: str) -> dict:
    """Execute SQL query via SQLite API"""
    logger.info(f"Executing SQL query: {query}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SQLITE_API_URL}/execute",
                json={"query": query}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Query executed successfully, returned {len(result.get('rows', []))} rows")
            return result
    except httpx.HTTPError as e:
        logger.error(f"HTTP error executing SQL query: {e}")
        if e.response is not None:
            error_detail = e.response.text
            logger.error(f"Error response: {error_detail}")
            return {"error": error_detail, "query": query}
        return {"error": str(e), "query": query}
    except Exception as e:
        logger.error(f"Unexpected error executing SQL query: {e}")
        return {"error": str(e), "query": query}

async def execute_nl_query(nl_query: str, max_results: int = 20) -> dict:
    """Execute natural language query via MCP API"""
    logger.info(f"Executing NL query: {nl_query}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_API_URL}/query",
                json={"query": nl_query, "max_results": max_results}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"NL query executed successfully")
            return result
    except httpx.HTTPError as e:
        logger.error(f"HTTP error executing NL query: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
            except:
                error_detail = {"error": e.response.text}
            logger.error(f"Error response: {error_detail}")
            return {"error": error_detail, "nl_query": nl_query}
        return {"error": str(e), "nl_query": nl_query}
    except Exception as e:
        logger.error(f"Unexpected error executing NL query: {e}")
        return {"error": str(e), "nl_query": nl_query}

# ------------------ Route Handlers ------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with SQL query interface"""
    try:
        schema = await get_database_schema()
        sample_queries = await get_sample_queries()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "SQL Query Interface",
                "schema": schema,
                "sample_queries": sample_queries,
                "active_tab": "sql"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Error",
                "error": str(e)
            }
        )

@app.get("/schema", response_class=HTMLResponse)
async def schema_page(request: Request):
    """Page displaying database schema"""
    try:
        schema = await get_database_schema()
        
        return templates.TemplateResponse(
            "schema.html",
            {
                "request": request,
                "title": "Database Schema",
                "schema": schema,
                "active_tab": "schema"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering schema page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Error",
                "error": str(e)
            }
        )

@app.get("/nl-query", response_class=HTMLResponse)
async def nl_query_page(request: Request):
    """Page for natural language queries"""
    try:
        schema = await get_database_schema()
        sample_queries = await get_nl_sample_queries()
        
        return templates.TemplateResponse(
            "nl_query.html",
            {
                "request": request,
                "title": "Natural Language Query",
                "schema": schema,
                "sample_queries": sample_queries,
                "active_tab": "nl-query"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering NL query page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Error",
                "error": str(e)
            }
        )

@app.post("/execute-sql", response_class=JSONResponse)
async def execute_sql(request: QueryRequest):
    """API endpoint to execute SQL queries"""
    query = request.query
    params = request.params or {}
    
    logger.info(f"Received SQL execution request: {query}")
    
    try:
        result = await execute_sql_query(query)
        return result
    except Exception as e:
        logger.error(f"Error in execute_sql endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "query": query}
        )

@app.post("/execute-nl", response_class=JSONResponse)
async def execute_nl(request: NLQueryRequest):
    """API endpoint to execute natural language queries"""
    query = request.query
    max_results = request.max_results
    
    logger.info(f"Received NL execution request: {query}")
    
    try:
        result = await execute_nl_query(query, max_results)
        return result
    except Exception as e:
        logger.error(f"Error in execute_nl endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "nl_query": query}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        services_status = {}
        
        # Check SQLite API
        try:
            async with httpx.AsyncClient() as client:
                sqlite_resp = await client.get(f"{SQLITE_API_URL}/health", timeout=2.0)
                sqlite_resp.raise_for_status()
                services_status["sqlite"] = "connected"
        except Exception as e:
            logger.error(f"SQLite API health check failed: {e}")
            services_status["sqlite"] = f"error: {str(e)}"
        
        # Check MCP API
        try:
            async with httpx.AsyncClient() as client:
                mcp_resp = await client.get(f"{MCP_API_URL}/health", timeout=2.0)
                mcp_resp.raise_for_status()
                services_status["mcp"] = "connected"
        except Exception as e:
            logger.error(f"MCP API health check failed: {e}")
            services_status["mcp"] = f"error: {str(e)}"
        
        status = "healthy" if all(s == "connected" for s in services_status.values()) else "degraded"
        
        return {
            "status": status,
            "services": services_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
