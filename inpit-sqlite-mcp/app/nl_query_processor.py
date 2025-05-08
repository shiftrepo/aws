#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Natural Language Query Processor for Patent Data

This module provides functionality to process natural language queries against patent data,
converting them to SQL queries that can be executed against the SQLite database.
"""

import re
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentNLQueryProcessor:
    """
    Process natural language queries for patent data and convert them to SQL queries
    """
    
    def __init__(self, db_path: str = "/app/data/google_patents_gcp.db"):
        """
        Initialize the natural language query processor
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.table_map = {
            "publications": self._get_table_info("publications"),
            "patent_families": self._get_table_info("patent_families")
        }
    
    def _get_table_info(self, table_name: str) -> Dict[str, str]:
        """
        Get information about the specified table
        
        Args:
            table_name: Name of the table to get information about
            
        Returns:
            Dictionary of column names and types
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {}
            for row in cursor.fetchall():
                col_name = row[1]
                col_type = row[2]
                columns[col_name] = col_type
            
            conn.close()
            return columns
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {}
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a natural language query and convert it to SQL
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Dictionary containing the SQL query and metadata
        """
        try:
            # Normalize query
            query_text = query_text.strip().lower()
            
            # Extract key entities and conditions from the query
            conditions, limit = self._extract_conditions(query_text)
            
            # Determine which table to query
            table = "publications"
            if "family" in query_text or "related" in query_text:
                join_clause = "JOIN patent_families f ON p.family_id = f.family_id"
            else:
                join_clause = ""
            
            # Build SQL query
            sql_query = f"SELECT * FROM {table} p"
            
            # Add join if needed
            if join_clause:
                sql_query += f" {join_clause}"
            
            # Add WHERE clause if there are conditions
            if conditions:
                sql_query += " WHERE " + " AND ".join(conditions)
            
            # Add ORDER BY
            if "new" in query_text or "latest" in query_text or "recent" in query_text:
                sql_query += " ORDER BY p.publication_date DESC"
            elif "old" in query_text or "earliest" in query_text:
                sql_query += " ORDER BY p.publication_date ASC"
            else:
                sql_query += " ORDER BY p.publication_date DESC"
            
            # Add LIMIT
            sql_query += f" LIMIT {limit}"
            
            return {
                "natural_language_query": query_text,
                "sql_query": sql_query,
                "conditions": conditions,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": str(e),
                "natural_language_query": query_text,
                "sql_query": None
            }
    
    def _extract_conditions(self, query_text: str) -> Tuple[List[str], int]:
        """
        Extract SQL conditions from natural language query
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Tuple of (list of SQL conditions, limit)
        """
        conditions = []
        limit = 10  # Default limit
        
        # Extract year references
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, query_text)
        if years:
            year_conditions = []
            for year in years:
                if "before" in query_text and year in query_text.split("before")[1]:
                    year_conditions.append(f"strftime('%Y', p.publication_date) < '{year}'")
                elif "after" in query_text and year in query_text.split("after")[1]:
                    year_conditions.append(f"strftime('%Y', p.publication_date) > '{year}'")
                else:
                    year_conditions.append(f"strftime('%Y', p.publication_date) = '{year}'")
            if year_conditions:
                conditions.append("(" + " OR ".join(year_conditions) + ")")
        
        # Extract applicant/assignee
        company_keywords = ["company", "corporation", "inc", "co", "ltd", "株式会社", "k.k.", "gmbh"]
        words = query_text.split()
        for i, word in enumerate(words):
            if word in ["by", "from", "of"]:
                # Look for company names after these prepositions
                if i + 1 < len(words):
                    potential_company = words[i + 1]
                    # Check if the next word might be a company
                    if any(kw in potential_company for kw in company_keywords) or len(potential_company) > 3:
                        conditions.append(f"p.assignee_harmonized LIKE '%{potential_company}%'")
        
        # Check for specific companies or inventors
        if "sony" in query_text:
            conditions.append("p.assignee_harmonized LIKE '%sony%'")
        if "toyota" in query_text:
            conditions.append("p.assignee_harmonized LIKE '%toyota%'")
        if "honda" in query_text:
            conditions.append("p.assignee_harmonized LIKE '%honda%'")
        if "toshiba" in query_text:
            conditions.append("p.assignee_harmonized LIKE '%toshiba%'")
        if "canon" in query_text:
            conditions.append("p.assignee_harmonized LIKE '%canon%'")
        
        # Extract technology fields by keywords
        if "camera" in query_text or "imaging" in query_text:
            conditions.append("(p.title_ja LIKE '%カメラ%' OR p.title_en LIKE '%camera%' OR p.abstract_ja LIKE '%カメラ%' OR p.abstract_en LIKE '%camera%')")
        if "vehicle" in query_text or "car" in query_text or "automotive" in query_text:
            conditions.append("(p.title_ja LIKE '%車%' OR p.title_en LIKE '%vehicle%' OR p.abstract_ja LIKE '%車%' OR p.abstract_en LIKE '%vehicle%')")
        if "semiconductor" in query_text:
            conditions.append("(p.title_ja LIKE '%半導体%' OR p.title_en LIKE '%semiconductor%' OR p.abstract_ja LIKE '%半導体%' OR p.abstract_en LIKE '%semiconductor%')")
        if "battery" in query_text or "電池" in query_text:
            conditions.append("(p.title_ja LIKE '%電池%' OR p.title_en LIKE '%battery%' OR p.abstract_ja LIKE '%電池%' OR p.abstract_en LIKE '%battery%')")
        if "display" in query_text or "画面" in query_text:
            conditions.append("(p.title_ja LIKE '%画面%' OR p.title_en LIKE '%display%' OR p.abstract_ja LIKE '%画面%' OR p.abstract_en LIKE '%display%')")
        
        # Check for IPC code patterns (e.g., "G06F" or "G 06 F")
        ipc_pattern = r'[A-H]\d{2}[A-Z]'
        ipc_codes = re.findall(ipc_pattern, query_text.upper())
        if ipc_codes:
            ipc_conditions = []
            for ipc in ipc_codes:
                ipc_conditions.append(f"p.ipc_code LIKE '%{ipc}%'")
            if ipc_conditions:
                conditions.append("(" + " OR ".join(ipc_conditions) + ")")
        
        # Extract text search terms for title/abstract
        search_term_pattern = r'"([^"]+)"'
        search_terms = re.findall(search_term_pattern, query_text)
        
        if not search_terms and "about" in query_text:
            parts = query_text.split("about")
            if len(parts) > 1:
                about_text = parts[1].strip()
                # Take words until next clear separator
                separators = [" and ", " or ", " with ", " from ", " to ", " by "]
                for sep in separators:
                    if sep in about_text:
                        about_text = about_text.split(sep)[0].strip()
                if about_text:
                    search_terms.append(about_text)
        
        # Handle "related to" pattern
        if "related to" in query_text:
            parts = query_text.split("related to")
            if len(parts) > 1:
                related_text = parts[1].strip()
                # Take words until next clear separator
                separators = [" and ", " or ", " with ", " from ", " to ", " by "]
                for sep in separators:
                    if sep in related_text:
                        related_text = related_text.split(sep)[0].strip()
                if related_text:
                    search_terms.append(related_text)
        
        for term in search_terms:
            conditions.append(f"(p.title_ja LIKE '%{term}%' OR p.title_en LIKE '%{term}%' OR p.abstract_ja LIKE '%{term}%' OR p.abstract_en LIKE '%{term}%')")
        
        # Handle family-related queries
        if "family" in query_text:
            family_id_pattern = r'family\s+id\s+(\S+)'
            family_id_match = re.search(family_id_pattern, query_text)
            if family_id_match:
                family_id = family_id_match.group(1)
                conditions.append(f"p.family_id = '{family_id}'")
        
        # Extract limit
        limit_pattern = r'(show|get|return|find|limit)\s+(\d+)'
        limit_match = re.search(limit_pattern, query_text)
        if limit_match:
            try:
                limit = int(limit_match.group(2))
                # Constrain limit to reasonable range
                limit = max(1, min(limit, 100))
            except ValueError:
                pass
        
        return conditions, limit
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute an SQL query against the patent database
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            Query results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return results as dictionaries
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            
            # Convert to list of dicts
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip([column[0] for column in cursor.description], row)))
            
            conn.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": sql_query
            }
    
    def process_and_execute(self, query_text: str) -> Dict[str, Any]:
        """
        Process a natural language query and execute the resulting SQL query
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Query results
        """
        processed = self.process_query(query_text)
        
        if "error" in processed or not processed.get("sql_query"):
            return {
                "success": False,
                "error": processed.get("error", "Failed to process query"),
                "natural_language_query": query_text
            }
        
        sql_query = processed["sql_query"]
        results = self.execute_query(sql_query)
        
        return {
            "success": results.get("success", False),
            "natural_language_query": query_text,
            "sql_query": sql_query,
            "count": results.get("count", 0),
            "results": results.get("results", [])
        }


if __name__ == "__main__":
    # Example usage
    processor = PatentNLQueryProcessor()
    result = processor.process_and_execute("Show me 5 patents about electric vehicles from Toyota")
    print(f"Found {result['count']} results")
    for patent in result['results'][:3]:  # Show first 3 patents
        print(f"{patent.get('title_ja')} - {patent.get('publication_number')}")
