#!/bin/bash
################################################################################
# Certificate Export Script
#
# Purpose: Package CA and server certificates for use on other servers
# Creates a tarball with:
#   - CA certificate (for client trust)
#   - Server certificate and key
#   - Certificate chain
#   - Installation instructions
#   - Verification script
################################################################################

set -e

# Color logging functions
log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$CA_ROOT"

echo "========================================"
echo "  Certificate Export"
echo "========================================"
echo ""

# Check if certificates exist
if [[ ! -f "certs/ca/ca.crt" ]] || [[ ! -f "certs/server/server.crt" ]]; then
    log_error "Certificates not found. Please run ./scripts/create-ca.sh first."
    exit 1
fi

# Create export directory
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
EXPORT_NAME="ca-bundle-${TIMESTAMP}"
EXPORT_DIR="certs/export/${EXPORT_NAME}"
EXPORT_ARCHIVE="certs/export/${EXPORT_NAME}.tar.gz"

log_info "Creating export directory: $EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

# Copy certificates
log_info "Copying certificates..."
cp certs/ca/ca.crt "$EXPORT_DIR/"
cp certs/server/server.crt "$EXPORT_DIR/"
cp certs/server/server.key "$EXPORT_DIR/"
cp certs/server/server-chain.crt "$EXPORT_DIR/"
log_success "Certificates copied"

# Create installation README
log_info "Creating installation instructions..."
cat > "$EXPORT_DIR/README.txt" << 'EOFREADME'
================================================================================
CA Certificate Bundle - Installation Instructions
================================================================================

This package contains:
  - ca.crt              : CA certificate (for client trust)
  - server.crt          : Server certificate
  - server.key          : Server private key (KEEP SECURE!)
  - server-chain.crt    : Full certificate chain (server + CA)
  - verify.sh           : Verification script

================================================================================
IMPORTANT: CERTIFICATE FILE FORMAT
================================================================================

The ca.crt file in this package is in PEM format (Base64-encoded X.509).

Supported formats for CA certificate installation:
  - .crt or .pem  : PEM format (Base64-encoded) - RECOMMENDED
  - .cer or .der  : DER format (Binary-encoded) - Also works

If you need to convert between formats:
  # Convert DER to PEM
  openssl x509 -inform der -in ca.cer -out ca.crt

  # Convert PEM to DER
  openssl x509 -outform der -in ca.crt -out ca.cer

Verify certificate format:
  # View certificate details
  openssl x509 -in ca.crt -noout -text

  # Check subject and issuer (should both be OnPremise-CA-Root for self-signed CA)
  openssl x509 -in ca.crt -noout -subject -issuer

IMPORTANT: Make sure you are using the CA certificate (ca.crt), not the
           server certificate (server.crt). The CA certificate is what
           needs to be installed on client machines to trust the server.

================================================================================
GETTING CA CERTIFICATE FROM BROWSER (Alternative Method)
================================================================================

If you don't have the certificate files, you can export the CA certificate
directly from your browser while visiting the HTTPS site:

Chrome/Edge/Chromium:
  1. Visit the HTTPS site (even if warning appears)
  2. Click "Not Secure" or warning icon in address bar
  3. Click "Certificate is not valid" or "Certificate (Invalid)"
  4. Go to "Details" tab
  5. Find and select "OnPremise-CA-Root" (the CA certificate)
  6. Click "Export..." button
  7. Save format:
     - Windows: Choose "Base64-encoded X.509 (.CER)"
     - Linux/Mac: Choose "Base64 (PEM)"
  8. Save as ca.crt

Firefox:
  1. Visit the HTTPS site (even if warning appears)
  2. Click warning icon → "More information"
  3. Click "View Certificate" button
  4. Find the issuer certificate "OnPremise-CA-Root"
  5. Click "Download" → Choose "PEM (cert)" format
  6. Save as ca.crt

Safari (Mac):
  1. Visit the HTTPS site (even if warning appears)
  2. Click lock icon or warning text
  3. Click "Show Certificate"
  4. Select root certificate "OnPremise-CA-Root"
  5. Drag certificate icon to Desktop/Finder
  6. Rename to ca.crt if needed

⚠️  Common mistakes:
  ✗ Don't export server certificate (CN=SERVER_IP) - export CA (CN=OnPremise-CA-Root)
  ✗ Don't save as .pfx or .p12 format
  ✓ Do verify Subject/Issuer shows "OnPremise-CA-Root"

================================================================================
INSTALLATION INSTRUCTIONS
================================================================================

----------------------------------------
1. Linux / Ubuntu
----------------------------------------

# Install CA certificate to system trust store
sudo cp ca.crt /usr/local/share/ca-certificates/onpremise-ca.crt
sudo update-ca-certificates

# Verify installation
ls -l /etc/ssl/certs/ | grep onpremise-ca

# Test HTTPS connection (replace SERVER_IP and PORT)
curl https://SERVER_IP:PORT/

