# System Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Technology Stack](#technology-stack)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)
- [Performance Optimization](#performance-optimization)
- [Security Architecture](#security-architecture)
- [Infrastructure Architecture](#infrastructure-architecture)
- [Deployment Architecture](#deployment-architecture)

## Overview

This document describes the technical architecture of the Organization Management System. The system follows a microservices-inspired architecture with GitOps deployment methodology, containerization, and automated CI/CD pipelines.

### Architecture Goals

- **Scalability**: Horizontal scaling capability for each component
- **Reliability**: High availability with automated recovery
- **Maintainability**: Clear separation of concerns
- **Security**: Defense in depth with multiple security layers
- **Automation**: Fully automated CI/CD pipeline
- **Observability**: Comprehensive monitoring and logging

## High-Level Architecture

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         External Users                               │
│                     (Developers, Operators)                          │
└───────────────────┬─────────────────┬───────────────────────────────┘
                    │                 │
        ┌───────────▼─────────┐      │
        │   Web Browser       │      │
        │  (Frontend UI)      │      │
        └───────────┬─────────┘      │
                    │                 │
┌───────────────────▼─────────────────▼───────────────────────────────┐
│                     Application Layer                                │
│  ┌──────────────────────┐       ┌──────────────────────┐            │
│  │  React Frontend      │       │  Spring Boot Backend │            │
│  │  - Vite Build        │◄─────►│  - REST API          │            │
│  │  - React Router      │       │  - Business Logic    │            │
│  │  - Axios HTTP        │       │  - Data Validation   │            │
│  └──────────────────────┘       └──────────┬───────────┘            │
└────────────────────────────────────────────┼────────────────────────┘
                                              │
┌─────────────────────────────────────────────▼────────────────────────┐
│                     Data Layer                                        │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │  PostgreSQL Database                                      │        │
│  │  - Organizations, Departments, Users                      │        │
│  │  - Flyway Migrations                                      │        │
│  │  - Connection Pooling                                     │        │
│  └──────────────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                     DevOps Layer                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   GitLab    │  │    Nexus    │  │   ArgoCD    │  │  Monitoring │ │
│  │   CI/CD     │  │  Repository │  │   GitOps    │  │   Logging   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Container Runtime (Podman)                       │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                 ArgoCD Network Bridge                        │    │
│  │                                                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │ Frontend │  │ Backend  │  │ Postgres │  │  ArgoCD  │   │    │
│  │  │Container │◄─┤Container │◄─┤Container │  │ Services │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  │       :80          :8080         :5432         :5010       │    │
│  │                                                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │  GitLab  │  │  Nexus   │  │ pgAdmin  │  │  Redis   │   │    │
│  │  │Container │  │Container │  │Container │  │Container │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  │      :5003         :8081         :5050         :6379       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Persistent Volumes                         │    │
│  │  - postgres-data      - gitlab-data      - nexus-data       │    │
│  │  - argocd-data        - redis-data       - pgadmin-data     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.2.0 | UI library |
| **Build Tool** | Vite | 5.0.11 | Fast build and HMR |
| **Router** | React Router | 6.21.1 | Client-side routing |
| **HTTP Client** | Axios | 1.6.5 | API communication |
| **Testing** | Jest | 29.7.0 | Unit testing |
| **E2E Testing** | Playwright | 1.40.0 | End-to-end testing |
| **Linting** | ESLint | 8.56.0 | Code quality |

**Technology Choices:**

- **React**: Industry-standard, large ecosystem, component reusability
- **Vite**: Fast development server, optimized production builds
- **Axios**: Promise-based HTTP client, interceptors support

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Java | 17 | Programming language |
| **Framework** | Spring Boot | 3.2.1 | Application framework |
| **ORM** | Spring Data JPA | 3.2.1 | Data access layer |
| **Database** | PostgreSQL | 16 | Primary database |
| **Migrations** | Flyway | - | Schema versioning |
| **Build Tool** | Maven | 3.9 | Dependency management |
| **Testing** | JUnit 5 | - | Unit testing |
| **Coverage** | JaCoCo | 0.8.11 | Code coverage |
| **Monitoring** | Actuator | - | Health checks, metrics |

**Technology Choices:**

- **Spring Boot**: Production-ready, extensive ecosystem, auto-configuration
- **PostgreSQL**: ACID compliance, advanced features, reliability
- **Flyway**: Version control for database, repeatable migrations

### Infrastructure Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Container Runtime** | Podman | latest | Container management |
| **Orchestration** | podman-compose | latest | Multi-container apps |
| **GitOps** | ArgoCD | v2.10.0 | Declarative deployment |
| **CI/CD** | GitLab CE | latest | Source control, pipelines |
| **Artifact Repository** | Nexus | 3.63.0 | Artifact management |
| **Automation** | Ansible | 2.x | Infrastructure as code |
| **Cache** | Redis | 7 | ArgoCD caching |

**Technology Choices:**

- **Podman**: Daemonless, rootless containers, Docker-compatible
- **ArgoCD**: Native Kubernetes GitOps, automated sync, rollback
- **GitLab**: All-in-one DevOps platform, container registry

## Component Architecture

### Frontend Architecture

```
src/
├── components/
│   ├── organizations/
│   │   ├── OrganizationList.jsx       # List view
│   │   ├── OrganizationForm.jsx       # Create/Edit form
│   │   └── OrganizationDetail.jsx     # Detail view
│   ├── departments/
│   │   ├── DepartmentList.jsx
│   │   ├── DepartmentForm.jsx
│   │   └── DepartmentDetail.jsx
│   └── users/
│       ├── UserList.jsx
│       ├── UserForm.jsx
│       └── UserDetail.jsx
├── services/
│   ├── api.js                         # Axios instance
│   ├── organizationService.js         # Organization API
│   ├── departmentService.js           # Department API
│   └── userService.js                 # User API
├── App.jsx                            # Main app component
└── main.jsx                           # Entry point
```

**Design Patterns:**

1. **Component-Based Architecture**: Reusable, testable components
2. **Service Layer**: Centralized API communication
3. **Separation of Concerns**: UI logic separate from business logic
4. **Error Boundaries**: Graceful error handling

### Backend Architecture

```
com.example.orgmgmt/
├── controller/
│   ├── OrganizationController.java    # REST endpoints
│   ├── DepartmentController.java
│   └── UserController.java
├── service/
│   ├── OrganizationService.java       # Business logic
│   ├── DepartmentService.java
│   ├── UserService.java
│   └── EntityMapper.java              # DTO mapping
├── repository/
│   ├── OrganizationRepository.java    # Data access
│   ├── DepartmentRepository.java
│   └── UserRepository.java
├── entity/
│   ├── Organization.java              # JPA entities
│   ├── Department.java
│   └── User.java
├── dto/
│   ├── OrganizationDTO.java           # Data transfer objects
│   ├── DepartmentDTO.java
│   └── UserDTO.java
└── exception/
    ├── GlobalExceptionHandler.java    # Error handling
    ├── ResourceNotFoundException.java
    └── DuplicateResourceException.java
```

**Design Patterns:**

1. **Layered Architecture**: Controller → Service → Repository
2. **Repository Pattern**: Data access abstraction
3. **DTO Pattern**: Decouple API from domain model
4. **Exception Handling**: Centralized error handling
5. **Dependency Injection**: Spring-managed beans

### Data Model

```
┌─────────────────────┐
│   Organization      │
├─────────────────────┤
│ id (PK)             │
│ name                │
│ code (UNIQUE)       │
│ description         │
│ active              │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐
│   Department        │
├─────────────────────┤
│ id (PK)             │
│ organization_id (FK)│
│ name                │
│ code (UNIQUE)       │
│ description         │
│ active              │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐
│   User              │
├─────────────────────┤
│ id (PK)             │
│ department_id (FK)  │
│ first_name          │
│ last_name           │
│ email (UNIQUE)      │
│ phone               │
│ active              │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

**Relationships:**

- One Organization has many Departments
- One Department has many Users
- Cascading deletes configured for referential integrity
- Indexes on foreign keys for query performance

## Data Flow

### Read Operation Flow

```
1. User clicks "View Organizations" in Browser
         │
         ▼
2. React Component calls organizationService.getAll()
         │
         ▼
3. Axios sends GET /api/organizations
         │
         ▼
4. Spring Boot Controller receives request
         │
         ▼
5. OrganizationService.getAllOrganizations()
         │
         ▼
6. OrganizationRepository.findAll()
         │
         ▼
7. Spring Data JPA generates SQL query
         │
         ▼
8. PostgreSQL executes query and returns rows
         │
         ▼
9. JPA maps rows to Organization entities
         │
         ▼
10. Service maps entities to DTOs
         │
         ▼
11. Controller returns ResponseEntity<List<OrganizationDTO>>
         │
         ▼
12. JSON serialization
         │
         ▼
13. HTTP response sent to frontend
         │
         ▼
14. React component updates state and re-renders
```

### Write Operation Flow

```
1. User submits "Create Organization" form
         │
         ▼
2. React validates form inputs
         │
         ▼
3. Axios sends POST /api/organizations with JSON body
         │
         ▼
4. Spring Boot Controller receives request
         │
         ▼
5. @Valid annotation triggers validation
         │
         ▼
6. OrganizationService.createOrganization()
         │
         ├─► Check for duplicate code
         │
         ├─► Save to database via repository
         │
         └─► Return saved entity as DTO
         │
         ▼
7. Transaction commits
         │
         ▼
8. HTTP 201 Created response with created resource
         │
         ▼
9. React component updates UI with new organization
```

### CI/CD Pipeline Flow

```
1. Developer pushes code to GitLab
         │
         ▼
2. GitLab CI/CD pipeline triggered
         │
         ├─► Build Backend (Maven)
         ├─► Test Backend (JUnit)
         ├─► Build Frontend (Vite)
         ├─► Test Frontend (Jest)
         ├─► Package Artifacts
         │   ├─► JAR file
         │   └─► Tarball
         │
         ▼
3. Deploy artifacts to Nexus Repository
         │
         ▼
4. Container Builder pulls artifacts from Nexus
         │
         ├─► Build backend container image
         ├─► Build frontend container image
         └─► Push images to GitLab Registry
         │
         ▼
5. Update GitOps manifests with new image tags
         │
         ▼
6. Commit manifest changes to Git
         │
         ▼
7. ArgoCD detects changes in GitOps repository
         │
         ▼
8. ArgoCD syncs application state
         │
         ├─► Pull new container images
         ├─► Stop old containers
         ├─► Start new containers
         └─► Verify health checks
         │
         ▼
9. Application deployed and running
         │
         ▼
10. Run E2E tests with Playwright
         │
         ▼
11. Report pipeline success/failure
```

## Design Decisions

### 1. Monolithic vs Microservices

**Decision**: Start with monolithic architecture

**Rationale**:
- Simpler development and deployment
- Easier to refactor into microservices later
- Lower operational complexity
- Single transaction boundary
- Good for MVP and small teams

**Trade-offs**:
- Harder to scale specific components
- Longer deployment times
- Technology lock-in per service

### 2. REST API vs GraphQL

**Decision**: REST API with Spring Boot

**Rationale**:
- Simpler to implement and understand
- Better tooling and ecosystem
- HTTP caching support
- Standard HTTP methods
- Widely adopted

**Trade-offs**:
- Over-fetching/under-fetching data
- Multiple round trips for related data
- No schema introspection

### 3. PostgreSQL vs MySQL

**Decision**: PostgreSQL

**Rationale**:
- Better JSON support for future flexibility
- Advanced features (window functions, CTEs)
- Better standards compliance
- Excellent performance
- Strong community support

**Trade-offs**:
- Slightly higher resource usage
- Less familiar to some developers

### 4. Podman vs Docker

**Decision**: Podman

**Rationale**:
- Daemonless architecture (better security)
- Rootless containers
- Docker-compatible CLI
- No single point of failure
- Better for RHEL environments

**Trade-offs**:
- Smaller ecosystem
- Some Docker Compose features missing

### 5. ArgoCD vs Flux

**Decision**: ArgoCD

**Rationale**:
- Excellent UI dashboard
- Mature project
- Better RBAC support
- Easier to learn
- Good documentation

**Trade-offs**:
- Kubernetes-native (we adapted for Podman)
- More resource intensive

### 6. GitOps vs Traditional CD

**Decision**: GitOps with ArgoCD

**Rationale**:
- Git as single source of truth
- Declarative infrastructure
- Easy rollback capabilities
- Audit trail in Git history
- Automated drift detection

**Trade-offs**:
- Learning curve
- Additional tooling required
- Git repository becomes critical

### 7. Maven vs Gradle

**Decision**: Maven

**Rationale**:
- More predictable builds
- Better IDE integration
- Larger plugin ecosystem
- Standard in Spring Boot projects
- Easier for new developers

**Trade-offs**:
- More verbose XML configuration
- Slower build times
- Less flexible than Gradle

### 8. Vite vs Create React App

**Decision**: Vite

**Rationale**:
- Much faster development server
- Faster production builds
- Better ES modules support
- Modern tooling
- Smaller bundle sizes

**Trade-offs**:
- Newer, less mature
- Smaller community
- Some plugins missing

## Scalability Considerations

### Horizontal Scaling

#### Application Tier

```yaml
# Scale backend replicas
services:
  orgmgmt-backend:
    deploy:
      replicas: 3

  # Load balancer (nginx)
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**Capacity**: Each backend instance can handle ~500 concurrent requests

#### Database Tier

```
Primary PostgreSQL
       │
       ├─► Read Replica 1
       ├─► Read Replica 2
       └─► Read Replica 3
```

**Strategies**:
- Read replicas for read-heavy workloads
- Connection pooling (HikariCP)
- Query optimization with indexes
- Partitioning large tables

### Vertical Scaling

```yaml
# Increase container resources
services:
  orgmgmt-backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

### Caching Strategy

```
┌─────────────┐
│   Browser   │
│  (HTTP Cache)
└──────┬──────┘
       │
┌──────▼──────┐
│   CDN       │
│  (Static)   │
└──────┬──────┘
       │
┌──────▼──────┐
│   nginx     │
│  (Reverse   │
│   Proxy)    │
└──────┬──────┘
       │
┌──────▼──────┐
│   Redis     │
│  (API Cache)│
└──────┬──────┘
       │
┌──────▼──────┐
│  Backend    │
│   API       │
└──────┬──────┘
       │
┌──────▼──────┐
│  PostgreSQL │
└─────────────┘
```

### Database Optimization

1. **Indexes**: Add indexes on frequently queried columns
2. **Connection Pooling**: HikariCP with optimal pool size
3. **Query Optimization**: Use EXPLAIN ANALYZE
4. **Pagination**: Limit result set sizes
5. **Caching**: Redis for frequently accessed data

## Performance Optimization

### Frontend Optimization

1. **Code Splitting**: Lazy load routes
2. **Tree Shaking**: Remove unused code
3. **Minification**: Compress JavaScript and CSS
4. **Image Optimization**: WebP format, lazy loading
5. **HTTP/2**: Multiplexing requests
6. **Service Worker**: Offline support

```javascript
// Lazy loading
const OrganizationList = React.lazy(() =>
  import('./components/organizations/OrganizationList')
);
```

### Backend Optimization

1. **Database Indexes**: Strategic index placement
2. **Query Optimization**: N+1 query prevention
3. **Connection Pooling**: Reuse database connections
4. **Batch Operations**: Bulk inserts/updates
5. **Async Processing**: Non-blocking operations
6. **Caching**: Redis for hot data

```java
// N+1 prevention with JOIN FETCH
@Query("SELECT o FROM Organization o LEFT JOIN FETCH o.departments")
List<Organization> findAllWithDepartments();
```

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_org_code ON organizations(code);
CREATE INDEX idx_dept_org_id ON departments(organization_id);
CREATE INDEX idx_user_dept_id ON users(department_id);
CREATE INDEX idx_user_email ON users(email);

-- Analyze queries
EXPLAIN ANALYZE SELECT * FROM organizations WHERE active = true;

-- Vacuum regularly
VACUUM ANALYZE organizations;
```

### Container Optimization

```dockerfile
# Multi-stage builds
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Benefits**:
- Smaller image sizes
- Faster builds with layer caching
- Better security (no build tools in runtime)

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                              │
│  - Firewall rules                                       │
│  - Network isolation                                    │
│  - Port restrictions                                    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Layer 2: Application Security                          │
│  - Input validation                                     │
│  - Output encoding                                      │
│  - CORS policies                                        │
│  - Security headers                                     │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Layer 3: Authentication & Authorization                │
│  - JWT tokens                                           │
│  - Role-based access control                            │
│  - Password policies                                    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Layer 4: Data Security                                 │
│  - Encryption at rest                                   │
│  - Encryption in transit (TLS)                          │
│  - Database encryption                                  │
│  - Secrets management                                   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Layer 5: Monitoring & Auditing                         │
│  - Security logging                                     │
│  - Audit trails                                         │
│  - Intrusion detection                                  │
│  - Compliance monitoring                                │
└─────────────────────────────────────────────────────────┘
```

### Security Measures

1. **Input Validation**: Bean Validation (JSR-380)
2. **SQL Injection**: Parameterized queries (JPA)
3. **XSS Protection**: Output encoding, CSP headers
4. **CSRF Protection**: Spring Security CSRF tokens
5. **Authentication**: JWT or OAuth2
6. **Authorization**: Role-based access control
7. **TLS/HTTPS**: Encrypt data in transit
8. **Secrets**: Environment variables, vault
9. **Container Security**: Non-root users, scanning
10. **Audit Logging**: Track all operations

## Infrastructure Architecture

### Container Architecture

```
Host Machine (RHEL 9)
├── Podman Engine
│   ├── argocd-network (bridge)
│   │   ├── orgmgmt-postgres:5432
│   │   ├── orgmgmt-pgadmin:5050
│   │   ├── orgmgmt-nexus:8081,8082
│   │   ├── orgmgmt-gitlab:5003,5005,2222
│   │   ├── orgmgmt-gitlab-runner
│   │   ├── argocd-redis:6379
│   │   ├── argocd-repo-server
│   │   ├── argocd-application-controller
│   │   ├── argocd-server:5010
│   │   ├── orgmgmt-backend-dev:8080
│   │   └── orgmgmt-frontend-dev:5006
│   │
│   └── Volumes
│       ├── postgres-data
│       ├── pgadmin-data
│       ├── nexus-data
│       ├── gitlab-config
│       ├── gitlab-logs
│       ├── gitlab-data
│       ├── gitlab-runner-config
│       ├── argocd-redis-data
│       ├── argocd-repo-data
│       ├── argocd-controller-data
│       └── argocd-server-data
```

### Network Architecture

```
External Network (Internet)
         │
         │ Port Forwarding
         │
    ┌────▼─────┐
    │ Firewall │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Host    │
    │  :5006   │ Frontend
    │  :8080   │ Backend API
    │  :5010   │ ArgoCD UI
    │  :5003   │ GitLab
    │  :8081   │ Nexus
    └────┬─────┘
         │
┌────────▼────────┐
│ argocd-network  │
│  (172.16.0.0/24)│
│                 │
│  Internal DNS:  │
│  - postgres     │
│  - nexus        │
│  - gitlab       │
│  - argocd-redis │
└─────────────────┘
```

## Deployment Architecture

### Environment Strategy

```
┌─────────────┐
│   GitLab    │
│ Repository  │
└──────┬──────┘
       │
       │ Push/Merge
       │
┌──────▼──────────────────────────────────────────────┐
│              GitOps Repository                      │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │   dev/  │  │staging/ │  │  prod/  │            │
│  └─────────┘  └─────────┘  └─────────┘            │
└──────┬─────────────┬────────────┬──────────────────┘
       │             │            │
┌──────▼──────┐ ┌────▼─────┐ ┌───▼──────┐
│   ArgoCD    │ │  ArgoCD  │ │  ArgoCD  │
│  orgmgmt-dev│ │ staging  │ │   prod   │
└──────┬──────┘ └────┬─────┘ └───┬──────┘
       │             │            │
┌──────▼──────┐ ┌────▼─────┐ ┌───▼──────┐
│Development  │ │ Staging  │ │Production│
│Environment  │ │Environment│ │Environment│
└─────────────┘ └──────────┘ └──────────┘
```

### Deployment Process

1. **Development**: Auto-deploy on every commit
2. **Staging**: Manual approval required
3. **Production**: Manual approval + change window

### Rollback Strategy

```
Current State (v2.0) ──┐
                       │
    Deployment Issue   │
                       │
                       ▼
    Rollback Trigger ──► ArgoCD Rollback
                       │
                       ▼
    Previous State (v1.9) ◄─── Git Revert
                       │
                       ▼
    Health Check ──────► Success/Fail
                       │
    Success            │ Fail
       │               │
       ▼               ▼
    Complete      Emergency
                   Procedure
```

## Conclusion

This architecture provides:

- **Scalability**: Horizontal and vertical scaling options
- **Reliability**: Automated recovery and rollback
- **Security**: Multiple security layers
- **Maintainability**: Clear separation of concerns
- **Observability**: Comprehensive monitoring
- **Automation**: Fully automated CI/CD pipeline

The design is production-ready and can be adapted for various deployment scenarios from single-server to multi-cluster deployments.
