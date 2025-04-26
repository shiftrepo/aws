FROM python:3.9-slim

WORKDIR /app

# Install SQLite and required packages
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Set proper permissions
RUN chmod 755 app.py

# Create directory for data
RUN mkdir -p /data

# Set volume
VOLUME /data

# Run the application
CMD ["python", "app.py"]
