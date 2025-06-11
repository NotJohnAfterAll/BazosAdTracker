# Quick Start - Production Test
# Test the production build locally before deploying to Coolify

Write-Host "Starting Bazos Ad Tracker - Production Test Mode" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

$projectRoot = "c:\Users\musil\Documents\CodeProjects\Bazos\BazosAdTracker"
Set-Location $projectRoot

# Set production environment variables
$env:FLASK_ENV = "production"
$env:FLASK_DEBUG = "false"
$env:PORT = "5000"
$env:HOST = "127.0.0.1"
$env:CHECK_INTERVAL = "60"  # Shorter interval for testing

Write-Host ""
Write-Host "🔧 Environment Configuration:" -ForegroundColor Cyan
Write-Host "   FLASK_ENV: $env:FLASK_ENV"
Write-Host "   PORT: $env:PORT"
Write-Host "   HOST: $env:HOST"
Write-Host "   CHECK_INTERVAL: $env:CHECK_INTERVAL seconds"

Write-Host ""
Write-Host "🏗️  Building frontend..." -ForegroundColor Blue
Set-Location "frontend"
npm run build | Out-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

Write-Host ""
Write-Host "🚀 Starting scheduler process..." -ForegroundColor Blue
$schedulerJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    $env:FLASK_ENV = $using:env:FLASK_ENV
    python scheduler.py
}

Write-Host "   Scheduler Job ID: $($schedulerJob.Id)"

# Give scheduler time to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🌐 Starting web application..." -ForegroundColor Blue
Write-Host "   URL: http://$env:HOST`:$env:PORT" -ForegroundColor Yellow
Write-Host "   Health Check: http://$env:HOST`:$env:PORT/api/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop both processes" -ForegroundColor Gray
Write-Host ""

try {
    # Start Flask app (this will block)
    python app.py
}
finally {
    Write-Host ""
    Write-Host "🛑 Stopping scheduler process..." -ForegroundColor Red
    Stop-Job -Job $schedulerJob -PassThru | Remove-Job
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}
