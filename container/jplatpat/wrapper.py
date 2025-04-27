#!/usr/bin/env python3
"""
Wrapper module to adapt the jplatpat module for containerized usage.
This ensures imports work correctly inside the container.
"""

import os
import sys
import logging

# Configure database path to use the volume
if os.environ.get('PATENTS_DB_PATH'):
    os.environ['JPLATPAT_DATABASE_PATH'] = os.environ['PATENTS_DB_PATH']

# Add the app directory to sys.path so imports work correctly
sys.path.insert(0, '/app')

# Create a module structure that matches expected imports
import jplatpat
sys.modules['app'] = type('AppModule', (), {})()
sys.modules['app.patent_system'] = type('PatentSystemModule', (), {})()
sys.modules['app.patent_system.jplatpat'] = jplatpat

# Now import CLI after adjusting the module structure
from jplatpat import cli

if __name__ == "__main__":
    # Directly pass arguments to CLI
    cli.main()
