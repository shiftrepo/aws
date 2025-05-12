#!/usr/bin/env python3
"""
SQLite Database API Service
---------------------------
This service provides API endpoints to access SQLite databases 
downloaded from S3, with OpenAPI documentation for Dify integration.
"""

import logging
import os
import json
import sqlite3
import time
from pathlib import Path
import subprocess
import threading

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_restful import Api, Resource
import boto3
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
DATA_DIR = Path("/app/data")
INPUT_DB_PATH = DATA_DIR / "inpit.db"
BIGQUERY_DB_PATH = DATA_DIR / "google_patents_gcp.db"
INPUT_DB_S3_PATH = os.environ.get("INPUT_DB_S3_PATH")
BIGQUERY_DB_S3_PATH = os.environ.get("BIGQUERY_DB_S3_PATH")

app = Flask(__name__)
CORS(app)
api = Api(app)

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True, parents=True)

def download_db_from_s3(s3_path, local_path):
    """Download a database file from S3"""
    logger.info(f"Downloading database from {s3_path} to {local_path}")
    try:
        cmd = ["aws", "s3", "cp", s3_path, str(local_path)]
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        # AWS credentials should be available as environment variables via source
        process = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"Download completed: {process.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download database from S3: {e.stderr}")
        return False

def get_db_schema(db_path):
    """Get schema of a SQLite database"""
    logger.info(f"Getting schema for database: {db_path}")
    schemas = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue  # Skip internal SQLite tables
                
            logger.debug(f"Getting schema for table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            schemas[table_name] = [
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "dflt_value": col[4],
                    "pk": col[5]
                }
                for col in columns
            ]
            
        conn.close()
        return schemas
    except sqlite3.Error as e:
        logger.error(f"Error getting database schema: {str(e)}")
        return {}

def download_databases():
    """Download all required databases from S3"""
    logger.info("Starting database downloads...")
    
    # Download Input database
    if not INPUT_DB_PATH.exists():
        if not download_db_from_s3(INPUT_DB_S3_PATH, INPUT_DB_PATH):
            logger.error("Failed to download Input database")
    else:
        logger.info(f"Input database already exists at {INPUT_DB_PATH}")
    
    # Download BigQuery database
    if not BIGQUERY_DB_PATH.exists():
        if not download_db_from_s3(BIGQUERY_DB_S3_PATH, BIGQUERY_DB_PATH):
            logger.error("Failed to download BigQuery database")
    else:
        logger.info(f"BigQuery database already exists at {BIGQUERY_DB_PATH}")

class Health(Resource):
    def get(self):
        """Health check endpoint"""
        logger.debug("Health check requested")
        
        health_status = {
            "status": "healthy",
            "databases": {
                "input": INPUT_DB_PATH.exists(),
                "bigquery": BIGQUERY_DB_PATH.exists()
            },
            "timestamp": time.time()
        }
        
        return health_status

class Databases(Resource):
    def get(self):
        """List available databases"""
        logger.debug("Database list requested")
        
        databases = {
            "databases": [
                {
                    "name": "input",
                    "description": "Inpit Database",
                    "path": str(INPUT_DB_PATH),
                    "exists": INPUT_DB_PATH.exists(),
                    "size_bytes": INPUT_DB_PATH.stat().st_size if INPUT_DB_PATH.exists() else None
                },
                {
                    "name": "bigquery",
                    "description": "Google Patents BigQuery Database",
                    "path": str(BIGQUERY_DB_PATH),
                    "exists": BIGQUERY_DB_PATH.exists(),
                    "size_bytes": BIGQUERY_DB_PATH.stat().st_size if BIGQUERY_DB_PATH.exists() else None
                }
            ]
        }
        
        return databases

class Schema(Resource):
    def get(self, db_name):
        """Get schema of a database"""
        logger.debug(f"Schema requested for database: {db_name}")
        
        if db_name not in ["input", "bigquery"]:
            return {"error": "Invalid database name"}, 400
            
        db_path = INPUT_DB_PATH if db_name == "input" else BIGQUERY_DB_PATH
        
        if not db_path.exists():
            return {"error": f"Database {db_name} does not exist"}, 404
            
        schema = get_db_schema(db_path)
        return {"database": db_name, "schema": schema}

