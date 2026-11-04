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
  // Baixa a página de um link quando o mouse passa por ele (ou o foco chega):
  // a navegação seguinte sai do cache, quase instantânea.
  prefetch: { prefetchAll: true },
  // Imagens dos relatórios ganham srcset: o celular baixa a versão do tamanho
  // da tela em vez do arquivo cheio.
  image: {
    layout: 'constrained',
    responsiveStyles: true,
  },
  markdown: {
    shikiConfig: {
      langs: [yaraGrammar],
    },
  },
  integrations: [
    react(),
    tailwind({ applyBaseStyles: false }),
    sitemap(),
  ],
});