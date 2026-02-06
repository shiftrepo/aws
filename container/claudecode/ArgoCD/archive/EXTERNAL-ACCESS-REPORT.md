# Frontend Service External Access Report

**Date**: 2026-02-05T08:08:09Z
**Service**: Organization Management Frontend

## Access Information

### Public Access
- **Public IP**: 13.219.96.72
- **Primary URL**: http://13.219.96.72:5006
- **NodePort URL**: http://13.219.96.72:30006

### Internal Access
- **Private IP**: 10.0.1.191
- **Internal URL**: http://10.0.1.191:5006
- **Cluster IP**: http://10.0.1.191:5006

## Service Configuration

- **Service Type**: NodePort
- **Service Port**: 5006
- **NodePort**: 30006
- **Target Port**: 80 (container)
- **Replicas**: 3
- **Load Balancing**: Round-robin

## Firewall Status

- **Port Forwarding**: 5006 -> 30006 (via socat)
- **NodePort Direct**: 30006 (via K3s)
- **Systemd Service**: k3s-frontend-forward.service

## Access Tests

- **NodePort (30006)**: PASSED
- **Port Forward (5006)**: PASSED
- **Private IP (5006)**: PASSED

## AWS Security Group Requirements

**Inbound Rules to Add:**

```
Type: Custom TCP
Port: 5006
Source: 0.0.0.0/0 (anywhere) or your IP

Type: Custom TCP
Port: 30006
Source: 0.0.0.0/0 (anywhere) or your IP
```

## Verification Commands

```bash
# Test from local machine
curl http://13.219.96.72:5006/health
curl http://13.219.96.72:30006/health

# Check service status
kubectl get svc orgmgmt-frontend -n default

# Check port forwarding service
systemctl status k3s-frontend-forward

# Check pods
kubectl get pods -l app=orgmgmt-frontend -n default
```

## Troubleshooting

If you cannot access the service:

1. Check AWS Security Group allows ports 5006 and 30006
2. Verify service is running: `systemctl status k3s-frontend-forward`
3. Check K3s service: `kubectl get svc orgmgmt-frontend`
4. Test locally first: `curl http://127.0.0.1:5006/health`

## Next Steps

1. Add AWS Security Group rules for ports 5006 and 30006
2. Test access from browser: http://13.219.96.72:5006
3. Verify round-robin load balancing is working
