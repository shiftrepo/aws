#!/usr/bin/env python3
"""
Standalone version of the SQLite web interface with minimal dependencies.
This version skips all data download operations and uses existing database files.
"""

import os
import sqlite3
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database file paths
INPIT_DB_PATH = "data/inpit.db"
GOOGLE_PATENTS_DB_PATH = "data/google_patents.db"
GOOGLE_PATENTS_GCP_DB_PATH = "data/google_patents_gcp.db"
GOOGLE_PATENTS_S3_DB_PATH = "data/google_patents_s3.db"

# Default database path
DB_PATH = INPIT_DB_PATH
DB_URI = f"sqlite:///{DB_PATH}"

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """
    Redirect to admin interface.
    """
    return "Inpit SQLite Database Web Interface is running! This is a minimal standalone version."

@app.route('/tables')
def tables():
    """
    Return the list of tables in the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"tables": tables})
    except Exception as e:
        logger.error(f"Error accessing tables: {e}")
        return jsonify({"error": f"Error accessing database: {str(e)}"})

@app.route('/health')
def health():
    """
    Check if the database is accessible.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        return jsonify({"status": "healthy", "message": "Database is accessible."})
    except Exception as e:
        return jsonify({"status": "unhealthy", "message": str(e)}), 500

@app.route('/info')
def info():
    """Display info about existing database files"""
    db_info = {}
    
    for name, path in [
        ("INPIT", INPIT_DB_PATH),
        ("Google Patents (Legacy)", GOOGLE_PATENTS_DB_PATH),
        ("Google Patents (GCP)", GOOGLE_PATENTS_GCP_DB_PATH),
        ("Google Patents (S3)", GOOGLE_PATENTS_S3_DB_PATH)
    ]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                # Try to get one table's row count
                tables = []
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                table_result = cursor.fetchone()
                if table_result:
                    table_name = table_result[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    tables.append({"name": table_name, "rows": row_count})
                
                conn.close()
                status = "Available"
            except Exception as e:
                status = f"Error: {e}"
                table_count = "Unknown"
                tables = []
            
            db_info[name] = {
                "path": path,
                "size": f"{size / (1024 * 1024):.2f} MB",
                "status": status,
                "tables": table_count,
                "sample_tables": tables
            }
        else:
            db_info[name] = {"path": path, "status": "File not found"}
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Information</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .db-info { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .available { background-color: #eeffee; }
            .missing { background-color: #ffeeee; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 5px; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Database Information</h1>
    """
    
    for name, info in db_info.items():
        css_class = "available" if info.get("status") == "Available" else "missing"
        html += f'<div class="db-info {css_class}"><h2>{name}</h2>'
        html += f'<p>Path: {info.get("path")}</p>'
        html += f'<p>Status: {info.get("status")}</p>'
        
        if "size" in info:
            html += f'<p>Size: {info.get("size")}</p>'
            html += f'<p>Tables: {info.get("tables")}</p>'
            
            if info.get("sample_tables"):
                html += "<p>Sample table row counts:</p><ul>"
                for table in info.get("sample_tables"):
                    html += f'<li>{table["name"]}: {table["rows"]} rows</li>'
                html += "</ul>"
        
        html += '</div>'
    
    html += """
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("Starting standalone SQLite Web UI...")
    print(f"Database paths:")
    print(f"- Inpit Database: {INPIT_DB_PATH}")
    print(f"- GCP Database: {GOOGLE_PATENTS_GCP_DB_PATH}")
    print(f"- S3 Local Database: {GOOGLE_PATENTS_S3_DB_PATH}")
    
    # Check for existence of database files
    for db_path in [INPIT_DB_PATH, GOOGLE_PATENTS_GCP_DB_PATH, GOOGLE_PATENTS_S3_DB_PATH]:
        db_exists = os.path.exists(db_path)
        if db_exists:
            print(f"Database exists: {db_path}")
        else:
            print(f"Database does not exist: {db_path}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
