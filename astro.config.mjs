import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://0xdelta.org', 
  vite: {
    server: {
      allowedHosts: true
    }
  },

  integrations: [
    react(),
    tailwind({ applyBaseStyles: false }),
  ],
});