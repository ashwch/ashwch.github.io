# Cloudflare Pages deployment notes

## Recommended Pages configuration

- **Production branch:** `master`
- **Root directory:** `site`
- **Build command:** `pnpm build`
- **Build output directory:** `dist`
- **Node version:** `24`
- **Package manager:** `pnpm`

## Current repository automation shape

This repo currently uses **GitHub Actions direct uploads** to Cloudflare Pages rather than Cloudflare's native Git provider integration.

That means:
- Cloudflare Pages may still show `Git Provider: No`
- preview and production deploys are triggered by `.github/workflows/astro-pages-deploy.yml`
- Astro is built in GitHub Actions, then uploaded with `wrangler pages deploy`

## Custom-domain route preservation

Cloudflare Pages normalizes `.html` routes on its project domain (for example `/pages/about.html` → `/pages/about`).
Because preserving legacy `.html` URLs is launch-critical for `ashwch.com`, the custom domain is fronted by a small Worker proxy:

- source: `cloudflare/ashwch-astro-domain-proxy.mjs`
- routes: `ashwch.com/*`, `www.ashwch.com/*`
- behavior:
  - preserve legacy `.html` URLs by mapping them to the corresponding clean Pages routes upstream
  - keep `www.ashwch.com` redirected to apex
  - proxy the custom domain to `ashwch-main-site.pages.dev`

If the Pages project is redeployed or recreated, keep this Worker route in place or legacy `.html` parity will regress on the custom domain.

## Production env vars

Set as needed in Cloudflare Pages:

- `PUBLIC_GA_MEASUREMENT_ID`
- `PUBLIC_DISQUS_SHORTNAME`
- `UNSPLASH_ACCESS_KEY` (only if sync runs in CI/build; otherwise keep sync manual)
- `UNSPLASH_USERNAME=suicide_chewbacca`
- `UNSPLASH_REFERRAL_SOURCE=ashwch.com`

## GitHub Actions settings for direct-upload deploys

Set these in the GitHub repository so Actions builds preserve production behavior:

### Repository variables

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_PAGES_PROJECT=ashwch-main-site`
- `PUBLIC_GA_MEASUREMENT_ID`
- `PUBLIC_DISQUS_SHORTNAME` (optional; Astro currently defaults to `ashwch` in production)

### Repository secrets

- `CLOUDFLARE_API_TOKEN`

Use a scoped Cloudflare API token with Pages write access for this account. Do **not** use a personal OAuth refresh token from local Wrangler config in CI.

## Worker deployment note

The current Worker route was deployed manually with local Wrangler OAuth credentials because the existing GitHub Actions token is scoped for Pages deploys, not arbitrary Worker/route management.

If you want to automate `cloudflare/ashwch-astro-domain-proxy.mjs`, create a separate Cloudflare API token with Workers + Routes permissions and wire a dedicated workflow for it.

## Current live state

- `master` deploys to Cloudflare Pages production
- preview deployments can be created from PR branches
- `ashwch.com` and `www.ashwch.com` are attached to the Pages project
- the custom domain stays behind `cloudflare/ashwch-astro-domain-proxy.mjs` for legacy `.html` route preservation
- Google Analytics is carried through `PUBLIC_GA_MEASUREMENT_ID`

## Ongoing rollout guidance

Use preview deployments for every PR that changes:
- `site/**`
- `content/**`

Before making custom-domain or worker changes, verify route parity, feeds, analytics, and comments on actual Cloudflare edge responses rather than only the `pages.dev` project domain.
