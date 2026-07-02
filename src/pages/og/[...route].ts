import { getCollection } from 'astro:content';
import { OGImageRoute } from 'astro-og-canvas';

// Gera uma imagem OpenGraph (1200x630) por relatório, no build.
// A imagem fica em /og/<id-do-post>.png e é referenciada no <head> do post.
const entries = await getCollection('blog');
const pages = Object.fromEntries(entries.map((e) => [e.id, e.data]));

export const { getStaticPaths, GET } = await OGImageRoute({
  param: 'route',
  pages,
  getImageOptions: (_path, page: any) => {
    const isRed = page.team === 'Red Team';
    const accent: [number, number, number] = isRed ? [239, 68, 68] : [59, 130, 246];
    const meta =
      [page.risk, page.team, page.category].filter(Boolean).join('   ·   ') +
      `\n@${page.author}`;

    return {
      title: page.title,
      description: meta,
      // Fundo com o grid tático do site (1200x630).
      bgImage: { path: './src/assets/og/bg.png', fit: 'cover' },
      // Faixa de marca (logo Δ + "0xDelta Research") no topo.
      logo: { path: './src/assets/og/brand.png', size: [460] },
      // Borda lateral na cor do time (Red/Blue).
      border: { color: accent, width: 12, side: 'inline-start' },
      padding: 70,
      font: {
        title: { color: [237, 237, 237], size: 60, lineHeight: 1.15 },
        description: { color: [163, 163, 163], size: 29, lineHeight: 1.4 },
      },
    };
  },
});
