import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const posts = (await getCollection('blog')).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: '0xDelta Research',
    description: 'Offensive and defensive cybersecurity research — Red Team techniques, malware analysis, threat hunting, and more.',
    site: context.site!,
    items: posts.map(post => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/blog/${(post as any).slug || post.id}/`,
      categories: [post.data.team, post.data.category, ...(post.data.tags ?? [])],
      author: post.data.author,
    })),
    customData: `<language>en</language>`,
  });
}
