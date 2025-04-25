# Patent MCP Server

A specialized MCP (Model Context Protocol) server that provides tools and resources for patent analysis, focusing on Japanese applicant data.

## Overview

This server provides tools for patent examiners and researchers to analyze applicant data, generate reports, and compare applicants. It integrates with the MCP protocol to make these capabilities available to compatible clients.

## Features

- Comprehensive applicant summaries
- Visual reports with charts and statistics
- Assessment ratio analysis
- Technical field distribution analysis
- Competitor comparison
- PDF report generation

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Running with Docker

```bash
cd patent-mcp-server
docker-compose up -d
```

The server will be available at `http://localhost:8000`.

## API Usage

The server provides several REST API endpoints for patent analysis:

- `/applicant/{applicant_name}` - Get a comprehensive summary for an applicant
- `/report/{applicant_name}` - Generate a visual report for an applicant
- `/assessment/{applicant_name}` - Analyze assessment ratios for an applicant
- `/technical/{applicant_name}` - Analyze technical fields for an applicant
- `/compare/{applicant_name}` - Compare an applicant with competitors

### Important: URL Encoding for Japanese Characters

When using the API with non-ASCII characters (like Japanese company names), you must properly URL-encode the parameters. For example, to query data for "テック株式会社":

```bash
# INCORRECT - Will fail with "Invalid HTTP request received"
curl "http://localhost:8000/applicant/テック株式会社"

# CORRECT - Properly URL encoded
curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
```

We provide helper tools to assist with URL encoding:

1. `curl_examples.sh` - Shell script that demonstrates proper curl commands with encoding
   ```bash
   ./curl_examples.sh "テック株式会社"  # Generate encoded curl command for a specific applicant
   ```

2. `url_encode_demo.py` - Python script that demonstrates URL encoding in code
   ```bash
   python url_encode_demo.py
   ```

3. `test_url_encoding.py` - Test script to validate URL encoding works correctly
   ```bash
   python test_url_encoding.py "テック株式会社"
   ```

For more details, see [handling_non_ascii_characters.md](./docs/handling_non_ascii_characters.md).

## MCP Integration

This server implements the Model Context Protocol, providing tools and resources that can be consumed by MCP clients. Key MCP endpoints:

- `/tools` - List available tools
- `/tools/execute` - Execute a tool
- `/resources` - List available resources
- `/resources/access` - Access a resource

## Development

To modify or extend the server:

1. Update tool and resource implementations in `app/patent_system/mcp_patent_server.py`
2. Run the server in development mode for auto-reloading
   ```bash
   cd app
   python server.py
   ```

## License

Copyright © 2025
