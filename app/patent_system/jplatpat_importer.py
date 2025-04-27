import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from tqdm import tqdm

from app.patent_system.jplatpat_scraper import JPlatPatScraper, search_patents, get_patent_details
from app.patent_system.db_sqlite import SQLiteDBManager, init_sqlite_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JPlatPatImporter:
    """Class to import patent data from J-PlatPat to SQLite"""
    
    def __init__(self, use_proxy: bool = False, proxy_url: Optional[str] = None):
        """
        Initialize the importer
        
        Args:
            use_proxy: Whether to use a proxy for J-PlatPat requests
            proxy_url: Proxy URL if use_proxy is True
        """
        self.scraper = JPlatPatScraper(use_proxy=use_proxy, proxy_url=proxy_url)
        self.db_manager = SQLiteDBManager()
        
        # Initialize the database if needed
        init_sqlite_db()
    
    def import_from_search(self, query: str, limit: int = 100) -> int:
        """
        Import patent data from J-PlatPat search results
        
        Args:
            query: Search query string for J-PlatPat
            limit: Maximum number of patents to import
            
        Returns:
            int: Number of patents imported
        """
        logger.info(f"Searching for patents with query: {query}")
        
        # Search for patents
        search_results = self.scraper.search_patents(query=query, limit=limit)
        
        if not search_results:
            logger.warning(f"No patents found for query: {query}")
            return 0
            
        logger.info(f"Found {len(search_results)} patents in search results")
        
        # Extract application numbers
        application_numbers = []
        for result in search_results:
            app_num = result.get("application_number")
            if app_num:
                application_numbers.append(app_num)
        
        if not application_numbers:
            logger.warning("No valid application numbers found in search results")
            return 0
            
        logger.info(f"Processing {len(application_numbers)} patent application numbers")
        
        # Fetch detailed data for each patent
        full_patent_data = []
        
        for app_num in tqdm(application_numbers, desc="Fetching patent details"):
            try:
                details = self.scraper.get_patent_details(app_num)
                if details and "error" not in details:
                    full_patent_data.append(details)
            except Exception as e:
                logger.error(f"Error fetching details for {app_num}: {str(e)}")
        
        # Store patents in database
        with self.db_manager:
            count = self.db_manager.store_patents_batch(full_patent_data)
            logger.info(f"Successfully imported {count} patents to the database")
            return count
    
    def import_by_company(self, company_name: str, limit: int = 100) -> int:
        """
        Import patents by company name
        
        Args:
            company_name: Name of the company
            limit: Maximum number of patents to import
            
        Returns:
            int: Number of patents imported
        """
        logger.info(f"Searching for patents from company: {company_name}")
        
        # This is a specialized search for company
        return self.import_from_search(company_name, limit)
    
    def import_by_technology(self, technology: str, limit: int = 100) -> int:
        """
        Import patents by technology area
        
        Args:
            technology: Technology keyword or IPC code
            limit: Maximum number of patents to import
            
        Returns:
            int: Number of patents imported
        """
        logger.info(f"Searching for patents in technology area: {technology}")
        
        # This is a specialized search for technology
        return self.import_from_search(technology, limit)
    
    def import_from_json_file(self, json_file: str) -> int:
        """
        Import patent data from a JSON file
        
        Args:
            json_file: Path to JSON file containing patent data
            
        Returns:
            int: Number of patents imported
        """
        try:
            logger.info(f"Importing patent data from JSON file: {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different possible JSON structures
            patents_data = []
            
            if isinstance(data, list):
                # List of patent records
                patents_data = data
            elif isinstance(data, dict):
                # Single patent record or container with results field
                if "results" in data and isinstance(data["results"], list):
                    patents_data = data["results"]
                else:
                    # Assume it's a single patent record
                    patents_data = [data]
            
            logger.info(f"Found {len(patents_data)} patent records in JSON file")
            
            # Store in database
            with self.db_manager:
                count = self.db_manager.store_patents_batch(patents_data)
                logger.info(f"Successfully imported {count} patents from JSON file")
                return count
                
        except Exception as e:
            logger.error(f"Error importing patents from JSON file: {str(e)}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the patents in the database
        
        Returns:
            Dict with database statistics
        """
        with self.db_manager:
            patent_count = self.db_manager.count_patents()
            
            # In a real implementation, we could get more detailed stats here
            stats = {
                "patent_count": patent_count,
                "database_path": self.db_manager.db_path
            }
            
            return stats


def import_patents(query: str, limit: int = 100) -> int:
    """
    Convenience function to import patents by query
    
    Args:
        query: Search query string
        limit: Maximum number of patents to import
        
    Returns:
        int: Number of patents imported
    """
    importer = JPlatPatImporter()
    return importer.import_from_search(query, limit)


def import_by_company(company_name: str, limit: int = 100) -> int:
    """
    Convenience function to import patents by company name
    
    Args:
        company_name: Name of the company
        limit: Maximum number of patents to import
        
    Returns:
        int: Number of patents imported
    """
    importer = JPlatPatImporter()
    return importer.import_by_company(company_name, limit)


if __name__ == "__main__":
    # Example usage
    print("J-PlatPat Patent Importer")
    print("========================")
    
    importer = JPlatPatImporter()
    
    # Check current database stats
    stats = importer.get_database_stats()
    print(f"Current patent count: {stats['patent_count']}")
    
    # Import patents by company
    company = "トヨタ自動車"
    print(f"\nImporting patents for company: {company}")
    count = importer.import_by_company(company, limit=10)
    print(f"Imported {count} patents")
    
    # Check updated stats
    stats = importer.get_database_stats()
    print(f"Updated patent count: {stats['patent_count']}")
    
    # Import patents by technology
    tech = "人工知能"
    print(f"\nImporting patents for technology: {tech}")
    count = importer.import_by_technology(tech, limit=10)
    print(f"Imported {count} patents")
    
    # Final stats
    stats = importer.get_database_stats()
    print(f"Final patent count: {stats['patent_count']}")
