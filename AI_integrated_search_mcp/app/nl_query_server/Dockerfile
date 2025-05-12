FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    awscli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py /app/
COPY *.sh /app/
COPY templates/ /app/templates/

# Make scripts executable
RUN chmod +x /app/*.sh

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Set ownership to root
RUN chown -R root:root /app

# Expose port for MCP API
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
