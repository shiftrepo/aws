FROM python:3.10-slim

WORKDIR /app

# Install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py /app/
COPY templates/ /app/templates/
COPY static/ /app/static/

# Add the MCP endpoint patch
COPY mcp_endpoint_patch.py /app/
COPY patched_entrypoint.sh /app/
RUN chmod +x /app/patched_entrypoint.sh

# Default port
ENV PORT=5002

EXPOSE 5002

# Use our custom entrypoint
CMD ["/bin/bash", "/app/patched_entrypoint.sh"]
