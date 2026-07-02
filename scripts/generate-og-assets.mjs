// Gera os assets estáticos usados no card OpenGraph (src/pages/og/[...route].ts):
//   - src/assets/og/brand.png    : LOGO REAL (public/delta-favicon.png) + "0xDelta Research" (grande)
//   - src/assets/og/bg-blue.png  : fundo 1200x630 (grid) + tag "BLUE TEAM" no canto
//   - src/assets/og/bg-red.png   : fundo 1200x630 (grid) + tag "RED TEAM" no canto
// Rodar com: node scripts/generate-og-assets.mjs
import sharp from 'sharp';
import { mkdirSync, readFileSync } from 'node:fs';

mkdirSync('src/assets/og', { recursive: true });

// Logo real do 0xDelta, embutido como data URI para o sharp rasterizar.
const favB64 = readFileSync('public/delta-favicon.png').toString('base64');

// --- Faixa de marca: logo REAL (grande) + "0xDelta Research" (grande) ---
const brand = `<svg xmlns="http://www.w3.org/2000/svg" width="820" height="200" viewBox="0 0 820 200">
  <image href="data:image/png;base64,${favB64}" x="10" y="26" width="148" height="148"/>
  <text x="188" y="123" font-family="Consolas, 'DejaVu Sans Mono', monospace" font-size="62" font-weight="bold">
    <tspan fill="#e5e5e5">0xDelta</tspan><tspan fill="#737373" font-weight="normal" dx="20">Research</tspan>
  </text>
</svg>`;

// --- Fundo com grid + tag de time no canto superior direito ---
const bgFor = (label, color) => `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
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
  <!-- Tag de time (canto superior direito) -->
  <g>
    <rect x="${1130 - label.length * 20 - 40}" y="52" width="${label.length * 20 + 40}" height="52" rx="4"
          fill="${color}22" stroke="${color}" stroke-width="2"/>
    <text x="${1130 - 20}" y="87" text-anchor="end" font-family="Consolas, 'DejaVu Sans Mono', monospace"
          font-size="26" font-weight="bold" letter-spacing="3" fill="${color}">${label}</text>
  </g>
</svg>`;

await sharp(Buffer.from(brand)).png().toFile('src/assets/og/brand.png');
await sharp(Buffer.from(bgFor('BLUE TEAM', '#3b82f6'))).png().toFile('src/assets/og/bg-blue.png');
await sharp(Buffer.from(bgFor('RED TEAM', '#ef4444'))).png().toFile('src/assets/og/bg-red.png');
console.log('OG assets gerados: brand.png (grande) + bg-blue.png + bg-red.png');
