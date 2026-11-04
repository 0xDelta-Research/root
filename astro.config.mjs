import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import sitemap from '@astrojs/sitemap';
import yaraGrammar from './src/grammars/yara.tmLanguage.json';

// Tailwind 3 roda via PostCSS (postcss.config.mjs): @astrojs/tailwind não
// suporta Astro 6+, e migrar para Tailwind 4 mudaria a estratégia de CSS.
export default defineConfig({
  site: 'https://0xdelta.org',
  // Astro 7 passou o padrão para 'jsx', que remove espaços entre elementos
  // inline; true mantém o HTML como era gerado no Astro 5.
  compressHTML: true,
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
    sitemap(),
  ],
});