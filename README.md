# Bazos Ad Tracker

A comprehensive web application for monitoring classified ads on Bazos.cz. Track keywords, get notifications for new ads, manage favorites, and never miss a deal again.

## Features

### Core Functionality
- **Multi-user Support**: Multiple users can track different keywords independently
- **Real-time Ad Monitoring**: Automated scraping of Bazos.cz for new ads
- **Smart Keyword Management**: Add/remove keywords with instant feedback
- **Ad Resurrection**: Automatically restores ads that temporarily disappear and reappear
- **Favorites System**: Mark important ads as favorites for quick access
- **Advanced Search**: Filter ads by date, keyword, status, and more

### User Experience
- **Modern SPA Interface**: Built with Vue.js and Tailwind CSS
- **Responsive Design**: Works perfectly on desktop and mobile
- **Real-time Updates**: Live notifications for new ads
- **Sound Alerts**: Audio notifications for important events
- **Visual Indicators**: "NEW" tags, deleted ad markers, loading states
- **Smart Navigation**: Seamless routing between dashboard sections

### Data Management
- **Database-Driven**: SQLite for development, PostgreSQL for production
- **Automated Cleanup**: Removes old deleted ads and expired "NEW" tags
- **Data Persistence**: All user data survives server restarts
- **Export Capabilities**: View and manage all tracked data

## Technology Stack

### Backend
- **Python 3.12+** with Flask
- **SQLAlchemy** for database ORM
- **APScheduler** for background job scheduling
- **BeautifulSoup4** for web scraping
- **SQLite/PostgreSQL** for data storage

### Frontend
- **Vue.js 3** with Composition API
- **Vite** for fast development and building
- **Tailwind CSS** for modern styling
- **TypeScript** for type safety

### Infrastructure
- **Docker** for containerization
- **Nginx** for reverse proxy (production)
- **Cloudflare** for CDN and SSL (production)

## Quick Start

### Development Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd BazosCheckerCopilot
   ```

2. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create environment file
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev  # Development server
   ```

4. **Start the Backend**
   ```bash
   # In the root directory
   python app.py
   ```

5. **Access the Application**
   - Backend API: http://localhost:5000
   - Frontend (dev): http://localhost:5173
   - Combined (production): http://localhost:5000

### Environment Configuration

Create a `.env` file in the root directory:

```env
# Application Settings
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=development

# Database (leave empty for SQLite)
DATABASE_URL=

# Optional: Custom scheduling intervals (in seconds)
SCHEDULER_INTERVAL=300

# Optional: Logging level
LOG_LEVEL=INFO
```

## Deployment

### Production Deployment with Docker

1. **Prepare Environment**
   ```bash
   # Create production environment file
   cp .env.example .env.production
   
   # Edit with production settings:
   # - Strong SECRET_KEY
   # - PostgreSQL DATABASE_URL
   # - FLASK_ENV=production
   ```

2. **Build and Deploy**
   ```bash
   # Build the application
   docker-compose up --build -d
   
   # Check status
   docker-compose ps
   docker-compose logs
   ```

3. **Database Initialization**
   ```bash
   # The database will be automatically initialized on first run
   # Check logs to ensure successful initialization
   docker-compose logs app
   ```

### Production Environment Variables

```env
# Required for production
SECRET_KEY=very-strong-secret-key-here
JWT_SECRET_KEY=very-strong-jwt-secret-key-here
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@db:5432/bazos_tracker

# Optional production settings
SCHEDULER_INTERVAL=300
LOG_LEVEL=WARNING
```

### Coolify/Cloudflare Deployment

1. **Platform Setup**
   - Connect your repository to Coolify
   - Set up PostgreSQL database service
   - Configure environment variables

2. **PostgreSQL Database Setup in Coolify**
   
   **Step 1: Create PostgreSQL Service**
   - In your Coolify project, click "Add Service"
   - Select "Database" → "PostgreSQL"
   - Configure the following:
     ```
     Service Name: bazos-postgres
     Database Name: bazos_tracker
     Username: bazos_user
     Password: <generate-strong-password>
     Version: 15 (recommended)
     ```
   
   **Step 2: Get Connection Details**
   After the database is created, Coolify will provide:
   - **Internal hostname**: `bazos-postgres` (service name)
   - **Port**: `5432`
   - **Database**: `bazos_tracker`
   - **Username**: `bazos_user`
   - **Password**: The one you set above
   
   **Step 3: Construct DATABASE_URL**
   Your DATABASE_URL will be:
   ```
   postgresql://bazos_user:your-password@bazos-postgres:5432/bazos_tracker
   ```