----------------------------------------
2. CentOS / RHEL
----------------------------------------

# Install CA certificate
sudo cp ca.crt /etc/pki/ca-trust/source/anchors/onpremise-ca.crt
sudo update-ca-trust

# Test HTTPS connection
curl https://SERVER_IP:PORT/

----------------------------------------
3. Windows
----------------------------------------

Method 1: Command Line (Run as Administrator)
  certutil -addstore -f "ROOT" ca.crt

Method 2: GUI
  1. Double-click ca.crt file
  2. Click "Install Certificate"
  3. Select "Local Machine"
  4. Select "Place all certificates in the following store"
  5. Browse and select "Trusted Root Certification Authorities"
  6. Click "Finish"

# Test with PowerShell
Invoke-WebRequest -Uri https://SERVER_IP:PORT/

----------------------------------------
4. macOS
----------------------------------------

# Install CA certificate
sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain ca.crt

# Test HTTPS connection
curl https://SERVER_IP:PORT/

----------------------------------------
5. Browser (Firefox)
----------------------------------------

Firefox uses its own certificate store:

1. Open Firefox Settings
2. Go to "Privacy & Security"
3. Scroll down to "Certificates"
4. Click "View Certificates"
5. Go to "Authorities" tab
6. Click "Import"
7. Select ca.crt file
8. Check "Trust this CA to identify websites"
9. Click "OK"

----------------------------------------
6. Using Certificates on Another Server
----------------------------------------

For Nginx:
----------
# Copy certificates to nginx directory
sudo cp server.crt /etc/nginx/certs/
sudo cp server.key /etc/nginx/certs/
sudo cp server-chain.crt /etc/nginx/certs/

# Set proper permissions
sudo chmod 644 /etc/nginx/certs/server.crt
sudo chmod 600 /etc/nginx/certs/server.key
sudo chmod 644 /etc/nginx/certs/server-chain.crt

# Update nginx configuration
# In /etc/nginx/nginx.conf or your site config:
#   ssl_certificate /etc/nginx/certs/server-chain.crt;
#   ssl_certificate_key /etc/nginx/certs/server.key;

# Restart nginx
sudo systemctl restart nginx

For Apache:
-----------
# Copy certificates
sudo cp server.crt /etc/ssl/certs/
sudo cp server.key /etc/ssl/private/
sudo cp ca.crt /etc/ssl/certs/

# Set proper permissions
sudo chmod 644 /etc/ssl/certs/server.crt
sudo chmod 600 /etc/ssl/private/server.key
sudo chmod 644 /etc/ssl/certs/ca.crt

# Update apache configuration
# In your VirtualHost:
#   SSLCertificateFile /etc/ssl/certs/server.crt
#   SSLCertificateKeyFile /etc/ssl/private/server.key
#   SSLCertificateChainFile /etc/ssl/certs/ca.crt

# Restart apache
sudo systemctl restart apache2  # Ubuntu/Debian
sudo systemctl restart httpd    # CentOS/RHEL

================================================================================
VERIFICATION
================================================================================

1. Verify certificate chain:
   openssl verify -CAfile ca.crt server.crt

2. Test HTTPS connection (skip verification):
   curl -k https://SERVER_IP:PORT/

3. Test HTTPS connection (with CA certificate):
   curl --cacert ca.crt https://SERVER_IP:PORT/

4. View certificate details:
   openssl x509 -in server.crt -noout -text

5. Check certificate expiration:
   openssl x509 -in server.crt -noout -dates

6. Test with openssl s_client:
   openssl s_client -connect SERVER_IP:PORT -showcerts

================================================================================
SECURITY NOTES
================================================================================

1. server.key is a PRIVATE KEY - Keep it secure!
   - Never commit to version control
   - Set permissions to 600 (owner read/write only)
   - Store in secure location

2. CA certificate (ca.crt) should be distributed to all clients
   that need to trust your servers

3. Certificate validity: 730 days (2 years)
   - Check expiration dates regularly
   - Renew before expiration

4. Backup certificates securely
   - Store in encrypted backup
   - Keep CA private key separate and secure

================================================================================
TROUBLESHOOTING
================================================================================

Q: curl shows "certificate verify failed"
A: Make sure CA certificate is installed in system trust store

Q: Browser shows security warning
A: Import ca.crt into browser (see Browser section above)

Q: nginx fails to start
A: Check certificate file permissions and paths in nginx config

Q: Certificate expired
A: Regenerate certificates using create-ca.sh script

================================================================================

For more information, see:
  - Main README.md
  - QUICKSTART.md

Generated: $(date)
CA Infrastructure - OnPremise Certificate Authority
================================================================================
EOFREADME

log_success "Installation instructions created"

# Create verification script
log_info "Creating verification script..."
cat > "$EXPORT_DIR/verify.sh" << 'EOFVERIFY'
#!/bin/bash
# Certificate Verification Script

