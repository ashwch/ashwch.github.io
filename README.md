# ashwch.com source repository

This repository now powers the live Astro version of `https://ashwch.com`.

## Current state

- **Live site:** Astro
- **Hosting:** Cloudflare Pages
- **Production domain:** `ashwch.com`
- **Pages project:** `ashwch-main-site`
- **Custom-domain route preservation:** `cloudflare/ashwch-astro-domain-proxy.mjs`
- **Historical Pelican stack:** `archive/pelican/`

## Start here

If you are working on the current site, read:

- `AGENTS.md`
- `site/README.md`
- `docs/plans/cloudflare-pages-deployment.md`

## Repository layout

```text
.
├── site/                         # Astro app
├── content/                      # Source content and images
│   ├── articles/
│   ├── pages/
│   └── images/
├── scripts/                      # Photography/content helper scripts
├── cloudflare/                   # Custom-domain Worker source
├── docs/                         # Current docs and plans
└── archive/pelican/              # Historical Pelican stack and docs
```

## Local development

From `site/`:

```bash
pnpm install
pnpm dev
pnpm check
pnpm build
```

Notes:

- `pnpm check` and `pnpm build` automatically sync content and assets first.
- `content/` is still the source of truth for articles, pages, and images.
- `site/src/content/**` is generated output. Do not hand-edit it.

## Content workflow

- Articles live in `content/articles/*.md`
- Static pages live in `content/pages/*.md`
- Shared images live in `content/images/**`
- Shared acronym definitions live in `abbreviations.md`

Astro migration/sync scripts:

- `site/scripts/migrate-pelican-content.mjs`
- `site/scripts/sync-static-assets.mjs`
- `site/scripts/sync-unsplash.mjs`

## Photography workflow

Current helper commands:

```bash
uv run scripts/photo_manager.py
python3 scripts/set_photo_order.py
```

For the full current workflow, see:

- `docs/workflows/PHOTOGRAPHY_WORKFLOW.md`

## Deployment

### Site deploys

The current site is deployed by GitHub Actions direct-uploading Astro build output to Cloudflare Pages.

- PRs can publish preview deployments
- pushes/merges to `master` update the Pages production deployment

Relevant workflows:

- `.github/workflows/astro-site-ci.yml`
- `.github/workflows/astro-pages-deploy.yml`

### Custom domain behavior

`ashwch.com` sits behind a small Worker so legacy `.html` URLs continue to work even though Cloudflare Pages normalizes routes on its project domain.

Worker source:

- `cloudflare/ashwch-astro-domain-proxy.mjs`

## Historical Pelican archive

The old Pelican site, theme, configs, and helper scripts have been moved to:

- `archive/pelican/`

That archive is kept for historical reference so nothing is lost, but it is no longer the current production path.