3. **Required Environment Variables**
   ```env
   SECRET_KEY=<generated-secret-32-chars>
   JWT_SECRET_KEY=<generated-jwt-secret-32-chars>
   DATABASE_URL=postgresql://bazos_user:your-password@bazos-postgres:5432/bazos_tracker
   FLASK_ENV=production
   ```

4. **Build Configuration**
   - Build command: `./deploy.sh`
   - Port: `5000`
   - Health check: `/api/health`

> **Note**: The Dockerfile uses Debian-based Node.js 20 image and robust npm install strategies to avoid Rollup native dependency issues. If you encounter build issues, use the included troubleshooting scripts (`troubleshoot-frontend.sh` for Unix or `troubleshoot-frontend.bat` for Windows).

## User Guide

### Getting Started

1. **Create an Account**
   - Navigate to the registration page
   - Choose a secure password (8+ chars, mixed case, numbers)
   - Complete email verification if enabled

2. **Add Keywords**
   - Go to the Keywords tab
   - Add keywords you want to monitor (e.g., "iphone", "guitar")
   - Keywords are checked automatically every 5 minutes

3. **Monitor Ads**
   - **Recent Ads**: View all newly found ads
   - **Changes**: See what's new or removed
   - **Favorites**: Mark important ads for easy access
   - **Keywords**: Manage your tracked search terms

### Features Explained

#### Ad States
- **NEW**: Recently found ads (disappear after 6 hours)
- **ACTIVE**: Currently available on Bazos.cz
- **DELETED**: No longer available (grayed out)
- **FAVORITE**: Marked by user (star icon)

#### Smart Features
- **Auto-Resurrection**: Ads that temporarily disappear and reappear are automatically restored
- **Duplicate Detection**: Same ad won't be shown multiple times
- **Intelligent Cleanup**: Old deleted ads are permanently removed after 30 days
- **Sound Notifications**: Audio alerts for new ads and user actions

#### Advanced Options
- **Filter by Status**: Show/hide deleted ads
- **Adjustable Limits**: Display 20-500 recent ads
- **Keyword Management**: Enable/disable keywords without deleting
- **Export Data**: View raw data for analysis

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### User Data Endpoints
- `GET /api/user/keywords` - List user keywords
- `POST /api/user/keywords` - Add new keyword
- `DELETE /api/user/keywords/<id>` - Remove keyword
- `PATCH /api/user/keywords/<id>` - Update keyword status

### Ad Management Endpoints
- `GET /api/user/ads/recent` - Get recent ads
- `GET /api/user/ads/changes` - Get new/deleted ads
- `POST /api/user/ads/<id>/favorite` - Toggle favorite status
- `GET /api/user/manual-check` - Trigger manual ad check

### System Endpoints
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics

## Database Schema

### Core Tables
- **users**: User accounts and authentication
- **user_keywords**: Keywords tracked by each user
- **user_ads**: Ads found for each user/keyword combination
- **user_favorites**: User's favorite ads
- **user_stats**: User activity statistics

### Key Features
- **Automatic Initialization**: Database and tables created on first run
- **Migration Safe**: Schema updates handled automatically
- **Multi-user Isolation**: Complete data separation between users
- **Optimized Queries**: Indexed for fast lookups and filtering

## Maintenance

### Regular Tasks
- **Database Cleanup**: Automatically removes old deleted ads (30+ days)
- **NEW Tag Cleanup**: Removes expired "NEW" tags (6+ hours)
- **Log Rotation**: Manage application log files
- **Health Monitoring**: Check system status via `/api/health`

### Troubleshooting

#### Common Issues

1. **Ads Not Updating**
   ```bash
   # Check scheduler status
   curl http://localhost:5000/api/health
   
   # Manual check
   curl http://localhost:5000/api/user/manual-check
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose logs db
   
   # Verify connection string
   echo $DATABASE_URL
   ```

3. **Frontend Build Issues**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Docker Build Issues (Rollup/Alpine)**
   - Error: `Cannot find module @rollup/rollup-linux-x64-musl`
   - Solution: The Dockerfile uses Debian instead of Alpine to avoid this issue
   - If building locally on Alpine: `npm ci --platform=linux --arch=x64`

#### Performance Optimization
- **Database Indexing**: Automatically applied to key columns
- **Connection Pooling**: Managed by SQLAlchemy
- **Static File Serving**: Use CDN in production
- **Rate Limiting**: Built-in scraping delays

### Backup and Recovery

#### Database Backup
```bash
# SQLite (development)
cp data/bazos.db data/bazos.db.backup

# PostgreSQL (production)
pg_dump $DATABASE_URL > backup.sql
```

