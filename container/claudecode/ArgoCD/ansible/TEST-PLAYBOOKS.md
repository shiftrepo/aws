# Testing Ansible Playbooks

## Pre-Test Checklist

Before testing, ensure:
- [ ] RHEL/Rocky/CentOS 9 system
- [ ] 8GB RAM available
- [ ] 50GB disk space available
- [ ] Sudo/root access
- [ ] Internet connectivity
- [ ] No conflicting services on ports 5003, 5010, 8081, etc.

## Test Scenarios

### Test 1: Bootstrap Script (Recommended)

**Purpose:** Test the complete automated setup

**Steps:**
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```

**Expected Result:**
- Ansible installs (if not present)
- All prerequisites install
- All 9 containers start
- All services become healthy
- CREDENTIALS.txt created
- verify-environment.sh created
- Bootstrap log created

**Time:** 15-30 minutes

**Verification:**
```bash
# Check containers
podman ps | wc -l
# Should show 10 lines (9 containers + header)

# Check credentials
test -f /root/aws.git/container/claudecode/ArgoCD/CREDENTIALS.txt && echo "PASS" || echo "FAIL"

# Run verification
/root/aws.git/container/claudecode/ArgoCD/verify-environment.sh
```

### Test 2: Master Playbook

**Purpose:** Test the complete environment setup playbook

**Steps:**
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# Ensure Ansible is installed
sudo dnf install -y ansible

# Run playbook
ansible-playbook playbooks/setup_complete_environment.yml --ask-become-pass
```

**Expected Result:**
- All 6 phases complete successfully
- All services healthy
- CREDENTIALS.txt created

**Time:** 15-30 minutes

**Verification:**
```bash
ansible-playbook playbooks/verify_environment.yml
```

### Test 3: Step-by-Step Playbooks

**Purpose:** Test individual playbooks in sequence

**Steps:**
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# Test 1: Prerequisites
ansible-playbook playbooks/install_prerequisites.yml --ask-become-pass

# Verify
node --version  # Should show v20.x
mvn --version   # Should show 3.9.x
podman-compose --version

# Test 2: Registry Configuration
ansible-playbook playbooks/configure_podman_registry.yml --ask-become-pass

# Verify
test -f /etc/containers/registries.conf.d/gitlab.conf && echo "PASS"

# Test 3: ArgoCD CLI
ansible-playbook playbooks/install_argocd.yml --ask-become-pass

# Verify
argocd version --client

# Test 4: Infrastructure
ansible-playbook playbooks/deploy_infrastructure.yml

# Verify
podman ps

# Test 5: Application Setup
ansible-playbook playbooks/setup_application.yml

# Verify
argocd version
```

**Expected Result:** Each playbook succeeds independently

**Time:** 20-30 minutes total

### Test 4: Verification Playbook

**Purpose:** Test the environment verification

**Prerequisites:** Infrastructure must be running

**Steps:**
```bash
ansible-playbook playbooks/verify_environment.yml
```

**Expected Output:**
```
Services Healthy: 6/6
Containers: 9/9
Overall Status: HEALTHY
```

**Time:** 1 minute

### Test 5: Cleanup Playbook

**Purpose:** Test cleanup without data deletion

**Steps:**
```bash
# Stop containers only
ansible-playbook playbooks/cleanup_environment.yml

# Verify containers stopped
podman ps -a | grep orgmgmt

# Verify volumes preserved
podman volume ls | grep orgmgmt
```

**Expected Result:**
- All containers stopped
- Volumes still exist
- Images still exist

**Time:** 1-2 minutes

### Test 6: Complete Cleanup

**Purpose:** Test complete cleanup with data deletion

**Warning:** This is DESTRUCTIVE!

**Steps:**
```bash
# Complete cleanup
ansible-playbook playbooks/cleanup_environment.yml \
  -e cleanup_volumes=true \
  -e cleanup_images=true \
  -e cleanup_network=true

# Verify
podman ps -a | grep orgmgmt  # Should be empty
podman volume ls | grep orgmgmt  # Should be empty
```

**Expected Result:**
- All containers removed
- All volumes removed
- All images removed
- Network removed

**Time:** 2-3 minutes

### Test 7: Idempotency Test

**Purpose:** Verify playbooks are safe to run multiple times

**Steps:**
```bash
# Run complete setup
./bootstrap.sh

# Run again
./bootstrap.sh

