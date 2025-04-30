#!/usr/bin/env python3
import os
import argparse
import logging
from datetime import datetime

from app.patent_system.models_sqlite import ensure_db_exists
from app.patent_system.inpit_sqlite_connector import get_connector
from app.patent_system.data_importer import PatentDataImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("patent-system-init")

def initialize_database():
    """Initialize database tables"""
    logger.info("Initializing database tables...")
    ensure_db_exists()
    logger.info("Database initialization complete!")

def import_data_from_inpit(limit: int = 100):
    """
    Import patent data from the Inpit SQLite API
    
    Args:
        limit: Maximum number of patents to import
    """
    # Check for INPIT_API_URL environment variable, default to localhost
    api_url = os.environ.get("INPIT_API_URL", "http://localhost:5001")
    logger.info(f"Using Inpit SQLite API at: {api_url}")
    
    # Create an importer with the API URL
    importer = PatentDataImporter(api_url)
    
    # Check if the API is accessible
    connector = get_connector(api_url)
    status = connector.get_api_status()
    
    if "error" in status:
        logger.error(f"Error connecting to Inpit SQLite API: {status['error']}")
        logger.error("Make sure the Inpit SQLite service is running and accessible")
        return 0
    
    # Import data
    record_count = status.get("record_count", 0) if "record_count" in status else "unknown"
    logger.info(f"Inpit SQLite database contains {record_count} records")
    logger.info(f"Importing up to {limit} records from Inpit SQLite API...")
    
    count = importer.import_from_inpit_to_local_db(limit)
    logger.info(f"Imported {count} patents from Inpit SQLite API")
    
    return count

def print_usage_instructions():
    """Print instructions for using the system"""
    logger.info("\n" + "="*80)
    logger.info("PATENT SYSTEM SETUP COMPLETE!")
    logger.info("="*80)
    logger.info("\nYou can now use the patent analysis system with data from Inpit SQLite.")
    logger.info("\nExample commands:")
    
    logger.info("\n1. Import additional data:")
    logger.info("   python -m app.patent_system.data_importer")
    
    logger.info("\n2. Run analysis on the data:")
    logger.info("   python -m app.patent_system.patent_analyzer_inpit")
    
    logger.info("\n3. Generate reports:")
    logger.info("   python -m app.patent_system.report_generator")
    
    logger.info("\n" + "="*80)

def main():
    """Main function to initialize database and import data"""
    parser = argparse.ArgumentParser(description='Initialize patent database and import data from Inpit SQLite')
    parser.add_argument('--skip-init', action='store_true', help='Skip database initialization')
    parser.add_argument('--skip-import', action='store_true', help='Skip data import')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of records to import')
    
    args = parser.parse_args()
    
    if not args.skip_init:
        initialize_database()
    
    if not args.skip_import:
        import_data_from_inpit(args.limit)
    
    print_usage_instructions()

if __name__ == "__main__":
    main()
