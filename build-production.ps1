# Bazos Ad Tracker - Production Build Script
# This script builds the Vue.js frontend for production

Write-Host "Building Bazos Ad Tracker for Production..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

try {
    # Navigate to frontend directory
    Set-Location "c:\Users\musil\Documents\CodeProjects\Bazos\BazosAdTracker\frontend"
    
    Write-Host "Installing/updating dependencies..." -ForegroundColor Blue
    npm install
    
    Write-Host "Running TypeScript type check..." -ForegroundColor Blue
    npm run type-check
    
    Write-Host "Building production bundle..." -ForegroundColor Blue
    npm run build
    
    Write-Host ""
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Built files are in the 'dist' directory." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To test the production build locally:" -ForegroundColor Cyan
    Write-Host "  npm run preview" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To deploy, copy the contents of the 'dist' directory to your web server." -ForegroundColor Cyan
}
catch {
    Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
