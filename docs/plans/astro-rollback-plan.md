# Astro rollback plan

## Trigger conditions

Roll back immediately if any of the following happen after cutover:

- widespread 404s on preserved article URLs
- broken feed endpoints
- severe rendering regressions on article pages
- analytics or comment regressions judged unacceptable for launch
- photography page shipping incorrect licensing/download behavior

## Rollback steps

1. Restore the previous production target to the existing Pelican/GitHub Pages deployment.
2. Re-point Cloudflare origin / deployment target back to the last known-good production site.
3. Purge Cloudflare cache.
4. Re-verify a sample of critical URLs:
   - homepage
   - 3 recent article URLs
   - `/pages/about.html`
   - `/feeds/all.atom.xml`
5. Announce rollback status and capture the exact failure condition.

## Data safety notes

- Pelican source remains in the repo during migration, so rollback is source-safe.
- `gh-pages` should not be removed until Astro has been stable in production.
- Unsplash sync data is additive and does not block rollback to Pelican.

## Recovery after rollback

- fix the issue in Astro preview/staging first
- rerun route verification
- rerun feed verification
- rerun launch checklist before attempting a second cutover
