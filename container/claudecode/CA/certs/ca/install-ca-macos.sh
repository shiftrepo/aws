#!/bin/bash
################################################################################
# CA Certificate Installation Script for macOS
#
# Purpose: Download and install CA certificate on macOS
# Usage:
#   curl -O http://SERVER_IP:8080/install-ca-macos.sh
#   chmod +x install-ca-macos.sh
#   sudo ./install-ca-macos.sh
#
################################################################################

set -e

# Configuration
SERVER_IP="98.93.187.130"
DOWNLOAD_PORT="8080"
CA_CERT_URL="http://${SERVER_IP}:${DOWNLOAD_PORT}/ca.crt"
TEMP_CERT="/tmp/onpremise-ca.crt"

# Color logging functions
log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

echo "=========================================="
echo "  CA Certificate Installation (macOS)"
echo "=========================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   log_info "Please run: sudo $0"
   exit 1
fi

log_success "Running with root privileges"
echo ""

# Step 1: Download CA certificate
log_info "Step 1/4: Downloading CA certificate..."
log_info "  URL: $CA_CERT_URL"

if curl -f -o "$TEMP_CERT" "$CA_CERT_URL"; then
    log_success "  Downloaded to: $TEMP_CERT"
else
    log_error "  Failed to download certificate"
    log_info "Please check server is running: http://${SERVER_IP}:${DOWNLOAD_PORT}/"
    exit 1
fi

echo ""

# Step 2: Verify certificate
log_info "Step 2/4: Verifying certificate..."

if ! openssl x509 -in "$TEMP_CERT" -noout -text > /dev/null 2>&1; then
    log_error "  Invalid certificate file"
    exit 1
fi

SUBJECT=$(openssl x509 -in "$TEMP_CERT" -noout -subject)
ISSUER=$(openssl x509 -in "$TEMP_CERT" -noout -issuer)
EXPIRES=$(openssl x509 -in "$TEMP_CERT" -noout -enddate)

log_info "  $SUBJECT"
log_info "  $ISSUER"
log_info "  $EXPIRES"

if echo "$SUBJECT" | grep -q "OnPremise-CA-Root"; then
    log_success "  Verified: This is the correct CA certificate"
else
    log_error "  This is not the CA certificate!"
    log_error "  Expected: CN=OnPremise-CA-Root"
    exit 1
fi

echo ""

# Step 3: Check for existing certificate
log_info "Step 3/4: Checking for existing certificate..."

if security find-certificate -a -c "OnPremise-CA-Root" /Library/Keychains/System.keychain &> /dev/null; then
    log_warning "  Found existing OnPremise-CA certificate"
    log_info "  Removing old certificate..."

    # Remove existing certificate
    security delete-certificate -c "OnPremise-CA-Root" /Library/Keychains/System.keychain 2>/dev/null || true
    log_success "  Old certificate removed"
else
    log_info "  No existing certificate found"
fi

echo ""

# Step 4: Install certificate
log_info "Step 4/4: Installing CA certificate..."

if security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$TEMP_CERT"; then
    log_success "  Certificate installed to System keychain"
else
    log_error "  Failed to install certificate"
    exit 1
fi

echo ""

# Verification
log_info "Verifying installation..."

if security find-certificate -a -c "OnPremise-CA-Root" /Library/Keychains/System.keychain &> /dev/null; then
    log_success "  Certificate is installed and trusted"
else
    log_warning "  Certificate may not be fully trusted"
    log_info "  You may need to manually trust it in Keychain Access"
fi

echo ""

# Cleanup
rm -f "$TEMP_CERT"
log_info "Temporary file cleaned up"

echo ""
echo "=========================================="
echo "  Installation Complete"
echo "=========================================="
echo ""
log_success "CA certificate has been installed!"
echo ""
log_info "Certificate Details:"
echo "  Keychain: /Library/Keychains/System.keychain"
echo "  $SUBJECT"
echo "  $EXPIRES"
echo ""
log_success "Next Steps:"
log_info "  1. Close ALL browser windows completely"
log_info "  2. Restart your browser (Safari, Chrome, etc.)"
log_info "  3. Visit: https://${SERVER_IP}:5006/"
log_info "  4. You should see a lock icon 🔒 (no warning)"
echo ""
log_info "For Firefox, you need to import separately:"
log_info "  Settings → Privacy & Security → Certificates"
log_info "  → View Certificates → Authorities → Import"
echo ""
log_info "To manually verify in Keychain Access:"
log_info "  1. Open Keychain Access app"
log_info "  2. Select 'System' keychain"
log_info "  3. Find 'OnPremise-CA-Root'"
log_info "  4. Double-click → Trust → Set to 'Always Trust'"
echo ""
log_info "Test with curl:"
log_info "  curl https://${SERVER_IP}:5006/"
echo ""
