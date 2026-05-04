# Redirect map

Because launch-critical URLs are preserved, the redirect surface is intentionally small.

## Preserved as-is

- `/<article-slug>.html`
- `/pages/about.html`
- `/pages/projects.html`
- `/pages/photography.html`
- `/archives.html`
- `/tags.html`
- `/tag/<slug>.html`
- `/categories.html`
- `/category/<slug>.html`
- `/feeds/all.atom.xml`

## Aliases configured in `site/public/_redirects`

- `/about` → `/pages/about.html` (301)
- `/about/` → `/pages/about.html` (301)
- `/projects` → `/pages/projects.html` (301)
- `/projects/` → `/pages/projects.html` (301)
- `/photography` → `/pages/photography.html` (301)
- `/photography/` → `/pages/photography.html` (301)

## Custom-domain preservation note

Cloudflare Pages normalizes `.html` routes on the project domain, so `ashwch.com` uses a custom-domain Worker proxy to preserve legacy `.html` URLs externally.

That means:
- `https://ashwch-main-site.pages.dev/pages/about.html` may redirect to `/pages/about`
- `https://ashwch.com/pages/about.html` must continue to work as a stable legacy URL

## Notes

- Legacy article and page paths remain canonical at launch.
- Redirects for any future `.html` removal should be deferred until after launch and after analytics/SEO review.
