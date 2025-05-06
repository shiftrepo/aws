#!/usr/bin/env python3
"""
Download bulk data from S3 bucket or create mock data for testing.
"""

import os
import boto3
import logging
import csv
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 bucket details
S3_BUCKET = "ndi-3supervision"
S3_PATH = "MIT/sample/plidb_bulkdata_202503.csv"
LOCAL_FILE_PATH = "/app/data/plidb_bulkdata_202503.csv"

def download_from_s3():
    """
    Download the bulk data file from S3 bucket.
    """
    logger.info(f"Attempting to download file from s3://{S3_BUCKET}/{S3_PATH} to {LOCAL_FILE_PATH}")
    
    try:
        # Print current user information
        logger.info(f"Running download as user {os.getuid()}:{os.getgid()}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Ensure directory exists with proper permissions
        data_dir = os.path.dirname(LOCAL_FILE_PATH)
        os.makedirs(data_dir, exist_ok=True)
        
        # Use a temporary file first to avoid permission issues
        tmp_file = f"{LOCAL_FILE_PATH}.download"
        
        # Download file to temporary location
        s3_client.download_file(S3_BUCKET, S3_PATH, tmp_file)
        
        # Make the file readable and writable by everyone
        try:
            os.chmod(tmp_file, 0o666)
        except Exception as e:
            logger.warning(f"Could not set permissions on downloaded file: {e}")
        
        # Move to final location
        import shutil
        shutil.move(tmp_file, LOCAL_FILE_PATH)
        
        # Final permission check
        try:
            os.chmod(LOCAL_FILE_PATH, 0o666)
        except Exception as e:
            logger.warning(f"Could not set final permissions: {e}")
        
        logger.info("File downloaded successfully from S3")
        return True
    except Exception as e:
        logger.error(f"Error downloading file from S3: {e}")
        logger.error("S3 download failed. Sample data processing is disabled.")
        return False

# Mock data creation has been removed as per requirements

if __name__ == "__main__":
    success = download_from_s3()
    if not success:
        logger.error("Failed to download data from S3. Exiting.")
        import sys
        sys.exit(1)
    else:
        logger.info("Data downloaded successfully. Ready for importing.")
