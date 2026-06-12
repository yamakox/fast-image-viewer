import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/', // NOTE: Vue RouterのcreateWebHistoryで用いられるベースパスはここで設定する。(例: /app/ など)
  server: {
    host: true,
    hmr: {
      host: 'localhost',
      // HMR crashes with ENOENT when deleting SVG asset with Vite + Tailwind v4
      // https://github.com/vitejs/vite/issues/19786
      overlay: false,
    },
  },
  plugins: [
    vue({
      template: {
        transformAssetUrls: {
          base: null,
          includeAbsolute: false,
        },
      },
    }),
    tailwindcss(),
  ],
  build: {
    // outDir: fileURLToPath(new URL('./dist', import.meta.url)),
    emptyOutDir: true,
    chunkSizeWarningLimit: 1024 * 1024 * 10, // 10MiB
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
