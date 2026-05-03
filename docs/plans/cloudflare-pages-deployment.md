# Cloudflare Pages deployment notes

## Recommended Pages configuration

- **Production branch:** `master`
- **Root directory:** `site`
- **Build command:** `pnpm build`
- **Build output directory:** `dist`
- **Node version:** `24`
- **Package manager:** `pnpm`

## Production env vars

Set as needed in Cloudflare Pages:

- `PUBLIC_GA_MEASUREMENT_ID`
- `PUBLIC_DISQUS_SHORTNAME`
- `UNSPLASH_ACCESS_KEY` (only if sync runs in CI/build; otherwise keep sync manual)
- `UNSPLASH_USERNAME=suicide_chewbacca`
- `UNSPLASH_REFERRAL_SOURCE=ashwch.com`

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
