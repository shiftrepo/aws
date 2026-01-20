#!/bin/bash
################################################################################
# CA and Server Certificate Generation Script
#
# Purpose: Generate CA certificate and server certificate with minimal user input
# Usage: ./create-ca.sh [--auto]
#   --auto: Use all defaults from .env without prompts
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

# Check if auto mode
AUTO_MODE=false
if [[ "$1" == "--auto" ]]; then
    AUTO_MODE=true
    log_info "Running in automatic mode (no prompts)"
fi

echo "========================================"
echo "  CA Certificate Generation"
echo "========================================"
echo ""

# Load environment variables
if [[ ! -f .env ]]; then
    log_error ".env file not found. Please run setup-ca-environment.sh first."
    exit 1
fi

source .env
log_success "Environment variables loaded from .env"

# Set defaults from environment
DEFAULT_SERVER_NAME="${SERVER_NAME:-${EC2_PUBLIC_IP:-localhost}}"
DEFAULT_VALIDITY_DAYS="${CERT_VALIDITY_DAYS:-730}"
DEFAULT_COUNTRY="${CERT_COUNTRY:-JP}"
DEFAULT_STATE="${CERT_STATE:-Tokyo}"
DEFAULT_LOCALITY="${CERT_LOCALITY:-Tokyo}"
DEFAULT_ORGANIZATION="${CERT_ORGANIZATION:-OnPremise-CA}"
DEFAULT_ORG_UNIT="${CERT_ORG_UNIT:-IT}"

# User input (minimal)
if [[ "$AUTO_MODE" == false ]]; then
    echo ""
    echo "Certificate Configuration"
    echo "Press Enter to use default values shown in brackets"
    echo ""

    read -p "Server name or IP address [$DEFAULT_SERVER_NAME]: " INPUT_SERVER_NAME
    SERVER_NAME="${INPUT_SERVER_NAME:-$DEFAULT_SERVER_NAME}"

    read -p "Certificate validity days [$DEFAULT_VALIDITY_DAYS]: " INPUT_VALIDITY_DAYS
    VALIDITY_DAYS="${INPUT_VALIDITY_DAYS:-$DEFAULT_VALIDITY_DAYS}"

    read -p "Organization name [$DEFAULT_ORGANIZATION]: " INPUT_ORGANIZATION
    ORGANIZATION="${INPUT_ORGANIZATION:-$DEFAULT_ORGANIZATION}"

    echo ""
else
    SERVER_NAME="$DEFAULT_SERVER_NAME"
    VALIDITY_DAYS="$DEFAULT_VALIDITY_DAYS"
    ORGANIZATION="$DEFAULT_ORGANIZATION"
fi

COUNTRY="$DEFAULT_COUNTRY"
STATE="$DEFAULT_STATE"
LOCALITY="$DEFAULT_LOCALITY"
ORG_UNIT="$DEFAULT_ORG_UNIT"

log_info "Configuration:"
log_info "  Server Name: $SERVER_NAME"
log_info "  Validity: $VALIDITY_DAYS days"
log_info "  Organization: $ORGANIZATION"
echo ""

# Create log file
LOG_FILE="logs/certificate-generation.log"
echo "=== Certificate Generation $(date) ===" > "$LOG_FILE"

# ========================================
# Generate CA Certificate
# ========================================

if [[ -f "certs/ca/ca.crt" ]] && [[ -f "certs/ca/ca.key" ]]; then
    log_warning "CA certificate already exists. Skipping CA generation."
    log_info "  CA Certificate: certs/ca/ca.crt"
    log_info "  CA Private Key: certs/ca/ca.key"
    echo "" >> "$LOG_FILE"
    echo "CA certificate already exists (skipped)" >> "$LOG_FILE"
