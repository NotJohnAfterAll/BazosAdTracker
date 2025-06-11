# Bazos Ad Tracker - Development Startup Script
# This script starts both the Flask backend and Vue.js frontend

Write-Host "Starting Bazos Ad Tracker Development Environment..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to start Flask backend
function Start-FlaskBackend {
    Write-Host "Starting Flask backend on port 5000..." -ForegroundColor Blue
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\musil\Documents\CodeProjects\Bazos\BazosAdTracker'; python app.py"
}

# Function to start Vue frontend
function Start-VueFrontend {
    Write-Host "Starting Vue.js frontend on port 3000..." -ForegroundColor Blue
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\musil\Documents\CodeProjects\Bazos\BazosAdTracker\frontend'; npm run dev"
}

# Start backend
Start-FlaskBackend
Start-Sleep -Seconds 3

# Start frontend
Start-VueFrontend
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Both services are starting up..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "- Vue.js Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "- Flask Backend:   http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "The Vue frontend will proxy API calls to the Flask backend." -ForegroundColor Gray
Write-Host "Both terminals will remain open for monitoring logs." -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this script (services will continue running)..." -ForegroundColor Green

# Wait for user input
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
