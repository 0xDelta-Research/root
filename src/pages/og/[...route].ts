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
      // Fundo com grid + tag do time (Blue/Red) no canto.
      bgImage: { path: isRed ? './src/assets/og/bg-red.png' : './src/assets/og/bg-blue.png', fit: 'cover' },
      // Faixa de marca (logo real + "0xDelta Research"), maior.
      logo: { path: './src/assets/og/brand.png', size: [600] },
      // Barra lateral (bem visível) na cor do time.
      border: { color: accent, width: 24, side: 'inline-start' },
      padding: 70,
      font: {
        title: { color: [237, 237, 237], size: 60, lineHeight: 1.15 },
        description: { color: [163, 163, 163], size: 29, lineHeight: 1.4 },
      },
    };
  },
});
