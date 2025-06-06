FROM node:18-alpine

WORKDIR /app

# Copy package.json first for better layer caching
COPY package.json ./

# Copy all application code
COPY . .

# Set environment variables
ENV NODE_ENV=development
ENV PORT=3000

# Expose the application port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "dev"]