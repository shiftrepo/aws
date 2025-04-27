#!/bin/bash

# This script modifies the import statements in the J-PlatPat modules
# to make them compatible with the containerized environment

set -e

echo "Fixing import statements for J-PlatPat modules..."

# Fix importer.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/importer.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/importer.py

# Fix analyzer.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/analyzer.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/analyzer.py

# Fix db_manager.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/db_manager.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/db_manager.py

# Fix cli.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/cli.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/cli.py

# Fix scraper.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/scraper.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/scraper.py

# Fix models.py
sed -i 's/from app.patent_system.jplatpat/from jplatpat/g' /app/jplatpat/models.py
sed -i 's/import app.patent_system.jplatpat/import jplatpat/g' /app/jplatpat/models.py

echo "Import statements fixed successfully"
