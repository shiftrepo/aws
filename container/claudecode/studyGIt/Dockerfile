FROM node:18-alpine

# Install curl for healthcheck
RUN apk --no-cache add curl

# Create app user with proper permissions
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy package.json first for better layer caching
COPY package.json ./

# Set proper ownership
RUN chown -R appuser:appgroup /app

# Switch to app user
USER appuser

# Install dependencies
RUN npm install

# Switch back to root for copying files
USER root

# Copy all application code
COPY . .

# Set proper ownership again
RUN chown -R appuser:appgroup /app

# Switch to app user for running the app
USER appuser

# Set environment variables
ENV NODE_ENV=development
ENV PORT=3000

# Expose the application port
EXPOSE 3000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "run", "dev"]