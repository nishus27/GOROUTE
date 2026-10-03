import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The dev server proxies /api to the Flask backend so that session cookies are
// same-origin during development. Set VITE_API_TARGET to point elsewhere.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET ?? 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
