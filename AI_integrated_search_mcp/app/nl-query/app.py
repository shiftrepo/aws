#!/usr/bin/env python3
"""
Natural Language Query API Service
----------------------------------
This service provides API endpoints to handle natural language queries
and translate them into SQL using AWS Bedrock models.
"""

import logging
import os
import json
import time
import re
import sys
from typing import Dict, List, Any, Optional

import boto3
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_restful import Api, Resource
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
DATABASE_API_URL = os.environ.get("DATABASE_API_URL", "http://sqlite-db:5000")

app = Flask(__name__)
CORS(app)
api = Api(app)

class BedrockClient:
    """Client for AWS Bedrock API"""

    def __init__(self):
        """Initialize Bedrock client"""
        logger.info("Initializing Bedrock client")

        # Get AWS region from environment
        self.region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
        if not self.region:
            logger.error("AWS region not found in environment variables")
            raise ValueError("AWS region not found in environment variables")

        logger.info(f"Using AWS region: {self.region}")

        # Create Bedrock client with cross-region functionality
        try:
            # For normal Bedrock operations
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)

            # Use the same region for all models, as specified in environment variables
            # No special region handling for specific models
            self.cross_region_bedrock = self.bedrock
            logger.info(f"Using environment-configured region for all models: {self.region}")

            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise

        # Model IDs - hardcoded values instead of environment variables
        self.llm_model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        self.embedding_model_id = "amazon.titan-embed-text-v2:0"
        self.rerank_model_id = "amazon.rerank-v1:0"

        logger.info(f"Using LLM model: {self.llm_model_id}")
        logger.info(f"Using embedding model: {self.embedding_model_id}")
        logger.info(f"Using rerank model: {self.rerank_model_id}")

    def get_completion(self, prompt: str) -> str:
        """Get completion from Bedrock LLM"""
        logger.debug(f"Getting completion for prompt: {prompt[:100]}...")

        try:
            # Prepare request body based on model
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Convert request body to JSON
            body_json = json.dumps(body)

            # Determine which client to use based on the model ID
            if "claude-3-7" in self.llm_model_id or "us.anthropic" in self.llm_model_id:
                logger.info(f"Using cross-region client for model: {self.llm_model_id}")
                client = self.cross_region_bedrock
            else:
                client = self.bedrock

            # Send request to Bedrock
            response = client.invoke_model(
                modelId=self.llm_model_id,
                body=body_json
            )

            # Parse response
            response_body = json.loads(response.get('body').read())

            # Extract and return generated text
            if "content" in response_body and len(response_body["content"]) > 0:
                generated_text = response_body["content"][0]["text"]
                logger.debug(f"Got completion: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Unexpected response format: {response_body}")
                return ""

        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            return f"Error: {str(e)}"

    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings from Bedrock embedding model"""
        logger.debug(f"Getting embeddings for text: {text[:100]}...")

        try:
            # Prepare request body
            body = {
                "inputText": text
            }

            # Convert request body to JSON
            body_json = json.dumps(body)

            # Send request to Bedrock
            response = self.bedrock.invoke_model(
                modelId=self.embedding_model_id,
                body=body_json
            )

            # Parse response
            response_body = json.loads(response.get('body').read())

            # Extract and return embeddings
            if "embedding" in response_body:
                embeddings = response_body["embedding"]
                logger.debug(f"Got embeddings of dimension {len(embeddings)}")
                return embeddings
            else:
                logger.error(f"Unexpected response format: {response_body}")
                return []

        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            return []

    def rerank_results(self, query: str, results: List[Dict[str, Any]], k: int = 10) -> List[Dict[str, Any]]:
        """Rerank results using Bedrock rerank model"""
        logger.debug(f"Reranking {len(results)} results for query: {query}")

        if not results:
            return []

        try:
            # Prepare request body
            body = {
                "query": query,
                "passages": [{"id": str(i), "text": json.dumps(result)} for i, result in enumerate(results)]
            }

            # Convert request body to JSON
            body_json = json.dumps(body)

            # Send request to Bedrock
            response = self.bedrock.invoke_model(
                modelId=self.rerank_model_id,
                body=body_json
            )

            # Parse response
            response_body = json.loads(response.get('body').read())

            # Extract and return ranked results
            if "results" in response_body:
                ranked_indices = [int(item["id"]) for item in response_body["results"][:k]]
                ranked_results = [results[i] for i in ranked_indices]
                logger.debug(f"Reranked results, top result: {ranked_results[0] if ranked_results else None}")
                return ranked_results
            else:
                logger.error(f"Unexpected response format: {response_body}")
                return results[:k]  # Return top k if reranking failed

        except Exception as e:
            logger.error(f"Error reranking results: {str(e)}")
            return results[:k]  # Return top k if reranking failed

class DatabaseClient:
    """Client for SQLite Database API"""

    def __init__(self, api_url):
        """Initialize Database API client"""
        self.api_url = api_url
        logger.info(f"Initialized Database API client with URL: {api_url}")

    def get_databases(self) -> List[Dict[str, Any]]:
        """Get list of available databases"""
        logger.debug("Getting list of databases")

        try:
            response = requests.get(f"{self.api_url}/databases")
            response.raise_for_status()
            data = response.json()

            databases = data.get("databases", [])
            logger.debug(f"Found {len(databases)} databases")
            return databases

        except requests.RequestException as e:
            logger.error(f"Error getting databases: {str(e)}")
            return []

    def get_schema(self, db_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get schema of a database"""
        logger.debug(f"Getting schema for database: {db_name}")

        try:
            response = requests.get(f"{self.api_url}/schema/{db_name}")
            response.raise_for_status()
            data = response.json()

            schema = data.get("schema", {})
            logger.debug(f"Got schema with {len(schema)} tables for database {db_name}")
            return schema

        except requests.RequestException as e:
            logger.error(f"Error getting schema for database {db_name}: {str(e)}")
            return {}

    def execute_query(self, db_name: str, query: str) -> Dict[str, Any]:
        """Execute SQL query on a database"""
        logger.info(f"Executing query on database {db_name}: {query}")

        try:
            response = requests.post(
                f"{self.api_url}/execute/{db_name}",
                json={"query": query},
                timeout=30  # Increased timeout for potentially long-running queries
            )
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Query execution successful, returned {data.get('row_count', 0)} rows")
            return data

        except requests.RequestException as e:
            logger.error(f"Error executing query on database {db_name}: {str(e)}")
            error_msg = str(e)

            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass

            return {"error": error_msg, "query": query}

