import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import svgr from 'vite-plugin-svgr'

// Бэкенд: отдаёт картинки к условиям заданий (/storage). Из Docker-контейнера: API_SERVER=http://host.docker.internal:8000
const API_SERVER = process.env.API_SERVER ?? 'http://127.0.0.1:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr()
  ],
  server: {
    proxy: {
      // картинки к условиям заданий
      '/storage': API_SERVER,
    },
  },
})
