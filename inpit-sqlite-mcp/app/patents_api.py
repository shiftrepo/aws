#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI endpoints for Google Patents Public Data and Natural Language Processing

This module provides FastAPI routes for accessing Google Patents data and
processing natural language queries against the patent database.
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from google_patents_fetcher import GooglePatentsFetcher
from nl_query_processor import PatentNLQueryProcessor

router = APIRouter(prefix="/patents", tags=["Patents"])

# Path to Google Patents database
DB_PATH = "/app/data/google_patents.db"

# Initialize processors
patent_fetcher = GooglePatentsFetcher(db_path=DB_PATH)
nl_processor = PatentNLQueryProcessor(db_path=DB_PATH)

# Define models for request/response
class NLQueryRequest(BaseModel):
    query: str

class ImportRequest(BaseModel):
    limit: int = 10000
    credentials_path: Optional[str] = None

class NLQueryResponse(BaseModel):
    success: bool
    natural_language_query: str
    sql_query: Optional[str] = None
    count: int = 0
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None

class ImportResponse(BaseModel):
    success: bool
    count: int = 0
    message: str
    error: Optional[str] = None

class FamilyResponse(BaseModel):
    success: bool
    application_number: str
    family_members: List[Dict[str, Any]] = []
    count: int = 0
    error: Optional[str] = None

@router.post("/query", response_model=NLQueryResponse)
async def query_patents(request: NLQueryRequest):
    """
    Process a natural language query against the patents database.
    """
    try:
        result = nl_processor.process_and_execute(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/query/{query_text}", response_model=NLQueryResponse)
async def get_query_patents(query_text: str):
    """
    Process a natural language query against the patents database (GET method).
    """
    try:
        result = nl_processor.process_and_execute(query_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/import", response_model=ImportResponse)
async def import_patents(request: ImportRequest):
    """
    Import Japanese patents from Google Patents Public Data.
    """
    try:
        # Set Google application credentials if provided
        if request.credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = request.credentials_path
        
        # Import patents
        count = patent_fetcher.fetch_japanese_patents(limit=request.limit)
        
        if count > 0:
            return {
                "success": True,
                "count": count,
                "message": f"Successfully imported {count} Japanese patents"
            }
        else:
            return {
                "success": False,
                "count": 0,
                "message": "Failed to import patents",
                "error": "No patents were imported. Check logs for details."
            }
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "message": "Error importing patents",
            "error": str(e)
        }

@router.get("/family/{application_number}", response_model=FamilyResponse)
async def get_family_members(application_number: str):
    """
    Get all family members for a given application number.
    """
    try:
        family_members = patent_fetcher.get_family_members(application_number)
        
        return {
            "success": True,
            "application_number": application_number,
            "family_members": family_members,
            "count": len(family_members)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching family members: {str(e)}")

@router.get("/status")
async def get_patent_status():
    """
    Check the status of the patents database and return basic statistics.
    """
    try:
        import sqlite3
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the database exists and has tables
        try:
            cursor.execute("SELECT COUNT(*) FROM publications")
            publication_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM patent_families")
            family_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT family_id) FROM patent_families")
            unique_families = cursor.fetchone()[0]
            
            # Get most recent publication date
            cursor.execute("SELECT MAX(publication_date) FROM publications")
            latest_publication = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "available",
                "publication_count": publication_count,
                "family_count": family_count,
                "unique_families": unique_families,
                "latest_publication": latest_publication
            }
        except sqlite3.OperationalError:
            conn.close()
            return {
                "status": "empty",
                "message": "Patent database exists but no tables found or tables are empty"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking database status: {str(e)}"
        }