class NLQueryProcessor:
    """Natural Language Query Processor"""

    def __init__(self, bedrock_client: BedrockClient, db_client: DatabaseClient):
        """Initialize NL Query Processor"""
        self.bedrock_client = bedrock_client
        self.db_client = db_client
        logger.info("Initialized Natural Language Query Processor")

    def generate_sql(self, user_query: str, db_name: str) -> str:
        """Generate SQL query from natural language query"""
        logger.info(f"Generating SQL for query: {user_query}")

        # Get database schema
        schema = self.db_client.get_schema(db_name)
        if not schema:
            logger.error(f"Could not get schema for database {db_name}")
            return ""

        # Create schema description for prompt
        schema_desc = "Database Schema:\n"
        for table, columns in schema.items():
            schema_desc += f"Table: {table}\n"
            schema_desc += "Columns:\n"
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                is_pk = "PRIMARY KEY" if col['pk'] == 1 else ""
                schema_desc += f"  - {col_name} ({col_type}) {is_pk}\n"
            schema_desc += "\n"

        # Create prompt for SQL generation
        prompt = f"""As an expert SQL developer, your task is to convert a natural language question into a valid SQLite query.

{schema_desc}

User question: {user_query}

Generate ONLY a valid SQL query that answers this question. Do not include any explanations or comments. The query should be executable in SQLite.

SQL Query:"""

        # Generate SQL query
        sql_query = self.bedrock_client.get_completion(prompt)

        # Clean up generated SQL
        sql_query = self._clean_sql(sql_query)
        logger.info(f"Generated SQL query: {sql_query}")

        return sql_query

    def _clean_sql(self, sql: str) -> str:
        """Clean up generated SQL query"""
        # Remove markdown code block formatting if present
        sql = re.sub(r'^```sql\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)

        # Remove any other code block formatting
        sql = re.sub(r'^```\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)

        # Trim whitespace
        sql = sql.strip()

        return sql

    def process_nl_query(self, user_query: str, db_name: str) -> Dict[str, Any]:
        """Process natural language query and return results"""
        logger.info(f"Processing natural language query: {user_query}")

        # Generate SQL query
        sql_query = self.generate_sql(user_query, db_name)
        if not sql_query:
            logger.error("Failed to generate SQL query")
            return {"error": "Failed to generate SQL query", "query": user_query}

        # Execute SQL query
        query_result = self.db_client.execute_query(db_name, sql_query)
        if "error" in query_result:
            logger.error(f"Error executing query: {query_result['error']}")
            return query_result

        # Ensure query was a SELECT
        if "rows" not in query_result:
            logger.error("Generated query was not a SELECT query")
            return {
                "error": "Generated query was not a SELECT query",
                "query": sql_query,
                "result": query_result
            }

        # Generate explanation
        explanation = self._generate_explanation(user_query, sql_query, query_result)
        logger.info(f"Generated explanation of length {len(explanation)} chars")

        # Return results
        result = {
            "user_query": user_query,
            "sql_query": sql_query,
            "results": query_result.get("rows", []),
            "columns": query_result.get("columns", []),
            "row_count": query_result.get("row_count", 0),
            "execution_time_ms": query_result.get("execution_time_ms", 0),
            "explanation": explanation
        }

        logger.info(f"Query processed successfully, returned {result['row_count']} rows")
        logger.debug(f"Result structure: {list(result.keys())}")
        return result

    def _generate_explanation(self, user_query: str, sql_query: str, query_result: Dict[str, Any]) -> str:
        """Generate explanation of query results"""
        logger.debug("Generating explanation for query results")

        # Limit rows to include in prompt for explanation
        max_rows = 10
        rows = query_result.get("rows", [])[:max_rows]
        row_count = query_result.get("row_count", 0)

        # Create prompt for explanation
        prompt = f"""As a data analyst, your task is to explain the results of a SQL query in clear, concise language.

User question: {user_query}

SQL query that was executed:
{sql_query}

Query returned {row_count} rows. Here are up to {max_rows} rows of the results:
{json.dumps(rows, indent=2, ensure_ascii=False)}

Please provide a brief explanation of these results, focusing on answering the user's question directly. Include key insights from the data.

Explanation:"""

        # Generate explanation
        explanation = self.bedrock_client.get_completion(prompt)
        logger.debug(f"Generated explanation: {explanation[:100]}...")

        return explanation.strip()

class Health(Resource):
    def get(self):
        """Health check endpoint"""
        logger.debug("Health check requested")

        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "dependencies": {
                "database_api": self._check_database_api(),
                "bedrock_api": self._check_bedrock_api()
            }
        }

        return health_status

    def _check_database_api(self) -> bool:
        """Check if Database API is healthy"""
        try:
            response = requests.get(f"{DATABASE_API_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

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
                "title": "Natural Language Query API",
                "description": "API for processing natural language queries using AWS Bedrock",
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
                        "summary": "Process natural language query",
                        "parameters": [
                            {
                                "name": "db_name",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "enum": ["input", "bigquery", "inpit"]}
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

class NLQuery(Resource):
    def __init__(self):
        self.bedrock_client = None
        self.db_client = None
        self.nl_processor = None

        # Initialize clients
        try:
            self.bedrock_client = BedrockClient()
            self.db_client = DatabaseClient(DATABASE_API_URL)
            self.nl_processor = NLQueryProcessor(self.bedrock_client, self.db_client)
        except Exception as e:
            logger.error(f"Error initializing NLQuery resource: {str(e)}")

    def post(self, db_name):
        """Process natural language query"""
        logger.debug(f"NL Query requested for database: {db_name}")

        if not self.nl_processor:
            return {"error": "NL Query processor not initialized"}, 500

        if db_name not in ["input", "bigquery", "inpit"]:
            return {"error": "Invalid database name"}, 400
            
        # Map "inpit" to "input" for backward compatibility
        if db_name == "inpit":
            db_name = "input"

        data = request.get_json()
        if not data or "query" not in data:
            return {"error": "Missing query parameter"}, 400

        user_query = data["query"]
        logger.info(f"Processing NL query on {db_name} database: {user_query}")

        try:
            result = self.nl_processor.process_nl_query(user_query, db_name)
            
            # Ensure we always have consistent result structure
            if "explanation" in result and (not result.get("results") or not result.get("columns")):
                # Ensure minimal structure for UI if we have explanation but no proper results table
                if not result.get("results"):
                    result["results"] = []
                if not result.get("columns"):
                    result["columns"] = []
                if not result.get("row_count"):
                    result["row_count"] = 0
            
            logger.info(f"Sending response: {list(result.keys())}")
            
            # Ensure proper JSON encoding for multilingual content
            return Response(
                json.dumps(result, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            )

        except Exception as e:
            logger.error(f"Error processing NL query: {str(e)}")
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
        <title>Natural Language Query API - Documentation</title>
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
api.add_resource(NLQuery, '/query/<string:db_name>')
api.add_resource(OpenAPISpec, '/openapi')

def main():
    """Main entry point"""
    logger.info("Starting Natural Language Query API Service")

    # Log AWS region from environment
    aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    logger.info(f"Using AWS region: {aws_region}")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG")

if __name__ == "__main__":
    main()
