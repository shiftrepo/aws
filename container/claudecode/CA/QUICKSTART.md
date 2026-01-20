# CA Infrastructure - Quick Start Guide

Quick reference for setting up and using the CA infrastructure.

## Prerequisites

- OpenSSL installed
- Docker and docker-compose installed
- sudo access

## 5-Minute Setup

### 1. Initial Setup

```bash
cd /root/aws.git/container/claudecode/CA
chmod +x scripts/*.sh scripts/utils/*.sh
./scripts/setup-ca-environment.sh
```

### 2. Generate Certificates

```bash
./scripts/create-ca.sh
```

**Prompts:**
- Server name: (default: 98.93.187.130)
- Validity days: (default: 730)
- Organization: (default: OnPremise-CA)

### 3. Start HTTPS Server

**Important: Use sudo**

```bash
sudo docker-compose up -d
```

### 4. Verify Service

```bash
# Check container status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f ca-https-test

# Test HTTPS connection (local)
curl -k https://localhost:5006/

# Test from external IP
curl -k https://98.93.187.130:5006/
```

### 5. Export Certificates (Optional)

```bash
./scripts/export-certificates.sh
```

Export package will be created in: `certs/export/ca-bundle-YYYYMMDD-HHMMSS.tar.gz`

## Common Commands

### Certificate Management

```bash
# Verify certificates
./scripts/utils/verify-certificates.sh

# View CA certificate details
openssl x509 -in certs/ca/ca.crt -noout -text

# View server certificate details
openssl x509 -in certs/server/server.crt -noout -text

# Check certificate expiration
openssl x509 -in certs/server/server.crt -noout -dates
```

### Docker Management

**All docker commands require sudo:**

```bash
# Start container
sudo docker-compose up -d

# Stop container
sudo docker-compose down

# Restart container
sudo docker-compose restart

# View container status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f

# View real-time logs
sudo docker-compose logs --tail=50 -f ca-https-test
```

### Testing

```bash
# Test HTTPS connection (skip verification)
curl -k https://98.93.187.130:5006/

# Test with CA certificate
curl --cacert certs/ca/ca.crt https://98.93.187.130:5006/

# Test health endpoint
curl -k https://98.93.187.130:5006/health

# Test certificate info endpoint
curl -k https://98.93.187.130:5006/cert-info

# View certificate details with OpenSSL
openssl s_client -connect 98.93.187.130:5006 -showcerts
```

## Browser Access

Open in your browser:
```
https://98.93.187.130:5006/
```

**Note:** Browser may show security warning. To eliminate warning, import CA certificate.

---

## Automated Client Certificate Installation

### On Server (Start Download Server)

```bash
# Start certificate download server
./scripts/serve-cert.sh

# Server will display download URLs
```

### On Client (Windows)

```powershell
# Download and run installation script
Invoke-WebRequest -Uri "http://98.93.187.130:8080/install-ca-windows.ps1" -OutFile "install-ca-windows.ps1"

# Run with Administrator privileges
powershell -ExecutionPolicy Bypass -File install-ca-windows.ps1

# Restart browser and visit https://98.93.187.130:5006/
```

### On Client (Linux)

```bash
# Download and run installation script
curl -O http://98.93.187.130:8080/install-ca-linux.sh
chmod +x install-ca-linux.sh
sudo ./install-ca-linux.sh

# Restart browser and visit https://98.93.187.130:5006/
```

### On Client (macOS)

```bash
# Download and run installation script
curl -O http://98.93.187.130:8080/install-ca-macos.sh
chmod +x install-ca-macos.sh
sudo ./install-ca-macos.sh

# Restart browser and visit https://98.93.187.130:5006/
```

---

## Manual Certificate Installation

If automated installation doesn't work, install manually:

**Get CA certificate (3 options):**
1. Use existing file: `certs/ca/ca.crt`
2. Export bundle: `./scripts/export-certificates.sh`
3. Download from browser while viewing site (see below)

**⚠️ IMPORTANT:** Install `ca.crt` (CN=OnPremise-CA-Root), NOT `server.crt` (CN=98.93.187.130)!

**Certificate Format:**
- Use `.crt` or `.pem` format (Base64-encoded X.509) - RECOMMENDED
- Save as `ca.crt` when exporting from browser
- Choose "PEM (cert)" in Firefox, "Base64-encoded X.509" in Chrome/Edge

### Export from Browser

**Chrome/Edge:**
1. Visit `https://98.93.187.130:5006/` (even with warning)
2. Click "Not Secure" → "Certificate (Invalid)" → "Details" tab
3. Select "OnPremise-CA-Root" certificate
4. Export as "Base64-encoded X.509 (.CER)", save as `ca.crt`

**Firefox:**
1. Visit site → Click warning → "View Certificate"
2. Find "OnPremise-CA-Root" → "Download" → "PEM (cert)"
3. Save as `ca.crt`

### Install CA Certificate

### Firefox
1. Settings → Privacy & Security → Certificates → View Certificates
2. Authorities tab → Import
3. Select `certs/ca/ca.crt`
4. Check "Trust this CA to identify websites"

### Chrome / Edge (Linux)
```bash
sudo cp certs/ca/ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt
sudo update-ca-certificates
```

Restart browser after installation.

## File Locations

```
CA/
├── certs/
│   ├── ca/
│   │   ├── ca.crt         # CA certificate
│   │   └── ca.key         # CA private key (600)
│   └── server/
│       ├── server.crt      # Server certificate
│       ├── server.key      # Server private key (600)
│       └── server-chain.crt # Certificate chain
├── logs/
│   └── certificate-generation.log
└── scripts/
    ├── create-ca.sh
    ├── export-certificates.sh
    └── utils/
        └── verify-certificates.sh
```

## Troubleshooting

### Container won't start

```bash
# Check if port 5006 is already in use
sudo netstat -tlnp | grep 5006

# Check container logs
sudo docker-compose logs ca-https-test

# Rebuild container
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Certificate errors

```bash
# Verify certificates
./scripts/utils/verify-certificates.sh

# Regenerate certificates
rm -rf certs/ca/* certs/server/*
./scripts/create-ca.sh
sudo docker-compose restart
```

### Permission denied errors

Make sure to use `sudo` for all docker commands:
```bash
sudo docker-compose up -d
```

### Cannot connect from external IP

```bash
# Check firewall
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=5006/tcp --permanent
sudo firewall-cmd --reload

# Or with iptables
sudo iptables -I INPUT -p tcp --dport 5006 -j ACCEPT
```

## Next Steps

- Read full documentation: `README.md`
- Export certificates for other servers: `./scripts/export-certificates.sh`
- Check certificate expiration regularly
- Set up automatic certificate renewal (if needed)

## Support

For issues or questions:
- Check logs: `logs/certificate-generation.log`
- View container logs: `sudo docker-compose logs ca-https-test`
- See full documentation: `README.md`
