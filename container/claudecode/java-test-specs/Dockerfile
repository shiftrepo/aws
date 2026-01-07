FROM maven:3.9-eclipse-temurin-17

# Use the default maven working directory
WORKDIR /usr/src/app

# Copy the entire project
COPY . .

# Default command for building the project
CMD ["mvn", "clean", "package"]