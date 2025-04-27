#!/usr/bin/env python3
"""
SQL Query Tool for JplatPat Container's SQLite Database

This tool allows users to execute SQL queries against the jplatpat SQLite database.
"""

import os
import sqlite3
import argparse
import json
import pandas as pd
import sys
from datetime import datetime
from tabulate import tabulate

def execute_query(query, format_output="table", output_file=None, limit=None, db_path=None):
    """
    Execute an SQL query against the patent database
    
    Args:
        query: SQL query to execute
        format_output: Output format (table, csv, json)
        output_file: File to write results to (optional)
        limit: Maximum number of rows to return (optional)
        db_path: Path to the database file (optional)
    
    Returns:
        Query results in the specified format
    """
    # Use provided db_path or get it from environment variable
    database_path = db_path or os.environ.get("PATENTS_DB_PATH", "/data/patents.db")
    
    if not os.path.exists(database_path):
        print(f"Error: Database not found at {database_path}")
        return None
    
    # Add LIMIT clause if requested and not already in query
    if limit is not None and "LIMIT" not in query.upper():
        query = f"{query} LIMIT {limit}"
    
    try:
        conn = sqlite3.connect(database_path)
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Use pandas to execute query and get results
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Return empty result for queries that don't return data (like INSERT, UPDATE)
        if df.empty and not query.upper().startswith("SELECT"):
            return {"message": "Query executed successfully. No results to display."}
        
        # Format output according to user preference
        if format_output == "csv":
            output = df.to_csv(index=False)
            if output_file:
                df.to_csv(output_file, index=False)
                return {"message": f"Results saved to {output_file}"}
            return output
            
        elif format_output == "json":
            # Convert datetime objects to ISO format strings for JSON serialization
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
                
            # Handle duplicate column names by adding suffixes
            df_columns = df.columns.tolist()
            if len(df_columns) != len(set(df_columns)):
                # Identify duplicate columns and rename them
                seen = {}
                for i, col in enumerate(df_columns):
                    if col in seen:
                        seen[col] += 1
                        df_columns[i] = f"{col}_{seen[col]}"
                    else:
                        seen[col] = 0
                df.columns = df_columns
            
            output = df.to_json(orient="records", date_format="iso")
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                return {"message": f"Results saved to {output_file}"}
            return output
            
        else:  # Default to table format
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(tabulate(df, headers='keys', tablefmt='psql'))
                return {"message": f"Results saved to {output_file}"}
            return tabulate(df, headers='keys', tablefmt='psql')
            
    except sqlite3.Error as e:
        return {"error": f"SQLite error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def list_tables(db_path=None):
    """List all tables in the database"""
    query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' 
    ORDER BY name;
    """
    return execute_query(query, db_path=db_path)

def show_schema(table_name, db_path=None):
    """Show schema for a specific table"""
    query = f"""
    SELECT sql FROM sqlite_master 
    WHERE type='table' AND name='{table_name}';
    """
    return execute_query(query, db_path=db_path)

def show_count(table_name, db_path=None):
    """Show row count for a specific table"""
    query = f"""
    SELECT COUNT(*) as count FROM {table_name};
    """
    return execute_query(query, db_path=db_path)

def main():
    parser = argparse.ArgumentParser(description='SQL Query Tool for JplatPat Database')
    parser.add_argument('-q', '--query', help='SQL query to execute')
    parser.add_argument('-f', '--file', help='File containing SQL query')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('--format', choices=['table', 'csv', 'json'], default='table', 
                        help='Output format (default: table)')
    parser.add_argument('-l', '--limit', type=int, help='Limit number of results')
    parser.add_argument('--tables', action='store_true', help='List all tables')
    parser.add_argument('--schema', help='Show schema for a table')
    parser.add_argument('--count', help='Show row count for a table')
    parser.add_argument('--db', help='Path to the database file')
    
    args = parser.parse_args()
    
    database_path = args.db or os.environ.get("PATENTS_DB_PATH", "/data/patents.db")
    
    # Handle database path
    if not os.path.exists(database_path):
        print(f"Error: Database not found at {database_path}")
        print(f"Please ensure the database exists or set the PATENTS_DB_PATH environment variable.")
        sys.exit(1)
    
    # Execute the requested operation
    if args.tables:
        result = list_tables(database_path)
        print(result)
        
    elif args.schema:
        result = show_schema(args.schema, database_path)
        print(result)
        
    elif args.count:
        result = show_count(args.count, database_path)
        print(result)
        
    elif args.query:
        result = execute_query(args.query, args.format, args.output, args.limit, database_path)
        if isinstance(result, dict) and "message" in result:
            print(result["message"])
        elif isinstance(result, dict) and "error" in result:
            print(result["error"])
        else:
            print(result)
            
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                query = f.read()
            result = execute_query(query, args.format, args.output, args.limit, database_path)
            if isinstance(result, dict) and "message" in result:
                print(result["message"])
            elif isinstance(result, dict) and "error" in result:
                print(result["error"])
            else:
                print(result)
        except FileNotFoundError:
            print(f"Error: Query file {args.file} not found")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
