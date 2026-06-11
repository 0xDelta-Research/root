import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import yaraGrammar from './src/grammars/yara.tmLanguage.json';

export default defineConfig({
  site: 'https://0xdelta.org',
  vite: {
    server: {
      allowedHosts: true
    }
  },
  markdown: {
    shikiConfig: {
      langs: [{ ...yaraGrammar, name: 'yara', aliases: ['yara'] }],
    },
  },
  integrations: [
    react(),
    tailwind({ applyBaseStyles: false }),
    sitemap(),
  ],
});