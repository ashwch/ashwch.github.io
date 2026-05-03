# Future subdomain adoption notes

## Recommended model

Use `ashwch.com` as the brand hub and shared visual system origin.

### Tier A — documentation-heavy properties
Use Astro + Starlight with shared brand tokens and footer/header conventions.

Good fit:
- `auto-uv-env.ashwch.com`

### Tier B — custom product surfaces
Use custom Astro builds that consume the shared ashwch tokens/components.

Good fit:
- `microverse.ashwch.com`

### Tier C — media/editorial properties
Keep a content-first shell while reusing shared typography, spacing, footer, and ecosystem navigation patterns.

Good fit:
- `codessey-podcast.ashwch.com`

## Shared pieces to standardize first

- color and typography tokens
- header/footer conventions
- subdomain switcher behavior
- metadata/SEO defaults
- analytics bootstrapping
- dark-mode behavior

## What should not be forced too early

- one monorepo for every property
- one information architecture for all properties
- one component set for every domain-specific need

The main site should prove the system first. Subdomains can adopt it incrementally.
