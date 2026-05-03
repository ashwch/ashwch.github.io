# Scaling Photography Storage for 1000s of Photos

## Current Storage Limitations

### GitHub Repository Limits
- **Soft limit**: 1GB per repository
- **Hard limit**: 5GB per repository  
- **File size limit**: 100MB per file
- **GitHub Pages**: Serves from repository, inherits same limits
- **Git history**: Every photo creates permanent history, increasing repo size

### Current Setup Analysis
With your current setup (23 photos):
- Each photo has 3 thumbnails (small, medium, large)
- Estimated storage: 50-200MB currently
- At this rate, 1000 photos would be 2-8GB (exceeding limits)

## Recommended Hybrid Architecture

### What Stays in GitHub
✅ **Keep in repository:**
- Small thumbnails (800px, ~60-120KB each)
- Medium thumbnails (1600px, ~120-300KB each)  
- Gallery metadata JSON
- All Pelican site code and content
- Photography page and templates

### What Moves to External Storage
❌ **Store externally:**
- Original full-resolution photos
- Large display versions (2400px+)
- Any RAW files or very high-res versions

## External Storage Options Comparison

### 1. Cloudflare R2 (Recommended)
**Pros:**
- Free tier: 10GB storage, 10M requests/month
- Paid: $0.015/GB/month (very affordable)
- **Zero egress fees** (huge cost advantage)
- S3-compatible API
- Global CDN built-in
- Excellent for image delivery

**Setup:**
```python
# Example integration
import boto3

r2 = boto3.client('s3',
    endpoint_url='https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)
```

### 2. Backblaze B2
**Pros:**
- Free tier: 10GB storage
- Paid: $0.006/GB/month (cheapest storage)
- S3-compatible API
- Good reliability

**Cons:**
- Egress fees: $0.01/GB
- Not as fast as Cloudflare globally

### 3. AWS S3
**Pros:**
- Industry standard
- Excellent reliability
- Many integration options

**Cons:**
- More expensive: $0.023/GB/month
- Complex pricing (requests, egress)
- Overkill for personal photography

### 4. Self-Hosted (VPS/Dedicated)
**Pros:**
- Full control
- No storage limits
- One-time cost

**Cons:**
- Requires maintenance
- Need to handle CDN/caching
- Bandwidth limitations

## Implementation Architecture

### Modified Workflow

```
┌─────────────────────┐
│  Photo Upload       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Photo Manager      │
│  (AI Processing)    │
└──────────┬──────────┘
           │
           ├────────────────┐
           ▼                ▼
┌─────────────────┐  ┌─────────────────┐
│  GitHub          │  │  External       │
│  - Small thumb   │  │  - Original     │
│  - Medium thumb  │  │  - Large size   │
│  - Metadata      │  │                 │
└─────────────────┘  └─────────────────┘
           │                │
           ▼                ▼
┌─────────────────────────────────────┐
│  Photography Page                    │
│  - Gallery loads from GitHub         │
│  - Lightbox loads from External      │
└───────────────────────────────────────┘
```

### Modified Photo Manager Code Structure

```python
class PhotoManager:
    def process_photo(self, photo_path):
        # 1. Generate AI metadata (existing)
        metadata = self.analyze_with_ai(photo_path)
        
        # 2. Generate GitHub thumbnails
        small_thumb = self.create_thumbnail(photo_path, size='small')
        medium_thumb = self.create_thumbnail(photo_path, size='medium')
        
        # 3. Save to GitHub (existing)
        self.save_to_local(small_thumb, medium_thumb)
        
        # 4. Upload to external (new)
        if self.use_external_storage:
            large_thumb = self.create_thumbnail(photo_path, size='large')
            original_url = self.upload_to_r2(photo_path)
            large_url = self.upload_to_r2(large_thumb)
            metadata['external_urls'] = {
                'original': original_url,
                'large': large_url
            }
        
        return metadata
```

### Gallery Page Modifications

```javascript
// Progressive loading strategy
function openLightbox(photoData) {
    // 1. Show medium thumbnail immediately (from GitHub)
    lightbox.showImage(photoData.mediumUrl);
    
    // 2. Load large version from external storage
    if (photoData.externalUrls?.large) {
        const img = new Image();
        img.onload = () => lightbox.upgradeImage(photoData.externalUrls.large);
        img.src = photoData.externalUrls.large;
    }
}
```

