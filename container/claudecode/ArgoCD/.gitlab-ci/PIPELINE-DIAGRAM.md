# GitLab CI/CD Pipeline Flow Diagram

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GITLAB CI/CD PIPELINE                       │
│                     Organization Management System                   │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: BUILD BACKEND                                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐                                                         │
│  │ maven-build  │  ─── mvn clean compile                                 │
│  └──────┬───────┘                                                         │
│         │                                                                 │
│         └─→ Artifacts: app/backend/target/  (1 hour)                     │
│         └─→ Cache: .m2/repository/                                        │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: TEST BACKEND                                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐                                                         │
│  │  maven-test  │  ─── mvn test + JaCoCo coverage                        │
│  └──────┬───────┘                                                         │
│         │                                                                 │
│         └─→ Artifacts: target/site/jacoco/  (1 week)                     │
│         └─→ Coverage: 80% minimum                                         │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: BUILD FRONTEND                                                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐                                                         │
│  │  npm-build   │  ─── npm ci && npm run build                           │
│  └──────┬───────┘                                                         │
│         │                                                                 │
│         └─→ Artifacts: app/frontend/dist/  (1 hour)                      │
│         └─→ Cache: node_modules/                                          │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: TEST FRONTEND                                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐                                                         │
│  │   npm-test   │  ─── npm test --coverage                               │
│  └──────┬───────┘                                                         │
│         │                                                                 │
│         └─→ Artifacts: coverage/  (1 week)                               │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: PACKAGE                                                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐              ┌──────────────────┐                  │
│  │ package-backend  │              │ package-frontend │                  │
│  └────────┬─────────┘              └────────┬─────────┘                  │
│           │                                 │                             │
│           │ mvn package                     │ tar -czf                    │
│           │                                 │                             │
│           └─→ orgmgmt-backend.jar           └─→ frontend-{VERSION}.tgz   │
│               (1 day)                           (1 day)                   │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: NEXUS DEPLOY                      [Only: main, develop]         │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐              ┌──────────────────┐                  │
│  │  deploy-maven    │              │   deploy-npm     │                  │
│  └────────┬─────────┘              └────────┬─────────┘                  │
│           │                                 │                             │
│           │ mvn deploy                      │ curl upload                 │
│           │                                 │                             │
│           ↓                                 ↓                             │
│  ┌────────────────────────────────────────────────────┐                  │
│  │         Nexus Repository Manager                   │                  │
│  │  - maven-snapshots/orgmgmt-backend.jar             │                  │
│  │  - npm-hosted/frontend-{VERSION}.tgz               │                  │
│  └────────────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 7: CONTAINER BUILD                   [Only: main, develop]         │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐                                                     │
│  │ build-containers │                                                     │
│  └────────┬─────────┘                                                     │
│           │                                                               │
│           │ 1. build-from-nexus.sh                                        │
│           │    - Download from Nexus                                      │
│           │    - Build backend image                                      │
│           │    - Build frontend image                                     │
│           │                                                               │
│           │ 2. push-to-registry.sh                                        │
│           │    - Push images to registry                                  │
│           │                                                               │
│           ↓                                                               │
│  ┌────────────────────────────────────────────────────┐                  │
│  │         Container Registry (localhost:5005)        │                  │
│  │  - orgmgmt-backend:{VERSION}                       │                  │
│  │  - orgmgmt-frontend:{VERSION}                      │                  │
│  └────────────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 8: GITOPS UPDATE                          [Only: main]             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐                                                     │
│  │ update-manifests │                                                     │
│  └────────┬─────────┘                                                     │
│           │                                                               │
│           │ update-gitops.sh                                              │
│           │ - Update image tags                                           │
│           │ - Update podman-compose.yml                                   │
│           │ - Commit changes                                              │
│           │                                                               │
│           ↓                                                               │
│  ┌────────────────────────────────────────────────────┐                  │
│  │    Git Repository: gitops/dev/                     │                  │
│  │    Updated: podman-compose.yml                     │                  │
│  └────────────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 9: ARGOCD SYNC                            [Only: main]             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐                                                     │
│  │    deploy-dev    │                                                     │
│  └────────┬─────────┘                                                     │
│           │                                                               │
│           │ sync-argocd.sh dev                                            │
│           │ - argocd login                                                │
│           │ - argocd app sync orgmgmt-dev                                 │
│           │ - argocd app wait orgmgmt-dev                                 │
│           │                                                               │
│           ↓                                                               │
│  ┌────────────────────────────────────────────────────┐                  │
│  │         ArgoCD (localhost:5010)                    │                  │
│  │  Application: orgmgmt-dev                          │                  │
│  │  Status: Synced & Healthy                          │                  │
│  └────────┬───────────────────────────────────────────┘                  │
│           │                                                               │
│           │ Deploys to Podman                                             │
│           ↓                                                               │
│  ┌────────────────────────────────────────────────────┐                  │
│  │         Running Containers                         │                  │
│  │  - orgmgmt-backend:8080                            │                  │
│  │  - orgmgmt-frontend:5006                           │                  │
│  │  - postgres:5432                                   │                  │
│  └────────────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────────┐
│ STAGE 10: E2E TEST                              [Only: main]             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐                                                     │
│  │ playwright-tests │                                                     │
│  └────────┬─────────┘                                                     │
│           │                                                               │
│           │ 1. check-health.sh                                            │
│           │    - Verify backend health                                    │
│           │    - Verify frontend accessibility                            │
│           │                                                               │
│           │ 2. npm run test:e2e                                           │
│           │    - Run Playwright tests                                     │
│           │    - Generate reports                                         │
│           │                                                               │
│           └─→ Artifacts: playwright-report/, screenshots/                │
│               (1 week, allow_failure: true)                               │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                          PIPELINE COMPLETE ✓                              │
└───────────────────────────────────────────────────────────────────────────┘
```

## Branch-Specific Behavior

### Feature Branch Flow
```
[Stages 1-5 Only]

