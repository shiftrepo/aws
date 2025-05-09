#!/usr/bin/env python3
"""
Create SQLite schema and import data from CSV file.
"""

import os
import sqlite3
import pandas as pd
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, MetaData, Table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File paths
CSV_FILE_PATH = "/app/data/plidb_bulkdata_202503.csv"
DB_PATH = "/app/data/inpit.db"

def create_schema_and_import():
    """
    Create database schema and import data from CSV.
    """
    try:
        # Print current user information
        logger.info(f"Running schema import as user {os.getuid()}:{os.getgid()}")

        # Create SQLite database directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            
        # Create SQLite database engine
        engine = create_engine(f"sqlite:///{DB_PATH}")
        metadata = MetaData()
        
        # Check if CSV file exists
        if not os.path.exists(CSV_FILE_PATH):
            logger.warning(f"CSV file not found: {CSV_FILE_PATH}")
            logger.info("Creating basic schema without CSV data")
            
            # Create a basic schema with default columns
            table_name = 'inpit_data'
            columns = []
            columns.append(Column('id', Integer, primary_key=True))
            
            # Add some standard columns for patent data
            default_columns = [
                'application_number', 'publication_number', 'applicant_name', 
                'inventor_name', 'title', 'abstract', 'filing_date', 'publication_date',
                'legal_status', 'ipc_code', 'family_id'
            ]
            
            # Create column mapping for reference
            column_mapping = {}
            for col in default_columns:
                clean_col_name = col
                column_mapping[clean_col_name] = col
                columns.append(Column(clean_col_name, Text))
            
            # Save column mapping to file for reference by app.py
            import json
            with open('/app/data/column_mapping.json', 'w') as f:
                json.dump(column_mapping, f)
            
            # Create table
            table = Table(table_name, metadata, *columns)
            metadata.create_all(engine)
            
            # Create indexes for better query performance
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Add indexes for important columns
            for col in default_columns[:5]:  # Create indexes for first 5 columns
                try:
                    cursor.execute(f"CREATE INDEX idx_{col} ON {table_name} ({col})")
                except Exception as e:
                    logger.warning(f"Could not create index for {col}: {e}")
                    
            conn.commit()
            conn.close()
            
            logger.info("Basic schema created successfully")
            return True
            
        # Log file permissions
        import stat
        try:
            file_stat = os.stat(CSV_FILE_PATH)
            logger.info(f"CSV file permissions: {oct(stat.S_IMODE(file_stat.st_mode))}")
            logger.info(f"CSV file owner: {file_stat.st_uid}:{file_stat.st_gid}")
        except Exception as e:
            logger.warning(f"Could not get CSV file permissions: {e}")
        
        # Read first few rows to automatically determine columns
        logger.info(f"Reading CSV file header: {CSV_FILE_PATH}")
        try:
            df_sample = pd.read_csv(CSV_FILE_PATH, nrows=5, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            logger.info("Falling back to basic schema creation")
            return create_schema_and_import()  # Recursive call that will hit the "file not found" branch
        
        # Create table dynamically based on CSV columns
        logger.info("Creating database schema")
        table_name = 'inpit_data'
        
        columns = []
        columns.append(Column('id', Integer, primary_key=True))
        
        # Add columns based on CSV headers - preserve original column names
        column_mapping = {}
        for col in df_sample.columns:
            col_name = col.strip()
            # Create a SQL-friendly column name but preserve mapping to original name
            clean_col_name = ''.join(e if e.isalnum() else '_' for e in col_name)
            column_mapping[clean_col_name] = col_name
            columns.append(Column(clean_col_name, Text))
            
        # Save column mapping to file for reference by app.py
        import json
        with open('/app/data/column_mapping.json', 'w') as f:
            json.dump(column_mapping, f)
        
        # Create table
        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)
        
        logger.info(f"Importing data from CSV into SQLite")
        
        # Process the CSV file in chunks to handle large files efficiently
        logger.info("Loading all data from CSV file")
        
        # Use chunksize for memory-efficient processing of large files
        chunksize = 10000
        total_rows = 0
        
        for chunk_df in pd.read_csv(CSV_FILE_PATH, encoding='utf-8', chunksize=chunksize):
            # Clean column names
            chunk_df.columns = [''.join(e if e.isalnum() else '_' for e in col.strip()) for col in chunk_df.columns]
            # Insert into database
            chunk_df.to_sql(table_name, engine, if_exists='append' if total_rows > 0 else 'replace', index=False)
            total_rows += len(chunk_df)
            logger.info(f"Processed {total_rows} rows so far")
        
        logger.info("Schema created and data imported successfully")
        
        # Create indexes for better query performance
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Add indexes for important columns
        logger.info("Creating database indexes")
        important_cols = ["applicant_name", "inventor_name", "title", "abstract"]
        
        for col in df_sample.columns:
            col_name = col.strip()
            clean_col_name = ''.join(e if e.isalnum() else '_' for e in col_name)
            # Create indexes for important columns and first few columns
            if clean_col_name.lower() in important_cols or col in df_sample.columns[:5]:
                try:
                    cursor.execute(f"CREATE INDEX idx_{clean_col_name} ON {table_name} ({clean_col_name})")
                except Exception as e:
                    logger.warning(f"Could not create index for {clean_col_name}: {e}")
                
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error creating schema and importing data: {e}")
        return False

if __name__ == "__main__":
    create_schema_and_import()
