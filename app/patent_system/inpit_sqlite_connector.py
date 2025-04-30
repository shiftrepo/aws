#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inpit SQLite Connector

This module provides functions to interact with the Inpit SQLite MCP server
for retrieving patent data.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InpitSQLiteConnector:
    """
    Connector for interacting with the Inpit SQLite MCP service
    """
    
    def __init__(self, api_url: str = "http://localhost:5001"):
        """Initialize the connector with the API URL"""
        self.api_url = api_url
        logger.info(f"Initialized Inpit SQLite connector with URL: {api_url}")
    
    def get_patent_by_application_number(self, application_number: str) -> Dict[str, Any]:
        """
        Get patent data by application number
        
        Args:
            application_number: Patent application number
            
        Returns:
            Dictionary with patent data or error
        """
        try:
            encoded_app_number = quote(application_number)
            url = f"{self.api_url}/api/application/{encoded_app_number}"
            
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error querying application number: {response.text}")
                return {"error": f"API request failed with status code: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception in get_patent_by_application_number: {str(e)}")
            return {"error": str(e)}
    
    def get_patents_by_applicant(self, applicant_name: str) -> Dict[str, Any]:
        """
        Get patents by applicant name
        
        Args:
            applicant_name: Name of the patent applicant
            
        Returns:
            Dictionary with patent data or error
        """
        try:
            encoded_applicant = quote(applicant_name)
            url = f"{self.api_url}/api/applicant/{encoded_applicant}"
            
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error querying applicant name: {response.text}")
                return {"error": f"API request failed with status code: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception in get_patents_by_applicant: {str(e)}")
            return {"error": str(e)}
    
    def execute_sql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query against the Inpit SQLite database
        
        Args:
            query: SQL query string (must be a SELECT query)
            
        Returns:
            Dictionary with query results or error
        """
        try:
            url = f"{self.api_url}/api/sql-query"
            headers = {'Content-Type': 'application/json'}
            data = {"query": query}
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error executing SQL query: {response.text}")
                return {"error": f"API request failed with status code: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception in execute_sql_query: {str(e)}")
            return {"error": str(e)}
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get API status and database information
        
        Returns:
            Dictionary with API status information
        """
        try:
            url = f"{self.api_url}/api/status"
            
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting API status: {response.text}")
                return {"error": f"API request failed with status code: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception in get_api_status: {str(e)}")
            return {"error": str(e)}
    
    def map_to_patent_model(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Map Inpit SQLite data format to the patent system's model format
        
        Args:
            data: Raw data from Inpit SQLite API
            
        Returns:
            List of dictionaries formatted as patent models
        """
        if not data.get("success") or not data.get("results"):
            return []
        
        columns = data.get("columns", [])
        results = data.get("results", [])
        patents = []
        
        # Find column indexes
        app_num_idx = -1
        app_date_idx = -1
        pub_num_idx = -1
        pub_date_idx = -1
        title_idx = -1
        abstract_idx = -1
        applicants_idx = -1
        inventors_idx = -1
        ipc_idx = -1
        
        for i, col in enumerate(columns):
            col_lower = col.lower()
            if "出願番号" in col or "application" in col_lower and "number" in col_lower:
                app_num_idx = i
            elif "出願日" in col or "application" in col_lower and "date" in col_lower:
                app_date_idx = i
            elif "公開番号" in col or "publication" in col_lower and "number" in col_lower:
                pub_num_idx = i
            elif "公開日" in col or "publication" in col_lower and "date" in col_lower:
                pub_date_idx = i
            elif "発明の名称" in col or "title" in col_lower:
                title_idx = i
            elif "要約" in col or "abstract" in col_lower:
                abstract_idx = i
            elif "出願人" in col or "applicant" in col_lower:
                applicants_idx = i
            elif "発明者" in col or "inventor" in col_lower:
                inventors_idx = i
            elif "ipc" in col_lower or "分類" in col:
                ipc_idx = i
        
        # Process each result row
        for row in results:
            patent_data = {
                "applicationNumber": row[app_num_idx] if app_num_idx >= 0 and app_num_idx < len(row) else None,
                "applicationDate": row[app_date_idx] if app_date_idx >= 0 and app_date_idx < len(row) else None,
                "publicationNumber": row[pub_num_idx] if pub_num_idx >= 0 and pub_num_idx < len(row) else None,
                "publicationDate": row[pub_date_idx] if pub_date_idx >= 0 and pub_date_idx < len(row) else None,
                "title": row[title_idx] if title_idx >= 0 and title_idx < len(row) else None,
                "abstract": row[abstract_idx] if abstract_idx >= 0 and abstract_idx < len(row) else None,
                "applicants": [],
                "inventors": [],
                "ipcClassifications": []
            }
            
            # Process applicants
            if applicants_idx >= 0 and applicants_idx < len(row) and row[applicants_idx]:
                applicant_names = str(row[applicants_idx]).split(";")
                for name in applicant_names:
                    name = name.strip()
                    if name:
                        patent_data["applicants"].append({"name": name, "address": ""})
            
            # Process inventors
            if inventors_idx >= 0 and inventors_idx < len(row) and row[inventors_idx]:
                inventor_names = str(row[inventors_idx]).split(";")
                for name in inventor_names:
                    name = name.strip()
                    if name:
                        patent_data["inventors"].append({"name": name, "address": ""})
            
            # Process IPC classifications
            if ipc_idx >= 0 and ipc_idx < len(row) and row[ipc_idx]:
                ipc_codes = str(row[ipc_idx]).split(";")
                for code in ipc_codes:
                    code = code.strip()
                    if code:
                        patent_data["ipcClassifications"].append({
                            "code": code,
                            "description": ""
                        })
            
            patents.append(patent_data)
        
        return patents


# Create a singleton instance for easy import
connector = InpitSQLiteConnector()

def get_connector(api_url=None):
    """Get the connector instance, optionally with a new API URL"""
    global connector
    if api_url:
        connector = InpitSQLiteConnector(api_url)
    return connector
