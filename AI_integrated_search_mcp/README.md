# AI Integrated Search MCP

AI Integrated Search MCP is a system that combines SQLite database access with natural language querying capabilities powered by AWS Bedrock. The system provides a web-based user interface for executing both SQL and natural language queries against a SQLite database.

## Features

- **SQLite Database API**: Direct SQL query execution with API endpoints for database interaction
- **Natural Language Querying**: Convert natural language questions into SQL using AWS Bedrock's Claude model
- **Web UI**: User-friendly interface with:
  - SQL query editor with sample queries
  - Natural language question interface
  - Database schema visualization
  - Results display with export capabilities
- **MCP Protocol Support**: Implements the Model Context Protocol for integration with tools like Dify

## Architecture

The system consists of three main components running as containers:

1. **SQLite Database Container (Port 5001)**
   - Provides API access to the SQLite database
   - Supports downloading database files from S3
   - Includes schema exploration and SQL execution endpoints
   
2. **Natural Language Query Container (Port 8000)**
   - Provides MCP-compatible API for natural language processing
   - Uses AWS Bedrock AI models:
     - Claude 3.7 Sonnet for SQL generation
     - Titan Embedding for text embedding
     - Amazon Reranker for result optimization
   
3. **Web UI Container (Port 5002)**
   - User-friendly web interface for both SQL and NL queries
   - Database schema visualization
   - Query results display and export

## Prerequisites

- Podman and podman-compose installed
- AWS account with Bedrock access and appropriate permissions
- S3 bucket with a SQLite database file (or the system can create an empty one)

## Environment Variables

The following environment variables need to be set:

```bash
# Required
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=ap-northeast-1  # or your preferred region

# Optional (SQLite database location in S3)
export S3_DB_BUCKET=your-s3-bucket
export S3_DB_KEY=path/to/your/db.sqlite
```

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/AI_integrated_search_mcp.git
cd AI_integrated_search_mcp
```

2. Set up environment variables (see above)

3. Make the scripts executable:

```bash
chmod +x start_services.sh stop_services.sh
```

4. Start the services:

```bash
sudo ./start_services.sh
```

Or, if you've added your user to the `podman` group:

```bash
./start_services.sh
```

## Usage

After starting the services, you can access the Web UI at:

```
http://localhost:5002
```

The Web UI provides three main sections:

- **SQL Query**: Direct SQL querying with syntax highlighting
- **Natural Language Query**: Ask questions in plain language
- **Database Schema**: View tables and columns in the database

## API Endpoints

### SQLite API (Port 5001)

- `/health`: Health check endpoint
- `/tables`: List all tables in the database
- `/tables/{table_name}`: Get details about a specific table
- `/execute`: Execute SQL queries
- `/sample_queries`: Get sample SQL queries

### Natural Language Query API (Port 8000)

- `/health`: Health check endpoint
- `/query`: Process natural language queries
- MCP resources:
  - `/schema`: Get database schema
  - `/sample_queries`: Get sample natural language queries
- MCP tools:
  - `generate_sql`: Generate SQL from natural language
  - `execute_nl_query`: Execute natural language queries

## Stopping the Services

To stop all services:

```bash
sudo ./stop_services.sh
```

## Security Considerations

- The system uses environment variables for AWS credentials instead of hardcoding them
- Root execution is required for podman in some environments
- Access to the Web UI and APIs should be restricted in production environments

## Dify Integration

The natural language query container implements the MCP protocol, making it compatible with Dify and similar platforms. To connect to Dify:

1. In Dify, go to Model Providers > Add Custom Provider
2. Select "Model Context Protocol (MCP)"
3. Enter the URL of your MCP server (e.g., `http://your-server-ip:8000`)
4. Select the available tools and resources to use

## License

This project is licensed under the MIT License - see the LICENSE file for details.
