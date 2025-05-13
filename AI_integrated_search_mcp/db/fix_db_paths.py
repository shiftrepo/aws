#!/usr/bin/env python3
"""
Fix Database Path Issues
------------------------
This script addresses path issues in the sqlite-db container.
It ensures the database files are correctly located and accessible.
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path("/app/data")
INPUT_DB_PATH = DATA_DIR / "inpit.db"
BIGQUERY_DB_PATH = DATA_DIR / "google_patents_gcp.db"

def fix_db_paths():
    """Fix database paths and ensure files are accessible"""
    logger.info("Starting database path fix")
    
    # Check if we're running inside container
    in_container = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
    logger.info(f"Running in container: {in_container}")
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    logger.info(f"Data directory created/verified: {DATA_DIR}")
    
    # Check if database files exist
    input_db_exists = INPUT_DB_PATH.exists()
    bigquery_db_exists = BIGQUERY_DB_PATH.exists()
    
    logger.info(f"Inpit DB exists: {input_db_exists} at {INPUT_DB_PATH}")
    logger.info(f"BigQuery DB exists: {bigquery_db_exists} at {BIGQUERY_DB_PATH}")
    
    # If running in container and files don't exist, they should be mounted
    # or manually copied. Let's check permissions.
    if input_db_exists:
        try:
            # Test if we can open the database
            conn = sqlite3.connect(str(INPUT_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            logger.info("Successfully opened Inpit database!")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to Inpit database: {str(e)}")
            # Try to fix permission issues
            try:
                os.chmod(str(INPUT_DB_PATH), 0o644)
                logger.info("Applied read permissions to Inpit database")
            except Exception as e:
                logger.error(f"Failed to change permissions: {str(e)}")
    
    if bigquery_db_exists:
        try:
            # Test if we can open the database
            conn = sqlite3.connect(str(BIGQUERY_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            logger.info("Successfully opened BigQuery database!")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to BigQuery database: {str(e)}")
            # Try to fix permission issues
            try:
                os.chmod(str(BIGQUERY_DB_PATH), 0o644)
                logger.info("Applied read permissions to BigQuery database")
            except Exception as e:
                logger.error(f"Failed to change permissions: {str(e)}")
    
    # Create or update a marker file to indicate fix was attempted
    marker_file = DATA_DIR / ".db_fix_applied"
    with open(marker_file, "w") as f:
        f.write("DB fix script was applied")
    logger.info("Created marker file to indicate fix was applied")
    
    return {
        "input_db_exists": input_db_exists,
        "bigquery_db_exists": bigquery_db_exists,
        "input_db_size": INPUT_DB_PATH.stat().st_size if input_db_exists else 0,
        "bigquery_db_size": BIGQUERY_DB_PATH.stat().st_size if bigquery_db_exists else 0,
        "data_dir_writable": os.access(DATA_DIR, os.W_OK),
    }

if __name__ == "__main__":
    try:
        results = fix_db_paths()
        print("Database path fix completed")
        print(f"Inpit DB exists: {results['input_db_exists']} (size: {results['input_db_size']} bytes)")
        print(f"BigQuery DB exists: {results['bigquery_db_exists']} (size: {results['bigquery_db_size']} bytes)")
        print(f"Data directory writable: {results['data_dir_writable']}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fixing database paths: {str(e)}")
        sys.exit(1)
