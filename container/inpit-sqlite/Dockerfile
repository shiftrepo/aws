FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    awscli \
    curl \
    gosu \
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

# Create the ec2-user user with UID/GID 1000
RUN groupadd -g 1000 ec2-user && \
    useradd -u 1000 -g 1000 -d /home/ec2-user -m ec2-user && \
    chown -R ec2-user:ec2-user /app

# Expose port for SQLite Web UI
EXPOSE 5001

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
