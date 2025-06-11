# Coolify Deployment Guide

This guide shows how to deploy the Bazos Ad Tracker on Coolify with HTTPS support.

## 🚀 Quick Deployment

### 1. Create New Application in Coolify

1. **Login to Coolify** and create a new application
2. **Choose "Git Repository"** as source
3. **Connect your repository** (GitHub/GitLab/etc.)
4. **Select branch**: `main` (or your preferred branch)

### 2. Configure Build Settings

**Build Pack**: `Docker`
**Dockerfile Path**: `./dockerfile` (default)
**Build Context**: `.` (root directory)

### 3. Environment Variables

Copy the variables from `.env.coolify` to your Coolify environment:

```bash
# Required
PORT=5000
HOST=0.0.0.0
FLASK_ENV=production
FLASK_DEBUG=false

# Application
CHECK_INTERVAL=300
FLASK_HTTPS=false

# Performance (optional)
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=120
```

### 4. Port Configuration

- **Application Port**: `5000`
- **Public Port**: Will be auto-assigned by Coolify
- **Protocol**: `HTTP` (Coolify handles HTTPS termination)

### 5. Domain & HTTPS

1. **Add your domain** in Coolify settings
2. **Enable "Force HTTPS"** (recommended)
3. Coolify will automatically handle SSL certificates

### 6. Persistent Storage (Optional)

Add persistent volumes for data storage:

```yaml
/app/data -> /data/bazos-tracker
/app/logs -> /logs/bazos-tracker
```

## ⚙️ Scheduler Architecture

The app uses a **dual-process architecture** for production:

### **Web Application Process**
- Handles HTTP requests and WebSocket connections
- Serves the Vue.js frontend
- Provides API endpoints
- Runs on Gunicorn with multiple workers

### **Scheduler Process** 
- Runs independently as background service
- Checks for new ads every 5 minutes (configurable)
- Writes notifications to shared file system
- Prevents conflicts with Gunicorn worker processes

### **Communication**
- **File-based**: Scheduler writes to `data/notifications.json`
- **HTTP Polling**: Frontend polls `/api/notifications` every 30s
- **WebSocket Fallback**: Real-time updates when Socket.IO works
- **Dual Strategy**: Ensures reliability in all environments

## 🔧 Advanced Configuration

### Resource Limits

Recommended for production:
- **Memory**: 512MB limit, 256MB reserved
- **CPU**: 0.5 cores limit, 0.25 cores reserved

### Health Checks

Coolify will automatically use the built-in health check:
- **Endpoint**: `/api/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

### Environment-Specific Settings

**Development:**
```bash
FLASK_ENV=development
FLASK_DEBUG=true
CHECK_INTERVAL=60
```

**Production:**
```bash
FLASK_ENV=production
FLASK_DEBUG=false
CHECK_INTERVAL=300
```

## 🌐 HTTPS & WebSocket Configuration

The app is fully compatible with:
- ✅ **HTTPS termination** at Coolify level
- ✅ **WebSocket proxying** through Coolify
- ✅ **Auto SSL certificates** via Let's Encrypt
- ✅ **Force HTTPS redirects**

### Frontend Configuration

The Vue.js frontend automatically detects:
- Protocol (HTTP/HTTPS) from browser
- WebSocket connection (WS/WSS) based on protocol
- API endpoints through Coolify's reverse proxy

## 🐛 Troubleshooting

### Common Issues

**1. App doesn't start:**
- Check logs in Coolify dashboard
- Verify PORT environment variable is set
- Ensure Dockerfile builds successfully

**2. WebSocket connection fails:**
- Enable WebSocket support in Coolify
- Check that Socket.IO can connect through proxy
- Verify no firewall blocking connections

**3. Data not persisting:**
- Add persistent volumes for `/app/data`
- Check container logs for file permission issues

**4. High memory usage:**
- Reduce GUNICORN_WORKERS to 1-2
- Lower CHECK_INTERVAL if needed
- Monitor resource usage in Coolify

### Debug Commands

Access container shell:
```bash
# Check if app is running
curl http://localhost:5000/api/health

# View application logs
tail -f /app/logs/scraper.log

# Check environment variables
env | grep -E "(PORT|HOST|FLASK_)"
```

## 📊 Monitoring

The app provides several monitoring endpoints:

- **Health**: `/api/health` - Container health status
- **Stats**: `/api/stats` - Application statistics
- **Manual Check**: `/api/manual-check` - Trigger manual scan

### Metrics Available

```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "scraper": "ok", 
    "scheduler": "ok"
  },
  "stats": {
    "keywords_count": 5,
    "total_ads": 127,
    "uptime": 86400
  }
}
```

## 🔄 Deployment Workflow

1. **Push to repository** (auto-deploys if configured)
2. **Coolify builds** Docker image
3. **Health check** validates deployment
4. **Traffic routes** to new container
5. **Old container** shuts down gracefully

## 🆘 Support

If you encounter issues:

1. Check Coolify deployment logs
2. Review application logs at `/api/health`
3. Verify environment variables are set correctly
4. Test locally with `docker-compose up`
