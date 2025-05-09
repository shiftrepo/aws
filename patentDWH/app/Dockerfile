FROM python:3.9-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Make the entry script executable
RUN chmod +x /app/entrypoint.sh

# Expose the API port
EXPOSE 8080

# Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
