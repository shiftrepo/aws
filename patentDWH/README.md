# patentDWH (Patent Data Warehouse)

patentDWH is a patent data warehouse system that provides SQLite-based storage and querying capabilities for patent data through a user-friendly web interface and MCP server.

## Overview

This system consists of two main components:

1. **Patent Database (patent-dwh-db)**: A SQLite-based database with a web interface for directly querying patent data.
2. **MCP Server (patent-dwh-mcp)**: A Model Context Protocol (MCP) server that allows AI assistants like Claude to interact with the patent database.

The system provides access to three different patent databases:

- **INPIT Database**: Patent data from the Japan Patent Office.
- **Google Patents GCP Database**: Patent data from Google Patents sourced from BigQuery.
- **Google Patents S3 Database**: Patent data from Google Patents stored in S3.

## Features

- **Web UI for SQL Queries**: Direct web interface for executing SQL queries against all databases.
- **SQL Examples**: Pre-built SQL query examples for common patent searches.
- **MCP Integration**: Full MCP server implementation for AI assistant integration.
- **Multi-Database Support**: Query different patent databases with the same interface.
- **RESTful API**: API endpoints for programmatic access to the databases.

## Requirements

- Podman or Docker
- Podman Compose or Docker Compose
- Internet connection (for initial data download)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd patentDWH
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```

3. The setup script will:
   - Check for required dependencies
   - Build and start the containers
   - Verify services are running
   - Display connection information

## Usage

### Web Interface

- **Database UI**: Access at http://localhost:5002/
- The web interface provides three main sections:
  - INPIT SQL Examples
  - Google Patents GCP Examples
  - Google Patents S3 Examples
  - Free SQL Query Tool

### MCP Server

The MCP server runs at http://localhost:8080/ and provides the following tools:

1. **patent_sql_query**: Execute SQL queries on any of the patent databases.
2. **get_database_info**: Get information about the available patent databases.
3. **get_sql_examples**: Get example SQL queries for a specific database type.

To use with Claude or another AI assistant that supports MCP:

```json
{
  "serverName": "patentDWH",
  "description": "Patent DWH MCP Server",
  "url": "http://localhost:8080/api/v1/mcp"
}
```

## Data Sources

The system downloads and processes data from:

1. INPIT CSV data: Sourced from S3 bucket `ndi-3supervision`
2. Google Patents GCP data: Sourced from BigQuery
3. Google Patents S3 data: Sourced from S3 bucket `ndi-3supervision`

## Directory Structure

```
patentDWH/
├── app/                    # MCP Server files
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   └── server.py
├── data/                   # Data storage directory
│   └── db/                 # SQLite database files
├── db/                     # Database server files
│   ├── Dockerfile
│   ├── app.py
│   ├── download_data.py
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── static/
│   └── templates/
├── podman-compose.yml      # Container orchestration
├── setup.sh                # Setup script
└── README.md               # This file
```

## Troubleshooting

If services do not start properly:

1. Check container logs:
   ```
   podman-compose logs -f
   ```

2. Verify database files are downloaded:
   ```
   ls -la data/
   ```

3. Restart services:
   ```
   podman-compose down
   podman-compose up -d
   ```

## License

[Include license information]
