#!/usr/bin/env python3
"""
SQLite Database Web UI
----------------------
Web UI for interacting with SQLite databases, executing queries,
and using natural language processing for queries.
"""

import logging
import os
import json
import time
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
from flask_cors import CORS
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
NL_QUERY_API_URL = os.environ.get("NL_QUERY_API_URL", "http://nl-query-service:5000")
LANGCHAIN_QUERY_API_URL = os.environ.get("LANGCHAIN_QUERY_API_URL", "http://langchain-query-service:5000")

app = Flask(__name__)
CORS(app)

class DatabaseClient:
    """Client for SQLite Database API"""
    
    def __init__(self, api_url):
        """Initialize Database API client"""
        self.api_url = api_url
        logger.info(f"Initialized Database API client with URL: {api_url}")
    
    def get_health(self):
        """Get health status of the database API"""
        logger.debug("Getting database API health")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            return True, data
        except Exception as e:
            logger.error(f"Error getting database API health: {str(e)}")
            return False, {"error": str(e)}
    
    def get_databases(self):
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
    
    def get_schema(self, db_name):
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
    
    def execute_query(self, db_name, query):
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
    
    def get_sample_queries(self, db_name):
        """Get sample queries for a database"""
        logger.debug(f"Getting sample queries for database: {db_name}")
        
        try:
            response = requests.get(f"{self.api_url}/sample_queries/{db_name}")
            response.raise_for_status()
            data = response.json()
            
            sample_queries = data.get("sample_queries", [])
            logger.debug(f"Got {len(sample_queries)} sample queries for database {db_name}")
            return sample_queries
            
        except requests.RequestException as e:
            logger.error(f"Error getting sample queries for database {db_name}: {str(e)}")
            return []

class NLQueryClient:
    """Client for NL Query API"""
    
    def __init__(self, api_url):
        """Initialize NL Query API client"""
        self.api_url = api_url
        logger.info(f"Initialized NL Query API client with URL: {api_url}")
    
    def get_health(self):
        """Get health status of the NL Query API"""
        logger.debug("Getting NL Query API health")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            return True, data
        except Exception as e:
            logger.error(f"Error getting NL Query API health: {str(e)}")
            return False, {"error": str(e)}
    
    def process_nl_query(self, db_name, query):
        """Process natural language query"""
        logger.info(f"Processing natural language query on database {db_name}: {query}")
        
        try:
            response = requests.post(
                f"{self.api_url}/query/{db_name}",
                json={"query": query},
                timeout=60,  # Increased timeout for NL processing
                headers={'Accept': 'application/json; charset=utf-8'}
            )
            response.raise_for_status()
            
            # Use response.content to get raw bytes and decode with utf-8
            data = json.loads(response.content.decode('utf-8'))
            
            logger.debug(f"NL Query processing successful")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error processing NL query on database {db_name}: {str(e)}")
            error_msg = str(e)
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass
                    
            return {"error": error_msg, "query": query}

class LangChainQueryClient:
    """Client for LangChain Query API"""
    
    def __init__(self, api_url):
        """Initialize LangChain Query API client"""
        self.api_url = api_url
        logger.info(f"Initialized LangChain Query API client with URL: {api_url}")
    
    def get_health(self):
        """Get health status of the LangChain Query API"""
        logger.debug("Getting LangChain Query API health")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            return True, data
        except Exception as e:
            logger.error(f"Error getting LangChain Query API health: {str(e)}")
            return False, {"error": str(e)}
    
    def process_langchain_query(self, db_name, query):
        """Process natural language query using LangChain"""
        logger.info(f"Processing LangChain query on database {db_name}: {query}")
        
        try:
            response = requests.post(
                f"{self.api_url}/query/{db_name}",
                json={"query": query},
                timeout=60  # Increased timeout for LangChain processing
            )
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"LangChain Query processing successful")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error processing LangChain query on database {db_name}: {str(e)}")
            error_msg = str(e)
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass
                    
            return {"error": error_msg, "query": query}

