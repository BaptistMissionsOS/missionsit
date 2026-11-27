// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'

// The public web app, served by the site at /missions (see missionsit/www/missions.py and
// website_route_rules in hooks.py). Built into the app's public folder so `bench build` ships it.
export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/missions',
      buildConfig: {
        outDir: '../public/frontend',
        baseUrl: '/assets/missionsit/frontend/',
        indexHtmlPath: '../www/missions.html',
      },
    }),
    vue(),
  ],
  build: {
    // The map chunk is mostly MapLibre GL (about 1 MB, 275 kB gzipped). It is split out already
    // and loads only on pages with a map, so this warning would only repeat what we know.
    chunkSizeWarningLimit: 1100,
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
})
