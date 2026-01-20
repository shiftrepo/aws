################################################################################
# Certificate Installation Script for Azure DevOps Server
#
# Purpose: Install CA and server certificates on Azure DevOps Server (on-premise)
# Requirements:
#   - Administrator privileges
#   - Azure DevOps Server installed
#   - IIS installed
#
# Usage:
#   1. Copy certificate files to the server
#   2. Run this script with Administrator privileges
#   3. Configure Azure DevOps Server to use HTTPS
################################################################################

param(
    [Parameter(Mandatory=$false)]
    [string]$CertificateBundle = "",

    [Parameter(Mandatory=$false)]
    [string]$SiteName = "Azure DevOps Server",

    [Parameter(Mandatory=$false)]
    [int]$HttpsPort = 443
)

# Color output functions
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }

Clear-Host

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Azure DevOps Server Certificate Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Error "This script requires Administrator privileges"
    Write-Info "Please run PowerShell as Administrator"
    exit 1
}

Write-Success "Running with Administrator privileges"
Write-Host ""

# Prompt for certificate files if not provided
if ($CertificateBundle -eq "") {
    Write-Info "Please provide the certificate bundle directory path"
    Write-Info "Example: C:\Temp\ca-bundle-20260120-013115"
    $CertificateBundle = Read-Host "Certificate bundle path"
}

if (-not (Test-Path $CertificateBundle)) {
    Write-Error "Certificate bundle not found: $CertificateBundle"
    Write-Info "Please extract the ca-bundle-*.tar.gz file first"
    exit 1
}

Write-Success "Found certificate bundle: $CertificateBundle"
Write-Host ""

# Define certificate file paths
$CaCertPath = Join-Path $CertificateBundle "ca.crt"
$ServerCertPath = Join-Path $CertificateBundle "server.crt"
$ServerKeyPath = Join-Path $CertificateBundle "server.key"
$ServerChainPath = Join-Path $CertificateBundle "server-chain.crt"

# Verify all required files exist
Write-Info "Verifying certificate files..."
$missingFiles = @()

if (-not (Test-Path $CaCertPath)) { $missingFiles += "ca.crt" }
if (-not (Test-Path $ServerCertPath)) { $missingFiles += "server.crt" }
if (-not (Test-Path $ServerKeyPath)) { $missingFiles += "server.key" }

if ($missingFiles.Count -gt 0) {
    Write-Error "Missing required files: $($missingFiles -join ', ')"
    exit 1
}

Write-Success "All required certificate files found"
Write-Host ""

# Step 1: Install CA certificate to Trusted Root
Write-Host "Step 1: Installing CA Certificate" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

try {
    $caCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($CaCertPath)

    Write-Info "CA Certificate Details:"
    Write-Host "  Subject: $($caCert.Subject)" -ForegroundColor White
    Write-Host "  Issuer: $($caCert.Issuer)" -ForegroundColor White
    Write-Host "  Valid Until: $($caCert.NotAfter)" -ForegroundColor White

    # Install to Trusted Root Certification Authorities
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
    $store.Open("ReadWrite")

    # Remove existing if present
    $existingCA = $store.Certificates | Where-Object { $_.Thumbprint -eq $caCert.Thumbprint }
    if ($existingCA) {
        $store.Remove($existingCA)
        Write-Info "Removed existing CA certificate"
    }

    $store.Add($caCert)
    $store.Close()

    Write-Success "CA certificate installed to Trusted Root"
} catch {
    Write-Error "Failed to install CA certificate: $_"
    exit 1
}

Write-Host ""

# Step 2: Create PFX from certificate and private key
Write-Host "Step 2: Creating PFX Certificate" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

$pfxPassword = Read-Host "Enter password for PFX file (or press Enter for auto-generated)" -AsSecureString
if ($pfxPassword.Length -eq 0) {
    $pfxPassword = ConvertTo-SecureString -String ([System.Guid]::NewGuid().ToString()) -AsPlainText -Force
    Write-Info "Auto-generated PFX password"
}

