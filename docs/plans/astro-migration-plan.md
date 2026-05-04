# Astro migration plan for ashwch.com

> Historical note: this was the working migration plan before the Astro cutover. `ashwch.com` now runs on Astro/Cloudflare Pages; use root `README.md` and `AGENTS.md` for the current state.


## Decisions locked before implementation

### 1) URL preservation policy
Treat current live URLs as launch-critical.

- Articles stay at `/<slug>.html`
- Pages stay at `/pages/about.html`, `/pages/projects.html`, `/pages/photography.html`
- Archives stay at `/archives.html`
- Tags stay at `/tags.html` and `/tag/<slug>.html`
- Categories stay at `/categories.html` and `/category/<slug>.html`
- Feeds stay at `/feeds/all.atom.xml` and existing category feeds
- Preserve legacy oddities too, including `terminal-setup-using-zsh-prezto-starship.md.html`
- New IA routes, if added later, are aliases or secondary entry points, not launch replacements

### 2) Photography source-of-truth decision
Phase 1 will use **Unsplash-hosted photos** as the public source model.

This means:

- Unsplash is the public source-of-truth for portfolio photo metadata
- Astro renders from a generated local cache created by an official API sync step
- Core gallery rendering does **not** depend on client-side live API fetches
- ashwch.com will act as a curated editorial front-end, not a self-hosted relicensing layer
- We will not ship a fake direct-download button for Unsplash-hosted assets
- Launch CTA behavior should be explicit, e.g. `View on Unsplash` / `Download on Unsplash`

If Ashwini later wants self-hosted derivatives or originals on ashwch.com, that becomes an explicit phase-2 licensing/product decision.

## Current site audit

### Content inventory
- Articles: 14 markdown files in `content/articles/`
- Pages: 3 markdown files in `content/pages/`
- Photography assets: 23 local images plus generated thumbnails and metadata

### Current generated route inventory
- Article/detail pages: 14
- Static pages: 3
- Tag pages: 112
- Category pages: 9
- Author pages: 3 legacy author routes
- Index pages: `index.html`, `index2.html`, `index3.html`
- Listing pages: `archives.html`, `tags.html`, `authors.html`, `categories.html`
- Feeds: 10 XML files including `/feeds/all.atom.xml`

### Current feature inventory
- Dark/light mode
- Long-form reading-oriented article layout
- Archives and tags
- RSS/Atom feeds
- Google Analytics (GA4)
- Disqus comments
- Photography gallery with:
  - filters
  - lightbox
  - EXIF/GPS metadata
  - CC BY 4.0 download/license UI
  - local thumbnail pipeline

## Implementation shape

### App structure
Build the new site in `site/` using Astro latest.

High-level structure:

- `site/src/content/` — Astro content collections
- `site/src/pages/` — route-preserving page files
- `site/src/components/` — shared UI
- `site/src/layouts/` — base and prose layouts
- `site/src/data/` — project, navigation, and photography data
- `site/scripts/` — migration/sync utilities

### Content strategy
Do not edit Pelican source files in place.

Instead:

1. Keep legacy source in `content/`
2. Add a migration script that converts Pelican metadata into Astro frontmatter
3. Generate normalized Astro collection files into `site/src/content/`
4. Replace Pelican-specific content markers like `{static}/images/...` during migration

### Static asset strategy
Keep existing assets in the repo, but sync them into Astro’s public surface via script.

Assets to preserve:
- `content/images/**`
- `content/extra/CNAME`

### Route strategy in Astro
Use route-preserving Astro pages with `build.format = 'file'` so output stays on legacy `.html` URLs.

Current implementation shape:

- `src/pages/[slug].astro` → `/<slug>.html`
- `src/pages/pages/[slug].astro` → `/pages/<slug>.html`
- `src/pages/archives.astro` → `/archives.html`
- `src/pages/tags.astro` → `/tags.html`
- `src/pages/tag/[slug].astro` → `/tag/<slug>.html`
- `src/pages/categories.astro` → `/categories.html`
- `src/pages/category/[slug].astro` → `/category/<slug>.html`
- `src/pages/feeds/all.atom.xml.ts` → `/feeds/all.atom.xml`

Important note:
- the new Writing landing page currently builds to `/writing.html`
- `/writing` and `/writing/` are only aliases via Cloudflare `_redirects`
- this is acceptable only if we make the canonical/redirect decision explicit and test it on the real host, because local/static previews will not always model platform rewrites perfectly

### Reading-first implementation priorities
The first high-value build target is the article experience:

- calm typography
- strong code block styling
- good table/list/blockquote defaults
- deep-linkable headings
- desktop TOC where useful
- dark mode parity
- image and figure handling for diagrams/charts
- preserved Disqus threads unless replaced explicitly later
- parity for legacy markdown behaviors that affect reading quality or semantics, especially shared abbreviations/tooltips and legacy heading-link behavior

### Photography system shape
Use a generated dataset and override layer.

Planned files:
- `site/src/data/photography/generated/unsplash-photos.json`
- `site/src/data/photography/overrides.json`
- `site/scripts/sync-unsplash.mjs`

Normalized data fields should include at least:
- Unsplash photo id
- slug
- title
- description
- alt text
- dimensions
- color / blur hash
- publish date
- tags/topics
- exif
- location
- editorial categories
- featured / hidden flags
- ordering metadata
- Unsplash links including download tracking metadata

