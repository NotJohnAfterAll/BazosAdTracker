# Bazos Ad Tracker - Vue.js Frontend

This is the Vue.js frontend for the Bazos Ad Tracker application, built with modern technologies including Vue 3, TypeScript, Tailwind CSS, and shadcn/vue components.

## Features

- **Modern Vue.js Frontend**: Built with Vue 3 and TypeScript
- **shadcn/vue Components**: Beautiful, accessible UI components
- **Real-time Updates**: Socket.IO integration for live ad updates
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Dark/Light Theme**: Theme toggle support
- **HTTPS Ready**: Configurable HTTPS support for production

## Tech Stack

- Vue 3 with Composition API
- TypeScript
- Tailwind CSS
- shadcn/vue components
- Socket.IO client
- Vite (development server)

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Flask backend running on port 5000

### Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   Edit `.env` file to customize API URL:
   ```
   VITE_API_URL=http://localhost:3000/api
   VITE_APP_TITLE=Bazos Ad Tracker Vue
   VITE_APP_VERSION=1.0.0
   ```

### Development

1. **Start the Flask backend** (in the root directory):
   ```bash
   python app.py
   ```

2. **Start the Vue development server** (in the frontend directory):
   ```bash
   npm run dev
   ```

3. **Access the application**:
   - Vue frontend: http://localhost:3000
   - Flask backend: http://localhost:5000

The Vue development server will proxy API calls to the Flask backend automatically.

### HTTPS Setup (Optional)

To enable HTTPS in development:

1. **Generate SSL certificates**:
   ```bash
   # Run the certificate generation script
   powershell -ExecutionPolicy Bypass -File generate-certs.ps1
   ```

2. **Enable HTTPS in vite.config.ts**:
   ```typescript
   server: {
     https: {
       key: './certs/localhost-key.pem',
       cert: './certs/localhost.pem'
     },
     // ... other config
   }
   ```

3. **Update .env file**:
   ```
   VITE_API_URL=https://localhost:3000/api
   ```

### Production Build

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Preview the build**:
   ```bash
   npm run preview
   ```

The built files will be in the `dist` directory and can be served by any static file server.

## Architecture

### Component Structure

```
src/
├── components/
│   ├── ui/              # shadcn/vue base components
│   ├── AdCard.vue       # Individual ad display
│   ├── AppHeader.vue    # Main header with stats
│   ├── AppTabs.vue      # Navigation tabs
│   ├── KeywordManager.vue # Keyword management
│   ├── RecentAdsTab.vue # Recent ads view
│   ├── KeywordsTab.vue  # Keyword-specific ads
│   ├── FavoritesTab.vue # Favorite ads
│   ├── ChangesTab.vue   # Changes log
│   └── SettingsModal.vue # Settings dialog
├── lib/
│   └── utils.ts         # Utility functions
├── assets/
│   └── index.css        # Global styles
└── App.vue              # Main application component
```

### API Integration

The frontend communicates with the Flask backend through:

- **REST API**: For CRUD operations (keywords, ads, stats)
- **Socket.IO**: For real-time updates and notifications

### State Management

- Uses Vue 3 Composition API with reactive refs
- Local storage for user preferences (favorites, settings)
- Real-time state updates via Socket.IO

## Key Features

### Real-time Updates
- Socket.IO connection for live ad updates
- Automatic refresh of ad lists when new ads are found
- Visual notifications for new ads

### Responsive Design
- Mobile-first approach with Tailwind CSS
- Adaptive layouts for different screen sizes
- Touch-friendly interface elements

### Accessibility
- shadcn/vue components with built-in accessibility
- Keyboard navigation support
- Screen reader friendly

### Performance
- Vite for fast development and optimized builds
- Code splitting and lazy loading
- Efficient component updates with Vue 3

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:3000/api` |
| `VITE_APP_TITLE` | Application title | `Bazos Ad Tracker Vue` |
| `VITE_APP_VERSION` | Application version | `1.0.0` |

## Troubleshooting

### Common Issues

1. **CORS Issues**: Make sure the Flask backend is running and accessible
2. **Socket.IO Connection**: Check that Socket.IO is properly configured on both frontend and backend
3. **Certificate Errors**: For HTTPS development, accept the self-signed certificate warning in your browser

### Development Tips

- Use browser dev tools to monitor Socket.IO connections
- Check the Network tab for API call issues
- Use Vue DevTools for component debugging

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Run TypeScript type checking

## Contributing

When contributing to the frontend:

1. Follow Vue 3 Composition API patterns
2. Use TypeScript for type safety
3. Follow the existing component structure
4. Ensure responsive design principles
5. Test on multiple browsers and devices

## Migration from Original

This Vue.js frontend is a complete rewrite of the original Flask template-based frontend, providing:

- Better performance and user experience
- Modern development practices
- Enhanced maintainability
- Better separation of concerns
- Real-time capabilities without page refreshes
