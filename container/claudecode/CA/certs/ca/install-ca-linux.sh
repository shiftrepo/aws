#!/bin/bash
################################################################################
# CA Certificate Installation Script for Linux
#
# Purpose: Download and install CA certificate on Linux
# Usage:
#   curl -O http://SERVER_IP:8080/install-ca-linux.sh
#   chmod +x install-ca-linux.sh
#   sudo ./install-ca-linux.sh
#
# Supports: Ubuntu, Debian, CentOS, RHEL, Fedora
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
echo "  CA Certificate Installation (Linux)"
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

# Detect Linux distribution
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    log_info "Detected OS: $PRETTY_NAME"
else
    log_error "Cannot detect Linux distribution"
    exit 1
fi

echo ""

# Step 1: Download CA certificate
log_info "Step 1/4: Downloading CA certificate..."
log_info "  URL: $CA_CERT_URL"

if command -v curl &> /dev/null; then
    if curl -f -o "$TEMP_CERT" "$CA_CERT_URL"; then
        log_success "  Downloaded to: $TEMP_CERT"
    else
        log_error "  Failed to download certificate"
        log_info "Please check server is running: http://${SERVER_IP}:${DOWNLOAD_PORT}/"
        exit 1
    fi
elif command -v wget &> /dev/null; then
    if wget -O "$TEMP_CERT" "$CA_CERT_URL"; then
        log_success "  Downloaded to: $TEMP_CERT"
    else
        log_error "  Failed to download certificate"
        log_info "Please check server is running: http://${SERVER_IP}:${DOWNLOAD_PORT}/"
        exit 1
    fi
else
    log_error "Neither curl nor wget found"
    log_info "Please install curl or wget"
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

# Step 3: Install based on distribution
log_info "Step 3/4: Installing CA certificate..."

case "$OS" in
    ubuntu|debian)
        CERT_DIR="/usr/local/share/ca-certificates"
        CERT_FILE="$CERT_DIR/onpremise-ca.crt"

        log_info "  Installing to: $CERT_FILE"
        cp "$TEMP_CERT" "$CERT_FILE"
        chmod 644 "$CERT_FILE"

        log_info "  Updating certificate store..."
        update-ca-certificates

        if [[ $? -eq 0 ]]; then
            log_success "  Certificate installed successfully"
        else
            log_error "  Failed to update certificate store"
            exit 1
        fi
        ;;

    centos|rhel|fedora|rocky|almalinux)
        CERT_DIR="/etc/pki/ca-trust/source/anchors"
        CERT_FILE="$CERT_DIR/onpremise-ca.crt"

        log_info "  Installing to: $CERT_FILE"
        cp "$TEMP_CERT" "$CERT_FILE"
        chmod 644 "$CERT_FILE"

        log_info "  Updating certificate store..."
        update-ca-trust extract

        if [[ $? -eq 0 ]]; then
            log_success "  Certificate installed successfully"
        else
            log_error "  Failed to update certificate store"
            exit 1
        fi
        ;;

    *)
        log_error "  Unsupported distribution: $OS"
        log_info "Please install manually:"
        log_info "  1. Copy $TEMP_CERT to your CA certificate directory"
        log_info "  2. Run your distribution's certificate update command"
        exit 1
        ;;
esac

echo ""

# Step 4: Verify installation
log_info "Step 4/4: Verifying installation..."

if [[ -f "$CERT_FILE" ]]; then
    log_success "  Certificate file exists: $CERT_FILE"

    # Try to verify using openssl
    if openssl verify -CAfile "$CERT_FILE" "$CERT_FILE" &> /dev/null; then
        log_success "  Certificate verification passed"
    fi
else
    log_error "  Certificate file not found: $CERT_FILE"
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
echo "  Location: $CERT_FILE"
echo "  $SUBJECT"
echo "  $EXPIRES"
echo ""
log_success "Next Steps:"
log_info "  1. Close ALL browser windows completely"
log_info "  2. Restart your browser"
log_info "  3. Visit: https://${SERVER_IP}:5006/"
log_info "  4. You should see a lock icon 🔒 (no warning)"
echo ""
log_info "For Firefox, you need to import separately:"
log_info "  Settings → Privacy & Security → Certificates"
log_info "  → View Certificates → Authorities → Import"
log_info "  → Select: $CERT_FILE"
echo ""
log_info "Test with curl:"
log_info "  curl https://${SERVER_IP}:5006/"
echo ""
