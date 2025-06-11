# Production Deployment Fix for BazosChecker

## 🚨 Issue Fixed
The app was stuck in a restart loop because it was trying to use Flask's development server (Werkzeug) in production mode, which is not allowed.

## ✅ Solutions Applied

### 1. Updated app.py
- Added `allow_unsafe_werkzeug=True` for production mode
- Better production vs development detection
- Cleaner error handling

### 2. Added Gunicorn Support
- Updated `requirements.txt` to include `gunicorn`
- Created `wsgi.py` for proper WSGI deployment

## 🚀 Production Deployment Options

### Option 1: Quick Fix (Current)
The app now runs with the updated code that allows Werkzeug in production:
```bash
# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here

# Run the app
python app.py
```

### Option 2: Proper Production (Recommended)
Use Gunicorn for better performance and stability:

```bash
# Install Gunicorn (already in requirements.txt)
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app

# Or with more options
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --timeout 120 --keep-alive 5 app:app
```

### Option 3: Docker/Coolify Deployment
Update your Docker CMD or Coolify start command to:
```dockerfile
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🔧 Environment Variables for Production

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
CHECK_INTERVAL=300
FLASK_DEBUG=false
```

## 📋 Deployment Checklist

1. ✅ **Fixed app restart loop** - Updated production server handling
2. ✅ **Added Gunicorn support** - Better production server option
3. ✅ **WebSocket configuration** - Cloudflare-compatible settings
4. ✅ **Environment detection** - Proper prod vs dev handling

## 🎯 Next Steps

1. **Deploy the updated code** to your server
2. **Choose deployment method**:
   - Quick: Use updated `python app.py` (fixed)
   - Better: Use `gunicorn` command above
3. **Start the scheduler separately** in production:
   ```bash
   python scheduler.py &
   ```

## 🐛 Troubleshooting

If you still see issues:

1. **Check logs** for the actual error
2. **Verify environment variables** are set correctly
3. **Use Gunicorn** instead of direct Flask for production
4. **Ensure only one instance** is running (kill any existing processes)

The restart loop should now be fixed! 🎉
