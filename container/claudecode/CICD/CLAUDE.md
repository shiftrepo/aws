# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete CI/CD infrastructure project running GitLab, Nexus, SonarQube, and PostgreSQL in Docker containers with Podman. It includes a sample Spring Boot + React application (**frontend/backend split architecture**) demonstrating the full pipeline:

**Frontend (5 stages)**: install → lint → test → sonarqube → build
**Backend (7 stages)**: build → test → coverage → sonarqube → package → nexus-deploy → container-deploy

**Critical Architecture Context**: All services run in containers managed by a single `docker-compose.yml`, authentication/configuration is centralized in `.env` files with automatic token preservation on re-setup, and **frontend/backend are deployed as separate GitLab projects with independent CI/CD pipelines**.

## Repository Purpose and Architecture

### Master Repository: `/root/aws.git/container/claudecode/CICD/`

**This is the master repository (source of truth).**

- **Purpose**: CI/CD infrastructure construction project
- **Scope**: Complete environment setup supporting EC2 scratch builds (zero-to-production setup)
- **Contents**:
  - `docker-compose.yml` - All service definitions
  - `scripts/` - Setup, backup, cleanup, credential management
  - `sample-app/` - Sample Spring Boot + React application (master source)
    - `frontend/` - React frontend master
    - `backend/` - Spring Boot backend master
    - `common/` - Common module (DTOs)
    - `.gitlab-ci.yml.frontend` - Frontend CI/CD definition
    - `.gitlab-ci.yml.backend` - Backend CI/CD definition
  - `.env` templates and configuration files

### Working Copies: Frontend and Backend Split Projects

**v2.6.0: These are CI/CD testing working copies, NOT the master.**

**Frontend Project**:
- **Path**: `/tmp/gitlab-sample-app-frontend-YYYYMMDD-HHMMSS/`
- **GitLab Project**: `sample-app-frontend-YYYYMMDD-HHMMSS`
- **Source**: Copied from `sample-app/frontend/` via `setup-sample-app-split.sh`
- **CI/CD**: 5-stage pipeline (install → lint → test → sonarqube → build)
- **Git Remote**: `http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-YYYYMMDD-HHMMSS.git`

**Backend Project**:
- **Path**: `/tmp/gitlab-sample-app-backend-YYYYMMDD-HHMMSS/`
- **GitLab Project**: `sample-app-backend-YYYYMMDD-HHMMSS`
- **Source**: Copied from `sample-app/backend/`, `common/`, `pom.xml` via `setup-sample-app-split.sh`
- **CI/CD**: 7-stage pipeline (build → test → coverage → sonarqube → package → nexus-deploy → container-deploy)
- **Git Remote**: `http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-YYYYMMDD-HHMMSS.git`

**CRITICAL PRINCIPLE**:
```
⚠️  /tmp/gitlab-sample-app-*/ directories are NOT the master repository
✅  Changes MUST be reflected back to /root/aws.git/container/claudecode/CICD/sample-app/
✅  Use rsync for synchronization, preserving all files and permissions
```

