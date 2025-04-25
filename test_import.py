#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to diagnose import issues with the MCP Patent Server module.
"""

import sys
import os
import traceback

# Add the current directory to Python path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Current working directory:", os.getcwd())
print("Python path:")
for p in sys.path:
    print(f"  - {p}")

# Try direct import from app.patent_system
try:
    print("\nTrying to import mcp_patent_server directly...")
    from app.patent_system.mcp_patent_server import get_tools, get_resources
    print("SUCCESS: Direct import worked!")
    print("Available tools:", get_tools())
except Exception as e:
    print("ERROR:", e)
    print("\nDetailed traceback:")
    traceback.print_exc()

# Try to access and list the app/patent_system directory
try:
    patent_system_dir = os.path.join(os.getcwd(), 'app', 'patent_system')
    print(f"\nListing files in {patent_system_dir}:")
    for f in os.listdir(patent_system_dir):
        print(f"  - {f}")
except Exception as e:
    print("ERROR listing directory:", e)
