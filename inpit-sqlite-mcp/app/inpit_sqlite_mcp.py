#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inpit SQLite MCP Module

This module provides MCP tools and resources for interacting with the Inpit SQLite service.
It enables querying patent data by application number, applicant name, executing SQL queries,
and performing advanced patent analysis like applicant summaries, visual reports,
assessment ratio analysis, technical field analysis, and competitor comparisons.
"""

import os
import json
import requests
import logging
import re
import base64
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import quote, unquote
from collections import Counter, defaultdict

# Import new libraries for visualization and PDF generation
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from fpdf import FPDF
from PIL import Image

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
    },
    "get_applicant_summary": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            }
        },
        "required": ["applicant_name"]
    },
    "generate_visual_report": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            }
        },
        "required": ["applicant_name"]
    },
    "analyze_assessment_ratios": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            }
        },
        "required": ["applicant_name"]
    },
    "analyze_technical_fields": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            }
        },
        "required": ["applicant_name"]
    },
    "compare_with_competitors": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            },
            "num_competitors": {
                "type": "integer",
                "description": "比較する競合他社の数",
                "default": 3,
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["applicant_name"]
    },
    "generate_pdf_report": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "出願人名"
            }
        },
        "required": ["applicant_name"]
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
            },
            {
                "name": "get_applicant_summary",
                "description": "特定の出願人に関する包括的なサマリーを取得します",
                "schema": SCHEMAS["get_applicant_summary"]
            },
            {
                "name": "generate_visual_report",
                "description": "特定の出願人に関するチャートや統計を含む視覚的レポートを生成します",
                "schema": SCHEMAS["generate_visual_report"]
            },
            {
                "name": "analyze_assessment_ratios",
                "description": "特定の出願人の特許審査比率を分析します",
                "schema": SCHEMAS["analyze_assessment_ratios"]
            },
            {
                "name": "analyze_technical_fields",
                "description": "特定の出願人の技術分野分布を分析します",
                "schema": SCHEMAS["analyze_technical_fields"]
            },
            {
                "name": "compare_with_competitors",
                "description": "特定の出願人と競合他社を比較します",
                "schema": SCHEMAS["compare_with_competitors"]
            },
            {
                "name": "generate_pdf_report",
                "description": "特定の出願人に関するPDFレポートを生成します",
                "schema": SCHEMAS["generate_pdf_report"]
            }
        ]
    
    def get_resources(self) -> List[Dict[str, str]]:
        """Return list of available resources"""
        return [
            {
                "uri": "inpit-sqlite://status",
                "description": "Inpit SQLiteサービスのステータス情報とデータベーススキーマ"
            },
            {
                "uri": "inpit-sqlite://ipc-classifications",
                "description": "IPCコード（国際特許分類）の説明"
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
            elif tool_name == "get_applicant_summary":
                return self._get_applicant_summary(arguments)
            elif tool_name == "generate_visual_report":
                return self._generate_visual_report(arguments)
            elif tool_name == "analyze_assessment_ratios":
                return self._analyze_assessment_ratios(arguments)
            elif tool_name == "analyze_technical_fields":
                return self._analyze_technical_fields(arguments)
            elif tool_name == "compare_with_competitors":
                return self._compare_with_competitors(arguments)
            elif tool_name == "generate_pdf_report":
                return self._generate_pdf_report(arguments)
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
            elif uri == "inpit-sqlite://ipc-classifications":
                return self._get_ipc_classifications()
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
        
        # Ensure application_number is properly URL encoded - first decode in case it came already encoded
        encoded_app_number = quote(unquote(application_number))
        url = f"{self.api_url}/api/application/{encoded_app_number}"
        
        logger.info(f"Getting patent by application number: {application_number}")
        logger.info(f"Request URL (encoded): {url}")
        
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
        
        # Ensure applicant_name is properly URL encoded - first decode in case it came already encoded
        encoded_applicant = quote(unquote(applicant_name))
        url = f"{self.api_url}/api/applicant/{encoded_applicant}"
        
        logger.info(f"Getting patents by applicant: {applicant_name}")
        logger.info(f"Request URL (encoded): {url}")
        
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
        
        # Since we don't have a real mapping for "審査状況", we'll skip the column mapping part 
        # and instead improve error handling to show available columns when this column is used

        original_query = query
        
                # Check for Japanese column names that don't exist in the schema
        if "審査状況" in query:
            logger.info(f"Query contains non-existent column name '審査状況': {query}")
            
            # Get available columns to suggest alternatives
            try:
                logger.info("Retrieving available columns to provide in error message")
                col_query = "SELECT name FROM pragma_table_info('inpit_data')"
                col_payload = {"query": col_query}
                col_url = f"{self.api_url}/api/sql-query"
                col_response = requests.post(col_url, json=col_payload)
                
                if col_response.status_code == 200:
                    col_data = col_response.json()
                    if col_data.get("success") and col_data.get("results"):
                        columns = [row["name"] for row in col_data.get("results", []) if row.get("name")]
                        return {
                            "error": f"カラム '審査状況' はデータベースに存在しません。",
                            "message": "利用可能なカラム名は下記です：",
                            "available_columns": columns[:20],  # First 20 columns to avoid too much data
                            "note": "クエリで使用する場合は正しいカラム名を指定してください。"
                        }
            except Exception as e:
                logger.error(f"Error retrieving column list: {e}")
                
            # If we couldn't get columns, continue with the query but it will likely fail
            logger.warning("Column '審査状況' was requested but doesn't exist in the schema")
        
        url = f"{self.api_url}/api/sql-query"
        payload = {"query": query}
        
        logger.info(f"Executing SQL query: {query}")
        logger.info(f"Request URL: {url}")
        
        try:
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
                    
                    response_data = {
                        "success": True,
                        "query": query,
                        "columns": columns,
                        "results": processed_results,
                        "count": len(processed_results)
                    }
                    
                    # If we substituted columns, add a note
                    if query != original_query:
                        response_data["note"] = f"Column names were substituted in your query for compatibility."
                    
                    return response_data
                else:
                    return {
                        "success": False,
                        "message": "Query executed but returned no results",
                        "query": query
                    }
            else:
                error_text = response.text
                # Check for specific SQLite errors related to column names
                if "no such column:" in error_text:
                    # Extract the column name from error message
                    import re
                    match = re.search(r'no such column: ([\w\s\u3000-\u9fff]+)', error_text)
                    if match:
                        bad_column = match.group(1).strip()
                        
                        # Instead of just returning an error, let's get the actual column list
                        try:
                            col_query = "SELECT name FROM pragma_table_info('inpit_data')"
                            col_payload = {"query": col_query}
                            col_response = requests.post(url, json=col_payload)
                            
                            if col_response.status_code == 200:
                                col_data = col_response.json()
                                if col_data.get("success") and col_data.get("results"):
                                    columns = [row.get("name") for row in col_data.get("results", [])]
                                    
                                    return {
                                        "error": f"カラム '{bad_column}' はデータベースに存在しません。",
                                        "message": "利用可能なカラム名は下記です：",
                                        "available_columns": columns
                                    }
                            
                        except Exception as col_err:
                            logger.error(f"Error getting column list: {col_err}")
                        
                        # Fallback if we can't get columns
                        return {
                            "error": f"カラム '{bad_column}' はデータベースに存在しません。",
                            "message": "利用可能なカラム一覧は次のクエリで確認できます: SELECT name FROM pragma_table_info('inpit_data')",
                            "details": "正確なカラム名を確認してからクエリを再実行してください。"
                        }
                
                return {
                    "error": f"API request failed with status code: {response.status_code}",
                    "details": error_text
                }
        except Exception as e:
            return {
                "error": f"Error executing SQL query: {str(e)}",
                "query": query
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

    def _get_applicant_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific patent applicant
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            Comprehensive summary of the applicant's patent portfolio
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        try:
            # Get patents by this applicant
            applicant_patents = self._get_patents_by_applicant({"applicant_name": applicant_name})
            
            if "error" in applicant_patents:
                return applicant_patents
            
            if not applicant_patents.get("success") or applicant_patents.get("count", 0) == 0:
                return {
                    "success": False,
                    "message": f"No patents found for applicant: {applicant_name}"
                }
            
            patents = applicant_patents.get("patents", [])
            patent_count = applicant_patents.get("count", 0)
            
            # 1. Patent count per year
            patents_by_year = defaultdict(int)
            for patent in patents:
                if "出願日" in patent and patent["出願日"]:
                    try:
                        year = patent["出願日"].split('-')[0]
                        patents_by_year[year] += 1
                    except (IndexError, ValueError):
                        continue
            
            yearly_stats = [{"year": year, "count": count} for year, count in patents_by_year.items()]
            yearly_stats.sort(key=lambda x: x["year"])
            
            # 2. Technology fields (IPC classifications)
            ipc_counts = Counter()
            for patent in patents:
                if "国際特許分類_IPC_" in patent and patent["国際特許分類_IPC_"]:
                    ipc = patent["国際特許分類_IPC_"].split()[0] if patent["国際特許分類_IPC_"].split() else patent["国際特許分類_IPC_"]
                    ipc_counts[ipc] += 1
            
            top_technologies = [{"ipc": ipc, "count": count} for ipc, count in ipc_counts.most_common(5)]
            
            # 3. Assessment status
            assessment_status = Counter()
            for patent in patents:
                if "審査状況" in patent and patent["審査状況"]:
                    assessment_status[patent["審査状況"]] += 1
            
            status_counts = [{"status": status, "count": count} for status, count in assessment_status.most_common()]
            
            # 4. Recent patents
            try:
                recent_patents = sorted(
                    [p for p in patents if "出願日" in p and p["出願日"]],
                    key=lambda x: x["出願日"],
                    reverse=True
                )[:5]
            except Exception:
                recent_patents = patents[:5]
            
            # Combine the results
            return {
                "success": True,
                "applicant_name": applicant_name,
                "total_patents": patent_count,
                "yearly_stats": yearly_stats,
                "top_technologies": top_technologies,
                "assessment_status": status_counts,
                "recent_patents": recent_patents
            }
        
        except Exception as e:
            error_msg = f"Error generating applicant summary: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _generate_visual_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visual report with charts and statistics for the specified applicant
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            Visual report data with base64-encoded chart images
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        try:
            # Get applicant summary first
            summary = self._get_applicant_summary({"applicant_name": applicant_name})
            
            if "error" in summary:
                return summary
            
            if not summary.get("success"):
                return {
                    "success": False,
                    "message": f"Could not generate visual report for applicant: {applicant_name}"
                }
            
            # Generate actual charts using matplotlib
            chart_images = {}
            
            # 1. Patent trend over time (line chart)
            if summary.get("yearly_stats"):
                yearly_stats = summary.get("yearly_stats", [])
                if yearly_stats:
                    years = [stat["year"] for stat in yearly_stats]
                    counts = [stat["count"] for stat in yearly_stats]
                    
                    plt.figure(figsize=(10, 6))
                    plt.plot(years, counts, marker='o', linewidth=2)
                    plt.title(f"{applicant_name}の年間特許出願数", fontsize=16)
                    plt.xlabel("年", fontsize=14)
                    plt.ylabel("特許出願数", fontsize=14)
                    plt.grid(True, linestyle='--', alpha=0.7)
                    plt.tight_layout()
                    
                    # Convert plot to base64 image
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=100)
                    buffer.seek(0)
                    yearly_trend_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    chart_images["yearly_trend"] = yearly_trend_img
                    plt.close()
            
            # 2. Technology distribution (pie chart)
            if summary.get("top_technologies"):
                tech_data = summary.get("top_technologies", [])
                if tech_data:
                    labels = [item["ipc"] for item in tech_data]
                    sizes = [item["count"] for item in tech_data]
                    
                    plt.figure(figsize=(10, 8))
                    plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                            shadow=True, startangle=140)
                    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    plt.title(f"{applicant_name}の技術分野分布", fontsize=16)
                    plt.tight_layout()
                    
                    # Convert plot to base64 image
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=100)
                    buffer.seek(0)
                    tech_dist_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    chart_images["tech_distribution"] = tech_dist_img
                    plt.close()
            
            # 3. Assessment status distribution (bar chart)
            if summary.get("assessment_status"):
                status_data = summary.get("assessment_status", [])
                if status_data:
                    statuses = [item["status"] for item in status_data]
                    counts = [item["count"] for item in status_data]
                    
                    plt.figure(figsize=(12, 6))
                    bars = plt.bar(statuses, counts, color='skyblue')
                    plt.title(f"{applicant_name}の特許審査状況", fontsize=16)
                    plt.xlabel("審査状況", fontsize=14)
                    plt.ylabel("特許数", fontsize=14)
                    plt.grid(True, linestyle='--', alpha=0.3, axis='y')
                    
                    # Add count labels on top of each bar
                    for bar in bars:
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{int(height)}',
                                ha='center', va='bottom')
                    
                    plt.tight_layout()
                    
                    # Convert plot to base64 image
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=100)
                    buffer.seek(0)
                    assessment_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    chart_images["assessment_distribution"] = assessment_img
                    plt.close()
            
            # Prepare the report data
            yearly_trend = {
                "chart_type": "line",
                "title": f"{applicant_name}の年間特許出願数",
                "x_axis": "年",
                "y_axis": "特許出願数",
                "data": summary.get("yearly_stats", []),
                "image": chart_images.get("yearly_trend")
            }
            
            tech_distribution = {
                "chart_type": "pie",
                "title": f"{applicant_name}の技術分野分布",
                "data": summary.get("top_technologies", []),
                "image": chart_images.get("tech_distribution")
            }
            
            assessment_distribution = {
                "chart_type": "bar",
                "title": f"{applicant_name}の特許審査状況",
                "x_axis": "審査状況",
                "y_axis": "特許数",
                "data": summary.get("assessment_status", []),
                "image": chart_images.get("assessment_distribution")
            }
            
            # Return the visualization data with chart images
            return {
                "success": True,
                "applicant_name": applicant_name,
                "total_patents": summary.get("total_patents"),
                "charts": {
                    "yearly_trend": yearly_trend,
                    "tech_distribution": tech_distribution,
                    "assessment_distribution": assessment_distribution
                },
                "recent_patents": summary.get("recent_patents", [])
            }
        
        except Exception as e:
            error_msg = f"Error generating visual report: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _analyze_assessment_ratios(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patent assessment ratios for the specified applicant
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            Assessment ratio analysis
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        try:
            # Get patents by this applicant
            applicant_patents = self._get_patents_by_applicant({"applicant_name": applicant_name})
            
            if "error" in applicant_patents:
                return applicant_patents
            
            if not applicant_patents.get("success") or applicant_patents.get("count", 0) == 0:
                return {
                    "success": False,
                    "message": f"No patents found for applicant: {applicant_name}"
                }
            
            patents = applicant_patents.get("patents", [])
            
            # Calculate assessment ratios
            assessment_counts = Counter()
            total_analyzed = 0
            
            # 特許成立, 拒絶, 審査中 などのステータスをカウント
            for patent in patents:
                if "審査状況" in patent and patent["審査状況"]:
                    assessment_counts[patent["審査状況"]] += 1
                    total_analyzed += 1
            
            # Calculate approval ratio and other metrics
            # Get assessment status counts
            approval_count = assessment_counts.get("特許成立", 0)
            rejection_count = assessment_counts.get("拒絶", 0)
            pending_count = assessment_counts.get("審査中", 0)
            
            # Calculate ratios
            approval_ratio = (approval_count / total_analyzed * 100) if total_analyzed > 0 else 0
            rejection_ratio = (rejection_count / total_analyzed * 100) if total_analyzed > 0 else 0
            pending_ratio = (pending_count / total_analyzed * 100) if total_analyzed > 0 else 0
            
            # Calculate industry average (mock data for demonstration)
            # In a real implementation, you would query this from a database
            industry_approval_ratio = 65  # Mock data
            
            # Calculate time-to-approval metrics
            approval_times = []
            for patent in patents:
                if "審査状況" in patent and patent["審査状況"] == "特許成立":
                    if "出願日" in patent and "特許登録日" in patent:
                        try:
                            application_date = datetime.strptime(patent["出願日"], "%Y-%m-%d")
                            approval_date = datetime.strptime(patent["特許登録日"], "%Y-%m-%d")
                            days_to_approval = (approval_date - application_date).days
                            approval_times.append(days_to_approval)
                        except (ValueError, TypeError):
                            continue
            
            avg_approval_time = sum(approval_times) / len(approval_times) if approval_times else None
            
            # Get assessment status by technology field
            assessment_by_tech = defaultdict(lambda: defaultdict(int))
            for patent in patents:
                if "審査状況" in patent and "国際特許分類_IPC_" in patent:
                    status = patent["審査状況"]
                    ipc = patent["国際特許分類_IPC_"].split()[0] if patent["国際特許分類_IPC_"].split() else ""
                    if ipc:
                        assessment_by_tech[ipc][status] += 1
            
            # Convert to list format for output
            tech_assessment = []
            for ipc, statuses in assessment_by_tech.items():
                tech_assessment.append({
                    "ipc": ipc,
                    "statuses": [{"status": s, "count": c} for s, c in statuses.items()]
                })
            
            # Sort by total count
            tech_assessment.sort(key=lambda x: sum(item["count"] for item in x["statuses"]), reverse=True)
            
            return {
                "success": True,
                "applicant_name": applicant_name,
                "total_patents": applicant_patents.get("count", 0),
                "total_analyzed": total_analyzed,
                "approval_stats": {
                    "approved": approval_count,
                    "rejected": rejection_count,
                    "pending": pending_count,
                    "approval_ratio": round(approval_ratio, 2),
                    "rejection_ratio": round(rejection_ratio, 2),
                    "pending_ratio": round(pending_ratio, 2),
                },
                "industry_comparison": {
                    "applicant_approval_ratio": round(approval_ratio, 2),
                    "industry_avg_approval_ratio": industry_approval_ratio,
                    "difference": round(approval_ratio - industry_approval_ratio, 2)
                },
                "approval_time": {
                    "average_days": avg_approval_time,
                    "sample_size": len(approval_times)
                },
                "assessment_by_technology": tech_assessment[:5]  # Top 5 tech fields
            }
        
        except Exception as e:
            error_msg = f"Error analyzing assessment ratios: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _analyze_technical_fields(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze technical field distribution for the specified applicant
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            Technical field distribution analysis
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        try:
            # Get patents by this applicant
            applicant_patents = self._get_patents_by_applicant({"applicant_name": applicant_name})
            
            if "error" in applicant_patents:
                return applicant_patents
            
            if not applicant_patents.get("success") or applicant_patents.get("count", 0) == 0:
                return {
                    "success": False,
                    "message": f"No patents found for applicant: {applicant_name}"
                }
            
            patents = applicant_patents.get("patents", [])
            
            # Analyze IPC codes
            ipc_sections = Counter()  # e.g., A, B, C...
            ipc_classes = Counter()   # e.g., A01, B60...
            ipc_subclasses = Counter()  # e.g., A01B, B60R...
            
            for patent in patents:
                if "国際特許分類_IPC_" in patent and patent["国際特許分類_IPC_"]:
                    ipc_code = patent["国際特許分類_IPC_"]
                    
                    # Parse IPC code
                    pattern = re.compile(r'^([A-H])(\d{2})([A-Z])')
                    match = pattern.match(ipc_code)
                    
                    if match:
                        section = match.group(1)  # e.g., "G"
                        class_num = match.group(2)  # e.g., "06"
                        subclass = match.group(3)  # e.g., "F"
                        
                        ipc_sections[section] += 1
                        ipc_classes[f"{section}{class_num}"] += 1
                        ipc_subclasses[f"{section}{class_num}{subclass}"] += 1
            
            # Get IPC section descriptions
            ipc_descriptions = {
                "A": "人間の必需品",
                "B": "処理操作、運輸",
                "C": "化学、冶金",
                "D": "繊維、紙",
                "E": "固定構造物",
                "F": "機械工学、照明、加熱、武器、爆破",
                "G": "物理学",
                "H": "電気"
            }
            
            # Prepare results for different hierarchy levels
            section_results = [
                {"section": section, "count": count, "description": ipc_descriptions.get(section, "不明")}
                for section, count in ipc_sections.most_common()
            ]
            
            class_results = [
                {"class": class_code, "count": count}
                for class_code, count in ipc_classes.most_common(10)
            ]
            
            subclass_results = [
                {"subclass": subclass_code, "count": count}
                for subclass_code, count in ipc_subclasses.most_common(10)
            ]
            
            # Calculate distribution percentages
            total_patents = sum(ipc_sections.values())
            
            if total_patents > 0:
                for item in section_results:
                    item["percentage"] = round((item["count"] / total_patents) * 100, 2)
            
            # Get top technical fields over time
            tech_trends = defaultdict(lambda: defaultdict(int))
            
            for patent in patents:
                if "出願日" in patent and "国際特許分類_IPC_" in patent and patent["出願日"] and patent["国際特許分類_IPC_"]:
                    try:
                        year = patent["出願日"].split('-')[0]
                        ipc_code = patent["国際特許分類_IPC_"]
                        
                        match = pattern.match(ipc_code)
                        if match:
                            section = match.group(1)
                            tech_trends[year][section] += 1
                    except (IndexError, ValueError):
                        continue
            
            # Format trend data
            trend_data = []
            for year, techs in sorted(tech_trends.items()):
                year_data = {"year": year}
                for section in "ABCDEFGH":
                    year_data[section] = techs.get(section, 0)
                trend_data.append(year_data)
            
            return {
                "success": True,
                "applicant_name": applicant_name,
                "total_patents": applicant_patents.get("count", 0),
                "sections": {
                    "total": total_patents,
                    "data": section_results
                },
                "classes": {
                    "total": sum(ipc_classes.values()),
                    "data": class_results
                },
                "subclasses": {
                    "total": sum(ipc_subclasses.values()),
                    "data": subclass_results
                },
                "trend_data": trend_data
            }
        
        except Exception as e:
            error_msg = f"Error analyzing technical fields: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _compare_with_competitors(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare the specified applicant with competitors
        
        Args:
            arguments: Arguments containing applicant_name and optionally num_competitors
            
        Returns:
            Comparison analysis between the applicant and competitors
        """
        applicant_name = arguments.get("applicant_name")
        num_competitors = int(arguments.get("num_competitors", 3))
        
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        # Limit number of competitors to reasonable range
        num_competitors = max(1, min(num_competitors, 10))
        
        try:
            # Get the main applicant's patents
            main_applicant_data = self._get_applicant_summary({"applicant_name": applicant_name})
            
            if "error" in main_applicant_data:
                return main_applicant_data
            
            if not main_applicant_data.get("success"):
                return {
                    "success": False,
                    "message": f"No data found for applicant: {applicant_name}"
                }
            
            # Find potential competitors based on technology overlap
            # Identify the main applicant's technology areas
            top_technologies = main_applicant_data.get("top_technologies", [])
            
            if not top_technologies:
                return {
                    "success": False,
                    "message": f"No technology data available for {applicant_name}"
                }
            
            # Get top IPC codes for this applicant
            ipc_codes = [tech["ipc"] for tech in top_technologies[:3]]
            
            # Find other applicants in the same technology areas
            competitors = []
            
            for ipc_code in ipc_codes:
                # SQL query to find other applicants in this technology area
                query = f"""
                    SELECT 出願人, COUNT(*) as count
                    FROM inpit_data
                    WHERE 国際特許分類_IPC_ LIKE '{ipc_code}%'
                    AND 出願人 != '{applicant_name}'
                    GROUP BY 出願人
                    ORDER BY count DESC
                    LIMIT 10
                """
                
                result = self._execute_sql_query({"query": query})
                
                if result.get("success") and result.get("results"):
                    for row in result.get("results", []):
                        competitor_name = row.get("出願人")
                        patent_count = row.get("count")
                        
                        if competitor_name and patent_count:
                            # Check if already in our list
                            existing = next((c for c in competitors if c["name"] == competitor_name), None)
                            
                            if existing:
                                # Update existing competitor's data
                                existing["relevance"] += 1  # Increment relevance for each shared tech area
                            else:
                                # Add new competitor
                                competitors.append({
                                    "name": competitor_name,
                                    "patent_count": patent_count,
                                    "relevance": 1  # Initial relevance score
                                })
            
            # Sort by relevance and take top N
            competitors.sort(key=lambda x: (x["relevance"], x["patent_count"]), reverse=True)
            competitors = competitors[:num_competitors]
            
            # Get detailed data for each competitor
            competitor_details = []
            
            for competitor in competitors:
                try:
                    competitor_summary = self._get_applicant_summary({"applicant_name": competitor["name"]})
                    
                    if competitor_summary.get("success"):
                        competitor_details.append({
                            "name": competitor["name"],
                            "total_patents": competitor_summary.get("total_patents"),
                            "top_technologies": competitor_summary.get("top_technologies", [])[:3],
                            "yearly_stats": competitor_summary.get("yearly_stats", [])[-5:] if competitor_summary.get("yearly_stats") else []
                        })
                except Exception as e:
                    logger.error(f"Error getting data for competitor {competitor['name']}: {str(e)}")
                    continue
            
            # Prepare comparison data
            # 1. Patent counts over time
            all_years = set()
            
            # Add main applicant's years
            for stat in main_applicant_data.get("yearly_stats", []):
                if "year" in stat:
                    all_years.add(stat["year"])
            
            # Add competitors' years
            for competitor in competitor_details:
                for stat in competitor.get("yearly_stats", []):
                    if "year" in stat:
                        all_years.add(stat["year"])
            
            # Create yearly comparison data
            years_list = sorted(all_years)
            yearly_comparison = []
            
            for year in years_list:
                year_data = {"year": year}
                
                # Add main applicant
                main_year_stat = next((s for s in main_applicant_data.get("yearly_stats", []) if s.get("year") == year), None)
                year_data[applicant_name] = main_year_stat.get("count", 0) if main_year_stat else 0
                
                # Add competitors
                for competitor in competitor_details:
                    comp_year_stat = next((s for s in competitor.get("yearly_stats", []) if s.get("year") == year), None)
                    year_data[competitor["name"]] = comp_year_stat.get("count", 0) if comp_year_stat else 0
                
                yearly_comparison.append(year_data)
            
            # 2. Technology overlap
            overlap_data = []
            main_technologies = {tech["ipc"]: tech["count"] for tech in main_applicant_data.get("top_technologies", [])}
            
            for competitor in competitor_details:
                comp_name = competitor["name"]
                comp_technologies = {tech["ipc"]: tech["count"] for tech in competitor.get("top_technologies", [])}
                
                # Find shared technologies
                shared_techs = []
                for tech, count in main_technologies.items():
                    if tech in comp_technologies:
                        shared_techs.append({
                            "ipc": tech,
                            "main_count": count,
                            "competitor_count": comp_technologies[tech]
                        })
                
                overlap_data.append({
                    "competitor_name": comp_name,
                    "shared_technologies": shared_techs,
                    "overlap_score": len(shared_techs)
                })
            
            return {
                "success": True,
                "main_applicant": {
                    "name": applicant_name,
                    "total_patents": main_applicant_data.get("total_patents"),
                    "top_technologies": main_applicant_data.get("top_technologies", [])[:3]
                },
                "competitors": competitor_details,
                "comparisons": {
                    "yearly_patent_counts": yearly_comparison,
                    "technology_overlap": overlap_data
                }
            }
        
        except Exception as e:
            error_msg = f"Error comparing with competitors: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _generate_pdf_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a PDF report for the specified applicant
        
        Args:
            arguments: Arguments containing applicant_name
            
        Returns:
            PDF report data in base64 format
        """
        applicant_name = arguments.get("applicant_name")
        if not applicant_name:
            return {"error": "applicant_name is required"}
        
        try:
            # Get comprehensive data for the report
            summary_data = self._get_applicant_summary({"applicant_name": applicant_name})
            technical_data = self._analyze_technical_fields({"applicant_name": applicant_name})
            assessment_data = self._analyze_assessment_ratios({"applicant_name": applicant_name})
            competitor_data = self._compare_with_competitors({
                "applicant_name": applicant_name,
                "num_competitors": 3
            })
            
            # Check if all data retrieval was successful
            if not all(data.get("success", False) for data in [summary_data, technical_data, assessment_data, competitor_data]):
                missing_data = []
                if not summary_data.get("success", False):
                    missing_data.append("サマリーデータ")
                if not technical_data.get("success", False):
                    missing_data.append("技術分野データ")
                if not assessment_data.get("success", False):
                    missing_data.append("審査状況データ")
                if not competitor_data.get("success", False):
                    missing_data.append("競合他社データ")
                
                return {
                    "success": False,
                    "message": f"レポート生成に必要なデータが不足しています: {', '.join(missing_data)}"
                }
            
            # Generate report content in Markdown format
            current_date = datetime.now().strftime("%Y年%m月%d日")
            
            report_md = f"""
