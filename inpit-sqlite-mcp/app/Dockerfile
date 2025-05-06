FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make sure server.py and start_server.sh are executable
RUN chmod +x server.py start_server.sh

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["./start_server.sh"]
