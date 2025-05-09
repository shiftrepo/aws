#!/usr/bin/env python3
"""
Download bulk data from S3 bucket and create SQLite databases.
"""

import os
import boto3
import logging
import csv
import sqlite3
import tempfile
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 bucket details for INPIT data
S3_BUCKET = "ndi-3supervision"
S3_PATH_INPIT = "MIT/sample/plidb_bulkdata_202503.csv"
LOCAL_FILE_PATH_INPIT = "/app/data/plidb_bulkdata_202503.csv"
INPIT_DB_PATH = "/app/data/inpit.db"

# Google Patents database paths
S3_BUCKET_PATENTS = "ndi-3supervision"
S3_KEY_PATENTS_GCP = "MIT/demo/GCP/google_patents_gcp.db"
S3_KEY_PATENTS_S3 = "MIT/demo/GCP/google_patents_s3.db"
GOOGLE_PATENTS_GCP_DB_PATH = "/app/data/google_patents_gcp.db"
GOOGLE_PATENTS_S3_DB_PATH = "/app/data/google_patents_s3.db"

def download_from_s3(bucket, key, local_path, description="file"):
    """
    Download a file from S3 bucket.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        local_path: Local path to save the file
        description: Description of the file for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Attempting to download {description} from s3://{bucket}/{key} to {local_path}")
    
    try:
        # Print current user information
        logger.info(f"Running download as user {os.getuid()}:{os.getgid()}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Ensure directory exists with proper permissions
        data_dir = os.path.dirname(local_path)
        os.makedirs(data_dir, exist_ok=True)
        
        # Use a temporary file first to avoid permission issues
        tmp_file = f"{local_path}.download"
        
        # Check if the S3 object exists
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
        except Exception as e:
            logger.error(f"Error: S3 object does not exist at s3://{bucket}/{key}")
            logger.error(f"Error details: {e}")
            # List objects with similar path to help debugging
            try:
                prefix = '/'.join(key.split('/')[:-1])
                logger.info(f"Listing contents of s3://{bucket}/{prefix}/")
                response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix+'/')
                for obj in response.get('Contents', []):
                    logger.info(f"Found object: {obj['Key']}")
            except Exception as list_err:
                logger.error(f"Error listing S3 objects: {list_err}")
            return False
        
        # Download file to temporary location
        s3_client.download_file(bucket, key, tmp_file)
        
        # Make the file readable and writable by everyone
        try:
            os.chmod(tmp_file, 0o666)
        except Exception as e:
            logger.warning(f"Could not set permissions on downloaded file: {e}")
        
        # Move to final location
        import shutil
        shutil.move(tmp_file, local_path)
        
        # Final permission check
        try:
            os.chmod(local_path, 0o666)
        except Exception as e:
            logger.warning(f"Could not set final permissions: {e}")
        
        logger.info(f"{description} downloaded successfully from S3")
        
        # Verify file size
        file_size = os.path.getsize(local_path)
        logger.info(f"Downloaded file size: {file_size} bytes")
        
        return True
    except Exception as e:
        logger.error(f"Error downloading {description} from S3: {e}")
        return False

def create_empty_db(db_path, schema_type="patents"):
    """
    Create an empty database with basic schema if download fails.
    
    Args:
        db_path: Path to create the empty database
        schema_type: Type of schema to create ('patents' or 'inpit')
    """
    logger.info(f"Creating empty {schema_type} database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if schema_type == "patents":
            # Create basic schema for patents database
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS publications (
                publication_number TEXT PRIMARY KEY,
                filing_date TEXT,
                publication_date TEXT,
                application_number TEXT,
                assignee_harmonized TEXT,
                assignee_original TEXT,
                title_ja TEXT,
                title_en TEXT,
                abstract_ja TEXT,
                abstract_en TEXT,
                claims TEXT,
                ipc_code TEXT,
                family_id TEXT,
                country_code TEXT,
                kind_code TEXT,
                priority_date TEXT,
                grant_date TEXT,
                priority_claim TEXT,
                status TEXT,
                legal_status TEXT,
                examined TEXT,
                family_size INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS patent_families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                application_number TEXT,
                publication_number TEXT,
                country_code TEXT,
                UNIQUE(family_id, application_number)
            )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_id ON publications (family_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_num ON publications (application_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assignee_harmonized ON publications (assignee_harmonized)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_country_code ON publications (country_code)')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_family_id ON patent_families (family_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_app_num ON patent_families (application_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_pub_num ON patent_families (publication_number)')
        
        elif schema_type == "inpit":
            # Create empty inpit data table (column names will be determined from CSV)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS inpit_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
            ''')
        
        conn.commit()
        conn.close()
        
        # Set appropriate permissions
        try:
            os.chmod(db_path, 0o666)
        except Exception as e:
            logger.warning(f"Could not set permissions on empty database file: {e}")
            
        logger.info(f"Empty database created successfully at {db_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating empty database: {e}")
        return False

def process_inpit_csv_to_sqlite():
    """
    Process downloaded INPIT CSV file and create SQLite database.
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(LOCAL_FILE_PATH_INPIT):
        logger.error(f"INPIT CSV file not found at {LOCAL_FILE_PATH_INPIT}")
        return False

    try:
        logger.info(f"Processing INPIT CSV file to SQLite database: {INPIT_DB_PATH}")
        
        # Read the CSV file using pandas with proper encoding
        df = pd.read_csv(LOCAL_FILE_PATH_INPIT, encoding='utf-8')
        
        # Store column mapping for future reference
        column_mapping = {}
        cleaned_columns = []
        
        # Clean column names for SQLite
        for col in df.columns:
            # Create a SQL-friendly column name
            clean_col = col.lower().replace(' ', '_').replace('-', '_').replace('/', '_').replace('(', '').replace(')', '')
            clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_col)
            
            # Ensure the column name starts with a letter
            if not clean_col[0].isalpha():
                clean_col = f"col_{clean_col}"
                
            # Avoid duplicate column names
            base_col = clean_col
            i = 1
            while clean_col in cleaned_columns:
                clean_col = f"{base_col}_{i}"
                i += 1
                
            cleaned_columns.append(clean_col)
            column_mapping[clean_col] = col  # Store mapping of clean name to original
            
        # Rename the columns
        df.columns = cleaned_columns
        
        # Create SQLite connection
        conn = sqlite3.connect(INPIT_DB_PATH)
        
        # Write to SQLite
        df.to_sql('inpit_data', conn, if_exists='replace', index=False)
        
        # Create indexes for better performance
        cursor = conn.cursor()
        
        # Create indexes on likely query columns
        for col in cleaned_columns:
            if 'application' in col or 'number' in col or 'date' in col or 'name' in col or 'id' in col:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{col} ON inpit_data ({col})')
                except Exception as e:
                    logger.warning(f"Could not create index on column {col}: {e}")
        
        conn.commit()
        conn.close()
        
        # Save column mapping to a JSON file for reference
        import json
        with open('/app/data/column_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(column_mapping, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Successfully created INPIT database with {len(df)} records")
        logger.info(f"Created {len(cleaned_columns)} columns with mapping saved to column_mapping.json")
        
        return True
    except Exception as e:
        logger.error(f"Error processing INPIT CSV to SQLite: {e}")
        return False

def download_google_patents_databases():
    """
    Download the Google Patents databases from S3 bucket.
    """
    success_gcp = False
    success_s3 = False
    
    # Create directory structure if it doesn't exist
    os.makedirs(os.path.dirname(GOOGLE_PATENTS_GCP_DB_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(GOOGLE_PATENTS_S3_DB_PATH), exist_ok=True)
    
    # Download GCP database
    if os.path.exists(GOOGLE_PATENTS_GCP_DB_PATH):
        logger.info(f"Removing existing GCP database file: {GOOGLE_PATENTS_GCP_DB_PATH}")
        os.remove(GOOGLE_PATENTS_GCP_DB_PATH)
    
    success_gcp = download_from_s3(
        S3_BUCKET_PATENTS,
        S3_KEY_PATENTS_GCP,
        GOOGLE_PATENTS_GCP_DB_PATH, 
        "Google Patents GCP database"
    )
    
    if not success_gcp:
        # If download fails, create an empty database
        logger.warning("Creating fallback empty Google Patents GCP database")
        create_empty_db(GOOGLE_PATENTS_GCP_DB_PATH, "patents")
    
    # Download S3 database
    if os.path.exists(GOOGLE_PATENTS_S3_DB_PATH):
        logger.info(f"Removing existing S3 database file: {GOOGLE_PATENTS_S3_DB_PATH}")
        os.remove(GOOGLE_PATENTS_S3_DB_PATH)
    
    success_s3 = download_from_s3(
        S3_BUCKET_PATENTS,
        S3_KEY_PATENTS_S3,
        GOOGLE_PATENTS_S3_DB_PATH, 
        "Google Patents S3 database"
    )
    
    if not success_s3:
        # If download fails, create an empty database
        logger.warning("Creating fallback empty Google Patents S3 database")
        create_empty_db(GOOGLE_PATENTS_S3_DB_PATH, "patents")
    
    return success_gcp or success_s3

if __name__ == "__main__":
    # Download INPIT data
    inpit_success = download_from_s3(S3_BUCKET, S3_PATH_INPIT, LOCAL_FILE_PATH_INPIT, "INPIT CSV data")
    
    if inpit_success:
        # Process the CSV to SQLite
        process_success = process_inpit_csv_to_sqlite()
        if not process_success:
            logger.error("Failed to process INPIT CSV to SQLite.")
    else:
        logger.error("Failed to download INPIT data from S3.")
        # Create empty database
        create_empty_db(INPIT_DB_PATH, "inpit")
    
    # Download Google Patents databases
    patents_success = download_google_patents_databases()
    
    if not patents_success:
        logger.warning("Failed to download Google Patents databases from S3.")
    
    # If all downloads failed, exit with error
    if not inpit_success and not patents_success:
        logger.error("All data downloads failed.")
        sys.exit(1)
    else:
        logger.info("Data download completed. Ready for importing.")