build-backend → test-backend → build-frontend → test-frontend → package
     ↓              ↓               ↓               ↓              ↓
  Maven         JaCoCo           Vite             Jest       JAR + TGZ
  compile       coverage         build          coverage    artifacts

[STOP HERE - No deployment]
```

### Develop Branch Flow
```
[Stages 1-7]

Feature Branch Flow (1-5)
         ↓
nexus-deploy → container-build
     ↓               ↓
Maven + NPM     Build + Push
to Nexus        to Registry

[STOP HERE - No GitOps/ArgoCD]
```

### Main Branch Flow
```
[All Stages 1-10]

Develop Branch Flow (1-7)
         ↓
gitops-update → argocd-sync → e2e-test
     ↓               ↓            ↓
Update YAML    Deploy to Dev  Playwright
manifests      with ArgoCD    tests

[COMPLETE PIPELINE]
```

## Data Flow Diagram

```
┌──────────┐
│   Code   │
│  Commit  │
└────┬─────┘
     │
     ↓
┌────────────────┐
│  Source Code   │
│   (GitLab)     │
└────┬───────────┘
     │
     ├─→ Build Backend  ─→ JAR ────────┐
     │                                  │
     └─→ Build Frontend ─→ Tarball ────┤
                                        │
                                        ↓
                               ┌────────────────┐
                               │  Nexus Repo    │
                               │  - JAR         │
                               │  - Tarball     │
                               └────┬───────────┘
                                    │
                                    ↓
                          ┌──────────────────┐
                          │ Container Build  │
                          │ (from Nexus)     │
                          └────┬─────────────┘
                               │
                               ↓
                       ┌────────────────────┐
                       │ Container Registry │
                       │ - Backend image    │
                       │ - Frontend image   │
                       └────┬───────────────┘
                            │
                            ↓
                    ┌────────────────────┐
                    │  GitOps Update     │
                    │  (manifests)       │
                    └────┬───────────────┘
                         │
                         ↓
                 ┌────────────────────┐
                 │  ArgoCD Sync       │
                 └────┬───────────────┘
                      │
                      ↓
              ┌────────────────────┐
              │ Podman Containers  │
              │ - Backend          │
              │ - Frontend         │
              │ - Database         │
              └────┬───────────────┘
                   │
                   ↓
           ┌────────────────────┐
           │   E2E Testing      │
           └────────────────────┘
```

## Artifact Lifecycle

```
Build Phase:
  maven-build    → target/                    [1 hour]
  npm-build      → dist/                      [1 hour]

