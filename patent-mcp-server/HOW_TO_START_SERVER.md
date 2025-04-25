# How to Start the Patent MCP Server

There are two ways to start the Patent MCP server:

## Method 1: Using Docker (Recommended)

Docker provides an isolated environment with all dependencies pre-installed. This is the recommended method.

```bash
# Navigate to the patent-mcp-server directory
cd patent-mcp-server

# Start the server with Docker Compose
docker-compose up
```

The server will be available at http://localhost:8000

To run in detached mode (background):

```bash
docker-compose up -d
```

To stop the server:

```bash
docker-compose down
```

## Method 2: Running Directly

If you prefer not to use Docker, you can run the server directly. Make sure you have all required dependencies installed (see requirements.txt).

```bash
# Navigate to the patent-mcp-server directory
cd patent-mcp-server

# Use the start script
./start_server.sh
```

OR manually:

```bash
# Navigate to the server directory
cd patent-mcp-server

# Set Python path to include parent directory
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))

# Go to app directory and start server
cd app
python3 server.py
```

## Verify the Server is Running

Once started, you can verify the server is running by:

```bash
# Check if the server is responding
curl http://localhost:8000
```

You should see output like:

```json
{"status":"ok","message":"Patent MCP Server is running"}
```

## Testing with Japanese Applicant Names

To test with Japanese applicant names (e.g., "テック株式会社"), remember to URL-encode the name:

```bash
# Use the helper script to generate a properly encoded URL
cd patent-mcp-server/app
./curl_examples.sh "テック株式会社"

# Or test directly with the encoded URL
curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
```

For more details on URL encoding, see [handling_non_ascii_characters.md](./docs/handling_non_ascii_characters.md).
