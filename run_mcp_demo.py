#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Patent System Demo Runner

This script ensures proper module importing when running the MCP demo
from the project root directory.
"""

import sys
import os
import traceback

# Add the current directory to Python path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and find where the error is occurring
try:
    # Import and run the demo
    from app.patent_system.mcp_demo import main
    main()
except ImportError as e:
    print("ImportError:", e)
    print("\nDetailed traceback:")
    traceback.print_exc()
    print("\nPython path:")
    for p in sys.path:
        print(f"  - {p}")
