export function GET() {
  return new Response(`User-agent: *
Allow: /

Sitemap: https://ashwch.com/sitemap-index.xml
`, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}
