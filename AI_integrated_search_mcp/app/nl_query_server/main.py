import os
import time
import logging
import json
from typing import Dict, List, Any, Optional

import boto3
import httpx
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# MCP protocol imports
from model_context_protocol import (
    MCPServer, 
    ResourceDefinition, 
    ToolDefinition,
    ResourceProperties,
    ResourceResponse
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SQLITE_API_URL = os.environ.get("SQLITE_API_URL", "http://localhost:5001")
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1")
LLM_MODEL = os.environ.get("LLM_MODEL", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "amazon.titan-embed-text-v2:0")
RERANK_MODEL = os.environ.get("RERANK_MODEL", "amazon.rerank-v1:0")

# Initialize AWS clients
try:
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_DEFAULT_REGION)
    logger.info(f"Connected to AWS Bedrock in region {AWS_DEFAULT_REGION}")
    logger.info(f"Using LLM model: {LLM_MODEL}")
    logger.info(f"Using embedding model: {EMBED_MODEL}")
    logger.info(f"Using reranking model: {RERANK_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize AWS Bedrock client: {e}")
    bedrock_runtime = None

# FastAPI app
app = FastAPI(
    title="Natural Language SQLite Query",
    description="API for querying SQLite database using natural language via AWS Bedrock",
    version="1.0.0"
)

# Create MCP server
mcp_server = MCPServer(
    server_name="nl-sqlite-query",
    server_description="Natural language to SQLite query via AWS Bedrock",
    app=app,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class NLQueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 20
    confidence_threshold: Optional[float] = 0.7

class SQLGenerationRequest(BaseModel):
    nl_query: str
    db_schema: dict

class SQLQueryResponse(BaseModel):
    nl_query: str
    generated_sql: str
    execution_time: float
    confidence_score: float
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ------------------ Helper Functions ------------------

async def get_database_schema() -> dict:
    """Fetch database schema from SQLite API"""
    logger.info("Fetching database schema from SQLite API")
    try:
        async with httpx.AsyncClient() as client:
            # Fetch list of tables
            tables_resp = await client.get(f"{SQLITE_API_URL}/tables")
            tables_resp.raise_for_status()
            tables_data = tables_resp.json()
            
            schema = {"tables": {}}
            
            # Fetch details for each table
            for table_name in tables_data["tables"]:
                table_resp = await client.get(f"{SQLITE_API_URL}/tables/{table_name}")
                table_resp.raise_for_status()
                table_info = table_resp.json()
                
                schema["tables"][table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": col["type"],
                            "nullable": not col["notnull"],
                            "primary_key": col["pk"],
                            "default": col["dflt_value"]
                        }
                        for col in table_info["columns"]
                    ],
                    "row_count": table_info["row_count"]
                }
            
            logger.info(f"Retrieved schema for {len(schema['tables'])} tables")
            return schema
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database schema: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database schema: {str(e)}")

