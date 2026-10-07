import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import svgr from 'vite-plugin-svgr'

// Сервер нарешки из концепта (concepts/tasks_page, порт 8100), пока её API нет в основном бэкенде.
// Из Docker-контейнера: PRACTICE_SERVER=http://host.docker.internal:8100
const PRACTICE_SERVER = process.env.PRACTICE_SERVER ?? 'http://127.0.0.1:8100'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr()
  ],
  server: {
    proxy: {
      '/concept-practice': {
        target: PRACTICE_SERVER,
        rewrite: (path) => path.replace(/^\/concept-practice/, '/api'),
      },
      // картинки к условиям заданий
      '/storage': PRACTICE_SERVER,
    },
  },
})
