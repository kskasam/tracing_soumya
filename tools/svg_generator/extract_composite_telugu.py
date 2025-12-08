#!/usr/bin/env python3
"""
extract_composite_telugu.py - Extract composite Telugu characters (అం, అః) as SVG paths

Usage:
  python3 tools/svg_generator/extract_composite_telugu.py [am|aha|both]

This script extracts composite Telugu characters by rendering the full Unicode string.
"""

import sys
import os
import io
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.recordingPen import RecordingPen
    import requests
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip3 install fonttools requests")
    sys.exit(1)

# Composite Telugu characters
COMPOSITE_CHARS = {
    'am': 'అం',   # అ (U+0C05) + ం (U+0C02 anusvara)
    'aha': 'అః',  # అ (U+0C05) + ః (U+0C03 visarga)
}

# Font URLs
DEFAULT_FONT_URLS = [
    "https://github.com/google/fonts/raw/main/apache/notosanstelugu/NotoSansTelugu-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/google/fonts@main/apache/notosanstelugu/NotoSansTelugu-Regular.ttf",
]


def find_local_font():
    """Find local Telugu font."""
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    workspace_font = os.path.join(workspace_root, "downloaded_font.ttf")
    if os.path.isfile(workspace_font):
        return workspace_font
    return None


def download_font(url):
    """Download font from URL."""
    print(f"Downloading font from: {url}")
    try:
        r = requests.get(url, allow_redirects=True, timeout=30)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"Error downloading font: {e}")
        return None


