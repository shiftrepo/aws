#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Patents MCP Integration

This module extends the Inpit SQLite MCP Server with Google Patents Public Data functionality.
It adds tools for importing Japanese patents, querying with natural language, and 
retrieving patent family relationships.
"""

import os
import json
import logging
from typing import Dict, List, Any

# Import Google Patents functionality
from google_patents_fetcher import GooglePatentsFetcher
from nl_query_processor import PatentNLQueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths to Google Patents databases
GOOGLE_PATENTS_DB_PATH = "/app/data/google_patents_gcp.db"  # GCP data
S3_LOCAL_DB_PATH = "/app/data/google_patents_s3.db"        # S3 downloaded data

# Schema definitions for MCP tools
SCHEMAS = {
    "import_japanese_patents": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "取得する特許公開の数（約）",
                "default": 10000,
                "minimum": 1000,
                "maximum": 50000
            },
            "credentials_path": {
                "type": "string",
                "description": "Google Cloud認証情報のJSONファイルへのパス（オプション）"
            }
        },
        "required": []
    },
    "query_patents_natural_language": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "特許データに対する自然言語クエリ"
            }
        },
        "required": ["query"]
    },
    "get_patent_family_members": {
        "type": "object",
        "properties": {
            "application_number": {
                "type": "string",
                "description": "ファミリーメンバーを検索する出願番号"
            }
        },
        "required": ["application_number"]
    }
}

class GooglePatentsMCPExtension:
    """Extension for Google Patents functionality in MCP"""
    
    def __init__(self):
        """
        Initialize the Google Patents functionality
        """
        try:
            # First try to use the GCP database
            if os.path.exists(GOOGLE_PATENTS_DB_PATH) and os.path.getsize(GOOGLE_PATENTS_DB_PATH) > 10485760:
                self.active_db_path = GOOGLE_PATENTS_DB_PATH
                logger.info(f"Using GCP database: {GOOGLE_PATENTS_DB_PATH}")
            # Fall back to S3 database if GCP database doesn't exist or is too small
            elif os.path.exists(S3_LOCAL_DB_PATH) and os.path.getsize(S3_LOCAL_DB_PATH) > 10485760:
                self.active_db_path = S3_LOCAL_DB_PATH
                logger.info(f"Using S3 database: {S3_LOCAL_DB_PATH}")
            # Default to GCP database path even if it doesn't exist yet
            else:
                self.active_db_path = GOOGLE_PATENTS_DB_PATH
                logger.warning(f"No valid database found, defaulting to GCP database path: {GOOGLE_PATENTS_DB_PATH}")
            
            self.patent_fetcher = GooglePatentsFetcher(db_path=self.active_db_path)
            self.nl_processor = PatentNLQueryProcessor(db_path=self.active_db_path)
            logger.info(f"Google Patents functionality initialized with database: {self.active_db_path}")
        except Exception as e:
            logger.error(f"Error initializing Google Patents functionality: {e}")
            self.active_db_path = GOOGLE_PATENTS_DB_PATH  # Default to GCP path if initialization fails
            # We'll continue even if this fails
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return [
            {
                "name": "import_japanese_patents",
                "description": "Google Patents Public Dataから日本国特許公開データを取得してSQLiteに格納します",
                "schema": SCHEMAS["import_japanese_patents"]
            },
            {
                "name": "query_patents_natural_language",
                "description": "自然言語で特許データを検索します",
                "schema": SCHEMAS["query_patents_natural_language"]
            },
            {
                "name": "get_patent_family_members",
                "description": "特定の出願番号に関するファミリー出願（関連出願）を取得します",
                "schema": SCHEMAS["get_patent_family_members"]
            }
        ]
    
    def get_resources(self) -> List[Dict[str, str]]:
        """Return list of available resources"""
        return [
            {
                "uri": "google-patents://status",
                "description": "Google Patents SQLiteサービスのステータス情報とデータベーススキーマ"
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with the given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        logger.info(f"Executing Google Patents tool: {tool_name} with arguments: {arguments}")
        
        try:
            if tool_name == "import_japanese_patents":
                return self._import_japanese_patents(arguments)
            elif tool_name == "query_patents_natural_language":
                return self._query_patents_natural_language(arguments)
            elif tool_name == "get_patent_family_members":
                return self._get_patent_family_members(arguments)
            else:
                error_msg = f"Unknown Google Patents tool: {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error executing Google Patents tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def access_resource(self, uri: str) -> Dict[str, Any]:
        """
        Access a specific resource by URI
        
        Args:
            uri: URI of the resource to access
            
        Returns:
            Resource data
        """
        logger.info(f"Accessing Google Patents resource: {uri}")
        
        try:
            if uri == "google-patents://status":
                return self._get_google_patents_status()
            else:
                error_msg = f"Unknown Google Patents resource URI: {uri}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error accessing Google Patents resource {uri}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _import_japanese_patents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import Japanese patents from Google Patents Public Data
        
        Args:
            arguments: Arguments containing limit and optional credentials_path
            
        Returns:
            Import results
        """
        try:
            limit = arguments.get("limit", 5000)  # Default reduced to 5000
            credentials_path = arguments.get("credentials_path", None)
            
            # Ensure limit is within reasonable bounds
            limit = max(1000, min(limit, 50000))
            
            # Re-initialize the patent fetcher to use S3 credentials 
            # The GooglePatentsFetcher will automatically handle S3 credentials fetching
            self.patent_fetcher = GooglePatentsFetcher(
                credentials_path=credentials_path,  # This is now optional and used as a fallback
                db_path=GOOGLE_PATENTS_DB_PATH  # Always import to the GCP database
            )
            
            # Import the patents
            count = self.patent_fetcher.fetch_japanese_patents(limit=limit)
            
            if count > 0:
                return {
                    "success": True,
                    "count": count,
                    "message": f"成功: {count}件の日本国特許を取得しました。"
                }
            else:
                return {
                    "success": False,
                    "count": 0,
                    "message": "特許データの取得に失敗しました。詳細はログをご確認ください。",
                    "error": "No patents were imported"
                }
        except Exception as e:
            error_msg = f"Error importing Japanese patents: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message": "特許データの取得中にエラーが発生しました。"
            }
    
    def _query_patents_natural_language(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query patents using natural language
        
        Args:
            arguments: Arguments containing the natural language query
            
        Returns:
            Query results
        """
        try:
            query = arguments.get("query")
            if not query:
                return {"error": "query parameter is required"}
            
            result = self.nl_processor.process_and_execute(query)
            
            # Format the result for better readability
            if result.get("success"):
                return {
                    "success": True,
                    "query": query,
                    "sql_query": result.get("sql_query"),
                    "count": result.get("count", 0),
                    "results": result.get("results", [])
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": result.get("error", "Unknown error processing natural language query")
                }
        except Exception as e:
            error_msg = f"Error processing natural language query: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_patent_family_members(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all family members for a given application number
        
        Args:
            arguments: Arguments containing application_number
            
        Returns:
            Family member information
        """
        try:
            application_number = arguments.get("application_number")
            if not application_number:
                return {"error": "application_number is required"}
            
            family_members = self.patent_fetcher.get_family_members(application_number)
            
            return {
                "success": True,
                "application_number": application_number,
                "family_members": family_members,
                "count": len(family_members)
            }
        except Exception as e:
            error_msg = f"Error getting patent family members: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_google_patents_status(self) -> Dict[str, Any]:
        """
        Get status information about the Google Patents database
        
        Returns:
            Status information and database schema
        """
        try:
            import sqlite3
            
            # Check both databases and provide status for both
            gcp_db_exists = os.path.exists(GOOGLE_PATENTS_DB_PATH)
            s3_db_exists = os.path.exists(S3_LOCAL_DB_PATH)
            
            if not (gcp_db_exists or s3_db_exists):
                return {
                    "status": "not_found",
                    "message": "No Google Patents database files found",
                    "gcp_path": GOOGLE_PATENTS_DB_PATH,
                    "s3_path": S3_LOCAL_DB_PATH
                }
            
            # Use the active database for schema information
            conn = sqlite3.connect(self.active_db_path)
            cursor = conn.cursor()
            
            # Check if publications table exists
            try:
                cursor.execute("SELECT COUNT(*) FROM publications")
                publication_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM patent_families")
                family_count = cursor.fetchone()[0]
                
                # Get table schemas
                cursor.execute("PRAGMA table_info(publications)")
                publications_schema = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
                
                cursor.execute("PRAGMA table_info(patent_families)")
                families_schema = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
                
                # Get most recent publication date
                cursor.execute("SELECT MAX(publication_date) FROM publications")
                latest_publication = cursor.fetchone()[0]
                
                # Get country code distribution
                cursor.execute("""
                SELECT country_code, COUNT(*) as count 
                FROM publications 
                GROUP BY country_code 
                ORDER BY count DESC
                """)
                country_distribution = [{"country": row[0], "count": row[1]} for row in cursor.fetchall()]
                
                conn.close()
                
                # Gather status for both databases
                gcp_status = "not_found"
                s3_status = "not_found"
                
                if gcp_db_exists:
                    gcp_status = "available" if os.path.getsize(GOOGLE_PATENTS_DB_PATH) > 10485760 else "empty"
                
                if s3_db_exists:
                    s3_status = "available" if os.path.getsize(S3_LOCAL_DB_PATH) > 10485760 else "empty"
                
                return {
                    "status": "available",
                    "message": "Google Patents database is available",
                    "active_db": self.active_db_path,
                    "databases": {
                        "gcp": {
                            "path": GOOGLE_PATENTS_DB_PATH,
                            "status": gcp_status
                        },
                        "s3": {
                            "path": S3_LOCAL_DB_PATH,
                            "status": s3_status
                        }
                    },
                    "statistics": {
                        "publication_count": publication_count,
                        "family_count": family_count,
                        "latest_publication": latest_publication,
                        "country_distribution": country_distribution[:10]  # Top 10 countries
                    },
                    "schema": {
                        "publications": publications_schema,
                        "patent_families": families_schema
                    }
                }
            except sqlite3.OperationalError as e:
                conn.close()
                return {
                    "status": "empty",
                    "message": f"Google Patents database exists but tables are missing or empty: {str(e)}",
                    "path": GOOGLE_PATENTS_DB_PATH
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking Google Patents database status: {str(e)}"
            }

# Create singleton instance
google_patents_extension = GooglePatentsMCPExtension()

# Functions to integrate with the main MCP server
def get_extension_tools():
    """Return the Google Patents tools"""
    return google_patents_extension.get_tools()

def get_extension_resources():
    """Return the Google Patents resources"""
    return google_patents_extension.get_resources()

def execute_extension_tool(tool_name, arguments):
    """Execute a Google Patents tool"""
    return google_patents_extension.execute_tool(tool_name, arguments)

def access_extension_resource(uri):
    """Access a Google Patents resource"""
    return google_patents_extension.access_resource(uri)
