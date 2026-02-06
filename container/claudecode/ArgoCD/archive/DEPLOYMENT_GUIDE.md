# Redis Session Management - Quick Deployment Guide

**Date:** 2026-02-06
**Feature:** Redis Session Management & System Information Display

---

## Quick Start

### 1. Build and Deploy

```bash
cd /root/aws.git/container/claudecode/ArgoCD

# Build backend and frontend containers
./scripts/build-and-deploy.sh --environment dev

# Deploy to Kubernetes
kubectl apply -f k8s-manifests/backend-deployment.yaml
kubectl apply -f k8s-manifests/backend-service.yaml
```

### 2. Verify Backend Deployment

```bash
# Check pod status (should show 2/2 running)
kubectl get pods -l app=orgmgmt-backend

# View logs
kubectl logs -l app=orgmgmt-backend --tail=50 -f

# Check for Redis connection success
kubectl logs -l app=orgmgmt-backend | grep -i redis

# Check service
kubectl get svc orgmgmt-backend
```

### 3. Test System Info Endpoint

```bash
# Test the API endpoint
curl -c cookies.txt http://10.0.1.191:8083/api/system/info

# Should return JSON like:
# {
#   "podName": "orgmgmt-backend-xxxxx-xxxxx",
#   "sessionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "flywayVersion": "4",
#   "databaseStatus": "OK",
#   "timestamp": "2026-02-06T..."
# }

# Test with same session cookie
curl -b cookies.txt http://10.0.1.191:8083/api/system/info
# sessionId should remain the same
```

### 4. Verify Redis Sessions

```bash
# Connect to Redis
podman exec -it argocd-redis redis-cli

# List all session keys
KEYS spring:session:orgmgmt:*

# View session data
KEYS spring:session:orgmgmt:sessions:*

# Check session count
KEYS spring:session:orgmgmt:sessions:* | wc -l

# View session TTL (should be ~1800 seconds)
TTL spring:session:orgmgmt:sessions:{session-id}

# Exit Redis CLI
exit
```

### 5. Test Frontend

```bash
# Access frontend
# http://10.0.1.191:5006

# Verify system info badges appear in navigation bar
# - Pod name should show (e.g., "orgmgmt-backend-xxxxx")
# - Session ID should show first 8 characters
# - Flyway version should show "4"

# Open browser console (F12) and check:
# - No CORS errors
# - System info updates every 30 seconds
# - Network tab shows /api/system/info requests
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check pod events
kubectl describe pod -l app=orgmgmt-backend

# View full logs
kubectl logs -l app=orgmgmt-backend --all-containers=true

# Common issues:
# 1. Redis connection failed
#    - Check: kubectl get svc | grep redis
#    - Check: podman ps | grep redis
# 2. Database connection failed
#    - Check: kubectl get svc | grep postgres
#    - Check: podman ps | grep postgres
# 3. Image pull error
#    - Check: kubectl describe pod -l app=orgmgmt-backend
```

### Redis Connection Issues

```bash
# Check Redis status
podman ps | grep redis

# If not running, start infrastructure
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d argocd-redis

# Test Redis connectivity
podman exec -it argocd-redis redis-cli PING
# Should return: PONG

# Check Redis logs
podman logs argocd-redis
```

### System Info Not Displaying

```bash
# Check frontend console for errors (F12)

# Test API directly
curl http://10.0.1.191:8083/api/system/info

# If API works but frontend doesn't display:
# 1. Check browser console for errors
# 2. Verify axios withCredentials: true
# 3. Check CORS headers in browser Network tab
# 4. Clear browser cache and reload

# Rebuild frontend if needed
cd /root/aws.git/container/claudecode/ArgoCD/app/frontend
npm run build
```

### Session ID Changes on Every Request

```bash
# This means session cookies aren't being sent

# Check:
# 1. axios withCredentials: true (should be set)
# 2. CORS headers allow credentials
# 3. Browser allows cookies (check settings)
# 4. No SameSite cookie issues

# Test with curl:
curl -c cookies.txt http://10.0.1.191:8083/api/system/info
curl -b cookies.txt http://10.0.1.191:8083/api/system/info
# sessionId should be same in both responses
```

### Pod Name Shows "unknown"