### Repository Workflow (v2.6.0 - Split Architecture)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. Master Repository                                                 │
│    /root/aws.git/container/claudecode/CICD/sample-app/              │
│    (Source of Truth)                                                 │
│    ├── frontend/                ← Frontend master                    │
│    ├── backend/                 ← Backend master                     │
│    ├── common/                  ← Common module                      │
│    ├── .gitlab-ci.yml.frontend  ← Frontend CI/CD definition         │
│    └── .gitlab-ci.yml.backend   ← Backend CI/CD definition          │
└────────────────────┬─────────────────────────────────────────────────┘
                     │
                     │ setup-sample-app-split.sh
                     │ (Split Copy + GitLab Configuration + Token Auto-Generation)
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 2. Working Copies (CI/CD Testing) - TWO SEPARATE PROJECTS           │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Frontend: /tmp/gitlab-sample-app-frontend-20260113-135159/ │   │
│ │ - GitLab: sample-app-frontend-20260113-135159               │   │
│ │ - Git remote: http://${EC2_PUBLIC_IP}:5003/root/...         │   │
│ │ - CI/CD Variables: EC2_PUBLIC_IP, SONAR_TOKEN (auto-set)    │   │
│ │ - Pipeline: 5 stages                                         │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Backend: /tmp/gitlab-sample-app-backend-20260113-135159/    │   │
│ │ - GitLab: sample-app-backend-20260113-135159                │   │
│ │ - Git remote: http://${EC2_PUBLIC_IP}:5003/root/...         │   │
│ │ - CI/CD Variables: EC2_PUBLIC_IP, SONAR_TOKEN (auto-set)    │   │
│ │ - Pipeline: 7 stages                                         │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────────────┘
                     │
                     │ ✓ CI/CD Success
                     │ Manual reflection required
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3. Reflect Changes Back to Master                                   │
│    rsync /tmp/gitlab-sample-app-frontend-*/ → sample-app/frontend/ │
│    rsync /tmp/gitlab-sample-app-backend-*/ → sample-app/backend/   │
│    git commit -m "Verified CI/CD changes #115"                      │
│    git push origin main                                              │
└──────────────────────────────────────────────────────────────────────┘
```

### Pipeline Execution Script: `setup-sample-app-split.sh`

**v2.6.0: This is the current recommended method (replaces setup-sample-app.sh)**

This script executes complete automated CI/CD setup with split frontend/backend projects:

**Automated Steps**:
1. **Environment Variable Loading** - Loads EC2_PUBLIC_IP from `.env`
2. **Execution ID Generation** - Creates timestamp YYYYMMDD-HHMMSS for unique project names
3. **Working Directory Cleanup** - Removes existing `/tmp/gitlab-sample-app-*` directories
4. **GitLab Personal Access Token Creation** - Auto-generates via GitLab Rails Console
5. **GitLab Project Creation (API)** - Creates two separate projects via GitLab API
6. **CI/CD Variables Setup (Frontend)** - Sets EC2_PUBLIC_IP and auto-generated SONAR_TOKEN **BEFORE push**
7. **Git Init & Push (Frontend)** - Initializes git, sets remote, pushes to GitLab
8. **CI/CD Variables Setup (Backend)** - Sets EC2_PUBLIC_IP and auto-generated SONAR_TOKEN **BEFORE push**
9. **Git Init & Push (Backend)** - Initializes git, sets remote, pushes to GitLab
10. **Setup Complete** - Displays project URLs and pipeline URLs

**Key Operations**:
```bash
cd /root/aws.git/container/claudecode/CICD
./scripts/setup-sample-app-split.sh

# What it does automatically:
# 1. Generates GitLab Personal Access Token (glpat-xxxxx)
# 2. Creates two GitLab projects:
#    - sample-app-frontend-20260113-135159
#    - sample-app-backend-20260113-135159
# 3. Generates SonarQube tokens for each project (sqa-xxxxx)
# 4. Sets CI/CD Variables BEFORE git push
# 5. Pushes to GitLab → triggers pipelines automatically
```

**Important**:
- **Timestamp-based naming**: Projects are uniquely named with execution timestamp
- **Complete automation**: No manual token generation or variable setup required
- **CI/CD Variables set BEFORE push**: Ensures variables exist when pipeline runs
- **View results**:
  - Frontend: `http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-YYYYMMDD-HHMMSS/-/pipelines`
  - Backend: `http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-YYYYMMDD-HHMMSS/-/pipelines`

## Core Commands

### Environment Setup & Management

```bash
# Initial setup (12-step process with interactive password/EC2 domain input)
./scripts/setup-from-scratch.sh

# View all credentials (services, databases, tokens)
./scripts/utils/show-credentials.sh
./scripts/utils/show-credentials.sh --file  # Output to credentials.txt (600 perms)

# Update passwords/tokens/EC2 host
./scripts/utils/update-passwords.sh --show
./scripts/utils/update-passwords.sh --gitlab 'NewPassword123!'
./scripts/utils/update-passwords.sh --nexus 'NewPassword123!'
./scripts/utils/update-passwords.sh --sonarqube 'NewPassword123!'
./scripts/utils/update-passwords.sh --sonar-token 'sqa_xxxx'
./scripts/utils/update-passwords.sh --runner-token 'glrt-xxxx'
./scripts/utils/update-passwords.sh --ec2-host '${EC2_PUBLIC_IP}'  # Use actual EC2 domain/IP
./scripts/utils/update-passwords.sh --all 'Degital2026!'  # Bulk update

