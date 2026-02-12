import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VueDevTools()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api/arxiv': {
        target: 'https://export.arxiv.org',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api\/arxiv/, '')
      }
    }
  }
})
