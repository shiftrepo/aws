# CA Infrastructure with HTTPS Test Interface

Self-signed Certificate Authority (CA) infrastructure for on-premise closed environments with automated certificate generation and HTTPS test server.

## Overview

This project provides a complete Certificate Authority infrastructure designed for closed on-premise environments where SSL/TLS encryption is required but self-signed certificates cause authentication errors. The solution includes:

- **Self-signed CA certificate** (4096-bit RSA)
- **Server certificates signed by CA** (2048-bit RSA)
- **Automated certificate generation** with minimal user input
- **Docker-based HTTPS test server** (Nginx on port 5006)
- **Certificate export** for use on other servers
- **No IP restrictions** - accessible from external network

## Features

### Certificate Generation
- OpenSSL-based CA and server certificate generation
- Automated workflow with intelligent defaults
- Minimal user input (server name, validity period)
- Strong encryption (CA: 4096-bit, Server: 2048-bit RSA)
- SHA-256 signing algorithm
- SubjectAltName (SAN) support for DNS and IP addresses

### HTTPS Test Environment
- Nginx-based HTTPS server in Docker container
- TLS 1.2/1.3 support
- Health check and certificate info endpoints
- Beautiful test page with detailed instructions
- External IP access with no restrictions

### Certificate Management
- Certificate verification utilities
- Certificate export for other servers
- Detailed logging
- File permission management
- Certificate chain validation

### Security
- Private keys never committed to version control
- Proper file permissions (600 for keys, 644 for certificates)
- SELinux-compatible volume mounts
- Secure defaults throughout

## Requirements

- OpenSSL
- Docker
- docker-compose
- sudo access
- Port 5006 available

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

### Basic Usage

```bash
# 1. Initial setup
./scripts/setup-ca-environment.sh

# 2. Generate certificates
./scripts/create-ca.sh

# 3. Start HTTPS server (requires sudo)
sudo docker-compose up -d

# 4. Test connection
curl -k https://98.93.187.130:5006/
```

## Directory Structure

```
CA/
├── README.md                           # This file
├── QUICKSTART.md                       # Quick start guide
├── .env                                # Environment configuration
├── .gitignore                          # Security settings
├── docker-compose.yml                  # HTTPS server definition
│
├── scripts/
│   ├── setup-ca-environment.sh        # Initial setup script
│   ├── create-ca.sh                   # Main certificate generation script
│   ├── export-certificates.sh         # Certificate export utility
│   └── utils/
│       └── verify-certificates.sh     # Certificate verification
│
├── config/
│   ├── openssl-ca.cnf                 # CA certificate OpenSSL config
│   ├── openssl-server.cnf             # Server certificate OpenSSL config
│   └── nginx/
│       ├── Dockerfile                 # Nginx container definition
│       ├── nginx.conf                 # HTTPS configuration
│       └── index.html                 # Test page
│
├── certs/                             # Generated certificates (gitignored)
│   ├── ca/
│   │   ├── ca.key                     # CA private key
│   │   ├── ca.crt                     # CA certificate
│   │   └── ca.srl                     # Serial number file
│   ├── server/
│   │   ├── server.key                 # Server private key
│   │   ├── server.csr                 # Certificate signing request
│   │   ├── server.crt                 # Server certificate
│   │   └── server-chain.crt           # Certificate chain (server + CA)
│   └── export/                        # Export packages
│       └── ca-bundle-*.tar.gz
│
└── logs/
    └── certificate-generation.log     # Operation logs
```

## Detailed Usage

### 1. Initial Setup

Run the setup script to verify dependencies and create directory structure:

```bash
chmod +x scripts/*.sh scripts/utils/*.sh
./scripts/setup-ca-environment.sh
```

This script will:
- Check for OpenSSL, Docker, and docker-compose
- Create necessary directories
- Set execute permissions on scripts
- Verify .env and .gitignore files

### 2. Generate Certificates

Run the certificate generation script:

```bash
./scripts/create-ca.sh
```

**Interactive Mode** (default):
- Prompts for server name (default: 98.93.187.130)
- Prompts for validity days (default: 730)
- Prompts for organization name (default: OnPremise-CA)

**Automatic Mode** (no prompts):
```bash
./scripts/create-ca.sh --auto
```

The script will:
1. Generate CA certificate (if not exists)
   - 4096-bit RSA private key
   - Self-signed certificate valid for specified days
2. Generate server certificate
   - 2048-bit RSA private key
   - Certificate Signing Request (CSR)
   - Server certificate signed by CA
   - Certificate chain (server + CA)
3. Set proper file permissions
4. Display certificate summary

### 3. Verify Certificates

Verify certificates are valid and properly configured:

```bash
./scripts/utils/verify-certificates.sh
```

This checks:
- Certificate validity
- Certificate chain correctness
- File permissions
- Expiration dates
- CA:TRUE extension for CA certificate

### 4. Start HTTPS Server

**Important: All docker-compose commands must use sudo**