else
    log_info "Generating CA certificate..."

    # Generate CA private key (4096-bit RSA)
    log_info "  Step 1/2: Generating CA private key (4096-bit)..."
    openssl genrsa -out certs/ca/ca.key 4096 >> "$LOG_FILE" 2>&1

    # Generate self-signed CA certificate
    log_info "  Step 2/2: Generating self-signed CA certificate..."
    openssl req -new -x509 \
        -days "$VALIDITY_DAYS" \
        -key certs/ca/ca.key \
        -out certs/ca/ca.crt \
        -config config/openssl-ca.cnf \
        -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORG_UNIT/CN=OnPremise-CA-Root" \
        >> "$LOG_FILE" 2>&1

    # Set permissions
    chmod 600 certs/ca/ca.key
    chmod 644 certs/ca/ca.crt

    log_success "CA certificate generated successfully"
    log_info "  CA Certificate: certs/ca/ca.crt"
    log_info "  CA Private Key: certs/ca/ca.key (600)"
    echo ""
fi

# ========================================
# Generate Server Certificate
# ========================================

log_info "Generating server certificate for: $SERVER_NAME"

# Create temporary OpenSSL config with subjectAltName
TEMP_CONF=$(mktemp)
cat config/openssl-server.cnf > "$TEMP_CONF"
cat >> "$TEMP_CONF" << EOF

[ alt_names ]
DNS.1 = $SERVER_NAME
IP.1 = $SERVER_NAME
EOF

# Generate server private key
log_info "  Step 1/4: Generating server private key (2048-bit)..."
openssl genrsa -out certs/server/server.key 2048 >> "$LOG_FILE" 2>&1

# Generate Certificate Signing Request (CSR)
log_info "  Step 2/4: Generating Certificate Signing Request (CSR)..."
openssl req -new \
    -key certs/server/server.key \
    -out certs/server/server.csr \
    -config "$TEMP_CONF" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORG_UNIT/CN=$SERVER_NAME" \
    >> "$LOG_FILE" 2>&1

# Sign server certificate with CA
log_info "  Step 3/4: Signing server certificate with CA..."
openssl x509 -req \
    -in certs/server/server.csr \
    -CA certs/ca/ca.crt \
    -CAkey certs/ca/ca.key \
    -CAcreateserial \
    -out certs/server/server.crt \
    -days "$VALIDITY_DAYS" \
    -sha256 \
    -extensions v3_req \
    -extfile "$TEMP_CONF" \
    >> "$LOG_FILE" 2>&1

# Create certificate chain (server + CA)
log_info "  Step 4/4: Creating certificate chain..."
cat certs/server/server.crt certs/ca/ca.crt > certs/server/server-chain.crt

# Clean up temporary config
rm -f "$TEMP_CONF"

# Set permissions
chmod 600 certs/server/server.key
chmod 644 certs/server/server.crt
chmod 644 certs/server/server-chain.crt
chmod 600 certs/server/server.csr

log_success "Server certificate generated successfully"
log_info "  Server Certificate: certs/server/server.crt"
log_info "  Server Private Key: certs/server/server.key (600)"
log_info "  Certificate Chain: certs/server/server-chain.crt"
echo ""

# ========================================
# Display Certificate Summary
# ========================================

echo "========================================"
echo "  Certificate Generation Summary"
echo "========================================"
echo ""

log_info "CA Certificate Details:"
openssl x509 -in certs/ca/ca.crt -noout -subject -issuer -dates | while IFS= read -r line; do
    log_info "  $line"
done
echo ""

log_info "Server Certificate Details:"
openssl x509 -in certs/server/server.crt -noout -subject -issuer -dates | while IFS= read -r line; do
    log_info "  $line"
done
echo ""

log_info "Certificate Files:"
log_info "  CA Certificate:       certs/ca/ca.crt"
log_info "  CA Private Key:       certs/ca/ca.key"
log_info "  Server Certificate:   certs/server/server.crt"
log_info "  Server Private Key:   certs/server/server.key"
log_info "  Certificate Chain:    certs/server/server-chain.crt"
echo ""

log_success "All certificates generated successfully!"
echo ""
echo "Next steps:"
echo "  1. Verify certificates: ./scripts/utils/verify-certificates.sh"
echo "  2. Start HTTPS server:  sudo docker-compose up -d"
echo "  3. Test connection:     curl -k https://$SERVER_NAME:${HTTPS_PORT:-3000}/"
echo "  4. Export certificates: ./scripts/export-certificates.sh"
echo ""