# Initialize clients
db_client = DatabaseClient(DATABASE_API_URL)
nl_client = NLQueryClient(NL_QUERY_API_URL)
langchain_client = LangChainQueryClient(LANGCHAIN_QUERY_API_URL)

@app.route('/')
def index():
    """Render index page"""
    logger.debug("Rendering index page")
    
    # Get list of databases
    databases = db_client.get_databases()
    
    # Check health of services
    db_health, _ = db_client.get_health()
    nl_health, _ = nl_client.get_health()
    
    return render_template(
        'index.html',
        databases=databases,
        db_service_health=db_health,
        nl_service_health=nl_health
    )

@app.route('/database/<db_name>')
def database_view(db_name):
    """Render database view page"""
    logger.debug(f"Rendering database view page for database: {db_name}")
    
    # Get database schema
    schema = db_client.get_schema(db_name)
    
    # Get sample queries
    sample_queries = db_client.get_sample_queries(db_name)
    
    return render_template(
        'database.html',
        db_name=db_name,
        schema=schema,
        sample_queries=sample_queries
    )

@app.route('/api/execute_query', methods=['POST'])
def api_execute_query():
    """API endpoint for executing SQL query"""
    logger.debug("API execute query requested")
    
    data = request.get_json()
    if not data or "db_name" not in data or "query" not in data:
        return jsonify({"error": "Missing required parameters"}), 400
        
    db_name = data["db_name"]
    query = data["query"]
    
    result = db_client.execute_query(db_name, query)
    return jsonify(result)

@app.route('/api/nl_query', methods=['POST'])
def api_nl_query():
    """API endpoint for processing natural language query"""
    logger.debug("API NL query requested")
    
    data = request.get_json()
    if not data or "db_name" not in data or "query" not in data:
        return jsonify({"error": "Missing required parameters"}), 400
        
    db_name = data["db_name"]
    query = data["query"]
    
    result = nl_client.process_nl_query(db_name, query)
    
    # Ensure field names match what the frontend expects
    if "rows" in result and "results" not in result:
        result["results"] = result["rows"]
    
    # Return with explicit charset encoding
    return Response(
        json.dumps(result, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

@app.route('/api/langchain_query', methods=['POST'])
def api_langchain_query():
    """API endpoint for processing natural language query using LangChain"""
    logger.debug("API LangChain query requested")
    
    data = request.get_json()
    if not data or "db_name" not in data or "query" not in data:
        return jsonify({"error": "Missing required parameters"}), 400
        
    db_name = data["db_name"]
    query = data["query"]
    
    result = langchain_client.process_langchain_query(db_name, query)
    return jsonify(result)

@app.route('/api/schema/<db_name>')
def api_get_schema(db_name):
    """API endpoint for getting database schema"""
    logger.debug(f"API get schema requested for database: {db_name}")
    
    schema = db_client.get_schema(db_name)
    return jsonify({"database": db_name, "schema": schema})

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.debug("Health check requested")
    
    # Check health of services
    db_health, db_data = db_client.get_health()
    nl_health, nl_data = nl_client.get_health()
    langchain_health, langchain_data = langchain_client.get_health()
    
    health_status = {
        "status": "healthy" if db_health and nl_health and langchain_health else "degraded",
        "timestamp": time.time(),
        "dependencies": {
            "database_api": {
                "status": "healthy" if db_health else "unhealthy",
                "details": db_data
            },
            "nl_query_api": {
                "status": "healthy" if nl_health else "unhealthy",
                "details": nl_data
            },
            "langchain_query_api": {
                "status": "healthy" if langchain_health else "unhealthy",
                "details": langchain_data
            }
        }
    }
    
    return jsonify(health_status)

def main():
    """Main entry point"""
    logger.info("Starting SQLite Database Web UI")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG")

if __name__ == "__main__":
    main()