# Or run playbook again
ansible-playbook playbooks/setup_complete_environment.yml --ask-become-pass
```

**Expected Result:**
- No errors
- Services remain healthy
- No duplicate containers
- Minimal changes reported

**Time:** 5-10 minutes second run

### Test 8: Site Playbook

**Purpose:** Test the master site.yml playbook

**Steps:**
```bash
# With confirmation
ansible-playbook playbooks/site.yml --ask-become-pass

# Without confirmation
ANSIBLE_AUTO_CONTINUE=true ansible-playbook playbooks/site.yml --ask-become-pass
```

**Expected Result:**
- All 4 playbooks execute
- Services configured and running

**Time:** 15-20 minutes

### Test 9: Tag-Based Execution

**Purpose:** Test running specific phases with tags

**Steps:**
```bash
# Registry only
ansible-playbook playbooks/site.yml --tags registry --ask-become-pass

# CLI only
ansible-playbook playbooks/site.yml --tags cli --ask-become-pass

# Infrastructure only
ansible-playbook playbooks/site.yml --tags infrastructure

# Application only
ansible-playbook playbooks/site.yml --tags application
```

**Expected Result:** Only tagged tasks execute

**Time:** 1-15 minutes per tag

### Test 10: Custom Variables

**Purpose:** Test variable overrides

**Steps:**
```bash
ansible-playbook playbooks/setup_complete_environment.yml \
  -e postgres_password="TestPass123!" \
  -e gitlab_password="GitLabTest123!" \
  -e skip_application_build=true \
  --ask-become-pass
```

**Expected Result:**
- Custom passwords used
- Build phase skipped
- Credentials file contains custom passwords

**Time:** 10-20 minutes

### Test 11: Check Mode (Dry Run)

**Purpose:** Test playbook logic without making changes

**Steps:**
```bash
ansible-playbook playbooks/setup_complete_environment.yml --check
```

**Expected Result:**
- Shows what would be changed
- No actual changes made
- No errors in logic

**Time:** 1-2 minutes

### Test 12: Verbose Mode

**Purpose:** Test detailed output

**Steps:**
```bash
# Verbose
ansible-playbook playbooks/verify_environment.yml -v

# Very verbose
ansible-playbook playbooks/verify_environment.yml -vv

# Debug level
ansible-playbook playbooks/verify_environment.yml -vvv
```

**Expected Result:** Detailed execution information

**Time:** 1-2 minutes

## Automated Test Script

Create a test script:

```bash
#!/bin/bash
# test-ansible-setup.sh

set -e

BASE_DIR="/root/aws.git/container/claudecode/ArgoCD"
ANSIBLE_DIR="$BASE_DIR/ansible"

echo "=========================================="
echo "Testing Ansible Playbooks"
echo "=========================================="

# Test 1: Check files exist
echo "Test 1: Checking files..."
test -f "$ANSIBLE_DIR/bootstrap.sh" && echo "✓ bootstrap.sh exists"
test -f "$ANSIBLE_DIR/playbooks/setup_complete_environment.yml" && echo "✓ setup_complete_environment.yml exists"
test -f "$ANSIBLE_DIR/group_vars/all.yml" && echo "✓ all.yml exists"

# Test 2: Check script is executable
echo "Test 2: Checking executability..."
test -x "$ANSIBLE_DIR/bootstrap.sh" && echo "✓ bootstrap.sh is executable"

# Test 3: Syntax check
echo "Test 3: Checking YAML syntax..."
ansible-playbook "$ANSIBLE_DIR/playbooks/setup_complete_environment.yml" --syntax-check && echo "✓ Syntax valid"

# Test 4: List tasks
echo "Test 4: Listing tasks..."
ansible-playbook "$ANSIBLE_DIR/playbooks/setup_complete_environment.yml" --list-tasks > /dev/null && echo "✓ Tasks listed"

# Test 5: Check mode
echo "Test 5: Running in check mode..."
ansible-playbook "$ANSIBLE_DIR/playbooks/verify_environment.yml" --check && echo "✓ Check mode passed"

