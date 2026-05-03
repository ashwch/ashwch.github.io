import { getAllArticles } from '../lib/content';
import { createFeed } from '../lib/feeds';

export async function GET() {
  const articles = await getAllArticles();
  const feed = createFeed({
    title: 'ashwch RSS',
    description: 'Writing by Ashwini Chaudhary.',
    id: 'https://ashwch.com/',
    feedUrl: 'https://ashwch.com/rss.xml',
    articles,
  });

  return new Response(feed.rss2(), {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
    },
  });
}
