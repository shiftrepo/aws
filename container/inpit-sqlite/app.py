#!/usr/bin/env python3
"""
Flask application for SQLite web interface.
"""

import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database file path
DB_PATH = "/app/data/inpit.db"
DB_URI = f"sqlite:///{DB_PATH}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Load column mapping if exists
column_mapping = {}
mapping_path = '/app/data/column_mapping.json'
if os.path.exists(mapping_path):
    try:
        with open(mapping_path, 'r') as f:
            column_mapping = json.load(f)
    except Exception as e:
        print(f"Error loading column mapping: {e}")

# Create dynamic model from database
Base = declarative_base()
engine = create_engine(DB_URI)
metadata = MetaData()

# Check if the database file exists
db_file_exists = os.path.exists(DB_PATH)

# Initialize the model class variable
InpitData = None

def initialize_db():
    global InpitData, metadata
    
    try:
        # Reflect database structure
        metadata.reflect(bind=engine)
        
        # Create dynamic model for the table if table exists
        if 'inpit_data' in metadata.tables:
            class InpitDataModel(Base):
                __table__ = Table('inpit_data', metadata, autoload=True, autoload_with=engine)
                
                def __str__(self):
                    return f"InpitData {self.id}"
            
            return InpitDataModel
        else:
            print("Warning: 'inpit_data' table not found in database")
            return None
    except Exception as e:
        print(f"Error initializing database model: {e}")
        return None

# Try to initialize the database model
InpitData = initialize_db()

# Custom ModelView to use original column names
class InpitDataView(ModelView):
    column_labels = {}
    
    def __init__(self, model, session, **kwargs):
        # Set column labels based on the mapping
        for clean_name, original_name in column_mapping.items():
            self.column_labels[clean_name] = original_name
        
        super(InpitDataView, self).__init__(model, session, **kwargs)

# Custom view for SQL queries
class SQLQueryView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/sql_query.html')

# Setup Flask-Admin
admin = Admin(app, name='Inpit SQLite Database', template_mode='bootstrap3')

if InpitData:
    # Add the data view if the model is available
    admin.add_view(InpitDataView(InpitData, db.session))

# Always add SQL query view
admin.add_view(SQLQueryView(name='SQL Query', endpoint='sql'))

# Create templates directory and SQL query template
os.makedirs('templates/admin', exist_ok=True)
with open('templates/admin/sql_query.html', 'w') as f:
    f.write('''
{% extends 'admin/master.html' %}

{% block body %}
<h1>SQL Query Tool</h1>
<div class="row">
    <div class="col-md-12">
        <div class="box">
            <div class="box-body">
                <div class="form-group">
                    <label for="queryInput">SQL Query:</label>
                    <textarea id="queryInput" class="form-control" rows="5" placeholder="Enter your SQL query..."></textarea>
                </div>
                <button id="executeBtn" class="btn btn-primary">Execute Query</button>
            </div>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-md-12">
        <div id="results" class="box">
            <div class="box-header">
                <h3 class="box-title">Results</h3>
            </div>
            <div class="box-body">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('executeBtn').addEventListener('click', function() {
    const query = document.getElementById('queryInput').value;
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'query=' + encodeURIComponent(query)
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('resultContent');
        
        if (!data.success) {
            resultDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        if (data.message) {
            resultDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            return;
        }
        
        // Display results in a table
        let tableHtml = '<div class="table-responsive"><table class="table table-striped table-bordered">';
        tableHtml += '<thead><tr>';
        data.columns.forEach(column => {
            tableHtml += `<th>${column}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        
        data.results.forEach(row => {
            tableHtml += '<tr>';
            row.forEach(cell => {
                tableHtml += `<td>${cell === null ? '<em>NULL</em>' : cell}</td>`;
            });
            tableHtml += '</tr>';
        });
        
        tableHtml += '</tbody></table></div>';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success">Query executed successfully. ${data.results.length} rows returned.</div>
            ${tableHtml}
        `;
    })
    .catch(error => {
        document.getElementById('resultContent').innerHTML = `<div class="alert alert-danger">Error: ${error}</div>`;
    });
});
</script>
{% endblock %}
    ''')

@app.route('/')
def index():
    """
    Redirect to admin interface.
    """
    return redirect('/admin')

@app.route('/tables')
def tables():
    """
    Return the list of tables in the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"tables": tables})

@app.route('/query', methods=['POST'])
def query():
    """
    Execute a SQL query and return results.
    """
    sql_query = request.form.get('query', '')
    try:
        conn = sqlite3.connect(DB_PATH)
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

# Add context for the SQLAlchemy session
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