```bash
# Start container in detached mode
sudo docker-compose up -d

# Check container status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f ca-https-test

# Stop container
sudo docker-compose down

# Restart container
sudo docker-compose restart
```

The HTTPS server will:
- Listen on port 5006 (external) → 443 (container)
- Serve test page at `https://[SERVER]:5006/`
- Provide health check at `https://[SERVER]:5006/health`
- Provide certificate info at `https://[SERVER]:5006/cert-info`

### 5. Test HTTPS Connection

**Local testing:**
```bash
# Test without certificate verification
curl -k https://localhost:5006/

# Test with CA certificate
curl --cacert certs/ca/ca.crt https://localhost:5006/

# Test health endpoint
curl -k https://localhost:5006/health
```

**External testing:**
```bash
# From another machine
curl -k https://98.93.187.130:5006/

# With certificate verification (after installing CA cert)
curl --cacert ca.crt https://98.93.187.130:5006/
```

**Browser testing:**
```
https://98.93.187.130:5006/
```

### 6. Automated Client Installation (Recommended)

The easiest way to install the CA certificate on client machines is using the automated installation scripts.

#### 6.0.1. Start Certificate Download Server (on server)

On the CA server, start the certificate download HTTP server:

```bash
# On the server
cd /root/aws.git/container/claudecode/CA
./scripts/serve-cert.sh

# Or specify a custom port
./scripts/serve-cert.sh 8080
```

The server will display:
```
==========================================
  CA Certificate Download Server
==========================================

Download URL:
  http://98.93.187.130:8080/ca.crt

Client Installation Scripts:
  Windows: http://98.93.187.130:8080/install-ca-windows.ps1
  Linux:   http://98.93.187.130:8080/install-ca-linux.sh
  macOS:   http://98.93.187.130:8080/install-ca-macos.sh
```

**Keep this server running** while clients download and install certificates.

#### 6.0.2. Automated Installation - Windows

**On the Windows client machine:**

1. **Download the PowerShell script:**
   - Open browser and visit: `http://98.93.187.130:8080/install-ca-windows.ps1`
   - Or use PowerShell:
   ```powershell
   Invoke-WebRequest -Uri "http://98.93.187.130:8080/install-ca-windows.ps1" -OutFile "install-ca-windows.ps1"
   ```

2. **Run the script with Administrator privileges:**
   - Right-click `install-ca-windows.ps1` → **"Run with PowerShell"**
   - Or from PowerShell (Administrator):
   ```powershell
   powershell -ExecutionPolicy Bypass -File install-ca-windows.ps1
   ```

3. **The script will automatically:**
   - Download the CA certificate (ca.crt)
   - Verify it's the correct certificate
   - Remove any old OnPremise-CA certificates
   - Install to LocalMachine\Root (trusted root)
   - Display installation confirmation

4. **Restart your browser** completely and visit `https://98.93.187.130:5006/`

#### 6.0.3. Automated Installation - Linux

**On the Linux client machine:**

```bash
# Download and run the installation script
curl -O http://98.93.187.130:8080/install-ca-linux.sh
chmod +x install-ca-linux.sh
sudo ./install-ca-linux.sh
```

The script will automatically:
- Download the CA certificate
- Verify the certificate
- Install to the system trust store (Ubuntu/Debian/CentOS/RHEL/Fedora)
- Update the certificate store
- Display installation confirmation

**Supported distributions:**
- Ubuntu / Debian → `/usr/local/share/ca-certificates/`
- CentOS / RHEL / Fedora → `/etc/pki/ca-trust/source/anchors/`

#### 6.0.4. Automated Installation - macOS

**On the macOS client machine:**

```bash
# Download and run the installation script
curl -O http://98.93.187.130:8080/install-ca-macos.sh
chmod +x install-ca-macos.sh
sudo ./install-ca-macos.sh
```

The script will automatically:
- Download the CA certificate
- Verify the certificate
- Install to System keychain with trustRoot
- Display installation confirmation

**Note:** You may need to manually set trust in Keychain Access:
1. Open Keychain Access app
2. Select "System" keychain
3. Find "OnPremise-CA-Root"
4. Double-click → Trust → Set to "Always Trust"

#### 6.0.5. What the Scripts Do

All automated installation scripts perform these steps:

1. **Download** the CA certificate from the server
2. **Verify** the certificate is correct (CN=OnPremise-CA-Root)
3. **Remove** any existing OnPremise-CA certificates
4. **Install** the certificate to the system trust store
5. **Verify** the installation was successful
6. **Display** next steps (restart browser, test URL)

**Advantages of automated installation:**
- ✅ No manual file management
- ✅ Automatic verification (ensures correct certificate)
- ✅ Removes old certificates automatically
- ✅ Works on correct system store (not user store)
- ✅ Provides clear feedback and error messages

---

### 7. Manual Client Installation

If you prefer manual installation or the automated scripts don't work, follow these manual steps:

#### 7.1. Why "Not Secure" Warning Appears