async def generate_sql_using_bedrock(nl_query: str, schema: dict) -> dict:
    """Generate SQL from natural language using AWS Bedrock"""
    if bedrock_runtime is None:
        logger.error("Bedrock client not initialized")
        raise HTTPException(status_code=500, detail="AWS Bedrock client not initialized")
    
    logger.info(f"Generating SQL for query: {nl_query}")
    
    # Prepare prompt for the LLM
    tables_info = []
    for table_name, table_info in schema["tables"].items():
        columns_info = ", ".join([
            f"{col['name']} ({col['type']}){' PRIMARY KEY' if col['primary_key'] else ''}"
            for col in table_info["columns"]
        ])
        tables_info.append(f"Table: {table_name} - Columns: {columns_info}")
    
    schema_description = "\n".join(tables_info)
    
    prompt = f"""You are an expert SQL generator that converts natural language questions into SQL queries.

DATABASE SCHEMA:
{schema_description}

TASK: Convert the following natural language question to a valid SQLite SQL query. Return ONLY the SQL query and nothing else.

QUESTION: {nl_query}

SQL: """

    # Send request to Claude model
    try:
        if LLM_MODEL.startswith("us.anthropic.claude"):
            # For Claude models
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.1,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        else:
            # Generic structure for other models
            request_body = {
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.1
            }
        
        logger.debug(f"Sending request to Bedrock model {LLM_MODEL}")
        response = bedrock_runtime.invoke_model(
            body=json.dumps(request_body),
            modelId=LLM_MODEL
        )
        
        response_body = json.loads(response.get("body").read())
        
        # Extract the generated SQL based on model response structure
        if LLM_MODEL.startswith("us.anthropic.claude"):
            generated_sql = response_body.get("content", [{}])[0].get("text", "").strip()
        else:
            generated_sql = response_body.get("generation", "").strip()
        
        # Simple confidence estimate
        confidence_score = 0.85  # Default confidence
        
        # Clean up SQL (remove backticks, etc.)
        if generated_sql.startswith("```sql"):
            generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
        elif generated_sql.startswith("```"):
            generated_sql = generated_sql.replace("```", "").strip()
        
        logger.info(f"Generated SQL: {generated_sql}")
        
        return {
            "generated_sql": generated_sql,
            "confidence_score": confidence_score
        }
    except Exception as e:
        logger.error(f"Error generating SQL with Bedrock: {e}")
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

async def execute_sql_query(sql: str) -> dict:
    """Execute generated SQL query on the SQLite database"""
    logger.info(f"Executing SQL query: {sql}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SQLITE_API_URL}/execute",
                json={"query": sql}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error executing SQL query: {e}")
        if e.response is not None:
            error_detail = e.response.text
            logger.error(f"Response error: {error_detail}")
            return {"error": f"SQL execution failed: {error_detail}"}
        else:
            return {"error": f"SQL execution failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error executing SQL query: {e}")
        return {"error": f"SQL execution failed: {str(e)}"}

# ------------------ API Endpoints ------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check SQLite API
        async with httpx.AsyncClient() as client:
            sqlite_resp = await client.get(f"{SQLITE_API_URL}/health")
            sqlite_resp.raise_for_status()
        
        # Check AWS Bedrock connectivity
        if bedrock_runtime is None:
            return JSONResponse(
                status_code=500,
                content={"status": "unhealthy", "detail": "AWS Bedrock client not initialized"}
            )
        
        # All checks passed
        logger.debug("Health check successful")
        return {"status": "healthy", "services": {"sqlite": "connected", "bedrock": "connected"}}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "detail": str(e)}
        )

@app.post("/query", response_model=SQLQueryResponse)
async def nl_query(request: NLQueryRequest):
    """Process natural language query and return SQL results"""
    nl_query = request.query
    max_results = request.max_results
    confidence_threshold = request.confidence_threshold
    
    logger.info(f"Processing natural language query: {nl_query}")
    start_time = time.time()
    
    try:
        # Get database schema
        schema = await get_database_schema()
        
        # Generate SQL using Bedrock
        sql_result = await generate_sql_using_bedrock(nl_query, schema)
        generated_sql = sql_result["generated_sql"]
        confidence_score = sql_result["confidence_score"]
        
        # Check confidence threshold
        if confidence_score < confidence_threshold:
            execution_time = time.time() - start_time
            logger.warning(f"Low confidence score ({confidence_score}) for query: {nl_query}")
            return SQLQueryResponse(
                nl_query=nl_query,
                generated_sql=generated_sql,
                execution_time=execution_time,
                confidence_score=confidence_score,
                error="Generated SQL has low confidence score, please refine your query"
            )
        
        # Limit results if needed
        if max_results and "LIMIT" not in generated_sql.upper():
            generated_sql = f"{generated_sql} LIMIT {max_results}"
        
        # Execute the SQL query
        query_results = await execute_sql_query(generated_sql)
        
        execution_time = time.time() - start_time
        logger.info(f"Query processed in {execution_time:.3f} seconds")
        
        # Check for errors
        if "error" in query_results:
            return SQLQueryResponse(
                nl_query=nl_query,
                generated_sql=generated_sql,
                execution_time=execution_time,
                confidence_score=confidence_score,
                error=query_results["error"]
            )
        
        return SQLQueryResponse(
            nl_query=nl_query,
            generated_sql=generated_sql,
            execution_time=execution_time,
            confidence_score=confidence_score,
            results=query_results
        )
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error processing query: {e}")
        return SQLQueryResponse(
            nl_query=nl_query,
            generated_sql="",
            execution_time=execution_time,
            confidence_score=0.0,
            error=str(e)
        )

