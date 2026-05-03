import { getCanonicalSitemapEntries, renderSitemapUrlset } from '../lib/sitemap';

export async function GET() {
  const entries = await getCanonicalSitemapEntries();

  return new Response(renderSitemapUrlset(entries), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
    },
  });
}
