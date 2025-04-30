#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inpit SQLite MCP Module

This module provides MCP tools and resources for interacting with the Inpit SQLite service.
It enables querying patent data by application number, applicant name, and executing SQL queries.
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    filename='/tmp/inpit-sqlite-mcp.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPIT_API_URL = os.environ.get('INPIT_API_URL', 'http://localhost:5001')

# Schema definitions for MCP tools
SCHEMAS = {
    "get_patent_by_application_number": {
        "type": "object",
        "properties": {
            "application_number": {
                "type": "string",
                "description": "出願番号または部分的な番号"
            }
        },
        "required": ["application_number"]
    },
    "get_patents_by_applicant": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名または部分的な名称"
            }
        },
        "required": ["applicant_name"]
    },
    "execute_sql_query": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "実行するSQLクエリ（SELECT文のみ）"
            }
        },
        "required": ["query"]
    }
}

class InpitSQLiteMCPServer:
    """MCP Server for Inpit SQLite database interactions"""
    
    def __init__(self, api_url: str = INPIT_API_URL):
        """
        Initialize the server

        Args:
            api_url: Base URL for the Inpit SQLite API service
        """
        self.api_url = api_url
        logger.info(f"Initialized Inpit SQLite MCP Server with API URL: {self.api_url}")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return [
            {
                "name": "get_patent_by_application_number",
                "description": "出願番号で特許情報を検索します（部分一致も可）",
                "schema": SCHEMAS["get_patent_by_application_number"]
            },
            {
                "name": "get_patents_by_applicant",
                "description": "出願人名で特許情報を検索します（部分一致も可）",
                "schema": SCHEMAS["get_patents_by_applicant"]
            },
            {
                "name": "execute_sql_query",
                "description": "SQLクエリを実行して特許データベースに対する検索を行います（SELECT文のみ）",
                "schema": SCHEMAS["execute_sql_query"]
            }
        ]
    
    def get_resources(self) -> List[Dict[str, str]]:
        """Return list of available resources"""
        return [
            {
                "uri": "inpit-sqlite://status",
                "description": "Inpit SQLiteサービスのステータス情報とデータベーススキーマ"
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
        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
        
        try:
            if tool_name == "get_patent_by_application_number":
                return self._get_patent_by_application_number(arguments)
            elif tool_name == "get_patents_by_applicant":
                return self._get_patents_by_applicant(arguments)
            elif tool_name == "execute_sql_query":
                return self._execute_sql_query(arguments)
            else:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
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
        logger.info(f"Accessing resource: {uri}")
        
        try:
            if uri == "inpit-sqlite://status":
                return self._get_status()
            else:
                error_msg = f"Unknown resource URI: {uri}"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error accessing resource {uri}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_patent_by_application_number(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get patent information by application number
        
        Args:
            arguments: Arguments containing application_number
            
        Returns:
            Patent information matching the application number
        """
        application_number = arguments.get("application_number")
        if not application_number:
            return {"error": "application_number is required"}
        
        encoded_app_number = quote(application_number)
        url = f"{self.api_url}/api/application/{encoded_app_number}"
        
        logger.info(f"Getting patent by application number: {application_number}")
        logger.info(f"Request URL: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Process the results to make them more readable for LLM
            if data.get("success") and data.get("results"):
                results = data.get("results", [])
                columns = data.get("columns", [])
                
                processed_results = []
                for result in results:
                    row_data = {}
                    for i, col in enumerate(columns):
                        if i < len(result):
                            row_data[col] = result[i]
                    processed_results.append(row_data)
                
                return {
                    "success": True,
                    "application_number": application_number,
                    "patents": processed_results,
                    "count": len(processed_results)
                }
            else:
                return {
                    "success": False,
                    "message": "No patents found matching the application number",
                    "application_number": application_number
                }
        else:
            return {
                "error": f"API request failed with status code: {response.status_code}",
                "details": response.text
            }
    
    def _get_patents_by_applicant(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get patent information by applicant name
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            Patent information for the specified applicant
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        encoded_applicant = quote(applicant_name)
        url = f"{self.api_url}/api/applicant/{encoded_applicant}"
        
        logger.info(f"Getting patents by applicant: {applicant_name}")
        logger.info(f"Request URL: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Process the results to make them more readable for LLM
            if data.get("success") and data.get("results"):
                results = data.get("results", [])
                columns = data.get("columns", [])
                
                processed_results = []
                for result in results:
                    row_data = {}
                    for i, col in enumerate(columns):
                        if i < len(result):
                            row_data[col] = result[i]
                    processed_results.append(row_data)
                
                return {
                    "success": True,
                    "applicant_name": applicant_name,
                    "patents": processed_results,
                    "count": len(processed_results)
                }
            else:
                return {
                    "success": False,
                    "message": "No patents found for this applicant",
                    "applicant_name": applicant_name
                }
        else:
            return {
                "error": f"API request failed with status code: {response.status_code}",
                "details": response.text
            }
    
    def _execute_sql_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SQL query against the patent database
        
        Args:
            arguments: Arguments containing query
            
        Returns:
            Query results
        """
        query = arguments.get("query")
        if not query:
            return {"error": "query is required"}
        
        # Basic security check - only allow SELECT queries
        if not query.strip().lower().startswith("select"):
            return {"error": "Only SELECT queries are allowed for security reasons"}
        
        url = f"{self.api_url}/api/sql-query"
        payload = {"query": query}
        
        logger.info(f"Executing SQL query: {query}")
        logger.info(f"Request URL: {url}")
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            # Process the results to make them more readable for LLM
            if data.get("success") and data.get("results"):
                results = data.get("results", [])
                columns = data.get("columns", [])
                
                processed_results = []
                for result in results:
                    row_data = {}
                    for i, col in enumerate(columns):
                        if i < len(result):
                            row_data[col] = result[i]
                    processed_results.append(row_data)
                
                return {
                    "success": True,
                    "query": query,
                    "columns": columns,
                    "results": processed_results,
                    "count": len(processed_results)
                }
            else:
                return {
                    "success": False,
                    "message": "Query executed but returned no results",
                    "query": query
                }
        else:
            return {
                "error": f"API request failed with status code: {response.status_code}",
                "details": response.text
            }
    
    def _get_status(self) -> Dict[str, Any]:
        """
        Get status information about the Inpit SQLite service
        
        Returns:
            Status information and database schema
        """
        url = f"{self.api_url}/api/status"
        
        logger.info(f"Getting API status from: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API status request failed with status code: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "error": f"Failed to get API status: {str(e)}",
                "service_url": self.api_url
            }

# Create singleton instance
inpit_sqlite_server = InpitSQLiteMCPServer()

# MCP server functions that will be called by the MCP framework
def get_tools():
    """Return the tools provided by this server"""
    return inpit_sqlite_server.get_tools()

def get_resources():
    """Return the resources provided by this server"""
    return inpit_sqlite_server.get_resources()

def execute_tool(tool_name, arguments):
    """Execute a tool with the given arguments"""
    arguments_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
    return inpit_sqlite_server.execute_tool(tool_name, arguments_dict)

def access_resource(uri):
    """Access a resource by URI"""
    return inpit_sqlite_server.access_resource(uri)
