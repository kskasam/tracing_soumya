#!/usr/bin/env python3
"""
extract_hindi_svg.py - Generic script to extract Hindi letters from TTF font and generate SVG paths

Usage:
  python3 tools/svg_generator/extract_hindi_svg.py [letter_name] [font_path_or_url] [output_dir]
  
  Examples:
    # Extract specific letter 'ka'
    python3 tools/svg_generator/extract_hindi_svg.py ka
    
    # Extract all Hindi letters
    python3 tools/svg_generator/extract_hindi_svg.py all
    
    # Extract with custom font path
    python3 tools/svg_generator/extract_hindi_svg.py ka /path/to/font.ttf

Dependencies: fonttools, requests
Install: python3 -m pip install --user fonttools requests
"""
import sys
import io
import os
import json
import re
import glob
import requests
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen

# Hindi (Devanagari) Unicode range: U+0900 to U+097F
# Complete mapping of Hindi letters (vowels and consonants)
HINDI_LETTERS = {
    # Vowels (स्वर)
    'a': 0x0905,      # अ
    'aa': 0x0906,     # आ
    'i': 0x0907,      # इ
    'ii': 0x0908,     # ई
    'u': 0x0909,      # उ
    'uu': 0x090A,     # ऊ
    'e': 0x090F,      # ए
    'ee': 0x0910,     # ऐ
    'o': 0x0913,      # ओ
    'oo': 0x0914,     # औ
    'ri': 0x090B,     # ऋ
    'ri_long': 0x0960, # ॠ
    'lri': 0x090C,    # ऌ
    'lri_long': 0x0961, # ॡ
    
    # Consonants (व्यंजन)
    'ka': 0x0915,     # क
    'kha': 0x0916,    # ख
    'ga': 0x0917,     # ग
    'gha': 0x0918,    # घ
    'nga': 0x0919,    # ङ
    'cha': 0x091A,    # च
    'chha': 0x091B,   # छ
    'ja': 0x091C,     # ज
    'jha': 0x091D,    # झ
    'nya': 0x091E,    # ञ
    'ta': 0x091F,     # ट
    'tha': 0x0920,    # ठ
    'da': 0x0921,     # ड
    'dha': 0x0922,    # ढ
    'na': 0x0923,     # ण
    'ta2': 0x0924,    # त
    'tha2': 0x0925,   # थ
    'da2': 0x0926,    # द
    'dha2': 0x0927,   # ध
    'na2': 0x0928,    # न
    'pa': 0x092A,     # प
    'pha': 0x092B,    # फ
    'ba': 0x092C,     # ब
    'bha': 0x092D,    # भ
    'ma': 0x092E,     # म
    'ya': 0x092F,     # य
    'ra': 0x0930,     # र
    'la': 0x0932,     # ल
    'va': 0x0935,     # व
    'sha': 0x0936,    # श
    'ssa': 0x0937,    # ष
    'sa': 0x0938,     # स
    'ha': 0x0939,     # ह
    'lla': 0x0933,    # ळ
}

# Try multiple possible URLs for Noto Sans Devanagari (fallback)
DEFAULT_FONT_URLS = [
    "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf",
    "https://github.com/google/fonts/raw/main/apache/notosansdevanagari/NotoSansDevanagari-Regular.ttf",
]


