#!/usr/bin/env python3
"""
Simple script to extract అం (am) and అః (aha) by combining base character with diacritics.

Since these are composite characters, we extract:
- అ (U+0C05) - base 'a'
- ం (U+0C02) - anusvara for 'am'  
- ః (U+0C03) - visarga for 'aha'

Then combine them properly.
"""

import sys
import os
import io
import re
import glob

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    import requests
except ImportError:
    print("Error: Install fonttools: pip3 install fonttools requests")
    sys.exit(1)

# Unicode values
A_BASE = 0x0C05  # అ
ANUSVARA = 0x0C02  # ం
VISARGA = 0x0C03  # ః

def find_font():
    """Find Telugu font."""
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    font_path = os.path.join(workspace_root, "downloaded_font.ttf")
    if os.path.isfile(font_path):
        return font_path
    return None

def extract_glyph(font, codepoint):
    """Extract single glyph path."""
    try:
        cmap = font.getBestCmap()
        
        if codepoint not in cmap:
            for subtable in font['cmap'].tables:
                if codepoint in subtable.cmap:
                    cmap = subtable.cmap
                    break
            else:
                print(f"  ✗ Codepoint U+{codepoint:04X} not found in any cmap")
                return None
        
        glyph_name = cmap[codepoint]
        print(f"  Glyph name: {glyph_name} (type: {type(glyph_name)})")
        glyph_set = font.getGlyphSet()
        
        if glyph_name not in glyph_set:
            print(f"  ✗ Glyph {glyph_name} not in glyph set")
            return None
        
        glyph = glyph_set[glyph_name]
        pen = SVGPathPen(glyph_set)
        glyph.draw(pen)
        path_d = pen.getCommands()
        
        if not path_d or path_d.strip() == 'M 0 0 Z':
            print(f"  ✗ Empty path for glyph {glyph_name}")
            return None
        
        # Get glyph metrics
        width = 0
        try:
            if 'hmtx' in font:
                width = font['hmtx'].metrics[glyph_name][0]
        except (KeyError, AttributeError):
            # If metrics not found, estimate from bounding box
            width = 500  # Default estimate
        
        em = font['head'].unitsPerEm if 'head' in font else 1000
        
        print(f"  ✓ Extracted {glyph_name}: width={width}, em={em}")
        return path_d, width, em
    except Exception as e:
        import traceback
        print(f"  ✗ Error extracting glyph U+{codepoint:04X}: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return None

def translate_path_x(path_d, x_offset):
    """Translate all X coordinates by x_offset."""
    def transform_coord(match):
        cmd = match.group(1)
        args = match.group(2) if match.group(2) else ""
        cmd_upper = cmd.upper()
        
        if not args:
            return cmd
        
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        transformed = []
        
        if cmd_upper == 'H':
            # Horizontal: only X
            for num in nums:
                try:
                    transformed.append(f"{float(num) + x_offset:.2f}")
                except:
                    transformed.append(num)
        elif cmd_upper == 'V':
            # Vertical: only Y, no change
            transformed = nums
        elif cmd_upper in ['M', 'L', 'T']:
            # (x, y) pairs
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i % 2 == 0:  # X
                        val += x_offset
                    transformed.append(f"{val:.2f}")
                except:
                    transformed.append(num)
        elif cmd_upper == 'C':
            # Cubic: (x1, y1, x2, y2, x, y)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [0, 2, 4]:  # X coords
                        val += x_offset
                    transformed.append(f"{val:.2f}")
                except:
                    transformed.append(num)
        elif cmd_upper == 'S':
            # Smooth cubic: (x2, y2, x, y)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [0, 2]:  # X coords
                        val += x_offset
                    transformed.append(f"{val:.2f}")
                except:
                    transformed.append(num)
        elif cmd_upper == 'Q':
            # Quadratic: (x1, y1, x, y)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [0, 2]:  # X coords
                        val += x_offset
                    transformed.append(f"{val:.2f}")
                except:
                    transformed.append(num)
        else:
            transformed = nums
        
        return f"{cmd} {' '.join(transformed)}"
    
    return re.sub(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]*)', transform_coord, path_d)

def normalize_path(path_d, em=1000, padding=0.1):
    """Normalize path to fit in viewBox."""
    # This is a simplified version - use the full normalize from extract_telugu_svg.py for production
    # For now, return as-is since fonts usually have reasonable coordinates
    return path_d

def combine_paths(base_path, diacritic_path, base_width):
    """Combine base and diacritic paths."""
    # For anusvara/visarga, they typically go to the right of the base character
    # Translate diacritic by base_width
    translated_diacritic = translate_path_x(diacritic_path, base_width)
    return f"{base_path} {translated_diacritic}"

def save_files(path_d, letter_name, output_dir):
    """Save SVG and path text files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save SVG
    svg_path = os.path.join(output_dir, f"{letter_name}_extracted.svg")
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{path_d}" fill="black" stroke="none"/>
</svg>'''
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  ✓ Saved: {svg_path}")
    
    # Save path text
    txt_path = os.path.join(output_dir, f"{letter_name}_path.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(path_d)
    print(f"  ✓ Saved: {txt_path}")

def extract_am(font, output_dir):
    """Extract అం (am)."""
    print("\nExtracting అం (am)...")
    
    # Extract base 'a'
    print("  Extracting base 'a' (U+0C05)...")
    base_result = extract_glyph(font, A_BASE)
    if not base_result:
        print("  ✗ Failed to extract base 'a'")
        return False
    
    base_path, base_width, em = base_result
    
    # Extract anusvara
    print("  Extracting anusvara (U+0C02)...")
    anusvara_result = extract_glyph(font, ANUSVARA)
    if not anusvara_result:
        print("  ✗ Failed to extract anusvara")
        return False
    
    anusvara_path, anusvara_width, _ = anusvara_result
    
    # Combine paths - place anusvara to the right of base
    print(f"  Combining paths (base width: {base_width})...")
    combined = combine_paths(base_path, anusvara_path, base_width)
    normalized = normalize_path(combined, em)
    
    save_files(normalized, 'am', output_dir)
    return True

def extract_aha(font, output_dir):
    """Extract అః (aha)."""
    print("\nExtracting అః (aha)...")
    
    # Extract base 'a'
    print("  Extracting base 'a' (U+0C05)...")
    base_result = extract_glyph(font, A_BASE)
    if not base_result:
        print("  ✗ Failed to extract base 'a'")
        return False
    
    base_path, base_width, em = base_result
    
    # Extract visarga
    print("  Extracting visarga (U+0C03)...")
    visarga_result = extract_glyph(font, VISARGA)
    if not visarga_result:
        print("  ✗ Failed to extract visarga")
        return False
    
    visarga_path, visarga_width, _ = visarga_result
    
    # Combine paths - place visarga to the right of base
    print(f"  Combining paths (base width: {base_width})...")
    combined = combine_paths(base_path, visarga_path, base_width)
    normalized = normalize_path(combined, em)
    
    save_files(normalized, 'aha', output_dir)
    return True

def main():
    output_dir = "tools/svg_generator/output"
    
    # Load font
    font_path = find_font()
    if not font_path:
        print("Error: Could not find downloaded_font.ttf")
        print("Please ensure the font file exists in the workspace root")
        sys.exit(1)
    
    print(f"Using font: {font_path}")
    font = TTFont(font_path)
    
    # Extract both
    success_am = extract_am(font, output_dir)
    success_aha = extract_aha(font, output_dir)
    
    if success_am and success_aha:
        print("\n✓ Successfully extracted both characters")
    else:
        print("\n✗ Some extractions failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

