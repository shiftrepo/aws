#!/bin/bash
# Script to execute SQL queries against the JplatPat database

# Forward all arguments to the SQL query tool
python /app/sql_query_tool.py "$@"
