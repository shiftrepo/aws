#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Try to import the MCP server module
try:
    from app.patent_system.mcp_patent_server import get_tools, get_resources
    print("Successfully imported patent MCP server module")
    
    # Get and print available tools and resources
    tools = get_tools()
    resources = get_resources()
    
    print("\nAvailable tools:")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nAvailable resources:")
    for resource in resources:
        print(f"- {resource['uri']}: {resource['description']}")
    
    print("\nImport test successful!")
except ImportError as e:
    print(f"Failed to import patent MCP server module: {e}")
    sys.exit(1)