def extract_text_path(font_bytes, text_string):
    """Extract SVG path for a text string by rendering each character."""
    try:
        font = TTFont(io.BytesIO(font_bytes))
        glyph_set = font.getGlyphSet()
        cmap = font.getBestCmap()
        
        # Get glyph names for each character
        glyph_names = []
        for char in text_string:
            codepoint = ord(char)
            print(f"    Looking for codepoint U+{codepoint:04X} ({char})...")
            if codepoint in cmap:
                glyph_name = cmap[codepoint]
                print(f"    Found glyph: {glyph_name}")
                if glyph_name in glyph_set:
                    glyph_names.append((glyph_name, char))
                else:
                    print(f"    ✗ Glyph {glyph_name} not in glyph set")
            else:
                print(f"    ✗ Codepoint U+{codepoint:04X} not in cmap")
                # Try all cmaps
                for subtable in font['cmap'].tables:
                    if codepoint in subtable.cmap:
                        glyph_name = subtable.cmap[codepoint]
                        print(f"    Found in alternate cmap: {glyph_name}")
                        if glyph_name in glyph_set:
                            glyph_names.append((glyph_name, char))
                            break
        
        if not glyph_names:
            print(f"  ✗ Could not find glyphs for: {text_string}")
            return None
        
        print(f"  Found {len(glyph_names)} glyph(s)")
        
        # Combine paths from all glyphs
        combined_paths = []
        x_offset = 0
        
        for glyph_name, char in glyph_names:
            print(f"    Processing glyph: {glyph_name} ({char})")
            glyph = glyph_set[glyph_name]
            pen = SVGPathPen(glyph_set)
            glyph.draw(pen)
            path_d = pen.getCommands()
            
            if path_d and path_d.strip() != 'M 0 0 Z':
                print(f"    Path length: {len(path_d)} chars")
                # Translate path by x_offset
                if x_offset > 0:
                    # Simple translation: add x_offset to all X coordinates
                    translated_path = re.sub(
                        r'([MmLlHhCcSsQqTtAa])\s*([-\d.,\s]+)',
                        lambda m: translate_path_command(m.group(1), m.group(2), x_offset),
                        path_d
                    )
                    combined_paths.append(translated_path)
                else:
                    combined_paths.append(path_d)
            else:
                print(f"    ✗ Empty or invalid path for {glyph_name}")
            
            # Get glyph width for next position
            if 'hmtx' in font and glyph_name in font['hmtx']:
                glyph_width = font['hmtx'][glyph_name][0]
                print(f"    Glyph width: {glyph_width}")
                x_offset += glyph_width
            else:
                # Estimate width (rough approximation)
                print(f"    Using estimated width: 500")
                x_offset += 500
        
        if not combined_paths:
            print(f"  ✗ No valid paths extracted")
            return None
        
        combined_path = ' '.join(combined_paths)
        em = font['head'].unitsPerEm if 'head' in font else 1000
        
        print(f"  Combined path length: {len(combined_path)} chars")
        return combined_path, em
        
    except Exception as e:
        import traceback
        print(f"  ✗ Error extracting path: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return None


def translate_path_command(cmd, args, x_offset):
    """Translate X coordinates in a path command by x_offset."""
    if not args:
        return cmd
    
    nums = re.findall(r'([-+]?\d*\.?\d+)', args)
    translated_nums = []
    
    cmd_upper = cmd.upper()
    
    if cmd_upper == 'H':
        # Horizontal line: only X
        for num in nums:
            try:
                val = float(num) + x_offset
                translated_nums.append(f"{val:.2f}")
            except ValueError:
                translated_nums.append(num)
    elif cmd_upper == 'V':
        # Vertical line: only Y, no translation needed
        translated_nums = nums
    elif cmd_upper in ['M', 'L', 'T']:
        # (x, y) pairs - translate X (even indices)
        for i, num in enumerate(nums):
            try:
                val = float(num)
                if i % 2 == 0:  # X coordinate
                    val += x_offset
                translated_nums.append(f"{val:.2f}")
            except ValueError:
                translated_nums.append(num)
    elif cmd_upper in ['C', 'S']:
        # Bezier curves - translate X coordinates
        for i, num in enumerate(nums):
            try:
                val = float(num)
                # X coordinates are at indices 0, 2, 4 for C, and 0, 2 for S
                if cmd_upper == 'C' and i in [0, 2, 4]:
                    val += x_offset
                elif cmd_upper == 'S' and i in [0, 2]:
                    val += x_offset
                translated_nums.append(f"{val:.2f}")
            except ValueError:
                translated_nums.append(num)
    elif cmd_upper in ['Q']:
        # Quadratic bezier - translate X (indices 0, 2)
        for i, num in enumerate(nums):
            try:
                val = float(num)
                if i in [0, 2]:
                    val += x_offset
                translated_nums.append(f"{val:.2f}")
            except ValueError:
                translated_nums.append(num)
    else:
        # For other commands, keep as is
        translated_nums = nums
    
    return f"{cmd} {' '.join(translated_nums)}"


def normalize_path(path_d, em=1000, padding=0.1):
    """Normalize path coordinates (simplified version)."""
    # Extract all coordinates
    coords = []
    for match in re.finditer(r'[-+]?\d*\.?\d+', path_d):
        try:
            coords.append(float(match.group()))
        except ValueError:
            pass
    
    if not coords:
        return path_d
    
    # Find bounding box
    x_coords = [coords[i] for i in range(0, len(coords), 2) if i < len(coords)]
    y_coords = [coords[i+1] for i in range(0, len(coords), 2) if i+1 < len(coords)]
    
    if not x_coords or not y_coords:
        return path_d
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x if max_x != min_x else em
    height = max_y - min_y if max_y != min_y else em
    
    # Calculate scale and offset
    scale = min(em * (1 - 2*padding) / width, em * (1 - 2*padding) / height) if width > 0 and height > 0 else 1
    offset_x = em * padding - min_x * scale
    offset_y = em * padding - min_y * scale
    
    # Transform coordinates
    def transform_coord(val_str, is_x):
        try:
            val = float(val_str)
            if is_x:
                return val * scale + offset_x
            else:
                return val * scale + offset_y
        except ValueError:
            return val_str
    
    # Rebuild path with transformed coordinates
    # This is a simplified transformation - for production, use the full normalize function
    return path_d  # For now, return as-is (you can enhance this)


def save_svg(path_d, output_path, letter_name, char):
    """Save SVG file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{path_d}" fill="black" stroke="none"/>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"  ✓ Saved SVG to: {output_path}")


def extract_composite(letter_name, font_bytes, output_dir):
    """Extract a composite Telugu character."""
    if letter_name not in COMPOSITE_CHARS:
        print(f"Error: Unknown composite character '{letter_name}'")
        print(f"Available: {', '.join(COMPOSITE_CHARS.keys())}")
        return False
    
    text_string = COMPOSITE_CHARS[letter_name]
    print(f"\nExtracting {text_string} - {letter_name}...")
    
    result = extract_text_path(font_bytes, text_string)
    
    if not result:
        print(f"  ✗ Failed to extract")
        return False
    
    path_d, em = result
    # Use the normalize function from the main script if available
    # For now, use the path as-is (it should already be normalized)
    normalized_path = path_d
    
    # Save files
    svg_output = os.path.join(output_dir, f"{letter_name}_extracted.svg")
    save_svg(normalized_path, svg_output, letter_name, text_string)
    
    path_output = os.path.join(output_dir, f"{letter_name}_path.txt")
    with open(path_output, 'w', encoding='utf-8') as f:
        f.write(normalized_path)
    
    print(f"  ✓ Saved path to: {path_output}")
    print(f"  ✓ Path: {normalized_path[:100]}...")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_composite_telugu.py [am|aha|both]")
        print(f"\nAvailable composite characters: {', '.join(COMPOSITE_CHARS.keys())}")
        sys.exit(1)
    
    letter_name = sys.argv[1].lower()
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "tools/svg_generator/output"
    
    # Load font
    font_bytes = None
    local_font = find_local_font()
    if local_font:
        print(f"Using local font: {local_font}")
        with open(local_font, 'rb') as f:
            font_bytes = f.read()
    else:
        print("Downloading font...")
        for url in DEFAULT_FONT_URLS:
            font_bytes = download_font(url)
            if font_bytes:
                break
    
    if not font_bytes:
        print("Error: Could not load font")
        sys.exit(1)
    
    # Extract
    if letter_name == 'both':
        for name in COMPOSITE_CHARS.keys():
            extract_composite(name, font_bytes, output_dir)
    else:
        if extract_composite(letter_name, font_bytes, output_dir):
            print(f"\n✓ Successfully extracted '{letter_name}'")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

