#!/usr/bin/env python3

import os
import sqlite3
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
import urllib.parse
from jplatpat_client import JPlatPatClient

app = Flask(__name__)
CORS(app)

# Path to SQLite database
SQLITE_DB_PATH = "/data/patents.db"

# BigQuery settings
PROJECT_ID = "tosapi"
DATASET_ID = "patents_public_data"
TABLE_ID = "patents"

def init_db():
    """Initialize SQLite database with necessary tables"""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Create patents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patents (
        patent_id TEXT PRIMARY KEY,
        publication_number TEXT,
        applicant TEXT,
        theme TEXT,
        title TEXT,
        abstract TEXT,
        filing_date TEXT,
        grant_date TEXT,
        assignee TEXT,
        inventor TEXT,
        additional_data TEXT
    )
    ''')
    
    # Create index for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_publication ON patents (publication_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applicant ON patents (applicant)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_theme ON patents (theme)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def connect_bigquery():
    """Connect to BigQuery using service account"""
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(
        key_path, 
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
    return client

def list_datasets_and_tables():
    """List available datasets and tables in BigQuery"""
    try:
        client = connect_bigquery()
        print(f"Successfully connected to BigQuery as {client.project}")
        
        # Create job config to ensure all operations use the client's project
        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        
        print(f"Attempting to list datasets in project {PROJECT_ID}...")
        datasets = list(client.list_datasets())
        
        result = {}
        if datasets:
            print(f"Found {len(datasets)} datasets in project {PROJECT_ID}:")
            for dataset in datasets:
                dataset_id = dataset.dataset_id
                print(f"- Dataset: {dataset_id}")
                
                # List tables in this dataset
                try:
                    print(f"  Listing tables in dataset {dataset_id}...")
                    tables = list(client.list_tables(dataset_id))
                    table_list = []
                    if tables:
                        print(f"  Found {len(tables)} tables in dataset {dataset_id}:")
                        for table in tables:
                            table_id = table.table_id
                            print(f"  - Table: {table_id}")
                            table_list.append(table_id)
                    else:
                        print(f"  No tables found in dataset {dataset_id}")
                    
                    result[dataset_id] = table_list
                except Exception as e:
                    print(f"  Error listing tables in dataset {dataset_id}: {str(e)}")
                    result[dataset_id] = f"Error: {str(e)}"
        else:
            print(f"No datasets found in project {PROJECT_ID}")
        
        return result
    except Exception as e:
        print(f"Error in list_datasets_and_tables: {str(e)}")
        raise e

def search_patent_datasets():
    """Search for available patent datasets in BigQuery public data"""
    client = connect_bigquery()
    
    # Try to find the patents in public datasets
    try:
        # First check if patents_public_data exists
        try:
            dataset_ref = client.dataset('patents_public_data', project='bigquery-public-data')
            dataset = client.get_dataset(dataset_ref)
            print(f"Found public patents dataset: {dataset.dataset_id}")
            
            # Check tables in this dataset
            tables = list(client.list_tables(dataset))
            if tables:
                print(f"Found {len(tables)} tables in public patents dataset:")
                for table in tables:
                    print(f"- Table: {table.table_id}")
                return 'bigquery-public-data', 'patents_public_data', tables[0].table_id
            else:
                print("No tables found in public patents dataset")
        except Exception as e:
            print(f"Error accessing public patent dataset: {str(e)}")
        
        # Try alternative patent datasets - Patents View is another known patent dataset
        try:
            dataset_ref = client.dataset('patents', project='bigquery-public-data')
            dataset = client.get_dataset(dataset_ref)
            print(f"Found public patents dataset: {dataset.dataset_id}")
            
            # Check tables in this dataset
            tables = list(client.list_tables(dataset))
            if tables:
                print(f"Found {len(tables)} tables in patents dataset:")
                for table in tables:
                    print(f"- Table: {table.table_id}")
                
                # Look for a table that might contain patent data
                patent_tables = [t for t in tables if 'patent' in t.table_id.lower()]
                if patent_tables:
                    return 'bigquery-public-data', 'patents', patent_tables[0].table_id
                
                # If no patent table found, use the first table
                return 'bigquery-public-data', 'patents', tables[0].table_id
            else:
                print("No tables found in patents dataset")
        except Exception as e:
            print(f"Error accessing patents dataset: {str(e)}")
            
        # Final fallback - try a sample patents dataset
        try:
            # Use Patent Public Data sample if available
            query = """
            SELECT table_name
            FROM `bigquery-public-data`.INFORMATION_SCHEMA.TABLES
            WHERE table_name LIKE '%patent%' 
            LIMIT 10
            """
            # Use job_config to ensure query runs in our project
            job_config = bigquery.QueryJobConfig(
                use_query_cache=True,
                default_dataset=f"{client.project}.{DATASET_ID}"
            )
            job = client.query(query, job_config=job_config)
            results = list(job.result())
            
            if results:
                print(f"Found {len(results)} patent-related tables:")
                for row in results:
                    print(f"- Table: {row.table_name}")
                return 'bigquery-public-data', 'uspto_oce_cancer', 'patent'
        except Exception as e:
            print(f"Error finding sample patent data: {str(e)}")
    
    except Exception as e:
        print(f"Error in search_patent_datasets: {str(e)}")
    
    # If no dataset found, return the USPTO Cancer Moonshot Open Patent Data
    print("Using USPTO Cancer Moonshot dataset as fallback")
    return 'bigquery-public-data', 'uspto_oce_cancer', 'patent'

def fetch_and_store_patents(query_conditions=None):
    """Fetch patents from BigQuery and store in SQLite"""
    try:
        print("Connecting to BigQuery...")
        client = connect_bigquery()
        print(f"Connected to BigQuery as project {client.project}")
        
        # Ensure we're using our own project for job execution
        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        print(f"Query jobs will be executed in project: {client.project}")
        
        # First, check what datasets and tables are available in the current project
        print("Listing available datasets and tables in current project...")
        available_datasets = list_datasets_and_tables()
        print(f"Dataset analysis for project {client.project} complete.")
        
        # Find a suitable patents dataset
        global PROJECT_ID, DATASET_ID, TABLE_ID
        found_project, found_dataset, found_table = search_patent_datasets()
        
        # Update our application to use the found dataset but keep queries in our own project
        print(f"Updating application to use {found_project}.{found_dataset}.{found_table}")
        # Do NOT update our PROJECT_ID, as we want to keep running jobs in our own project
        # PROJECT_ID remains as the original value (tosapi)
        DATASET_ID = found_dataset
        TABLE_ID = found_table
        
        # Store the external project ID for reference but don't use it for job execution
        external_project_id = found_project
        
        # Now try to fetch data from the selected dataset and table
        print(f"Fetching patent data from {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
        
        # First get the table schema to understand the structure
        table_ref = client.dataset(DATASET_ID, project=external_project_id).table(TABLE_ID)
        try:
            # Try using get_table for schema, but this might fail due to permissions
            # If it fails, we'll fall back to using a query to get schema information
            try:
                table = client.get_table(table_ref)
            except Exception as schema_error:
                print(f"Could not directly access table schema: {str(schema_error)}")
                print("Using fallback method to get schema via query...")
                
                # Use a query to get schema information from INFORMATION_SCHEMA including data types
                schema_query = f"""
                SELECT column_name, data_type
                FROM `{external_project_id}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
                WHERE table_name = '{TABLE_ID}'
                """
                schema_job_config = bigquery.QueryJobConfig(use_query_cache=True)
                schema_job = client.query(schema_query, job_config=schema_job_config)
                schema_results = schema_job.result()
                
                # Create a mock table schema object with field names
                class MockField:
                    def __init__(self, name, data_type):
                        self.name = name
                        # Map BigQuery data types to our internal type names
                        if data_type.startswith('ARRAY'):
                            self.field_type = "ARRAY"  # This is an array type
                        elif data_type == 'STRUCT':
                            self.field_type = "RECORD"  # This is a record/struct type
                        else:
                            self.field_type = data_type  # Use the actual data type
                
                class MockTable:
                    def __init__(self, fields):
                        self.schema = fields
                
                fields = [MockField(row.column_name, row.data_type) for row in schema_results]
                table = MockTable(fields)
            print("Table schema:")
            field_names = [field.name for field in table.schema]
            print(f"Fields: {', '.join(field_names)}")
            
            # Dynamically build a query based on the available fields
            # Common patent fields we're looking for
            target_fields = {
                'patent_id': ['patent_id', 'id', 'patent_number', 'patent'],
                'publication_number': ['publication_number', 'pub_number', 'publication'],
                'applicant': ['applicant', 'assignee', 'owner'],
                'theme': ['theme', 'classification', 'primary_classification'],
                'title': ['title'],
                'abstract': ['abstract'],
                'filing_date': ['filing_date', 'application_date'],
                'grant_date': ['grant_date', 'issue_date'],
                'inventor': ['inventor', 'inventors']
            }
            
            # Map available fields to our target fields
            field_mapping = {}
            for target, possible_names in target_fields.items():
                for name in possible_names:
                    if name in field_names:
                        field_mapping[target] = name
                        break
            
            print(f"Field mapping: {field_mapping}")
            
            # Construct a query using the available fields
            select_clause = []
            for target, source in field_mapping.items():
                select_clause.append(f"{source} as {target}")
            
            if not select_clause:
                select_clause = ["*"]  # If no matching fields, just select all
                
            query = f"""
            SELECT {', '.join(select_clause)}
            FROM `{external_project_id}.{DATASET_ID}.{TABLE_ID}`
            """
            
            # For improved reliability, do ALL filtering in Python instead of SQL
            # This approach completely avoids LOWER function errors with arrays
            filters = {}
            
            if query_conditions:
                print(f"Will apply all filters in Python: {query_conditions}")
                # Store all filters for post-query processing
                for target, value in query_conditions.items():
                    if target in field_mapping:
                        source = field_mapping[target]
                        filters[source] = value.lower()
            
            # Add limit to prevent overwhelming the system
            query += " LIMIT 50"
            
            print(f"Executing query: {query}")
            # Explicitly configure job to run in the client's project
            job_config = bigquery.QueryJobConfig(
                use_query_cache=True,
                default_dataset=f"{client.project}.{DATASET_ID}" if DATASET_ID in client.project else None
            )
            
            # No query parameters needed since we filter in Python
            
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()
            
            # Convert results to a pandas DataFrame
            df = results.to_dataframe()
            
            if df.empty:
                print("No data returned from BigQuery")
                return {
                    'message': 'No patent data found matching your criteria',
                    'project_datasets': available_datasets,
                    'current_config': {
                        'project': PROJECT_ID,
                        'dataset': DATASET_ID,
                        'table': TABLE_ID
                    }
                }
                
            # Apply filtering in Python if needed
            if query_conditions and filters:
                print(f"Applying filters in Python: {filters}")
                
                # Original row count
                original_count = len(df)
                
                # Apply each filter
                for source_field, filter_value in filters.items():
                    # Get the target field name from our mapping
                    target_field = None
                    for t, s in field_mapping.items():
                        if s == source_field:
                            target_field = t
                            break
                    
                    if target_field and target_field in df.columns:
                        # Define filter function for array values
                        def array_contains_filter(arr, value):
                            if arr is None:
                                return False
                            # Check if it's a list/array
                            if isinstance(arr, (list, tuple, np.ndarray)):
                                # Convert each element to lowercase and check if any contains the filter
                                return any(value in str(x).lower() for x in arr)
                            # If it's a string, check if it contains the filter
                            return value in str(arr).lower()
                        
                        # Apply filter
                        mask = df[target_field].apply(lambda x: array_contains_filter(x, filter_value))
                        df = df[mask]
                
                filtered_count = len(df)
                print(f"Python filtering: {original_count} rows → {filtered_count} rows")
            
            print(f"Found {len(df)} patents matching the criteria")
            
            # Store in SQLite
            conn = sqlite3.connect(SQLITE_DB_PATH)
            
            # Map DataFrame columns to our SQLite table structure
            for target in ['patent_id', 'publication_number', 'applicant', 'theme', 'title', 'abstract', 
                          'filing_date', 'grant_date', 'assignee', 'inventor']:
                if target not in df.columns:
                    df[target] = None
            
            # Handle array fields - convert arrays to strings for SQLite
            print("Processing arrays for SQLite storage")
            array_fields = ['applicant', 'assignee', 'inventor']
            for field in array_fields:
                if field in df.columns and df[field].dtype == 'object':
                    print(f"Converting {field} arrays to strings")
                    # Convert arrays to comma-separated strings
                    df[field] = df[field].apply(
                        lambda x: ', '.join(x) if isinstance(x, (list, tuple, np.ndarray)) else x
                    )
            
            # Additional data will be any columns not in our standard schema
            standard_cols = ['patent_id', 'publication_number', 'applicant', 'theme', 'title', 'abstract', 
                            'filing_date', 'grant_date', 'assignee', 'inventor']
            extra_cols = [col for col in df.columns if col not in standard_cols]
            
            if extra_cols:
                # Convert extra columns to JSON in additional_data, handling NumPy types
                def convert_to_json_safe(row):
                    row_dict = {}
                    for col in extra_cols:
                        val = row[col]
                        # Convert NumPy types to Python native types
                        if hasattr(val, 'item'):  # NumPy scalars have .item() method
                            row_dict[col] = val.item() if not pd.isna(val) else None
                        elif isinstance(val, (list, tuple)) and len(val) > 0 and hasattr(val[0], 'item'):
                            row_dict[col] = [x.item() if hasattr(x, 'item') else x for x in val]
                        else:
                            row_dict[col] = val
                    return json.dumps(row_dict)
                
                df['additional_data'] = df[extra_cols].apply(convert_to_json_safe, axis=1)
            else:
                df['additional_data'] = None
            
            # Insert data, replacing any existing entries with the same patent_id
            df[standard_cols + ['additional_data']].to_sql('patents', conn, if_exists='append', index=False, method='multi', chunksize=100)
            
            row_count = len(df)
            conn.commit()
            conn.close()
            
            print(f"Stored {row_count} patents in SQLite")
            return {
                'message': f'Successfully imported {row_count} patents',
                'project_datasets': available_datasets,
                'current_config': {
                    'project': PROJECT_ID,
                    'dataset': DATASET_ID,
                    'table': TABLE_ID
                },
                'sample_patents': df.head(5).to_dict(orient='records')
            }
            
        except Exception as e:
            print(f"Error getting table schema: {str(e)}")
            raise e
        
    except Exception as e:
        print(f"Error in fetch_and_store_patents: {str(e)}")
        raise e

@app.route('/init', methods=['GET'])
def initialize():
    """Initialize the database"""
    init_db()
    return jsonify({"status": "success", "message": "Database initialized"})

# Add custom JSON encoder to handle NumPy types
class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super(NumpyJSONEncoder, self).default(obj)

@app.route('/import', methods=['POST'])
def import_data():
    """Import data from BigQuery based on provided filters"""
    try:
        # Get filter conditions from request
        filters = request.json if request.is_json else {}
        print(f"Import request received with filters: {filters}")
        
        # Ensure we're not trying to run jobs in bigquery-public-data project
        # Log the current project to verify
        client = connect_bigquery()
        print(f"Running import using project: {client.project}")
        
        # Fetch and store data
        datasets_info = fetch_and_store_patents(filters)
        
        # Use custom JSON encoder for NumPy types
        response_data = {
            "status": "success", 
            "message": "Patent data imported successfully",
            "filters": filters,
            "datasets": datasets_info
        }
        
        # Use Flask's Response with our custom JSON encoder
        from flask import Response
        return Response(
            json.dumps(response_data, cls=NumpyJSONEncoder),
            mimetype='application/json'
        )
    except Exception as e:
        error_message = str(e)
        print(f"Error in import_data: {error_message}")
        return jsonify({
            "status": "error", 
            "message": error_message,
            "error_type": type(e).__name__
        }), 500

@app.route('/patents', methods=['GET'])
def get_patents():
    """Query patents from SQLite with filters"""
    try:
        # Get query parameters
        patent_id = request.args.get('patent_id')
        publication_number = request.args.get('publication_number')
        applicant = request.args.get('applicant')
        theme = request.args.get('theme')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Debug log the received parameters
        print(f"Received patent query - params: patent_id={patent_id}, publication_number={publication_number}, "
              f"applicant={applicant}, theme={theme}, limit={limit}, offset={offset}")
        
        # Build query with DISTINCT to avoid duplicates
        query = "SELECT DISTINCT * FROM patents WHERE 1=1"
        params = []
        
        if patent_id:
            # URL-decode the patent_id
            decoded_patent_id = urllib.parse.unquote(patent_id)
            
            # Need to match different format patterns
            # For example, US3560531 needs to match US-3560531-A
            
            # Check publication_number field since patent_id is empty in the database
            # Extract the country code (usually 2 letters at the start)
            country_code = None
            number_part = None
            
            if decoded_patent_id and len(decoded_patent_id) >= 2 and decoded_patent_id[:2].isalpha():
                # Standard format like US3560531
                country_code = decoded_patent_id[:2]
                number_part = ''.join(c for c in decoded_patent_id[2:] if c.isdigit())
            
            if country_code and number_part:
                # Search in publication_number field with LIKE to match various formats
                query += " AND (publication_number LIKE ? OR publication_number LIKE ? OR publication_number LIKE ?)"
                params.extend([
                    f"{country_code}-{number_part}%",  # Match US-3560531-A
                    f"{country_code}{number_part}%",   # Match US3560531A
                    f"{country_code}%{number_part}%"   # Match any format with country and number
                ])
            else:
                # Fallback to direct comparison
                query += " AND (patent_id = ? OR publication_number = ?)"
                params.extend([patent_id, patent_id])
        
        if publication_number:
            # URL-decode the publication_number
            decoded_publication_number = urllib.parse.unquote(publication_number)
            query += " AND publication_number = ?"
            params.append(decoded_publication_number)
        
        if applicant:
            # Ensure applicant is properly URL-decoded
            decoded_applicant = urllib.parse.unquote(applicant)
            query += " AND applicant LIKE ?"
            params.append(f"%{decoded_applicant}%")
        
        if theme:
            # URL-decode the theme
            decoded_theme = urllib.parse.unquote(theme)
            query += " AND theme LIKE ?"
            params.append(f"%{decoded_theme}%")
        
        # Add pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # Fetch results
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON data if needed
            if 'additional_data' in result and result['additional_data']:
                try:
                    result['additional_data'] = json.loads(result['additional_data'])
                except:
                    pass
            results.append(result)
        
        # Get total count for pagination
        count_query = query.split(" LIMIT ")[0].replace("SELECT DISTINCT *", "SELECT COUNT(DISTINCT publication_number)")
        cursor.execute(count_query, params[:-2])
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "patents": results
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def fetch_and_store_patents_from_jplatpat(search_params):
    """
    Fetch patents from J-PlatPat API and store them in SQLite
    
    Args:
        search_params: Dict containing search parameters such as:
            - company: Company name to search for
            - theme: Classification/theme to search for
            - keyword: Keyword to search in title/abstract
            - limit: Maximum number of results to retrieve
            
    Returns:
        Dict containing search results and import status
    """
    try:
        # Initialize J-PlatPat client
        client = JPlatPatClient()
        print(f"Initialized J-PlatPat client, searching with params: {search_params}")
        
        # Extract search parameters
        company = search_params.get('company')
        theme = search_params.get('theme')
        keyword = search_params.get('keyword')
        limit = int(search_params.get('limit', 100))
        
        all_patents = []
        
        # Fetch patents based on provided parameters
        if company:
            print(f"Searching patents for company: {company}")
            company_patents = client.fetch_patents_by_company(company, limit=limit)
            all_patents.extend(company_patents)
            print(f"Found {len(company_patents)} patents for company {company}")
            
        if theme:
            print(f"Searching patents for theme/classification: {theme}")
            theme_patents = client.fetch_patents_by_theme(theme, limit=limit)
            all_patents.extend(theme_patents)
            print(f"Found {len(theme_patents)} patents for theme {theme}")
            
        if keyword:
            print(f"Searching patents with keyword: {keyword}")
            keyword_patents = client.fetch_patents_by_keyword(keyword, limit=limit)
            all_patents.extend(keyword_patents)
            print(f"Found {len(keyword_patents)} patents with keyword {keyword}")
            
        # Remove duplicates based on patent_id or publication_number
        unique_patents = {}
        for patent in all_patents:
            patent_id = patent.get('applicationNumber') or patent.get('publicationNumber')
            if patent_id and patent_id not in unique_patents:
                unique_patents[patent_id] = patent
                
        unique_patent_list = list(unique_patents.values())
        print(f"Found {len(unique_patent_list)} unique patents total")
        
        if not unique_patent_list:
            return {
                'message': 'No patents found matching the search criteria',
                'patents_found': 0,
                'patents_imported': 0
            }
            
        # Format patents for SQLite storage
        formatted_patents = []
        for patent in unique_patent_list:
            formatted_patent = client.format_patent_for_sqlite(patent)
            formatted_patents.append(formatted_patent)
            
        # Store in SQLite
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Insert with ON CONFLICT DO UPDATE to handle duplicates
        insert_count = 0
        update_count = 0
        
        for patent in formatted_patents:
            try:
                # Check if patent already exists
                cursor.execute("SELECT patent_id FROM patents WHERE patent_id = ?", (patent['patent_id'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing patent
                    cursor.execute("""
                    UPDATE patents SET 
                        publication_number = ?,
                        applicant = ?,
                        theme = ?,
                        title = ?,
                        abstract = ?,
                        filing_date = ?,
                        grant_date = ?,
                        assignee = ?,
                        inventor = ?,
                        additional_data = ?
                    WHERE patent_id = ?
                    """, (
                        patent['publication_number'],
                        patent['applicant'],
                        patent['theme'],
                        patent['title'],
                        patent['abstract'],
                        patent['filing_date'],
                        patent['grant_date'],
                        patent['assignee'],
                        patent['inventor'],
                        patent['additional_data'],
                        patent['patent_id']
                    ))
                    update_count += 1
                else:
                    # Insert new patent
                    cursor.execute("""
                    INSERT INTO patents (
                        patent_id, publication_number, applicant, theme, title, abstract,
                        filing_date, grant_date, assignee, inventor, additional_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        patent['patent_id'],
                        patent['publication_number'],
                        patent['applicant'],
                        patent['theme'],
                        patent['title'],
                        patent['abstract'],
                        patent['filing_date'],
                        patent['grant_date'],
                        patent['assignee'],
                        patent['inventor'],
                        patent['additional_data']
                    ))
                    insert_count += 1
            except Exception as e:
                print(f"Error processing patent {patent['patent_id']}: {str(e)}")
                
        conn.commit()
        conn.close()
        
        print(f"J-PlatPat import complete: {insert_count} patents added, {update_count} patents updated")
        
        return {
            'message': f'Successfully imported {insert_count + update_count} patents from J-PlatPat',
            'patents_found': len(unique_patent_list),
            'patents_imported': insert_count,
            'patents_updated': update_count,
            'sample_patents': formatted_patents[:5] if formatted_patents else []
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in fetch_and_store_patents_from_jplatpat: {error_message}")
        return {
            'status': 'error',
            'message': error_message,
            'error_type': type(e).__name__
        }

@app.route('/import-jplatpat', methods=['POST'])
def import_jplatpat_data():
    """Import data from J-PlatPat based on provided search parameters"""
    try:
        # Get search parameters from request
        search_params = request.json if request.is_json else {}
        print(f"J-PlatPat import request received with params: {search_params}")
        
        # Fetch and store data
        import_result = fetch_and_store_patents_from_jplatpat(search_params)
        
        if 'status' in import_result and import_result['status'] == 'error':
            return jsonify(import_result), 500
            
        # Use custom JSON encoder for NumPy types if needed
        response_data = {
            "status": "success", 
            "message": import_result.get('message', 'Patent data imported successfully'),
            "search_params": search_params,
            "results": import_result
        }
        
        # Use Flask's Response with our custom JSON encoder
        from flask import Response
        return Response(
            json.dumps(response_data, cls=NumpyJSONEncoder),
            mimetype='application/json'
        )
    except Exception as e:
        error_message = str(e)
        print(f"Error in import_jplatpat_data: {error_message}")
        return jsonify({
            "status": "error", 
            "message": error_message,
            "error_type": type(e).__name__
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Get database status"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Check if database exists and has data
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='patents'")
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM patents")
            patent_count = cursor.fetchone()[0]
        else:
            patent_count = 0
            
        conn.close()
        
        return jsonify({
            "status": "success",
            "database_initialized": table_exists,
            "patent_count": patent_count
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(SQLITE_DB_PATH):
        init_db()
    
    # Set Werkzeug options to be more lenient with URL parsing
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