When you access the HTTPS server from a browser, you will see a **"Not Secure" or "Your connection is not private"** warning. This is because the browser doesn't trust our self-signed CA certificate yet.

**Why this happens:**
- Our CA certificate is self-signed (not issued by a trusted Certificate Authority)
- The browser doesn't have our CA certificate in its trust store
- This is expected behavior for self-signed certificates

**Solution:** Install the CA certificate (`ca.crt`) on the client machine.

#### 7.2. Download CA Certificate

First, get the CA certificate file to your client machine:

**Option 1: Use the export bundle**
```bash
# On the server
./scripts/export-certificates.sh

# Copy to client machine
scp certs/export/ca-bundle-*.tar.gz user@client-machine:/tmp/

# On client machine
cd /tmp
tar xzf ca-bundle-*.tar.gz
cd ca-bundle-*/
# Now you have ca.crt file
```

**Option 2: Copy CA certificate directly**
```bash
# On the server
cd /root/aws.git/container/claudecode/CA

# Copy to client machine
scp certs/ca/ca.crt user@client-machine:/tmp/
```

**Option 3: Export certificate from browser**

You can export the CA certificate directly from your browser while viewing the HTTPS site (even if it shows a security warning).

**Important: Export Format**
- **Recommended format**: `.crt` or `.pem` (Base64-encoded X.509)
- **Alternative format**: `.cer` or `.der` (DER-encoded binary)
- **For Linux/Mac**: Use `.crt` or `.pem` format
- **For Windows**: Both `.crt` and `.cer` work, but `.crt` is recommended
- **Avoid**: `.p7b` or `.pfx` formats (these are for certificate chains or include private keys)

**Export from Chrome/Edge/Chromium:**

1. Visit `https://98.93.187.130:5006/` (even if warning appears)
2. Click the **"Not Secure"** or **warning icon** in address bar
3. Click **"Certificate is not valid"** or **"Certificate (Invalid)"**
4. Certificate viewer opens
5. Go to **"Details"** tab
6. Look for the **CA certificate**: "OnPremise-CA-Root" (NOT the server certificate)
   - You may need to select it from the certificate path/chain
7. Click **"Export..."** or **"Copy to File..."** button
8. Choose format:
   - **Windows**: Select "Base64-encoded X.509 (.CER)" or "DER encoded binary X.509 (.CER)"
   - **Linux/Mac**: Select "Base64 (PEM)" format
9. Save as `ca.crt` (recommended filename)
10. Use this file to install (see sections below)

**Export from Firefox:**

1. Visit `https://98.93.187.130:5006/` (even if warning appears)
2. Click the **lock icon** or **warning icon** in address bar
3. Click **"Connection not secure"** → **"More information"**
4. Click **"View Certificate"** button
5. Certificate viewer opens in new tab
6. Scroll down to find the **Issuer** section showing "OnPremise-CA-Root"
7. Look for certificate chain and click on the **root CA certificate** (OnPremise-CA-Root)
8. Click **"Download"** section
9. Choose **"PEM (cert)"** format (this creates a `.crt` file)
10. Save as `ca.crt`

**Alternative Firefox method:**
1. Visit the site (even with warning)
2. Click **"Advanced..."** → **"View Certificate"**
3. In the certificate viewer, find the issuer certificate (OnPremise-CA-Root)
4. Click **"Download"** → **"PEM (cert)"**
5. Save the file

**Export from Safari (Mac):**

1. Visit `https://98.93.187.130:5006/` (even if warning appears)
2. Click the **lock icon** or **warning text** in address bar
3. Click **"Show Certificate"**
4. Look for the certificate chain
5. Select the **root certificate**: "OnPremise-CA-Root"
6. Drag the certificate icon to Desktop or Finder
   - This saves as `.cer` file
7. Rename to `ca.crt` if needed (optional)

**Verify downloaded certificate:**
```bash
# Check certificate details
openssl x509 -in ca.crt -noout -text

# Should show:
# Subject: C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root
# Issuer: C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root
# (Subject and Issuer are the same for self-signed CA)

# If file format is DER (binary), convert to PEM:
openssl x509 -inform der -in ca.cer -out ca.crt
```

**Common mistakes to avoid:**
- ❌ Don't export the server certificate (CN=98.93.187.130) - export the CA certificate (CN=OnPremise-CA-Root)
- ❌ Don't save as `.pfx` or `.p12` format (these require passwords and are for different purposes)
- ❌ Don't export the entire certificate chain - just the root CA certificate
- ✅ Do verify the certificate has "OnPremise-CA-Root" in the subject/issuer

**⚠️ CRITICAL: Server Certificate vs CA Certificate**

**DO NOT install the server certificate on client machines!**

This is the most common mistake:

| Certificate | File | Subject (CN) | Purpose | Install on Client? |
|------------|------|--------------|---------|-------------------|
| ❌ Server Certificate | `server.crt` | CN=98.93.187.130 | Used by HTTPS server | **NO - Don't install!** |
| ✅ CA Certificate | `ca.crt` | CN=OnPremise-CA-Root | Signs server certificates | **YES - Install this!** |

