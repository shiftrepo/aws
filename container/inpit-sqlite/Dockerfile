FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    awscli \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts and files
COPY *.py /app/
COPY *.sh /app/

# Make scripts executable
RUN chmod +x /app/*.sh

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose port for SQLite Web UI
EXPOSE 5001

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