def find_local_hindi_font():
    """Search common locations for Hindi/Devanagari fonts, prioritizing Kohinoor Devanagari."""
    # Prioritize Kohinoor Devanagari (better ligature/conjunct support, prevents letter breaking)
    kohinoor_paths = [
        "/System/Library/Fonts/Kohinoor.ttc",  # macOS - contains Kohinoor Devanagari
        "/Library/Fonts/Kohinoor*.ttc",
        os.path.expanduser("~/Library/Fonts/Kohinoor*.ttc"),
        "C:/Windows/Fonts/Kohinoor*.ttc",
        "C:/Windows/Fonts/Kohinoor*.ttf",
    ]
    
    for pattern in kohinoor_paths:
        try:
            matches = glob.glob(pattern)
            if matches:
                # Verify it's actually Devanagari by checking font name
                try:
                    from fontTools.ttLib import TTFont
                    for font_path in matches:
                        # TTC files can contain multiple fonts, check first one
                        font = TTFont(font_path, fontNumber=0)
                        font_name = None
                        if 'name' in font:
                            for name_record in font['name'].names:
                                if name_record.nameID == 1:  # Font family name
                                    font_name = name_record.toUnicode()
                                    break
                        if font_name and 'Devanagari' in font_name:
                            return font_path
                except Exception:
                    # If we can't verify, use it anyway (likely correct)
                    return matches[0]
        except Exception:
            pass
    
    # Fallback to other Devanagari fonts
    possible_paths = [
        "/System/Library/Fonts/*Devanagari*.ttf",
        "/System/Library/Fonts/*Devanagari*.ttc",
        "/System/Library/Fonts/*Hindi*.ttf",
        "/System/Library/Fonts/*Hindi*.ttc",
        "/Library/Fonts/*Devanagari*.ttf",
        "/Library/Fonts/*Devanagari*.ttc",
        "/Library/Fonts/*Hindi*.ttf",
        "/Library/Fonts/*Hindi*.ttc",
        os.path.expanduser("~/Library/Fonts/*Devanagari*.ttf"),
        os.path.expanduser("~/Library/Fonts/*Devanagari*.ttc"),
        os.path.expanduser("~/Library/Fonts/*Hindi*.ttf"),
        os.path.expanduser("~/Library/Fonts/*Hindi*.ttc"),
        "/usr/share/fonts/**/*Devanagari*.ttf",
        "/usr/share/fonts/**/*Devanagari*.ttc",
        "/usr/share/fonts/**/*Hindi*.ttf",
        "/usr/share/fonts/**/*Hindi*.ttc",
        "/usr/local/share/fonts/**/*Devanagari*.ttf",
        "/usr/local/share/fonts/**/*Devanagari*.ttc",
        "/usr/local/share/fonts/**/*Hindi*.ttf",
        "/usr/local/share/fonts/**/*Hindi*.ttc",
        "C:/Windows/Fonts/*Devanagari*.ttf",
        "C:/Windows/Fonts/*Hindi*.ttf",
    ]
    
    for pattern in possible_paths:
        try:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]
        except Exception:
            pass
    
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


def extract_glyph_path(font_bytes, codepoint, font_path=None):
    """Extract SVG path for a glyph from font bytes.
    
    Args:
        font_bytes: Font file bytes (for TTF) or None (for TTC file path)
        codepoint: Unicode codepoint to extract
        font_path: Path to font file (required for TTC files)
    """
    try:
        # Handle TTC files (TrueType Collections) - need file path
        if font_path and font_path.lower().endswith('.ttc'):
            # Try different font numbers in the collection (0 is usually Regular)
            for font_number in [0, 1, 2, 3, 4]:
                try:
                    font = TTFont(font_path, fontNumber=font_number)
                    # Verify it's Devanagari by checking if it has the codepoint
                    cmap = font.getBestCmap()
                    if codepoint in cmap:
                        break
                except Exception:
                    continue
            else:
                # If no font number worked, use 0 (default)
                font = TTFont(font_path, fontNumber=0)
        else:
            # Regular TTF file
            font = TTFont(io.BytesIO(font_bytes))
    except Exception as e:
        print(f"Error loading font: {e}")
        return None
    
    # Get the best cmap
    cmap = font.getBestCmap()
    
    if codepoint not in cmap:
        # Try all cmaps
        for subtable in font['cmap'].tables:
            if codepoint in subtable.cmap:
                cmap = subtable.cmap
                break
        else:
            return None
    
    glyph_name = cmap[codepoint]
    glyph_set = font.getGlyphSet()
    
    if glyph_name not in glyph_set:
        return None
    
    glyph = glyph_set[glyph_name]
    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_d = pen.getCommands()
    
    if not path_d or path_d.strip() == 'M 0 0 Z':
        return None
    
    # Get units per em for scaling
    em = font['head'].unitsPerEm if 'head' in font else 1000
    
    return path_d, em