**How to verify you have the correct file:**

```bash
# Check certificate subject
openssl x509 -in your-file.crt -noout -subject

# CORRECT (CA certificate):
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=OnPremise-CA-Root

# WRONG (Server certificate):
subject=C=JP, ST=Tokyo, L=Tokyo, O=OnPremise-CA, OU=IT, CN=98.93.187.130
```

**If you accidentally installed the server certificate:**
1. Remove it from your certificate store
2. Download the correct `ca.crt` file
3. Install `ca.crt` (the file with CN=OnPremise-CA-Root)

#### 7.3. Install CA Certificate - Linux (Ubuntu/Debian)

```bash
# Copy CA certificate to system trust store
sudo cp ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt

# Update certificate store
sudo update-ca-certificates

# Verify installation
ls -l /etc/ssl/certs/ | grep onpremise-ca

# Restart browser (important!)
# Close all browser windows and reopen
```

**For Chrome/Chromium on Linux:**
Chrome uses the system certificate store, so the above steps are sufficient. Just restart Chrome after running `update-ca-certificates`.

**For Firefox on Linux:**
Firefox uses its own certificate store (see Section 6.6 below).

#### 7.4. Install CA Certificate - Linux (CentOS/RHEL/Fedora)

```bash
# Copy CA certificate to trust store
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt

# Update trust store
sudo update-ca-trust extract

# Verify installation
trust list | grep "OnPremise-CA"

# Restart browser
```

#### 7.5. Install CA Certificate - Windows

**Method 1: Command Line (Administrator PowerShell)**
```powershell
# Open PowerShell as Administrator
# Navigate to the directory containing ca.crt

# Install to Trusted Root Certification Authorities
certutil -addstore -f "ROOT" ca.crt

# Verify installation
certutil -store ROOT | findstr "OnPremise-CA"
```

**Method 2: GUI (Easier for most users)**

1. **Download ca.crt** to your Windows machine
2. **Double-click** the `ca.crt` file
3. Click **"Install Certificate..."**
4. Select **"Local Machine"** (requires admin rights) or **"Current User"**
5. Click **"Next"**
6. Select **"Place all certificates in the following store"**
7. Click **"Browse"**
8. Select **"Trusted Root Certification Authorities"**
9. Click **"OK"** → **"Next"** → **"Finish"**
10. Click **"Yes"** on the security warning
11. You should see **"The import was successful"**
12. **Close and restart** all browser windows

**For Edge/Chrome on Windows:**
- These browsers use the Windows certificate store
- After installation, restart the browser
- The warning should disappear

**For Firefox on Windows:**
- Firefox uses its own certificate store (see Section 6.6 below)

#### 7.6. Install CA Certificate - macOS

**Method 1: Command Line**
```bash
# Copy ca.crt to your Mac
# Open Terminal

# Install to System keychain (requires password)
sudo security add-trusted-cert \
    -d -r trustRoot \
    -k /Library/Keychains/System.keychain \
    ca.crt

# Verify installation
security find-certificate -a -c "OnPremise-CA-Root" /Library/Keychains/System.keychain
```

**Method 2: Keychain Access GUI**