# Backup and restore
./scripts/utils/backup-all.sh       # Creates backup-YYYYMMDD-HHMMSS.tar.gz
./scripts/utils/restore-all.sh backup-YYYYMMDD-HHMMSS
./scripts/cleanup-all.sh      # Delete all containers/volumes
./scripts/utils/deploy-oneclick.sh  # Backup → cleanup → restore
```

**IMPORTANT**: Never hardcode EC2 IP addresses in configuration files. Always use `${EC2_PUBLIC_IP}` environment variable reference. EC2 instances are recreated and IPs change.

### Container Management

```bash
# Service lifecycle
cd /root/aws.git/container/claudecode/CICD
podman-compose up -d              # Start all services
podman-compose down               # Stop all services
podman-compose restart gitlab     # Restart specific service
podman-compose logs -f gitlab     # View logs
podman ps                         # Check container status
podman stats                      # Resource usage

# Service health checks (use localhost for local checks)
curl http://localhost:5003/       # GitLab
curl http://localhost:8082/       # Nexus
curl http://localhost:8000/       # SonarQube
psql -h localhost -p 5001 -U cicduser -d cicddb  # PostgreSQL
```

### Sample Application Development

**Backend**:
```bash
# Build and test (Maven multi-module)
cd sample-app
mvn clean install                 # Build all modules
mvn clean test                    # Run unit tests
mvn test -Dtest=OrganizationServiceTest  # Single test
mvn jacoco:report                 # Generate coverage report
mvn clean test -X                 # Debug mode

# View coverage report
open backend/target/site/jacoco/index.html

# SonarQube analysis (local)
mvn sonar:sonar \
  -Dsonar.host.url=http://localhost:8000 \
  -Dsonar.projectKey=sample-app-backend \
  -Dsonar.token=$SONAR_TOKEN

# Package and deploy to Nexus
mvn package -DskipTests
mvn deploy -DskipTests --settings .ci-settings.xml

# Run backend locally
cd backend
mvn spring-boot:run
# Access: http://localhost:8501
# Swagger UI: http://localhost:8501/swagger-ui.html
```

**Frontend**:
```bash
# Frontend development
cd sample-app/frontend
npm install
npm run dev      # Access: http://localhost:3000
npm test
npm test -- --coverage

# Build for production
npm run build

# View coverage report
open coverage/lcov-report/index.html
```

### GitLab CI/CD Management

```bash
# Register GitLab Runner (required after setup)
# Note: Use ${EC2_PUBLIC_IP} from .env file, not hardcoded IP
source .env
sudo gitlab-runner register \
  --url http://${EC2_PUBLIC_IP}:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

sudo systemctl enable --now gitlab-runner
sudo systemctl status gitlab-runner
sudo gitlab-runner list