class ExecuteQuery(Resource):
    def post(self, db_name):
        """Execute SQL query on a database"""
        logger.debug(f"Query execution requested for database: {db_name}")
        
        if db_name not in ["input", "bigquery"]:
            return {"error": "Invalid database name"}, 400
            
        db_path = INPUT_DB_PATH if db_name == "input" else BIGQUERY_DB_PATH
        
        if not db_path.exists():
            return {"error": f"Database {db_name} does not exist"}, 404
            
        data = request.get_json()
        if not data or "query" not in data:
            return {"error": "Missing query parameter"}, 400
            
        query = data["query"]
        logger.info(f"Executing query on {db_name} database: {query}")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute(query)
            
            if query.strip().upper().startswith(("SELECT", "PRAGMA", "EXPLAIN")):
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                
                results = []
                for row in rows:
                    results.append({columns[i]: row[i] for i in range(len(columns))})
                
                execution_time = time.time() - start_time
                response = {
                    "database": db_name,
                    "query": query,
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results),
                    "execution_time_ms": round(execution_time * 1000, 2)
                }
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
                affected_rows = cursor.rowcount
                conn.commit()
                
                execution_time = time.time() - start_time
                response = {
                    "database": db_name,
                    "query": query,
                    "affected_rows": affected_rows,
                    "execution_time_ms": round(execution_time * 1000, 2)
                }
                
            conn.close()
            return response
            
        except sqlite3.Error as e:
            error_msg = str(e)
            logger.error(f"SQL error: {error_msg}")
            return {"error": f"SQL error: {error_msg}", "query": query}, 400

class SampleQueries(Resource):
    def get(self, db_name):
        """Get sample queries for a database"""
        logger.debug(f"Sample queries requested for database: {db_name}")
        
        if db_name not in ["input", "bigquery"]:
            return {"error": "Invalid database name"}, 400
            
        # Define sample queries for each database
        sample_queries = {
            "input": [
                {
                    "name": "List all tables",
                    "query": "SELECT name FROM sqlite_master WHERE type='table';"
                },
                {
                    "name": "Count rows in table",
                    "query": "SELECT COUNT(*) AS row_count FROM table_name;"
                }
            ],
            "bigquery": [
                {
                    "name": "List all tables",
                    "query": "SELECT name FROM sqlite_master WHERE type='table';"
                },
                {
                    "name": "Top patent applicants",
                    "query": "SELECT assignee_harmonized, COUNT(*) as patent_count FROM patents GROUP BY assignee_harmonized ORDER BY patent_count DESC LIMIT 10;"
                }
            ]
        }
        
        return {"database": db_name, "sample_queries": sample_queries.get(db_name, [])}

class OpenAPISpec(Resource):
    def get(self):
        """Get OpenAPI specification for MCP integration"""
        logger.debug("OpenAPI spec requested")
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "SQLite Database API",
                "description": "API for accessing SQLite databases downloaded from S3",
                "version": "1.0.0"
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {
                                "description": "Health status"
                            }
                        }
                    }
                },
                "/databases": {
                    "get": {
                        "summary": "List available databases",
                        "responses": {
                            "200": {
                                "description": "List of databases"
                            }
                        }
                    }
                },
                "/schema/{db_name}": {
                    "get": {
                        "summary": "Get database schema",
                        "parameters": [
                            {
                                "name": "db_name",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "enum": ["input", "bigquery"]}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Database schema"
                            }
                        }
                    }
                },
                "/execute/{db_name}": {
                    "post": {
                        "summary": "Execute SQL query",
                        "parameters": [
                            {
                                "name": "db_name", 
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "enum": ["input", "bigquery"]}
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"}
                                        },
                                        "required": ["query"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Query results"
                            }
                        }
                    }
                },
                "/sample_queries/{db_name}": {
                    "get": {
                        "summary": "Get sample queries for a database",
                        "parameters": [
                            {
                                "name": "db_name",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "enum": ["input", "bigquery"]}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Sample queries"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {}
            }
        }
        
        return spec

# Static files for OpenAPI UI
@app.route('/docs')
def docs():
    """API Documentation page using Swagger UI"""
    logger.debug("Documentation page requested")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SQLite Database API - Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/openapi",
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                })
            }
        </script>
    </body>
    </html>
    """

# Register API resources
api.add_resource(Health, '/health')
api.add_resource(Databases, '/databases')
api.add_resource(Schema, '/schema/<string:db_name>')
api.add_resource(ExecuteQuery, '/execute/<string:db_name>')
api.add_resource(SampleQueries, '/sample_queries/<string:db_name>')
api.add_resource(OpenAPISpec, '/openapi')

def main():
    """Main entry point"""
    logger.info("Starting SQLite Database API Service")
    
    # Download databases in a separate thread to not block server startup
    download_thread = threading.Thread(target=download_databases)
    download_thread.start()
    
    # Log AWS region from environment
    aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    logger.info(f"Using AWS region: {aws_region}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG")

if __name__ == "__main__":
    main()
