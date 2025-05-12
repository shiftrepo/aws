FROM python:3.10-slim

# Create ec2-user user and group with specific UID/GID
RUN groupadd -g 1000 ec2-user && \
    useradd -u 1000 -g ec2-user -s /bin/bash -m ec2-user

WORKDIR /app

# Install necessary packages for network troubleshooting and S3 downloads
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    iputils-ping \
    net-tools \
    netcat-openbsd \
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

# Set proper ownership for application files
RUN chown -R ec2-user:ec2-user /app

# Expose port for API
EXPOSE 5000

# Switch to ec2-user
USER ec2-user

# Command to run the API
CMD ["python", "app.py"]
