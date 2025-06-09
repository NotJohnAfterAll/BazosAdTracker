# Bazos.cz Ad Tracker

A modern web application to track advertisements on Bazos.cz based on keywords. Get notified when new ads appear or existing ones are removed.

## Features

- Track multiple keywords simultaneously
- Modern UI with shadcn-inspired components
- Dashboard showing most recent advertisements across all keywords
- Keyword-specific ad views
- Changes log to track new and deleted advertisements
- Audio notifications for new ads
- Dark/light theme toggle
- Responsive design for all devices

## Requirements

- Python 3.8 or higher
- pip for package management

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Initialize the project:
   ```
   python init.py
   ```

## Usage

1. Start the application:
   ```
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Add keywords to track
4. The application will automatically check for new ads at regular intervals
5. Receive notifications when new ads are found

## Configuration

The application can be configured using environment variables or a `.env` file:

- `CHECK_INTERVAL`: Time in seconds between checks for new ads (default: 300)
- `FLASK_ENV`: Set to `development` for development mode or `production` for production
- `SECRET_KEY`: Secret key for Flask

## License

MIT

## Disclaimer

This tool is intended for personal use only. Please respect Bazos.cz's terms of service and avoid making excessive requests to their server.
