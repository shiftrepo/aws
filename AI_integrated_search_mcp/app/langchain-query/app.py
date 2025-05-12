#!/usr/bin/env python3
"""
LangChain Database Query Service
-------------------------------
This service provides API endpoints for natural language database querying using LangChain's DatabaseChain.
It sends database structure and data to an LLM for processing natural language queries.
"""

import logging
import os
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from dotenv import load_dotenv

# Import LangChain components
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat

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
DATABASE_API_URL = os.environ.get("DATABASE_API_URL", "http://sqlite-db:5000")

app = Flask(__name__)
CORS(app)
api = Api(app)


class BedrockLLM:
    """Client for AWS Bedrock API integrated with LangChain"""
    
    def __init__(self):
        """Initialize Bedrock LLM"""
        logger.info("Initializing Bedrock LLM for LangChain")
        
        # Get AWS region from environment
        self.region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
        if not self.region:
            logger.error("AWS region not found in environment variables")
            raise ValueError("AWS region not found in environment variables")
        
        logger.info(f"Using AWS region: {self.region}")
        
        # Model ID
        self.llm_model_id = os.environ.get("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
        logger.info(f"Using LLM model: {self.llm_model_id}")
        
        try:
            # Create LangChain Bedrock Chat model
            self.llm = BedrockChat(
                model_id=self.llm_model_id,
                region_name=self.region,
                model_kwargs={"temperature": 0}
            )
            logger.info("Bedrock LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock LLM: {str(e)}")
            raise


class LangChainQueryProcessor:
    """LangChain Database Query Processor"""
    
    def __init__(self, llm):
        """Initialize LangChain Query Processor"""
        self.llm = llm
        self.db_connections = {}
        logger.info("Initialized LangChain Query Processor")
    
    def get_db_connection(self, db_name: str) -> SQLDatabase:
        """Get SQLDatabase instance for a database"""
        if db_name in self.db_connections:
            return self.db_connections[db_name]
        
        db_path = str(INPUT_DB_PATH if db_name == "input" else BIGQUERY_DB_PATH)
        logger.info(f"Creating SQLDatabase connection for: {db_path}")
        
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        self.db_connections[db_name] = db
        return db
    
    def process_nl_query(self, user_query: str, db_name: str) -> Dict[str, Any]:
        """Process natural language query using LangChain's DatabaseChain"""
        logger.info(f"Processing natural language query with LangChain: {user_query}")
        
        try:
            # Get SQLDatabase connection
            db = self.get_db_connection(db_name)
            
            # Create query generation chain
            query_chain = create_sql_query_chain(self.llm, db)
            
            # Generate SQL query
            start_time = time.time()
            sql_query = query_chain.invoke({"question": user_query})
            query_generation_time = time.time() - start_time
            
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute the query
            query_tool = QuerySQLDataBaseTool(db=db)
            
            execute_start_time = time.time()
            query_result = query_tool.invoke({"query": sql_query})
            execution_time = time.time() - execute_start_time
            
            # Generate explanation
            explanation_start_time = time.time()
            explanation = self._generate_explanation(user_query, sql_query, query_result, db)
            explanation_time = time.time() - explanation_start_time
            
            # Parse and format results
            result = {
                "user_query": user_query,
                "sql_query": sql_query,
                "result": query_result,
                "explanation": explanation,
                "performance": {
                    "query_generation_time_ms": round(query_generation_time * 1000, 2),
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "explanation_time_ms": round(explanation_time * 1000, 2),
                    "total_time_ms": round((query_generation_time + execution_time + explanation_time) * 1000, 2)
                }
            }
            
            # Format output to match the existing API structure
            formatted_result = self._format_output(result, sql_query, query_result)
            
            logger.info(f"Query processed successfully with LangChain")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error processing NL query with LangChain: {str(e)}")
            return {"error": f"Error processing query: {str(e)}", "query": user_query}
    
    def _generate_explanation(self, user_query: str, sql_query: str, query_result: str, db: SQLDatabase) -> str:
        """Generate explanation of query results using LangChain"""
        logger.debug("Generating explanation for query results")
        
        explanation_prompt = PromptTemplate.from_template(
            """
            You are a data analyst explaining database query results.
            
            User question: {question}
            
            SQL query that was executed: 
            {query}
            
            Query results:
            {results}
            
            Please provide a brief explanation of these results, focusing on answering the user's question directly. Include key insights from the data.
            """
        )
        
        # Create chain for explanation
        chain = explanation_prompt | self.llm
        
        # Generate explanation
        explanation = chain.invoke({
            "question": user_query,
            "query": sql_query,
            "results": query_result
        })
        
        # Extract content from the response
        if hasattr(explanation, "content"):
            explanation_text = explanation.content
        else:
            explanation_text = str(explanation)
        
        logger.debug(f"Generated explanation: {explanation_text[:100]}...")
        return explanation_text.strip()
    
    def _format_output(self, result: Dict[str, Any], sql_query: str, query_result: str) -> Dict[str, Any]:
        """Format the output to match the existing API structure"""
        # Parse the query result (assuming it's a string representation of a table)
        rows = []
        columns = []
        
        try:
            # Get a database connection to execute the query directly and get results in structured format
            db_name = result.get("database", "input")  # Default to input if not specified
            db_path = INPUT_DB_PATH if db_name == "input" else BIGQUERY_DB_PATH
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Re-execute the query to get structured results
            cursor.execute(sql_query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Get rows
            raw_rows = cursor.fetchall()
            
            # Convert to list of dicts
            for row in raw_rows:
                rows.append({columns[i]: row[i] for i in range(len(columns))})
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error parsing query result: {str(e)}")
            # Fallback: use the text representation
            formatted_rows = query_result.strip().split("\n")
            
            # Skip empty lines
            formatted_rows = [row for row in formatted_rows if row.strip()]
            
            if len(formatted_rows) > 1:
                # Try to extract columns from first row
                try:
                    # If it looks like CSV format
                    if "," in formatted_rows[0]:
                        columns = [col.strip() for col in formatted_rows[0].split(",")]
                        for row_str in formatted_rows[1:]:
                            row_values = [val.strip() for val in row_str.split(",")]
                            if len(row_values) == len(columns):
                                row = {columns[i]: row_values[i] for i in range(len(columns))}
                                rows.append(row)
                    # If it looks like a space/pipe-separated format
                    else:
                        rows.append({"result": query_result})
                except:
                    rows.append({"result": query_result})
        
        formatted_output = {
            "user_query": result["user_query"],
            "sql_query": sql_query,
            "results": rows,
            "columns": columns,
            "row_count": len(rows),
            "execution_time_ms": result["performance"]["total_time_ms"],
            "explanation": result["explanation"]
        }
        
        return formatted_output


class Health(Resource):
    def get(self):
        """Health check endpoint"""
        logger.debug("Health check requested")
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "dependencies": {
                "langchain": True,
                "bedrock": self._check_bedrock_api()
            }
        }
        
        return health_status
    
    def _check_bedrock_api(self) -> bool:
        """Check if Bedrock API is available"""
        try:
            # Initialize Bedrock client
            session = boto3.Session()
            region = session.region_name or os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
            boto3.client('bedrock-runtime', region_name=region)
            return True
        except:
            return False


class OpenAPISpec(Resource):
    def get(self):
        """Get OpenAPI specification for MCP integration"""
        logger.debug("OpenAPI spec requested")
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "LangChain Database Query API",
                "description": "API for processing natural language queries using LangChain DatabaseChain",
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
                "/query/{db_name}": {
                    "post": {
                        "summary": "Process natural language query using LangChain",
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
                }
            }
        }
        
        return spec