1. **Download ca.crt** to your Mac
2. **Double-click** `ca.crt` (opens Keychain Access)
3. It will be added to "login" keychain by default
4. **Find the certificate** "OnPremise-CA-Root" in the list
5. **Double-click** the certificate
6. Expand **"Trust"** section
7. Set **"When using this certificate"** to **"Always Trust"**
8. Close the window (you'll be asked for your password)
9. **Restart browser**

**For Safari:**
- Uses the system keychain
- Should work after installation and browser restart

**For Chrome on Mac:**
- Uses the system keychain
- Should work after installation and browser restart

**For Firefox on Mac:**
- Uses its own certificate store (see Section 6.6 below)

#### 7.7. Install CA Certificate - Firefox (All Platforms)

Firefox uses its own certificate store, separate from the operating system.

**Steps for Firefox:**

1. **Open Firefox**
2. Go to **Settings** (or type `about:preferences` in address bar)
3. Search for **"certificates"** in the search box
4. Click **"View Certificates..."** button
5. Go to **"Authorities"** tab
6. Click **"Import..."** button
7. Select the **`ca.crt`** file you downloaded
8. Check the box: **"Trust this CA to identify websites"**
9. Click **"OK"**
10. You should see "OnPremise-CA-Root" in the list under "OnPremise-CA"
11. Close the settings
12. **Refresh the page** (F5) or revisit `https://98.93.187.130:5006/`

The warning should now be gone, and you'll see a lock icon 🔒.

#### 7.8. Verify Installation

After installing the CA certificate, verify it works:

**In Browser:**
1. Visit `https://98.93.187.130:5006/`
2. You should see a **lock icon** 🔒 in the address bar (not a warning triangle)
3. Click the lock icon
4. Click **"Connection is secure"** or **"Certificate"**
5. Verify:
   - Issued to: `98.93.187.130`
   - Issued by: `OnPremise-CA-Root`
   - Valid from: (certificate start date)
   - Valid until: (certificate expiration date)

**Command Line Test:**
```bash
# Linux/Mac
curl https://98.93.187.130:5006/

# Should work without -k flag if CA cert is installed system-wide
# If it fails with certificate error, CA cert not properly installed

# Windows PowerShell
Invoke-WebRequest -Uri https://98.93.187.130:5006/

# Should work without certificate errors
```

#### 7.9. Troubleshooting Client Installation

**Problem: Still seeing "Not Secure" after installation**

Solutions:
1. **Restart browser completely** (close all windows, not just tabs)
2. **Clear browser cache**: Settings → Privacy → Clear browsing data
3. **Check certificate is in correct store**:
   - Windows: Must be in "Trusted Root Certification Authorities", not "Personal"
   - Linux: Run `update-ca-certificates` with sudo
   - Mac: Certificate must be set to "Always Trust"
4. **For Firefox**: Install via Firefox's own certificate manager (not OS)
5. **Hard refresh page**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

**Problem: "This CA Root certificate is not trusted"**

Solutions:
1. Make sure you installed `ca.crt` (not `server.crt`)
2. Install to "Trusted Root" store (not Intermediate or Personal)
3. On Windows, run certutil as Administrator
4. On Linux, make sure filename ends with `.crt` in ca-certificates directory

**Problem: Chrome says "NET::ERR_CERT_AUTHORITY_INVALID"**

Solutions:
1. CA certificate not in system trust store
2. On Linux: Run `sudo update-ca-certificates` and restart Chrome
3. On Windows: Install via certutil or GUI, restart Chrome
4. Try opening in Incognito/Private mode to test

**Problem: Firefox still shows warning, but Chrome works**

Solutions:
- Firefox uses separate certificate store
- Must import CA cert through Firefox Settings → Certificates
- System installation doesn't affect Firefox

### 8. Export Certificates

Export certificates for use on other servers:

```bash
./scripts/export-certificates.sh
```

This creates a tarball in `certs/export/` containing:
- `ca.crt` - CA certificate for client trust
- `server.crt` - Server certificate
- `server.key` - Server private key (keep secure!)
- `server-chain.crt` - Full certificate chain
- `README.txt` - Installation instructions
- `verify.sh` - Verification script
- `CERTIFICATE_INFO.txt` - Certificate details

**Transfer to another server:**
```bash
scp certs/export/ca-bundle-*.tar.gz user@other-server:/tmp/
```

## 9. Configuration

### Environment Variables (.env)

```bash
# Server Configuration
SERVER_NAME=98.93.187.130          # Server hostname or IP
HTTPS_PORT=5006                    # External HTTPS port
CERT_VALIDITY_DAYS=730             # Certificate validity (2 years)

# Certificate Subject Information
CERT_COUNTRY=JP                    # Country code
CERT_STATE=Tokyo                   # State/Province
CERT_LOCALITY=Tokyo                # City
CERT_ORGANIZATION=OnPremise-CA     # Organization name
CERT_ORG_UNIT=IT                   # Organizational unit

# External Access
EC2_PUBLIC_IP=98.93.187.130        # Public IP address
```

### OpenSSL Configuration

#### CA Certificate (config/openssl-ca.cnf)
- 4096-bit RSA key
- Self-signed
- CA:TRUE extension
- keyCertSign and cRLSign key usage

#### Server Certificate (config/openssl-server.cnf)
- 2048-bit RSA key
- Signed by CA
- serverAuth and clientAuth extended key usage
- SubjectAltName with DNS and IP

### Nginx Configuration

#### SSL/TLS Settings
- TLS 1.2 and TLS 1.3 only
- Strong cipher suites
- HTTP/2 enabled
- Security headers (HSTS, X-Frame-Options, etc.)

#### Endpoints
- `/` - Test page with instructions
- `/health` - Health check (returns "healthy")
- `/cert-info` - Certificate information

## 10. Using Certificates on Other Servers

### Azure DevOps Server (On-Premise)

Azure DevOps Server requires both the CA certificate (for client trust) and the server certificate with private key (for HTTPS operation).

#### Prerequisites

- Azure DevOps Server installed on Windows Server
- IIS installed and running
- OpenSSL available (Git for Windows includes OpenSSL)
- Administrator privileges

#### Method 1: Automated Installation (PowerShell Script)

**Step 1: Export certificates from CA server**

```bash
# On the CA server
cd /root/aws.git/container/claudecode/CA
./scripts/export-certificates.sh

# Transfer to Azure DevOps Server
# The bundle includes: ca.crt, server.crt, server.key, server-chain.crt
```

**Step 2: Transfer certificate bundle to Azure DevOps Server**

```bash
# From CA server to DevOps server
scp certs/export/ca-bundle-*.tar.gz administrator@devops-server:C:\Temp\
```

**Step 3: Extract and run installation script**

On Azure DevOps Server (PowerShell as Administrator):

```powershell
# Extract certificate bundle
cd C:\Temp
tar -xzf ca-bundle-*.tar.gz

# Download installation script from CA server
Invoke-WebRequest -Uri "http://98.93.187.130:8080/install-cert-devops-server.ps1" -OutFile "install-cert-devops-server.ps1"

# Or copy from the extracted bundle if available
# Copy scripts\install-cert-devops-server.ps1 to current directory

# Run installation script
powershell -ExecutionPolicy Bypass -File install-cert-devops-server.ps1 -CertificateBundle "C:\Temp\ca-bundle-20260120-013115"
```

**What the script does:**
1. ✅ Installs CA certificate to Trusted Root Certification Authorities
2. ✅ Creates PFX file from certificate and private key
3. ✅ Imports server certificate to Personal certificate store
4. ✅ Configures IIS HTTPS binding (port 443)
5. ✅ Displays Azure DevOps Server configuration steps

**Step 4: Configure Azure DevOps Server**

After the script completes:

1. **Open Azure DevOps Server Administration Console**

2. **Navigate to Application Tier** → **Change URLs**

3. **Update Public URL** to use HTTPS:
   ```
   https://your-devops-server.domain.com/
   ```

4. **Click OK** and apply changes

5. **Restart Azure DevOps Server services:**
   - Open Services (`services.msc`)
   - Restart "Azure DevOps Server" and related services
   - Or use PowerShell:
   ```powershell
   Restart-Service "Azure DevOps Server"
   Restart-Service "VSS*"
   ```

6. **Test HTTPS access:**
   ```
   https://your-devops-server.domain.com/
   ```

#### Method 2: Manual Installation

If you prefer manual installation:

**Step 1: Install CA Certificate**

```powershell
# Import CA certificate to Trusted Root
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("C:\Temp\ca-bundle-xxx\ca.crt")

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()

Write-Host "CA certificate installed"
```

**Step 2: Create PFX from certificate and key**

```powershell
# Using OpenSSL (from Git for Windows)
cd "C:\Temp\ca-bundle-xxx"

# Create PFX
& "C:\Program Files\Git\usr\bin\openssl.exe" pkcs12 -export `
  -out server.pfx `
  -inkey server.key `
  -in server.crt `
  -certfile ca.crt `
  -password pass:YourPassword

# Or use GUI: Import wizard requires PFX format
```

**Step 3: Import Server Certificate**

```powershell
# Import PFX to Personal store
$pfxPassword = ConvertTo-SecureString -String "YourPassword" -AsPlainText -Force

$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    "C:\Temp\ca-bundle-xxx\server.pfx",
    $pfxPassword,
    [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet
)

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My","LocalMachine")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()

Write-Host "Server certificate installed"
Write-Host "Thumbprint: $($cert.Thumbprint)"
```

**Step 4: Configure IIS HTTPS Binding**

Method A: Using IIS Manager (GUI)

1. Open **IIS Manager** (`inetmgr`)
2. Select your **Azure DevOps Server site** (or "Default Web Site")
3. Click **"Bindings..."** in the Actions pane
4. Click **"Add..."** or **"Edit..."** for HTTPS
5. **Type:** https
6. **Port:** 443
7. **SSL certificate:** Select your server certificate (shows Subject/CN)
8. Click **OK**

Method B: Using PowerShell

```powershell
Import-Module WebAdministration

# Remove existing HTTPS binding if present
Remove-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443 -ErrorAction SilentlyContinue

# Add new HTTPS binding
New-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443 -SslFlags 0

# Get certificate thumbprint
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*your-server-name*" }

# Bind certificate
$binding = Get-WebBinding -Name "Default Web Site" -Protocol "https" -Port 443
$binding.AddSslCertificate($cert.Thumbprint, "My")

Write-Host "HTTPS binding configured"
```

**Step 5: Test IIS Configuration**

```powershell
# Test HTTPS binding
netstat -an | findstr ":443"

# Should show:
# TCP    0.0.0.0:443            0.0.0.0:0              LISTENING

# Test with browser or curl
curl https://localhost/ -k
```

**Step 6: Update Azure DevOps Server Configuration**

Follow Step 4 from Method 1 (Azure DevOps Server Administration Console configuration).

#### Troubleshooting Azure DevOps Server HTTPS

**Problem: Certificate not showing in IIS**

Solution:
```powershell
# Verify certificate is in Personal store
Get-ChildItem -Path Cert:\LocalMachine\My | Format-List Subject, Issuer, Thumbprint

# Verify certificate has private key
Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.HasPrivateKey } | Format-List Subject
```

**Problem: IIS shows "The specified network password is not correct"**

Solution: Certificate was imported to user store instead of machine store
```powershell
# Reimport with MachineKeySet flag
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    "server.pfx",
    $password,
    [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet
)
```

**Problem: Azure DevOps Server still uses HTTP**

Solution:
1. Check Application Tier URL in Administration Console
2. Verify IIS binding is active: `Get-WebBinding -Name "Default Web Site"`
3. Restart Azure DevOps services
4. Clear browser cache

**Problem: Clients still see certificate warning**

Solution: Clients need to install the CA certificate (ca.crt) - see Section 6 for client installation.

#### Security Best Practices for Azure DevOps Server

1. **Use strong PFX password** - Store securely, don't commit to source control
2. **Restrict certificate private key access** - Only service accounts need access
3. **Enable HTTPS-only** - Redirect HTTP to HTTPS in IIS
4. **Update firewall rules** - Allow port 443, block port 80 if not needed
5. **Monitor certificate expiration** - Set reminders before certificates expire (730 days)
6. **Backup certificates** - Store PFX and password in secure location

#### Firewall Configuration

```powershell
# Allow HTTPS (port 443)
New-NetFirewallRule -DisplayName "Azure DevOps HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Optional: Block HTTP (port 80) after HTTPS is working
New-NetFirewallRule -DisplayName "Block Azure DevOps HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Block
```

---

### Linux (Ubuntu/Debian)

```bash
# Extract certificate bundle
tar xzf ca-bundle-*.tar.gz
cd ca-bundle-*/