$tempPfxPath = Join-Path $env:TEMP "devops-server-cert.pfx"

Write-Info "Creating PFX file..."
Write-Info "  This requires OpenSSL to be installed"

# Check if OpenSSL is available
$opensslPath = $null
$possiblePaths = @(
    "C:\Program Files\Git\usr\bin\openssl.exe",
    "C:\Program Files (x86)\Git\usr\bin\openssl.exe",
    "C:\OpenSSL\bin\openssl.exe",
    "C:\OpenSSL-Win64\bin\openssl.exe",
    "openssl.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path -ErrorAction SilentlyContinue) {
        $opensslPath = $path
        break
    }
}

if (-not $opensslPath) {
    # Try to find in PATH
    try {
        $opensslPath = (Get-Command openssl -ErrorAction Stop).Source
    } catch {
        Write-Error "OpenSSL not found"
        Write-Info "Please install OpenSSL or Git for Windows"
        Write-Info "Alternatively, create PFX manually using:"
        Write-Info "  openssl pkcs12 -export -out server.pfx -inkey server.key -in server.crt -certfile ca.crt"
        exit 1
    }
}

Write-Info "Using OpenSSL: $opensslPath"

# Convert password to plain text for OpenSSL
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pfxPassword)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Create PFX using OpenSSL
$opensslCmd = "& `"$opensslPath`" pkcs12 -export -out `"$tempPfxPath`" -inkey `"$ServerKeyPath`" -in `"$ServerCertPath`" -certfile `"$CaCertPath`" -password pass:`"$plainPassword`""

try {
    Invoke-Expression $opensslCmd | Out-Null
    if (Test-Path $tempPfxPath) {
        Write-Success "PFX file created: $tempPfxPath"
    } else {
        throw "PFX file was not created"
    }
} catch {
    Write-Error "Failed to create PFX: $_"
    Write-Info "Manual command:"
    Write-Info "  openssl pkcs12 -export -out server.pfx -inkey `"$ServerKeyPath`" -in `"$ServerCertPath`" -certfile `"$CaCertPath`""
    exit 1
}

Write-Host ""

# Step 3: Import PFX to Personal certificate store
Write-Host "Step 3: Importing Server Certificate" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow

