import os
import argparse
import json
import logging
from typing import Dict, List, Any, Union
from tqdm import tqdm
import fitz  # PyMuPDF

from app.patent_system.j_platpat_scraper import JPlatPatClient, fetch_patents_by_company
from app.patent_system.db_manager import PatentDBManager, init_db_if_needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PatentDataImporter:
    """Class to import patent data from J-PlatPat to PostgreSQL"""
    
    def __init__(self):
        """Initialize the importer"""
        self.jplatpat_client = JPlatPatClient()
        self.db_manager = PatentDBManager()
        
    def import_from_search(self, query: str, max_results: int = 100) -> int:
        """
        Import patent data from J-PlatPat search results
        
        Args:
            query: Search query string for J-PlatPat
            max_results: Maximum number of patents to import
            
        Returns:
            int: Number of patents imported
        """
        # Initialize DB tables if needed
        init_db_if_needed()
        
        logger.info(f"Searching for patents with query: {query}")
        search_results = self.jplatpat_client.search_patents(
            query=query,
            page=1,
            results_per_page=max_results
        )
        
        if "error" in search_results:
            logger.error(f"Search error: {search_results['error']}")
            return 0
        
        patents = search_results.get("results", [])
        logger.info(f"Found {len(patents)} patents in search results")
        
        if not patents:
            return 0
        
        # Extract application numbers
        application_numbers = [p.get("applicationNumber") for p in patents if p.get("applicationNumber")]
        logger.info(f"Fetching full data for {len(application_numbers)} patent applications")
        
        # Fetch complete data for all patents
        full_data = self.jplatpat_client.fetch_full_patent_data(application_numbers)
        
        # Store in database
        with self.db_manager:
            count = self.db_manager.store_patents_batch(full_data)
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
        # Initialize DB tables if needed
        init_db_if_needed()
        
        logger.info(f"Searching for patents from company: {company_name}")
        patents = fetch_patents_by_company(self.jplatpat_client, company_name, limit)
        
        if not patents:
            logger.info(f"No patents found for company: {company_name}")
            return 0
        
        logger.info(f"Found {len(patents)} patents for company: {company_name}")
        
        # Extract application numbers
        application_numbers = [p.get("applicationNumber") for p in patents if p.get("applicationNumber")]
        
        # Fetch complete data for all patents
        full_data = self.jplatpat_client.fetch_full_patent_data(application_numbers)
        
        # Store in database
        with self.db_manager:
            count = self.db_manager.store_patents_batch(full_data)
            logger.info(f"Successfully imported {count} patents to the database for company {company_name}")
            return count
    
    def import_from_pdf(self, pdf_path: str) -> Union[Dict[str, Any], None]:
        """
        Import patent data from a PDF file
        
        Args:
            pdf_path: Path to the PDF file containing patent information
            
        Returns:
            Dict containing extracted patent data, or None if failed
        """
        try:
            # Initialize DB tables if needed
            init_db_if_needed()
            
            logger.info(f"Extracting patent data from PDF: {pdf_path}")
            
            # Extract text from PDF
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Here we would implement PDF parsing logic to extract structured data
            # This is a complex task requiring specific parsing logic for J-PlatPat PDFs
            
            # Placeholder implementation - in a real system this would implement full PDF parsing
            # Extract application number from filename or PDF content
            application_number = None
            
            filename = os.path.basename(pdf_path)
            # Try to extract from filename (assuming a format like "JPA2025027833-000000.pdf")
            if filename.startswith("JPA"):
                try:
                    application_number = filename.split("-")[0][3:]
                except:
                    pass
            
            # If not found in filename, try to find in content
            if not application_number:
                # Very simple regex - would need refinement for actual implementation
                import re
                match = re.search(r'出願番号[：:]\s*(\d{4}-\d+)', text)
                if match:
                    application_number = match.group(1)
                else:
                    # Try another pattern
                    match = re.search(r'特願\s*(\d{4}-\d+)', text)
                    if match:
                        application_number = match.group(1)
            
            if not application_number:
                logger.error("Could not extract application number from PDF")
                return None
            
            logger.info(f"Extracted application number: {application_number}")
            
            # Use the application number to fetch complete data from J-PlatPat
            patent_data = self.jplatpat_client.get_patent_details(application_number)
            
            if "error" in patent_data:
                logger.error(f"Error fetching patent details: {patent_data['error']}")
                
                # Fallback to basic data extracted from PDF
                # This would require more sophisticated PDF parsing
                patent_data = {
                    "applicationNumber": application_number,
                    "title": "Unknown",  # Would be extracted from PDF in real implementation
                    "abstract": text[:500],  # Use first part of text as abstract
                    "claims": [],
                    "descriptions": [{"text": text}]
                }
            
            # Store in database
            with self.db_manager:
                patent = self.db_manager.store_patent(patent_data)
                if patent:
                    logger.info(f"Successfully imported patent {application_number} from PDF")
                    return patent.to_dict()
                else:
                    logger.error(f"Failed to import patent {application_number} from PDF")
                    return None
                
        except Exception as e:
            logger.error(f"Error importing patent from PDF: {str(e)}")
            return None
    
    def import_from_json_file(self, json_file: str) -> int:
        """
        Import patent data from a JSON file
        
        Args:
            json_file: Path to JSON file containing patent data
            
        Returns:
            int: Number of patents imported
        """
        try:
            # Initialize DB tables if needed
            init_db_if_needed()
            
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


def main():
    """Main entry point when running as a script"""
    parser = argparse.ArgumentParser(description='Import patent data from J-PlatPat')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search import
    search_parser = subparsers.add_parser('search', help='Import from search results')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', type=int, default=100, help='Maximum results to import')
    
    # Company import
    company_parser = subparsers.add_parser('company', help='Import by company name')
    company_parser.add_argument('name', help='Company name')
    company_parser.add_argument('--limit', type=int, default=100, help='Maximum patents to import')
    
    # PDF import
    pdf_parser = subparsers.add_parser('pdf', help='Import from PDF file')
    pdf_parser.add_argument('file', help='Path to PDF file')
    
    # JSON import
    json_parser = subparsers.add_parser('json', help='Import from JSON file')
    json_parser.add_argument('file', help='Path to JSON file')
    
    # Parse arguments
    args = parser.parse_args()
    
    importer = PatentDataImporter()
    
    if args.command == 'search':
        importer.import_from_search(args.query, args.max_results)
    elif args.command == 'company':
        importer.import_by_company(args.name, args.limit)
    elif args.command == 'pdf':
        importer.import_from_pdf(args.file)
    elif args.command == 'json':
        importer.import_from_json_file(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
