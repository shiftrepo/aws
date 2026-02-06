FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy the JAR file
COPY target/orgmgmt-backend.jar /app/app.jar

# Expose port
EXPOSE 8080

# Set environment variables
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Run the application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]
