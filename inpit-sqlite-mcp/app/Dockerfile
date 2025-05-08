FROM python:3.9-slim

# Set non-interactive mode for debian packages
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install AWS CLI and user management tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Add ec2-user (UID 1000) to match EC2 instance standard user
RUN groupadd -g 1000 ec2-user && \
    useradd -u 1000 -g 1000 -ms /bin/bash ec2-user && \
    echo "ec2-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make sure scripts are executable
RUN chmod +x server.py start_server.sh entrypoint.sh

# Create non-mounted directories with proper permissions
RUN mkdir -p /app/templates
RUN chown -R ec2-user:ec2-user /app/templates && \
    chmod -R 755 /app/templates

# Expose the port the app runs on
EXPOSE 8000

# Set entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
