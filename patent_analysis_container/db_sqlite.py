import os
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import sqlalchemy.exc
from sqlalchemy import text

from .models_sqlite import (
    Base, engine, SessionLocal, Patent, Applicant, Inventor, 
    IPCClassification, Claim, Description, ensure_db_exists
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SQLiteDBManager:
    """Manager for SQLite database operations"""
    
    def __init__(self):
        """Initialize the database manager"""
        self.db_path = ensure_db_exists()
        self.db = None
    
    def __enter__(self):
        """Context manager entry"""
        self.db = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.db:
            self.db.close()
            
    def execute_raw_sql(self, sql_query: str, params=None):
        """
        Execute a raw SQL query and return results
        
        Args:
            sql_query: The SQL query string
            params: Query parameters (optional)
            
        Returns:
            Query results
        """
        try:
            logger.info(f"Executing raw SQL: {sql_query}")
            if params:
                logger.info(f"With parameters: {params}")
                
            result = self.db.execute(text(sql_query), params or {})
            if sql_query.strip().upper().startswith("SELECT"):
                # For SELECT queries, fetch all results
                data = [dict(row) for row in result.mappings()]
                logger.info(f"SQL query returned {len(data)} rows")
                return data
            else:
                # For non-SELECT queries, commit and return affected rows
                self.db.commit()
                return {"affected_rows": result.rowcount}
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            logger.error(traceback.format_exc())
            self.db.rollback()
            raise
    
    def get_patent_by_application_number(self, application_number: str) -> Optional[Patent]:
        """
        Get a patent by application number
        
        Args:
            application_number: Patent application number
            
        Returns:
            Patent object if found, None otherwise
        """
        try:
            return self.db.query(Patent).filter(
                Patent.application_number == application_number
            ).first()
        except Exception as e:
            logger.error(f"Error getting patent by application number: {str(e)}")
            return None
    
    def get_patents_by_applicant(self, applicant_name: str, limit: int = 100) -> List[Patent]:
        """
        Get patents by applicant name
        
        Args:
            applicant_name: Name of the applicant
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            # Log the equivalent SQL query
            sql = f"""
            SELECT p.* FROM patents p
            JOIN applicants a ON p.id = a.patent_id
            WHERE a.name LIKE '%{applicant_name}%'
            LIMIT {limit}
            """
            logger.info(f"Equivalent SQL for get_patents_by_applicant: {sql}")
            
            patents = self.db.query(Patent).join(
                Applicant
            ).filter(
                Applicant.name.like(f"%{applicant_name}%")
            ).limit(limit).all()
            
            logger.info(f"Found {len(patents)} patents for applicant {applicant_name}")
            
            # Try direct SQL for inpit_data if patents table has no data
            if not patents:
                try:
                    direct_sql = f"SELECT * FROM inpit_data WHERE applicant LIKE '%{applicant_name}%' ORDER BY application_date DESC LIMIT {limit};"
                    logger.info(f"Attempting direct SQL query on inpit_data: {direct_sql}")
                    inpit_data_results = self.execute_raw_sql(direct_sql)
                    if inpit_data_results:
                        logger.info(f"Found {len(inpit_data_results)} records in inpit_data table")
                        # Log the data structure for debugging
                        if inpit_data_results and len(inpit_data_results) > 0:
                            logger.info(f"Sample record structure: {list(inpit_data_results[0].keys())}")
                except Exception as sql_err:
                    logger.error(f"Error querying inpit_data table: {str(sql_err)}")
            
            return patents
        except Exception as e:
            logger.error(f"Error getting patents by applicant: {str(e)}")
            return []
    
    def search_patents(self, query: str, limit: int = 100) -> List[Patent]:
        """
        Search patents by title, abstract, or applicant name
        
        Args:
            query: Search query string
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            # Log the equivalent SQL query
            sql = f"""
            SELECT p.* FROM patents p 
            WHERE p.title LIKE '%{query}%' OR p.abstract LIKE '%{query}%'
            LIMIT {limit}
            """
            logger.info(f"Equivalent SQL for first part of search_patents: {sql}")
            
            # Search in title, abstract, applicant name
            results = self.db.query(Patent).filter(
                Patent.title.like(f"%{query}%") | 
                Patent.abstract.like(f"%{query}%")
            ).limit(limit).all()
            
            # Log the equivalent SQL query for applicant search
            sql = f"""
            SELECT p.* FROM patents p
            JOIN applicants a ON p.id = a.patent_id
            WHERE a.name LIKE '%{query}%'
            LIMIT {limit}
            """
            logger.info(f"Equivalent SQL for applicant part of search_patents: {sql}")
            
            # Also search in applicant names
            applicant_results = self.db.query(Patent).join(
                Applicant
            ).filter(
                Applicant.name.like(f"%{query}%")
            ).limit(limit).all()
            
            # Combine results, removing duplicates
            all_patents = {}
            for patent in results + applicant_results:
                all_patents[patent.id] = patent
            
            combined_results = list(all_patents.values())[:limit]
            logger.info(f"Combined search returned {len(combined_results)} unique patents")
            
            # Try direct SQL for inpit_data if patents table has no data
            if not combined_results:
                try:
                    direct_sql = f"""
                    SELECT * FROM inpit_data 
                    WHERE title LIKE '%{query}%' 
                    OR abstract LIKE '%{query}%' 
                    OR applicant LIKE '%{query}%'
                    ORDER BY application_date DESC 
                    LIMIT {limit};
                    """
                    logger.info(f"Attempting direct SQL query on inpit_data: {direct_sql}")
                    inpit_data_results = self.execute_raw_sql(direct_sql)
                    if inpit_data_results:
                        logger.info(f"Found {len(inpit_data_results)} matching records in inpit_data table")
                except Exception as sql_err:
                    logger.error(f"Error querying inpit_data table: {str(sql_err)}")
            
            return combined_results
        except Exception as e:
            logger.error(f"Error searching patents: {str(e)}")
            return []
    
    def get_all_patents(self, limit: int = 1000) -> List[Patent]:
        """
        Get all patents in the database
        
        Args:
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            # Log the equivalent SQL query
            sql = f"SELECT * FROM patents LIMIT {limit}"
            logger.info(f"Equivalent SQL for get_all_patents: {sql}")
            
            patents = self.db.query(Patent).limit(limit).all()
            logger.info(f"Retrieved {len(patents)} patents")
            
            # Try direct SQL for inpit_data if patents table has no data
            if not patents:
                try:
                    direct_sql = f"SELECT * FROM inpit_data LIMIT {limit};"
                    logger.info(f"Attempting direct SQL query on inpit_data: {direct_sql}")
                    inpit_data_results = self.execute_raw_sql(direct_sql)
                    if inpit_data_results:
                        logger.info(f"Found {len(inpit_data_results)} records in inpit_data table")
                except Exception as sql_err:
                    logger.error(f"Error querying inpit_data table: {str(sql_err)}")
            
            return patents
        except Exception as e:
            logger.error(f"Error getting all patents: {str(e)}")
            return []
    
    def count_patents(self) -> int:
        """
        Count the number of patents in the database
        
        Returns:
            Number of patents
        """
        try:
            # Log the equivalent SQL query
            sql = "SELECT COUNT(*) FROM patents"
            logger.info(f"Equivalent SQL for count_patents: {sql}")
            
            count = self.db.query(Patent).count()
            logger.info(f"Patent count: {count}")
            
            # Try direct SQL for inpit_data if patents table has no data
            if count == 0:
                try:
                    direct_sql = "SELECT COUNT(*) AS count FROM inpit_data;"
                    logger.info(f"Attempting direct SQL count on inpit_data: {direct_sql}")
                    result = self.execute_raw_sql(direct_sql)
                    if result and len(result) > 0:
                        inpit_count = result[0].get("count", 0)
                        logger.info(f"Found {inpit_count} records in inpit_data table")
                except Exception as sql_err:
                    logger.error(f"Error counting inpit_data records: {str(sql_err)}")
            
            return count
        except Exception as e:
            logger.error(f"Error counting patents: {str(e)}")
            return 0


def init_sqlite_db():
    """Initialize SQLite database if not exists"""
    ensure_db_exists()
    logger.info("SQLite database initialized")

if __name__ == "__main__":
    # Test database operations
    init_sqlite_db()
