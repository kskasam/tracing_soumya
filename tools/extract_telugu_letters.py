#!/usr/bin/env python3
"""
extract_telugu_letters.py - Extract Telugu letters from TTF font and generate SVG paths and JSON point files

Usage:
  python3 tools/extract_telugu_letters.py [font_path_or_url] [output_dir]

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
# Common Telugu letters to extract
TELUGU_LETTERS = {
    0x0C05: 'a',      # అ
    0x0C06: 'aa',     # ఆ
    0x0C07: 'i',      # ఇ
    0x0C08: 'ii',     # ఈ
    0x0C09: 'u',      # ఉ
    0x0C0A: 'uu',     # ఊ
    0x0C0E: 'e',      # ఎ
    0x0C0F: 'ee',     # ఏ
    0x0C10: 'ai',     # ఐ
    0x0C12: 'o',      # ఒ
    0x0C13: 'oo',     # ఓ
    0x0C14: 'au',     # ఔ
    0x0C15: 'ka',     # క
    0x0C16: 'kha',    # ఖ
    0x0C17: 'ga',     # గ
    0x0C18: 'gha',    # ఘ
    0x0C19: 'nga',    # ఙ
    0x0C1A: 'cha',    # చ
    0x0C1B: 'chha',   # ఛ
    0x0C1C: 'ja',     # జ
    0x0C1D: 'jha',    # ఝ
    0x0C1E: 'nya',    # ఞ
    0x0C1F: 'ta',     # ట
    0x0C20: 'tha',    # ఠ
    0x0C21: 'da',     # డ
    0x0C22: 'dha',    # ఢ
    0x0C23: 'na',     # ణ
    0x0C24: 'ta2',    # త
    0x0C25: 'tha2',   # థ
    0x0C26: 'da2',    # ద
    0x0C27: 'dha2',   # ధ
    0x0C28: 'na2',    # న
    0x0C2A: 'pa',     # ప
    0x0C2B: 'pha',    # ఫ
    0x0C2C: 'ba',     # బ
    0x0C2D: 'bha',    # భ
    0x0C2E: 'ma',     # మ
    0x0C2F: 'ya',     # య
    0x0C30: 'ra',     # ర
    0x0C32: 'la',     # ల
    0x0C33: 'lla',    # ళ
    0x0C35: 'va',     # వ
    0x0C36: 'sha',    # శ
    0x0C37: 'ssa',    # ష
    0x0C38: 'sa',     # స
    0x0C39: 'ha',     # హ
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
    workspace_font = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloaded_font.ttf")
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
    
    # Get bounding box
    recording_pen = RecordingPen()
    glyph.draw(recording_pen)
    bounds = recording_pen.value
    
    return path_d, em


def normalize_path_coordinates(path_d, em=1000, padding=0.1):
    """Normalize SVG path coordinates to fit in viewBox with padding.
    
    Fonts use Y-up coordinates (Y increases upward), but SVG/Flutter use Y-down.
    So we first flip Y coordinates, then normalize.
    """
    # First, flip Y coordinates (fonts use Y-up, SVG uses Y-down)
    # y_new = em - y_old
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', path_d)
    
    # Step 1: Flip Y coordinates in original path
    # Different commands have different coordinate patterns:
    # M, L: (x, y)
    # H: (x) - horizontal line, no Y
    # V: (y) - vertical line, only Y
    # C: (x1, y1, x2, y2, x, y) - cubic bezier
    # Q: (x1, y1, x, y) - quadratic bezier
    # S: (x2, y2, x, y) - smooth cubic bezier
    # T: (x, y) - smooth quadratic bezier
    # A: (rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y) - arc
    
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
            # rx, x-axis-rotation, large-arc-flag, sweep-flag, x are not Y coordinates
            # Only ry and y are Y coordinates
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


def path_to_points_simple(path_d, num_points=25):
    """Convert SVG path to normalized point coordinates by sampling along path segments.
    Detects multiple strokes based on 'M' (move) commands - each 'M' starts a new stroke."""
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', path_d)
    
    # Split path into multiple strokes based on 'M' commands
    strokes = []
    current_stroke = []
    current_x, current_y = 0, 0
    
    for cmd, args in commands:
        if cmd.upper() == 'M':
            # Move to - start a new stroke if we have points in current stroke
            if current_stroke:
                strokes.append(current_stroke)
                current_stroke = []
            # Add the move point
            nums = re.findall(r'[-+]?\d*\.?\d+', args)
            if len(nums) >= 2:
                current_x, current_y = float(nums[0]), float(nums[1])
                current_stroke.append((current_x, current_y))
        elif cmd.upper() == 'L':
            # Line to
            nums = re.findall(r'[-+]?\d*\.?\d+', args)
            if len(nums) >= 2:
                current_x, current_y = float(nums[0]), float(nums[1])
                current_stroke.append((current_x, current_y))
        elif cmd.upper() == 'C':
            # Cubic bezier - use end point
            nums = re.findall(r'[-+]?\d*\.?\d+', args)
            if len(nums) >= 6:
                current_x, current_y = float(nums[4]), float(nums[5])
                current_stroke.append((current_x, current_y))
        elif cmd.upper() == 'Q':
            # Quadratic bezier - use end point
            nums = re.findall(r'[-+]?\d*\.?\d+', args)
            if len(nums) >= 4:
                current_x, current_y = float(nums[2]), float(nums[3])
                current_stroke.append((current_x, current_y))
        elif cmd.upper() == 'Z':
            # Close path - connect to first point
            if current_stroke:
                current_stroke.append(current_stroke[0])
    
    # Add the last stroke
    if current_stroke:
        strokes.append(current_stroke)
    
    if not strokes:
        return []
    
    # Normalize all strokes to 0-1 range using the overall bounding box
    all_points = [p for stroke in strokes for p in stroke]
    if not all_points:
        return []
    
    x_coords = [p[0] for p in all_points]
    y_coords = [p[1] for p in all_points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x if max_x != min_x else 1
    height = max_y - min_y if max_y != min_y else 1
    
    # Normalize each stroke
    normalized_strokes = []
    for stroke in strokes:
        if not stroke:
            continue
        
        # Sample points evenly along this stroke
        normalized_points = []
        total_points = min(len(stroke), num_points)
        
        for i in range(total_points):
            idx = int(i * (len(stroke) - 1) / (total_points - 1)) if total_points > 1 else 0
            x, y = stroke[idx]
            norm_x = (x - min_x) / width if width > 0 else 0.5
            norm_y = (y - min_y) / height if height > 0 else 0.5
            normalized_points.append(f"{norm_x:.4f},{norm_y:.4f}")
        
        if normalized_points:
            normalized_strokes.append(normalized_points)
    
    return normalized_strokes


def generate_json_points(path_d, output_path):
    """Generate JSON point file from SVG path with multiple strokes for direction indicators."""
    strokes = path_to_points_simple(path_d, num_points=30)
    
    if not strokes:
        print(f"Warning: Could not generate points for {output_path}")
        return False
    
    # Create JSON with multiple strokes (each stroke gets a number indicator)
    json_data = {
        "strokes": [
            {"points": stroke_points} for stroke_points in strokes
        ]
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    return True


def main():
    font_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "lib/assets/phontics_assets_points/telugu_phontics"
    
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
            font_bytes = None
            for url in DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = download_font(url)
                if font_bytes:
                    break
            if not font_bytes:
                print("\nCould not download font from any URL.")
                print("Please download NotoSansTelugu-Regular.ttf manually and provide the path:")
                print("  python3 tools/extract_telugu_letters.py /path/to/NotoSansTelugu-Regular.ttf")
                print("\nYou can download it from: https://fonts.google.com/noto/specimen/Noto+Sans+Telugu")
    
    if not font_bytes:
        print("Error: Could not load font")
        print("Please provide a font path or URL as the first argument")
        sys.exit(1)
    
    # Extract all Telugu letters
    extracted = {}
    for codepoint, name in TELUGU_LETTERS.items():
        char = chr(codepoint)
        print(f"\nExtracting {char} (U+{codepoint:04X}) - {name}...", end=' ')
        result = extract_glyph_path(font_bytes, codepoint)
        
        if result:
            path_d, em = result
            normalized_path = normalize_path_coordinates(path_d, em)
            extracted[codepoint] = (name, normalized_path, path_d, char)
            print("✓")
        else:
            print("✗")
    
    if not extracted:
        print("\nError: No letters were extracted. Please check the font file.")
        sys.exit(1)
    
    # Generate output files
    print(f"\nGenerating output files in {output_dir}...")
    
    svg_paths = {}
    for codepoint, (name, normalized_path, original_path, char) in extracted.items():
        # Generate JSON point files (big and small versions)
        big_json = os.path.join(output_dir, f"{name}_big_PointsInfo.json")
        small_json = os.path.join(output_dir, f"{name}_small_PointsInfo.json")
        
        generate_json_points(normalized_path, big_json)
        generate_json_points(normalized_path, small_json)
        
        # Store paths for Dart file generation
        svg_paths[name] = (normalized_path, char)
    
    # Generate Dart file with SVG paths
    dart_content = "class TeluguShapePaths {\n"
    for name, (path, char) in sorted(svg_paths.items()):
        # Clean up path string for Dart
        path_clean = path.replace('\n', ' ').strip()
        # Escape single quotes
        path_clean = path_clean.replace("'", "\\'")
        dart_content += f'  // {char} - {name}\n'
        dart_content += f'  static const {name}Big = \'\'\'{path_clean}\'\'\';\n'
        dart_content += f'  static const {name}Small = \'\'\'{path_clean}\'\'\';\n'
        dart_content += f'  static const {name}Dotted = \'\'\'{path_clean}\'\'\';\n\n'
    
    dart_content += "}\n"
    
    dart_file = os.path.join("lib/src/phontics_constants", "telugu_shape_paths.dart")
    os.makedirs(os.path.dirname(dart_file), exist_ok=True)
    with open(dart_file, 'w', encoding='utf-8') as f:
        f.write(dart_content)
    
    print(f"\n✓ Generated {len(extracted)} Telugu letters")
    print(f"✓ Created JSON files in {output_dir}")
    print(f"✓ Updated {dart_file}")
    print(f"\nNext steps:")
    print(f"1. Review the generated SVG paths in {dart_file}")
    print(f"2. Update ShapePointsManger.dart to add paths for new letters")
    print(f"3. Update enum_of_arabic_and_numbers_letters.dart to add letter cases")


if __name__ == "__main__":
    main()
