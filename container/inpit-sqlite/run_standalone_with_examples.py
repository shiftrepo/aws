#!/usr/bin/env python3
"""
Standalone version of the SQLite web interface with SQL examples page.
This version includes SQL examples functionality missing from the original standalone version.
"""

import os
import sqlite3
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory

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

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load column mapping if exists
column_mapping = {}
mapping_path = 'data/column_mapping.json'
if os.path.exists(mapping_path):
    try:
        with open(mapping_path, 'r') as f:
            column_mapping = json.load(f)
    except Exception as e:
        logger.error(f"Error loading column mapping: {e}")

@app.route('/')
def index():
    """
    Redirect to info page.
    """
    return redirect('/examples')

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
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; text-decoration: none; padding: 5px 10px; background-color: #f0f0f0; border-radius: 3px; }
            .nav a:hover { background-color: #e0e0e0; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/info">Database Info</a>
            <a href="/examples">SQL Examples</a>
        </div>
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

@app.route('/examples')
def examples():
    """Render the SQL examples page"""
    return render_template('standalone_sql_examples.html', 
                          db_type='inpit', 
                          db_title='INPIT SQLite',
                          db_file=INPIT_DB_PATH)

@app.route('/gcp_examples')
def gcp_examples():
    """Render the Google Patents GCP examples page"""
    return render_template('standalone_sql_examples.html', 
                          db_type='google_patents_gcp', 
                          db_title='Google Patents GCP',
                          db_file=GOOGLE_PATENTS_GCP_DB_PATH)

@app.route('/s3_examples')
def s3_examples():
    """Render the Google Patents S3 examples page"""
    return render_template('standalone_sql_examples.html', 
                          db_type='google_patents_s3', 
                          db_title='Google Patents S3',
                          db_file=GOOGLE_PATENTS_S3_DB_PATH)

@app.route('/inpit_examples/query', methods=['POST'])
def query_inpit():
    """Execute a SQL query on inpit database and return results."""
    sql_query = request.form.get('query', '')
    db_path = INPIT_DB_PATH
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Check if query returns data
        if sql_query.strip().lower().startswith(('select', 'pragma', 'explain')):
            columns = [description[0] for description in cursor.description]
            
            # Map DB column names to original CSV headers if possible
            display_columns = []
            for col in columns:
                display_columns.append(column_mapping.get(col, col))
                
            results = cursor.fetchall()
            conn.close()
            return jsonify({
                "success": True,
                "columns": display_columns,
                "results": results
            })
        else:
            # For non-SELECT queries
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return jsonify({
                "success": True,
                "message": f"Query executed successfully. {affected_rows} rows affected."
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/google_patents_gcp_examples/query', methods=['POST'])
def query_gcp():
    """Execute a SQL query on Google Patents GCP database and return results."""
    sql_query = request.form.get('query', '')
    db_path = GOOGLE_PATENTS_GCP_DB_PATH
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Check if query returns data
        if sql_query.strip().lower().startswith(('select', 'pragma', 'explain')):
            columns = [description[0] for description in cursor.description]
            
            # Map DB column names to original CSV headers if possible
            display_columns = []
            for col in columns:
                display_columns.append(column_mapping.get(col, col))
                
            results = cursor.fetchall()
            conn.close()
            return jsonify({
                "success": True,
                "columns": display_columns,
                "results": results
            })
        else:
            # For non-SELECT queries
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return jsonify({
                "success": True,
                "message": f"Query executed successfully. {affected_rows} rows affected."
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/google_patents_s3_examples/query', methods=['POST'])
def query_s3():
    """Execute a SQL query on Google Patents S3 database and return results."""
    sql_query = request.form.get('query', '')
    db_path = GOOGLE_PATENTS_S3_DB_PATH
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Check if query returns data
        if sql_query.strip().lower().startswith(('select', 'pragma', 'explain')):
            columns = [description[0] for description in cursor.description]
            
            # Map DB column names to original CSV headers if possible
            display_columns = []
            for col in columns:
                display_columns.append(column_mapping.get(col, col))
                
            results = cursor.fetchall()
            conn.close()
            return jsonify({
                "success": True,
                "columns": display_columns,
                "results": results
            })
        else:
            # For non-SELECT queries
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return jsonify({
                "success": True,
                "message": f"Query executed successfully. {affected_rows} rows affected."
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("Starting standalone SQLite Web UI with SQL examples...")
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
    
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
