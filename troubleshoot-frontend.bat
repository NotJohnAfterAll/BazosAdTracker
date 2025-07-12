@echo off
REM Troubleshooting script for npm/rollup issues on Windows
REM Run this script to diagnose frontend build problems

echo 🔍 BazosChecker Frontend Build Troubleshooter (Windows)
echo =======================================================

cd frontend
if %errorlevel% neq 0 (
    echo ❌ Could not change to frontend directory
    exit /b 1
)

echo 📋 System Information:
node --version
npm --version
echo Platform: Windows
echo Architecture: %PROCESSOR_ARCHITECTURE%
echo.

echo 📦 Package Information:
if exist package.json (
    echo package.json exists ✅
    echo Dependencies with 'rollup':
    findstr /i rollup package.json
    if %errorlevel% neq 0 echo No rollup dependencies found
) else (
    echo package.json missing ❌
)
echo.

echo 🔧 NPM Configuration:
if exist .npmrc (
    echo .npmrc exists ✅
    type .npmrc
) else (
    echo .npmrc missing - creating one...
    (
        echo target_platform=linux
        echo target_arch=x64
        echo optional=true
        echo package-lock=false
        echo save-exact=true
        echo fetch-timeout=300000
        echo fetch-retries=3
    ) > .npmrc
    echo .npmrc created ✅
)
echo.

echo 🧹 Cleaning existing installation:
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
echo Cleaned node_modules and package-lock.json ✅
echo.

echo 📥 Testing npm install strategies:

REM Strategy 1: CI with platform flags
echo Strategy 1: npm ci with platform flags
npm ci --platform=linux --arch=x64 --no-optional >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Success with platform flags
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Build successful
        exit /b 0
    ) else (
        echo ❌ Build failed
    )
) else (
    echo ❌ Failed with platform flags
    if exist node_modules rmdir /s /q node_modules
    if exist package-lock.json del package-lock.json
)

REM Strategy 2: CI without platform flags
echo Strategy 2: npm ci without platform flags
npm ci --no-optional >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Success without platform flags
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Build successful
        exit /b 0
    ) else (
        echo ❌ Build failed
    )
) else (
    echo ❌ Failed without platform flags
    if exist node_modules rmdir /s /q node_modules
    if exist package-lock.json del package-lock.json
)

REM Strategy 3: Regular install with platform
echo Strategy 3: npm install with platform flags
npm install --platform=linux --arch=x64 --no-optional >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Success with install + platform flags
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Build successful
        exit /b 0
    ) else (
        echo ❌ Build failed
    )
) else (
    echo ❌ Failed with install + platform flags
    if exist node_modules rmdir /s /q node_modules
    if exist package-lock.json del package-lock.json
)

REM Strategy 4: Regular install without optional
echo Strategy 4: npm install without optional deps
npm install --no-optional >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Success without optional deps
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Build successful
        exit /b 0
    ) else (
        echo ❌ Build failed
    )
) else (
    echo ❌ Failed without optional deps
    if exist node_modules rmdir /s /q node_modules
    if exist package-lock.json del package-lock.json
)

REM Strategy 5: Force install
echo Strategy 5: npm install with --force
npm install --force >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Success with --force
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Build successful
        exit /b 0
    ) else (
        echo ❌ Build failed
    )
) else (
    echo ❌ Failed with --force
)

echo.
echo ❌ All strategies failed!
echo 💡 Troubleshooting suggestions:
echo 1. Try using a different Node.js version (18, 20, or latest)
echo 2. Clear npm cache: npm cache clean --force
echo 3. Try using yarn instead of npm
echo 4. Check if you're behind a corporate firewall/proxy
echo 5. Try building on a different machine/platform
echo.
echo 🔍 For more help, check the README troubleshooting section
