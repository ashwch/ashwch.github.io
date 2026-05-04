const ROBOTS_TXT = `User-agent: *
Allow: /

Sitemap: https://ashwch.com/sitemap-index.xml
`;

function isBodylessMethod(method) {
  return method === 'GET' || method === 'HEAD';
}

function buildUpstreamUrl(requestUrl) {
  const upstream = new URL(requestUrl);
  upstream.protocol = 'https:';
  upstream.hostname = 'ashwch-main-site.pages.dev';

  if (upstream.pathname !== '/' && upstream.pathname.endsWith('.html')) {
    upstream.pathname = upstream.pathname.slice(0, -5);
  }

  return upstream;
}

async function fetchFollowingPagesRedirects(request, upstreamUrl) {
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('Host', 'ashwch-main-site.pages.dev');

  let currentUrl = upstreamUrl;
  let response;

  for (let redirects = 0; redirects < 5; redirects += 1) {
    response = await fetch(currentUrl.toString(), {
      method: request.method,
      headers: requestHeaders,
      body: isBodylessMethod(request.method) ? undefined : request.body,
      redirect: 'manual',
    });

    if (![301, 302, 307, 308].includes(response.status)) {
      return response;
    }

    const location = response.headers.get('Location');
    if (!location) {
      return response;
    }

    currentUrl = new URL(location, currentUrl);
    currentUrl.protocol = 'https:';
    currentUrl.hostname = 'ashwch-main-site.pages.dev';
  }

  return response;
}

export default {
  async fetch(request) {
    const incomingUrl = new URL(request.url);

    if (incomingUrl.hostname === 'www.ashwch.com') {
      const redirectUrl = new URL(request.url);
      redirectUrl.hostname = 'ashwch.com';
      return Response.redirect(redirectUrl.toString(), 301);
    }

    if (incomingUrl.pathname === '/robots.txt') {
      return new Response(ROBOTS_TXT, {
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'cache-control': 'public, max-age=0, must-revalidate',
        },
      });
    }

    const upstreamUrl = buildUpstreamUrl(request.url);
    const response = await fetchFollowingPagesRedirects(request, upstreamUrl);

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  },
};