#### Data Recovery
```bash
# Restore SQLite
cp data/bazos.db.backup data/bazos.db

# Restore PostgreSQL
psql $DATABASE_URL < backup.sql
```

## Development

### Project Structure
```
├── app.py                 # Main Flask application
├── scheduler.py          # Background job scheduler
├── app/
│   ├── models.py         # Database models
│   ├── user_service.py   # User business logic
│   ├── auth.py          # Authentication handlers
│   └── utils/
│       └── bazos_scraper_fixed.py  # Web scraper
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue.js components
│   │   ├── views/       # Page components
│   │   └── assets/      # Static assets
│   └── public/          # Public assets
├── data/                # Database and logs (gitignored)
├── docker-compose.yml   # Docker configuration
└── requirements.txt     # Python dependencies
```

### Adding New Features

1. **Backend Changes**
   - Update models in `app/models.py`
   - Add business logic to `app/user_service.py`
   - Create API endpoints in `app.py`

2. **Frontend Changes**
   - Create components in `frontend/src/components/`
   - Add views in `frontend/src/views/`
   - Update routing as needed

3. **Database Changes**
   - Modify models and run with auto-migration
   - Test with both SQLite and PostgreSQL

### Testing
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm run test

# Integration tests
npm run test:e2e
```

## Security

### Authentication
- **Password Requirements**: 8+ characters, mixed case, numbers
- **Session Management**: Secure session cookies
- **CSRF Protection**: Built-in Flask-WTF protection
- **SQL Injection**: Protected by SQLAlchemy ORM

### Data Protection
- **User Isolation**: Complete data separation
- **Input Validation**: All user inputs validated
- **Rate Limiting**: Scraping delays to respect target site
- **Secure Headers**: Production security headers

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

### Getting Help
- Check this README for common issues
- Review the troubleshooting section
- Check application logs for error details
- Verify environment configuration

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Changelog

#### v2.0.0 (Current)
- **Database Migration**: Complete migration from JSON to database storage
- **Multi-user Support**: Full user account system with authentication
- **Ad Resurrection**: Automatic restoration of temporarily missing ads
- **Enhanced UI**: Modern Vue.js SPA with real-time updates
- **Smart Cleanup**: Automated maintenance of old data
- **Production Ready**: Docker deployment with PostgreSQL support

#### v1.0.0 (Legacy)
- Basic ad monitoring with JSON file storage
- Single-user functionality
- Simple web interface

---

**Built with ❤️ for the Bazos.cz community**
- **Vue 3**: Modern reactive framework with Composition API
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Pinia**: State management
- **Socket.IO Client**: Real-time updates
- **Responsive Design**: Mobile-first approach

## 🚀 Quick Deployment (Coolify)

### 1. PostgreSQL Database Setup
1. **Create Database Service**:
   - Go to your Coolify project
   - Click "Add Service" → "Database" → "PostgreSQL"
   - Set these values:
     ```
     Service Name: bazos-postgres
     Database Name: bazos_tracker
     Username: bazos_user
     Password: [generate strong password]
     Version: 15
     ```

2. **Note the Connection Details**:
   - Hostname: `bazos-postgres` (internal service name)
   - Port: `5432`
   - Database: `bazos_tracker`
   - Username: `bazos_user`

### 2. Environment Variables
Set these in your Coolify application:

```bash
# Required - Security (generate strong random strings)
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_SECRET_KEY=your-jwt-secret-key-different-from-above

# Database (use your PostgreSQL service details)
DATABASE_URL=postgresql://bazos_user:your-password@bazos-postgres:5432/bazos_tracker

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
CHECK_INTERVAL=300
PORT=5000
HOST=0.0.0.0

# Optional
MAX_ADS_PER_KEYWORD=50
LOG_LEVEL=INFO
```

### 3. Application Deployment
1. **Add Application Service**:
   - Click "Add Service" → "Application"
   - Connect your Git repository
   - Set build command: `./deploy.sh`
   - Set port: `5000`
   - Set health check: `/api/health`

2. **Deploy**:
   - Click Deploy
   - Wait for build to complete
   - Database tables will be created automatically
   - Visit your domain and create your first account!

### 🗄️ Database Creation
- **Production**: PostgreSQL database is automatically provided by Coolify
- **Local Development**: SQLite database is automatically created in `data/` directory
- **No manual setup required** - just deploy and the database will be initialized
- **Migration included** - if upgrading from JSON version, data is automatically migrated

## 💻 Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite (for development)

### Setup

1. **Clone repository:**
```bash
git clone <your-repo-url>
cd BazosCheckerCopilot
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment:**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your local settings
```

4. **Initialize database:**
```bash
python init_db.py
```

5. **Build frontend:**
```bash
cd frontend
npm install
npm run build
cd ..
```

6. **Start development server:**
```bash
python app.py
```

Visit `http://localhost:5000` and create your account!

