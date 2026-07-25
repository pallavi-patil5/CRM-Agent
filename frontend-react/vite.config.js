import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/dashboard': 'http://localhost:8000',
      '/ingest': 'http://localhost:8000',
      '/process-email': 'http://localhost:8000',
      '/process-all-emails': 'http://localhost:8000',
      '/agent': 'http://localhost:8000',
      '/analytics': 'http://localhost:8000',
      '/contacts': 'http://localhost:8000',
      '/threads': 'http://localhost:8000',
      '/thread': 'http://localhost:8000',
      '/tickets': 'http://localhost:8000',
      '/actions': 'http://localhost:8000',
      '/email': 'http://localhost:8000',
      '/rag': 'http://localhost:8000',
      '/gmail': 'http://localhost:8000',
    }
  }
})
