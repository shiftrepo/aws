#!/usr/bin/env python3
"""
Execute GraphDB creation script against Neo4j
This script reads the Cypher file and executes it against Neo4j in manageable chunks
"""

import requests
import json
import sys
import re

def execute_cypher_query(query, neo4j_url="http://localhost:7474", username="neo4j", password="password", database="neo4j"):
    """Execute a single Cypher query against Neo4j"""
    
    # Neo4j transaction endpoint
    tx_url = f"{neo4j_url}/db/{database}/tx/commit"
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {requests.auth._basic_auth_str(username, password)}"
    }
    
    payload = {
        "statements": [
            {
                "statement": query
            }
        ]
    }
    
    # Execute the query
    try:
        response = requests.post(tx_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('errors'):
            print(f"Error executing query: {result['errors']}")
            return False
            
        print(f"Query executed successfully. Results: {len(result.get('results', []))}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return False

def split_cypher_file(file_path):
    """Split Cypher file into individual statements"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments (lines starting with //)
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove full-line comments
        if line.strip().startswith('//'):
            continue
        # Remove inline comments
        if '//' in line:
            line = line.split('//')[0].rstrip()
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Split by semicolons but be careful with semicolons inside strings
    statements = []
    current_statement = ""
    in_string = False
    escape_next = False
    
    for char in cleaned_content:
        if escape_next:
            current_statement += char
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            current_statement += char
            continue
            
        if char in ["'", '"'] and not escape_next:
            in_string = not in_string
            current_statement += char
            continue
            
        if char == ';' and not in_string:
            statement = current_statement.strip()
            if statement:
                statements.append(statement)
            current_statement = ""
            continue
            
        current_statement += char
    
    # Add the last statement if it exists
    final_statement = current_statement.strip()
    if final_statement:
        statements.append(final_statement)
    
    return [stmt for stmt in statements if stmt]

def main():
    """Main execution function"""
    
    cypher_file = "/root/aws.git/container/graphRAG/sample/create_graphdb.cypher"
    
    print("Reading Cypher file...")
    try:
        statements = split_cypher_file(cypher_file)
        print(f"Found {len(statements)} statements to execute")
    except Exception as e:
        print(f"Error reading Cypher file: {e}")
        sys.exit(1)
    
    print("Connecting to Neo4j and executing statements...")
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        print(f"\nExecuting statement {i}/{len(statements)}:")
        print(f"Statement preview: {statement[:100]}{'...' if len(statement) > 100 else ''}")
        
        if execute_cypher_query(statement):
            success_count += 1
            print("✓ Success")
        else:
            error_count += 1
            print("✗ Failed")
    
    print(f"\n=== Execution Summary ===")
    print(f"Total statements: {len(statements)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    
    if error_count == 0:
        print("🎉 All statements executed successfully!")
    else:
        print("⚠️  Some statements failed. Please review the errors above.")
    
    return error_count == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)