#!/usr/bin/env pwsh

# HTTPS Development Server Startup Script
# This script starts both the Flask backend and Vue frontend with HTTPS support

Write-Host "🔒 Starting Bazos Ad Tracker with HTTPS support..." -ForegroundColor Green

# Check if certificates exist
$certDir = "frontend/certs"
$keyFile = "$certDir/localhost-key.pem"
$certFile = "$certDir/localhost.pem"

if (-not (Test-Path $keyFile) -or -not (Test-Path $certFile)) {
    Write-Host "📄 SSL certificates not found. Generating self-signed certificates..." -ForegroundColor Yellow
    
    # Create certs directory if it doesn't exist
    if (-not (Test-Path $certDir)) {
        New-Item -ItemType Directory -Path $certDir -Force
    }
    
    # Generate self-signed certificate using OpenSSL or mkcert
    # If mkcert is available, use it for better browser compatibility
    if (Get-Command mkcert -ErrorAction SilentlyContinue) {
        Write-Host "Using mkcert to generate certificates..." -ForegroundColor Cyan
        Set-Location $certDir
        mkcert localhost 127.0.0.1 ::1
        Move-Item "localhost+2.pem" "localhost.pem" -Force
        Move-Item "localhost+2-key.pem" "localhost-key.pem" -Force
        Set-Location ../..
    } else {
        Write-Host "⚠️  mkcert not found. Please install mkcert for better HTTPS support:" -ForegroundColor Yellow
        Write-Host "   - Download from: https://github.com/FiloSottile/mkcert/releases" -ForegroundColor Yellow
        Write-Host "   - Or use: choco install mkcert (if you have Chocolatey)" -ForegroundColor Yellow
        Write-Host "   - Or use: scoop install mkcert (if you have Scoop)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Falling back to OpenSSL certificate generation..." -ForegroundColor Yellow
        
        # Try to use OpenSSL if available
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            Set-Location $certDir
            openssl req -x509 -newkey rsa:4096 -keyout localhost-key.pem -out localhost.pem -days 365 -nodes -subj "/C=US/ST=Development/L=Development/O=Development/CN=localhost"
            Set-Location ../..
        } else {
            Write-Host "❌ Neither mkcert nor OpenSSL found. Cannot generate certificates." -ForegroundColor Red
            Write-Host "Please install one of them to use HTTPS." -ForegroundColor Red
            exit 1
        }
    }
}

# Set environment variables for HTTPS
$env:VITE_API_TARGET = "https://localhost:5000"
$env:VITE_SOCKET_URL = "https://localhost:5000"

Write-Host "🚀 Starting Flask backend with HTTPS on port 5000..." -ForegroundColor Blue

# Start Flask backend with HTTPS in background
$flaskJob = Start-Job -ScriptBlock {
    param($workingDir)
    Set-Location $workingDir
    
    # Check if SSL cert exists for Flask
    $flaskCertDir = "certs"
    if (-not (Test-Path $flaskCertDir)) {
        New-Item -ItemType Directory -Path $flaskCertDir -Force
    }
    
    if (-not (Test-Path "$flaskCertDir/server.crt") -or -not (Test-Path "$flaskCertDir/server.key")) {
        # Copy frontend certs to backend
        if (Test-Path "frontend/certs/localhost.pem") {
            Copy-Item "frontend/certs/localhost.pem" "$flaskCertDir/server.crt"
            Copy-Item "frontend/certs/localhost-key.pem" "$flaskCertDir/server.key"
        }
    }
    
    # Start Flask with HTTPS if certificates exist
    if ((Test-Path "$flaskCertDir/server.crt") -and (Test-Path "$flaskCertDir/server.key")) {
        python app.py --ssl-context=adhoc
    } else {
        python app.py
    }
} -ArgumentList (Get-Location)

Start-Sleep -Seconds 3

Write-Host "🎨 Starting Vue frontend with HTTPS on port 3000..." -ForegroundColor Cyan

# Start Vue frontend with HTTPS
Set-Location frontend

# Update Vite config to enable HTTPS
$viteConfig = Get-Content "vite.config.ts" -Raw
if ($viteConfig -notmatch "https:") {
    Write-Host "Enabling HTTPS in Vite configuration..." -ForegroundColor Yellow
    $viteConfig = $viteConfig -replace "// https:", "https:"
    $viteConfig = $viteConfig -replace "//   key:", "  key:"
    $viteConfig = $viteConfig -replace "//   cert:", "  cert:"
    Set-Content "vite.config.ts" -Value $viteConfig
}

# Start Vue dev server
npm run dev -- --host 0.0.0.0

# Cleanup when script ends
Write-Host "🛑 Shutting down servers..." -ForegroundColor Red
Remove-Job $flaskJob -Force
Set-Location ..

Write-Host "✅ Servers stopped." -ForegroundColor Green
