# Employee Management System - Setup Guide

Complete setup guide for the containerized employee management system with PostgreSQL and comprehensive testing capabilities.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: At least 2GB free space for containers and data
- **Network**: Internet connection for downloading container images

### Required Software

#### 1. Container Runtime
**Option A: podman (Recommended)**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y podman podman-compose

# CentOS/RHEL/Fedora
sudo dnf install -y podman podman-compose

# macOS with Homebrew
brew install podman podman-compose

# Start podman machine (macOS/Windows)
podman machine init
podman machine start
```

**Option B: Docker (Alternative)**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Add user to docker group
```

#### 2. Java Development Kit (Optional - for local development)
```bash
# Ubuntu/Debian
sudo apt-get install -y openjdk-17-jdk

# CentOS/RHEL/Fedora
sudo dnf install -y java-17-openjdk-devel

# macOS with Homebrew
brew install openjdk@17

# Verify installation
java -version
```

#### 3. Maven (Optional - for local development)
```bash
# Ubuntu/Debian
sudo apt-get install -y maven

# CentOS/RHEL/Fedora
sudo dnf install -y maven

# macOS with Homebrew
brew install maven

# Verify installation
mvn -version
```

## 🚀 Installation Steps

### Step 1: Obtain the Project

#### Option A: Clone Repository
```bash
git clone https://github.com/your-org/employee-management-system.git
cd employee-management-system
```

#### Option B: Download Archive
```bash
# Download and extract the project archive
wget https://github.com/your-org/employee-management-system/archive/main.zip
unzip main.zip
cd employee-management-system-main
```

### Step 2: Environment Configuration

#### Create Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Edit environment variables (optional)
nano .env
```

#### Default Environment Variables
```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=employee_db
DB_USERNAME=postgres
DB_PASSWORD=password

# pgAdmin Configuration
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin

# Application Configuration
SPRING_PROFILES_ACTIVE=dev
SERVER_PORT=8080
```

### Step 3: Container Setup

#### Build and Start Services
```bash
# Pull and build all containers
podman-compose build

# Start all services in detached mode
podman-compose up -d

# Alternative: Start with live logs
podman-compose up
```

#### Verify Services Are Running
```bash
# Check service status
podman-compose ps

# Expected output:
# NAME                  COMMAND                  SERVICE             STATUS
# employee_postgres     "docker-entrypoint.s…"   postgres            Up
# employee_pgadmin      "/entrypoint.sh"         pgadmin             Up
# employee_app          "tail -f /dev/null"      app                 Up
```

#### Check Service Health
```bash
# Test PostgreSQL connection
podman-compose exec postgres pg_isready -U postgres

# Test application container
podman-compose exec app java -version

# View service logs
podman-compose logs postgres
podman-compose logs pgladmin
podman-compose logs app
```

## 🔧 Configuration Options

### Database Configuration

#### Customize Database Settings
```yaml
# In podman-compose.yml
services:
  postgres:
    environment:
      POSTGRES_DB: your_custom_db_name
      POSTGRES_USER: your_username
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
```

#### Persistent Data Storage
```yaml
# Ensure data persistence
volumes:
  postgres_data:
    driver: local
  pgadmin_data:
    driver: local
```

### Application Configuration

#### Development Profile
```yaml
# src/main/resources/application-dev.yml
spring:
  jpa:
    hibernate:
      ddl-auto: update  # Auto-create/update schema
    show-sql: true      # Show SQL queries in logs

logging:
  level:
    com.example.employee: DEBUG
    org.hibernate.SQL: DEBUG
```

#### Production Profile
```yaml
# src/main/resources/application-prod.yml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # Only validate schema
    show-sql: false

logging:
  level:
    com.example.employee: INFO
```

## 🌐 Service Access

### Web Interfaces

#### pgAdmin Database Manager
- **URL**: http://localhost:5050
- **Email**: admin@example.com
- **Password**: admin

**Initial Setup**:
1. Login to pgAdmin
2. The PostgreSQL server should be automatically configured
3. If not, add server with:
   - **Host**: postgres
   - **Port**: 5432
   - **Database**: employee_db
   - **Username**: postgres
   - **Password**: password

#### Application API
- **Base URL**: http://localhost:8080/api/v1
- **Health Check**: http://localhost:8080/actuator/health
- **API Documentation**: http://localhost:8080/swagger-ui.html (if enabled)

### Database Direct Access

#### Command Line Access
```bash
# Connect to PostgreSQL directly
podman-compose exec postgres psql -U postgres -d employee_db

# Run SQL commands
\\dt                    # List tables
\\d employees          # Describe employees table
SELECT COUNT(*) FROM employees;
```

#### External Database Tools
- **Host**: localhost
- **Port**: 5432
- **Database**: employee_db
- **Username**: postgres
- **Password**: password

## 🧪 Testing Setup

### Test Environment Configuration

#### Run Initial Tests
```bash
# Build the application
podman-compose exec app mvn clean compile

