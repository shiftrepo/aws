# AI Integrated Search MCP

A system that combines SQLite databases with natural language querying powered by AWS Bedrock, designed to be used as MCP servers for Dify integration.

## Overview

This system provides a comprehensive solution for interacting with SQLite databases through both direct SQL queries and natural language queries. It consists of three main components:

1. **Database Service**: A service that downloads SQLite databases from S3 and provides an API to interact with them
2. **Natural Language Query Service**: A service that uses AWS Bedrock models to translate natural language queries into SQL
3. **Web UI**: A user interface that allows users to interact with both services through a web browser

## Architecture

The system is built using a containerized microservices architecture:

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │
│    Web UI     │◄────►│  Database API │◄────►│     AWS S3    │
│   (Port 5002) │      │   (Port 5003) │      │               │
│               │      │               │      └───────────────┘
└───────┬───────┘      └───────┬───────┘
        │                      │
        │                      │
        │              ┌───────┴───────┐      ┌───────────────┐
        │              │  NL Query API │      │  AWS Bedrock  │
        └──────────────►   (Port 5004) │◄────►│     Claude    │
                       │               │      │               │
                       └───────────────┘      └───────────────┘
```

## Prerequisites

- podman and podman-compose
- AWS credentials configured (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
- Access to AWS Bedrock services (Claude, Titan Embedding, and Rerank models)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_integrated_search_mcp
```

### 2. Set Up AWS Credentials

Create a source file with your AWS credentials that can be sourced:

```bash
mkdir -p ~/.aws
cat > ~/.aws/source.aws << EOF
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=your_aws_region
EOF
chmod 600 ~/.aws/source.aws
```

### 3. Start the Services

```bash
source ~/.aws/source.aws  # Source AWS credentials
./scripts/start_services.sh
```

The script will:
- Check for AWS credentials
- Start all services using podman-compose
- Verify that all services are running
- Display the URLs for accessing the services

### 4. Access the Web UI

Open a web browser and navigate to:
```
http://localhost:5002
```

## Services

### Database Service (Port 5003)

This service downloads SQLite databases from S3 and provides an API to interact with them:

- `/health` - Health check endpoint
- `/databases` - List available databases
- `/schema/{db_name}` - Get schema for a specific database
- `/execute/{db_name}` - Execute SQL query on a database
- `/sample_queries/{db_name}` - Get sample queries for a database
- `/docs` - API documentation

### Natural Language Query Service (Port 5004)

This service translates natural language queries into SQL:

- `/health` - Health check endpoint
- `/query/{db_name}` - Process natural language query
- `/docs` - API documentation

### Web UI (Port 5002)

The web interface allows users to:
- View available databases
- Execute SQL queries with syntax highlighting
- Ask natural language questions about the databases
- View database schemas
- Use sample queries as templates
- Export query results as CSV

## Using the System

### Direct SQL Queries

1. Navigate to the Web UI at http://localhost:5002
2. Select a database
3. Use the SQL Query tab to write and execute SQL queries
4. View the results in the table format

### Natural Language Queries

1. Navigate to the Web UI at http://localhost:5002
2. Select a database
3. Switch to the Natural Language Query tab
4. Type your question in plain English
5. View the generated SQL, results, and AI-generated explanation

### Database Schema

1. Navigate to the Web UI at http://localhost:5002
2. Select a database
3. Switch to the Database Schema tab
4. Browse through the tables and their columns

## Databases

The system works with two databases:

1. **Inpit Database**: Located at `s3://ndi-3supervision/MIT/demo/inpit/inpit.db`
2. **BigQuery Database**: Located at `s3://ndi-3supervision/MIT/demo/GCP/google_patents_gcp.db`

## MCP Integration

Both the Database API and Natural Language Query API are designed to be used as MCP servers for Dify integration. They provide OpenAPI specifications at the `/openapi` endpoint.

### Example MCP Configuration for Dify

```yaml
name: ai-integrated-search
server_url: http://localhost:5003
tools:
  - name: execute_sql
    description: Execute SQL query on a database
    parameters:
      - name: db_name
        description: Database name (input or bigquery)
        required: true
        type: string
        enum: [input, bigquery]
      - name: query
        description: SQL query to execute
        required: true
        type: string
resources:
  - name: get_schema
    description: Get database schema
    url: /schema/{db_name}
  - name: get_sample_queries
    description: Get sample SQL queries for a database
    url: /sample_queries/{db_name}
```

## Admin Commands

### Starting Services

```bash
./scripts/start_services.sh
```

### Stopping Services

```bash
./scripts/stop_services.sh
```

### Checking Health

```bash
./scripts/check_health.sh
```

## Troubleshooting

### Container Connectivity Issues

If services can't communicate with each other, check the network configuration:

```bash
podman network ls
podman inspect mcp-network
```

### Database Download Issues

If databases fail to download, check:

1. AWS credentials are properly set
2. The S3 buckets are accessible
3. The database service logs:

```bash
podman logs sqlite-db
```

### Service Health Issues

Run the health check script:

```bash
./scripts/check_health.sh
```

## Security Notes

- AWS credentials are never stored in the container or code files
- Credentials are obtained from environment variables set via source command
- The system is designed for internal use and should not be exposed to the internet without proper security measures
