# Photography Workflow

This is the current photography workflow for the live Astro-based `ashwch.com` site.

## Source of truth

Photography source files live in:

- `content/images/photography/`

Generated metadata and thumbnails live alongside them:

- `content/images/photography/gallery_metadata.json`
- `content/images/photography/thumbnails/`

The Astro site then syncs those assets into `site/public/` during build.

## Add new photos

1. Copy originals into:

```bash
content/images/photography/
```

2. Process them:

```bash
uv run scripts/photo_manager.py
```

This updates:
- AI-generated titles/descriptions
- EXIF/GPS metadata
- thumbnails
- gallery metadata cache

## Regenerate everything

If you want to rebuild all metadata/thumbnails from scratch:

```bash
# Re-run the processor after clearing or editing metadata if you want a full refresh
uv run scripts/photo_manager.py
```

## Set manual order

```bash
python3 scripts/set_photo_order.py
```

This updates manual ordering in the gallery metadata.

## Preview in Astro

From `site/`:

```bash
pnpm dev
```

Or run validation builds:

```bash
pnpm check
pnpm build
```

## Notes

- Root `content/images/**` is still the asset source of truth.
- Do not hand-edit generated Astro content under `site/src/content/**`.
- Historical Pelican-era photography workflow notes are preserved in `archive/pelican/docs/workflows/PHOTOGRAPHY_WORKFLOW.md`.
