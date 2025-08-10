# Scripts Directory

This directory contains utility scripts for managing the blog and its content.

## Photo Management Scripts

### photo_manager.py
Smart photo management system using Moondream2 AI for image understanding.

**Features:**
- Automatic title and description generation using AI
- EXIF data extraction including GPS coordinates
- Thumbnail generation (1600px, 2000px, 2400px)
- Smart categorization based on image content
- MPS acceleration support for Apple Silicon

**Usage:**
```bash
python3 scripts/photo_manager.py [update|regenerate]
```

### set_photo_order.py
Interactive tool for manually ordering photos in the gallery.

**Features:**
- Set custom order for specific photos
- Reset to automatic ordering
- View current photo order

**Usage:**
```bash
python3 scripts/set_photo_order.py
```

## Running Scripts

All photo-related scripts are integrated with the main blog management script:

```bash
./blog.sh photos update      # Process new photos
./blog.sh photos regenerate  # Force regenerate all thumbnails
./blog.sh photos order       # Set manual photo ordering
./blog.sh photos stats       # Show gallery statistics
./blog.sh photos clean       # Remove orphaned thumbnails
```

## Dependencies

The photo management scripts require:
- Python 3.9+
- Pillow (image processing)
- piexif (EXIF data extraction)
- transformers & torch (for Moondream2 AI)
- einops (tensor operations)

Install with:
```bash
pip install pillow piexif transformers torch einops
```

Or use uv (recommended):
```bash
uv pip install pillow piexif transformers torch einops
```