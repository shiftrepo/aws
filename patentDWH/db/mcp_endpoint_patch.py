"""
Patch module to add MCP endpoint to the database service
This file adds the necessary MCP endpoint implementation to the Flask app
"""

from flask import request, jsonify
import logging
import sqlite3
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database file paths from the main app
from app import INPIT_DB_PATH, GOOGLE_PATENTS_GCP_DB_PATH, GOOGLE_PATENTS_S3_DB_PATH

def add_mcp_endpoint(app):
    """Add MCP endpoint to the Flask app"""
    
    @app.route('/api/v1/mcp', methods=['POST'])
    def mcp_endpoint():
        """Model Context Protocol (MCP) endpoint for the database service"""
        try:
            # Parse request
            data = request.get_json()
            if not data or 'tool_name' not in data or 'tool_input' not in data:
                logger.warning("Invalid MCP request format")
                return jsonify({
                    "success": False,
                    "error": "Invalid request format. Expected tool_name and tool_input fields."
                }), 400
                
            tool_name = data['tool_name']
            tool_input = data['tool_input']
            
            logger.info(f"MCP request for tool: {tool_name}")
            
            # Handle different tools
            if tool_name == "get_sql_examples":
                # Return SQL examples for specified database
                db_type = tool_input.get('db_type', 'inpit')
                return get_sql_examples(db_type)
                
            elif tool_name == "get_schema_info":
                # Get database schema information
                db_type = tool_input.get('db_type', 'inpit')
                return get_schema_info(db_type)
                
            elif tool_name == "execute_sql":
                # Execute SQL query
                query = tool_input.get('query', '')
                db_type = tool_input.get('db_type', 'inpit')
                
                if not query:
                    return jsonify({
                        "success": False, 
                        "error": "Query is required"
                    }), 400
                    
                # Forward to SQL query endpoint
                from app import query as execute_query
                return execute_query(query, db_type)
            
            else:
                # Unknown tool
                return jsonify({
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }), 400
                
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return jsonify({
                "success": False,
                "error": f"Error processing request: {str(e)}"
            }), 500

    def get_sql_examples(db_type):
        """Return SQL examples for specified database"""
        examples = {
            "inpit": [
                {
                    "name": "基本検索",
                    "description": "基本的な特許情報の検索",
                    "sql": "SELECT * FROM inpit_data LIMIT 10;"
                },
                {
                    "name": "出願人による検索",
                    "description": "特定の企業・出願人の特許を検索",
                    "sql": "SELECT * FROM inpit_data WHERE applicant LIKE '%テック%' ORDER BY application_date DESC LIMIT 20;"
                },
                {
                    "name": "日付範囲による検索",
                    "description": "特定の期間の特許を検索",
                    "sql": "SELECT * FROM inpit_data WHERE application_date BETWEEN '2022-01-01' AND '2023-12-31' ORDER BY application_date DESC LIMIT 20;"
                },
                {
                    "name": "集計クエリ",
                    "description": "年ごとの出願数を集計",
                    "sql": "SELECT strftime('%Y', application_date) as year, COUNT(*) as application_count FROM inpit_data GROUP BY strftime('%Y', application_date) ORDER BY year DESC;"
                }
            ],
            "google_patents_gcp": [
                {
                    "name": "基本検索",
                    "description": "基本的な特許情報の検索",
                    "sql": "SELECT publication_number, title_ja, publication_date, assignee_harmonized FROM publications LIMIT 10;"
                },
                {
                    "name": "タイトルによる検索",
                    "description": "特定のキーワードを含む特許を検索",
                    "sql": "SELECT publication_number, title_ja, abstract_ja, assignee_harmonized, publication_date FROM publications WHERE title_ja LIKE '%人工知能%' OR title_ja LIKE '%AI%' ORDER BY publication_date DESC LIMIT 15;"
                },
                {
                    "name": "ファミリー検索",
                    "description": "特許ファミリーのサイズによる検索",
                    "sql": "SELECT p.publication_number, p.title_ja, p.publication_date, p.assignee_harmonized, p.family_id, COUNT(pf.publication_number) as family_size FROM publications p JOIN patent_families pf ON p.family_id = pf.family_id GROUP BY p.family_id HAVING family_size > 2 ORDER BY family_size DESC LIMIT 15;"
                },
                {
                    "name": "年別特許数",
                    "description": "年ごとの特許発行数",
                    "sql": "SELECT substr(publication_date, 1, 4) as year, COUNT(*) as patent_count FROM publications GROUP BY year ORDER BY year DESC;"
                }
            ],
            "google_patents_s3": [
                {
                    "name": "基本検索",
                    "description": "基本的な特許情報の検索",
                    "sql": "SELECT publication_number, title_ja, publication_date, assignee_harmonized FROM publications LIMIT 10;"
                },
                {
                    "name": "タイトルによる検索",
                    "description": "特定のキーワードを含む特許を検索",
                    "sql": "SELECT publication_number, title_ja, abstract_ja, assignee_harmonized, publication_date FROM publications WHERE title_ja LIKE '%機械学習%' OR title_ja LIKE '%深層学習%' ORDER BY publication_date DESC LIMIT 15;"
                },
                {
                    "name": "企業別特許数",
                    "description": "企業ごとの特許数を集計",
                    "sql": "SELECT assignee_harmonized as company, COUNT(*) as patent_count FROM publications WHERE assignee_harmonized IS NOT NULL GROUP BY assignee_harmonized ORDER BY patent_count DESC LIMIT 20;"
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "db_type": db_type,
            "examples": examples.get(db_type, [])
        })

    def get_schema_info(db_type):
        """Get database schema information"""
        try:
            # Select database based on type
            db_path = INPIT_DB_PATH
            if db_type == 'google_patents_gcp':
                db_path = GOOGLE_PATENTS_GCP_DB_PATH
            elif db_type == 'google_patents_s3':
                db_path = GOOGLE_PATENTS_S3_DB_PATH
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {"tables": {}}
            
            # Get column info for each table
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                schema_info["tables"][table] = {"columns": columns}
            
            conn.close()
            
            return jsonify({
                "success": True,
                "db_type": db_type,
                "schema": schema_info
            })
            
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return jsonify({
                "success": False,
                "error": f"Error getting schema info: {str(e)}"
            }), 500
