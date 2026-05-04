# Photography Gallery Workflow

This guide covers the complete workflow for managing the AI-powered photography gallery on ashwch.com.

## Overview

The photography gallery uses Moondream2 (1.86B parameter vision-language model) to automatically understand and describe photos, generate creative titles, and categorize images - all without requiring descriptive filenames.

## Directory Structure

```
content/images/photography/
├── *.jpg, *.jpeg, *.png       # Original photos (any filename)
├── thumbnails/                 # Auto-generated thumbnails
│   ├── *_small.jpg            # 1600px thumbnails for gallery
│   ├── *_medium.jpg           # 2000px for medium display
│   └── *_large.jpg            # 2400px for lightbox view
└── gallery_metadata.json       # AI-generated metadata cache
```

## Adding New Photos

### Step 1: Add Photos
Simply copy your photos to the photography directory:
```bash
cp your-photos/*.jpg content/images/photography/
```

**Supported formats:** JPG, JPEG, PNG
**Naming:** Any filename works! (IMG_3197.JPG, DSC0001.jpg, photo.jpg, etc.)

### Step 2: Process with AI
Run the photo update command:
```bash
./blog.sh photos update
```

This will:
1. Detect new/changed photos
2. Use Moondream2 AI to:
   - Generate creative titles
   - Write detailed descriptions
   - Extract keywords
   - Determine categories
3. Extract EXIF data (camera, settings, GPS)
4. Generate optimized thumbnails
5. Update the gallery page automatically

### Step 3: Build & Preview
```bash
./blog.sh build
./blog.sh serve
```
Visit http://localhost:8000/pages/photography.html

## Gallery Management Commands

All commands are available through `blog.sh`:

### Process New Photos
```bash
./blog.sh photos update
```
- Processes only new/changed photos
- Preserves existing metadata
- Rebuilds gallery page

### Force Regenerate Everything
```bash
./blog.sh photos regenerate
```
- Clears all metadata
- Regenerates all thumbnails
- Reprocesses all photos with AI

### Set Manual Photo Order
```bash
./blog.sh photos order
```
Interactive tool to:
- Set specific order for photos
- Override automatic ordering (by date/filename)
- Reset to automatic ordering

Example session:
```
Current photos in gallery:
 1. [auto]   IMG_3197.JPG                  - Ocean's Edge
 2. [auto]   moon-1.jpg                    - Full Moon
 3. [auto]   sunset.jpg                    - Golden Hour

Enter: 'filename order' (e.g., 'moon-1.jpg 1')
Or: 'all auto' to reset to automatic ordering
Or: 'done' to finish

> moon-1.jpg 1
✅ Set moon-1.jpg to order 1
> sunset.jpg 2
✅ Set sunset.jpg to order 2
> done
```

### View Gallery Statistics
```bash
./blog.sh photos stats
```
Shows:
- Total photos and thumbnails
- Storage usage
- Photos per category
- Processing status

### Clean Orphaned Files
```bash
./blog.sh photos clean
```
Removes thumbnails for deleted original photos.

## Photo Ordering System

Photos are sorted by (in priority order):
1. **Manual order** - Set via `photos order` command
2. **EXIF date taken** - When the photo was captured
3. **Filename** - Alphabetical fallback

This ensures consistent ordering across regenerations.

## AI Features

### Moondream2 Capabilities
- **Intelligent Understanding:** Recognizes subjects, scenes, composition
- **Creative Titles:** Generates artistic 2-4 word titles
- **Detailed Descriptions:** Writes comprehensive photo descriptions
- **Smart Categorization:** Auto-assigns categories like:
  - astronomy (night sky, moon, stars)
  - portrait (people, faces)
  - nature (landscapes, trees, mountains)
  - urban (cities, buildings, streets)
  - architecture (buildings, structures)
  - beach (ocean, sand, coast)
  - And more...

### Hardware Acceleration
- **Apple Silicon (M1/M2/M3):** Uses MPS acceleration
- **NVIDIA GPUs:** CUDA acceleration
- **CPU Fallback:** Still fast with Moondream2's small size

## Gallery Features

### Thumbnail View
- Clean masonry layout
- Text overlays only on hover
- GPS location badges (when available)
- Responsive 1-3 columns

### Lightbox View
- Side-by-side layout (image + info panel)
- Full descriptions
- EXIF data display
- Download button with CC BY 4.0 license
- Previous/Next navigation

## Customization

### Modify Thumbnail Sizes
Edit `scripts/photo_manager.py`:
```python
self.sizes = {
    'small': (1600, 1600, 94),   # (max_width, max_height, quality)
    'medium': (2000, 2000, 95),
    'large': (2400, 2400, 96)
}
```

### Adjust AI Prompts
Modify prompts in `scripts/photo_manager.py`:
```python
caption = ask_moondream("Describe this photograph in detail.", max_tokens=300)
title = ask_moondream("Create a creative, artistic title for this photo (2-4 words only):", max_tokens=50)
```

### Change Categories
Edit category patterns in `scripts/photo_manager.py`:
```python
category_patterns = {
    'astronomy': ['moon', 'star', 'galaxy', ...],
    'portrait': ['person', 'people', 'face', ...],
    # Add your own...
}
```

## Troubleshooting

### Photos Not Processing
1. Check file permissions
2. Ensure valid image format (JPG/PNG)
3. Check for corrupt EXIF data
4. Run with regenerate flag

### AI Not Working
1. Check Moondream2 installation:
   ```bash
   pip install transformers torch einops
   ```
2. Verify MPS/CUDA availability
3. Check memory usage (needs ~4GB RAM)

### Thumbnails Missing
1. Check write permissions on `thumbnails/` directory
2. Verify Pillow installation:
   ```bash
   pip install Pillow
   ```
3. Run `./blog.sh photos regenerate`

### Wrong Orientation
- The system automatically handles EXIF orientation
- If issues persist, check original file's EXIF data

### Truncated Descriptions
- Descriptions are set to 300 tokens max
- Increase in `scripts/photo_manager.py` if needed

## Performance Tips

1. **Batch Processing:** Add multiple photos before running update
2. **Use MPS/CUDA:** Significantly faster than CPU
3. **Optimize Originals:** Resize extremely large photos (>10MB) before adding
4. **Cache Management:** Metadata is cached to avoid reprocessing

## Deployment

After updating photos locally:
```bash
./blog.sh build production
./blog.sh deploy
```

This deploys to GitHub Pages at https://ashwch.com/pages/photography.html

## File Locations

- **Scripts:** `scripts/photo_manager.py`, `scripts/set_photo_order.py`
- **Gallery Page:** `content/pages/photography.md`
- **Photos:** `content/images/photography/`
- **Output:** `output/images/photography/`
- **Metadata:** `content/images/photography/gallery_metadata.json`

## Dependencies

Required Python packages:
```bash
pip install pillow piexif transformers torch einops
```

Or with uv (recommended):
```bash
uv pip install pillow piexif transformers torch einops
```

## Tips & Best Practices

1. **Filename Independence:** Don't worry about naming - AI handles understanding
2. **EXIF Preservation:** Keep EXIF data for automatic dating and GPS
3. **Quality Settings:** Current settings optimized for web (94-96 quality)
4. **Regular Updates:** Run `photos update` after adding new photos
5. **Backup Originals:** Keep originals backed up separately

## Future Enhancements

Potential improvements to consider:
- WebP format support for smaller files
- Lazy loading for faster page loads
- EXIF-based search/filtering
- Tags from AI keywords
- Social sharing metadata

---

*Last updated: November 2024*