```bash
# Check if POD_NAME environment variable is set
kubectl exec -it $(kubectl get pods -l app=orgmgmt-backend -o name | head -1) -- env | grep POD_NAME

# If not set, check deployment yaml:
kubectl get deployment orgmgmt-backend -o yaml | grep -A5 POD_NAME

# Should see:
# - name: POD_NAME
#   valueFrom:
#     fieldRef:
#       fieldPath: metadata.name
```

### Database Status Shows Error

```bash
# Check database connectivity
kubectl exec -it $(kubectl get pods -l app=orgmgmt-backend -o name | head -1) -- sh -c 'curl http://localhost:8080/actuator/health'

# Check PostgreSQL status
podman ps | grep postgres

# Test database connection
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT COUNT(*) FROM organizations;"
```

---

## Testing Scenarios

### Test 1: Session Persistence

```bash
# Scenario: Session should persist across requests

# Steps:
1. Open browser to http://10.0.1.191:5006
2. Note the Session ID in navbar (first 8 chars)
3. Navigate to Organizations page
4. Navigate to Departments page
5. Navigate to Users page
6. Return to home page

# Expected: Session ID remains the same throughout

# If session changes:
# - Check browser cookies (F12 → Application → Cookies)
# - Should see SESSION cookie with HttpOnly flag
# - Check axios withCredentials: true
```

### Test 2: Multi-Pod Load Balancing

```bash
# Scenario: Different pods should be identified by pod name

# Steps:
1. Scale backend to 3 replicas:
   kubectl scale deployment orgmgmt-backend --replicas=3

2. Wait for all pods to be ready:
   kubectl get pods -l app=orgmgmt-backend -w

3. Open multiple browser windows to http://10.0.1.191:5006

4. Note pod names in navbar (may be different due to load balancing)

5. Verify session affinity:
   - Same browser should see same pod (ClientIP affinity)
   - Different IPs should see different pods

# Expected:
# - Multiple pod names visible across different clients
# - Same client sees same pod consistently (30 min affinity)
```

### Test 3: Pod Failure Recovery

```bash
# Scenario: System should survive pod restarts

# Steps:
1. Open browser to http://10.0.1.191:5006
2. Note current pod name in navbar
3. Delete the pod:
   kubectl delete pod $(kubectl get pods -l app=orgmgmt-backend -o name | head -1)

4. Wait for new pod to start:
   kubectl get pods -l app=orgmgmt-backend -w

5. Refresh browser

# Expected:
# - New pod name appears in navbar
# - New session ID (session was in Redis, but pod is new)
# - Application continues to work
# - All data still accessible
```

### Test 4: Redis Session Expiration

```bash
# Scenario: Sessions should expire after 30 minutes

# Steps:
1. Open browser to http://10.0.1.191:5006
2. Note session ID
3. Wait 31 minutes (or adjust session timeout for testing)
4. Refresh browser

# Expected:
# - New session ID appears
# - Application continues to work

# To test faster, temporarily reduce timeout:
# In application.yml: spring.session.timeout: 60s
# Rebuild and redeploy
```

### Test 5: Database Connectivity Check

```bash
# Scenario: Database status should reflect connectivity

# Steps:
1. Check current status:
   curl http://10.0.1.191:8083/api/system/info | jq .databaseStatus
   # Should return: "OK"

2. Stop database:
   podman stop orgmgmt-postgres

3. Wait 10 seconds, check again:
   curl http://10.0.1.191:8083/api/system/info | jq .databaseStatus
   # Should return: "Error: ..."

4. Start database:
   podman start orgmgmt-postgres

5. Wait 10 seconds, check again:
   curl http://10.0.1.191:8083/api/system/info | jq .databaseStatus
   # Should return: "OK"

# Expected:
# - Status accurately reflects database state
# - Error messages are descriptive
# - System recovers automatically when DB comes back
```

---

## Monitoring

### Check Backend Health

```bash
# Health endpoint
curl http://10.0.1.191:8083/actuator/health | jq

# Should return:
# {
#   "status": "UP",
#   "components": {
#     "db": { "status": "UP" },
#     "diskSpace": { "status": "UP" },
#     "ping": { "status": "UP" },
#     "redis": { "status": "UP" }
#   }
# }

# Prometheus metrics
curl http://10.0.1.191:8083/actuator/prometheus | grep session
```

### Monitor Redis

```bash
# Redis info
podman exec -it argocd-redis redis-cli INFO | grep -A10 Keyspace

# Monitor Redis commands in real-time
podman exec -it argocd-redis redis-cli MONITOR

# Check memory usage
podman exec -it argocd-redis redis-cli INFO memory | grep used_memory_human
```