def normalize_path_coordinates(path_d, em=1000, padding=0.1):
    """Normalize SVG path coordinates to fit in viewBox with padding.
    
    Fonts use Y-up coordinates (Y increases upward), but SVG/Flutter use Y-down.
    So we first flip Y coordinates, then normalize.
    """
    # First, flip Y coordinates (fonts use Y-up, SVG uses Y-down)
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', path_d)
    
    # Step 1: Flip Y coordinates and extract all X/Y coordinates for bounding box
    flipped_commands = []
    x_coords = []
    y_coords = []
    
    # Track position for H/V commands and relative commands
    current_x, current_y = 0, 0
    start_x, start_y = 0, 0
    
    for cmd, args in commands:
        if not args or cmd.upper() == 'Z':
            flipped_commands.append((cmd, args))
            if cmd.upper() == 'Z':
                current_x, current_y = start_x, start_y
            continue
        
        cmd_upper = cmd.upper()
        is_relative = cmd.islower()
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        flipped_nums = []
        
        if cmd_upper == 'H':
            # Horizontal line: only X coordinate
            for num in nums:
                try:
                    val = float(num)
                    if is_relative:
                        current_x += val
                    else:
                        current_x = val
                    flipped_nums.append(f"{val:.2f}")
                    x_coords.append(current_x)
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'V':
            # Vertical line: only Y coordinate, flip it
            for num in nums:
                try:
                    val = float(num)
                    if is_relative:
                        # For relative V: original_y_new = original_y_old + val
                        # flipped_y_new = em - original_y_new = em - original_y_old - val
                        # Since current_y (flipped) = em - original_y_old
                        # flipped_y_new = current_y - val
                        current_y = current_y - val
                    else:
                        # For absolute V: flip the coordinate
                        current_y = em - val
                    flipped_nums.append(f"{current_y:.2f}")
                    y_coords.append(current_y)
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'C':
            # Cubic bezier: (x1, y1, x2, y2, x, y) - 6 numbers
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3, 5]:  # Y coordinates
                        val = em - val
                        y_coords.append(val)
                    else:  # X coordinates
                        x_coords.append(val)
                    if i == 4:  # x (second to last)
                        if is_relative:
                            current_x += float(nums[i])
                        else:
                            current_x = val
                    elif i == 5:  # y (last)
                        if is_relative:
                            # For relative: original_y_new = original_y_old + orig_y
                            # current_y (flipped) = em - original_y_old
                            # new_y_flipped = em - original_y_new = current_y - orig_y
                            orig_y = float(nums[i])
                            current_y = current_y - orig_y
                        else:
                            current_y = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'S':
            # Smooth cubic bezier: (x2, y2, x, y) - 4 numbers
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3]:  # Y coordinates
                        val = em - val
                        y_coords.append(val)
                    else:  # X coordinates
                        x_coords.append(val)
                    if i == 2:  # x
                        if is_relative:
                            current_x += float(nums[i])
                        else:
                            current_x = val
                    elif i == 3:  # y
                        if is_relative:
                            orig_y = float(nums[i])
                            current_y = em - (em - current_y + orig_y)
                        else:
                            current_y = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'Q':
            # Quadratic bezier: (x1, y1, x, y) - 4 numbers
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3]:  # Y coordinates
                        val = em - val
                        y_coords.append(val)
                    else:  # X coordinates
                        x_coords.append(val)
                    if i == 2:  # x
                        if is_relative:
                            current_x += float(nums[i])
                        else:
                            current_x = val
                    elif i == 3:  # y
                        if is_relative:
                            orig_y = float(nums[i])
                            current_y = em - (em - current_y + orig_y)
                        else:
                            current_y = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'T':
            # Smooth quadratic bezier: (x, y) - 2 numbers
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i == 1:  # Y coordinate
                        val = em - val
                        y_coords.append(val)
                        if is_relative:
                            orig_y = float(nums[i])
                            current_y = em - (em - current_y + orig_y)
                        else:
                            current_y = val
                    else:  # X coordinate
                        x_coords.append(val)
                        if is_relative:
                            current_x += val
                        else:
                            current_x = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'A':
            # Arc: (rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y) - 7 numbers
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i == 1:  # ry - flip it
                        val = em - val
                    elif i == 6:  # y - flip it
                        val = em - val
                        y_coords.append(val)
                        if is_relative:
                            orig_y = float(nums[i])
                            current_y = em - (em - current_y + orig_y)
                        else:
                            current_y = val
                    elif i == 5:  # x
                        x_coords.append(val)
                        if is_relative:
                            current_x += val
                        else:
                            current_x = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        else:
            # M, L, m, l: (x, y) pairs - standard case
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i % 2 == 1:  # Y coordinate (odd index)
                        val = em - val
                        y_coords.append(val)
                        if is_relative:
                            orig_y = float(nums[i])
                            current_y = em - (em - current_y + orig_y)
                        else:
                            current_y = val
                    else:  # X coordinate (even index)
                        x_coords.append(val)
                        if is_relative:
                            current_x += val
                        else:
                            current_x = val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
            # Set start position after processing M command coordinates
            if cmd_upper == 'M' and len(nums) >= 2:
                try:
                    start_x = float(nums[0]) if not is_relative else current_x
                    start_y = em - float(nums[1]) if not is_relative else current_y
                except (ValueError, IndexError):
                    pass
        
        flipped_args = ' '.join(flipped_nums)
        flipped_commands.append((cmd, flipped_args))
    
    # Fallback: if we didn't extract coordinates properly, extract all numbers from flipped path
    if not x_coords or not y_coords:
        # Try to extract all coordinates from the flipped path string
        flipped_path_str = ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
        all_nums = re.findall(r'[-+]?\d*\.?\d+', flipped_path_str)
        try:
            all_coords = [float(n) for n in all_nums]
            if all_coords:
                # Use all coordinates for bounding box (not perfect for H/V, but better than nothing)
                # We'll use min/max of all coordinates as a rough bounding box
                if not x_coords:
                    x_coords = all_coords[::2] if len(all_coords) > 0 else []
                if not y_coords:
                    y_coords = all_coords[1::2] if len(all_coords) > 1 else []
                # If still empty, use all coordinates as both X and Y (rough approximation)
                if not x_coords and not y_coords:
                    x_coords = all_coords
                    y_coords = all_coords
                elif not x_coords:
                    x_coords = y_coords[:]
                elif not y_coords:
                    y_coords = x_coords[:]
        except (ValueError, IndexError):
            pass
    
    if not x_coords or not y_coords:
        # Still no coordinates - return flipped path as-is
        return ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
    
    # Find bounding box of flipped path
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x if max_x != min_x else 1
    height = max_y - min_y if max_y != min_y else 1
    
    # Always normalize to fit in em x em with padding (even if already in range)
    # This ensures the letter is properly centered and scaled
    if width > 0 and height > 0:
        scale = min(em * (1 - 2*padding) / width, em * (1 - 2*padding) / height)
        offset_x = em * padding - min_x * scale
        offset_y = em * padding - min_y * scale
    else:
        # Fallback if width/height is 0
        scale = 1
        offset_x = em * padding
        offset_y = em * padding
    
    # Step 2: Normalize the flipped path
    def transform_coord(coord_str, is_x):
        try:
            val = float(coord_str)
            if is_x:
                return val * scale + offset_x
            else:
                return val * scale + offset_y
        except ValueError:
            return coord_str
    
    transformed_commands = []
    
    for cmd, args in flipped_commands:
        if not args or cmd.upper() == 'Z':
            transformed_commands.append(cmd)
            continue
        
        cmd_upper = cmd.upper()
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        transformed_nums = []
        
        if cmd_upper == 'H':
            # Horizontal line: only X coordinate
            for num in nums:
                transformed_val = transform_coord(num, True)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'V':
            # Vertical line: only Y coordinate
            for num in nums:
                transformed_val = transform_coord(num, False)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'C':
            # Cubic bezier: (x1, y1, x2, y2, x, y) - 6 numbers
            for i, num in enumerate(nums):
                is_x = (i in [0, 2, 4])  # x1, x2, x are X coordinates
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'S':
            # Smooth cubic bezier: (x2, y2, x, y) - 4 numbers
            for i, num in enumerate(nums):
                is_x = (i in [0, 2])  # x2, x are X coordinates
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'Q':
            # Quadratic bezier: (x1, y1, x, y) - 4 numbers
            for i, num in enumerate(nums):
                is_x = (i in [0, 2])  # x1, x are X coordinates
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'T':
            # Smooth quadratic bezier: (x, y) - 2 numbers
            for i, num in enumerate(nums):
                is_x = (i == 0)  # x is X coordinate
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'A':
            # Arc: (rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y) - 7 numbers
            # Transform rx, x-axis-rotation, x as X; ry, y as Y; flags stay as-is
            for i, num in enumerate(nums):
                if i in [2, 3, 4]:  # x-axis-rotation, flags - don't transform
                    transformed_nums.append(num)
                elif i == 1:  # ry - Y coordinate
                    transformed_val = transform_coord(num, False)
                    transformed_nums.append(f"{transformed_val:.2f}")
                elif i == 0:  # rx - X coordinate
                    transformed_val = transform_coord(num, True)
                    transformed_nums.append(f"{transformed_val:.2f}")
                elif i == 5:  # x - X coordinate
                    transformed_val = transform_coord(num, True)
                    transformed_nums.append(f"{transformed_val:.2f}")
                elif i == 6:  # y - Y coordinate
                    transformed_val = transform_coord(num, False)
                    transformed_nums.append(f"{transformed_val:.2f}")
                else:
                    transformed_nums.append(num)
        else:
            # M, L, m, l: (x, y) pairs - standard case
            for i, num in enumerate(nums):
                is_x = (i % 2 == 0)
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        
        transformed_args = ' '.join(transformed_nums)
        transformed_commands.append(f"{cmd} {transformed_args}")
    
    return ' '.join(transformed_commands)


