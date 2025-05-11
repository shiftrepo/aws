#!/usr/bin/env python3
"""
Flask application for Patent DWH web interface with API endpoints.
"""

import os
import sqlite3
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_restful import Api, Resource
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database file paths
INPIT_DB_PATH = "/app/data/inpit.db"
GOOGLE_PATENTS_GCP_DB_PATH = "/app/data/google_patents_gcp.db"
GOOGLE_PATENTS_S3_DB_PATH = "/app/data/google_patents_s3.db"
# Default database path
DB_PATH = INPIT_DB_PATH
DB_URI = f"sqlite:///{DB_PATH}"

# Check for existence of database files
for db_path in [INPIT_DB_PATH, GOOGLE_PATENTS_GCP_DB_PATH, GOOGLE_PATENTS_S3_DB_PATH]:
    db_exists = os.path.exists(db_path)
    if db_exists:
        logger.info(f"Database exists: {db_path}")
    else:
        logger.warning(f"Database does not exist: {db_path}")

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
        # Log current user
        print(f"Running as user {os.getuid()}:{os.getgid()}")
        
        # Check database file existence and permissions
        db_exists = os.path.exists(DB_PATH)
        if db_exists:
            try:
                import stat
                file_stat = os.stat(DB_PATH)
                print(f"Database file permissions: {oct(stat.S_IMODE(file_stat.st_mode))}")
                print(f"Database file owner: {file_stat.st_uid}:{file_stat.st_gid}")
                
                # Make sure file is readable
                if not os.access(DB_PATH, os.R_OK):
                    print(f"Warning: Database file exists but is not readable")
                    try:
                        # Try to fix permissions if needed
                        os.chmod(DB_PATH, 0o666)
                        print("Attempted to fix database file permissions")
                    except Exception as perm_err:
                        print(f"Could not fix permissions: {perm_err}")
            except Exception as e:
                print(f"Could not check database permissions: {e}")
        else:
            print(f"Database file does not exist at {DB_PATH}")
        
        # Reflect database structure
        metadata.reflect(bind=engine)
        
        # Create dynamic model for the table if table exists
        if 'inpit_data' in metadata.tables:
            # Get the inpit_data table
            inpit_table = metadata.tables['inpit_data']
            
            # SQLAlchemy requires primary keys for ORM operations
            # Check if the table already has a primary key defined
            has_pk = any(column.primary_key for column in inpit_table.columns)
            
            if not has_pk:
                # If no primary key is found, add a primary key constraint to the first column
                # This is a workaround for the SQLAlchemy mapper requirement
                first_column = list(inpit_table.columns)[0]
                first_column.primary_key = True
                logger.info(f"Added primary key to column '{first_column.name}' for table 'inpit_data'")
            
            # Define the model class inside the function
            class InpitDataModel(Base):
                __tablename__ = inpit_table.name
                __table_args__ = {'extend_existing': True}
                
                # Map columns dynamically
                for column in inpit_table.columns:
                    # Set the column in the model's __dict__
                    locals()[column.name] = column
                
                def __str__(self):
                    return f"InpitData {self.__table__.columns[0].name}={getattr(self, self.__table__.columns[0].name, None)}"
            
            # Return the dynamically created model class
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

# Custom view for free SQL queries
class SQLQueryView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/sql_query.html')
        
# Custom views for SQL examples - one for each database
class InpitSQLExamplesView(BaseView):
    @expose('/')
    def index(self):
        # Create the template with hardcoded db_type for the INPIT database
        return self.render('admin/inpit_sql_examples.html', db_type='inpit', 
                          db_title='INPIT SQLite',
                          db_file='inpit.db')

    @expose('/query', methods=['POST'])
    def query(self):
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

class GooglePatentsGCPExamplesView(BaseView):
    @expose('/')
    def index(self):
        # Create the template with hardcoded db_type for the GCP database
        return self.render('admin/google_patents_gcp_examples.html', db_type='google_patents_gcp', 
                          db_title='Google Patents GCP',
                          db_file='google_patents_gcp.db')
    
    @expose('/query', methods=['POST'])
    def query(self):
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
        
class GooglePatentsS3ExamplesView(BaseView):
    @expose('/')
    def index(self):
        # Create the template with hardcoded db_type for the S3 database
        return self.render('admin/google_patents_s3_examples.html', db_type='google_patents_s3', 
                          db_title='Google Patents S3',
                          db_file='google_patents_s3.db')
    
    @expose('/query', methods=['POST'])
    def query(self):
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