### Monitor Kubernetes

```bash
# Pod status
kubectl get pods -l app=orgmgmt-backend -o wide

# Resource usage
kubectl top pods -l app=orgmgmt-backend

# Service endpoints
kubectl get endpoints orgmgmt-backend

# Events
kubectl get events --sort-by='.lastTimestamp' | grep backend
```

---

## Performance Testing

### Load Test

```bash
# Install hey (HTTP load testing tool)
# Or use ab (Apache Bench)

# Test system info endpoint
hey -n 1000 -c 10 http://10.0.1.191:8083/api/system/info

# Expected results:
# - Response time: < 50ms (p95)
# - Success rate: 100%
# - No errors in backend logs

# Monitor during test:
kubectl top pods -l app=orgmgmt-backend
```

### Session Creation Load

```bash
# Test with multiple clients (different IPs if possible)
for i in {1..100}; do
  curl -c /tmp/cookie_$i.txt http://10.0.1.191:8083/api/system/info &
done
wait

# Check Redis session count
podman exec -it argocd-redis redis-cli KEYS "spring:session:orgmgmt:sessions:*" | wc -l
# Should show 100 sessions

# Check memory usage
podman exec -it argocd-redis redis-cli INFO memory | grep used_memory_human
```

---

## Rollback Procedure

### Quick Rollback

```bash
# 1. Remove backend deployment
kubectl delete -f k8s-manifests/backend-deployment.yaml
kubectl delete -f k8s-manifests/backend-service.yaml

# 2. Revert code changes
cd /root/aws.git/container/claudecode/ArgoCD
git diff HEAD app/

# 3. If needed, revert commits
git revert HEAD

# 4. Rebuild and redeploy
./scripts/build-and-deploy.sh --environment dev
```

### Partial Rollback (Keep Backend, Disable Sessions)

```bash
# Edit application.yml
# Change:
#   spring.session.store-type: none

# Rebuild and redeploy
./scripts/build-and-deploy.sh --skip-frontend --environment dev

# Frontend will continue to work, just won't display system info
```

---

## Production Checklist

Before deploying to production:

- [ ] Update CORS configuration to restrict origins
- [ ] Migrate database password to Kubernetes Secret
- [ ] Configure Redis persistence (RDB/AOF)
- [ ] Set up Redis replication or clustering
- [ ] Configure session cookie secure flag
- [ ] Enable HTTPS for frontend and backend
- [ ] Set up monitoring alerts (Prometheus/Grafana)
- [ ] Configure log aggregation (ELK stack)
- [ ] Review resource limits (CPU/memory)
- [ ] Test disaster recovery procedure
- [ ] Document production troubleshooting steps
- [ ] Set up backup for Redis data
- [ ] Configure rate limiting for API endpoints
- [ ] Review security scanning results
- [ ] Update documentation with production URLs

---

## Useful Commands Reference

```bash
# Backend
kubectl get pods -l app=orgmgmt-backend
kubectl logs -l app=orgmgmt-backend --tail=100 -f
kubectl describe pod -l app=orgmgmt-backend
kubectl exec -it <pod-name> -- sh

# Service
kubectl get svc orgmgmt-backend
kubectl describe svc orgmgmt-backend
kubectl get endpoints orgmgmt-backend

# Redis
podman exec -it argocd-redis redis-cli
podman logs argocd-redis --tail=50 -f

# Database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Frontend
curl http://10.0.1.191:5006
kubectl get pods -l app=orgmgmt-frontend

# System Info
curl http://10.0.1.191:8083/api/system/info | jq
curl -c cookies.txt -b cookies.txt http://10.0.1.191:8083/api/system/info

# Health Check
curl http://10.0.1.191:8083/actuator/health | jq
curl http://10.0.1.191:8083/actuator/prometheus

# Scale
kubectl scale deployment orgmgmt-backend --replicas=3
kubectl get hpa  # if horizontal pod autoscaler configured

# Cleanup
kubectl delete -f k8s-manifests/backend-deployment.yaml
kubectl delete -f k8s-manifests/backend-service.yaml
```

---

**Generated:** 2026-02-06
**Status:** Ready for Deployment
**Next Step:** Run `./scripts/build-and-deploy.sh`
