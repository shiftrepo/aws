#!/usr/bin/env python3
"""
Download bulk data from S3 bucket or create mock data for testing.
This script also handles downloading Google Patents databases from S3 and creating one from BigQuery.
"""

import os
import boto3
import logging
import csv
import random
import sqlite3
import tempfile
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 bucket details for INPIT data
S3_BUCKET = "ndi-3supervision"
S3_PATH = "MIT/sample/plidb_bulkdata_202503.csv"
LOCAL_FILE_PATH = "/app/data/plidb_bulkdata_202503.csv"

# Google Patents database paths
S3_BUCKET_PATENTS = "ndi-3supervision"
S3_KEY_PATENTS = "MIT/demo/GCP/bak/google_patents.db"
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

def create_empty_db(db_path):
    """
    Create an empty database with basic schema if download fails.
    
    Args:
        db_path: Path to create the empty database
    """
    logger.info(f"Creating empty database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic schema
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

class GooglePatentsFetcher:
    """Class to fetch and process Google Patents Public Data"""
    
    def __init__(self, credentials_path: str = None, db_path: str = "/app/data/google_patents_gcp.db"):
        """
        Initialize the Google Patents fetcher
        
        Args:
            credentials_path: Path to Google Cloud service account credentials JSON file
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.client = None
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # S3 bucket and key for GCP credentials from environment variables or defaults
        s3_bucket = os.environ.get('GCP_CREDENTIALS_S3_BUCKET', 'ndi-3supervision')
        s3_key = os.environ.get('GCP_CREDENTIALS_S3_KEY', 'MIT/GCPServiceKey/tosapi-bf0ac4918370.json')
        
        # Try to initialize BigQuery client with service account credentials from S3
        try:
            # Download credentials from S3
            logger.info(f"Downloading GCP credentials from S3 bucket: {s3_bucket}, key: {s3_key}")
            s3_client = boto3.client('s3')
            
            # Create a temporary file to store the credentials
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
                temp_credentials_path = temp_file.name
                
            # Download the credentials file from S3
            s3_client.download_file(s3_bucket, s3_key, temp_credentials_path)
            logger.info(f"GCP credentials downloaded to temporary file: {temp_credentials_path}")
            
            # Initialize BigQuery client with downloaded credentials
            credentials = service_account.Credentials.from_service_account_file(
                temp_credentials_path,
                scopes=["https://www.googleapis.com/auth/bigquery"]
            )
            self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
            logger.info(f"BigQuery client initialized with credentials from S3")
            
            # Clean up the temporary file
            os.unlink(temp_credentials_path)
            logger.info("Temporary credentials file removed")
            
        except Exception as e:
            logger.error(f"Error initializing BigQuery client from S3 credentials: {e}")
            
            # Fallback to credentials path if provided or environment variable
            if not credentials_path:
                credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            
            logger.warning(f"Falling back to credentials path: {credentials_path}")
            
            # Initialize BigQuery client with local credentials if available
            if credentials_path and os.path.exists(credentials_path):
                try:
                    credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=["https://www.googleapis.com/auth/bigquery"]
                    )
                    self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
                    logger.info(f"BigQuery client initialized with fallback credentials from file: {credentials_path}")
                except Exception as e:
                    logger.error(f"Error initializing BigQuery client from file: {e}")
                    logger.error("Please provide a valid service account credentials file.")
            else:
                logger.error(f"Credentials file not found at path: {credentials_path}")
    
    def _create_database_schema(self):
        """
        Create the SQLite database schema for patent data and family relationships
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create publications table for patent data
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
            
            # Create patent family relationship table
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
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_id ON publications (family_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_num ON publications (application_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assignee_harmonized ON publications (assignee_harmonized)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_country_code ON publications (country_code)')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_family_id ON patent_families (family_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_app_num ON patent_families (application_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_pub_num ON patent_families (publication_number)')
            
            conn.commit()
            conn.close()
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            raise
    
    def fetch_japanese_patents(self, limit: int = 5000):
        """
        Fetch Japanese patent publications from Google Patents Public Data
        
        Args:
            limit: Number of patent publications to fetch (approximate)
            
        Returns:
            int: Number of patents processed
        """
        if not self.client:
            logger.error("BigQuery client is not initialized")
            return 0
        
        try:
            # Create database schema first
            self._create_database_schema()
            
            # Use publication_date to get approximately the requested number
            # Note: Updated to use the latest BigQuery schema
            query = f"""
            SELECT
                publication_number,
                filing_date,
                publication_date,
                application_number,
                (SELECT STRING_AGG(name, '; ') FROM UNNEST(assignee_harmonized)) as assignee_harmonized,
                ARRAY_TO_STRING(assignee, '; ') as assignee_original,
                (SELECT STRING_AGG(text, ' ') FROM UNNEST(title_localized) WHERE language = 'ja') as title_ja,
                (SELECT STRING_AGG(text, ' ') FROM UNNEST(title_localized) WHERE language = 'en') as title_en,
                (SELECT STRING_AGG(text, ' ') FROM UNNEST(abstract_localized) WHERE language = 'ja') as abstract_ja,
                (SELECT STRING_AGG(text, ' ') FROM UNNEST(abstract_localized) WHERE language = 'en') as abstract_en,
                (SELECT STRING_AGG(text, ' ') FROM UNNEST(claims_localized) WHERE language = 'ja') as claims,
                (SELECT STRING_AGG(code, '; ') FROM UNNEST(ipc)) as ipc_code,
                family_id,
                country_code,
                kind_code,
                priority_date,
                grant_date,
                '' as priority_claim,
                '' as legal_status,
                '' as status
            FROM
                `patents-public-data.patents.publications`
            WHERE
                country_code = 'JP'
            ORDER BY
                publication_date DESC
            LIMIT
                {limit}
            """
            
            logger.info(f"Executing BigQuery query to fetch {limit} Japanese patents")
            query_job = self.client.query(query)
            
            # Process results in batches and insert into SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Counter for processed rows
            processed_rows = 0
            batch_size = 100
            current_batch = []
            
            logger.info("Processing query results...")
            for row in query_job:
                # Convert row to dictionary
                patent_data = dict(row.items())
                
                # Process the data - handle NoneType values
                for key, value in patent_data.items():
                    if value is None:
                        patent_data[key] = ""
                
                # Calculate family size using a separate query
                family_size = self._get_family_size(patent_data.get('family_id', ''))
                patent_data['family_size'] = family_size
                
                # Prepare insertion tuple
                insertion_tuple = (
                    patent_data.get('publication_number', ''),
                    patent_data.get('filing_date', ''),
                    patent_data.get('publication_date', ''),
                    patent_data.get('application_number', ''),
                    patent_data.get('assignee_harmonized', ''),
                    patent_data.get('assignee_original', ''),
                    patent_data.get('title_ja', ''),
                    patent_data.get('title_en', ''),
                    patent_data.get('abstract_ja', ''),
                    patent_data.get('abstract_en', ''),
                    patent_data.get('claims', ''),
                    patent_data.get('ipc_code', ''),
                    patent_data.get('family_id', ''),
                    patent_data.get('country_code', ''),
                    patent_data.get('kind_code', ''),
                    patent_data.get('priority_date', ''),
                    patent_data.get('grant_date', ''),
                    patent_data.get('priority_claim', ''),
                    patent_data.get('status', ''),
                    patent_data.get('legal_status', ''),
                    'true' if patent_data.get('examined') else 'false',
                    patent_data.get('family_size', 0)
                )
                
                current_batch.append(insertion_tuple)
                
                # Insert in batches for better performance
                if len(current_batch) >= batch_size:
                    cursor.executemany(
                        '''
                        INSERT OR REPLACE INTO publications
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        current_batch
                    )
                    conn.commit()
                    processed_rows += len(current_batch)
                    logger.info(f"Processed {processed_rows} patents")
                    current_batch = []
            
            # Insert remaining rows
            if current_batch:
                cursor.executemany(
                    '''
                    INSERT OR REPLACE INTO publications
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    current_batch
                )
                conn.commit()
                processed_rows += len(current_batch)
            
            logger.info(f"Total number of patents processed: {processed_rows}")
            conn.close()
            
            # Build the patent family relationships
            self._build_family_relationships()
            
            return processed_rows
        except Exception as e:
            logger.error(f"Error fetching Japanese patents: {e}")
            return 0
    
    def _get_family_size(self, family_id: str) -> int:
        """
        Get the size of a patent family by counting the number of patents with the same family_id
        
        Args:
            family_id: The family ID to query
            
        Returns:
            Size of the patent family
        """
        try:
            if not family_id:
                return 0
            
            # Use a local estimate instead of potentially expensive BigQuery count query
            # In a production environment, we might cache this calculation
            try:
                # Try local calculation first if we already have some data
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM publications WHERE family_id = ?", 
                    (family_id,)
                )
                local_count = cursor.fetchone()[0]
                conn.close()
                
                if local_count > 0:
                    # We already have some family members in the database
                    return local_count
            except Exception as local_err:
                # If local calculation fails, log and continue with BigQuery
                logger.warning(f"Local family size calculation failed: {local_err}")
                
            # Fall back to BigQuery query
            query = f"""
            SELECT
                COUNT(*) as family_size
            FROM
                `patents-public-data.patents.publications`
            WHERE
                family_id = '{family_id}'
            """
            
            query_job = self.client.query(query)
            results = list(query_job)
            
            if results:
                return results[0].get('family_size', 0)
            return 0
        except Exception as e:
            logger.error(f"Error getting family size: {e}")
            # Return a default value if we can't determine the family size
            return 1  # Assume at least this patent is in the family
    
    def _build_family_relationships(self):
        """
        Build patent family relationships datamart from the publications table
        Using family_id as the grouping key
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, truncate the patent_families table to avoid duplicates
            cursor.execute("DELETE FROM patent_families")
            conn.commit()
            logger.info("Cleared existing family relationships")
            
            # Get all patents with family_ids and application_numbers for building relationships
            cursor.execute('''
            SELECT
                family_id,
                application_number,
                publication_number,
                country_code
            FROM
                publications
            WHERE
                family_id != '' AND application_number != ''
            ''')
            
            # Insert all family relationships at once
            family_data = cursor.fetchall()
            
            if family_data:
                # Insert all relationship records
                cursor.executemany(
                    '''
                    INSERT OR IGNORE INTO patent_families
                    (family_id, application_number, publication_number, country_code)
                    VALUES (?, ?, ?, ?)
                    ''',
                    family_data
                )
                conn.commit()
                
                # Get unique family count
                cursor.execute("SELECT COUNT(DISTINCT family_id) FROM patent_families")
                family_count = cursor.fetchone()[0]
                
                # Get total relationship count
                cursor.execute("SELECT COUNT(*) FROM patent_families")
                relationship_count = cursor.fetchone()[0]
                
                logger.info(f"Built family relationships for {relationship_count} patents across {family_count} families")
            else:
                logger.warning("No family relationships found to build")
            
            conn.close()
        except Exception as e:
            logger.error(f"Error building family relationships: {e}")
            raise

def download_inpit_data():
    """
    Download the INPIT bulk data file from S3 bucket.
    """
    return download_from_s3(S3_BUCKET, S3_PATH, LOCAL_FILE_PATH, "INPIT CSV data")

def download_google_patents_db():
    """
    Download the Google Patents database from S3 bucket.
    """
    # Create directory structure if it doesn't exist
    os.makedirs(os.path.dirname(GOOGLE_PATENTS_S3_DB_PATH), exist_ok=True)
    
    # Remove any existing database files to ensure a fresh download
    if os.path.exists(GOOGLE_PATENTS_S3_DB_PATH):
        logger.info(f"Removing existing S3 database file: {GOOGLE_PATENTS_S3_DB_PATH}")
        os.remove(GOOGLE_PATENTS_S3_DB_PATH)
    
    # Download the database
    success = download_from_s3(
        S3_BUCKET_PATENTS,
        S3_KEY_PATENTS,
        GOOGLE_PATENTS_S3_DB_PATH, 
        "Google Patents database"
    )
    
    if not success:
        # If download fails, create an empty database
        logger.warning("Creating fallback empty Google Patents database")
        create_empty_db(GOOGLE_PATENTS_S3_DB_PATH)
    
    # Make a copy for GCP path
    if os.path.exists(GOOGLE_PATENTS_GCP_DB_PATH):
        os.remove(GOOGLE_PATENTS_GCP_DB_PATH)
    
    if success:
        try:
            logger.info(f"Creating copy for GCP database path: {GOOGLE_PATENTS_GCP_DB_PATH}")
            import shutil
            shutil.copy2(GOOGLE_PATENTS_S3_DB_PATH, GOOGLE_PATENTS_GCP_DB_PATH)
            os.chmod(GOOGLE_PATENTS_GCP_DB_PATH, 0o666)
            logger.info("Google Patents GCP database copy created")
        except Exception as e:
            logger.error(f"Error creating Google Patents GCP database copy: {e}")
            success = False
    
    return success

def create_google_patents_gcp_db():
    """
    Create Google Patents GCP database by fetching data from BigQuery.
    """
    logger.info("Creating/Refreshing GCP database from BigQuery...")
    
    # Remove any existing database file to ensure a fresh start
    if os.path.exists(GOOGLE_PATENTS_GCP_DB_PATH):
        logger.info(f"Removing existing GCP database file: {GOOGLE_PATENTS_GCP_DB_PATH}")
        os.remove(GOOGLE_PATENTS_GCP_DB_PATH)
    
    # Import data from BigQuery (GCP credentials will be downloaded from S3)
    logger.info("Importing patent data from BigQuery...")
    
    # Create the fetcher and import data
    fetcher = GooglePatentsFetcher(db_path=GOOGLE_PATENTS_GCP_DB_PATH)
    count = fetcher.fetch_japanese_patents(limit=5000)
    
    if count > 0:
        logger.info(f"Successfully imported {count} patents from BigQuery")
        return True
    else:
        logger.error("Failed to import patent data from BigQuery")
        return False

if __name__ == "__main__":
    # Download INPIT data
    inpit_success = download_inpit_data()
    
    # Download Google Patents S3 database
    s3_patents_success = download_google_patents_db()
    
    # Create Google Patents GCP database from BigQuery
    gcp_patents_success = create_google_patents_gcp_db()
    
    if not inpit_success:
        logger.error("Failed to download INPIT data from S3.")
    
    if not s3_patents_success:
        logger.error("Failed to download Google Patents database from S3.")
    
    if not gcp_patents_success:
        logger.error("Failed to create Google Patents GCP database from BigQuery.")
        
    # If all downloads failed, exit with error
    if not inpit_success and not s3_patents_success and not gcp_patents_success:
        import sys
        sys.exit(1)
    else:
        logger.info("Data download completed. Ready for importing.")
