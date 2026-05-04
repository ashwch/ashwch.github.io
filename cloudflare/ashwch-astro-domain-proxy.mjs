/**
 * Custom-domain proxy Worker for ashwch.com.
 *
 * PROBLEM
 *   Cloudflare Pages serves our Astro site correctly on its project domain
 *   (ashwch-main-site.pages.dev), but the platform normalises .html routes
 *   on the custom domain.  For example:
 *
 *     /pages/about.html  →  308 redirect to /pages/about
 *     /writing.html      →  308 redirect to /writing
 *
 *   This breaks our launch-critical URL preservation policy.  Legacy
 *   Pelican-era URLs must continue to work at their exact .html paths.
 *
 * SOLUTION
 *   A small Worker that sits in front of the custom domain and:
 *
 *     1. Intercepts .html requests and strips the extension before
 *        forwarding to the Pages origin (which serves clean paths).
 *
 *     2. Returns the Pages response as if it came from the original
 *        .html URL, preserving the URL externally.
 *
 *     3. Redirects www.ashwch.com → ashwch.com (apex canonical).
 *
 *     4. Serves our own /robots.txt directly because Cloudflare's
 *        managed Content Signals policy would otherwise replace the body
 *        on the custom domain.
 *
 * REQUEST FLOW
 *
 *   Browser:  GET /pages/about.html
 *       │
 *       ▼
 *   Worker:   strip .html → GET /pages/about (to Pages origin)
 *       │
 *       ▼
 *   Pages:    200 OK (serves the Astro HTML)
 *       │
 *       ▼
 *   Worker:   forwards response as if /pages/about.html was served
 *       │
 *       ▼
 *   Browser:  sees /pages/about.html in the address bar, gets correct HTML
 *
 * DEPLOYMENT
 *
 *   This Worker was deployed manually with local Wrangler OAuth credentials
 *   because the GitHub Actions token is scoped for Pages deploys, not
 *   Worker/route management.
 *
 *   Command:
 *     npx wrangler deploy cloudflare/ashwch-astro-domain-proxy.mjs \
 *       --name ashwch-astro-domain-proxy \
 *       --compatibility-date 2026-05-03 \
 *       --routes 'ashwch.com/*' \
 *       --routes 'www.ashwch.com/*'
 *
 *   If you recreate the Pages project or change domain routing, re-deploy
 *   this Worker or legacy .html parity will regress on the custom domain.
 */

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
