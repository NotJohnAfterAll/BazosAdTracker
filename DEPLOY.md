# BazosChecker - Complete Coolify Deployment Guide

## Overview
This guide will deploy BazosChecker with both Flask app and scheduler running in a single container, with automatic file monitoring to ensure real-time updates.

## Prerequisites
- Coolify instance running
- Git repository connected to Coolify
- Domain name (optional, but recommended)

## Step 1: Environment Variables in Coolify

### Required Environment Variables
Set these in your Coolify application settings:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
HOST=0.0.0.0

# Python Configuration
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

# Application Settings
CHECK_INTERVAL=300  # Check every 5 minutes (300 seconds)
MAX_ADS_PER_KEYWORD=50
ENABLE_NOTIFICATIONS=true
LOG_LEVEL=INFO
```

### Optional Environment Variables
```bash
# Custom scheduler settings
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL=300  # 5 minutes

# File monitoring
FILE_MONITOR_INTERVAL=5  # Check files every 5 seconds

# Debug mode (set to 'true' for troubleshooting)
DEBUG_MODE=false
```

## Step 2: Coolify Application Configuration

### Build Settings
- **Build Pack**: Docker
- **Dockerfile Path**: `dockerfile`
- **Build Command**: (leave empty, Docker handles it)
- **Start Command**: (leave empty, uses CMD from Dockerfile)

### Port Configuration
- **Port**: `5000`
- **Protocol**: HTTP
- **Public Port**: 80 (or 443 for HTTPS)

### Health Check
- **Path**: `/api/health`
- **Port**: `5000`
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3

## Step 3: Deploy to Coolify

### Option A: Connect Git Repository
1. **Add Git Repository** in Coolify:
   - Repository URL: `https://github.com/yourusername/bazos-checker`
   - Branch: `main` (or your default branch)
   - Build Pack: Docker

2. **Deploy**:
   - Click "Deploy" in Coolify
   - Monitor build logs
   - Wait for deployment to complete

### Option B: Manual Deployment
```bash
# 1. Commit and push your changes
git add .
git commit -m "Production deployment with scheduler fix"
git push origin main

# 2. Trigger deployment in Coolify (if auto-deploy is disabled)
# Go to your Coolify dashboard and click "Deploy"
```

## Step 4: Configure Domain (Optional)

### Custom Domain Setup
1. **Add Domain** in Coolify:
   - Domain: `your-bazos-checker.com`
   - Enable HTTPS: Yes
   - Force HTTPS: Yes

2. **DNS Configuration**:
   - Add A record: `your-bazos-checker.com` → Your server IP
   - Add CNAME: `www.your-bazos-checker.com` → `your-bazos-checker.com`

### Cloudflare Setup (if using Cloudflare)
```bash
# Cloudflare settings for WebSocket support
Proxy status: Proxied (orange cloud)
SSL/TLS mode: Full (strict)
WebSocket: Enabled (under Network tab)
```

## Step 5: Verify Deployment

### 1. Check Application Status
Visit your application URL and verify:
- ✅ Frontend loads correctly
- ✅ Can add keywords
- ✅ Manual checks work
- ✅ WebSocket connection established

### 2. Monitor Logs
In Coolify, check application logs for:
```
🚀 Starting BazosChecker production processes...
Scheduler started with PID: 123
Flask app started with PID: 456
🔍 Starting file monitoring for production...
 * Running on http://0.0.0.0:5000
```

### 3. Test Automatic Updates
```bash
# Check debug endpoint
curl https://your-domain.com/api/debug

# Expected response:
{
  "status": "healthy",
  "file_monitoring": true,
  "scheduler_running": true,
  "flask_app_running": true,
  "data_files": {
    "keywords": "exists",
    "ads": "exists"
  }
}
```

## Step 6: Configure Scheduler Settings

### Default Scheduler Configuration
The scheduler runs automatically with these settings:
- **Check Interval**: 5 minutes (300 seconds)
- **Max Ads per Keyword**: 50
- **Notifications**: Enabled
- **File Monitoring**: Active

### Custom Scheduler Configuration
To modify scheduler behavior, update these environment variables in Coolify:

```bash
# Change check interval to 10 minutes
CHECK_INTERVAL=600

# Increase max ads per keyword
MAX_ADS_PER_KEYWORD=100

# Disable notifications
ENABLE_NOTIFICATIONS=false
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Scheduler Not Running
**Symptoms**: Manual checks work, but no automatic updates
**Check**: Application logs for scheduler startup
**Solution**: Verify `start.sh` has execute permissions and environment variables are set

#### 2. Frontend Not Updating
**Symptoms**: New ads found but don't appear on frontend
**Check**: Visit `/api/debug` endpoint
**Solution**: Ensure file monitoring is active and WebSocket connection works

#### 3. Build Failures
**Symptoms**: Coolify build fails
**Common causes**:
- Missing `start.sh` execute permission
- Frontend build errors
- Python dependency issues

**Solution**:
```bash
# Check Dockerfile for proper permissions
RUN chmod +x start.sh

# Verify all files are committed
git status
git add .
git commit -m "Fix permissions"
```

#### 4. WebSocket Connection Issues
**Symptoms**: Real-time updates don't work
**Check**: Browser console for WebSocket errors
**Solutions**:
- Ensure port 5000 is properly exposed
- Check Cloudflare WebSocket settings
- Verify CORS configuration

### Debug Commands
```bash
# Check running processes in container
ps aux | grep python

# Check file permissions
ls -la start.sh

# Monitor logs in real-time
tail -f logs/flask.log logs/scheduler.log

# Test API endpoints
curl https://your-domain.com/api/health
curl https://your-domain.com/api/debug
curl https://your-domain.com/api/recent-ads
```

## Production Checklist

### Before Deployment
- [ ] All environment variables configured in Coolify
- [ ] Git repository connected and up-to-date
- [ ] Domain name configured (if using custom domain)
- [ ] Health check endpoint configured

### After Deployment
- [ ] Application accessible via URL
- [ ] Both Flask app and scheduler running in logs
- [ ] File monitoring active (`/api/debug` shows `file_monitoring: true`)
- [ ] Manual keyword checks work
- [ ] Automatic scheduler runs every 5 minutes
- [ ] New ads appear automatically without refresh
- [ ] WebSocket notifications working

### Monitoring
- [ ] Set up Coolify alerts for application downtime
- [ ] Monitor disk usage (logs and data files)
- [ ] Check application logs regularly
- [ ] Verify scheduler is finding new ads

## File Structure in Production
```
/app/
├── data/
│   ├── keywords.json      # User keywords
│   ├── ads.json          # Found ads
│   └── stats.json        # Statistics
├── logs/
│   ├── flask.log         # Flask application logs
│   ├── scheduler.log     # Scheduler logs
│   └── supervisord.log   # Process manager logs
├── notifications/        # Notification files
├── frontend/dist/        # Built frontend files
└── ...                  # Application files
```

## Success Indicators
When everything is working correctly:
- ✅ Coolify shows application as "Running"
- ✅ Health check endpoint returns 200 OK
- ✅ Both processes appear in application logs  
- ✅ File monitoring is active
- ✅ Scheduler runs automatically every 5 minutes
- ✅ New ads appear on frontend without manual refresh
- ✅ Real-time notifications work via WebSocket
- ✅ Manual checks still work instantly

Your BazosChecker is now fully deployed and operational! 🎉
