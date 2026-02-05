FROM mcr.microsoft.com/playwright:v1.40.0-focal

# Set working directory
WORKDIR /tests

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy test files
COPY tests ./tests
COPY page-objects ./page-objects
COPY fixtures ./fixtures
COPY utils ./utils
COPY playwright.config.ts ./

# Create directories for reports
RUN mkdir -p playwright-report test-results screenshots coverage

# Set environment variables
ENV CI=true
ENV PLAYWRIGHT_HEADLESS=true

# Run tests by default
CMD ["npm", "test"]
