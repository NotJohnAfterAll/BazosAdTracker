# Cloudflare Configuration Guide for BazosChecker

## WebSocket Issues with Cloudflare

Cloudflare has specific requirements for WebSocket connections that can cause issues with Socket.IO. Here's how we've configured the app to work with Cloudflare:

## Backend Configuration (Already Applied)

### Socket.IO Server Settings
- **Transports**: Set to `['polling']` only (no WebSockets initially)
- **Upgrade**: Disabled (`allow_upgrades=False`)
- **Timeouts**: Increased for Cloudflare (ping_timeout=120s, ping_interval=60s)
- **CORS**: Configured for your domain `bazos.notjohn.net`

### Production Environment Detection
The app automatically detects production environment and applies Cloudflare-friendly settings.

## Frontend Configuration (Already Applied)

### Vue.js Frontend
- **Transports**: `['polling']` only
- **Upgrade**: Disabled
- **Reconnection**: Enhanced with more attempts and longer delays
- **Timeouts**: Increased for Cloudflare compatibility

### Static JavaScript
- Same polling-only configuration for consistency

## Cloudflare Dashboard Configuration

You need to configure these settings in your Cloudflare dashboard:

### 1. WebSocket Support
- Go to **Network** tab in Cloudflare dashboard
- Enable **WebSockets** (even though we're using polling, this helps with connection stability)

### 2. SSL/TLS Settings
- Set SSL/TLS encryption mode to **Full (strict)** or **Full**
- Enable **Always Use HTTPS**

### 3. Page Rules (Optional but Recommended)
Create a page rule for `bazos.notjohn.net/socket.io/*`:
- **Browser Cache TTL**: Bypass
- **Cache Level**: Bypass
- **Disable Performance**: On (to avoid caching Socket.IO requests)

### 4. Speed Settings
- **Auto Minify**: Disable for JavaScript (can break Socket.IO)
- **Rocket Loader**: Disable (can interfere with real-time connections)

## Testing the Configuration

### 1. Test Socket.IO Connection
Visit: `https://bazos.notjohn.net/test-socket`

This page will:
- Test the Socket.IO connection with your exact configuration
- Show connection status and transport method
- Log all connection events
- Verify that polling works correctly

### 2. Check Browser Console
In your browser's developer tools, you should see:
```
🔍 Socket.IO connecting to: https://bazos.notjohn.net
✅ Socket connected via: polling
```

## Troubleshooting

### If Connection Still Fails:

1. **Check Cloudflare Firewall**
   - Ensure your server IP is not blocked
   - Check security level (should be "Medium" or lower)

2. **Verify DNS Settings**
   - Ensure A record points to your server
   - Orange cloud should be enabled for CDN benefits

3. **Server Logs**
   - Check your server logs for CORS errors
   - Verify the app is binding to the correct port

4. **Browser Network Tab**
   - Check if `/socket.io/` requests are reaching the server
   - Look for 404 or 502 errors

### Common Issues:

1. **502 Bad Gateway**: Server not responding - check if app is running
2. **CORS Errors**: Domain not in allowed origins - verify CORS settings
3. **Timeout Errors**: Increase timeout values further if needed

## Production Deployment Commands

```powershell
# Start the app in production mode
$env:FLASK_ENV="production"
$env:SECRET_KEY="your-secret-key-here"
python app.py

# Or use Gunicorn for production
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

## Environment Variables for Production

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
CHECK_INTERVAL=300
FLASK_DEBUG=false
```

## Next Steps

1. **Deploy the updated code** to your server
2. **Configure Cloudflare settings** as described above
3. **Test the connection** using the test page
4. **Monitor the logs** for any remaining issues

The current configuration prioritizes **stability over performance** by using polling instead of WebSockets. Once the connection is stable, you can gradually re-enable WebSocket upgrades by changing:

Backend: `transports=['polling', 'websocket']` and `allow_upgrades=True`
Frontend: `transports: ['polling', 'websocket']` and `upgrade: true`
