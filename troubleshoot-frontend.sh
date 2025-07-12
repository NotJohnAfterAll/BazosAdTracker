#!/bin/bash

# Troubleshooting script for npm/rollup issues
# Run this script to diagnose frontend build problems

echo "🔍 BazosChecker Frontend Build Troubleshooter"
echo "============================================="

cd frontend || exit 1

echo "📋 System Information:"
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "Platform: $(uname -a)"
echo "Architecture: $(uname -m)"
echo ""

echo "📦 Package Information:"
if [ -f package.json ]; then
    echo "package.json exists ✅"
    echo "Dependencies with 'rollup':"
    grep -i rollup package.json || echo "No rollup dependencies found"
else
    echo "package.json missing ❌"
fi
echo ""

echo "🔧 NPM Configuration:"
if [ -f .npmrc ]; then
    echo ".npmrc exists ✅"
    cat .npmrc
else
    echo ".npmrc missing - creating one..."
    cat > .npmrc << 'EOF'
target_platform=linux
target_arch=x64
optional=true
package-lock=false
save-exact=true
fetch-timeout=300000
fetch-retries=3
EOF
    echo ".npmrc created ✅"
fi
echo ""

echo "🧹 Cleaning existing installation:"
rm -rf node_modules package-lock.json
echo "Cleaned node_modules and package-lock.json ✅"
echo ""

echo "📥 Testing npm install strategies:"

# Strategy 1: CI with platform flags
echo "Strategy 1: npm ci with platform flags"
if npm ci --platform=linux --arch=x64 --no-optional; then
    echo "✅ Success with platform flags"
    npm run build && echo "✅ Build successful" || echo "❌ Build failed"
    exit 0
else
    echo "❌ Failed with platform flags"
    rm -rf node_modules package-lock.json
fi

# Strategy 2: CI without platform flags
echo "Strategy 2: npm ci without platform flags"
if npm ci --no-optional; then
    echo "✅ Success without platform flags"
    npm run build && echo "✅ Build successful" || echo "❌ Build failed"
    exit 0
else
    echo "❌ Failed without platform flags"
    rm -rf node_modules package-lock.json
fi

# Strategy 3: Regular install with platform
echo "Strategy 3: npm install with platform flags"
if npm install --platform=linux --arch=x64 --no-optional; then
    echo "✅ Success with install + platform flags"
    npm run build && echo "✅ Build successful" || echo "❌ Build failed"
    exit 0
else
    echo "❌ Failed with install + platform flags"
    rm -rf node_modules package-lock.json
fi

# Strategy 4: Regular install without optional
echo "Strategy 4: npm install without optional deps"
if npm install --no-optional; then
    echo "✅ Success without optional deps"
    npm run build && echo "✅ Build successful" || echo "❌ Build failed"
    exit 0
else
    echo "❌ Failed without optional deps"
    rm -rf node_modules package-lock.json
fi

# Strategy 5: Force install
echo "Strategy 5: npm install with --force"
if npm install --force; then
    echo "✅ Success with --force"
    npm run build && echo "✅ Build successful" || echo "❌ Build failed"
    exit 0
else
    echo "❌ Failed with --force"
fi

echo ""
echo "❌ All strategies failed!"
echo "💡 Troubleshooting suggestions:"
echo "1. Try using a different Node.js version (18, 20, or latest)"
echo "2. Clear npm cache: npm cache clean --force"
echo "3. Try using yarn instead of npm"
echo "4. Check if you're behind a corporate firewall/proxy"
echo "5. Try building on a different machine/platform"
echo ""
echo "🔍 For more help, check the logs above and the README troubleshooting section"
