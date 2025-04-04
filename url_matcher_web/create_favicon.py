#!/usr/bin/env python
"""
Script to create a simple favicon.ico file for the URL Matcher application.
This script creates a basic 16x16 pixel favicon with a "U" character.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_favicon():
    # Create directory if it doesn't exist
    favicon_dir = os.path.join('matcher_app', 'static', 'matcher_app', 'img')
    os.makedirs(favicon_dir, exist_ok=True)
    
    # Create a 16x16 image with a blue background
    img = Image.new('RGB', (16, 16), color=(0, 102, 204))
    d = ImageDraw.Draw(img)
    
    # Try to add a "U" character (for URL)
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        d.text((4, 1), "U", fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"Could not add text to favicon: {e}")
        # If text fails, add a simple shape
        d.rectangle([(4, 4), (12, 12)], fill=(255, 255, 255))
    
    # Save the image as favicon.ico
    favicon_path = os.path.join(favicon_dir, 'favicon.ico')
    img.save(favicon_path)
    print(f"Created favicon at {favicon_path}")

if __name__ == "__main__":
    create_favicon()
