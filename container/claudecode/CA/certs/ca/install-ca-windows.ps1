################################################################################
# CA Certificate Installation Script for Windows
#
# Purpose: Download and install CA certificate on Windows
# Usage:
#   1. Right-click and "Run with PowerShell"
#   2. Or: powershell -ExecutionPolicy Bypass -File install-ca-windows.ps1
#
# Requirements: Administrator privileges
################################################################################

# Configuration
$SERVER_IP = "98.93.187.130"
$DOWNLOAD_PORT = "8080"
$CA_CERT_URL = "http://${SERVER_IP}:${DOWNLOAD_PORT}/ca.crt"
$DOWNLOAD_PATH = "$env:TEMP\onpremise-ca.crt"

# Color output functions
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }

# Clear screen
Clear-Host

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CA Certificate Installation (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "This script requires Administrator privileges"
    Write-Info "Please right-click and select 'Run as Administrator'"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Success "Running with Administrator privileges"
Write-Host ""

# Step 1: Download CA certificate
Write-Info "Step 1/4: Downloading CA certificate..."
Write-Info "  URL: $CA_CERT_URL"

try {
    Invoke-WebRequest -Uri $CA_CERT_URL -OutFile $DOWNLOAD_PATH -UseBasicParsing
    Write-Success "  Downloaded to: $DOWNLOAD_PATH"
} catch {
    Write-Error "  Failed to download certificate"
    Write-Error "  $_"
    Write-Host ""
    Write-Info "Please check:"
    Write-Info "  1. Server is running: http://${SERVER_IP}:${DOWNLOAD_PORT}/"
    Write-Info "  2. Firewall allows port $DOWNLOAD_PORT"
    Write-Info "  3. Network connectivity"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 2: Verify certificate
Write-Info "Step 2/4: Verifying certificate..."

try {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($DOWNLOAD_PATH)

    Write-Info "  Subject: $($cert.Subject)"
    Write-Info "  Issuer: $($cert.Issuer)"
    Write-Info "  Valid Until: $($cert.NotAfter)"

    # Check if it's a CA certificate
    if ($cert.Subject -like "*OnPremise-CA-Root*") {
        Write-Success "  Verified: This is the correct CA certificate"
    } else {
        Write-Error "  This is not the CA certificate!"
        Write-Error "  Expected: CN=OnPremise-CA-Root"
        Write-Error "  Got: $($cert.Subject)"
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Error "  Failed to read certificate"
    Write-Error "  $_"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 3: Remove existing certificate (if any)
Write-Info "Step 3/4: Checking for existing certificate..."

$existingCerts = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*OnPremise-CA-Root*" }

if ($existingCerts) {
    Write-Warning "  Found existing OnPremise-CA certificate"
    Write-Info "  Removing old certificate..."

    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
    $store.Open("ReadWrite")

    foreach ($oldCert in $existingCerts) {
        $store.Remove($oldCert)
        Write-Info "  Removed: $($oldCert.Thumbprint)"
    }

    $store.Close()
    Write-Success "  Old certificate removed"
} else {
    Write-Info "  No existing certificate found"
}

Write-Host ""

# Step 4: Install certificate
Write-Info "Step 4/4: Installing CA certificate..."

try {
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
    $store.Open("ReadWrite")
    $store.Add($cert)
    $store.Close()

    Write-Success "  Certificate installed to LocalMachine\Root"
} catch {
    Write-Error "  Failed to install certificate"
    Write-Error "  $_"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Verification
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installation Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$installedCert = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*OnPremise-CA-Root*" }

if ($installedCert) {
    Write-Success "Certificate is installed!"
    Write-Host ""
    Write-Info "Certificate Details:"
    Write-Host "  Subject:    $($installedCert.Subject)" -ForegroundColor White
    Write-Host "  Issuer:     $($installedCert.Issuer)" -ForegroundColor White
    Write-Host "  Thumbprint: $($installedCert.Thumbprint)" -ForegroundColor White
    Write-Host "  Valid Until: $($installedCert.NotAfter)" -ForegroundColor White
    Write-Host ""

    Write-Success "Next Steps:"
    Write-Info "  1. Close ALL browser windows completely"
    Write-Info "  2. Restart your browser"
    Write-Info "  3. Visit: https://${SERVER_IP}:5006/"
    Write-Info "  4. You should see a lock icon 🔒 (no warning)"
    Write-Host ""

} else {
    Write-Error "Certificate installation failed!"
    Write-Info "Please try manual installation:"
    Write-Info "  1. Run: certmgr.msc"
    Write-Info "  2. Import $DOWNLOAD_PATH to Trusted Root Certification Authorities"
    Write-Host ""
}

# Cleanup
try {
    Remove-Item $DOWNLOAD_PATH -Force -ErrorAction SilentlyContinue
    Write-Info "Temporary file cleaned up"
} catch {
    # Ignore cleanup errors
}

Write-Host ""
Write-Info "Installation complete!"
Write-Host ""
Read-Host "Press Enter to exit"
