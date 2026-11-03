import type { CollectionEntry } from 'astro:content';

// Mais novo primeiro. Mesma data desempata pelo id: sem isso, relatórios do
// mesmo dia trocavam de ordem (e de Anterior/Próximo) conforme a ordem em que
// os arquivos eram lidos no build.
export const byNewest = (a: CollectionEntry<'blog'>, b: CollectionEntry<'blog'>) =>
  b.data.pubDate.valueOf() - a.data.pubDate.valueOf() || a.id.localeCompare(b.id);
