FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome Driver (simpler approach)
RUN apt-get update && apt-get install -y chromium-driver \
    && ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY app/patent_system/jplatpat/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for SQL query tool
RUN pip install --no-cache-dir pandas tabulate

# Copy jplatpat module
COPY app/patent_system/jplatpat /app/jplatpat

# Create a directory for the database
RUN mkdir -p /data

# Set environment variable for database location
ENV PATENTS_DB_PATH=/data/patents.db

# Copy the wrapper module and fix-imports script
COPY container/jplatpat/wrapper.py /app/wrapper.py
COPY container/jplatpat/fix-imports.sh /app/fix-imports.sh
COPY container/jplatpat/sql_query_tool.py /app/sql_query_tool.py
COPY container/jplatpat/sql.sh /app/sql.sh
RUN chmod +x /app/wrapper.py /app/fix-imports.sh /app/sql_query_tool.py /app/sql.sh

# Fix import statements in the module
RUN /app/fix-imports.sh

# Set working directory to the jplatpat module
WORKDIR /app

# Create an entrypoint script
COPY container/jplatpat/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
