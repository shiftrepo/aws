#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Natural Language Query Processor for Inpit Database

This module provides functionality to process natural language queries against the Inpit database,
converting them to SQL queries that can be executed against the SQLite database.
"""

import re
import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InpitNLQueryProcessor:
    """
    Process natural language queries for Inpit patent data and convert them to SQL queries
    """
    
    def __init__(self, db_path: str = "/app/data/inpit.db", 
                 column_mapping_path: str = "/app/data/column_mapping.json"):
        """
        Initialize the natural language query processor for Inpit database
        
        Args:
            db_path: Path to the SQLite database file
            column_mapping_path: Path to column mapping JSON file
        """
        self.db_path = db_path
        self.column_map = self._load_column_mapping(column_mapping_path)
        self.table_info = self._get_table_info("inpit_data")
        
        # Common column names used in natural language queries
        self.common_columns = {
            "出願番号": self._find_column_by_name("application_number", "出願番号"),
            "公開番号": self._find_column_by_name("publication_number", "公開番号"),
            "出願人": self._find_column_by_name("applicant_name", "出願人"),
            "発明者": self._find_column_by_name("inventor_name", "発明者"),
            "タイトル": self._find_column_by_name("title", "タイトル", "発明の名称"),
            "要約": self._find_column_by_name("abstract", "要約"),
            "出願日": self._find_column_by_name("filing_date", "出願日"),
            "公開日": self._find_column_by_name("publication_date", "公開日"),
            "特許番号": self._find_column_by_name("patent_number", "特許番号"),
            "法的状態": self._find_column_by_name("legal_status", "法的状態"),
            "IPC分類": self._find_column_by_name("ipc_code", "IPC", "国際特許分類"),
            "ファミリーID": self._find_column_by_name("family_id", "ファミリーID")
        }
        
        # Used to support variant names in queries
        self.column_synonyms = {
            "会社": "出願人",
            "企業": "出願人",
            "申請者": "出願人",
            "出願者": "出願人",
            "権利者": "出願人",
            "考案者": "発明者",
            "作者": "発明者",
            "題名": "タイトル",
            "件名": "タイトル",
            "表題": "タイトル",
            "公報番号": "公開番号",
            "登録番号": "特許番号",
            "申請日": "出願日",
            "登録日": "公開日",
            "公表日": "公開日",
            "状態": "法的状態",
            "分類": "IPC分類",
            "特許分類": "IPC分類",
            "ファミリー": "ファミリーID"
        }
    
    def _load_column_mapping(self, mapping_path: str) -> Dict[str, str]:
        """
        Load column mapping from JSON file
        
        Args:
            mapping_path: Path to the column mapping JSON file
            
        Returns:
            Dictionary of column mappings
        """
        try:
            if mapping_path:
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load column mapping from {mapping_path}: {e}")
        return {}
    
    def _find_column_by_name(self, *possible_names: str) -> str:
        """
        Find actual column name in database that matches any of the possible names
        
        Args:
            *possible_names: Possible column name variations
            
        Returns:
            Actual column name in database or first possible name as fallback
        """
        # First check if any column exactly matches
        for name in possible_names:
            if name in self.column_map or name in self.column_map.values():
                return name
        
        # Then check for partial matches in column mapping values
        for col_name, col_value in self.column_map.items():
            for possible in possible_names:
                if possible.lower() in col_value.lower():
                    return col_name
        
        # Check existing table columns
        if self.table_info:
            for possible in possible_names:
                if possible in self.table_info:
                    return possible
        
        # Use first name as fallback
        return possible_names[0]
    
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
            query_text = query_text.strip()
            
            # Extract key entities and conditions from the query
            table_name = "inpit_data"
            conditions, limit, order_by = self._extract_conditions(query_text)
            
            # Build SQL query
            sql_query = f"SELECT * FROM {table_name}"
            
            # Add WHERE clause if there are conditions
            if conditions:
                sql_query += " WHERE " + " AND ".join(conditions)
            
            # Add ORDER BY
            if order_by:
                sql_query += f" ORDER BY {order_by}"
            
            # Add LIMIT
            sql_query += f" LIMIT {limit}"
            
            return {
                "natural_language_query": query_text,
                "sql_query": sql_query,
                "conditions": conditions,
                "order_by": order_by,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": str(e),
                "natural_language_query": query_text,
                "sql_query": None
            }
    
    def _extract_conditions(self, query_text: str) -> Tuple[List[str], int, Optional[str]]:
        """
        Extract SQL conditions from natural language query
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Tuple of (list of SQL conditions, limit, order by clause)
        """
        conditions = []
        limit = 10  # Default limit
        order_by = None
        
        # Convert query to lowercase for easier matching but keep original for entity extraction
        query_lower = query_text.lower()
        
        # 1. Extract time/date references
        
        # Extract year references
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, query_text)
        if years:
            year_conditions = []
            
            # Process years with context
            for year in years:
                if "以前" in query_text or "前" in query_text or "より前" in query_text or "before" in query_lower:
                    if any(year in part for part in re.split(r'(以前|前|より前|before)', query_text)):
                        date_col = self.common_columns.get("出願日", "filing_date")
                        year_conditions.append(f"strftime('%Y', {date_col}) <= '{year}'")
                elif "以降" in query_text or "後" in query_text or "より後" in query_text or "after" in query_lower:
                    if any(year in part for part in re.split(r'(以降|後|より後|after)', query_text)):
                        date_col = self.common_columns.get("出願日", "filing_date")
                        year_conditions.append(f"strftime('%Y', {date_col}) >= '{year}'")
                else:
                    date_col = self.common_columns.get("出願日", "filing_date")
                    year_conditions.append(f"strftime('%Y', {date_col}) = '{year}'")
            
            if year_conditions:
                conditions.append("(" + " OR ".join(year_conditions) + ")")
        
        # 2. Extract applicant/company references
        
        # Look for company names
        company_patterns = [
            r'(?:会社|企業|出願人|申請者)(?:は|が|の)「([^」]+)」',  # Company is "XXX"
            r'(?:会社|企業|出願人|申請者)(?:は|が|の)([^\s,。]+)',   # Company is XXX
            r'"([^"]+)"(?:による|から|の)(?:特許|出願)',            # Patents "by XXX"
            r'([^\s,。]+)(?:による|から|の)(?:特許|出願)',          # Patents by XXX
            r'(?:from|by|of)\s+([A-Za-z0-9\s&]+)(?:\s|,|\.)',      # from/by/of XXX
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, query_text)
            for match in matches:
                if match and len(match) > 2:  # Avoid short matches that might be noise
                    applicant_col = self.common_columns.get("出願人", "applicant_name")
                    conditions.append(f"{applicant_col} LIKE '%{match}%'")
                    break  # Only use the first good match
        
        # 3. Extract inventor references
        inventor_patterns = [
            r'(?:発明者|考案者|inventor)(?:は|が|の)「([^」]+)」',  # Inventor is "XXX"
            r'(?:発明者|考案者|inventor)(?:は|が|の)([^\s,。]+)',   # Inventor is XXX
        ]
        
        for pattern in inventor_patterns:
            matches = re.findall(pattern, query_text)
            for match in matches:
                if match and len(match) > 2:  # Avoid short matches that might be noise
                    inventor_col = self.common_columns.get("発明者", "inventor_name")
                    conditions.append(f"{inventor_col} LIKE '%{match}%'")
                    break  # Only use the first good match
        
        # 4. Extract IPC classification references
        ipc_pattern = r'(?:IPC|分類)\s*[が|は|の]\s*([A-H]\d{2}[A-Z](?:\d{1,6})?(?:/\d{2,6})?)'
        ipc_matches = re.findall(ipc_pattern, query_text.upper())
        if not ipc_matches:
            # Also try general regex pattern for IPC
            ipc_pattern = r'\b([A-H]\d{2}[A-Z]\d{1,6}(?:/\d{2,6})?)\b'
            ipc_matches = re.findall(ipc_pattern, query_text.upper())
        
        if ipc_matches:
            ipc_condition = []
            ipc_col = self.common_columns.get("IPC分類", "ipc_code")
            for ipc in ipc_matches:
                ipc_condition.append(f"{ipc_col} LIKE '%{ipc}%'")
            if ipc_condition:
                conditions.append("(" + " OR ".join(ipc_condition) + ")")
        
        # 5. Extract application number references
        app_number_patterns = [
            r'(?:出願番号|application).+?(\d{4}-\d+)',  # Japanese style
            r'(?:出願番号|application).+?(\d{6,12})',   # Just numbers
        ]
        
        for pattern in app_number_patterns:
            matches = re.findall(pattern, query_text)
            if matches:
                app_col = self.common_columns.get("出願番号", "application_number")
                conditions.append(f"{app_col} LIKE '%{matches[0]}%'")
                break
        
        # 6. Extract publication number references
        pub_number_patterns = [
            r'(?:公開番号|publication).+?(\d{4}-\d+)',  # Japanese style
            r'(?:公開番号|publication).+?(\d{6,12})',   # Just numbers
        ]
        
        for pattern in pub_number_patterns:
            matches = re.findall(pattern, query_text)
            if matches:
                pub_col = self.common_columns.get("公開番号", "publication_number")
                conditions.append(f"{pub_col} LIKE '%{matches[0]}%'")
                break
        
        # 7. Extract key technology terms
        tech_terms = {
            "カメラ": ["カメラ", "撮影", "写真"],
            "camera": ["camera", "photograph", "image", "imaging"],
            "車": ["自動車", "車両", "車"],
            "vehicle": ["vehicle", "car", "automobile", "automotive"],
            "半導体": ["半導体", "チップ", "ウェハー"],
            "semiconductor": ["semiconductor", "chip", "wafer", "integrated circuit", "ic"],
            "電池": ["電池", "バッテリー"],
            "battery": ["battery", "batteries", "power cell"],
            "ディスプレイ": ["ディスプレイ", "モニター", "画面"],
            "display": ["display", "monitor", "screen"],
            "通信": ["通信", "ネットワーク", "無線"],
            "communication": ["communication", "network", "wireless"],
            "医療": ["医療", "治療", "診断"],
            "medical": ["medical", "treatment", "diagnosis", "healthcare"]
        }
        
        # Check for tech terms in query
        for tech_category, terms in tech_terms.items():
            for term in terms:
                if term in query_lower:
                    title_col = self.common_columns.get("タイトル", "title")
                    abstract_col = self.common_columns.get("要約", "abstract")
                    conditions.append(
                        f"({title_col} LIKE '%{term}%' OR {abstract_col} LIKE '%{term}%')"
                    )
                    break  # Only add one condition per category
        
        # 8. Extract explicit search terms
        # Look for quoted text
        quoted_terms = re.findall(r'"([^"]+)"', query_text)
        for term in quoted_terms:
            if len(term) > 1:  # Avoid single chars
                title_col = self.common_columns.get("タイトル", "title")
                abstract_col = self.common_columns.get("要約", "abstract")
                conditions.append(
                    f"({title_col} LIKE '%{term}%' OR {abstract_col} LIKE '%{term}%')"
                )
        
        # Look for "about X" or "related to X" patterns
        about_patterns = [
            r'(?:に関する|について|に関連する|に関し)(?:、|\s)*(.+?)(?:の|を|が|は|$)',  # Japanese patterns
            r'(?:about|related to|concerning|regarding)\s+(.+?)(?:\s|,|\.|$)'  # English patterns
        ]
        
        for pattern in about_patterns:
            matches = re.findall(pattern, query_text)
            for match in matches:
                if match and len(match) > 1:
                    # Clean up the match, remove common stop words
                    terms = match.strip().split()
                    filtered_terms = [t for t in terms if len(t) > 1 and t not in ["the", "and", "or", "を", "が", "は", "の"]]
                    
                    if filtered_terms:
                        for term in filtered_terms:
                            title_col = self.common_columns.get("タイトル", "title")
                            abstract_col = self.common_columns.get("要約", "abstract")
                            conditions.append(
                                f"({title_col} LIKE '%{term}%' OR {abstract_col} LIKE '%{term}%')"
                            )
        
        # 9. Extract limit references
        limit_patterns = [
            r'(\d+)(?:件|個|つ|results|patents)',  # Japanese and English patterns
            r'(?:最大|最多|limit)(?:で|に)?\s*(\d+)',  # Max/limit patterns
            r'(?:show|limit|get|fetch)\s+(\d+)'  # English command patterns
        ]
        
        for pattern in limit_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                try:
                    limit = int(matches[0])
                    limit = max(1, min(limit, 100))  # Constrain between 1 and 100
                    break
                except (ValueError, IndexError):
                    pass
        
        # 10. Extract sorting preferences
        if any(term in query_lower for term in ["新しい", "最新", "newest", "latest", "recent"]):
            date_col = self.common_columns.get("出願日", "filing_date")
            order_by = f"{date_col} DESC"
        elif any(term in query_lower for term in ["古い", "oldest", "earliest"]):
            date_col = self.common_columns.get("出願日", "filing_date")
            order_by = f"{date_col} ASC"
        else:
            # Default ordering
            date_col = self.common_columns.get("出願日", "filing_date")
            order_by = f"{date_col} DESC"
        
        return conditions, limit, order_by
    
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
            column_names = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                # Map to original column names if possible
                row_dict = {}
                for i, col in enumerate(column_names):
                    display_name = self.column_map.get(col, col)
                    row_dict[display_name] = row[i]
                results.append(row_dict)
            
            conn.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results,
                "columns": column_names
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
        
        if not results.get("success"):
            # If the query fails, try a simpler approach with a text search
            fallback_query = self._generate_fallback_query(query_text)
            if fallback_query:
                fallback_results = self.execute_query(fallback_query)
                if fallback_results.get("success"):
                    return {
                        "success": True,
                        "natural_language_query": query_text,
                        "sql_query": fallback_query,
                        "note": "Used fallback query due to error in primary query",
                        "count": fallback_results.get("count", 0),
                        "results": fallback_results.get("results", []),
                        "columns": fallback_results.get("columns", [])
                    }
        
        return {
            "success": results.get("success", False),
            "natural_language_query": query_text,
            "sql_query": sql_query,
            "count": results.get("count", 0),
            "results": results.get("results", []),
            "columns": results.get("columns", [])
        }
    
    def _generate_fallback_query(self, query_text: str) -> Optional[str]:
        """
        Generate a simple fallback query when the main query fails
        
        Args:
            query_text: The original natural language query
            
        Returns:
            Simple SQL query or None if generation fails
        """
        try:
            # Strip query to essential parts
            clean_query = re.sub(r'\W+', ' ', query_text).strip()
            
            # Find most significant words (longer than 2 chars, not stop words)
            stop_words = {"the", "and", "or", "to", "from", "with", "by", "is", "are", "for", 
                         "を", "が", "は", "の", "に", "へ", "で", "と", "から"}
            words = [w for w in clean_query.split() if len(w) > 2 and w.lower() not in stop_words]
            
            if not words:
                return None
            
            # Select columns most likely to contain search text
            title_col = self.common_columns.get("タイトル", "title")
            abstract_col = self.common_columns.get("要約", "abstract")
            applicant_col = self.common_columns.get("出願人", "applicant_name")
            
            # Build simple LIKE conditions for each significant word
            conditions = []
            for word in words[:3]:  # Use at most 3 words to avoid over-constraining
                conditions.append(
                    f"({title_col} LIKE '%{word}%' OR {abstract_col} LIKE '%{word}%' OR {applicant_col} LIKE '%{word}%')"
                )
            
            # Build final query
            where_clause = " OR ".join(conditions)
            return f"SELECT * FROM inpit_data WHERE {where_clause} LIMIT 10"
        except Exception as e:
            logger.error(f"Error generating fallback query: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    processor = InpitNLQueryProcessor()
    result = processor.process_and_execute("トヨタの自動車関連の特許を5件見せて")
    print(f"Found {result.get('count', 0)} results")
    for patent in result.get('results', [])[:3]:  # Show first 3 patents
        print(f"{patent.get('タイトル', 'No title')} - {patent.get('出願番号', 'No number')}")
