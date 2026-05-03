# Astro launch checklist

## Before cutover

- [ ] `site/` builds cleanly with `pnpm build`
- [ ] critical legacy URLs render on Astro output
- [ ] article URLs preserved at `/<slug>.html`
- [ ] page URLs preserved at `/pages/*.html`
- [ ] feeds render at `/feeds/all.atom.xml` and `/rss.xml`
- [ ] `robots.txt` and sitemap are present
- [ ] GA4 is configured for production
- [ ] Disqus shortname is configured if comment preservation is required at launch
- [ ] Unsplash sync has run with production credentials
- [ ] photography attribution/download language is explicit and approved
- [ ] preview deploy exists on Cloudflare Pages
- [ ] redirect/canonical review is complete

## Cutover

- [ ] keep current Pelican site untouched until Astro preview passes
- [ ] point Cloudflare Pages production to the approved build
- [ ] verify DNS / origin configuration in Cloudflare
- [ ] purge Cloudflare cache after cutover

## Post-cutover verification

- [ ] open the homepage and at least 5 article URLs
- [ ] verify `/pages/about.html`, `/pages/projects.html`, `/pages/photography.html`
- [ ] verify `/archives.html`, `/tags.html`, and a sample tag page
- [ ] verify `/feeds/all.atom.xml` and `/rss.xml`
- [ ] verify analytics pageview firing
- [ ] verify Disqus thread load on a preserved article URL
- [ ] verify Unsplash links/attribution/download behavior
- [ ] verify sitemap is reachable
- [ ] verify dark mode, mobile nav, and code blocks on a long article
