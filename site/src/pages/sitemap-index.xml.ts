import { renderSitemapIndex } from '../lib/sitemap';

export function GET() {
  return new Response(renderSitemapIndex(['https://ashwch.com/sitemap-0.xml']), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
    },
  });
}