### Development Commands

```bash
# Start frontend dev server (with hot reload)
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build

# Run database migrations
python init_db.py

# Check migration status
python check_migration_status.py
```

## 🗄 Database Schema

### Core Tables
- **users**: User authentication and profiles
- **user_keywords**: Keywords tracked by each user
- **user_ads**: Ads found for user keywords (with new/deleted status)
- **user_favorites**: User's favorite ads
- **user_stats**: Personal usage statistics
- **user_sessions**: Secure session management

### Migration Features
- Automatic migration from JSON files to database
- Data integrity checks and validation
- Rollback capabilities if needed
- Performance optimizations

## 🔒 Security Features

### Implemented
✅ **Authentication**: JWT tokens with refresh mechanism  
✅ **Password Security**: Bcrypt hashing with salt  
✅ **Rate Limiting**: Protection against brute force attacks  
✅ **Data Isolation**: Complete separation between users  
✅ **SQL Injection Prevention**: SQLAlchemy ORM protection  
✅ **XSS Protection**: Secure headers and input validation  
✅ **CORS Configuration**: Proper cross-origin handling  

### Production Recommendations
- Use strong, unique SECRET_KEY and JWT_SECRET_KEY (32+ characters)
- Enable HTTPS (automatically handled by Coolify)
- Regular database backups
- Monitor logs for suspicious activity
- Keep dependencies updated

## 📱 API Documentation

### Authentication Endpoints
```bash
POST /api/auth/register    # Create new account
POST /api/auth/login       # User login
POST /api/auth/logout      # User logout
GET  /api/auth/me         # Get current user info
POST /api/auth/refresh    # Refresh JWT token
```

### User Data Endpoints
```bash
GET|POST /api/user/keywords              # Manage keywords
DELETE   /api/user/keywords/<keyword>    # Remove keyword
GET      /api/user/ads                   # Get user's ads
GET      /api/user/recent-ads           # Get recent ads
GET|POST /api/user/favorites            # Manage favorites
GET      /api/user/stats                # Get statistics
GET      /api/user/manual-check         # Trigger manual check
```

### System Endpoints
```bash
GET /api/health    # Application health check
GET /             # Serve frontend (catch-all)
```

## 🔧 Configuration

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Required | Flask secret key for sessions |
| `JWT_SECRET_KEY` | Required | JWT token signing key |
| `DATABASE_URL` | sqlite:///data/bazos_checker.db | Database connection URL |
| `CHECK_INTERVAL` | 300 | Ad checking interval in seconds |
| `MAX_ADS_PER_KEYWORD` | 50 | Maximum ads to store per keyword |
| `FLASK_ENV` | development | Flask environment |
| `LOG_LEVEL` | INFO | Logging level |
| `PORT` | 5000 | Server port |
| `HOST` | 127.0.0.1 | Server host |

## 🐛 Troubleshooting

### Common Issues

**Database connection failed:**
- Verify DATABASE_URL is correct
- Check database server is running
- Ensure proper credentials
- **For Coolify**: Make sure both app and database are in the same project
- **For Coolify**: Use internal service name (e.g., `bazos-postgres`) not external IP
- **For Coolify**: Check that database service is running in the Services tab

**Authentication not working:**
- Check SECRET_KEY and JWT_SECRET_KEY are set
- Verify tokens haven't expired
- Clear browser cookies/localStorage

**Frontend not loading:**
- Check if `frontend/dist` exists
- Run `npm run build` in frontend directory
- Verify static file serving

**Ads not updating:**
- Check scheduler is running in logs
- Verify keywords are properly added
- Test manual check functionality

**Sound alerts not working:**
- Check browser permissions for audio
- Verify notification.mp3 file exists
- Test in different browsers

**Docker build fails with Rollup native dependency errors:**
This is a known npm bug with optional dependencies. **This issue has been resolved** with the following improvements:

- ✅ **Updated to Node.js 20** with better dependency resolution
- ✅ **Added `.npmrc` configuration** to handle optional dependencies
- ✅ **Multi-strategy npm install** with automatic fallbacks
- ✅ **Comprehensive troubleshooting scripts** for both Unix and Windows

If you still encounter issues, try these solutions:

1. **Use the troubleshooting script:**
```bash
chmod +x troubleshoot-frontend.sh
./troubleshoot-frontend.sh
```

