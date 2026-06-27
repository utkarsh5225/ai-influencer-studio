import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/datasets': 'http://127.0.0.1:8000',
      '/training': 'http://127.0.0.1:8000',
      '/generation': 'http://127.0.0.1:8000',
      '/output': 'http://127.0.0.1:8000'
    }
  }
})