## Storage Cost Calculations

### For 1000 Photos
Assuming average photo size of 5MB original, 500KB large thumb:

| Storage Type | GitHub | Cloudflare R2 | Total Monthly |
|-------------|--------|---------------|---------------|
| Thumbnails (small+medium) | ~300MB | - | Free |
| Originals + Large | - | ~5.5GB | $0.08 |
| Bandwidth | Included | Free | Free |
| **Total Cost** | **Free** | **$0.08** | **$0.08/month** |

### For 5000 Photos

| Storage Type | GitHub | Cloudflare R2 | Total Monthly |
|-------------|--------|---------------|---------------|
| Thumbnails | ~1.5GB | - | Free (under 5GB) |
| Originals + Large | - | ~27GB | $0.40 |
| **Total Cost** | **Free** | **$0.40** | **$0.40/month** |

## Migration Steps

### Phase 1: Setup External Storage
1. Create Cloudflare R2 account
2. Create bucket for photos
3. Configure CORS for your domain
4. Generate API credentials

### Phase 2: Modify Photo Manager
1. Add R2 upload functionality
2. Update metadata structure
3. Implement selective thumbnail generation
4. Test with small batch

### Phase 3: Update Gallery Page
1. Modify JavaScript to handle external URLs
2. Implement progressive loading
3. Add fallback for missing external URLs
4. Test loading performance

### Phase 4: Batch Migration (Optional)
1. Script to upload existing photos to R2
2. Update existing metadata files
3. Verify all links work
4. Clean up large files from GitHub

## Configuration Example

```python
# config.py
STORAGE_CONFIG = {
    'use_external': True,
    'external_provider': 'r2',
    
    # GitHub storage (thumbnails)
    'github_sizes': ['small', 'medium'],
    
    # External storage (full size)
    'external_sizes': ['large', 'original'],
    
    # R2 Configuration
    'r2': {
        'endpoint': 'https://xxx.r2.cloudflarestorage.com',
        'access_key': 'env:R2_ACCESS_KEY',
        'secret_key': 'env:R2_SECRET_KEY',
        'bucket': 'photography',
        'public_url': 'https://photos.ashwch.com'  # Custom domain
    }
}
```

## Performance Optimizations

### CDN Strategy
1. **GitHub Pages**: Serves thumbnails with GitHub's CDN
2. **Cloudflare R2**: Automatic global CDN
3. **Browser caching**: Set long cache headers
4. **Lazy loading**: Load images only when needed

### Image Optimization
```python
# Recommended sizes and quality
THUMBNAIL_CONFIGS = {
    'small': {
        'size': (800, 800),    # Reduced for gallery grid
        'quality': 85,          # Lower quality acceptable
        'format': 'JPEG'
    },
    'medium': {
        'size': (1600, 1600),  # Good for preview
        'quality': 90,
        'format': 'JPEG'
    },
    'large': {
        'size': (2400, 2400),  # External storage only
        'quality': 95,
        'format': 'JPEG'
    }
}
```

## Backup Strategy

### Recommended 3-2-1 Backup
1. **Original photos**: Your local computer
2. **Cloud backup**: Google Photos, iCloud, or Dropbox
3. **External storage**: Cloudflare R2
4. **GitHub**: Thumbnails and metadata
5. **Optional**: Additional backup to B2 or personal NAS

## Summary

### For Your Use Case (1000s of photos)
✅ **Recommended approach:**
- Use **Cloudflare R2** for originals and large versions
- Keep thumbnails in **GitHub** for fast gallery loading
- Implement **progressive loading** in lightbox
- Total cost: Under $1/month for thousands of photos

### Benefits
- ✅ Unlimited photo scaling
- ✅ Fast gallery loading (thumbnails from GitHub CDN)
- ✅ High-quality lightbox (from R2 CDN)
- ✅ Very low cost
- ✅ No bandwidth charges
- ✅ Maintains your current workflow

### Next Steps
1. Sign up for Cloudflare R2
2. Test with a small batch of photos
3. Gradually migrate to hybrid approach
4. Monitor storage usage and costs

---

*This document provides a scalable solution for hosting thousands of photos while maintaining the simplicity of your GitHub Pages setup and keeping costs minimal.*