# Execute split project setup (recommended)
./scripts/setup-sample-app-split.sh
# This automatically creates two GitLab projects with CI/CD Variables set
```

## Architecture Critical Points

### 1. Frontend/Backend Split Architecture (v2.6.0)

**CRITICAL**: This project uses **separate GitLab projects** for frontend and backend, NOT a monorepo:

**Why Split Architecture**:
- **Independent CI/CD pipelines**: Frontend (5 stages) and Backend (7 stages) run separately
- **Different deployment targets**: Frontend (Nginx container), Backend (Spring Boot container)
- **Different quality tools**: Frontend (ESLint, Jest, LCOV), Backend (Checkstyle, JUnit, JaCoCo, Maven)
- **Independent SonarQube projects**: Separate quality gates for frontend/backend
- **Parallel development**: Teams can work independently without conflicts

**GitLab Project Structure**:
```
GitLab (http://${EC2_PUBLIC_IP}:5003)
├── sample-app-frontend-20260113-135159
│   ├── CI/CD: 5 stages (install → lint → test → sonarqube → build)
│   ├── Variables: EC2_PUBLIC_IP, SONAR_TOKEN (auto-set)
│   └── SonarQube: sample-app-frontend (LCOV coverage)
│
└── sample-app-backend-20260113-135159
    ├── CI/CD: 7 stages (build → test → coverage → sonarqube → package → nexus-deploy → container-deploy)
    ├── Variables: EC2_PUBLIC_IP, SONAR_TOKEN (auto-set)
    └── SonarQube: sample-app-backend (Maven plugin + JaCoCo)
```

**Master Repository Structure** (source of truth):
```
sample-app/
├── frontend/                    ← Frontend master
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   ├── jest.config.js
│   ├── sonar-project.properties  ← SonarQube config (LCOV only)
│   └── Dockerfile
├── backend/                     ← Backend master
│   ├── src/
│   ├── pom.xml
│   └── Dockerfile
├── common/                      ← Common module (DTOs)
│   ├── src/
│   └── pom.xml
├── pom.xml                      ← Parent POM
├── .gitlab-ci.yml.frontend      ← Frontend CI/CD definition
└── .gitlab-ci.yml.backend       ← Backend CI/CD definition
```

### 2. Token Preservation System

**CRITICAL**: `setup-from-scratch.sh` has built-in logic to preserve SONAR_TOKEN and RUNNER_TOKEN when re-running setup:

- Step 7 detects existing `.env` files
- Reads `SONAR_TOKEN` and `RUNNER_TOKEN` from existing file
- Creates automatic backup: `.env.backup.YYYYMMDDHHMMSS`
- Regenerates `.env` with preserved tokens + new passwords

**Why This Matters**: Users manually configure SonarQube tokens and GitLab Runner tokens after initial setup. Losing these requires manual re-registration in GitLab UI.

**Note**: In v2.6.0, `setup-sample-app-split.sh` **automatically generates SonarQube tokens** per project, eliminating manual token configuration.

### 3. EC2 Domain Name Dynamic Configuration

**CRITICAL**: The entire infrastructure supports dynamic EC2 domain/IP changes. **Never hardcode IP addresses**.

**Configuration Strategy**:
- `setup-from-scratch.sh` Step 6: Prompts for EC2 domain name (auto-detects via 169.254.169.254 if empty)
- All services use `${EC2_PUBLIC_IP}` from `.env`
- Maven settings.xml generated dynamically with password AND domain replacement
- docker-compose.yml references `${EC2_PUBLIC_IP}` for GitLab external_url, registry_external_url
- GitLab CI/CD Variables: EC2_PUBLIC_IP set automatically by `setup-sample-app-split.sh`

**Environment Variable Usage**:
```bash
# .env file (source of truth)
EC2_PUBLIC_IP=ec2-xx-xx-xx-xx.compute-1.amazonaws.com  # This value CHANGES

# Usage in docker-compose.yml
gitlab_rails['external_url'] = "http://${EC2_PUBLIC_IP}:5003"

# Usage in CI/CD pipelines
sonar.host.url=http://${EC2_PUBLIC_IP}:8000

# Usage in scripts
curl http://${EC2_PUBLIC_IP}:5003/api/v4/projects
```

**When EC2 Instance is Recreated**:
1. Run `setup-from-scratch.sh` (tokens preserved) OR `update-passwords.sh --ec2-host <NEW_DOMAIN>`
2. Update GitLab working copy git remote:
   ```bash
   cd /tmp/gitlab-sample-app-frontend-*
   git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-*/

   cd /tmp/gitlab-sample-app-backend-*
   git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-*/
   ```
3. Re-register GitLab Runner with new domain

**NEVER DO THIS**:
```bash
# ❌ BAD: Hardcoded IP in code or documentation
curl http://192.168.1.100:5003/api/v4/projects

# ❌ BAD: Hardcoded domain that will change
curl http://ec2-34-205-156-203.compute-1.amazonaws.com:5003/

# ✅ GOOD: Environment variable reference
curl http://${EC2_PUBLIC_IP}:5003/api/v4/projects

# ✅ GOOD: Placeholder for documentation
curl http://YOUR_EC2_IP:5003/api/v4/projects
```

### 4. Password Architecture

All passwords unified to `Degital2026!` by default, managed in `.env`:

```bash
GITLAB_ROOT_PASSWORD=Degital2026!
NEXUS_ADMIN_PASSWORD=Degital2026!
SONARQUBE_ADMIN_PASSWORD=Degital2026!
POSTGRES_PASSWORD=Degital2026!
PGADMIN_PASSWORD=Degital2026!
SONAR_DB_PASSWORD=Degital2026!
SAMPLE_DB_PASSWORD=Degital2026!
```

**Critical Files**:
- `docker-compose.yml`: Uses `${GITLAB_ROOT_PASSWORD}` for `gitlab_rails['initial_root_password']`
- `scripts/setup-from-scratch.sh`: Lines 277-287 use `sed` to replace BOTH password and EC2_PUBLIC_IP in Maven settings.xml
- `.gitignore`: Excludes `credentials.txt`, `.env.backup.*`

### 5. Frontend/Backend CI/CD Pipeline Architecture

**Frontend Pipeline** (`.gitlab-ci.yml.frontend` - 5 stages):

```yaml
stages:
  - install    # npm ci
  - lint       # ESLint
  - test       # Jest + coverage (LCOV)
  - sonarqube  # SonarQube Scanner + LCOV
  - build      # Vite build

Key Points:
- Uses sonar-scanner (not Maven plugin)
- Coverage format: LCOV only (no test-report.xml)
- sonar-project.properties defines project key
- CI/CD Variables: EC2_PUBLIC_IP, SONAR_TOKEN (auto-set by setup-sample-app-split.sh)
```

**Backend Pipeline** (`.gitlab-ci.yml.backend` - 7 stages):

```yaml
stages:
  - build           # Maven compile
  - test            # JUnit + JaCoCo
  - coverage        # JaCoCo report
  - sonarqube       # Maven sonar:sonar
  - package         # Maven package (JAR)
  - nexus-deploy    # Maven deploy to Nexus
  - container-deploy # Docker build & deploy

Key Points:
- Shell executor (uses host Maven, not Docker images)
- Cache: .m2/repository, backend/target
- before_script generates settings.xml with authentication dynamically
- Deploy stage uses same ./.m2/settings.xml (no separate template needed)
- CRITICAL: <id> in settings.xml MUST match pom.xml distributionManagement <id>
```

**Critical Differences**:
| Aspect | Frontend | Backend |
|--------|----------|---------|
| CI/CD Stages | 5 | 7 |
| Test Framework | Jest | JUnit 5 |
| Coverage Tool | Jest (LCOV) | JaCoCo |
| SonarQube Integration | sonar-scanner | Maven plugin |
| Coverage Format | LCOV only | JaCoCo XML |
| Build Tool | npm + Vite | Maven |
| Artifact | dist/ (static files) | JAR file |
| Deploy Target | Nginx container | Spring Boot container |

### 6. Complete Automation Features (v2.6.0)

**setup-sample-app-split.sh automates the following**:

1. **GitLab Personal Access Token Auto-Generation**:
   - Uses GitLab Rails Console: `gitlab-rails runner`
   - Scopes: api, read_api, write_repository
   - Expiration: 365 days
   - Token stored in variable for API calls

2. **GitLab Project Auto-Creation**:
   - Uses GitLab API: `POST /api/v4/projects`
   - Creates two separate projects (frontend/backend)
   - Timestamp-based unique naming (YYYYMMDD-HHMMSS)

3. **SonarQube Token Auto-Generation**:
   - Uses SonarQube API: `POST /api/user_tokens/generate`
   - Creates project-specific tokens (frontend-ci-token-*, backend-ci-token-*)
   - Different token for each project

4. **CI/CD Variables Auto-Setup (BEFORE push)**:
   - Uses GitLab API: `POST /api/v4/projects/{id}/variables`
   - Sets EC2_PUBLIC_IP (non-masked)
   - Sets SONAR_TOKEN (masked)
   - **Critical**: Variables are set BEFORE git push, ensuring they exist when pipeline runs

5. **Git Init and Auto-Push**:
   - Initializes fresh git repository
   - Sets remote to GitLab project
   - Commits all files
   - Pushes to GitLab → automatic pipeline trigger

**Why This Matters**:
- **Zero manual configuration**: No need to manually generate tokens or set variables
- **Repeatable**: Can be run multiple times without conflicts (timestamp-based naming)
- **Consistent**: Same setup process every time
- **Fast**: Complete setup in under 2 minutes

### 7. Database Schema Architecture

PostgreSQL (port 5001) has 4 databases initialized via `config/postgres/init.sql`:

1. **cicddb**: Main CICD database
2. **gitlabhq**: GitLab data (not gitlab_production - uses gitlabhq)
3. **sonardb**: SonarQube analysis data (user: sonaruser)
4. **sampledb**: Sample app data (user: sampleuser)

**Sample App Schema** (Flyway migrations in `backend/src/main/resources/db/migration/`):
- V1: organizations table
- V2: departments table (self-referencing parent_department_id)
- V3: users table
- V4: Sample data insert

**Entity Relationships**:
- Organization (1) → (N) Department
- Department (1) → (N) Department (hierarchical)
- Department (1) → (N) User

### 8. Service Ports

| Service | Internal | External | URL (use ${EC2_PUBLIC_IP}) |
|---------|----------|----------|----------------------------|
| PostgreSQL | 5432 | 5001 | psql -h localhost -p 5001 |
| pgAdmin | 80 | 5002 | http://${EC2_PUBLIC_IP}:5002 |
| GitLab HTTP | 80 | 5003 | http://${EC2_PUBLIC_IP}:5003 |
| GitLab SSH | 22 | 2223 | ssh://git@${EC2_PUBLIC_IP}:2223 |
| Nexus | 8081 | 8082 | http://${EC2_PUBLIC_IP}:8082 |
| Nexus Docker | 8083 | 8083 | ${EC2_PUBLIC_IP}:8083 |
| SonarQube | 9000 | 8000 | http://${EC2_PUBLIC_IP}:8000 |
| Backend API | 8080 | 8501 | http://${EC2_PUBLIC_IP}:8501 |
| Frontend | 3000 | 8500 | http://${EC2_PUBLIC_IP}:8500 |

**IMPORTANT**: All URLs must use `${EC2_PUBLIC_IP}` environment variable, not hardcoded IPs or domains.

## Critical Development Patterns

### When Modifying Environment Variables

1. **Always use `update-passwords.sh`** instead of direct `.env` editing - it creates automatic backups
2. If editing `.env` manually, create backup first: `cp .env .env.backup.$(date +%Y%m%d%H%M%S)`
3. After changing EC2_PUBLIC_IP in `.env`, update:
   - GitLab working copy git remotes
   - GitLab Runner registration
   - CI/CD Variables in GitLab projects (if not using setup-sample-app-split.sh)

### When Modifying setup-sample-app-split.sh

**Critical Sections**:
- **Lines 30-50**: GitLab Personal Access Token generation - DO NOT change token scopes
- **Lines 60-80**: GitLab API project creation - Ensure timestamp uniqueness
- **Lines 90-140**: CI/CD Variables setup - MUST happen BEFORE git push
- **Lines 150-170**: SonarQube token generation - Project-specific tokens required

### When Adding New Services

1. Add to `docker-compose.yml` with `${ENV_VAR}` references
2. Add variables to `.env`
3. Update `scripts/utils/show-credentials.sh` to display new credentials
4. Update `scripts/utils/update-passwords.sh` with new `--service` option
5. Document in `README.md` and `CREDENTIALS.md`
6. **Never hardcode IP addresses or domains**

### When Modifying CI/CD Pipeline

**GitLab Runner Requirement**: This project uses **shell executor**, NOT docker executor. All `image:` directives in `.gitlab-ci.yml.*` are commented out. Commands run directly on the host using installed Maven/Java/npm.

**Quality Gate Enforcement**: SonarQube stage has `allow_failure: false` - pipeline will fail if coverage < 90% or critical bugs exist.

**EC2_PUBLIC_IP Usage**:
- ❌ NEVER use `localhost` or hardcoded IPs in CI/CD files
- ✅ ALWAYS use `${EC2_PUBLIC_IP}` environment variable
- Files affected: `.gitlab-ci.yml.frontend`, `.gitlab-ci.yml.backend`, Maven pom.xml

**HEREDOC Variable Expansion**:
```yaml
# ❌ Wrong - variables not expanded
cat > settings.xml << 'EOF'
  <url>http://${EC2_PUBLIC_IP}:8082</url>
EOF

# ✅ Correct - variables expanded
cat > settings.xml << EOF
  <url>http://${EC2_PUBLIC_IP}:8082</url>
EOF
```

**Nexus Authentication Pattern** (Backend):
```yaml
before_script:
  - |
    cat > ./.m2/settings.xml << EOF
    <settings>
      <servers>
        <server>
          <id>nexus-snapshots</id>  <!-- Must match pom.xml -->
          <username>admin</username>
          <password>Degital2026!</password>
        </server>
      </servers>
      <mirrors>
        <mirror>
          <id>nexus-mirror</id>
          <mirrorOf>*</mirrorOf>
          <url>http://${EC2_PUBLIC_IP}:8082/repository/maven-public/</url>
        </mirror>
      </mirrors>
    </settings>
    EOF

deploy:
  script:
    - mvn deploy -DskipTests -s ./.m2/settings.xml  # Reuse same settings
```

**SonarQube Integration** (Frontend):
```yaml
sonarqube:
  script:
    - |
      sonar-scanner \
        -Dsonar.host.url="http://${EC2_PUBLIC_IP}:8000" \
        -Dsonar.token="${SONAR_TOKEN}" \
        -Dsonar.projectKey="sample-app-frontend" \
        -Dsonar.projectName="Sample App Frontend" \
        -Dsonar.sources=src \
        -Dsonar.tests=src \
        -Dsonar.test.inclusions="**/*.test.jsx,**/*.spec.jsx" \
        -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
```

## Common Troubleshooting Contexts

### Pipeline Fails with "EC2_PUBLIC_IP not set"

**Root Cause**: CI/CD Variables were not set before git push, or setup-sample-app-split.sh was not used.

**Diagnosis**:
```bash
# Check if variables are set in GitLab project
# GitLab UI → Settings → CI/CD → Variables
# Should see: EC2_PUBLIC_IP, SONAR_TOKEN

# Or use GitLab API
source .env
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  "http://${EC2_PUBLIC_IP}:5003/api/v4/projects/root%2Fsample-app-frontend-*/variables"
```

**Critical Requirements**:
1. **Variables set BEFORE push**: `setup-sample-app-split.sh` does this automatically
2. **EC2_PUBLIC_IP value**: Must match `.env` file value
3. **SONAR_TOKEN**: Must be valid SonarQube token (auto-generated by setup-sample-app-split.sh)

**Fixed in v2.6.0**: setup-sample-app-split.sh now sets variables BEFORE git push automatically.

### Frontend Pipeline Fails with "test-report.xml not found"

**Root Cause**: React + Jest uses LCOV coverage format, not Generic XML format.

**Solution**:
- Remove `sonar.testExecutionReportPaths=test-report.xml` from `sonar-project.properties`
- Add `sonar.tests=src` and `sonar.test.inclusions="**/*.test.jsx,**/*.spec.jsx"` to pipeline
- Use only `sonar.javascript.lcov.reportPaths=coverage/lcov.info`

**Fixed in v2.6.0**: Frontend sonar-project.properties uses LCOV-only configuration.

### Backend Pipeline Fails with 401 on Nexus Deploy Stage

**Root Cause**: Maven deploy requires authentication for `PUT` operations (uploads).

**Diagnosis**:
```bash
# Check if server ID matches in both files
grep "<id>nexus-snapshots</id>" sample-app/pom.xml
grep "<id>nexus-snapshots</id>" sample-app/.gitlab-ci.yml.backend
```

**Critical Requirements**:
1. **ID Match**: pom.xml `<snapshotRepository><id>` MUST exactly match settings.xml `<server><id>`
2. **Authentication in before_script**: `.gitlab-ci.yml.backend` must generate settings.xml with `<servers>` section
3. **Deploy uses correct settings**: `mvn deploy -s ./.m2/settings.xml`

**Fixed in v2.6.0**: before_script now automatically generates authenticated settings.xml.

### Re-setup Lost Tokens

**Symptom**: After re-running setup-from-scratch.sh, SonarQube tokens or GitLab Runner tokens disappeared.

**Root Cause**: Old version overwrote .env file without preserving tokens.

**Solution**:
- **v2.1.0+**: Tokens are automatically preserved
- Manual restore: `cp .env.backup.YYYYMMDDHHMMSS .env`
- Or use: `./scripts/utils/update-passwords.sh --sonar-token sqa_xxxxx`

**Note**: In v2.6.0, `setup-sample-app-split.sh` automatically generates new SonarQube tokens per project, eliminating this issue.

### EC2 IP Changed After Instance Recreation

**Symptom**: Services not accessible after EC2 instance recreation.

**Solution**:
1. Run `./scripts/utils/update-passwords.sh --ec2-host <NEW_EC2_DOMAIN_OR_IP>`
2. Update GitLab working copy git remotes:
   ```bash
   source .env
   cd /tmp/gitlab-sample-app-frontend-*
   git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-*/

   cd /tmp/gitlab-sample-app-backend-*
   git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-*/
   ```
3. Re-register GitLab Runner:
   ```bash
   source .env
   sudo gitlab-runner unregister --all-runners
   sudo gitlab-runner register \
     --url http://${EC2_PUBLIC_IP}:5003 \
     --token YOUR_TOKEN \
     --executor shell \
     --description "CICD Shell Runner"
   ```

### SonarQube Quality Gate Fails

**Diagnosis**:
```bash
# Backend: Run locally and view JaCoCo report
cd sample-app
mvn clean test jacoco:report
open backend/target/site/jacoco/index.html
# Need 90% line coverage, 90% branch coverage

# Frontend: Run locally and view LCOV report
cd sample-app/frontend
npm test -- --coverage
open coverage/lcov-report/index.html
# Need 90% line coverage
```

**Common Issues**:
- Missing test cases for new code
- Untested error handling branches
- Entity/DTO exclusions not configured correctly (Backend)

### Container Won't Start

**Common Issues**:
- **SELinux**: `sudo setenforce 0`
- **Memory**: `sudo sysctl -w vm.max_map_count=262144` (for SonarQube)
- **Port conflict**: `sudo ss -tuln | grep -E '5001|5002|5003|8000|8082|8500|8501'`
- **Disk space**: `df -h` (check available space)

## File Modification Safety

### Never Commit These Files
- `.env` (contains passwords and EC2_PUBLIC_IP)
- `credentials.txt` (generated by show-credentials.sh)
- `.env.backup.*` (automatic backups)
- `volumes/` (container data)

### Always Read Before Modifying
- `scripts/setup-sample-app-split.sh` - Complex token generation and API logic
- `docker-compose.yml` - Environment variable references
- `sample-app/pom.xml` - Nexus URL, coverage thresholds, plugin config
- `.gitlab-ci.yml.frontend` - Frontend pipeline stages, SonarQube Scanner config
- `.gitlab-ci.yml.backend` - Backend pipeline stages, Maven settings generation

### Template Files (Use sed for Dynamic Values)
- **DO NOT create template files with hardcoded IPs**
- Use environment variable references: `${EC2_PUBLIC_IP}`
- Generate files dynamically in before_script sections of CI/CD pipelines

## Version History Context

**v2.6.0** (Current - 2026-01-13):
- **Frontend/Backend Split Architecture**: Two separate GitLab projects
- **setup-sample-app-split.sh Implementation**: Complete automation
- **GitLab Personal Access Token Auto-Generation**: Via Rails Console
- **SonarQube Token Auto-Generation**: Per-project tokens via API
- **CI/CD Variables Auto-Setup (BEFORE push)**: Ensures variables exist when pipeline runs
- **Project Name Timestamping**: YYYYMMDD-HHMMSS for uniqueness
- **React + Jest + SonarQube LCOV-only Config**: Removed test-report.xml
- **Two .gitlab-ci.yml Files**: Frontend (5 stages), Backend (7 stages)
- **Quality Gate 90%**: Increased from 80%/70% to 90%/90%

**v2.5.1**:
- Backend CI/CD success, frontend authentication automation in progress
- container-deploy job artifact dependency fix

**v2.5.0**:
- Initial project split support (provisional)
- Separate frontend/backend Git repositories

**v2.4.1**:
- Backend completion
- Nexus authentication fix
- CI/CD variable automatic setup

## Key Lessons Learned

### 1. Never Hardcode IP Addresses

**Problem**: Hardcoded IPs/domains break when EC2 instances are recreated.

**Solution**:
- Use `${EC2_PUBLIC_IP}` environment variable everywhere
- Update `.env` file when EC2 domain changes
- Use `update-passwords.sh --ec2-host` for updates

**Examples**:
```bash
# ❌ BAD
curl http://192.168.1.100:5003/api/v4/projects

# ✅ GOOD
source .env
curl http://${EC2_PUBLIC_IP}:5003/api/v4/projects
```

### 2. CI/CD Variables Must Be Set BEFORE Push

**Problem**: Pushing to GitLab before setting CI/CD Variables causes pipeline failures.

**Solution**:
- Set variables via GitLab API BEFORE git push
- `setup-sample-app-split.sh` does this automatically
- Variables: EC2_PUBLIC_IP, SONAR_TOKEN

### 3. Frontend (React + Jest) Uses LCOV Only

**Problem**: React + Jest XML format ≠ SonarQube Generic XML format.

**Solution**:
- Use only `sonar.javascript.lcov.reportPaths=coverage/lcov.info`
- Remove `sonar.testExecutionReportPaths` from sonar-project.properties
- Add `sonar.test.inclusions` to identify test files

### 4. Maven Deploy Requires Authentication

**Problem**: Maven deploy shows "Uploading" but returns 401 Unauthorized.

**Solution**:
- Generate settings.xml in before_script with `<servers>` section
- Ensure exact ID match: `nexus-snapshots` in both pom.xml and settings.xml
- Include credentials: username=admin, password=Degital2026!
- Reuse same settings.xml in deploy stage

### 5. Frontend/Backend Split Requires Separate Pipelines

**Problem**: Monorepo approach causes unnecessary reruns and complex pipeline logic.

**Solution**:
- Create separate GitLab projects for frontend and backend
- Independent CI/CD pipelines with different stages
- Separate SonarQube projects for independent quality gates
- Timestamp-based naming for multiple sample coexistence
