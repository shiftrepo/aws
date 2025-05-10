FROM python:3.9-slim

WORKDIR /app

# Install dependencies for matplotlib and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY patent_trend_analyzer.py .
COPY *.py ./

# Create output directory for generated files
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a non-root user to run the application
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Command to run the application
ENTRYPOINT ["python", "patent_trend_analyzer.py"]
# The applicant name and db_type will be passed as arguments at runtime