## Fresh-eyes review findings after the first Astro scaffold

### 1) The plan and the implementation had drifted on route-file strategy
The written plan still referenced `.html.astro` route files, but the working implementation now uses normal `.astro` files plus `build.format = 'file'` to emit `.html` output. The plan must describe the real mechanism, not the earlier draft.

### 2) The new Writing route is still a product/hosting decision, not a finished launch decision
The current Astro build emits `/writing.html`, while clean `/writing` and `/writing/` paths depend on Cloudflare `_redirects` aliases. That is a reasonable temporary setup, but it is still a decision point:

- either canonicalize `writing` to `/writing.html`
- or make `/writing/` the public canonical and treat `/writing.html` as implementation detail via verified hosting rewrites

This must be decided explicitly before launch to avoid canonical confusion.

### 3) Feed continuity is not finished just because feed endpoints exist
The legacy Atom feed includes full rendered article content, stable ids, and specific published/updated behavior. The current Astro feed scaffold preserves the endpoints, but feed parity still needs a careful pass so readers do not get a degraded feed experience.

### 4) Markdown/content parity still needs continued spot checks
Legacy Pelican rendering used a custom shared-abbreviations plugin plus specific markdown extensions. The Astro scaffold now restores shared acronym expansion and tooltip behavior on rendered pages, but markdown parity still needs spot checks anywhere legacy rendering details might affect semantics or reading quality.

### 5) Photography is scaffolded, not launch-ready
The Unsplash sync layer exists, but the actual user experience is still incomplete relative to requirements. Remaining gaps include:

- true detail/lightbox view
- stronger EXIF/location presentation
- explicit, approved download behavior for Unsplash-hosted assets
- final attribution/legal copy review
- real populated sync data from production credentials

### 6) The current Unsplash sync approach needs an incremental/cached plan
The initial sync script does paginated user-photo fetches plus per-photo detail fetches. That is fine for scaffolding, but it should not stay naïve forever. Add incremental caching and re-sync rules so the build/manual workflow remains fast and respectful of API limits.

### 7) Generated content and synced assets need stronger guardrails
Two operational rules need to be explicit in the plan:

- `site/src/content/**` is generated output and should not be hand-edited
- `site/public/images/**` is currently a synced legacy-asset namespace and should not become a dumping ground for unrelated Astro-owned assets

### 8) Comment strategy should be recorded explicitly
The design handoff recommended Giscus, but the current implementation preserves Disqus for continuity. For phase 1, the plan should record that comments remain on Disqus unless the owner approves a migration.

### 9) Build success is not enough verification
The Astro build now succeeds, but launch readiness still requires a route diff, feed diff, metadata diff, and spot checks against the current generated `output/` site.

## Deployment strategy

### Preferred launch target
Cloudflare Pages for the Astro site.

### Safe rollout
1. Build Astro site in parallel while Pelican remains live
2. Add preview/staging deploys first
3. Keep `gh-pages` flow untouched until Astro output is ready
4. Prepare redirect/canonical map and rollback steps
5. Cut over only after route parity, feed parity, and live checks pass

### Existing production caveat
Current live publishing still depends on `gh-pages`. Source pushes to `master` do not update the live site.

## Risks to manage early

- Unsplash API credentials are required for real sync runs
- Unsplash license/download UX must stay explicit and compliant
- Legacy author routes and paginated index routes need intentional handling
- Feed continuity must be preserved for existing readers, including full-content Atom behavior
- Comment migration is deferred unless explicitly approved; default phase-1 behavior is Disqus preservation
- Existing analytics path continuity depends on keeping legacy paths canonical
- Platform-level route aliases like `/writing/` must be verified on the real host, not assumed from local preview behavior
- Markdown feature gaps, especially shared abbreviations/tooltips, can quietly degrade reading quality if left unported
- Generated-content and synced-asset directories need clear ownership to avoid accidental manual edits or asset clobbering

## Phase breakdown

### Phase 0
- complete audit
- write implementation plan
- lock URL policy
- lock photography source model

### Phase 1
- scaffold Astro foundation in `site/`
- add content migration + asset sync scripts
- establish design tokens, layouts, nav, theme system, SEO primitives
- document generated-file ownership clearly (`site/src/content/**` and synced `public/images/**`)
- resolve the public/canonical strategy for the new Writing landing route

### Phase 2
- implement article/detail experience and writing index
- verify route-preserved article pages
- port or pre-expand legacy markdown behaviors that materially affect reading quality, especially shared abbreviations/tooltips

### Phase 3
- migrate about/projects/photography/archives/tags/feeds
- do a feed-parity pass against Pelican output, including full-content Atom behavior and stable ids
- diff Astro route output against current `output/` for launch-critical paths

### Phase 4
- add Unsplash sync layer and override model
- add incremental caching/re-sync behavior so the API workflow does not stay N+1 and fragile

### Phase 5
- finish photography UX and launch-readiness work
- implement approved Unsplash-hosted download/detail behavior
- add detail/lightbox and stronger EXIF/location presentation

### Phase 6
- deployment, cutover, rollback, and post-launch verification
- verify canonical, redirect, and alias behavior on actual Cloudflare Pages/Cloudflare edge infrastructure