try {
    $serverCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($tempPfxPath, $pfxPassword, [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet -bor [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::PersistKeySet)

    Write-Info "Server Certificate Details:"
    Write-Host "  Subject: $($serverCert.Subject)" -ForegroundColor White
    Write-Host "  Issuer: $($serverCert.Issuer)" -ForegroundColor White
    Write-Host "  Thumbprint: $($serverCert.Thumbprint)" -ForegroundColor White
    Write-Host "  Valid Until: $($serverCert.NotAfter)" -ForegroundColor White

    # Install to Personal store
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My","LocalMachine")
    $store.Open("ReadWrite")

    # Remove existing if present
    $existing = $store.Certificates | Where-Object { $_.Thumbprint -eq $serverCert.Thumbprint }
    if ($existing) {
        $store.Remove($existing)
        Write-Info "Removed existing server certificate"
    }

    $store.Add($serverCert)
    $store.Close()

    Write-Success "Server certificate installed to Personal store"
    Write-Info "Certificate Thumbprint: $($serverCert.Thumbprint)"
} catch {
    Write-Error "Failed to import server certificate: $_"
    exit 1
}

Write-Host ""

# Step 4: Configure IIS HTTPS binding
Write-Host "Step 4: Configuring IIS HTTPS Binding" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow

# Check if WebAdministration module is available
try {
    Import-Module WebAdministration -ErrorAction Stop
    Write-Success "IIS WebAdministration module loaded"
} catch {
    Write-Warning "IIS WebAdministration module not available"
    Write-Info "You'll need to configure IIS binding manually"
    Write-Info "Certificate Thumbprint: $($serverCert.Thumbprint)"
    Write-Host ""
    Write-Info "Manual IIS configuration steps:"
    Write-Info "  1. Open IIS Manager"
    Write-Info "  2. Select your site: $SiteName"
    Write-Info "  3. Click 'Bindings' in the Actions pane"
    Write-Info "  4. Add/Edit HTTPS binding"
    Write-Info "  5. Select the certificate with thumbprint: $($serverCert.Thumbprint)"
    Write-Info "  6. Port: $HttpsPort"
    Write-Host ""

    # Skip IIS configuration
    $configureIIS = $false
}

if ($configureIIS -ne $false) {
    # Find the site
    $site = Get-Website | Where-Object { $_.Name -like "*$SiteName*" -or $_.Name -eq "Default Web Site" }

    if (-not $site) {
        Write-Warning "Could not find website: $SiteName"
        Write-Info "Available sites:"
        Get-Website | ForEach-Object { Write-Info "  - $($_.Name)" }

        $customSite = Read-Host "Enter the exact site name to configure (or press Enter to skip)"
        if ($customSite) {
            $site = Get-Website -Name $customSite
        }
    }

    if ($site) {
        Write-Info "Configuring site: $($site.Name)"

        # Check for existing HTTPS binding
        $existingBinding = Get-WebBinding -Name $site.Name -Protocol "https" -Port $HttpsPort

        if ($existingBinding) {
            Write-Info "Removing existing HTTPS binding on port $HttpsPort"
            Remove-WebBinding -Name $site.Name -Protocol "https" -Port $HttpsPort -Confirm:$false
        }

        # Add new HTTPS binding
        try {
            New-WebBinding -Name $site.Name -Protocol "https" -Port $HttpsPort -SslFlags 0

            # Bind certificate to the HTTPS binding
            $binding = Get-WebBinding -Name $site.Name -Protocol "https" -Port $HttpsPort
            $binding.AddSslCertificate($serverCert.Thumbprint, "My")

            Write-Success "HTTPS binding configured"
            Write-Info "  Site: $($site.Name)"
            Write-Info "  Port: $HttpsPort"
            Write-Info "  Certificate: $($serverCert.Thumbprint)"
        } catch {
            Write-Error "Failed to configure IIS binding: $_"
            Write-Info "Please configure manually in IIS Manager"
        }
    } else {
        Write-Warning "Site configuration skipped"
    }
}

Write-Host ""

# Step 5: Azure DevOps Server configuration
Write-Host "Step 5: Azure DevOps Server Configuration" -ForegroundColor Yellow
Write-Host "------------------------------------------" -ForegroundColor Yellow

Write-Info "Next steps for Azure DevOps Server:"
Write-Host ""
Write-Host "  1. Open Azure DevOps Server Administration Console" -ForegroundColor White
Write-Host "  2. Go to Application Tier → Change URLs" -ForegroundColor White
Write-Host "  3. Update Public URL to HTTPS:" -ForegroundColor White
Write-Host "     https://YOUR_SERVER_NAME/" -ForegroundColor Cyan
Write-Host "  4. Click OK and apply changes" -ForegroundColor White
Write-Host ""
Write-Host "  5. Restart Azure DevOps Server services:" -ForegroundColor White
Write-Host "     - Open Services (services.msc)" -ForegroundColor White
Write-Host "     - Restart 'Azure DevOps Server' and related services" -ForegroundColor White
Write-Host ""
Write-Host "  6. Test HTTPS access:" -ForegroundColor White
Write-Host "     https://YOUR_SERVER_NAME/" -ForegroundColor Cyan
Write-Host ""

Write-Info "Certificate Thumbprint (for reference):"
Write-Host "  $($serverCert.Thumbprint)" -ForegroundColor Yellow
Write-Host ""

# Cleanup
try {
    Remove-Item $tempPfxPath -Force -ErrorAction SilentlyContinue
    Write-Info "Temporary files cleaned up"
} catch {
    # Ignore cleanup errors
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Success "Server certificates have been installed"
Write-Info "Please complete Azure DevOps Server configuration as shown above"
Write-Host ""

Read-Host "Press Enter to exit"