class LangChainQuery(Resource):
    def __init__(self):
        self.bedrock_llm = None
        self.lc_processor = None
        
        # Initialize clients
        try:
            self.bedrock_llm = BedrockLLM()
            self.lc_processor = LangChainQueryProcessor(self.bedrock_llm.llm)
        except Exception as e:
            logger.error(f"Error initializing LangChainQuery resource: {str(e)}")
    
    def post(self, db_name):
        """Process natural language query using LangChain"""
        logger.debug(f"LangChain Query requested for database: {db_name}")
        
        if not self.lc_processor:
            return {"error": "LangChain Query processor not initialized"}, 500
        
        if db_name not in ["input", "bigquery"]:
            return {"error": "Invalid database name"}, 400
            
        data = request.get_json()
        if not data or "query" not in data:
            return {"error": "Missing query parameter"}, 400
            
        user_query = data["query"]
        logger.info(f"Processing LangChain query on {db_name} database: {user_query}")
        
        try:
            result = self.lc_processor.process_nl_query(user_query, db_name)
            return result
            
        except Exception as e:
            logger.error(f"Error processing LangChain query: {str(e)}")
            return {"error": f"Error processing query: {str(e)}", "query": user_query}, 500


# Static files for OpenAPI UI
@app.route('/docs')
def docs():
    """API Documentation page using Swagger UI"""
    logger.debug("Documentation page requested")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangChain Database Query API - Documentation</title>
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
api.add_resource(LangChainQuery, '/query/<string:db_name>')
api.add_resource(OpenAPISpec, '/openapi')

def main():
    """Main entry point"""
    logger.info("Starting LangChain Database Query API Service")
    
    # Log AWS region from environment
    aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    logger.info(f"Using AWS region: {aws_region}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG")

if __name__ == "__main__":
    main()
