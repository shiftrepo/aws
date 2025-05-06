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
    
    def __init__(self, credentials_path: str = None, db_path: str = "/app/data/google_patents.db"):
        """
        Initialize the Google Patents fetcher
        
        Args:
            credentials_path: Path to Google Cloud service account credentials JSON file
            db_path: Path to the SQLite database file
        """
        self.credentials_path = credentials_path
        self.db_path = db_path
        self.client = None
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize BigQuery client if credentials are provided
        if credentials_path and os.path.exists(credentials_path):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=["https://www.googleapis.com/auth/bigquery"]
                )
                self.client = bigquery.Client(credentials=credentials, project=credentials.project_id)
                logger.info("BigQuery client initialized with credentials")
            except Exception as e:
                logger.error(f"Error initializing BigQuery client: {e}")
        else:
            try:
                # Try to use application default credentials
                self.client = bigquery.Client()
                logger.info("BigQuery client initialized with application default credentials")
            except Exception as e:
                logger.error(f"Error initializing BigQuery client: {e}")
    
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
        
        try:
            # Create database schema first
            self._create_database_schema()
            
            # Use publication_date to get approximately the requested number
            query = f"""
            SELECT
                p.publication_number,
                p.filing_date,
                p.publication_date,
                p.application_number,
                ARRAY_TO_STRING(p.assignee_harmonized, '; ') as assignee_harmonized,
                ARRAY_TO_STRING(p.assignee, '; ') as assignee_original,
                ARRAY_TO_STRING(p.title_localized.ja, ' ') as title_ja,
                ARRAY_TO_STRING(p.title_localized.en, ' ') as title_en,
                ARRAY_TO_STRING(p.abstract_localized.ja, ' ') as abstract_ja,
                ARRAY_TO_STRING(p.abstract_localized.en, ' ') as abstract_en,
                ARRAY_TO_STRING(p.claims_localized.ja, ' ') as claims,
                ARRAY_TO_STRING(p.ipc, '; ') as ipc_code,
                p.family_id,
                p.country_code,
                p.kind_code,
                p.priority_date,
                p.grant_date,
                ARRAY_TO_STRING(p.priority_claim, '; ') as priority_claim,
                p.legal_status,
                f.status
            FROM
                `patents-public-data.patents.publications` p
            LEFT JOIN
                `patents-public-data.patents.families` f
            ON
                p.family_id = f.family_id
            WHERE
                p.country_code = 'JP'
            ORDER BY
                p.publication_date DESC
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
        Get the size of a patent family
        
        Args:
            family_id: The family ID to query
            
        Returns:
            Size of the patent family
        """
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
            logger.error(f"Error getting family size: {e}")
            return 0
    
    def _build_family_relationships(self):
        """
        Build patent family relationships datamart from the publications table
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all family_ids and their related application numbers
            cursor.execute('''
            SELECT
                family_id,
                application_number,
                publication_number,
                country_code
            FROM
                publications
            WHERE
                family_id != ''
            ''')
            
            rows = cursor.fetchall()
            
            # Group by family_id and insert into the relationships table
            insert_data = []
            for row in rows:
                family_id, application_number, publication_number, country_code = row
                if family_id and application_number:
                    insert_data.append((family_id, application_number, publication_number, country_code))
            
            # Insert family relationships in batches
            cursor.executemany(
                '''
                INSERT OR IGNORE INTO patent_families
                (family_id, application_number, publication_number, country_code)
                VALUES (?, ?, ?, ?)
                ''',
                insert_data
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Built family relationships for {len(insert_data)} patents")
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
