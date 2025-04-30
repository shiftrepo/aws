#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module provides the InpitDataAccess class for direct interaction
with the Inpit SQLite API, without importing data to a local database.
"""

import logging
from typing import Dict, List, Any, Optional

from app.patent_system.inpit_sqlite_connector import get_connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InpitDataAccess:
    """Class for accessing patent data directly from Inpit SQLite API"""

    def __init__(self, api_url: str = "http://localhost:5001"):
        """
        Initialize the data access object

        Args:
            api_url: URL for the Inpit SQLite API
        """
        self.connector = get_connector(api_url)
        logger.info(f"Initialized Inpit SQLite data access with URL: {api_url}")

    def get_patent_by_application_number(self, application_number: str) -> Dict[str, Any]:
        """
        Get patent data by application number

        Args:
            application_number: The application number to retrieve

        Returns:
            Dictionary with patent data in standardized format
        """
        logger.info(f"Retrieving patent by application number: {application_number}")

        try:
            # Get data from Inpit SQLite
            result = self.connector.get_patent_by_application_number(application_number)

            if "error" in result:
                logger.error(f"Error retrieving patent: {result['error']}")
                return {"error": result['error'], "patents": []}

            # Map to patent model format
            patents = self.connector.map_to_patent_model(result)

            if not patents:
                logger.info(f"No patent found with application number: {application_number}")
                return {"patents": []}

            logger.info(f"Successfully retrieved {len(patents)} patent(s)")
            return {"patents": patents}

        except Exception as e:
            logger.error(f"Error retrieving patent by application number: {str(e)}")
            return {"error": str(e), "patents": []}

    def get_patents_by_applicant(self, applicant_name: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get patents by applicant name

        Args:
            applicant_name: Name of the applicant
            limit: Maximum number of patents to retrieve

        Returns:
            Dictionary with patent data in standardized format
        """
        logger.info(f"Retrieving patents by applicant name: {applicant_name}")

        try:
            # Get data from Inpit SQLite
            result = self.connector.get_patents_by_applicant(applicant_name)

            if "error" in result:
                logger.error(f"Error retrieving patents: {result['error']}")
                return {"error": result['error'], "patents": []}

            # Map to patent model format
            patents = self.connector.map_to_patent_model(result)

            if not patents:
                logger.info(f"No patents found for applicant: {applicant_name}")
                return {"patents": []}

            # Limit the number of patents to return
            patents_to_return = patents[:limit]

            logger.info(f"Successfully retrieved {len(patents_to_return)} patents for applicant: {applicant_name}")
            return {"patents": patents_to_return}

        except Exception as e:
            logger.error(f"Error retrieving patents by applicant: {str(e)}")
            return {"error": str(e), "patents": []}

    def execute_sql_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute a custom SQL query against Inpit SQLite

        Args:
            query: SQL query to execute
            limit: Maximum number of results to map to patent format

        Returns:
            Dictionary with query results or mapped patents
        """
        logger.info(f"Executing SQL query")
        logger.debug(f"Query: {query}")

        try:
            # Execute SQL query via Inpit SQLite API
            result = self.connector.execute_sql_query(query)

            if "error" in result:
                logger.error(f"Error executing SQL query: {result['error']}")
                return {"error": result['error'], "results": []}

            # Return raw results if not mapping to patent models
            if not query.lower().strip().startswith("select * from"):
                logger.info(f"Returning raw SQL query results")
                return result

            # Try mapping to patent model format for more comprehensive queries
            try:
                patents = self.connector.map_to_patent_model(result)
                if patents:
                    logger.info(f"Query results mapped to {len(patents)} patent models")
                    return {"patents": patents[:limit], "raw_results": result}
            except Exception as mapping_error:
                logger.warning(f"Could not map query results to patent models: {str(mapping_error)}")

            # Return raw results if mapping fails
            logger.info(f"Returning raw SQL query results")
            return result

        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            return {"error": str(e), "results": []}

    def get_api_status(self) -> Dict[str, Any]:
        """
        Get Inpit SQLite API status and database information
        
        Returns:
            Dictionary with API status information
        """
        return self.connector.get_api_status()


# Create a singleton instance for easy import
data_access = InpitDataAccess()

def get_data_access(api_url=None):
    """Get the data access instance, optionally with a new API URL"""
    global data_access
    if api_url:
        data_access = InpitDataAccess(api_url)
    return data_access


if __name__ == "__main__":
    # Get API status when run directly
    access = InpitDataAccess()
    status = access.get_api_status()
    
    if "error" in status:
        print(f"Error connecting to Inpit SQLite API: {status['error']}")
    else:
        record_count = status.get("record_count", 0) if "record_count" in status else "unknown"
        print(f"Successfully connected to Inpit SQLite API")
        print(f"Database contains {record_count} records")
        print(f"API URL: {access.connector.api_url}")
