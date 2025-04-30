#!/usr/bin/env python3
import os
import argparse
import logging
from datetime import datetime

from app.patent_system.models_sqlite import ensure_db_exists

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

def print_usage_instructions():
    """Print instructions for using the system"""
    logger.info("\n" + "="*80)
    logger.info("PATENT SYSTEM SETUP COMPLETE!")
    logger.info("="*80)
    logger.info("\nYou can now use the patent analysis system with data from Inpit SQLite.")
    logger.info("\nExample commands:")
    
    logger.info("\n1. Analyze data using Inpit SQLite API:")
    logger.info("   python -m app.patent_system.patent_analyzer_inpit")

    logger.info("\n2. Start MCP server for Claude AI integration:")
    logger.info("   python -m app.patent_system.mcp_patent_server")

    logger.info("\n" + "="*80)

def main():
    """Main function to initialize database structure only"""
    parser = argparse.ArgumentParser(description='Initialize patent database structure for Inpit SQLite integration')
    parser.add_argument('--skip-init', action='store_true', help='Skip database initialization')
    parser.add_argument('--api-url', type=str, help='Inpit SQLite API URL (defaults to http://localhost:5001)')
    
    args = parser.parse_args()
    
    # Set API URL if provided
    if args.api_url:
        os.environ["INPIT_API_URL"] = args.api_url
    
    if not args.skip_init:
        initialize_database()
    
    print_usage_instructions()

if __name__ == "__main__":
    main()