# Run all tests
podman-compose exec app mvn test

# Run specific test categories
podman-compose exec app mvn test -Dtest="*Repository*"
podman-compose exec app mvn test -Dtest="*Service*"
podman-compose exec app mvn test -Dtest="*Controller*"
```

#### Test Data Configuration
```bash
# Test with different data profiles
podman-compose exec app mvn test -Dtestdata.profile=basic
podman-compose exec app mvn test -Dtestdata.profile=medium
podman-compose exec app mvn test -Dtestdata.profile=large
```

### Coverage Reporting
```bash
# Generate test coverage report
podman-compose exec app mvn test jacoco:report

# Copy report to local machine
podman cp $(podman-compose ps -q app):/workspace/target/site/jacoco ./coverage-report
```

## 🛠️ Development Workflow

### Local Development Setup

#### IDE Integration
```bash
# For IntelliJ IDEA or Eclipse
# Import as Maven project
# Set Java SDK to 17+
# Configure database connection:
# URL: jdbc:postgresql://localhost:5432/employee_db
# Username: postgres
# Password: password
```

#### Hot Reload Development
```bash
# Start application with dev profile
podman-compose exec app mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Or use the development override
podman-compose -f podman-compose.yml -f podman-compose.dev.yml up
```

### Code Changes Workflow
```bash
# 1. Make code changes in your IDE
# 2. Test changes
podman-compose exec app mvn clean test

# 3. Build application
podman-compose exec app mvn clean package

# 4. Restart application (if needed)
podman-compose restart app
```

## 🔍 Troubleshooting

### Common Setup Issues

#### Port Conflicts
```bash
# Check what's using ports
sudo netstat -tulpn | grep :8080
sudo netstat -tulpn | grep :5432
sudo netstat -tulpn | grep :5050

# Change ports in podman-compose.yml if needed
```

#### Container Build Issues
```bash
# Clean and rebuild
podman-compose down
podman system prune -f
podman-compose build --no-cache
podman-compose up -d
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
podman-compose logs postgres

# Verify database is accepting connections
podman-compose exec postgres pg_isready -U postgres -d employee_db

# Reset database (WARNING: destroys data)
podman-compose down -v
podman volume prune -f
podman-compose up -d
```

#### Memory Issues
```bash
# Increase container memory limits in podman-compose.yml
services:
  postgres:
    mem_limit: 1g
  app:
    mem_limit: 2g

# Or adjust system resources
podman system info | grep -E "Memory|CPUs"
```

### Performance Optimization

#### Database Performance
```bash
# Monitor database performance
podman-compose exec postgres psql -U postgres -d employee_db \\
  -c "SELECT * FROM pg_stat_activity;"

# Analyze query performance
podman-compose exec postgres psql -U postgres -d employee_db \\
  -c "EXPLAIN ANALYZE SELECT * FROM employees JOIN departments ON employees.department_id = departments.id;"
```

#### Application Performance
```bash
# Monitor JVM memory usage
podman-compose exec app jps -v

# Enable JVM monitoring (add to podman-compose.yml)
environment:
  - JAVA_OPTS=-XX:+UnlockExperimentalVMOptions -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0
```

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Update Container Images
```bash
# Pull latest images
podman-compose pull

# Rebuild and restart
podman-compose down
podman-compose up -d --build
```

#### Database Backup
```bash
# Create database backup
podman-compose exec postgres pg_dump -U postgres employee_db > backup.sql

# Restore from backup
podman-compose exec -T postgres psql -U postgres employee_db < backup.sql
```

#### Clean Up Resources
```bash
# Remove unused containers and images
podman system prune -a

# Remove unused volumes (WARNING: destroys data)
podman volume prune -f
```

### Monitoring and Logs

#### View Logs
```bash
# Follow all logs
podman-compose logs -f

# View specific service logs
podman-compose logs -f postgres
podman-compose logs -f app

# View last N lines
podman-compose logs --tail=50 app
```

#### System Monitoring
```bash
# Check container resource usage
podman stats $(podman-compose ps -q)

# Check system disk usage
df -h
```

## 📞 Support

### Getting Help

#### Log Collection for Support
```bash
# Collect system information
./scripts/collect-debug-info.sh

# Or manually:
podman-compose ps > debug-info.txt
podman-compose logs >> debug-info.txt
podman system info >> debug-info.txt
```

#### Common Support Scenarios
1. **Application won't start**: Check logs and verify all services are running
2. **Database connection issues**: Verify PostgreSQL service health
3. **Test failures**: Ensure test database is properly initialized
4. **Performance issues**: Monitor resource usage and optimize configurations

---

**Next Steps**: After successful setup, proceed to the [Testing Guide](TESTING_GUIDE.md) to learn about the comprehensive testing strategies.