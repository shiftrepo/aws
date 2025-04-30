#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Patent Analysis Server

This server provides specialized tools for patent examiners to analyze applicant data.
It uses the Inpit SQLite database as its data source.
"""

import json
import os
import tempfile
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.patent_system.patent_analyzer_inpit import PatentAnalyzerInpit
from app.patent_system.inpit_sqlite_connector import get_connector

# Schema definitions for MCP tools
SCHEMAS = {
    "query_patents": {
        "type": "object",
        "properties": {
            "application_number": {
                "type": "string",
                "description": "Patent application number"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        }
    },
    "search_patents_by_applicant": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of patent applicant"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["applicant_name"]
    },
    "execute_sql_query": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute (must be a SELECT query)"
            }
        },
        "required": ["query"]
    },
    "analyze_technology_trends": {
        "type": "object",
        "properties": {
            "years": {
                "type": "integer",
                "description": "Number of years to analyze",
                "default": 10,
                "minimum": 1,
                "maximum": 20
            },
            "top_n": {
                "type": "integer",
                "description": "Number of top technologies to include",
                "default": 5,
                "minimum": 1,
                "maximum": 20
            }
        }
    },
    "analyze_applicant_competition": {
        "type": "object",
        "properties": {
            "top_n": {
                "type": "integer",
                "description": "Number of top applicants to analyze",
                "default": 10,
                "minimum": 1,
                "maximum": 20
            }
        }
    },
    "analyze_patent_landscape": {
        "type": "object",
        "properties": {
            "ipc_level": {
                "type": "integer",
                "description": "Level of IPC hierarchy for grouping (1=section, 2=class, 3=subclass)",
                "default": 3,
                "minimum": 1,
                "maximum": 3
            }
        }
    },
    "generate_analysis_report": {
        "type": "object",
        "properties": {}
    },
    "get_patent_stats": {
        "type": "object",
        "properties": {}
    }
}

class PatentInpitServer:
    """MCP Server for patent analysis"""

    def __init__(self):
        """Initialize the server"""
        # Get API URL from environment or use default
        api_url = os.environ.get("INPIT_API_URL", "http://localhost:5001")
        self.connector = get_connector(api_url)
        self.analyzer = PatentAnalyzerInpit(api_url)

    def get_tools(self):
        """Return list of available tools"""
        return [
            {
                "name": "query_patents",
                "description": "Query patents by application number",
                "schema": SCHEMAS["query_patents"]
            },
            {
                "name": "search_patents_by_applicant",
                "description": "Search patents by applicant name",
                "schema": SCHEMAS["search_patents_by_applicant"]
            },
            {
                "name": "execute_sql_query",
                "description": "Execute a SQL query against the patent database",
                "schema": SCHEMAS["execute_sql_query"]
            },
            {
                "name": "analyze_technology_trends",
                "description": "Analyze technology trends based on IPC classifications",
                "schema": SCHEMAS["analyze_technology_trends"]
            },
            {
                "name": "analyze_applicant_competition",
                "description": "Analyze competition between patent applicants",
                "schema": SCHEMAS["analyze_applicant_competition"]
            },
            {
                "name": "analyze_patent_landscape",
                "description": "Analyze patent landscape by IPC classification hierarchy",
                "schema": SCHEMAS["analyze_patent_landscape"]
            },
            {
                "name": "generate_analysis_report",
                "description": "Generate a comprehensive patent analysis report",
                "schema": SCHEMAS["generate_analysis_report"]
            },
            {
                "name": "get_patent_stats",
                "description": "Get basic statistics about patents in the database",
                "schema": SCHEMAS["get_patent_stats"]
            }
        ]

    def get_resources(self):
        """Return list of available resources"""
        return [
            {
                "uri": "inpit-status",
                "description": "Status information from Inpit SQLite database"
            },
            {
                "uri": "ipc-descriptions",
                "description": "Descriptions of IPC classification codes"
            }
        ]

    def execute_tool(self, tool_name, arguments):
        """Execute a specific tool with the given arguments"""
        try:
            arguments_dict = json.loads(arguments) if isinstance(arguments, str) else arguments

            if tool_name == "query_patents":
                return self._query_patents(arguments_dict)
            elif tool_name == "search_patents_by_applicant":
                return self._search_patents_by_applicant(arguments_dict)
            elif tool_name == "execute_sql_query":
                return self._execute_sql_query(arguments_dict)
            elif tool_name == "analyze_technology_trends":
                return self._analyze_technology_trends(arguments_dict)
            elif tool_name == "analyze_applicant_competition":
                return self._analyze_applicant_competition(arguments_dict)
            elif tool_name == "analyze_patent_landscape":
                return self._analyze_patent_landscape(arguments_dict)
            elif tool_name == "generate_analysis_report":
                return self._generate_analysis_report(arguments_dict)
            elif tool_name == "get_patent_stats":
                return self._get_patent_stats(arguments_dict)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": f"Error executing tool {tool_name}: {str(e)}"}

    def access_resource(self, uri):
        """Access a specific resource by URI"""
        try:
            if uri == "inpit-status":
                return self._get_inpit_status()
            elif uri == "ipc-descriptions":
                return self._get_ipc_descriptions()
            else:
                return {"error": f"Unknown resource URI: {uri}"}
        except Exception as e:
            return {"error": f"Error accessing resource {uri}: {str(e)}"}

    def _query_patents(self, arguments):
        """Query patents by application number"""
        application_number = arguments.get("application_number", "")
        limit = arguments.get("limit", 10)

        if application_number:
            result = self.connector.get_patent_by_application_number(application_number)

            if "error" in result:
                return {"error": result["error"]}

            # Map to patent model format
            patents = self.connector.map_to_patent_model(result)

            if not patents:
                return {
                    "message": f"No patents found with application number: {application_number}",
                    "patents": []
                }

            # Limit the number of patents
            patents = patents[:limit]

            return {
                "message": f"Found {len(patents)} patents matching application number: {application_number}",
                "patents": patents
            }
        else:
            # Get random patents if no application number provided
            query = f"SELECT * FROM inpit_data ORDER BY RANDOM() LIMIT {limit}"
            result = self.connector.execute_sql_query(query)

            if "error" in result:
                return {"error": result["error"]}

            # Map to patent model format
            patents = self.connector.map_to_patent_model(result)

            return {
                "message": f"Retrieved {len(patents)} random patents",
                "patents": patents
            }

    def _search_patents_by_applicant(self, arguments):
        """Search patents by applicant name"""
        applicant_name = arguments.get("applicant_name", "")
        limit = arguments.get("limit", 10)

        if not applicant_name:
            return {"error": "applicant_name is required"}

        result = self.connector.get_patents_by_applicant(applicant_name)

        if "error" in result:
            return {"error": result["error"]}

        # Map to patent model format
        patents = self.connector.map_to_patent_model(result)

        if not patents:
            return {
                "message": f"No patents found for applicant: {applicant_name}",
                "patents": []
            }

        # Limit the number of patents
        patents = patents[:limit]

        return {
            "message": f"Found {len(patents)} patents for applicant: {applicant_name}",
            "patents": patents
        }

    def _execute_sql_query(self, arguments):
        """Execute a SQL query against the database"""
        query = arguments.get("query", "")

        if not query:
            return {"error": "query is required"}

        if not query.strip().lower().startswith("select"):
            return {"error": "Only SELECT queries are allowed"}

        result = self.connector.execute_sql_query(query)

        return result

    def _analyze_technology_trends(self, arguments):
        """Analyze technology trends"""
        years = arguments.get("years", 10)
        top_n = arguments.get("top_n", 5)

        result = self.analyzer.analyze_technology_trends(years=years, top_n=top_n)

        return result

    def _analyze_applicant_competition(self, arguments):
        """Analyze competition between patent applicants"""
        top_n = arguments.get("top_n", 10)

        result = self.analyzer.analyze_applicant_competition(top_n=top_n)

        return result

    def _analyze_patent_landscape(self, arguments):
        """Analyze patent landscape"""
        ipc_level = arguments.get("ipc_level", 3)

        result = self.analyzer.analyze_patent_landscape(ipc_level=ipc_level)

        return result

    def _generate_analysis_report(self, arguments):
        """Generate a comprehensive analysis report"""
        report = self.analyzer.generate_analysis_report()

        return {
            "report": report,
            "format": "markdown"
        }

    def _get_patent_stats(self, arguments):
        """Get basic statistics about patents in the database"""
        # Get stats from Inpit SQLite
        status = self.connector.get_api_status()

        if "error" in status:
            return {"error": status["error"]}

        # Get record count
        record_count = status.get("record_count", 0) if "record_count" in status else 0

        # Get distinct applicant count
        applicant_query = """
            SELECT COUNT(DISTINCT 出願人) FROM inpit_data
            WHERE 出願人 IS NOT NULL
        """
        applicant_result = self.connector.execute_sql_query(applicant_query)
        applicant_count = 0

        if applicant_result.get("success") and applicant_result.get("results"):
            try:
                applicant_count = applicant_result["results"][0][0]
            except (IndexError, ValueError):
                pass

        # Get distinct IPC count
        ipc_query = """
            SELECT COUNT(DISTINCT 国際特許分類) FROM inpit_data
            WHERE 国際特許分類 IS NOT NULL
        """
        ipc_result = self.connector.execute_sql_query(ipc_query)
        ipc_count = 0

        if ipc_result.get("success") and ipc_result.get("results"):
            try:
                ipc_count = ipc_result["results"][0][0]
            except (IndexError, ValueError):
                pass

        # Get date range
        date_query = """
            SELECT
                MIN(出願日) as earliest_date,
                MAX(出願日) as latest_date
            FROM inpit_data
            WHERE 出願日 IS NOT NULL
        """
        date_result = self.connector.execute_sql_query(date_query)
        earliest_date = None
        latest_date = None

        if date_result.get("success") and date_result.get("results"):
            try:
                row = date_result["results"][0]
                earliest_date = row[0]
                latest_date = row[1]
            except (IndexError, ValueError):
                pass

        return {
            "total_patents": record_count,
            "unique_applicants": applicant_count,
            "unique_ipc_classifications": ipc_count,
            "date_range": {
                "earliest": earliest_date,
                "latest": latest_date
            },
            "data_source": "Inpit SQLite",
            "api_url": self.connector.api_url
        }

    def _get_inpit_status(self):
        """Get status information from Inpit SQLite database"""
        return self.connector.get_api_status()

    def _get_ipc_descriptions(self):
        """Get descriptions of IPC classification codes"""
        # Use helper method from analyzer
        ipc_codes = [
            "A", "B", "C", "D", "E", "F", "G", "H",
            "G06", "G06F", "G06N", "G06Q", "H04", "H04L", "H04N",
            "H01", "H01L", "A61", "A61K", "B60", "C07", "C12"
        ]

        return self.analyzer._get_ipc_class_descriptions(ipc_codes)

# Create singleton instance for use with the MCP server
patent_inpit_server = PatentInpitServer()

# MCP server functions that will be called by the MCP framework

def get_tools():
    """Return the tools provided by this server"""
    return patent_inpit_server.get_tools()

def get_resources():
    """Return the resources provided by this server"""
    return patent_inpit_server.get_resources()

def execute_tool(tool_name, arguments):
    """Execute a tool with the given arguments"""
    return patent_inpit_server.execute_tool(tool_name, arguments)

def access_resource(uri):
    """Access a resource by URI"""
    return patent_inpit_server.access_resource(uri)