# Install CA certificate
sudo cp ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt
sudo update-ca-certificates

# Test connection
curl https://98.93.187.130:5006/
```

### Linux (CentOS/RHEL)

```bash
# Install CA certificate
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt
sudo update-ca-trust
```

### Windows

**Command Line (Administrator):**
```cmd
certutil -addstore -f "ROOT" ca.crt
```

**GUI:**
1. Double-click `ca.crt`
2. Click "Install Certificate"
3. Select "Local Machine"
4. Select "Trusted Root Certification Authorities"
5. Click "Finish"

### macOS

```bash
sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain ca.crt
```

### Web Servers

#### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-server.com;

    ssl_certificate /etc/nginx/certs/server-chain.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    # ... other configuration
}
```

#### Apache

```apache
<VirtualHost *:443>
    ServerName your-server.com

    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/server.crt
    SSLCertificateKeyFile /etc/ssl/private/server.key
    SSLCertificateChainFile /etc/ssl/certs/ca.crt

    # ... other configuration
</VirtualHost>
```

## 11. Security Considerations

### Private Key Protection

**Private keys must be protected:**
- Never commit to version control (gitignored)
- Set permissions to 600 (owner read/write only)
- Store backups in encrypted storage
- Rotate regularly

```bash
# Proper permissions
chmod 600 certs/ca/ca.key
chmod 600 certs/server/server.key
```

