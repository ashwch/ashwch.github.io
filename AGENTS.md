# AGENTS.md

This repository now powers the live Astro version of `https://ashwch.com`.

## Current deployment model

- **Production branch:** `master`
- **Current host:** Cloudflare Pages
- **Pages project:** `ashwch-main-site`
- **Production domain:** `ashwch.com`
- **Preview/production deploy workflow:** `.github/workflows/astro-pages-deploy.yml`
- **Custom-domain Worker:** `cloudflare/ashwch-astro-domain-proxy.mjs`

## Important rules

### 1) `site/` is the active app

Current application work happens in:

- `site/`
- `content/`
- `content/images/`
- `cloudflare/`

Do not treat the archived Pelican stack as current.

### 2) `site/src/content/**` is generated

Do not hand-edit:

- `site/src/content/articles/**`
- `site/src/content/pages/**`

Those files are regenerated from root `content/` by the Astro sync scripts.

### 3) Historical Pelican files live in `archive/pelican/`

The previous Pelican site, theme, configs, and old deployment instructions were moved to:

- `archive/pelican/`

Use that archive only for historical reference or one-off migration lookups.

## Safe workflow for current changes

### Local validation

From `site/` run:

```bash
pnpm check
pnpm build
```

If you touch the custom-domain Worker, also run:

```bash
node --check cloudflare/ashwch-astro-domain-proxy.mjs
```

### Content / image changes

Root `content/` remains the source of truth.

For article authoring and cross-site reposts with `engineering.diversio.com`, read:

- `docs/runbooks/blog-reposting.md` — explains why `ashwch.com` owns the full article, why the engineering site keeps a short stub, and which files/commands to use
- `docs/runbooks/article-end-matter.md` — standardized review acknowledgements and AI writing disclaimer blocks for article end matter

If you touch photography-related flows, current helpers are:

```bash
uv run scripts/photo_manager.py
python3 scripts/set_photo_order.py
```

## Deployment notes

### Astro deploys

- GitHub Actions builds Astro and uploads it directly to Cloudflare Pages.
- `master` updates production.
- PR branches can create preview deploys.

### Custom domain behavior

Cloudflare Pages normalizes `.html` routes on its project domain, so `ashwch.com` is fronted by a Worker to preserve legacy `.html` URLs externally.

If you touch route behavior, redirects, or custom-domain delivery, inspect both:

- `site/public/_redirects`
- `cloudflare/ashwch-astro-domain-proxy.mjs`

### DNS / propagation caveat

After custom-domain or DNS-related changes, your local resolver may lag behind public resolvers.

Prefer checking both:

```bash
dig +short @1.1.1.1 ashwch.com
dig +short @8.8.8.8 ashwch.com
```

## Done checklist

Before marking work done:

- [ ] `pnpm check` passes
- [ ] `pnpm build` passes
- [ ] Worker syntax is valid if `cloudflare/` changed
- [ ] Live/preview behavior was verified for the changed routes when relevant
- [ ] No archived Pelican instructions were reintroduced into current root docs
