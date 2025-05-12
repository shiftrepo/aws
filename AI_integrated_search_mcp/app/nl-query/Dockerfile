FROM python:3.10-slim

WORKDIR /app

# Install necessary packages for network troubleshooting
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    iputils-ping \
    net-tools \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for API
EXPOSE 5000

# Command to run the API
CMD ["python", "app.py"]