2. **Manual troubleshooting:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force

# Try these commands in order:
npm ci --platform=linux --arch=x64 --no-optional
# OR
npm install --no-optional
# OR
npm install --force
```

3. **Alternative Dockerfile:**
If the main build fails, try the alternative:
```bash
cp dockerfile.alternative dockerfile
docker build -t bazos-checker .
```

4. **Use different Node.js version:**
```bash
# In dockerfile, change the first line to:
FROM node:18-bullseye AS frontend-builder
# OR
FROM node:22-bullseye AS frontend-builder
```

5. **Use yarn instead of npm:**
```bash
cd frontend
rm package-lock.json
npm install -g yarn
yarn install
yarn build
```

**Common Rollup errors and solutions:**
- `Cannot find module @rollup/rollup-linux-x64-gnu` → Use `--no-optional` flag
- `ENOENT: no such file or directory` → Clear npm cache and node_modules
- `Platform mismatch` → Use explicit `--platform=linux --arch=x64` flags
- `Permission denied` → Run npm commands without sudo, use proper user permissions

**Build works locally but fails in Docker:**
- Different Node.js versions between local and Docker
- Platform-specific dependencies (especially on Apple Silicon Macs)
- NPM cache issues in Docker layers
- Use the alternative Dockerfile which has more robust fallback strategies

**PostgreSQL connection errors in production:**
- `Can't load plugin: sqlalchemy.dialects:postgres` → Missing psycopg2 driver
- `No module named 'psycopg2'` → PostgreSQL dependencies not installed

**Solutions for PostgreSQL issues:**
1. **Use troubleshooting script:**
```bash
chmod +x troubleshoot-postgres.sh
./troubleshoot-postgres.sh
```

2. **Manual fixes:**
```bash
# Install system dependencies (in Dockerfile)
apt-get update && apt-get install -y libpq-dev gcc python3-dev build-essential

# Install Python PostgreSQL driver
pip install --upgrade pip
pip install psycopg2-binary

# Test installation
python -c "import psycopg2; print('PostgreSQL driver OK')"
python -c "import sqlalchemy.dialects.postgresql; print('SQLAlchemy dialect OK')"
```

3. **Check environment variables:**
```bash
echo $DATABASE_URL  # Should be postgresql://user:pass@host:port/dbname
```

**Pip cache permission warnings:**
- Add to Dockerfile: `ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1`
- Install dependencies as root before switching to app user
- Or run: `chown -R appuser:appuser /home/appuser/.cache`

### Health Check
Visit `/api/health` for system status:
```json
{
  "status": "healthy",
  "database": "connected",
  "users_count": 5,
  "active_keywords": 15,
  "total_ads": 234
}
```

## 📊 Monitoring & Logs

### Application Logs
- `data/scraper.log` - Ad scraping activity
- Console logs - Application errors and info
- Coolify dashboard - Deployment and runtime logs

### Key Metrics
- User registration and login activity
- Ad checking performance and frequency
- Database query performance
- Error rates and types

### Database Maintenance
The application includes automatic cleanup mechanisms:
- **NEW tags**: Automatically removed after 6 hours
- **Deleted ads**: Permanently removed after 30 days
- **Manual cleanup**: Use `python check_deleted_ads.py --cleanup` for immediate cleanup

Check database statistics:
```bash
python check_deleted_ads.py           # Show current statistics
python check_deleted_ads.py --dry-run # Preview what would be cleaned
python check_deleted_ads.py --cleanup # Actually clean up old data
```

## 🔄 Migration from JSON

If upgrading from the legacy JSON-based version:

1. **Backup your data:**
```bash
cp -r data data_backup
```

2. **Run migration:**
```bash
python init_db.py
# Migration will automatically detect and import JSON data
```

3. **Verify migration:**
```bash
python check_migration_status.py
```

## 🚢 Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t bazos-checker .

# Run container
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-key \
  -e DATABASE_URL=your-db-url \
  bazos-checker
```

### Manual Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Run database initialization
4. Build frontend assets
5. Start application with process manager (PM2, systemd)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For issues and questions:

1. Check this README and troubleshooting section
2. Review application logs
3. Search existing GitHub issues
4. Create a new issue with detailed information

---

**🛡️ Security Notice**: This application handles user authentication and personal data. Ensure compliance with relevant data protection regulations (GDPR, CCPA, etc.) when deploying in production. Always use HTTPS and keep dependencies updated.

**📱 Mobile Ready**: Fully responsive design works perfectly on mobile devices, tablets, and desktops. Progressive Web App features provide a native-like experience.
