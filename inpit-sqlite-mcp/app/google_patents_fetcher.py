#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Patents Public Data Fetcher

This module fetches Japanese patent publication data from Google Patents Public Data
and stores it in a SQLite database along with family relationship information.
"""

import os
import json
import sqlite3
import logging
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import time
import tempfile
import boto3
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GooglePatentsFetcher:
    """Class to fetch and process Google Patents Public Data"""
    
    def __init__(self, credentials_path: str = None, db_path: str = "/app/data/db/google_patents_gcp.db"):
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
    
    def fetch_japanese_patents(self, limit: int = 10000):
        """
        Fetch Japanese patent publications from Google Patents Public Data
        
        Args:
            limit: Number of patent publications to fetch (approximate)
        """
        if not self.client:
            logger.error("BigQuery client is not initialized")
            return False
        
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
        
        # Implement retry logic for BigQuery fetch
        max_retries = 5
        retry_count = 0
        retry_delay = 2  # Start with 2 seconds
        
        while retry_count < max_retries:
            try:
                logger.info(f"Executing BigQuery query to fetch {limit} Japanese patents (attempt {retry_count+1}/{max_retries})")
                query_job = self.client.query(query)
                break
            except Exception as e:
                retry_count += 1
                if "quota exceeded" in str(e).lower() and retry_count < max_retries:
                    logger.warning(f"Quota exceeded error on retry {retry_count}/{max_retries}. Waiting {retry_delay} seconds before retrying...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    if retry_count >= max_retries:
                        logger.error(f"Maximum retries ({max_retries}) reached. Error executing BigQuery: {e}")
                        logger.info("Falling back to downloading pre-built DB files from S3")
                        
                        # Download DB files from S3 when all retries fail
                        success = self._download_s3_db_files()
                        if success:
                            logger.info("Successfully downloaded DB files from S3. Skipping BigQuery import.")
                            return 0  # Signal that we skipped BigQuery but downloaded files
                        else:
                            logger.error("Failed to download DB files from S3 after BigQuery failure")
                            return False
                    else:
                        logger.error(f"Error executing BigQuery on retry {retry_count}: {e}")
                        
        # If we got here, either the query was successful or all retries failed
        try:
            
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
    
    def _download_s3_db_files(self):
        """
        Download DB files from S3 bucket when BigQuery operations fail.
        """
        try:
            s3_client = boto3.client('s3')
            bucket_name = 'ndi-3supervision'
            
            # Define source and destination paths
            s3_files = [
                {'key': 'MIT/demo/GCP/google_patents_gcp.db', 'dest': '/app/data/db/google_patents_gcp.db'},
                {'key': 'MIT/demo/GCP/google_patents_s3.db', 'dest': '/app/data/db/google_patents_s3.db'}
            ]
            
            for file_info in s3_files:
                logger.info(f"Downloading {file_info['key']} from S3 to {file_info['dest']}...")
                # Make sure target directory exists
                os.makedirs(os.path.dirname(file_info['dest']), exist_ok=True)
                
                s3_client.download_file(bucket_name, file_info['key'], file_info['dest'])
                logger.info(f"Successfully downloaded {file_info['key']} to {file_info['dest']}")
                
                # Verify file was downloaded correctly
                if os.path.exists(file_info['dest']):
                    file_size = os.path.getsize(file_info['dest'])
                    logger.info(f"Downloaded file size: {file_size} bytes")
                else:
                    logger.error(f"Downloaded file not found at {file_info['dest']}")
            
            return True
        except Exception as e:
            logger.error(f"Error downloading DB files from S3: {e}")
            return False

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
            
            # Fall back to BigQuery query with retry logic
            max_retries = 5
            retry_count = 0
            retry_delay = 2  # Start with 2 seconds delay
            
            while retry_count < max_retries:
                try:
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
                    retry_count += 1
                    if "quota exceeded" in str(e).lower() and retry_count < max_retries:
                        logger.warning(f"Quota exceeded error on retry {retry_count}/{max_retries}. Waiting {retry_delay} seconds before retrying...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        if retry_count >= max_retries:
                            logger.error(f"Maximum retries ({max_retries}) reached. Error getting family size: {e}")
                        else:
                            logger.error(f"Error getting family size on retry {retry_count}: {e}")
                        break
            
            # Return a default value if we can't determine the family size after retries
            return 1  # Assume at least this patent is in the family
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
    
    def get_family_members(self, application_number: str) -> List[Dict[str, Any]]:
        """
        Get all family members for a given application number
        
        Args:
            application_number: The application number to find family for
            
        Returns:
            List of related patents in the same family
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # First get the family_id for this application number
            cursor.execute('''
            SELECT family_id FROM patent_families WHERE application_number = ?
            ''', (application_number,))
            
            result = cursor.fetchone()
            if not result:
                return []
            
            family_id = result['family_id']
            
            # Get all patents in this family
            cursor.execute('''
            SELECT p.*
            FROM publications p
            JOIN patent_families f ON p.publication_number = f.publication_number
            WHERE f.family_id = ?
            ''', (family_id,))
            
            family_members = []
            for row in cursor.fetchall():
                # Convert sqlite row to dict
                family_member = dict(zip([column[0] for column in cursor.description], row))
                family_members.append(family_member)
            
            conn.close()
            return family_members
        except Exception as e:
            logger.error(f"Error getting family members: {e}")
            return []


if __name__ == "__main__":
    # Example usage
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    fetcher = GooglePatentsFetcher(credentials_path=credentials_path)
    num_patents = fetcher.fetch_japanese_patents(limit=10000)
    print(f"Fetched {num_patents} Japanese patents")
