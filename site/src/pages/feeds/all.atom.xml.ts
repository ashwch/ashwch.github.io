import { getAllArticles } from '../../lib/content';
import { createFeed } from '../../lib/feeds';

export async function GET() {
  const articles = await getAllArticles();
  const feed = createFeed({
    title: 'ashwch Atom Feed',
    description: 'Writing by Ashwini Chaudhary.',
    id: 'https://ashwch.com/',
    feedUrl: 'https://ashwch.com/feeds/all.atom.xml',
    articles,
  });

  return new Response(feed.atom1(), {
    headers: {
      'Content-Type': 'application/atom+xml; charset=utf-8',
    },
  });
}
