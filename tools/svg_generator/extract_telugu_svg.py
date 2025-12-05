#!/usr/bin/env python3
"""
extract_telugu_svg.py - Generic script to extract Telugu letters from TTF font and generate SVG paths

Usage:
  python3 tools/svg_generator/extract_telugu_svg.py [letter_name] [font_path_or_url] [output_dir]
  
  Examples:
    # Extract specific letter 'aa'
    python3 tools/svg_generator/extract_telugu_svg.py aa
    
    # Extract all Telugu letters
    python3 tools/svg_generator/extract_telugu_svg.py all
    
    # Extract with custom font path
    python3 tools/svg_generator/extract_telugu_svg.py aa /path/to/font.ttf

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

# Telugu Unicode range: U+0C00 to U+0C7F
# Complete mapping of Telugu letters
TELUGU_LETTERS = {
    'a': 0x0C05,      # అ
    'aa': 0x0C06,     # ఆ
    'i': 0x0C07,      # ఇ
    'ii': 0x0C08,     # ఈ
    'u': 0x0C09,      # ఉ
    'uu': 0x0C0A,     # ఊ
    'e': 0x0C0E,      # ఎ
    'ee': 0x0C0F,     # ఏ
    'ai': 0x0C10,     # ఐ
    'o': 0x0C12,      # ఒ
    'oo': 0x0C13,     # ఓ
    'au': 0x0C14,     # ఔ
    'ka': 0x0C15,     # క
    'kha': 0x0C16,    # ఖ
    'ga': 0x0C17,     # గ
    'gha': 0x0C18,    # ఘ
    'nga': 0x0C19,    # ఙ
    'cha': 0x0C1A,    # చ
    'chha': 0x0C1B,   # ఛ
    'ja': 0x0C1C,     # జ
    'jha': 0x0C1D,    # ఝ
    'nya': 0x0C1E,    # ఞ
    'ta': 0x0C1F,     # ట
    'tha': 0x0C20,    # ఠ
    'da': 0x0C21,     # డ
    'dha': 0x0C22,    # ఢ
    'na': 0x0C23,     # ణ
    'ta2': 0x0C24,    # త
    'tha2': 0x0C25,   # థ
    'da2': 0x0C26,    # ద
    'dha2': 0x0C27,   # ధ
    'na2': 0x0C28,    # న
    'pa': 0x0C2A,     # ప
    'pha': 0x0C2B,    # ఫ
    'ba': 0x0C2C,     # బ
    'bha': 0x0C2D,    # భ
    'ma': 0x0C2E,     # మ
    'ya': 0x0C2F,     # య
    'ra': 0x0C30,     # ర
    'la': 0x0C32,     # ల
    'lla': 0x0C33,    # ళ
    'va': 0x0C35,     # వ
    'sha': 0x0C36,    # శ
    'ssa': 0x0C37,    # ష
    'sa': 0x0C38,     # స
    'ha': 0x0C39,     # హ
}

# Try multiple possible URLs for Noto Sans Telugu
DEFAULT_FONT_URLS = [
    "https://github.com/google/fonts/raw/main/apache/notosanstelugu/NotoSansTelugu-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/google/fonts@main/apache/notosanstelugu/NotoSansTelugu-Regular.ttf",
    "https://raw.githubusercontent.com/google/fonts/main/apache/notosanstelugu/NotoSansTelugu-Regular.ttf",
    "https://fonts.gstatic.com/s/notosanstelugu/v20/0FlxVOGZlE2Rrtr39mg0Wc3j9Mn3SckQ4H7F4bJX3nsLJg.ttf",
]


def find_local_telugu_font():
    """Search common locations for Telugu fonts."""
    # First check for downloaded_font.ttf in the workspace
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    workspace_font = os.path.join(workspace_root, "downloaded_font.ttf")
    if os.path.isfile(workspace_font):
        return workspace_font
    
    possible_paths = [
        "/System/Library/Fonts/*Telugu*.ttf",
        "/Library/Fonts/*Telugu*.ttf",
        os.path.expanduser("~/Library/Fonts/*Telugu*.ttf"),
        "/usr/share/fonts/**/*Telugu*.ttf",
        "/usr/local/share/fonts/**/*Telugu*.ttf",
        "C:/Windows/Fonts/*Telugu*.ttf",
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


def extract_glyph_path(font_bytes, codepoint):
    """Extract SVG path for a glyph from font bytes."""
    try:
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
    
    # Step 1: Flip Y coordinates in original path
    flipped_commands = []
    for cmd, args in commands:
        if not args or cmd.upper() == 'Z':
            flipped_commands.append((cmd, args))
            continue
        
        cmd_upper = cmd.upper()
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        flipped_nums = []
        
        if cmd_upper == 'H':
            # Horizontal line: only X coordinate, no Y to flip
            flipped_nums = nums
        elif cmd_upper == 'V':
            # Vertical line: only Y coordinate, flip it
            for num in nums:
                try:
                    val = float(num)
                    val = em - val  # Flip Y
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'C':
            # Cubic bezier: (x1, y1, x2, y2, x, y) - 6 numbers
            # Flip y1, y2, and y (indices 1, 3, 5)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3, 5]:  # Y coordinates
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'S':
            # Smooth cubic bezier: (x2, y2, x, y) - 4 numbers
            # Flip y2 and y (indices 1, 3)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3]:  # Y coordinates
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'Q':
            # Quadratic bezier: (x1, y1, x, y) - 4 numbers
            # Flip y1 and y (indices 1, 3)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 3]:  # Y coordinates
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'T':
            # Smooth quadratic bezier: (x, y) - 2 numbers
            # Flip y (index 1)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i == 1:  # Y coordinate
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'A':
            # Arc: (rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y) - 7 numbers
            # Flip ry and y (indices 1, 6)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i in [1, 6]:  # ry and y coordinates
                        val = em - val
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
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        
        flipped_args = ' '.join(flipped_nums)
        flipped_commands.append((cmd, flipped_args))
    
    # Step 2: Extract coordinates from flipped path for bounding box
    coords = []
    for cmd, args in flipped_commands:
        if not args or cmd.upper() == 'Z':
            continue
        nums = re.findall(r'[-+]?\d*\.?\d+', args)
        for num in nums:
            try:
                coords.append(float(num))
            except ValueError:
                pass
    
    if not coords:
        # Reconstruct path from flipped commands
        return ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
    
    # Find bounding box of flipped path
    x_coords = [coords[i] for i in range(0, len(coords), 2) if i < len(coords)]
    y_coords = [coords[i+1] for i in range(0, len(coords), 2) if i+1 < len(coords)]
    
    if not x_coords or not y_coords:
        return ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x if max_x != min_x else em
    height = max_y - min_y if max_y != min_y else em
    
    # Calculate scale and offset to fit in em x em with padding
    scale = min(em * (1 - 2*padding) / width, em * (1 - 2*padding) / height) if width > 0 and height > 0 else 1
    offset_x = em * padding - min_x * scale
    offset_y = em * padding - min_y * scale
    
    # Step 3: Normalize the flipped path
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
            for i, num in enumerate(nums):
                is_x = (i not in [1, 6])  # Everything except ry (1) and y (6)
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
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


def extract_letter(letter_name, font_bytes, output_dir):
    """Extract a single Telugu letter."""
    if letter_name not in TELUGU_LETTERS:
        print(f"Error: Unknown letter '{letter_name}'")
        print(f"Available letters: {', '.join(sorted(TELUGU_LETTERS.keys()))}")
        return False
    
    codepoint = TELUGU_LETTERS[letter_name]
    char = chr(codepoint)
    
    print(f"\nExtracting {char} (U+{codepoint:04X}) - {letter_name}...")
    
    result = extract_glyph_path(font_bytes, codepoint)
    
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
        print("Usage: python3 extract_telugu_svg.py [letter_name|all] [font_path_or_url] [output_dir]")
        print(f"\nAvailable letters: {', '.join(sorted(TELUGU_LETTERS.keys()))}")
        print("\nExamples:")
        print("  python3 extract_telugu_svg.py aa")
        print("  python3 extract_telugu_svg.py all")
        print("  python3 extract_telugu_svg.py aa /path/to/font.ttf")
        sys.exit(1)
    
    letter_name = sys.argv[1].lower()
    font_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/svg_generator/output"
    
    # Load font
    font_bytes = None
    if font_path:
        if os.path.isfile(font_path):
            print(f"Using local font: {font_path}")
            with open(font_path, 'rb') as f:
                font_bytes = f.read()
        else:
            font_bytes = download_font(font_path)
    else:
        local_font = find_local_telugu_font()
        if local_font:
            print(f"Using local font: {local_font}")
            with open(local_font, 'rb') as f:
                font_bytes = f.read()
        else:
            print(f"Downloading default font...")
            for url in DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = download_font(url)
                if font_bytes:
                    break
    
    if not font_bytes:
        print("\nError: Could not load font")
        print("Please provide a font path or URL as the second argument")
        print("\nYou can download NotoSansTelugu-Regular.ttf from:")
        print("https://fonts.google.com/noto/specimen/Noto+Sans+Telugu")
        sys.exit(1)
    
    # Extract letter(s)
    if letter_name == 'all':
        print(f"\nExtracting all Telugu letters...")
        success_count = 0
        for name in sorted(TELUGU_LETTERS.keys()):
            if extract_letter(name, font_bytes, output_dir):
                success_count += 1
        print(f"\n✓ Successfully extracted {success_count}/{len(TELUGU_LETTERS)} letters")
    else:
        if extract_letter(letter_name, font_bytes, output_dir):
            print(f"\n✓ Successfully extracted '{letter_name}'")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