# {applicant_name} 特許分析レポート

**生成日:** {current_date}

## 1. 出願人概要

- **総特許出願数:** {summary_data.get("total_patents", 0)}
- **主要技術分野:** {", ".join([f"{t['ipc']}" for t in summary_data.get("top_technologies", [])][:3])}

### 1.1 年間出願数の推移

| 年 | 出願数 |
|-------|--------|
"""
            
            # Add yearly stats table
            for stat in summary_data.get("yearly_stats", []):
                report_md += f"| {stat.get('year', 'N/A')} | {stat.get('count', 0)} |\n"
            
            report_md += """
## 2. 技術分野分析

### 2.1 IPCセクション分布
"""
            
            # Add technical field distribution
            if "sections" in technical_data and "data" in technical_data["sections"]:
                for section in technical_data["sections"]["data"]:
                    report_md += f"- **{section.get('section')}:** {section.get('description')} - {section.get('count')}件 ({section.get('percentage', 0)}%)\n"
            
            report_md += """
### 2.2 主要技術サブクラス (TOP 5)

| サブクラス | 特許数 |
|----------|-------|
"""
            
            # Add subclass table
            if "subclasses" in technical_data and "data" in technical_data["subclasses"]:
                for subclass in technical_data["subclasses"]["data"][:5]:
                    report_md += f"| {subclass.get('subclass', 'N/A')} | {subclass.get('count', 0)} |\n"
            
            report_md += """
