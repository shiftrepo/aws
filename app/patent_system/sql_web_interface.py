#!/usr/bin/env python3
"""
Web Interface for SQL Queries on Patent System Database

This script provides a web interface for executing SQL queries against the patent system SQLite database.
"""

import os
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from datetime import datetime

# Get database path from environment variables or use default
DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "patents.db")
)

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Patent System SQL Query Tool</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        h2 {
            color: #555;
            margin-top: 20px;
        }
        .query-form {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            font-family: monospace;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
            resize: vertical;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 20px;
            overflow-x: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .error {
            color: #ff0000;
            background-color: #ffe6e6;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .examples {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f7ff;
            border-radius: 5px;
        }
        .example-query {
            font-family: monospace;
            background-color: #eef;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .example-query:hover {
            background-color: #ddf;
        }
        .schema-section {
            margin-top: 20px;
            background-color: #f9fff9;
            padding: 15px;
            border-radius: 5px;
        }
        .schema-container {
            margin-top: 10px;
            font-family: monospace;
            white-space: pre-wrap;
            background-color: #eeffee;
            padding: 10px;
            border-radius: 4px;
            max-height: 300px;
            overflow-y: auto;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 15px;
            transition: 0.3s;
            font-size: 16px;
            color: #333;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 15px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
            animation: fadeEffect 1s;
        }
        @keyframes fadeEffect {
            from {opacity: 0;}
            to {opacity: 1;}
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Patent System SQL Query Tool</h1>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'QueryTab')">Query</button>
            <button class="tablinks" onclick="openTab(event, 'SchemaTab')">Schema</button>
            <button class="tablinks" onclick="openTab(event, 'ExamplesTab')">Examples</button>
            <button class="tablinks" onclick="openTab(event, 'HelpTab')">Help</button>
        </div>
        
        <div id="QueryTab" class="tabcontent" style="display: block;">
            <div class="query-form">
                <h2>Enter SQL Query</h2>
                <form id="queryForm" method="post" action="/query">
                    <textarea id="query" name="query" placeholder="Enter your SQL query here...">{{ query }}</textarea>
                    <button type="submit">Execute Query</button>
                </form>
            </div>
            
            {% if error %}
            <div class="error">
                <strong>Error:</strong> {{ error }}
            </div>
            {% endif %}
            
            {% if results %}
            <div class="results">
                <h2>Query Results</h2>
                <p><strong>Execution time:</strong> {{ execution_time }} seconds</p>
                <p><strong>Rows returned:</strong> {{ row_count }}</p>
                {% if row_count > 0 %}
                <table>
                    <tr>
                        {% for column in columns %}
                        <th>{{ column }}</th>
                        {% endfor %}
                    </tr>
                    {% for row in results %}
                    <tr>
                        {% for cell in row %}
                        <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <div id="SchemaTab" class="tabcontent">
            <div class="schema-section">
                <h2>Database Schema</h2>
                <p>Below is the schema of the main tables in the patent database:</p>
                
                {% for table_name, schema in schemas.items() %}
                <h3>{{ table_name }}</h3>
                <div class="schema-container">{{ schema }}</div>
                {% endfor %}
            </div>
        </div>
        
        <div id="ExamplesTab" class="tabcontent">
            <div class="examples">
                <h2>Example Queries</h2>
                <p>Click on any example to load it into the query editor:</p>
                
                <h3>Basic Queries</h3>
                <div class="example-query" onclick="setQueryText('SELECT * FROM patents LIMIT 10;')">
                    SELECT * FROM patents LIMIT 10;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT COUNT(*) AS patent_count FROM patents;')">
                    SELECT COUNT(*) AS patent_count FROM patents;
                </div>
                
                <h3>Patent Search Queries</h3>
                <div class="example-query" onclick="setQueryText('SELECT p.id, p.title, p.publication_number, p.application_date, a.name as applicant_name\\nFROM patents p\\nJOIN applicants a ON p.id = a.patent_id\\nLIMIT 20;')">
                    -- Patents with applicant names
                    SELECT p.id, p.title, p.publication_number, p.application_date, a.name as applicant_name
                    FROM patents p
                    JOIN applicants a ON p.id = a.patent_id
                    LIMIT 20;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT p.id, p.title, p.application_date, i.name as inventor_name\\nFROM patents p\\nJOIN inventors i ON p.id = i.patent_id\\nORDER BY p.application_date DESC\\nLIMIT 20;')">
                    -- Most recent patents with inventors
                    SELECT p.id, p.title, p.application_date, i.name as inventor_name
                    FROM patents p
                    JOIN inventors i ON p.id = i.patent_id
                    ORDER BY p.application_date DESC
                    LIMIT 20;
                </div>
                
                <h3>Advanced Queries</h3>
                <div class="example-query" onclick="setQueryText('SELECT a.name as applicant_name, COUNT(p.id) as patent_count\\nFROM patents p\\nJOIN applicants a ON p.id = a.patent_id\\nGROUP BY a.name\\nORDER BY patent_count DESC\\nLIMIT 10;')">
                    -- Top 10 applicants by patent count
                    SELECT a.name as applicant_name, COUNT(p.id) as patent_count
                    FROM patents p
                    JOIN applicants a ON p.id = a.patent_id
                    GROUP BY a.name
                    ORDER BY patent_count DESC
                    LIMIT 10;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT strftime(\\'%Y\\', p.application_date) as year, COUNT(*) as patent_count\\nFROM patents p\\nWHERE p.application_date IS NOT NULL\\nGROUP BY year\\nORDER BY year DESC;')">
                    -- Patents by year
                    SELECT strftime('%Y', p.application_date) as year, COUNT(*) as patent_count
                    FROM patents p
                    WHERE p.application_date IS NOT NULL
                    GROUP BY year
                    ORDER BY year DESC;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT c.code, COUNT(c.id) as usage_count\\nFROM patents p\\nJOIN ipc_classifications c ON p.id = c.patent_id\\nGROUP BY c.code\\nORDER BY usage_count DESC\\nLIMIT 15;')">
                    -- Top 15 IPC classifications
                    SELECT c.code, COUNT(c.id) as usage_count
                    FROM patents p
                    JOIN ipc_classifications c ON p.id = c.patent_id
                    GROUP BY c.code
                    ORDER BY usage_count DESC
                    LIMIT 15;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT p.title, p.abstract, claim.text as claim_text\\nFROM patents p\\nJOIN claims claim ON p.id = claim.patent_id\\nWHERE claim.claim_number = 1\\nLIMIT 10;')">
                    -- Patents with their first claim
                    SELECT p.title, p.abstract, claim.text as claim_text
                    FROM patents p
                    JOIN claims claim ON p.id = claim.patent_id
                    WHERE claim.claim_number = 1
                    LIMIT 10;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT p.id, p.title, p.abstract, GROUP_CONCAT(a.name, \\', \\') as applicants\\nFROM patents p\\nJOIN applicants a ON p.id = a.patent_id\\nWHERE p.title LIKE \\'%artificial intelligence%\\' OR p.abstract LIKE \\'%artificial intelligence%\\'\\nGROUP BY p.id\\nLIMIT 10;')">
                    -- Search for AI-related patents
                    SELECT p.id, p.title, p.abstract, GROUP_CONCAT(a.name, ', ') as applicants
                    FROM patents p
                    JOIN applicants a ON p.id = a.patent_id
                    WHERE p.title LIKE '%artificial intelligence%' OR p.abstract LIKE '%artificial intelligence%'
                    GROUP BY p.id
                    LIMIT 10;
                </div>
                
                <div class="example-query" onclick="setQueryText('SELECT * FROM sqlite_master WHERE type=\\'table\\' AND name=\\'inpit_data\\';')">
                    -- Check if inpit_data table exists
                    SELECT * FROM sqlite_master WHERE type='table' AND name='inpit_data';
                </div>
            </div>
        </div>
        
        <div id="HelpTab" class="tabcontent">
            <div class="examples">
                <h2>Help & Documentation</h2>
                
                <h3>About This Tool</h3>
                <p>This web interface allows you to execute SQL queries directly against the Patent System SQLite database. 
                   You can explore patent data, run analytical queries, and export results.</p>
                
                <h3>Database Structure</h3>
                <p>The database contains several related tables:</p>
                <ul>
                    <li><strong>patents</strong>: Main patent information including title, abstract, application dates</li>
                    <li><strong>applicants</strong>: Companies or individuals who applied for patents</li>
                    <li><strong>inventors</strong>: Individuals who invented the patented technologies</li>
                    <li><strong>ipc_classifications</strong>: International Patent Classification codes</li>
                    <li><strong>claims</strong>: Patent claims text</li>
                    <li><strong>descriptions</strong>: Detailed descriptions of patents</li>
                </ul>
                
                <h3>Tips for Using SQL Queries</h3>
                <ul>
                    <li>Use <code>LIMIT</code> to restrict the number of results (e.g., <code>LIMIT 100</code>)</li>
                    <li>Join tables to get related information (e.g., patents and applicants)</li>
                    <li>Use <code>WHERE</code> clauses to filter results</li>
                    <li>Use <code>GROUP BY</code> for aggregation and analytics</li>
                    <li>SQLite supports many common SQL functions and operators</li>
                </ul>
                
                <h3>Command Line Tool</h3>
                <p>You can also use the command-line version of this tool:</p>
                <pre>python sql_query_tool.py -q "SELECT * FROM patents LIMIT 10"</pre>
                <p>For more options, run:</p>
                <pre>python sql_query_tool.py --help</pre>
            </div>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        function setQueryText(text) {
            document.getElementById("query").value = text;
            // Switch to the query tab
            document.querySelector('.tablinks.active').className = document.querySelector('.tablinks.active').className.replace(" active", "");
            document.querySelector('.tablinks').className += " active";
            
            var tabcontent = document.getElementsByClassName("tabcontent");
            for (var i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            document.getElementById("QueryTab").style.display = "block";
            
            // Scroll to the query form
            document.querySelector('.query-form').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

def get_db_schemas():
    """Get schema for all tables in the database"""
    if not os.path.exists(DATABASE_PATH):
        return {"Error": "Database not found"}
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        schemas = {}
        for table in tables:
            table_name = table[0]
            # Get schema for this table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_text = f"CREATE TABLE {table_name} (\n"
            for i, col in enumerate(columns):
                # Format: cid, name, type, notnull, default_value, pk
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else ""
                pk = "PRIMARY KEY" if col[5] else ""
                
                schema_text += f"    {col_name} {col_type} {not_null} {pk}"
                if i < len(columns) - 1:
                    schema_text += ",\n"
                else:
                    schema_text += "\n"
            
            schema_text += ");"
            schemas[table_name] = schema_text
        
        conn.close()
        return schemas
    
    except Exception as e:
        return {"Error": str(e)}

def execute_query(query, limit=None):
    """Execute SQL query and return results"""
    if not os.path.exists(DATABASE_PATH):
        return None, "Database not found at {}".format(DATABASE_PATH), 0, [], 0
    
    # Add LIMIT clause if requested and not already in query
    if limit is not None and "LIMIT" not in query.upper():
        query = f"{query} LIMIT {limit}"
    
    try:
        start_time = datetime.now()
        
        conn = sqlite3.connect(DATABASE_PATH)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Use pandas to execute query and get results
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Convert DataFrame to list of lists for template rendering
        results = df.values.tolist()
        columns = df.columns.tolist()
        row_count = len(results)
        
        return results, None, execution_time, columns, row_count
    
    except Exception as e:
        return None, str(e), 0, [], 0

@app.route('/')
def index():
    """Render the main page with query form"""
    schemas = get_db_schemas()
    return render_template_string(
        HTML_TEMPLATE, 
        query="",
        results=None, 
        error=None,
        execution_time=0,
        columns=[],
        row_count=0,
        schemas=schemas
    )

@app.route('/query', methods=['POST'])
def query():
    """Execute the SQL query and display results"""
    query_text = request.form.get('query', '')
    
    if not query_text.strip():
        schemas = get_db_schemas()
        return render_template_string(
            HTML_TEMPLATE,
            query="", 
            results=None, 
            error="Query cannot be empty",
            execution_time=0,
            columns=[],
            row_count=0,
            schemas=schemas
        )
    
    # Execute query with a limit of 1000 rows for safety
    results, error, execution_time, columns, row_count = execute_query(query_text, 1000)
    
    # Get schema information for the Schema tab
    schemas = get_db_schemas()
    
    return render_template_string(
        HTML_TEMPLATE,
        query=query_text,
        results=results,
        error=error,
        execution_time=round(execution_time, 4),
        columns=columns,
        row_count=row_count,
        schemas=schemas
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
