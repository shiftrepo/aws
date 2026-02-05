# Ansible Automation - Complete Index

## Quick Navigation

### For New Users
1. Start here: [QUICKSTART.md](QUICKSTART.md)
2. Then read: [README-COMPLETE-SETUP.md](README-COMPLETE-SETUP.md)
3. Run this: `./bootstrap.sh`

### For Experienced Users
1. Quick reference: [PLAYBOOKS.md](PLAYBOOKS.md)
2. All playbooks: `playbooks/` directory
3. Variables: [group_vars/all.yml](group_vars/all.yml)

### For Troubleshooting
1. Common issues: [README-COMPLETE-SETUP.md#troubleshooting](README-COMPLETE-SETUP.md#troubleshooting)
2. Test suite: [TEST-PLAYBOOKS.md](TEST-PLAYBOOKS.md)
3. Verification: `ansible-playbook playbooks/verify_environment.yml`

## File Organization

### 🚀 Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - One-command setup, 5-minute guide
- **[bootstrap.sh](bootstrap.sh)** - Automated setup script (RECOMMENDED)
- **[README-COMPLETE-SETUP.md](README-COMPLETE-SETUP.md)** - Comprehensive 50+ page guide

### 📚 Reference Documentation
- **[PLAYBOOKS.md](PLAYBOOKS.md)** - Complete playbook reference
- **[ANSIBLE-SETUP-SUMMARY.md](ANSIBLE-SETUP-SUMMARY.md)** - What was created, overview
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and patterns
- **[README.md](README.md)** - Main README

### 🧪 Testing
- **[TEST-PLAYBOOKS.md](TEST-PLAYBOOKS.md)** - Test scenarios and validation
- **[playbooks/verify_environment.yml](playbooks/verify_environment.yml)** - Automated verification

### ⚙️ Configuration
- **[group_vars/all.yml](group_vars/all.yml)** - All variables and settings
- **[inventory/hosts.yml](inventory/hosts.yml)** - Inventory configuration
- **[ansible.cfg](ansible.cfg)** - Ansible configuration

### 🎭 Playbooks

#### Main Playbooks
- **[playbooks/setup_complete_environment.yml](playbooks/setup_complete_environment.yml)** - Master playbook (15-30 min)
- **[playbooks/site.yml](playbooks/site.yml)** - Sequential execution of all playbooks

#### Component Playbooks
- **[playbooks/install_prerequisites.yml](playbooks/install_prerequisites.yml)** - System packages, build tools
- **[playbooks/configure_podman_registry.yml](playbooks/configure_podman_registry.yml)** - Registry configuration
- **[playbooks/install_argocd.yml](playbooks/install_argocd.yml)** - ArgoCD CLI installation
- **[playbooks/deploy_infrastructure.yml](playbooks/deploy_infrastructure.yml)** - Start all containers
- **[playbooks/setup_application.yml](playbooks/setup_application.yml)** - Service configuration

#### Utility Playbooks
- **[playbooks/verify_environment.yml](playbooks/verify_environment.yml)** - Health checks
- **[playbooks/cleanup_environment.yml](playbooks/cleanup_environment.yml)** - Stop and cleanup

### 📊 Documentation Structure
- **[STRUCTURE.txt](STRUCTURE.txt)** - Directory structure
- **[SUMMARY.md](SUMMARY.md)** - Project summary
- **[DIRECTORY_TREE.txt](DIRECTORY_TREE.txt)** - File tree

## Usage Patterns

### Pattern 1: First-Time Setup (Recommended)
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```
**Time:** 15-30 minutes
**Result:** Complete environment ready to use

### Pattern 2: Manual Step-by-Step
```bash
# 1. Prerequisites
ansible-playbook playbooks/install_prerequisites.yml --ask-become-pass

# 2. Configure registry
ansible-playbook playbooks/configure_podman_registry.yml --ask-become-pass

# 3. Install ArgoCD CLI
ansible-playbook playbooks/install_argocd.yml --ask-become-pass

# 4. Deploy infrastructure
ansible-playbook playbooks/deploy_infrastructure.yml

# 5. Setup applications
ansible-playbook playbooks/setup_application.yml

# 6. Verify
ansible-playbook playbooks/verify_environment.yml
```
**Time:** 20-30 minutes
**Result:** Same as Pattern 1, more control

### Pattern 3: Site Playbook (Quick)
```bash
ansible-playbook playbooks/site.yml --ask-become-pass
```
**Time:** 15-20 minutes
**Result:** Infrastructure only (no app build)

### Pattern 4: Verification Only
```bash
ansible-playbook playbooks/verify_environment.yml
```
**Time:** 1 minute
**Result:** Health check report

### Pattern 5: Cleanup and Rebuild
```bash
# Cleanup
ansible-playbook playbooks/cleanup_environment.yml -e cleanup_volumes=true

# Rebuild
./bootstrap.sh
```
**Time:** 20-35 minutes
**Result:** Fresh environment

## Common Commands

### Environment Management
```bash
# Start environment
cd infrastructure && podman-compose up -d

# Stop environment
cd infrastructure && podman-compose down

# Restart environment
cd infrastructure && podman-compose restart

# Complete setup
cd ansible && ./bootstrap.sh

# Verify health
cd ansible && ansible-playbook playbooks/verify_environment.yml
```

### Service Access
```bash
# View credentials
cat /root/aws.git/container/claudecode/ArgoCD/CREDENTIALS.txt

# Check status
podman ps

# View logs
podman logs <container-name>
podman logs -f <container-name>  # Follow

# Connect to database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# ArgoCD login
argocd login localhost:5010 --insecure --username admin
```

### Troubleshooting
```bash
# Verify environment
./verify-environment.sh
ansible-playbook playbooks/verify_environment.yml

# Check logs
tail -f logs/bootstrap-*.log

# Container diagnostics
podman inspect <container-name>
podman stats

# Network check
podman network inspect argocd-network

# Restart service
podman restart <container-name>
```

## Documentation Matrix

| Document | Audience | Length | Purpose |
|----------|----------|--------|---------|
| QUICKSTART.md | Beginners | 2 pages | Get started quickly |
| README-COMPLETE-SETUP.md | All users | 50+ pages | Complete guide |
| PLAYBOOKS.md | Operators | 15 pages | Playbook reference |
| ANSIBLE-SETUP-SUMMARY.md | Managers | 10 pages | Overview and summary |
| EXAMPLES.md | Developers | 5 pages | Usage examples |
| TEST-PLAYBOOKS.md | QA/Testers | 10 pages | Testing procedures |
| INDEX.md | All users | 3 pages | This document |

## Playbook Decision Tree

```
Need to set up environment?
├─ Yes, first time
│  └─ Use: ./bootstrap.sh
│     Time: 15-30 min
│
├─ Yes, but manual control
│  └─ Use: playbooks/setup_complete_environment.yml
│     Time: 15-30 min
│
├─ Only infrastructure needed
│  └─ Use: playbooks/site.yml
│     Time: 15-20 min
│
├─ Already running, need to verify
│  └─ Use: playbooks/verify_environment.yml
│     Time: 1 min
│
├─ Need to stop and cleanup
│  └─ Use: playbooks/cleanup_environment.yml
│     Time: 1-2 min
│
└─ Need to reinstall component
   ├─ Prerequisites → playbooks/install_prerequisites.yml
   ├─ ArgoCD CLI → playbooks/install_argocd.yml
   ├─ Registry → playbooks/configure_podman_registry.yml
   └─ Services → playbooks/setup_application.yml
```

## Support Resources

### Documentation
1. [QUICKSTART.md](QUICKSTART.md) - Fast start
2. [README-COMPLETE-SETUP.md](README-COMPLETE-SETUP.md) - Deep dive
3. [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Problem solving
4. [ARCHITECTURE.md](../ARCHITECTURE.md) - System design

### Scripts
1. `bootstrap.sh` - Automated setup
2. `verify-environment.sh` - Health checks
3. `../scripts/status.sh` - Status info
4. `../scripts/logs.sh` - Log viewing

### Playbooks
1. `setup_complete_environment.yml` - Complete setup
2. `verify_environment.yml` - Verification
3. `cleanup_environment.yml` - Cleanup

### Configuration
1. `group_vars/all.yml` - All variables
2. `ansible.cfg` - Ansible config
3. `../infrastructure/.env` - Environment variables

## Quick Links

### External Documentation
- [Ansible Documentation](https://docs.ansible.com/)
- [Podman Documentation](https://docs.podman.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Documentation](https://help.sonatype.com/repomanager3)

### Service URLs (After Setup)
- PostgreSQL: localhost:5432
- pgAdmin: http://localhost:5050
- Nexus: http://localhost:8081
- GitLab: http://localhost:5003
- GitLab Registry: http://localhost:5005
- ArgoCD: http://localhost:5010

## Version Information

### Component Versions
- PostgreSQL: 16-alpine
- Nexus: 3.63.0
- GitLab: latest
- ArgoCD: v2.10.0
- Node.js: 20.x
- Maven: 3.9.9
- Redis: 7-alpine

### System Requirements
- OS: RHEL/Rocky/CentOS 9
- RAM: 8GB minimum, 16GB recommended
- Disk: 50GB minimum, 100GB recommended
- CPU: 4+ cores recommended
- Network: Stable internet connection

## FAQ

### Q: Which file should I read first?
**A:** Start with [QUICKSTART.md](QUICKSTART.md), then [README-COMPLETE-SETUP.md](README-COMPLETE-SETUP.md)

### Q: What's the fastest way to set up?
**A:** Run `./bootstrap.sh` - it does everything automatically

### Q: How do I verify the installation?
**A:** Run `ansible-playbook playbooks/verify_environment.yml` or `./verify-environment.sh`

### Q: Where are the credentials?
**A:** In `/root/aws.git/container/claudecode/ArgoCD/CREDENTIALS.txt` after setup

### Q: How do I stop everything?
**A:** Run `cd infrastructure && podman-compose down`

### Q: How do I start everything?
**A:** Run `cd infrastructure && podman-compose up -d`

### Q: How do I clean up completely?
**A:** Run `ansible-playbook playbooks/cleanup_environment.yml -e cleanup_volumes=true`

### Q: Is it safe to run setup multiple times?
**A:** Yes, all playbooks are idempotent

### Q: How long does setup take?
**A:** 15-30 minutes first time, 5-15 minutes subsequently

### Q: What if something fails?
**A:** Check [README-COMPLETE-SETUP.md#troubleshooting](README-COMPLETE-SETUP.md#troubleshooting)

## Change Log

### Version 1.0 (Current)
- ✅ Complete automation with bootstrap.sh
- ✅ Master playbook (setup_complete_environment.yml)
- ✅ All 9 containers supported
- ✅ Comprehensive documentation
- ✅ Health check automation
- ✅ Cleanup automation
- ✅ Variables configuration
- ✅ Testing framework

### Planned Enhancements
- 🔄 SSL/TLS support
- 🔄 Backup automation
- 🔄 Monitoring integration
- 🔄 Multi-host support
- 🔄 Custom network configuration

## Contributing

When adding or modifying playbooks:

1. Update the playbook
2. Update [PLAYBOOKS.md](PLAYBOOKS.md)
3. Add examples to [EXAMPLES.md](EXAMPLES.md)
4. Add tests to [TEST-PLAYBOOKS.md](TEST-PLAYBOOKS.md)
5. Update this INDEX.md
6. Test thoroughly

## Summary

This Ansible automation provides:

✅ **9 Documents** - Comprehensive guides
✅ **8 Playbooks** - Complete automation
✅ **1 Bootstrap Script** - One-command setup
✅ **Complete Variables** - Full configuration
✅ **Testing Framework** - Validation suite

**Result:** Production-ready ArgoCD environment in 15-30 minutes.

---

**Last Updated:** 2026-02-05
**Version:** 1.0
**Maintainer:** ArgoCD Team
