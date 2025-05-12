FROM python:3.10-slim

WORKDIR /app

# Install necessary packages for network troubleshooting and S3 downloads
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    iputils-ping \
    net-tools \
    netcat \
    sqlite3 \
    awscli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for SQLite databases
RUN mkdir -p /app/data

# Copy application code
COPY . .

# Expose port for API
EXPOSE 5000

# Command to run the API
CMD ["python", "app.py"]
