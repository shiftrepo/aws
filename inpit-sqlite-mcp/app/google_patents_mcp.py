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
import sqlite3
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
GOOGLE_PATENTS_DB_PATH = "/app/data/db/google_patents_gcp.db"  # GCP data
S3_LOCAL_DB_PATH = "/app/data/db/google_patents_s3.db"        # S3 downloaded data

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
            logger.info("Initializing Google Patents MCP Extension")
            logger.info(f"Checking for GCP database at: {GOOGLE_PATENTS_DB_PATH}")
            
            # Check GCP database
            gcp_exists = os.path.exists(GOOGLE_PATENTS_DB_PATH)
            logger.info(f"GCP database exists: {gcp_exists}")
            
            if gcp_exists:
                gcp_size = os.path.getsize(GOOGLE_PATENTS_DB_PATH)
                logger.info(f"GCP database size: {gcp_size} bytes")
                gcp_valid = gcp_size > 10485760  # 10MB
            else:
                gcp_valid = False
                logger.warning(f"GCP database not found at {GOOGLE_PATENTS_DB_PATH}")
            
            # Check S3 database
            logger.info(f"Checking for S3 database at: {S3_LOCAL_DB_PATH}")
            s3_exists = os.path.exists(S3_LOCAL_DB_PATH)
            logger.info(f"S3 database exists: {s3_exists}")
            
            if s3_exists:
                s3_size = os.path.getsize(S3_LOCAL_DB_PATH)
                logger.info(f"S3 database size: {s3_size} bytes")
                s3_valid = s3_size > 10485760  # 10MB
            else:
                s3_valid = False
                logger.warning(f"S3 database not found at {S3_LOCAL_DB_PATH}")
            
            # Check parent directories to verify they exist and have proper permissions
            for db_path in [GOOGLE_PATENTS_DB_PATH, S3_LOCAL_DB_PATH]:
                parent_dir = os.path.dirname(db_path)
                if os.path.exists(parent_dir):
                    logger.info(f"Parent directory exists for {db_path}: {parent_dir}")
                    # Check if directory is writable
                    if os.access(parent_dir, os.W_OK):
                        logger.info(f"Directory {parent_dir} is writable")
                    else:
                        logger.error(f"Directory {parent_dir} is not writable!")
                else:
                    logger.error(f"Parent directory does not exist for {db_path}: {parent_dir}")
            
            # Determine which database to use
            if gcp_valid:
                self.active_db_path = GOOGLE_PATENTS_DB_PATH
                logger.info(f"Using GCP database: {GOOGLE_PATENTS_DB_PATH}")
            elif s3_valid:
                self.active_db_path = S3_LOCAL_DB_PATH
                logger.info(f"Using S3 database: {S3_LOCAL_DB_PATH}")
            else:
                self.active_db_path = GOOGLE_PATENTS_DB_PATH
                logger.warning(f"No valid database found, defaulting to GCP database path: {GOOGLE_PATENTS_DB_PATH}")
                logger.error("Both GCP and S3 databases are missing or invalid - this will cause problems!")
            
            logger.info(f"Initializing patent fetcher with database path: {self.active_db_path}")
            self.patent_fetcher = GooglePatentsFetcher(db_path=self.active_db_path)
            
            logger.info(f"Initializing NL query processor with database path: {self.active_db_path}")
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
            
            # Check if patents were imported
            if count > 0:
                return {
                    "success": True,
                    "count": count,
                    "message": f"成功: {count}件の日本国特許を取得しました。"
                }
            elif count == 0:
                # count=0 is returned when BigQuery fails but S3 download succeeds
                # Check if S3 downloaded files exist and have data
                gcp_db_exists = os.path.exists(GOOGLE_PATENTS_DB_PATH)
                s3_db_exists = os.path.exists(S3_LOCAL_DB_PATH)
                
                if gcp_db_exists or s3_db_exists:
                    # Determine which database to use for status
                    db_path = GOOGLE_PATENTS_DB_PATH if gcp_db_exists else S3_LOCAL_DB_PATH
                    
                    try:
                        # Check if the database has content
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM publications")
                        pub_count = cursor.fetchone()[0]
                        conn.close()
                        
                        if pub_count > 0:
                            return {
                                "success": True,
                                "count": pub_count,
                                "message": f"BigQueryでのデータ取得はスキップされましたが、S3から{pub_count}件の特許データを正常にダウンロードしました。",
                                "from_s3": True
                            }
                    except Exception as db_error:
                        logger.error(f"Error checking database content: {db_error}")
                
                # If we reach here, either no files were downloaded or they don't have valid data
                return {
                    "success": False,
                    "count": 0,
                    "message": "BigQueryでのデータ取得に失敗し、S3からのバックアップデータも利用できませんでした。詳細はログをご確認ください。",
                    "error": "No patents were imported and backup data is not available"
                }
            else:
                return {
                    "success": False,
                    "count": 0,
                    "message": "特許データの取得に失敗しました。詳細はログをご確認ください。",
                    "error": "Import operation failed"
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
            
            logger.info(f"Checking database status - GCP DB exists: {gcp_db_exists}, S3 DB exists: {s3_db_exists}")
            
            # Check if we need to create an empty database on the fly
            if not (gcp_db_exists or s3_db_exists):
                logger.warning("No database files found. Attempting to create an empty fallback database.")
                try:
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(S3_LOCAL_DB_PATH), exist_ok=True)
                    
                    # Create an empty SQLite database with required schema
                    conn = sqlite3.connect(S3_LOCAL_DB_PATH)
                    cursor = conn.cursor()
                    
                    # Create publications table
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS publications (
                        publication_number TEXT PRIMARY KEY,
                        filing_date TEXT,
                        publication_date TEXT,
                        application_number TEXT,
                        assignee_harmonized TEXT,
                        assignee_original TEXT,
                        title_ja TEXT,
                        title_en TEXT,
                        abstract_ja TEXT,
                        abstract_en TEXT,
                        claims TEXT,
                        ipc_code TEXT,
                        family_id TEXT,
                        country_code TEXT,
                        kind_code TEXT,
                        priority_date TEXT,
                        grant_date TEXT,
                        priority_claim TEXT,
                        status TEXT,
                        legal_status TEXT,
                        examined TEXT,
                        family_size INTEGER
                    )
                    ''')
                    
                    # Create patent_families table
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patent_families (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_id TEXT,
                        application_number TEXT,
                        publication_number TEXT,
                        country_code TEXT,
                        UNIQUE(family_id, application_number)
                    )
                    ''')
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"Successfully created empty fallback database at {S3_LOCAL_DB_PATH}")
                    s3_db_exists = True  # We've just created it
                except Exception as e:
                    logger.error(f"Failed to create empty fallback database: {str(e)}")
            
            if not (gcp_db_exists or s3_db_exists):
                return {
                    "status": "not_found",
                    "message": "No Google Patents database files found and could not create a fallback database",
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