Test Phase:
  maven-test     → target/site/jacoco/        [1 week]
  npm-test       → coverage/                  [1 week]

Package Phase:
  package-backend  → *.jar                    [1 day]
  package-frontend → *.tgz                    [1 day]

Deploy Phase:
  deploy-maven   → Nexus (permanent)
  deploy-npm     → Nexus (permanent)

Container Phase:
  build-containers → Registry (tagged by commit SHA)

Test Phase:
  playwright-tests → playwright-report/       [1 week]
```

## Cache Strategy Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Maven Cache Flow                         │
└─────────────────────────────────────────────────────────────┘

First Run (Cold Cache):
  maven-build → Download deps → Populate .m2/repository/
                                       ↓
                                  [Cache Saved]
                                       ↓
  maven-test  → Reads from .m2/repository/ (cache hit)
       ↓
  package-backend → Reads from .m2/repository/ (cache hit)
       ↓
  deploy-maven → Reads from .m2/repository/ (cache hit)

Subsequent Runs (Warm Cache):
  maven-build → [Cache Hit] → Skip downloads (40% faster)

┌─────────────────────────────────────────────────────────────┐
│                     NPM Cache Flow                          │
└─────────────────────────────────────────────────────────────┘

First Run (Cold Cache):
  npm-build → npm ci → Download packages → node_modules/
                                                 ↓
                                           [Cache Saved]
                                                 ↓
  npm-test → Reads from node_modules/ (cache hit)
       ↓
  playwright-tests → Reads from node_modules/ (cache hit)

Subsequent Runs (Warm Cache):
  npm-build → [Cache Hit] → Skip downloads (50% faster)
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling                           │
└─────────────────────────────────────────────────────────────┘

Job Execution:
     │
     ├─→ Success → Continue to next stage
     │
     ├─→ Failure (allow_failure: false) → STOP PIPELINE
     │                                       │
     │                                       ↓
     │                              Notify developer
     │                                       ↓
     │                              Review job logs
     │                                       ↓
     │                              Fix issue & re-run
     │
     └─→ Failure (allow_failure: true) → Continue pipeline
                                           │
                                           ↓
                                  Mark as warning
```

## Parallel Execution

```
┌─────────────────────────────────────────────────────────────┐
│                 Parallel Job Execution                      │
└─────────────────────────────────────────────────────────────┘

Stage 5: Package
  ┌──────────────────┐        ┌──────────────────┐
  │ package-backend  │   ||   │ package-frontend │
  └──────────────────┘        └──────────────────┘
           ↓                           ↓
        JAR file                   Tarball
           └───────────┬───────────────┘
                       ↓

Stage 6: Nexus Deploy
  ┌──────────────────┐        ┌──────────────────┐
  │  deploy-maven    │   ||   │   deploy-npm     │
  └──────────────────┘        └──────────────────┘
           ↓                           ↓
      Maven repo                   NPM repo
           └───────────┬───────────────┘
                       ↓
           Both complete before next stage

Time Saved: ~2-3 minutes per pipeline run
```

## Environment Configuration

```
┌─────────────────────────────────────────────────────────────┐
│              Environment-Specific Configuration             │
└─────────────────────────────────────────────────────────────┘

Development (orgmgmt-dev)
  ├─ Branch: main
  ├─ Auto-sync: Enabled
  ├─ URL: http://localhost:5006
  └─ Tests: E2E enabled

Staging (orgmgmt-staging)
  ├─ Branch: release/*
  ├─ Auto-sync: Manual approval
  ├─ URL: TBD
  └─ Tests: E2E enabled

Production (orgmgmt-prod)
  ├─ Branch: tags (v*.*.*)
  ├─ Auto-sync: Manual approval
  ├─ URL: TBD
  └─ Tests: Smoke tests only
```

---

## Legend

```
┌─────────┐
│  Stage  │  = Pipeline stage
└─────────┘

┌─────────┐
│   Job   │  = Individual job
└─────────┘

─→  = Sequential flow
||  = Parallel execution
↓   = Dependency
```

---

**Note:** This diagram represents the complete pipeline flow. Actual execution varies by branch as shown in the "Branch-Specific Behavior" section.