def save_svg_file(path_d, output_path, letter_name, char):
    """Save SVG path to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{path_d}" fill="black" stroke="none"/>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"  ✓ Saved SVG to: {output_path}")


def extract_letter(letter_name, font_bytes, output_dir, font_path=None):
    """Extract a single Hindi letter.
    
    Args:
        letter_name: Name of the letter to extract
        font_bytes: Font file bytes (None for TTC files)
        output_dir: Output directory for SVG files
        font_path: Path to font file (required for TTC files)
    """
    if letter_name not in HINDI_LETTERS:
        print(f"Error: Unknown letter '{letter_name}'")
        print(f"Available letters: {', '.join(sorted(HINDI_LETTERS.keys()))}")
        return False
    
    codepoint = HINDI_LETTERS[letter_name]
    char = chr(codepoint)
    
    print(f"\nExtracting {char} (U+{codepoint:04X}) - {letter_name}...")
    
    result = extract_glyph_path(font_bytes, codepoint, font_path)
    
    if not result:
        print(f"  ✗ Failed to extract glyph")
        return False
    
    path_d, em = result
    normalized_path = normalize_path_coordinates(path_d, em)
    
    # Save SVG file
    svg_output = os.path.join(output_dir, f"{letter_name}_extracted.svg")
    save_svg_file(normalized_path, svg_output, letter_name, char)
    
    # Also save the path as a text file for easy copying
    path_output = os.path.join(output_dir, f"{letter_name}_path.txt")
    with open(path_output, 'w', encoding='utf-8') as f:
        f.write(normalized_path)
    
    print(f"  ✓ Saved path to: {path_output}")
    print(f"  ✓ Path: {normalized_path[:100]}...")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_hindi_svg.py [letter_name|all] [font_path_or_url] [output_dir]")
        print(f"\nAvailable letters: {', '.join(sorted(HINDI_LETTERS.keys()))}")
        print("\nExamples:")
        print("  python3 extract_hindi_svg.py ka")
        print("  python3 extract_hindi_svg.py all")
        print("  python3 extract_hindi_svg.py ka /path/to/font.ttf")
        sys.exit(1)
    
    letter_name = sys.argv[1].lower()
    font_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/svg_generator/out_hin"
    
    # Load font - prioritize Kohinoor Devanagari for better ligature support
    font_bytes = None
    actual_font_path = None
    
    if font_path:
        if os.path.isfile(font_path):
            print(f"Using specified font: {font_path}")
            actual_font_path = font_path
            # For TTC files, we'll use the path directly
            if not font_path.lower().endswith('.ttc'):
                with open(font_path, 'rb') as f:
                    font_bytes = f.read()
        else:
            font_bytes = download_font(font_path)
    else:
        # Search for Kohinoor Devanagari first (better for preventing letter breaking)
        local_font = find_local_hindi_font()
        if local_font:
            print(f"Using local font: {local_font}")
            if 'Kohinoor' in local_font:
                print("  ✓ Found Kohinoor Devanagari (better ligature/conjunct support)")
            actual_font_path = local_font
            # For TTC files, we'll use the path directly
            if not local_font.lower().endswith('.ttc'):
                with open(local_font, 'rb') as f:
                    font_bytes = f.read()
        else:
            print(f"Downloading fallback font (Noto Sans Devanagari)...")
            print("  Note: Kohinoor Devanagari is recommended for better letter rendering")
            for url in DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = download_font(url)
                if font_bytes:
                    break
    
    if not font_bytes and not actual_font_path:
        print("\nError: Could not load font")
        print("Please provide a font path or URL as the second argument")
        print("\nRecommended: Use Kohinoor Devanagari (often pre-installed on macOS)")
        print("Fallback: Download NotoSansDevanagari-Regular.ttf from:")
        print("https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
        sys.exit(1)
    
    # Extract letter(s)
    if letter_name == 'all':
        print(f"\nExtracting all Hindi letters...")
        success_count = 0
        for name in sorted(HINDI_LETTERS.keys()):
            if extract_letter(name, font_bytes, output_dir, actual_font_path):
                success_count += 1
        print(f"\n✓ Successfully extracted {success_count}/{len(HINDI_LETTERS)} letters")
    else:
        if extract_letter(letter_name, font_bytes, output_dir, actual_font_path):
            print(f"\n✓ Successfully extracted '{letter_name}'")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

