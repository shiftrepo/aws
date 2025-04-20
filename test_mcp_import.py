#!/usr/bin/env python3
import sys
import traceback
from importlib import import_module

print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    print("Attempting to import mcp_patent_server...")
    from app.patent_system import mcp_patent_server
    print("Successfully imported mcp_patent_server")
    
    print("\nAvailable tools:")
    for tool in mcp_patent_server.get_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nAvailable resources:")
    for resource in mcp_patent_server.get_resources():
        print(f"- {resource['uri']}: {resource['description']}")
    
except Exception as e:
    print(f"Import failed with error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
