import os
import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import boto3
import sqlalchemy
from databases import Database
from pydantic import BaseModel
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_PATH = "/app/data/db/database.sqlite"
DB_URL = f"sqlite:///{DATABASE_PATH}"

# FastAPI app
app = FastAPI(
    title="SQLite Database API",
    description="API for accessing SQLite database with support for S3 synchronization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
try:
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates directory setup successfully")
except Exception as e:
    logger.error(f"Error setting up templates: {e}")
    templates = None

# Database connection
database = Database(DB_URL)

# Models
class QueryRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None

class TableInfo(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]
    row_count: int

class SQLResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    query: str
    execution_time: float
    affected_rows: Optional[int] = None

@app.on_event("startup")
async def startup():
    """Connect to the database on startup"""
    logger.info("Starting up the SQLite Database API")
    await database.connect()
    logger.info(f"Connected to database at {DATABASE_PATH}")

@app.on_event("shutdown")
async def shutdown():
    """Disconnect from the database on shutdown"""
    logger.info("Shutting down the SQLite Database API")
    await database.disconnect()
    logger.info("Disconnected from database")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 1:
            logger.debug("Health check successful")
            return {"status": "healthy", "database": "connected"}
        else:
            logger.error("Health check failed: unexpected result from database")
            return JSONResponse(
                status_code=500,
                content={"status": "unhealthy", "detail": "Database check failed"}
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "detail": str(e)}
        )

@app.get("/tables")
async def list_tables():
    """List all tables in the database"""
    logger.info("Listing all tables")
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        result = await database.fetch_all(query=query)
        tables = [row["name"] for row in result]
        logger.info(f"Found {len(tables)} tables: {tables}")
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables/{table_name}")
async def get_table_info(table_name: str):
    """Get information about a specific table"""
    logger.info(f"Getting info for table: {table_name}")
    try:
        # Check if table exists
        exists_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        exists = await database.fetch_one(query=exists_query)
        
        if not exists:
            logger.warning(f"Table {table_name} not found")
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
        
        # Get column information
        pragma_query = f"PRAGMA table_info('{table_name}')"
        columns_info = await database.fetch_all(query=pragma_query)
        columns = [
            {
                "name": col["name"],
                "type": col["type"],
                "notnull": bool(col["notnull"]),
                "pk": bool(col["pk"]),
                "dflt_value": col["dflt_value"]
            }
            for col in columns_info
        ]
        
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM '{table_name}'"
        count = await database.fetch_one(query=count_query)
        row_count = count["count"] if count else 0
        
        logger.info(f"Table {table_name} has {len(columns)} columns and {row_count} rows")
        return {
            "table_name": table_name,
            "columns": columns,
            "row_count": row_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting table info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_query(request: QueryRequest):
    """Execute a SQL query and return results"""
    query = request.query
    params = request.params or {}
    
    logger.info(f"Executing query: {query}")
    logger.debug(f"Query parameters: {params}")
    
    import time
    start_time = time.time()
    
    try:
        # Check if it's a SELECT query
        is_select = query.strip().upper().startswith("SELECT")
        
        if is_select:
            # For SELECT queries, return the results
            result = await database.fetch_all(query=query, values=params)
            rows = [dict(row) for row in result]
            columns = list(rows[0].keys()) if rows else []
            affected_rows = len(rows)
        else:
            # For other queries, execute and get affected rows
            result = await database.execute(query=query, values=params)
            rows = []
            columns = []
            affected_rows = result
        
        execution_time = time.time() - start_time
        logger.info(f"Query executed successfully in {execution_time:.5f} seconds")
        logger.debug(f"Affected rows: {affected_rows}")
        
        return {
            "columns": columns,
            "rows": rows,
            "query": query,
            "execution_time": execution_time,
            "affected_rows": affected_rows
        }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error executing query: {e}")
        logger.debug(f"Failed query: {query}")
        logger.debug(f"Query failed after {execution_time:.5f} seconds")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sample_queries")
async def get_sample_queries():
    """Return a list of sample queries for the database"""
    logger.info("Getting sample queries")
    
    try:
        # Get list of tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = await database.fetch_all(query=tables_query)
        table_names = [row["name"] for row in tables]
        
        sample_queries = []
        
        # Generate sample queries for each table
        for table in table_names:
            # Basic SELECT
            sample_queries.append({
                "name": f"All {table} records",
                "query": f"SELECT * FROM {table} LIMIT 10",
                "description": f"Get the first 10 records from the {table} table"
            })
            
            # Get column info
            pragma_query = f"PRAGMA table_info('{table}')"
            columns_info = await database.fetch_all(query=pragma_query)
            
            # If there are at least 2 columns, create a join example if possible
            if len(columns_info) >= 2:
                # Try to find a numeric column for aggregation
                numeric_cols = [col["name"] for col in columns_info 
                               if col["type"].upper() in ('INTEGER', 'REAL', 'NUMERIC', 'INT')]
                
                if numeric_cols:
                    sample_queries.append({
                        "name": f"Aggregate {table}",
                        "query": f"SELECT COUNT(*), AVG({numeric_cols[0]}) FROM {table}",
                        "description": f"Count records and average of {numeric_cols[0]} in {table}"
                    })
                
                # Try to find a text column for filtering
                text_cols = [col["name"] for col in columns_info 
                            if col["type"].upper() in ('TEXT', 'VARCHAR', 'CHAR', 'STRING')]
                
                if text_cols:
                    sample_queries.append({
                        "name": f"Filter {table}",
                        "query": f"SELECT * FROM {table} WHERE {text_cols[0]} LIKE '%A%' LIMIT 5",
                        "description": f"Filter {table} records where {text_cols[0]} contains 'A'"
                    })
        
        # Add a few general examples
        for table in table_names[:min(2, len(table_names))]:
            sample_queries.append({
                "name": f"Count {table}",
                "query": f"SELECT COUNT(*) FROM {table}",
                "description": f"Count the number of records in {table}"
            })
        
        logger.info(f"Generated {len(sample_queries)} sample queries")
        return {"sample_queries": sample_queries}
    except Exception as e:
        logger.error(f"Error generating sample queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