## 3. 審査状況分析

### 3.1 審査状況の概要
"""
            
            # Add assessment ratios
            if "approval_stats" in assessment_data:
                approval_stats = assessment_data["approval_stats"]
                report_md += f"""
- **特許成立:** {approval_stats.get('approved', 0)}件 ({approval_stats.get('approval_ratio', 0)}%)
- **拒絶:** {approval_stats.get('rejected', 0)}件 ({approval_stats.get('rejection_ratio', 0)}%)
- **審査中:** {approval_stats.get('pending', 0)}件 ({approval_stats.get('pending_ratio', 0)}%)
"""
            
            # Add industry comparison
            if "industry_comparison" in assessment_data:
                comp = assessment_data["industry_comparison"]
                report_md += f"""
### 3.2 業界平均との比較

- **{applicant_name}の特許成立率:** {comp.get('applicant_approval_ratio', 0)}%
- **業界平均特許成立率:** {comp.get('industry_avg_approval_ratio', 0)}%
- **差異:** {comp.get('difference', 0)}%
"""
            
            report_md += """
## 4. 競合他社分析

### 4.1 主要競合他社
"""
            
            # Add competitor information
            if "competitors" in competitor_data:
                for idx, competitor in enumerate(competitor_data["competitors"]):
                    report_md += f"""