# ------------------ MCP Tool Definitions ------------------

@mcp_server.tool(
    name="generate_sql",
    description="Generate SQL query from natural language",
    inputs={
        "nl_query": {
            "type": "string",
            "description": "The natural language query to convert to SQL"
        }
    },
    output_type="object"
)
async def generate_sql_tool(nl_query: str) -> dict:
    """Convert natural language query to SQL"""
    logger.info(f"MCP Tool - generate_sql: {nl_query}")
    
    try:
        # Get database schema
        schema = await get_database_schema()
        
        # Generate SQL using Bedrock
        sql_result = await generate_sql_using_bedrock(nl_query, schema)
        generated_sql = sql_result["generated_sql"]
        confidence_score = sql_result["confidence_score"]
        
        return {
            "nl_query": nl_query,
            "generated_sql": generated_sql,
            "confidence_score": confidence_score
        }
    except Exception as e:
        logger.error(f"Error in generate_sql tool: {e}")
        return {
            "nl_query": nl_query,
            "error": str(e)
        }

@mcp_server.tool(
    name="execute_nl_query",
    description="Execute a natural language query on the SQLite database",
    inputs={
        "nl_query": {
            "type": "string",
            "description": "The natural language query to execute"
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "default": 20
        }
    },
    output_type="object"
)
async def execute_nl_query_tool(nl_query: str, max_results: int = 20) -> dict:
    """Execute a natural language query and return results"""
    logger.info(f"MCP Tool - execute_nl_query: {nl_query}, max_results: {max_results}")
    
    request = NLQueryRequest(
        query=nl_query,
        max_results=max_results
    )
    
    response = await nl_query(request)
    return response.dict()

@mcp_server.resource(
    uri="/schema",
    description="Get the database schema information",
    properties=ResourceProperties(
        content_type="application/json"
    )
)
async def get_schema_resource() -> ResourceResponse:
    """Get the database schema as a resource"""
    logger.info("MCP Resource - /schema requested")
    
    try:
        schema = await get_database_schema()
        return ResourceResponse(
            content=json.dumps(schema),
            content_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error fetching schema resource: {e}")
        return ResourceResponse(
            content=json.dumps({"error": str(e)}),
            content_type="application/json"
        )

@mcp_server.resource(
    uri="/sample_queries",
    description="Get sample natural language queries for the database",
    properties=ResourceProperties(
        content_type="application/json"
    )
)
async def get_sample_queries_resource() -> ResourceResponse:
    """Get sample natural language queries as a resource"""
    logger.info("MCP Resource - /sample_queries requested")
    
    try:
        # Get schema to build contextual samples
        schema = await get_database_schema()
        
        samples = []
        for table_name, table_info in schema["tables"].items():
            samples.append(f"Show me all records from the {table_name} table")
            samples.append(f"How many records are in the {table_name} table?")
            
            # Pick a random column for filtering examples
            if table_info["columns"]:
                col = table_info["columns"][0]
                if col["type"].upper() in ("TEXT", "VARCHAR", "CHAR"):
                    samples.append(f"Find records in {table_name} where {col['name']} contains 'A'")
                elif col["type"].upper() in ("INTEGER", "REAL", "NUMERIC"):
                    samples.append(f"Find records in {table_name} where {col['name']} is greater than 10")
        
        return ResourceResponse(
            content=json.dumps({"sample_queries": samples}),
            content_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error fetching sample queries resource: {e}")
        return ResourceResponse(
            content=json.dumps({"error": str(e)}),
            content_type="application/json"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
