FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets
COPY dist/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