echo "=========================================="
echo "Basic tests passed!"
echo "Run full test with: ./bootstrap.sh"
echo "=========================================="
```

## Test Matrix

| Test | Duration | Destructive | Requires Sudo | Network |
|------|----------|-------------|---------------|---------|
| Bootstrap Script | 15-30 min | No | Yes | Yes |
| Master Playbook | 15-30 min | No | Yes | Yes |
| Step-by-Step | 20-30 min | No | Yes | Yes |
| Verification | 1 min | No | No | No |
| Cleanup (Safe) | 1-2 min | No | No | No |
| Complete Cleanup | 2-3 min | Yes | No | No |
| Idempotency | 5-10 min | No | Yes | Yes |
| Site Playbook | 15-20 min | No | Yes | Yes |
| Tag-Based | 1-15 min | No | Yes | Varies |
| Custom Variables | 10-20 min | No | Yes | Yes |
| Check Mode | 1-2 min | No | No | No |
| Verbose Mode | 1-2 min | No | No | No |

## Success Criteria

### Must Pass
- [ ] Bootstrap script completes without errors
- [ ] All 9 containers start successfully
- [ ] All 6 services report healthy
- [ ] CREDENTIALS.txt created with all passwords
- [ ] verify-environment.sh works correctly
- [ ] Cleanup preserves data when requested
- [ ] Idempotency - can run multiple times safely

### Should Pass
- [ ] All individual playbooks work independently
- [ ] Tags filter execution correctly
- [ ] Custom variables override defaults
- [ ] Check mode reports no errors
- [ ] Verbose mode provides detailed output

### Nice to Have
- [ ] Complete setup in under 20 minutes (on fast network)
- [ ] No warnings in output
- [ ] All documentation accurate
- [ ] Error messages helpful

## Known Issues and Limitations

### GitLab Startup Time
- GitLab takes 5-10 minutes to fully start
- Health check may timeout on slow systems
- **Solution:** Increase retries in playbook

### Resource Requirements
- Minimum 8GB RAM required
- May fail with less memory
- **Solution:** Check memory before starting

### Network Dependency
- Requires internet for downloads
- May fail on slow connections
- **Solution:** Pre-download images

### Port Conflicts
- Fails if ports already in use
- Common conflicts: 5003, 5010, 8081
- **Solution:** Check ports before starting

## Troubleshooting Tests

### Test Failed - What to Check

1. **Check Logs**
   ```bash
   tail -f logs/bootstrap-*.log
   ```

2. **Check Ansible Version**
   ```bash
   ansible --version
   # Should be 2.9+
   ```

3. **Check System Resources**
   ```bash
   free -h
   df -h
   ```

4. **Check Port Availability**
   ```bash
   sudo ss -tulpn | grep -E ':(5003|5010|8081|5432)'
   ```

5. **Check Container Status**
   ```bash
   podman ps -a
   podman logs <container-name>
   ```

6. **Run Verification**
   ```bash
   ansible-playbook playbooks/verify_environment.yml -vv
   ```

## Reporting Issues

When reporting test failures, include:

1. Test name and number
2. OS version: `cat /etc/os-release`
3. System resources: `free -h && df -h`
4. Ansible version: `ansible --version`
5. Error message or log excerpt
6. Container status: `podman ps -a`
7. Full log file if available

## Continuous Testing

### Regular Tests
```bash
# Daily: Quick verification
ansible-playbook playbooks/verify_environment.yml

# Weekly: Complete setup test
./bootstrap.sh

# Monthly: Full cleanup and rebuild
ansible-playbook playbooks/cleanup_environment.yml -e cleanup_volumes=true
./bootstrap.sh
```

### Pre-Deployment Tests
```bash
# Before making changes
ansible-playbook playbooks/setup_complete_environment.yml --check

# After making changes
./bootstrap.sh
ansible-playbook playbooks/verify_environment.yml
```

## Performance Benchmarks

Target times on reference hardware (4 CPU, 16GB RAM, SSD, 100Mbps):

| Phase | Target | Acceptable | Slow |
|-------|--------|------------|------|
| Prerequisites | 5 min | 10 min | >15 min |
| Infrastructure | 10 min | 15 min | >20 min |
| Configuration | 2 min | 5 min | >7 min |
| Applications | 5 min | 10 min | >15 min |
| ArgoCD Setup | 1 min | 2 min | >3 min |
| Verification | 30 sec | 1 min | >2 min |
| **Total** | **20 min** | **30 min** | **>45 min** |

## Conclusion

A comprehensive test suite covering:
- ✅ Automated setup
- ✅ Manual setup
- ✅ Individual components
- ✅ Complete workflow
- ✅ Cleanup procedures
- ✅ Idempotency
- ✅ Error handling

All tests should pass before considering the setup production-ready.