#### 4.1.{idx+1} {competitor.get('name')}

- **総特許出願数:** {competitor.get('total_patents', 0)}
- **主要技術分野:** {", ".join([f"{t['ipc']}" for t in competitor.get("top_technologies", [])][:3])}
"""
            
            report_md += """
### 4.2 技術分野の重複

| 競合他社 | 重複技術分野数 |
|---------|------------|
"""
            
            # Add technology overlap
            if "comparisons" in competitor_data and "technology_overlap" in competitor_data["comparisons"]:
                for overlap in competitor_data["comparisons"]["technology_overlap"]:
                    report_md += f"| {overlap.get('competitor_name', 'N/A')} | {overlap.get('overlap_score', 0)} |\n"
            
            report_md += """
## 5. 結論と推奨事項

### 5.1 主要なインサイト

- この企業の特許ポートフォリオは...
- 技術トレンドとしては...
- 競合他社と比較して...

### 5.2 推奨されるアクション

1. ...
2. ...
3. ...

---

*このレポートは自動生成されたものです。詳細な分析には専門家の判断が必要です。*
"""
            
            # Generate visual charts for the PDF report
            visual_report = self._generate_visual_report({"applicant_name": applicant_name})
            
            # Create the PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set font for Japanese text
            pdf.add_font('IPAGothic', '', '')  # Use default font for better compatibility
            pdf.set_font('Arial', 'B', 16)
            
            # Title
            pdf.cell(190, 10, f"{applicant_name} 特許分析レポート", 0, 1, 'C')
            pdf.ln(10)
            
            # Basic information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "1. 出願人概要", 0, 1, 'L')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(60, 10, f"総特許出願数: {summary_data.get('total_patents', 0)}", 0, 1, 'L')
            
            # If we have chart images from visual report, add them
            if visual_report and visual_report.get("success") and "charts" in visual_report:
                charts = visual_report.get("charts", {})
                
                # Add yearly trend chart if available
                if "yearly_trend" in charts and charts["yearly_trend"].get("image"):
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(190, 10, "年間特許出願数の推移", 0, 1, 'C')
                    
                    # Decode and add the image
                    try:
                        trend_image_data = base64.b64decode(charts["yearly_trend"]["image"])
                        temp_img_path = "/tmp/yearly_trend.png"
                        with open(temp_img_path, 'wb') as f:
                            f.write(trend_image_data)
                        
                        pdf.image(temp_img_path, x=10, y=40, w=180)
                        os.remove(temp_img_path)  # Clean up
                    except Exception as e:
                        logger.error(f"Error adding trend chart to PDF: {e}")
                
                # Add technology distribution chart if available
                if "tech_distribution" in charts and charts["tech_distribution"].get("image"):
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(190, 10, "技術分野分布", 0, 1, 'C')
                    
                    # Decode and add the image
                    try:
                        tech_image_data = base64.b64decode(charts["tech_distribution"]["image"])
                        temp_img_path = "/tmp/tech_dist.png"
                        with open(temp_img_path, 'wb') as f:
                            f.write(tech_image_data)
                        
                        pdf.image(temp_img_path, x=10, y=40, w=180)
                        os.remove(temp_img_path)  # Clean up
                    except Exception as e:
                        logger.error(f"Error adding tech distribution chart to PDF: {e}")
                
                # Add assessment distribution chart if available
                if "assessment_distribution" in charts and charts["assessment_distribution"].get("image"):
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(190, 10, "特許審査状況", 0, 1, 'C')
                    
                    # Decode and add the image
                    try:
                        assessment_image_data = base64.b64decode(charts["assessment_distribution"]["image"])
                        temp_img_path = "/tmp/assessment_dist.png"
                        with open(temp_img_path, 'wb') as f:
                            f.write(assessment_image_data)
                        
                        pdf.image(temp_img_path, x=10, y=40, w=180)
                        os.remove(temp_img_path)  # Clean up
                    except Exception as e:
                        logger.error(f"Error adding assessment chart to PDF: {e}")
            
            # Add final page with report date
            pdf.add_page()
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f"レポート生成日: {current_date}", 0, 1, 'C')
            pdf.cell(0, 10, "このレポートは自動生成されたものです。詳細な分析には専門家の判断が必要です。", 0, 1, 'C')
            
            # Convert PDF to bytes and encode to base64
            pdf_bytes = pdf.output(dest='S').encode('latin1')  # FPDF outputs a string, need to encode to bytes
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Return both the PDF and markdown formats
            return {
                "success": True,
                "applicant_name": applicant_name,
                "formats": {
                    "pdf": {
                        "content_type": "application/pdf",
                        "data": pdf_base64
                    },
                    "markdown": {
                        "content_type": "text/markdown",
                        "data": report_md
                    }
                }
            }
        
        except Exception as e:
            error_msg = f"Error generating PDF report: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_ipc_classifications(self) -> Dict[str, Any]:
        """
        Get descriptions for IPC (International Patent Classification) codes
        
        Returns:
            Dictionary with IPC codes and descriptions
        """
        # This is a simplified version with common IPC sections and classes
        ipc_descriptions = {
            # Sections
            "A": "人間の必需品",
            "B": "処理操作、運輸",
            "C": "化学、冶金",
            "D": "繊維、紙",
            "E": "固定構造物",
            "F": "機械工学、照明、加熱、武器、爆破",
            "G": "物理学",
            "H": "電気",
            
            # Common classes and subclasses
            "A61": "医学または獣医学；衛生学",
            "A61K": "医薬用、歯科用または化粧用製剤",
            "B60": "車両一般",
            "C07": "有機化学",
            "C12": "生化学；ビール；酒精；ぶどう酒；酢；微生物学；酵素学；突然変異または遺伝子工学",
            "G01": "測定；試験",
            "G06": "計算；計数",
            "G06F": "電気的デジタルデータ処理",
            "G06Q": "管理目的、商業目的、金融目的、経営目的、監督目的または予測目的に特に適合したデータ処理システム／方法",
            "H01": "基本的電気素子",
            "H04": "電気通信技術",
            "H04L": "デジタル情報の伝送",
            "H04N": "画像通信"
        }
        
        return {
            "ipc_codes": [
                {"code": code, "description": desc}
                for code, desc in ipc_descriptions.items()
            ],
            "sections": [
                {"code": code, "description": desc}
                for code, desc in ipc_descriptions.items()
                if len(code) == 1  # sections are single characters
            ]
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