### Certificate Validity

- Default validity: 730 days (2 years)
- Monitor expiration dates
- Renew before expiration
- Test renewed certificates before deployment

```bash
# Check expiration
openssl x509 -in certs/server/server.crt -noout -dates
```

### Access Control

- HTTPS server accessible from external IP (no IP restrictions)
- For production: implement IP whitelisting in firewall
- Use strong TLS configuration (TLS 1.2+)
- Keep OpenSSL and Docker updated

## Troubleshooting

### Certificate Generation Issues

**Error: OpenSSL not found**
```bash
# Install OpenSSL
sudo yum install openssl          # CentOS/RHEL
sudo apt-get install openssl      # Ubuntu/Debian
```

**Error: .env file not found**
```bash
# Run setup script
./scripts/setup-ca-environment.sh
```

**Error: Permission denied**
```bash
# Set execute permissions
chmod +x scripts/*.sh scripts/utils/*.sh
```

### Docker Issues

**Error: Permission denied (docker socket)**
```bash
# Use sudo
sudo docker-compose up -d
```

**Error: Port 5006 already in use**
```bash
# Check what's using the port
sudo netstat -tlnp | grep 5006

# Change port in .env and docker-compose.yml
# Or stop the conflicting service
```

**Error: Container fails health check**
```bash
# Check logs
sudo docker-compose logs ca-https-test

# Check if certificates are mounted correctly
sudo docker-compose exec ca-https-test ls -la /etc/nginx/certs/

# Restart container
sudo docker-compose restart
```

### Connection Issues

**Error: Connection refused**
```bash
# Check if container is running
sudo docker-compose ps

# Check firewall
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=5006/tcp --permanent
sudo firewall-cmd --reload
```

**Error: Certificate verify failed**
```bash
# Install CA certificate on client machine
# Or use -k flag to skip verification (testing only)
curl -k https://98.93.187.130:5006/
```

**Browser shows security warning**
- Import CA certificate into browser (see "Using Certificates" section)
- For Firefox: use built-in certificate manager
- For Chrome/Edge: install CA certificate in OS trust store

### Certificate Issues

