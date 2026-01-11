# ========================================================================
# Backend Dockerfile - Spring Boot Application
# ========================================================================
# Base image: Eclipse Temurin JRE 17 (Alpine for minimal size)
# JAR file must exist before build (built by CI/CD pipeline)
# ========================================================================

FROM docker.io/library/eclipse-temurin:17-jre-alpine

# Working directory
WORKDIR /app

# Copy JAR file from target/ (built by CI/CD mvn package)
COPY target/*.jar app.jar

# Expose port 8080 (internal only, not published externally)
EXPOSE 8080

# Health check using Spring Boot Actuator
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "app.jar"]