echo "================================"
echo "Certificate Verification"
echo "================================"
echo ""

# Check files exist
echo "Checking files..."
for file in ca.crt server.crt server.key server-chain.crt; do
    if [[ -f "$file" ]]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        exit 1
    fi
done
echo ""

# Verify certificate chain
echo "Verifying certificate chain..."
if openssl verify -CAfile ca.crt server.crt > /dev/null 2>&1; then
    echo "  ✓ Certificate chain is valid"
else
    echo "  ✗ Certificate verification failed"
    exit 1
fi
echo ""

# Display certificate information
echo "CA Certificate Information:"
echo "  Subject: $(openssl x509 -in ca.crt -noout -subject | sed 's/subject=//')"
echo "  Issuer:  $(openssl x509 -in ca.crt -noout -issuer | sed 's/issuer=//')"
echo "  Expires: $(openssl x509 -in ca.crt -noout -enddate | sed 's/notAfter=//')"
echo ""

echo "Server Certificate Information:"
echo "  Subject: $(openssl x509 -in server.crt -noout -subject | sed 's/subject=//')"
echo "  Issuer:  $(openssl x509 -in server.crt -noout -issuer | sed 's/issuer=//')"
echo "  Expires: $(openssl x509 -in server.crt -noout -enddate | sed 's/notAfter=//')"
echo ""

# Check if certificates are expired
if openssl x509 -in ca.crt -noout -checkend 0 > /dev/null 2>&1; then
    echo "  ✓ CA certificate is valid (not expired)"
else
    echo "  ✗ CA certificate has expired!"
fi

if openssl x509 -in server.crt -noout -checkend 0 > /dev/null 2>&1; then
    echo "  ✓ Server certificate is valid (not expired)"
else
    echo "  ✗ Server certificate has expired!"
fi

echo ""
echo "Verification complete!"
EOFVERIFY

chmod +x "$EXPORT_DIR/verify.sh"
log_success "Verification script created"

# Create certificate information file
log_info "Generating certificate information..."
cat > "$EXPORT_DIR/CERTIFICATE_INFO.txt" << EOF
Certificate Bundle Information
===============================

Generated: $(date)
Export Name: ${EXPORT_NAME}

CA Certificate:
---------------
$(openssl x509 -in certs/ca/ca.crt -noout -subject -issuer -dates)

Server Certificate:
-------------------
$(openssl x509 -in certs/server/server.crt -noout -subject -issuer -dates)

Certificate Files:
------------------
- ca.crt              : CA certificate (public)
- server.crt          : Server certificate (public)
- server.key          : Server private key (PRIVATE - keep secure!)
- server-chain.crt    : Full certificate chain (public)

Key Sizes:
----------
CA:     $(openssl rsa -in certs/ca/ca.key -noout -text 2>/dev/null | grep "Private-Key:" | sed 's/.*(\(.*\)).*/\1/')
Server: $(openssl rsa -in certs/server/server.key -noout -text 2>/dev/null | grep "Private-Key:" | sed 's/.*(\(.*\)).*/\1/')

Purpose:
--------
Self-signed CA infrastructure for on-premise closed environment.
Certificates can be used on multiple servers for HTTPS/TLS encryption.

Installation:
-------------
See README.txt for detailed installation instructions for:
- Linux (Ubuntu, CentOS, RHEL)
- Windows
- macOS
- Web browsers (Firefox, Chrome, Edge)
- Web servers (Nginx, Apache)

===============================
EOF

log_success "Certificate information generated"

# Create archive
log_info "Creating archive: $EXPORT_ARCHIVE"
tar czf "$EXPORT_ARCHIVE" -C "certs/export" "$EXPORT_NAME"

# Clean up temporary directory
rm -rf "$EXPORT_DIR"

# Display summary
FILE_SIZE=$(du -h "$EXPORT_ARCHIVE" | cut -f1)

echo ""
echo "========================================"
echo "  Export Complete"
echo "========================================"
echo ""
log_success "Certificate bundle exported successfully!"
echo ""
log_info "Export Details:"
log_info "  Archive:  $EXPORT_ARCHIVE"
log_info "  Size:     $FILE_SIZE"
echo ""
log_info "Package Contents:"
log_info "  - CA certificate (ca.crt)"
log_info "  - Server certificate (server.crt)"
log_info "  - Server private key (server.key)"
log_info "  - Certificate chain (server-chain.crt)"
log_info "  - Installation instructions (README.txt)"
log_info "  - Verification script (verify.sh)"
log_info "  - Certificate information (CERTIFICATE_INFO.txt)"
echo ""
echo "To extract on another server:"
echo "  tar xzf ${EXPORT_NAME}.tar.gz"
echo "  cd ${EXPORT_NAME}"
echo "  cat README.txt"
echo "  ./verify.sh"
echo ""
log_warning "IMPORTANT: server.key is a private key. Keep it secure!"
echo ""
