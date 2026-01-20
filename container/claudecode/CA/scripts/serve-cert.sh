#!/bin/bash
################################################################################
# CA Certificate Download Server
#
# Purpose: Serve CA certificate via HTTP for easy client download
# Usage: ./scripts/serve-cert.sh [port]
################################################################################

set -e

# Color logging functions
log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

# Get script directory and CA root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$CA_ROOT"

# Load environment variables
if [[ -f .env ]]; then
    source .env
fi

# Use provided port or default to 8080
PORT="${1:-${CERT_DOWNLOAD_PORT:-8080}}"
CERT_DIR="certs/ca"
SERVER_IP="${SERVER_NAME:-${EC2_PUBLIC_IP:-localhost}}"

# Check if CA certificate exists
if [[ ! -f "$CERT_DIR/ca.crt" ]]; then
    log_error "CA certificate not found: $CERT_DIR/ca.crt"
    log_info "Please run: ./scripts/create-ca.sh first"
    exit 1
fi

echo "=========================================="
echo "  CA Certificate Download Server"
echo "=========================================="
echo ""
log_info "Certificate: $CERT_DIR/ca.crt"
log_info "Server Port: $PORT"
echo ""
log_success "Download URL:"
echo "  http://$SERVER_IP:$PORT/ca.crt"
echo ""
log_info "Client Installation Scripts:"
echo "  Windows: http://$SERVER_IP:$PORT/install-ca-windows.ps1"
echo "  Linux:   http://$SERVER_IP:$PORT/install-ca-linux.sh"
echo ""
log_warning "Press Ctrl+C to stop the server"
echo ""

# Check if port is available
if sudo ss -tlnp | grep -q ":$PORT "; then
    log_error "Port $PORT is already in use"
    log_info "Try a different port: ./scripts/serve-cert.sh <port>"
    exit 1
fi

# Use Python to serve the certificate
if command -v python3 &> /dev/null; then
    cd "$CERT_DIR"
    log_info "Starting Python HTTP server..."
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    cd "$CERT_DIR"
    log_info "Starting Python HTTP server..."
    python -m http.server $PORT
else
    log_error "Python not found"
    log_info "Please install Python to use this script"
    exit 1
fi
