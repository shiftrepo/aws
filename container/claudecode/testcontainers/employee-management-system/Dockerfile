FROM docker.io/eclipse-temurin:21-jdk-jammy

# Install Maven and essential tools
RUN apt-get update && \
    apt-get install -y \
    maven \
    curl \
    git \
    vim \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Create .m2 directory for Maven
RUN mkdir -p /root/.m2

# Pre-download Maven dependencies for faster builds
COPY pom.xml ./
RUN mvn dependency:go-offline -B || true

# Copy source code
COPY . .

# Expose application port
EXPOSE 8080

# Default command for development
CMD ["mvn", "spring-boot:run"]