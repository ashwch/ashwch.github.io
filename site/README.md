# Astro main site for ashwch.com

This directory contains the live Astro application for `ashwch.com`.

## Goals

- preserve legacy URL equity for launch-critical routes
- improve the reading experience, not just port templates
- provide a reusable design-system foundation for future `*.ashwch.com` properties
- move photography to an Unsplash-backed sync model

## Route policy

These routes are intentionally preserved:

- articles: `/<slug>.html`
- pages: `/pages/about.html`, `/pages/projects.html`, `/pages/photography.html`
- archives: `/archives.html`
- tags: `/tags.html`, `/tag/<slug>.html`
- categories: `/categories.html`, `/category/<slug>.html`
- feeds: `/feeds/all.atom.xml` and category atom feeds

## Commands

From `site/`:

```bash
pnpm install
pnpm dev
pnpm build
pnpm check
```

### Sync commands

```bash
pnpm sync            # migrate Pelican content + sync static assets
pnpm sync:content    # regenerate Astro collection files from ../content/
pnpm sync:assets     # copy ../content/images and ../content/extra/CNAME into public/
pnpm sync:unsplash   # fetch Unsplash portfolio metadata into the generated dataset
```

`pnpm dev` and `pnpm build` run `pnpm sync` automatically.

## Content model

Root `content/` remains the source input:

- `../content/articles/*.md`
- `../content/pages/*.md`

The migration script rewrites Pelican metadata into Astro frontmatter under:

- `src/content/articles/*.md`
- `src/content/pages/*.md`

It also normalizes `{static}/...` paths to site-root asset paths.

## Photography sync

Phase 1 uses an Unsplash-hosted model.

Required env vars:

```bash
export UNSPLASH_ACCESS_KEY=...
export UNSPLASH_USERNAME=suicide_chewbacca   # optional, defaults to this
export UNSPLASH_REFERRAL_SOURCE=ashwch.com   # optional
```

Generated dataset:

- `src/data/photography/generated/unsplash-photos.json`

Manual override file:

- `src/data/photography/overrides.json`

Current expected launch behavior:

- render gallery content from the generated dataset
- attribute and link back to Unsplash clearly
- do not pretend downloads are served directly from ashwch.com while using Unsplash-hosted assets

## Analytics and comments

- GA4 is supported through `PUBLIC_GA_MEASUREMENT_ID`
- no analytics script is injected unless `PUBLIC_GA_MEASUREMENT_ID` is set
- Disqus is preserved through `PUBLIC_DISQUS_SHORTNAME` and defaults to `ashwch` in production

## Deployment direction

Target platform: Cloudflare Pages.

Current live setup:

- `master` deploys to the Cloudflare Pages project `ashwch-main-site`
- `ashwch.com` and `www.ashwch.com` are served through Cloudflare
- the custom domain uses `../cloudflare/ashwch-astro-domain-proxy.mjs` to preserve legacy `.html` URLs
- the old Pelican stack is archived in `../archive/pelican/`

## Related docs

- content repost workflow: `../docs/runbooks/blog-reposting.md` (canonical ownership, link rewriting, asset paths, and validation commands)
- migration plan: `../docs/plans/astro-migration-plan.md`
- repository deployment caveats: `../AGENTS.md`
