#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pillow>=10.0.0",
#     "piexif>=1.1.3",
#     "transformers>=4.36.0",
#     "torch>=2.0.0",
#     "einops>=0.8.0",
# ]
# ///
"""
Smart photo manager using Moondream2 for image understanding.
Moondream2 is a tiny (1.86B) but powerful vision-language model.
Works with any filename - uses AI to understand content.
"""

import os
import json
import hashlib
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import piexif

# For image understanding with Moondream2
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

# Enable MPS fallback for ops not implemented on Apple Silicon
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

class SmartPhotoManager:
    def __init__(self):
        self.source_dir = Path("content/images/photography")
        self.thumb_dir = self.source_dir / "thumbnails"
        self.metadata_file = self.source_dir / "gallery_metadata.json"
        
        # Much larger thumbnail sizes for better visibility
        self.sizes = {
            'small': (1600, 1600, 94),
            'medium': (2000, 2000, 95),
            'large': (2400, 2400, 96)
        }
        
        # Load existing metadata
        self.metadata = {}
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        
        # Initialize Moondream2 model for image understanding
        print("🌙 Loading Moondream2 - Tiny but powerful vision model...")
        print("   Only 1.86B parameters - optimized for your Mac!")
        
        try:
            # Detect device - prefer MPS (Apple Silicon) over CPU
            if torch.backends.mps.is_available():
                self.device = "mps"
                print("   🍎 Apple Silicon detected - using MPS acceleration!")
            elif torch.cuda.is_available():
                self.device = "cuda"
                print("   🎮 NVIDIA GPU detected - using CUDA!")
            else:
                self.device = "cpu"
                print("   💻 Using CPU (still fast with Moondream2!)")
            
            # Load Moondream2 - a tiny but powerful vision-language model
            model_id = "vikhyatk/moondream2"
            
            # Load tokenizer (Moondream2 doesn't need a separate processor)
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            
            # Load model with appropriate dtype for device
            if self.device in ["mps", "cuda"]:
                torch_dtype = torch.float16
            else:
                torch_dtype = torch.float32
                
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                trust_remote_code=True
            )
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.ai_available = True
            print("   ✨ Moondream2 ready! Fast, creative captions on your device.")
        except Exception as e:
            print(f"   ⚠️  Could not load Moondream2: {e}")
            print("   Falling back to basic analysis")
            self.ai_available = False
    
    def understand_image(self, img_path):
        """Use Moondream2 to understand what's in the image and generate creative titles."""
        if not self.ai_available:
            return self.basic_analysis(img_path)
        
        try:
            img = Image.open(img_path).convert('RGB')
            
            # Encode image once using Moondream2's method
            enc_image = self.model.encode_image(img)
            
            # Helper function to ask questions about the image with longer responses
            def ask_moondream(prompt, max_tokens=256):
                return self.model.answer_question(enc_image, prompt, self.tokenizer, max_new_tokens=max_tokens)
            
            # Generate various descriptions with longer token limits for complete responses
            caption = ask_moondream("Describe this photograph in detail.", max_tokens=300)
            title = ask_moondream("Create a creative, artistic title for this photo (2-4 words only):", max_tokens=50)
            poetic_desc = ask_moondream("Describe this photo in a poetic, evocative way:", max_tokens=300)
            elements = ask_moondream("What are the main subjects or elements in this photo?")
            mood = ask_moondream("What is the mood or atmosphere of this photo?")
            
            # Clean up title
            title = title.strip('"\'.,!').strip()
            if len(title.split()) > 5:
                title = ' '.join(title.split()[:4])
            
            # Extract keywords from all text
            all_text = f"{caption} {elements}".lower()
            words = all_text.split()
            skip_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'of', 'with', 'in', 'on', 'at', 'to', 'and', 'very', 'this', 'that', 'it', 'be', 'have', 'has'}
            
            keywords = []
            for word in words:
                word = word.strip('.,!?;:\'"-')
                if len(word) > 3 and word not in skip_words and word not in keywords:
                    keywords.append(word)
                    if len(keywords) >= 8:
                        break
            
            # Use poetic description if it's good, otherwise use detailed caption
            final_caption = poetic_desc if len(poetic_desc) > 20 else caption
            
            return {
                'caption': final_caption,
                'title': title.title() if title else "Untitled",
                'descriptions': [caption, poetic_desc, mood],
                'keywords': keywords,
                'elements': elements,
                'ai_model': 'Moondream2'
            }
            
        except Exception as e:
            print(f"  ⚠️  AI analysis failed: {e}")
            return self.basic_analysis(img_path)
    
    def basic_analysis(self, img_path):
        """Fallback basic analysis if AI is not available."""
        return {
            'caption': 'Photo',
            'descriptions': [],
            'keywords': [],
            'ai_model': 'basic'
        }
    
    def categorize_from_ai(self, ai_analysis, exif_data):
        """Categorize based on AI understanding and EXIF."""
        caption = ai_analysis.get('caption', '').lower()
        keywords = ai_analysis.get('keywords', [])
        elements = ai_analysis.get('elements', '').lower()
        keywords_str = ' '.join(keywords).lower()
        all_text = f"{caption} {keywords_str} {elements}"
        
        # Category mapping based on AI understanding
        category_patterns = {
            'astronomy': ['moon', 'star', 'galaxy', 'eclipse', 'night sky', 'constellation', 'milky way', 'lunar', 'celestial'],
            'portrait': ['person', 'people', 'man', 'woman', 'face', 'portrait', 'selfie', 'human'],
            'nature': ['tree', 'forest', 'mountain', 'lake', 'river', 'landscape', 'nature', 'outdoor', 'hiking'],
            'urban': ['city', 'building', 'street', 'skyline', 'urban', 'downtown', 'traffic', 'cityscape'],
            'architecture': ['building', 'architecture', 'structure', 'bridge', 'interior', 'design', 'cathedral', 'clock tower'],
            'wildlife': ['animal', 'bird', 'wildlife', 'zoo', 'pet', 'dog', 'cat'],
            'food': ['food', 'meal', 'dish', 'restaurant', 'cooking', 'cuisine', 'cafe'],
            'sunset': ['sunset', 'sunrise', 'golden hour', 'dusk', 'dawn'],
            'night': ['night', 'dark', 'evening', 'lights', 'nocturnal'],
            'street': ['street', 'road', 'sidewalk', 'people walking', 'pedestrian'],
            'macro': ['close-up', 'macro', 'detail', 'texture'],
            'beach': ['beach', 'ocean', 'sea', 'sand', 'coast', 'waves', 'waterfront'],
            'sports': ['sport', 'game', 'playing', 'running', 'athlete']
        }
        
        # Check each category
        category_scores = {}
        for category, patterns in category_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in all_text:
                    score += 2  # Direct text match
                if pattern in keywords_str:
                    score += 1  # Keyword match bonus
            if score > 0:
                category_scores[category] = score
        
        # Return the best matching category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category
        
        # Check EXIF for additional hints
        focal = exif_data.get('settings', {}).get('focal_length_num', 0)
        if focal > 200:
            return 'telephoto'  # Long lens shots
        
        hour = exif_data.get('hour', 12)
        if hour < 6 or hour > 20:
            return 'night'
        
        return 'general'
    
    def extract_exif_data(self, img_path):
        """Extract comprehensive EXIF data including GPS."""
        exif_data = {
            'camera': {},
            'settings': {},
            'gps': {},
            'datetime': None
        }
        
        try:
            img = Image.open(img_path)
            exif = img._getexif()
            
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Camera info
                    if tag == 'Make':
                        exif_data['camera']['make'] = str(value).strip()
                    elif tag == 'Model':
                        exif_data['camera']['model'] = str(value).strip()
                    elif tag == 'LensModel':
                        exif_data['camera']['lens'] = str(value).strip()
                    
                    # Settings
                    elif tag == 'ExposureTime':
                        try:
                            if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                                # Handle IFDRational type
                                exif_data['settings']['shutter'] = f"{value.numerator}/{value.denominator}s"
                            elif isinstance(value, tuple):
                                exif_data['settings']['shutter'] = f"{value[0]}/{value[1]}s"
                            else:
                                exif_data['settings']['shutter'] = f"1/{int(1/float(value))}s" if value else None
                        except:
                            pass
                    elif tag == 'FNumber':
                        try:
                            if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                                # Handle IFDRational type
                                f_num = float(value.numerator) / float(value.denominator)
                                exif_data['settings']['aperture'] = f"f/{f_num:.1f}"
                            elif isinstance(value, tuple):
                                exif_data['settings']['aperture'] = f"f/{float(value[0])/float(value[1]):.1f}"
                            else:
                                exif_data['settings']['aperture'] = f"f/{value}"
                        except:
                            pass
                    elif tag == 'ISOSpeedRatings':
                        exif_data['settings']['iso'] = f"ISO {value}"
                    elif tag == 'FocalLength':
                        try:
                            if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                                # Handle IFDRational type
                                focal = float(value.numerator) / float(value.denominator)
                                exif_data['settings']['focal_length'] = f"{focal:.1f}mm"
                                exif_data['settings']['focal_length_num'] = focal
                            elif isinstance(value, tuple):
                                focal = float(value[0])/float(value[1])
                                exif_data['settings']['focal_length'] = f"{focal:.1f}mm"
                                exif_data['settings']['focal_length_num'] = focal
                            else:
                                exif_data['settings']['focal_length'] = f"{value}mm"
                                exif_data['settings']['focal_length_num'] = float(value)
                        except:
                            pass
                    
                    # Date/Time
                    elif tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        if not exif_data['datetime'] and value:
                            try:
                                dt = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                                exif_data['datetime'] = dt.isoformat()
                                exif_data['hour'] = dt.hour
                            except:
                                exif_data['datetime'] = str(value)
                    
                    # GPS Info
                    elif tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag in value:
                            sub_tag = GPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_tag] = value[gps_tag]
                        
                        if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                            lat = self.convert_gps_coord(gps_data['GPSLatitude'])
                            lon = self.convert_gps_coord(gps_data['GPSLongitude'])
                            
                            if gps_data.get('GPSLatitudeRef') == 'S':
                                lat = -lat
                            if gps_data.get('GPSLongitudeRef') == 'W':
                                lon = -lon
                            
                            exif_data['gps']['latitude'] = lat
                            exif_data['gps']['longitude'] = lon
                            exif_data['gps']['coordinates'] = f"{lat:.6f}, {lon:.6f}"
                            
                            # Try to get location name (optional enhancement)
                            exif_data['gps']['location'] = self.get_location_name(lat, lon)
        except:
            pass
        
        return exif_data
    
    def get_location_name(self, lat, lon):
        """Get location name from coordinates (returns coordinates if can't resolve)."""
        # For now, just return formatted coordinates
        # Could be enhanced with reverse geocoding API in future
        return f"{lat:.4f}, {lon:.4f}"
    
    def convert_gps_coord(self, coord):
        """Convert GPS coordinates to decimal degrees."""
        try:
            deg, min, sec = coord
            
            # Handle IFDRational types
            if hasattr(deg, 'numerator') and hasattr(deg, 'denominator'):
                deg = float(deg.numerator) / float(deg.denominator)
            elif isinstance(deg, tuple):
                deg = float(deg[0]) / float(deg[1])
            else:
                deg = float(deg)
            
            if hasattr(min, 'numerator') and hasattr(min, 'denominator'):
                min = float(min.numerator) / float(min.denominator)
            elif isinstance(min, tuple):
                min = float(min[0]) / float(min[1])
            else:
                min = float(min)
            
            if hasattr(sec, 'numerator') and hasattr(sec, 'denominator'):
                sec = float(sec.numerator) / float(sec.denominator)
            elif isinstance(sec, tuple):
                sec = float(sec[0]) / float(sec[1])
            else:
                sec = float(sec)
            
            return deg + (min / 60.0) + (sec / 3600.0)
        except:
            return 0
    
    def generate_thumbnails(self, img_path):
        """Generate thumbnails for an image."""
        with Image.open(img_path) as img:
            # Handle EXIF orientation
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except:
                pass
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            results = {}
            for size_name, (max_size, _, quality) in self.sizes.items():
                thumb = img.copy()
                thumb.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                thumb_path = self.thumb_dir / f"{img_path.stem}_{size_name}.jpg"
                thumb.save(thumb_path, "JPEG", quality=quality, optimize=True, progressive=True)
                
                results[size_name] = thumb.size
            
            return results, img.size
    
    def process_image(self, img_path):
        """Process a single image."""
        # Check if already processed
        file_hash = hashlib.md5(img_path.read_bytes()).hexdigest()
        
        if img_path.name in self.metadata:
            if self.metadata[img_path.name].get('hash') == file_hash:
                # Check if thumbnails exist
                all_exist = all(
                    (self.thumb_dir / f"{img_path.stem}_{size}.jpg").exists()
                    for size in self.sizes.keys()
                )
                if all_exist:
                    return False
        
        print(f"\n📷 Processing {img_path.name}")
        
        # Extract EXIF data
        print("  📍 Extracting EXIF data...")
        exif_data = self.extract_exif_data(img_path)
        
        # AI analysis
        print("  🤖 Understanding image content...")
        ai_analysis = self.understand_image(img_path)
        
        # Smart categorization
        category = self.categorize_from_ai(ai_analysis, exif_data)
        
        # Use creative AI title or caption
        title = ai_analysis.get('title', ai_analysis.get('caption', 'Photo'))
        if title and len(title) > 50:
            title = title[:47] + "..."
        
        # Generate thumbnails
        print("  🖼️  Generating thumbnails...")
        thumb_sizes, original_size = self.generate_thumbnails(img_path)
        
        # Create metadata
        self.metadata[img_path.name] = {
            'filename': img_path.name,
            'title': title,
            'description': ai_analysis.get('caption', ''),
            'category': category,
            'keywords': ai_analysis.get('keywords', []),
            'original_size': original_size,
            'thumbnail_sizes': thumb_sizes,
            'exif': exif_data,
            'ai_analysis': ai_analysis,
            'hash': file_hash,
            'processed': datetime.now().isoformat()
        }
        
        # Display info
        print(f"  🏷️  Category: {category}")
        print(f"  📝 AI says: {ai_analysis.get('caption', 'Could not analyze')[:60]}...")
        
        if ai_analysis.get('keywords'):
            print(f"  🔖 Keywords: {', '.join(ai_analysis['keywords'][:5])}")
        
        if exif_data['camera']:
            camera = f"{exif_data['camera'].get('make', '')} {exif_data['camera'].get('model', '')}"
            if camera.strip():
                print(f"  📷 Camera: {camera}")
        
        return True
    
    def update_gallery_page(self):
        """Update the photography.md page with all photos from metadata."""
        print("\n📝 Updating gallery page with all photos...")
        
        page_path = Path("content/pages/photography.md")
        if not page_path.exists():
            print("  ❌ Photography page not found!")
            return
        
        # Read current page
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Find the gallery section
        start_marker = '<div class="photo-masonry" id="photoGallery">'
        end_marker = '</div>\n\n<!-- Lightbox Modal -->'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("  ⚠️  Could not find gallery markers in page")
            return
        
        # Generate photo cards for all images
        photo_cards = [start_marker]
        
        # Sort photos by: 1) manual order, 2) date taken, 3) filename
        def sort_key(item):
            filename, data = item
            # Priority 1: Manual order (if specified)
            manual_order = data.get('order', 9999)
            # Priority 2: Date taken from EXIF
            date_taken = data.get('exif', {}).get('datetime', '')
            # Priority 3: Filename for consistent ordering
            return (manual_order, date_taken if date_taken else 'z' + filename, filename)
        
        for filename, data in sorted(self.metadata.items(), key=sort_key):
            stem = Path(filename).stem
            title = data.get('title', 'Photo')
            # Use the longest description from the descriptions array, or fall back to caption
            ai_analysis = data.get('ai_analysis', {})
            descriptions = ai_analysis.get('descriptions', [])
            if descriptions:
                # Use the longest description for better quality
                description = max(descriptions, key=len) if descriptions else ai_analysis.get('caption', '')
            else:
                description = data.get('description', ai_analysis.get('caption', ''))
            category = data.get('category', 'general')
            
            # Check if GPS location is available
            location_html = ""
            if data.get('exif', {}).get('gps', {}).get('coordinates'):
                gps_data = data['exif']['gps']
                location_display = gps_data.get('location', gps_data['coordinates'])
                location_html = f'''        <div class="photo-location">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
            </svg>
            <span>{location_display}</span>
        </div>
'''
            
            card = f'''    <div class="photo-card" data-category="{category}" data-full="/images/photography/{filename}">
{location_html}        <img src="/images/photography/thumbnails/{stem}_small.jpg" 
             data-medium="/images/photography/thumbnails/{stem}_large.jpg"
             alt="{title}" loading="lazy">
        <div class="photo-overlay">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    </div>'''
            photo_cards.append(card)
        
        photo_cards.append('</div>')
        
        # Replace gallery content
        new_content = content[:start_idx] + '\n'.join(photo_cards) + content[end_idx:]
        
        # Update filter buttons with categories
        categories = sorted(set(d.get('category', 'general') for d in self.metadata.values()))
        
        filter_start = '<div class="photo-filters">'
        filter_end = '</div>\n\n<div class="photo-masonry"'
        
        filter_start_idx = new_content.find(filter_start)
        filter_end_idx = new_content.find(filter_end)
        
        if filter_start_idx != -1 and filter_end_idx != -1:
            filters = [filter_start]
            filters.append('    <button class="filter-btn active" data-filter="all">All</button>')
            for cat in categories:
                count = sum(1 for d in self.metadata.values() if d.get('category') == cat)
                filters.append(f'    <button class="filter-btn" data-filter="{cat}">{cat.title()} ({count})</button>')
            filters.append('</div>\n')
            
            new_content = new_content[:filter_start_idx] + '\n'.join(filters) + new_content[filter_end_idx:]
        
        # Write updated page
        with open(page_path, 'w') as f:
            f.write(new_content)
        
        print(f"  ✅ Gallery updated with {len(self.metadata)} photos")
        print(f"  📊 Categories: {', '.join(categories)}")
    
    def run(self):
        """Main workflow."""
        print("=" * 60)
        print("🤖 SMART PHOTO MANAGER with AI Understanding")
        print("Works with any filename - AI understands your photos!")
        print("=" * 60)
        
        # Ensure directories exist
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all images
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        image_files = []
        for ext in extensions:
            image_files.extend(self.source_dir.glob(ext))
        
        # Filter out thumbnails
        image_files = [f for f in image_files if 'thumbnails' not in str(f)]
        
        print(f"\n📁 Found {len(image_files)} images")
        if self.ai_available:
            print("   ✨ Using Moondream2 for intelligent image understanding")
            print("   🚀 Faster and more creative than larger models!")
        else:
            print("   ⚠️  AI not available, using basic analysis")
        
        # Process images
        processed = 0
        for img_path in sorted(image_files):
            if self.process_image(img_path):
                processed += 1
        
        # Save metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Update gallery page with all photos
        self.update_gallery_page()
        
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE - Processed {processed} new/updated images")
        print(f"📊 Total images in gallery: {len(self.metadata)}")
        print("\n💡 Gallery page has been updated!")
        print("   Just rebuild to see your photos!")
        print("=" * 60)

if __name__ == "__main__":
    manager = SmartPhotoManager()
    manager.run()