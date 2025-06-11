# Bazos.cz Ad Tracker

A comprehensive application for monitoring classified ads on Bazos.cz, featuring a Flask backend with web scraping capabilities and a modern Vue.js frontend.

## Features

- **Keyword Monitoring**: Track multiple keywords simultaneously
- **Real-time Updates**: Instant notifications when new ads are found
- **Modern Web Interface**: Vue.js frontend with responsive design
- **Statistics Tracking**: Monitor system performance and ad discovery metrics
- **Favorites System**: Save and organize interesting ads
- **Changes Log**: Track new and deleted advertisements
- **Dark/Light Theme**: Toggle between themes for better usability

## Architecture

### Backend (Flask)
- **Web Scraping**: Automated scraping of Bazos.cz
- **Data Storage**: JSON-based storage for keywords, ads, and statistics
- **Real-time Communication**: Socket.IO for live updates
- **REST API**: Full API for frontend integration
- **Background Scheduling**: Automated periodic checks

### Frontend (Vue.js)
- **Modern Framework**: Vue 3 with TypeScript
- **Component Library**: shadcn/vue for beautiful UI
- **Real-time Updates**: Socket.IO integration
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Progressive Enhancement**: Works without JavaScript fallback

## Quick Start

### Option 1: Development Mode (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd BazosAdTracker
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start development environment**:
   ```bash
   # Run the convenient startup script
   powershell -ExecutionPolicy Bypass -File start-dev.ps1
   ```

   Or manually:
   ```bash
   # Terminal 1: Start Flask backend
   python app.py

   # Terminal 2: Start Vue frontend
   cd frontend
   npm run dev
   ```

5. **Access the application**:
   - **Vue.js Frontend**: http://localhost:3000 (recommended)
   - **Flask Backend**: http://localhost:5000 (API only)

### Option 2: Flask-only Mode (Legacy)

If you prefer the original Flask templates:

```bash
python app.py
# Access at http://localhost:5000
```

## Requirements

### Backend
- Python 3.8 or higher
- pip for package management

### Frontend (Optional)
- Node.js 16 or higher
- npm or yarn

## Production Deployment

### Build Vue.js Frontend
```bash
cd frontend
npm run build
```

### Serve Static Files
Configure your web server to:
1. Serve static files from `frontend/dist/`
2. Proxy API calls to the Flask backend
3. Handle Socket.IO connections

### Environment Variables
- `CHECK_INTERVAL`: Time in seconds between checks (default: 300)
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Flask secret key

## Development

### Backend Development
The Flask backend provides:
- REST API endpoints (`/api/`)
- Socket.IO real-time communication
- Background job scheduling
- Web scraping logic

### Frontend Development
The Vue.js frontend offers:
- Modern component-based architecture
- TypeScript for type safety
- Tailwind CSS for styling
- Real-time updates via Socket.IO

### API Endpoints
- `GET /api/keywords` - List tracked keywords
- `POST /api/keywords` - Add new keyword
- `DELETE /api/keywords/<keyword>` - Remove keyword
- `GET /api/ads` - Get ads for keyword
- `GET /api/recent-ads` - Get recent ads across all keywords
- `GET /api/stats` - Get system statistics
- `POST /api/manual-check` - Trigger manual check

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

MIT

## Disclaimer

This tool is intended for personal use only. Please respect Bazos.cz's terms of service and avoid making excessive requests to their server.
