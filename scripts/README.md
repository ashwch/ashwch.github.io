# Scripts Directory

This directory contains current helper scripts for content and photography workflows.

## Active scripts

### `photo_manager.py`
Smart photo management using Moondream2 for image understanding.

What it does:
- generates titles and descriptions
- extracts EXIF and GPS data
- creates photography thumbnails
- updates gallery metadata in `content/images/photography/gallery_metadata.json`

Usage:
```bash
uv run scripts/photo_manager.py
```

### `set_photo_order.py`
Interactive helper for manually ordering photos in the gallery metadata.

Usage:
```bash
python3 scripts/set_photo_order.py
```

### `generate_no_code_by_hand_charts.py`
One-off chart generator used for the “No Code by Hand” article assets.

## Notes

- These scripts operate on the root `content/` tree.
- The Astro app in `site/` picks up the resulting content and images during `pnpm sync` / `pnpm build`.
- Historical Pelican-era wrappers now live in `archive/pelican/`.
