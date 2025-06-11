import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },  server: {
    host: '0.0.0.0',
    port: 3000,
    // HTTPS configuration - uncomment for HTTPS support
    // https: {
    //   key: './certs/localhost-key.pem',
    //   cert: './certs/localhost.pem'
    // },
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        // Handle both HTTP and HTTPS targets
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error:', err);
          });
        }
      },
      '/socket.io': {
        target: process.env.VITE_API_TARGET || 'http://localhost:5000',
        changeOrigin: true,
        ws: true,
        secure: false,
        // Handle both HTTP and HTTPS targets
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Socket proxy error:', err);
          });
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