# Setup Flask-Admin
admin = Admin(app, name='patentDWH Database', template_mode='bootstrap3')

if InpitData:
    # Add the data view if the model is available
    admin.add_view(InpitDataView(InpitData, db.session))

# Always add SQL query view for free SQL queries
admin.add_view(SQLQueryView(name='自由SQL', endpoint='sql'))

# Add separate SQL Examples views for each database
admin.add_view(InpitSQLExamplesView(name='INPIT SQL サンプル', endpoint='inpit_examples'))
admin.add_view(GooglePatentsGCPExamplesView(name='GCP Patents サンプル', endpoint='gcp_examples'))
admin.add_view(GooglePatentsS3ExamplesView(name='S3 Patents サンプル', endpoint='s3_examples'))

# Create templates directory and SQL query template
os.makedirs('templates/admin', exist_ok=True)

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
    db_type = request.form.get('db_type', 'inpit')
    
    # Select database based on type
    db_path = INPIT_DB_PATH
    if db_type == 'google_patents_gcp':
        db_path = GOOGLE_PATENTS_GCP_DB_PATH
    elif db_type == 'google_patents_s3':
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

# Initialize Flask-RESTful API and CORS
api = Api(app)
CORS(app)

# Helper function to get schema information
def get_schema_info():
    """Get database schema information for API documentation."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {}
        
        # Get column info for each table
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
            schema_info[table] = columns
        
        conn.close()
        return schema_info
    except Exception as e:
        logger.error(f"Error getting schema info: {e}")
        return {}

# API Resource for direct SQL queries
class SQLQueryAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return {"error": "Missing 'query' field in JSON body"}, 400
            
            db_type = data.get('db_type', 'inpit')
            sql_query = data['query']
            logger.info(f"Direct SQL query on {db_type}: {sql_query}")
            
            # Basic security check - only allow SELECT queries
            if not sql_query.strip().lower().startswith('select'):
                return {"error": "Only SELECT queries are allowed"}, 403
            
            # Select database based on type
            db_path = INPIT_DB_PATH
            if db_type == 'google_patents_gcp':
                db_path = GOOGLE_PATENTS_GCP_DB_PATH
            elif db_type == 'google_patents_s3':
                db_path = GOOGLE_PATENTS_S3_DB_PATH
            
            # Execute the query
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            conn.close()
            
            return {
                "success": True,
                "columns": columns,
                "results": results,
                "record_count": len(results)
            }
        except Exception as e:
            logger.error(f"Error in SQL query API: {e}")
            return {"error": str(e)}, 500

# Register API resources
api.add_resource(SQLQueryAPI, '/api/sql-query')

# API status and documentation endpoint
@app.route('/api/status')
def api_status():
    """Return API status and documentation."""
    try:
        # Get schema info for documentation from all databases
        schemas = {}
        
        # Check INPIT database
        if os.path.exists(INPIT_DB_PATH):
            conn = sqlite3.connect(INPIT_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inpit_data")
            count = cursor.fetchone()[0]
            conn.close()
            schemas['inpit'] = {'record_count': count}
        else:
            schemas['inpit'] = {'error': 'Database not found'}
            
        # Check GCP database
        if os.path.exists(GOOGLE_PATENTS_GCP_DB_PATH):
            conn = sqlite3.connect(GOOGLE_PATENTS_GCP_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM publications")
            count = cursor.fetchone()[0]
            conn.close()
            schemas['google_patents_gcp'] = {'record_count': count}
        else:
            schemas['google_patents_gcp'] = {'error': 'Database not found'}
            
        # Check S3 database
        if os.path.exists(GOOGLE_PATENTS_S3_DB_PATH):
            conn = sqlite3.connect(GOOGLE_PATENTS_S3_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM publications")
            count = cursor.fetchone()[0]
            conn.close()
            schemas['google_patents_s3'] = {'record_count': count}
        else:
            schemas['google_patents_s3'] = {'error': 'Database not found'}
        
        return jsonify({
            "status": "active",
            "databases": schemas,
            "endpoints": {
                "POST /api/sql-query": "Direct SQL query (JSON body with 'query' field and optional 'db_type')",
                "GET /api/status": "This API status endpoint"
            }
        })
    except Exception as e:
        logger.error(f"Error in API status: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Add context for the SQLAlchemy session
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Create the template directories if they don't exist
os.makedirs('templates/admin', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Create SQL query template
with open('templates/admin/sql_query.html', 'w') as f:
    f.write('''
{% extends 'admin/master.html' %}

{% block body %}
<h1>自由SQLクエリツール</h1>
<div class="row">
    <div class="col-md-12">
        <div class="box">
            <div class="box-body">
                <div class="form-group">
                    <label for="dbSelector">データベース選択:</label>
                    <select id="dbSelector" class="form-control">
                        <option value="inpit">inpit.db</option>
                        <option value="google_patents_gcp">google_patents_gcp.db</option>
                        <option value="google_patents_s3">google_patents_s3.db</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="queryInput">SQL Query:</label>
                    <textarea id="queryInput" class="form-control" rows="8" placeholder="Enter your SQL query..."></textarea>
                </div>
                <button id="executeBtn" class="btn btn-primary">クエリ実行</button>
            </div>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-md-12">
        <div id="results" class="box">
            <div class="box-header">
                <h3 class="box-title">結果</h3>
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
    const dbType = document.getElementById('dbSelector').value;
    
    if (!query) {
        alert('クエリを入力してください');
        return;
    }
    
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'query=' + encodeURIComponent(query) + '&db_type=' + encodeURIComponent(dbType)
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
            <div class="alert alert-success">クエリ実行成功。${data.results.length} 行の結果。</div>
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

# Create the example templates
with open('templates/admin/inpit_sql_examples.html', 'w') as f:
    f.write('''
{% extends 'admin/master.html' %}

{% block body %}
<h1>INPIT SQLサンプル</h1>
<div class="row">
    <div class="col-md-12">
        <div class="box">
            <div class="box-header">
                <h3 class="box-title">サンプルクエリ</h3>
            </div>
            <div class="box-body">
                <div class="form-group">
                    <label for="exampleSelector">サンプルを選択:</label>
                    <select id="exampleSelector" class="form-control" onchange="loadExample()">
                        <option value="">-- 選択してください --</option>
                        <option value="basic">基本検索</option>
                        <option value="applicant">出願人による検索</option>
                        <option value="date">日付範囲による検索</option>
                        <option value="count">集計クエリ</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="queryInput">SQL Query:</label>
                    <textarea id="queryInput" class="form-control" rows="8"></textarea>
                </div>
                <button id="executeBtn" class="btn btn-primary">クエリ実行</button>
            </div>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-md-12">
        <div id="results" class="box">
            <div class="box-header">
                <h3 class="box-title">結果</h3>
            </div>
            <div class="box-body">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
</div>

<script>
const examples = {
    schema: `PRAGMA table_info(inpit_data);`,
    basic: `SELECT * FROM inpit_data LIMIT 10;`,
    applicant: `SELECT * FROM inpit_data 
WHERE applicant LIKE '%テック%'
ORDER BY application_date DESC
LIMIT 20;`,
    date: `SELECT * FROM inpit_data 
WHERE application_date BETWEEN '2022-01-01' AND '2023-12-31'
ORDER BY application_date DESC
LIMIT 20;`,
    count: `SELECT 
    strftime('%Y', application_date) as year,
    COUNT(*) as application_count
FROM inpit_data
GROUP BY strftime('%Y', application_date)
ORDER BY year DESC;`
};

function loadExample() {
    const example = document.getElementById('exampleSelector').value;
    if (example in examples) {
        document.getElementById('queryInput').value = examples[example];
    }
}

document.getElementById('executeBtn').addEventListener('click', function() {
    const query = document.getElementById('queryInput').value;
    
    if (!query) {
        alert('クエリを入力してください');
        return;
    }
    
    fetch('{{ url_for("inpit_examples.query") }}', {
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
            <div class="alert alert-success">クエリ実行成功。${data.results.length} 行の結果。</div>
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

with open('templates/admin/google_patents_gcp_examples.html', 'w') as f:
    f.write('''
{% extends 'admin/master.html' %}

{% block body %}
<h1>Google Patents GCP SQLサンプル</h1>
<div class="row">
    <div class="col-md-12">
        <div class="box">
            <div class="box-header">
                <h3 class="box-title">サンプルクエリ</h3>
            </div>
            <div class="box-body">
                <div class="form-group">
                    <label for="exampleSelector">サンプルを選択:</label>
                    <select id="exampleSelector" class="form-control" onchange="loadExample()">
                        <option value="">-- 選択してください --</option>
                        <option value="basic">基本検索</option>
                        <option value="title">タイトルによる検索</option>
                        <option value="family">ファミリー検索</option>
                        <option value="year">年別特許数</option>
                        <option value="company">企業別特許数</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="queryInput">SQL Query:</label>
                    <textarea id="queryInput" class="form-control" rows="8"></textarea>
                </div>
                <button id="executeBtn" class="btn btn-primary">クエリ実行</button>
            </div>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-md-12">
        <div id="results" class="box">
            <div class="box-header">
                <h3 class="box-title">結果</h3>
            </div>
            <div class="box-body">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
</div>

<script>
const examples = {
    basic: `SELECT publication_number, title_ja, publication_date, assignee_harmonized
FROM publications
LIMIT 10;`,
    title: `SELECT publication_number, title_ja, abstract_ja, assignee_harmonized, publication_date
FROM publications
WHERE title_ja LIKE '%人工知能%' OR title_ja LIKE '%AI%'
ORDER BY publication_date DESC
LIMIT 15;`,
    family: `SELECT p.publication_number, p.title_ja, p.publication_date, p.assignee_harmonized, p.family_id,
       COUNT(pf.publication_number) as family_size
FROM publications p
JOIN patent_families pf ON p.family_id = pf.family_id
GROUP BY p.family_id
HAVING family_size > 2
ORDER BY family_size DESC
LIMIT 15;`,
    year: `SELECT 
    substr(publication_date, 1, 4) as year,
    COUNT(*) as patent_count
FROM publications
GROUP BY year
ORDER BY year DESC;`,
    company: `SELECT 
    assignee_harmonized as company,
    COUNT(*) as patent_count
FROM publications 
WHERE assignee_harmonized IS NOT NULL
GROUP BY assignee_harmonized
ORDER BY patent_count DESC
LIMIT 20;`
};

function loadExample() {
    const example = document.getElementById('exampleSelector').value;
    if (example in examples) {
        document.getElementById('queryInput').value = examples[example];
    }
}

document.getElementById('executeBtn').addEventListener('click', function() {
    const query = document.getElementById('queryInput').value;
    
    if (!query) {
        alert('クエリを入力してください');
        return;
    }
    
    fetch('{{ url_for("gcp_examples.query") }}', {
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
            <div class="alert alert-success">クエリ実行成功。${data.results.length} 行の結果。</div>
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

with open('templates/admin/google_patents_s3_examples.html', 'w') as f:
    f.write('''
{% extends 'admin/master.html' %}

{% block body %}
<h1>Google Patents S3 SQLサンプル</h1>
<div class="row">
    <div class="col-md-12">
        <div class="box">
            <div class="box-header">
                <h3 class="box-title">サンプルクエリ</h3>
            </div>
            <div class="box-body">
                <div class="form-group">
                    <label for="exampleSelector">サンプルを選択:</label>
                    <select id="exampleSelector" class="form-control" onchange="loadExample()">
                        <option value="">-- 選択してください --</option>
                        <option value="basic">基本検索</option>
                        <option value="title">タイトルによる検索</option>
                        <option value="year">年別特許数</option>
                        <option value="company">企業別特許数</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="queryInput">SQL Query:</label>
                    <textarea id="queryInput" class="form-control" rows="8"></textarea>
                </div>
                <button id="executeBtn" class="btn btn-primary">クエリ実行</button>
            </div>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-md-12">
        <div id="results" class="box">
            <div class="box-header">
                <h3 class="box-title">結果</h3>
            </div>
            <div class="box-body">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
</div>

<script>
const examples = {
    basic: `SELECT publication_number, title_ja, publication_date, assignee_harmonized
FROM publications
LIMIT 10;`,
    title: `SELECT publication_number, title_ja, abstract_ja, assignee_harmonized, publication_date
FROM publications
WHERE title_ja LIKE '%機械学習%' OR title_ja LIKE '%深層学習%'
ORDER BY publication_date DESC
LIMIT 15;`,
    year: `SELECT 
    substr(publication_date, 1, 4) as year,
    COUNT(*) as patent_count
FROM publications
GROUP BY year
ORDER BY year DESC;`,
    company: `SELECT 
    assignee_harmonized as company,
    COUNT(*) as patent_count
FROM publications 
WHERE assignee_harmonized IS NOT NULL
GROUP BY assignee_harmonized
ORDER BY patent_count DESC
LIMIT 20;`
};

function loadExample() {
    const example = document.getElementById('exampleSelector').value;
    if (example in examples) {
        document.getElementById('queryInput').value = examples[example];
    }
}

document.getElementById('executeBtn').addEventListener('click', function() {
    const query = document.getElementById('queryInput').value;
    
    if (!query) {
        alert('クエリを入力してください');
        return;
    }
    
    fetch('{{ url_for("s3_examples.query") }}', {
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
            <div class="alert alert-success">クエリ実行成功。${data.results.length} 行の結果。</div>
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
