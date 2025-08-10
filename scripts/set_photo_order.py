#!/usr/bin/env python3
"""
Set manual order for photos in the gallery.
Usage: python set_photo_order.py

This allows you to manually control the order of photos in your gallery.
"""

import json
from pathlib import Path

def set_photo_order():
    metadata_file = Path("content/images/photography/gallery_metadata.json")
    
    if not metadata_file.exists():
        print("❌ Metadata file not found. Run './blog.sh photos update' first.")
        return
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    print("\n📸 Current photos in gallery:")
    print("-" * 50)
    
    # Sort by current order or filename
    sorted_photos = sorted(metadata.items(), 
                          key=lambda x: (x[1].get('order', 9999), x[0]))
    
    for i, (filename, data) in enumerate(sorted_photos, 1):
        current_order = data.get('order', '')
        order_str = f"[{current_order}]" if current_order else "[auto]"
        print(f"{i:2}. {order_str:7} {filename:30} - {data.get('title', 'Untitled')}")
    
    print("\n" + "=" * 50)
    print("📝 Set manual order for photos")
    print("Enter: 'filename order' (e.g., 'moon-1.jpg 1')")
    print("Or: 'all auto' to reset to automatic ordering")
    print("Or: 'done' to finish")
    print("-" * 50)
    
    while True:
        command = input("\n> ").strip()
        
        if command.lower() == 'done':
            break
        
        if command.lower() == 'all auto':
            for data in metadata.values():
                data.pop('order', None)
            print("✅ Reset all photos to automatic ordering")
            continue
        
        parts = command.split()
        if len(parts) != 2:
            print("❌ Invalid format. Use: 'filename order' or 'done'")
            continue
        
        filename, order_str = parts
        
        # Find matching filename
        matching = [f for f in metadata.keys() if filename in f]
        if not matching:
            print(f"❌ No photo found matching '{filename}'")
            continue
        
        if len(matching) > 1:
            print(f"⚠️  Multiple matches found: {matching}")
            print("Please be more specific.")
            continue
        
        try:
            order = int(order_str)
            metadata[matching[0]]['order'] = order
            print(f"✅ Set {matching[0]} to order {order}")
        except ValueError:
            print(f"❌ Invalid order number: {order_str}")
    
    # Save metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n✅ Photo order updated!")
    print("Run './blog.sh photos update' to regenerate the gallery.")

if __name__ == "__main__":
    set_photo_order()