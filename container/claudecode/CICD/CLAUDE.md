# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete CI/CD infrastructure project running GitLab, Nexus, SonarQube, and PostgreSQL in Docker containers with Podman. It includes a sample Spring Boot + React application demonstrating the full pipeline: build → test → coverage → static analysis → package → deploy.

**Critical Architecture Context**: All services run in containers managed by a single `docker-compose.yml`, and authentication/configuration is centralized in `.env` files with automatic token preservation on re-setup.

## Repository Purpose and Architecture

### Master Repository: `/root/aws.git/container/claudecode/CICD/`

**This is the master repository (source of truth).**

- **Purpose**: CI/CD infrastructure construction project
- **Scope**: Complete environment setup supporting EC2 scratch builds (zero-to-production setup)
- **Contents**:
  - `docker-compose.yml` - All service definitions
  - `scripts/` - Setup, backup, cleanup, credential management
  - `sample-app/` - Sample Spring Boot + React application
  - `.env` templates and configuration files

### Working Copy: `/tmp/gitlab-sample-app/`

**This is a CI/CD testing working copy, NOT the master.**

- **Purpose**: CI/CD pipeline testing and verification
- **Source**: Copied from master repository via `setup-sample-app.sh`
- **Lifecycle**: Temporary workspace for GitLab CI/CD execution

**CRITICAL PRINCIPLE**:
```
⚠️  /tmp/gitlab-sample-app/ is NOT the master repository
✅  Changes MUST be reflected back to /root/aws.git/container/claudecode/CICD/sample-app/
```

### Repository Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Master Repository                                        │
│    /root/aws.git/container/claudecode/CICD/sample-app/     │
│    (Source of Truth)                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ setup-sample-app.sh
                     │ (Copy + GitLab Configuration)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Working Copy (CI/CD Testing)                             │
