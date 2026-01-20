#!/bin/bash
################################################################################
# Certificate Verification Script
#
# Purpose: Verify CA and server certificates
# - Check certificate validity
# - Verify certificate chain
# - Check file permissions
# - Display certificate information
################################################################################

set -e

# Color logging functions
log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

# Get CA root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$CA_ROOT"

echo "========================================"
echo "  Certificate Verification"
echo "========================================"
echo ""

ERRORS=0

# ========================================
# Check CA Certificate
# ========================================

log_info "Checking CA certificate..."

if [[ ! -f "certs/ca/ca.crt" ]]; then
    log_error "CA certificate not found: certs/ca/ca.crt"
    ((ERRORS++))
else
    # Verify CA certificate
    if openssl x509 -in certs/ca/ca.crt -noout -text > /dev/null 2>&1; then
        log_success "CA certificate is valid"

        # Check if it's a CA certificate
        if openssl x509 -in certs/ca/ca.crt -noout -text | grep -q "CA:TRUE"; then
            log_success "CA certificate has CA:TRUE extension"
        else
            log_error "CA certificate missing CA:TRUE extension"
            ((ERRORS++))
        fi

        # Check expiration
        EXPIRY=$(openssl x509 -in certs/ca/ca.crt -noout -enddate | cut -d= -f2)
        log_info "CA certificate expires: $EXPIRY"

        # Check if expired
        if ! openssl x509 -in certs/ca/ca.crt -noout -checkend 0 > /dev/null 2>&1; then
            log_error "CA certificate has expired!"
            ((ERRORS++))
        fi
    else
        log_error "CA certificate is invalid or corrupted"
        ((ERRORS++))
    fi
fi

# Check CA private key
if [[ ! -f "certs/ca/ca.key" ]]; then
    log_error "CA private key not found: certs/ca/ca.key"
    ((ERRORS++))
else
    # Check permissions
    PERMS=$(stat -c "%a" certs/ca/ca.key)
    if [[ "$PERMS" == "600" ]]; then
        log_success "CA private key has correct permissions (600)"
    else
        log_warning "CA private key has incorrect permissions: $PERMS (should be 600)"
    fi
fi

echo ""

# ========================================
# Check Server Certificate
# ========================================

log_info "Checking server certificate..."

if [[ ! -f "certs/server/server.crt" ]]; then
    log_error "Server certificate not found: certs/server/server.crt"
    ((ERRORS++))
else
    # Verify server certificate
    if openssl x509 -in certs/server/server.crt -noout -text > /dev/null 2>&1; then
        log_success "Server certificate is valid"

        # Check expiration
        EXPIRY=$(openssl x509 -in certs/server/server.crt -noout -enddate | cut -d= -f2)
        log_info "Server certificate expires: $EXPIRY"

        # Check if expired
        if ! openssl x509 -in certs/server/server.crt -noout -checkend 0 > /dev/null 2>&1; then
            log_error "Server certificate has expired!"
            ((ERRORS++))
        fi

        # Check server name
        SERVER_CN=$(openssl x509 -in certs/server/server.crt -noout -subject | sed 's/.*CN = //')
        log_info "Server certificate CN: $SERVER_CN"
    else
        log_error "Server certificate is invalid or corrupted"
        ((ERRORS++))
    fi
fi

# Check server private key
if [[ ! -f "certs/server/server.key" ]]; then
    log_error "Server private key not found: certs/server/server.key"
    ((ERRORS++))
else
    # Check permissions
    PERMS=$(stat -c "%a" certs/server/server.key)
    if [[ "$PERMS" == "600" ]]; then
        log_success "Server private key has correct permissions (600)"
    else
        log_warning "Server private key has incorrect permissions: $PERMS (should be 600)"
    fi
fi

echo ""

# ========================================
# Verify Certificate Chain
# ========================================

log_info "Verifying certificate chain..."

if [[ -f "certs/ca/ca.crt" ]] && [[ -f "certs/server/server.crt" ]]; then
    # Verify server certificate is signed by CA
    if openssl verify -CAfile certs/ca/ca.crt certs/server/server.crt > /dev/null 2>&1; then
        log_success "Server certificate is correctly signed by CA"
    else
        log_error "Server certificate verification failed"
        ((ERRORS++))
    fi

    # Check certificate chain file
    if [[ -f "certs/server/server-chain.crt" ]]; then
        log_success "Certificate chain file exists"

        # Verify chain content
        CHAIN_CERTS=$(grep -c "BEGIN CERTIFICATE" certs/server/server-chain.crt)
        if [[ "$CHAIN_CERTS" == "2" ]]; then
            log_success "Certificate chain contains 2 certificates (server + CA)"
        else
            log_warning "Certificate chain contains $CHAIN_CERTS certificates (expected 2)"
        fi
    else
        log_error "Certificate chain file not found: certs/server/server-chain.crt"
        ((ERRORS++))
    fi
fi

echo ""

# ========================================
# Summary
# ========================================

echo "========================================"
echo "  Verification Summary"
echo "========================================"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    log_success "All certificates are valid!"
    echo ""
    echo "Certificate Details:"
    echo ""
    echo "CA Certificate:"
    openssl x509 -in certs/ca/ca.crt -noout -subject -issuer -dates 2>/dev/null || echo "  (not available)"
    echo ""
    echo "Server Certificate:"
    openssl x509 -in certs/server/server.crt -noout -subject -issuer -dates 2>/dev/null || echo "  (not available)"
    echo ""
    exit 0
else
    log_error "Found $ERRORS error(s) during verification"
    echo ""
    exit 1
fi
