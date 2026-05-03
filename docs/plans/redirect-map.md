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

- `/writing` → `/writing.html` (301)
- `/writing/` → `/writing.html` (301)
- `/about` → `/pages/about.html` (301)
- `/about/` → `/pages/about.html` (301)
- `/projects` → `/pages/projects.html` (301)
- `/projects/` → `/pages/projects.html` (301)
- `/photography` → `/pages/photography.html` (301)
- `/photography/` → `/pages/photography.html` (301)

## Notes

- Legacy article and page paths remain canonical at launch.
- Redirects for any future `.html` removal should be deferred until after launch and after analytics/SEO review.
