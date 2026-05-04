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

Use a scoped Cloudflare API token with Pages/Workers write access for this account. Do **not** use a personal OAuth refresh token from local Wrangler config in CI.

## Recommended rollout shape

### Preview first
Use Cloudflare Pages preview deployments for every PR that changes:
- `site/**`
- `content/**`

### Production later
Do not switch production traffic until:
- route parity is verified
- feeds are verified
- comment/analytics decisions are confirmed
- photography sync data is populated and approved

## Important migration caveat

The current live site still serves from GitHub Pages `gh-pages`. A Cloudflare Pages production deploy should be treated as a parallel target until cutover is approved.
