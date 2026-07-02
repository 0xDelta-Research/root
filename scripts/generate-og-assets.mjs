// Gera os assets estáticos usados no card OpenGraph (src/pages/og/[...route].ts):
//   - src/assets/og/brand.png : faixa de marca = LOGO REAL (public/delta-favicon.png) + "0xDelta Research"
//   - src/assets/og/bg.png    : fundo 1200x630 com o grid tático do site
// Rodar com: node scripts/generate-og-assets.mjs
import sharp from 'sharp';
import { mkdirSync, readFileSync } from 'node:fs';

mkdirSync('src/assets/og', { recursive: true });

// Logo real do 0xDelta, embutido como data URI para o sharp rasterizar.
const favB64 = readFileSync('public/delta-favicon.png').toString('base64');

// --- Faixa de marca: logo REAL + "0xDelta Research" ---
const brand = `<svg xmlns="http://www.w3.org/2000/svg" width="700" height="160" viewBox="0 0 700 160">
  <image href="data:image/png;base64,${favB64}" x="20" y="24" width="112" height="112"/>
  <text x="160" y="98" font-family="Consolas, 'DejaVu Sans Mono', monospace" font-size="50" font-weight="bold">
    <tspan fill="#e5e5e5">0xDelta</tspan><tspan fill="#737373" font-weight="normal" dx="18">Research</tspan>
  </text>
</svg>`;

// --- Fundo com grid tático + leve glow (igual ao site) ---
const bg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0 L0 0 0 40" fill="none" stroke="rgba(255,255,255,0.035)" stroke-width="1"/>
    </pattern>
    <radialGradient id="glow" cx="82%" cy="8%" r="60%">
      <stop offset="0%" stop-color="rgba(255,255,255,0.06)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="#050505"/>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
</svg>`;

await sharp(Buffer.from(brand)).png().toFile('src/assets/og/brand.png');
await sharp(Buffer.from(bg)).png().toFile('src/assets/og/bg.png');
console.log('OG assets gerados em src/assets/og/ (logo real + grid)');
