// Confere as tags de SEO de todas as páginas geradas. Roda no CI após o build:
//   node scripts/check-seo.mjs dist
// Falha (exit 1) listando cada página fora do padrão do BaseLayout.
import fs from 'node:fs';
import path from 'node:path';

const SITE = 'https://0xdelta.org/';
const dist = process.argv[2] ?? 'dist';

const walk = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : e.name.endsWith('.html') ? [path.join(dir, e.name)] : [],
  );

const attrs = (tag) => Object.fromEntries([...tag.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]));

// URL pública esperada para um arquivo gerado: dist/blog/x/index.html -> SITE + 'blog/x/'.
const urlFor = (file) => SITE + path.relative(dist, file).split(path.sep).join('/').replace(/index\.html$/, '');

function checkPage(html, file) {
  const head = html.split('</head>')[0];
  const tags = [...head.matchAll(/<(meta|link)\b[^>]*>/g)].map((m) => attrs(m[0]));
  const meta = (key, val) => tags.filter((t) => t[key] === val).map((t) => t.content);
  const problems = [];
  const one = (label, values) => {
    if (values.length !== 1 || !values[0]) problems.push(`${label}: expected 1, found ${values.length}`);
    return values[0];
  };

  one('<title>', [...head.matchAll(/<title>([^<]*)<\/title>/g)].map((m) => m[1].trim()));
  one('meta description', meta('name', 'description'));
  one('og:title', meta('property', 'og:title'));
  one('og:description', meta('property', 'og:description'));
  one('twitter:card', meta('name', 'twitter:card'));
  const image = one('og:image', meta('property', 'og:image'));
  if (image && !image.startsWith(SITE)) problems.push(`og:image not absolute on ${SITE}: ${image}`);
  else if (image && !fs.existsSync(path.join(dist, decodeURIComponent(new URL(image).pathname)))) problems.push(`og:image file not built: ${image}`);

  const noindex = meta('name', 'robots').some((c) => c?.includes('noindex'));
  if (!noindex) {
    const canonical = one('canonical', tags.filter((t) => t.rel === 'canonical').map((t) => t.href));
    const ogUrl = one('og:url', meta('property', 'og:url'));
    if (canonical && canonical !== urlFor(file)) problems.push(`canonical (${canonical}) != page URL (${urlFor(file)})`);
    if (canonical && ogUrl && canonical !== ogUrl) problems.push(`og:url (${ogUrl}) != canonical (${canonical})`);
  }

  const h1 = (html.match(/<h1[\s>]/g) || []).length;
  if (h1 !== 1) problems.push(`<h1>: expected 1, found ${h1}`);
  return problems;
}

const pages = walk(dist);
if (!pages.length) {
  console.log(`No HTML pages found in ${dist}`);
  process.exit(1);
}
let failed = 0;
for (const file of pages) {
  const problems = checkPage(fs.readFileSync(file, 'utf8'), file);
  if (problems.length) {
    failed++;
    console.log(`${path.relative(dist, file)}\n  - ${problems.join('\n  - ')}`);
  }
}
console.log(`${pages.length - failed}/${pages.length} pages pass the SEO check`);
process.exit(failed ? 1 : 0);