**Error: Certificate has expired**
```bash
# Regenerate certificates
rm -rf certs/ca/* certs/server/*
./scripts/create-ca.sh
sudo docker-compose restart
```

**Error: Certificate chain verification failed**
```bash
# Verify certificate chain
./scripts/utils/verify-certificates.sh

# Check if CA certificate signed server certificate
openssl verify -CAfile certs/ca/ca.crt certs/server/server.crt
```

## Architecture

### Certificate Hierarchy

```
OnPremise-CA-Root (CA Certificate)
  └── Self-signed, 4096-bit RSA
      └── Valid for 730 days
          └── Signs server certificates
              │
              └── Server Certificate (server.crt)
                  └── 2048-bit RSA
                  └── Valid for 730 days
                  └── SubjectAltName: DNS + IP
```

### Certificate Chain

```
Client ←→ HTTPS Server
          │
          └── Presents: server-chain.crt
              │
              ├── Server Certificate (server.crt)
              │   └── Signed by CA
              │
              └── CA Certificate (ca.crt)
                  └── Self-signed
```

### Docker Architecture

```
Host:5006 ←→ Docker Bridge ←→ Container:443
              (ca-network)
                  │
                  └── Nginx HTTPS Server
                      ├── Mounts: server.crt
                      ├── Mounts: server.key
                      ├── Mounts: server-chain.crt
                      ├── Mounts: nginx.conf
                      └── Mounts: index.html
```

## Maintenance

### Regular Tasks

**Check Certificate Expiration** (monthly)
```bash
# Check expiration dates
openssl x509 -in certs/ca/ca.crt -noout -enddate
openssl x509 -in certs/server/server.crt -noout -enddate

# Get days until expiration
openssl x509 -in certs/server/server.crt -noout -checkend 2592000
```

**Verify Certificates** (monthly)
```bash
./scripts/utils/verify-certificates.sh
```

**Check Container Health** (weekly)
```bash
sudo docker-compose ps
sudo docker-compose logs --tail=100 ca-https-test
```

**Review Logs** (weekly)
```bash
cat logs/certificate-generation.log
sudo docker-compose logs ca-https-test
```

### Certificate Renewal

When certificates are close to expiration:

```bash
# 1. Backup existing certificates
tar czf certs-backup-$(date +%Y%m%d).tar.gz certs/

# 2. Generate new certificates
./scripts/create-ca.sh

# 3. Restart HTTPS server
sudo docker-compose restart

# 4. Verify new certificates
./scripts/utils/verify-certificates.sh
curl -k https://98.93.187.130:5006/

# 5. Export for other servers
./scripts/export-certificates.sh
```

## Performance

### Resource Usage

- **CPU**: Minimal (Nginx is lightweight)
- **Memory**: ~10-20MB (Alpine-based container)
- **Disk**: ~50MB (container image + certificates)
- **Network**: Negligible (test server only)

### Scaling

For production use:
- Use load balancer with multiple HTTPS servers
- Implement certificate distribution automation
- Set up monitoring and alerting for certificate expiration
- Consider using Let's Encrypt for public-facing services

## Integration with CICD Project

This CA infrastructure is part of the larger CICD project:

- **Independent**: Separate docker network (ca-network)
- **Port Allocation**: Port 5006 (no conflict with CICD services)
- **Environment Variables**: Can inherit EC2_PUBLIC_IP from parent .env
- **Documentation Pattern**: Follows same structure as CICD project

## FAQ

**Q: Can I use these certificates for production?**
A: These are self-signed certificates suitable for on-premise closed environments. For public-facing services, use certificates from a trusted CA (e.g., Let's Encrypt).

**Q: How do I change the server name after certificate generation?**
A: Regenerate certificates with new server name:
```bash
rm -rf certs/server/*
./scripts/create-ca.sh
sudo docker-compose restart
```

**Q: Can I use the same CA to sign multiple server certificates?**
A: Yes! The CA certificate and key can be reused. Just run create-ca.sh with different server names. The script will skip CA generation if it already exists.

**Q: Why do I need sudo for docker-compose?**
A: This is a requirement specified in issue #119. Docker requires elevated privileges to access the Docker socket and manage containers.

**Q: Can I change the port from 5006?**
A: Yes. Update `HTTPS_PORT` in `.env` and the port mapping in `docker-compose.yml`.

**Q: How do I remove browser security warnings?**
A: Import the CA certificate (ca.crt) into your browser or system trust store. See "Using Certificates on Other Servers" section.

## License

This project is part of the CICD infrastructure for on-premise environments.

## Support

For issues or questions:
- Check this README thoroughly
- Review logs: `logs/certificate-generation.log`
- Check container logs: `sudo docker-compose logs ca-https-test`
- See QUICKSTART.md for common tasks
- Issue tracker: GitHub issues

## Version

Current version: 1.0.0

## Related Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [../CICD/README.md](../CICD/README.md) - Parent CICD project documentation
- [../CICD/CLAUDE.md](../CICD/CLAUDE.md) - Claude Code project guide