│    /tmp/gitlab-sample-app/                                  │
│    - Git remote: http://EC2_IP:5003/root/sample-app.git    │
│    - CI/CD Pipeline execution                               │
│    - Test modifications                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ ✓ CI/CD Success
                     │ Manual reflection required
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Reflect Changes Back to Master                           │
│    cp /tmp/gitlab-sample-app/* → sample-app/               │
│    git commit -m "Verified CI/CD changes"                   │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Execution Script: `run-sample-app-pipeline.sh`

**Replaced `setup-sample-app.sh` in v2.1.0** - This is the current recommended method:

This script executes CI/CD pipeline testing:

1. **Copy**: Copies `sample-app/` from master to `/tmp/gitlab-sample-app/`
2. **Git Init**: Initializes fresh git repository with GitLab remote
3. **Branch**: Creates timestamped feature branch (`feature/cicd-test-YYYYMMDD-HHMMSS`)
4. **Push**: Pushes to GitLab → triggers pipeline automatically

**Key Operations**:
```bash
cd /root/aws.git/container/claudecode/CICD
./scripts/run-sample-app-pipeline.sh

# What it does:
# 1. rm -rf /tmp/gitlab-sample-app
# 2. rsync -a sample-app/ /tmp/gitlab-sample-app/
# 3. cd /tmp/gitlab-sample-app && git init
# 4. git remote add origin http://root:${GITLAB_ROOT_PASSWORD}@${EC2_PUBLIC_IP}:5003/root/sample-app.git
# 5. git checkout -b feature/cicd-test-$(date +%Y%m%d-%H%M%S)
# 6. git add . && git commit -m "pipeline: パイプライン実行 - $(date)"
# 7. git push -u origin $BRANCH_NAME
```

**Important**:
- This script does NOT modify the master repository
- Creates fresh working copy each time (no state contamination)
- Automatic pipeline trigger on push
- View results: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/pipelines

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
./scripts/utils/update-passwords.sh --ec2-host 'ec2-xx-xx-xx-xx.compute-1.amazonaws.com'
./scripts/utils/update-passwords.sh --all 'Degital2026!'  # Bulk update

# Backup and restore
./scripts/utils/backup-all.sh       # Creates backup-YYYYMMDD-HHMMSS.tar.gz
./scripts/utils/restore-all.sh backup-YYYYMMDD-HHMMSS
./scripts/cleanup-all.sh      # Delete all containers/volumes
./scripts/utils/deploy-oneclick.sh  # Backup → cleanup → restore
```

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

# Service health checks
curl http://localhost:5003/       # GitLab
curl http://localhost:8082/       # Nexus
curl http://localhost:8000/       # SonarQube
psql -h localhost -p 5001 -U cicduser -d cicddb  # PostgreSQL
```

### Sample Application Development

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

# Frontend development
cd frontend
npm install
npm run dev      # Access: http://localhost:3000
npm test
npm test -- --coverage
```

### GitLab CI/CD Management

```bash
# Register GitLab Runner (required after setup)
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

sudo systemctl enable --now gitlab-runner
sudo systemctl status gitlab-runner
sudo gitlab-runner list

# Push to trigger pipeline
cd /tmp/gitlab-sample-app
git remote set-url origin http://YOUR_IP:5003/root/sample-app.git
git push -u origin master
```

## Architecture Critical Points

### 1. Token Preservation System

**CRITICAL**: `setup-from-scratch.sh` has built-in logic to preserve SONAR_TOKEN and RUNNER_TOKEN when re-running setup:

- Step 7 detects existing `.env` files
- Reads `SONAR_TOKEN` and `RUNNER_TOKEN` from existing file
- Creates automatic backup: `.env.backup.YYYYMMDDHHMMSS`
- Regenerates `.env` with preserved tokens + new passwords

**Why This Matters**: Users manually configure SonarQube tokens and GitLab Runner tokens after initial setup. Losing these requires manual re-registration in GitLab UI.

### 2. EC2 Domain Name Dynamic Configuration

**CRITICAL**: The entire infrastructure supports dynamic EC2 domain/IP changes:

- `setup-from-scratch.sh` Step 6: Prompts for EC2 domain name (auto-detects via 169.254.169.254 if empty)
- All services use `${EC2_PUBLIC_IP}` from `.env`
- Maven settings.xml generated dynamically with password AND domain replacement
- docker-compose.yml references `${EC2_PUBLIC_IP}` for GitLab external_url, registry_external_url

**When EC2 Instance is Recreated**:
1. Run `setup-from-scratch.sh` (tokens preserved) OR `update-passwords.sh --ec2-host`
2. Update GitLab working copy git remote: `git remote set-url origin http://NEW_IP:5003/root/sample-app.git`
3. Re-register GitLab Runner with new IP

### 3. Password Architecture

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
- `scripts/setup-from-scratch.sh`: Lines 277-287 use `sed` to replace BOTH password and IP in Maven settings.xml
- `.gitignore`: Excludes `credentials.txt`, `.env.backup.*`

### 4. Multi-Module Maven Architecture

**Parent POM** (`sample-app/pom.xml`):
- Defines JaCoCo thresholds: **90%** line coverage, **90%** branch coverage
- Nexus repositories configured: `${nexus.url}` (uses `${env.EC2_PUBLIC_IP}`)
- Distribution management for snapshots/releases
- Plugin management: compiler, surefire, jacoco, sonar-maven-plugin

**Module Structure**:
- `common/`: DTOs with Lombok annotations
- `backend/`: Spring Boot 3.2 + Java 17 + JPA + Flyway migrations

**CI/CD Pipeline** (`.gitlab-ci.yml`):
- 6 stages: build → test → coverage → sonarqube → package → deploy
- Shell executor (uses host Maven, not Docker images)
- Cache: `.m2/repository`, `backend/target`
- **before_script generates settings.xml with authentication**:
  ```yaml
  <servers>
    <server>
      <id>nexus-snapshots</id>
      <username>admin</username>
      <password>Degital2026!</password>
    </server>
  </servers>
  ```
- Deploy stage: Uses same `./.m2/settings.xml` (no separate template needed)
- **CRITICAL**: `<id>` in settings.xml MUST match pom.xml distributionManagement `<id>`

### 5. Database Schema Architecture

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

### 6. Service Ports

| Service | Internal | External | Notes |
|---------|----------|----------|-------|
| PostgreSQL | 5432 | 5001 | All databases |
| pgAdmin | 80 | 5002 | DB GUI |
| GitLab HTTP | 80 | 5003 | Main UI |
| GitLab SSH | 22 | 2223 | Git operations |
| GitLab Registry | 5050 | 5005 | Container registry |
| Nexus | 8081 | 8082 | Maven/npm |
| Nexus Docker | 8083 | 8083 | Docker registry |
| SonarQube | 9000 | 8000 | Static analysis |
| Backend API | 8080 | 8501 | Spring Boot |
| Frontend | 3000 | 3000 | React dev server |

## Critical Development Patterns

### When Modifying Environment Variables

1. **Always use `update-passwords.sh`** instead of direct `.env` editing - it creates automatic backups
2. If editing `.env` manually, create backup first: `cp .env .env.backup.$(date +%Y%m%d%H%M%S)`
3. After changing passwords in `.env`, update GitLab CI/CD Variables:
   - Settings → CI/CD → Variables
   - `NEXUS_ADMIN_PASSWORD` (Masked)
   - `SONAR_TOKEN` (Masked)

### When Modifying setup-from-scratch.sh

**Line 129-216 (Step 7)**: Token preservation logic - DO NOT overwrite `.env` unconditionally
**Line 277-287 (Step 11)**: Maven settings.xml generation - MUST replace both password AND EC2_HOST

### When Adding New Services

1. Add to `docker-compose.yml` with `${ENV_VAR}` references
2. Add variables to `.env`
3. Update `scripts/utils/show-credentials.sh` to display new credentials
4. Update `scripts/utils/update-passwords.sh` with new `--service` option
5. Document in `CREDENTIALS.md`

### When Modifying CI/CD Pipeline

**GitLab Runner Requirement**: This project uses **shell executor**, NOT docker executor. All `image:` directives in `.gitlab-ci.yml` are commented out. Commands run directly on the host using installed Maven/Java.

**Quality Gate Enforcement**: SonarQube stage has `allow_failure: false` - pipeline will fail if coverage < 90% or critical bugs exist.

**Localhost Prohibition**:
- ❌ NEVER use `localhost` in CI/CD files
- ✅ ALWAYS use `${EC2_PUBLIC_IP}` environment variable
- Files affected: `.gitlab-ci.yml`, `pom.xml`, `.ci-settings.xml.template`

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

**Nexus Authentication Pattern**:
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

## Common Troubleshooting Contexts

### Pipeline Fails with 401 on Deploy Stage

**Root Cause**: Maven deploy requires authentication for `PUT` operations (uploads), while `GET` (downloads) can be anonymous.

**Diagnosis**:
```bash
# Check if server ID matches in both files
grep "<id>nexus-snapshots</id>" sample-app/pom.xml
grep "<id>nexus-snapshots</id>" sample-app/.gitlab-ci.yml
```

**Critical Requirements**:
1. **ID Match**: pom.xml `<snapshotRepository><id>` MUST exactly match settings.xml `<server><id>`
2. **Authentication in before_script**: `.gitlab-ci.yml` must generate settings.xml with `<servers>` section
3. **Deploy uses correct settings**: `mvn deploy -s ./.m2/settings.xml` (not separate template)

**Fixed in v2.1.0**: before_script now automatically generates authenticated settings.xml

### Re-setup Lost Tokens
- **Fixed in v2.1.0**: `setup-from-scratch.sh` now preserves tokens automatically
- Manual restore: `cp .env.backup.YYYYMMDDHHMMSS .env`

### EC2 IP Changed After Instance Recreation
- Run `./scripts/utils/update-passwords.sh --ec2-host NEW_IP` OR re-run `setup-from-scratch.sh`
- Update GitLab working copy git remote: `git remote set-url origin http://NEW_IP:5003/root/sample-app.git`
- Re-register GitLab Runner

### SonarQube Quality Gate Fails
- Run locally: `mvn clean test jacoco:report`
- View: `backend/target/site/jacoco/index.html`
- Need 80% line coverage, 70% branch coverage

### Container Won't Start
- SELinux: `sudo setenforce 0`
- Memory: `sudo sysctl -w vm.max_map_count=262144` (for SonarQube)
- Port conflict: `sudo ss -tuln | grep -E '5001|5002|5003|8000|8082'`

## File Modification Safety

### Never Commit These Files
- `.env` (contains passwords)
- `credentials.txt` (generated by show-credentials.sh)
- `.env.backup.*` (automatic backups)
- `volumes/` (container data)

### Always Read Before Modifying
- `scripts/setup-from-scratch.sh` - Complex token preservation logic
- `docker-compose.yml` - Environment variable references
- `sample-app/pom.xml` - Nexus URL, coverage thresholds, plugin config
- `.gitlab-ci.yml` - Pipeline stages, artifact paths, branch restrictions

### Template Files (Use sed for Dynamic Values)
- `.ci-settings.xml.template` - Maven settings for CI/CD (password placeholder)
- `config/maven/settings.xml` - Local Maven settings (password + IP placeholders)

## Version History Context

**v2.1.1** (Current - 2026-01-11):
- **Localhost Elimination**: All CI/CD files use `${EC2_PUBLIC_IP}` environment variable
- **Nexus Authentication Fix**: before_script generates authenticated settings.xml with `<servers>` section
- **Deploy Stage Simplification**: Uses unified `./.m2/settings.xml` (removed separate template dependency)
- **Coverage Threshold Increase**: 90% line/branch coverage (from 80%/70%)
- **HEREDOC Fix**: Removed single quotes to enable variable expansion
- **Pipeline Execution Script**: `run-sample-app-pipeline.sh` replaces `setup-sample-app.sh`
- **README Complete Rewrite**: 348-line comprehensive project documentation

**v2.1.0**:
- Token preservation on re-setup (SONAR_TOKEN, RUNNER_TOKEN)
- EC2 domain name dynamic configuration
- Credential management scripts (show-credentials.sh, update-passwords.sh)
- Automatic .env backup on updates
- GitLab password environment variable fix
- Maven settings dynamic substitution (password + EC2 domain)

**v2.0.0**:
- Initial complete implementation
- GitLab + Nexus + SonarQube + PostgreSQL integration
- Sample Spring Boot + React application
- 6-stage CI/CD pipeline
- Backup/restore/cleanup scripts

## Key Lessons Learned

### Maven Deploy 401 Errors
**Problem**: `mvn deploy` shows "Uploading" but returns 401 Unauthorized

**Root Cause**:
- GET operations (dependency downloads) can be anonymous via mirrors
- PUT operations (artifact uploads) ALWAYS require authentication
- Maven uses `<server><id>` to match with `<distributionManagement><id>`

**Solution**:
1. Generate settings.xml in before_script with `<servers>` section
2. Ensure exact ID match: `nexus-snapshots` in both pom.xml and settings.xml
3. Include credentials: username=admin, password=Degital2026!
4. Reuse same settings.xml in deploy stage: `-s ./.m2/settings.xml`

### Localhost vs Environment Variables
**Problem**: Hardcoded localhost/IP breaks on EC2 instance changes

**Solution**:
- Define `EC2_PUBLIC_IP` variable in `.gitlab-ci.yml`
- Use `${EC2_PUBLIC_IP}` in all URLs (Nexus, SonarQube)
- Use `${env.EC2_PUBLIC_IP}` in pom.xml properties
- HEREDOC without quotes for variable expansion

### Master vs Working Copy Confusion
**Problem**: Editing `/tmp/gitlab-sample-app/` without syncing to master

**Solution**:
- ALWAYS edit master: `/root/aws.git/container/claudecode/CICD/sample-app/`
- Use `run-sample-app-pipeline.sh` to copy master → /tmp → GitLab
- Verify sync: `diff -r sample-app/ /tmp/gitlab-sample-app/ --exclude=.git`
- Script uses `rsync -a` to preserve all files including hidden ones
