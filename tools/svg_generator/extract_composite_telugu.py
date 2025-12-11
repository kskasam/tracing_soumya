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
    'ksha': 'క్ష',  # క (U+0C15) + ్ (U+0C4D virama) + ష (U+0C37 sha)
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


def process_text_with_gsub(font, text_string):
    """Process text string through GSUB to get final glyph sequence."""
    try:
        from fontTools.otlLib.builder import Builder
        from fontTools.ttLib.tables.otTables import Sequence
        
        # Get initial glyph sequence
        cmap = font.getBestCmap()
        initial_glyphs = []
        for char in text_string:
            codepoint = ord(char)
            if codepoint in cmap:
                initial_glyphs.append(cmap[codepoint])
            else:
                for subtable in font['cmap'].tables:
                    if codepoint in subtable.cmap:
                        initial_glyphs.append(subtable.cmap[codepoint])
                        break
        
        if not initial_glyphs:
            return None
        
        # Process through GSUB if available
        if 'GSUB' not in font:
            return initial_glyphs
        
        gsub = font['GSUB']
        if not gsub or not gsub.table:
            return initial_glyphs
        
        # This is complex - for now, return initial glyphs
        # GSUB processing requires a full OpenType layout engine
        return initial_glyphs
        
    except Exception as e:
        print(f"    Note: Could not process GSUB: {e}")
        return None


def resolve_ligature(font, glyph_names, text_string):
    """Try to resolve a ligature from GSUB table or by searching glyph names."""
    glyph_set = font.getGlyphSet()
    
    # First, try to find ligature by common naming patterns
    component_names = [name for name, _ in glyph_names]
    
    # Try common ligature name patterns
    potential_names = [
        '_'.join(component_names),  # ka_viramatelu_ssatelu
        ''.join([name.replace('telu', '').replace('telugu', '') for name in component_names]),  # kaviramassha
        'ksha',  # Direct name
        'kshatelu',  # With telu suffix
        'kshatelugu',  # With telugu suffix
    ]
    
    for potential_name in potential_names:
        if potential_name in glyph_set:
            print(f"    Found ligature by name pattern: {potential_name}")
            return potential_name
    
    # Try GSUB table - search for ligatures that match our sequence
    if 'GSUB' not in font:
        return None
    
    try:
        gsub = font['GSUB']
        if not gsub or not gsub.table:
            return None
        
        lookup_list = gsub.table.LookupList
        if not lookup_list:
            return None
        
        # Search through all lookups for ligature substitutions
        for lookup in lookup_list.Lookup:
            if lookup.LookupType == 4:  # Ligature substitution
                for subtable in lookup.SubTable:
                    # subtable.ligatures is a dict mapping first glyph to list of ligatures
                    first_glyph = glyph_names[0][0]
                    if first_glyph in subtable.ligatures:
                        for ligature in subtable.ligatures[first_glyph]:
                            # Check if components match (excluding the first one which is the key)
                            # ligature.Component contains the remaining components
                            if len(ligature.Component) == len(glyph_names) - 1:
                                match = True
                                for i, comp_glyph in enumerate(ligature.Component):
                                    # Component[i] should match glyph_names[i+1]
                                    if comp_glyph != glyph_names[i+1][0]:
                                        match = False
                                        break
                                if match:
                                    ligature_glyph = ligature.LigGlyph
                                    if ligature_glyph in glyph_set:
                                        print(f"    Found ligature via GSUB: {ligature_glyph}")
                                        print(f"      Components: {first_glyph} + {' + '.join(ligature.Component)}")
                                        return ligature_glyph
    except Exception as e:
        print(f"    Note: Could not resolve ligature via GSUB: {e}")
    
    return None


def extract_text_path(font_bytes, text_string):
    """Extract SVG path for a text string, using ligatures when available."""
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
        
        # Try to resolve ligature first
        ligature_glyph_name = resolve_ligature(font, glyph_names, text_string)
        
        if ligature_glyph_name and ligature_glyph_name in glyph_set:
            # Use the ligature glyph directly
            print(f"  Using ligature glyph: {ligature_glyph_name}")
            glyph = glyph_set[ligature_glyph_name]
            pen = SVGPathPen(glyph_set)
            glyph.draw(pen)
            path_d = pen.getCommands()
            
            if path_d and path_d.strip() != 'M 0 0 Z':
                em = font['head'].unitsPerEm if 'head' in font else 1000
                print(f"  Ligature path length: {len(path_d)} chars")
                return path_d, em
            else:
                print(f"  ✗ Empty ligature path, falling back to component glyphs")
        else:
            print(f"  No ligature found, combining component glyphs")
        
        # Fallback: Combine paths from all glyphs (but skip virama if it has no visual)
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
                print(f"    ✗ Empty or invalid path for {glyph_name} (may be invisible virama)")
            
            # Get glyph width for next position
            try:
                if 'hmtx' in font:
                    hmtx = font['hmtx']
                    if hasattr(hmtx, 'metrics') and glyph_name in hmtx.metrics:
                        glyph_width = hmtx.metrics[glyph_name][0]
                        print(f"    Glyph width: {glyph_width}")
                        # Only advance if glyph has visual content
                        if path_d and path_d.strip() != 'M 0 0 Z':
                            x_offset += glyph_width
                    else:
                        # Estimate width (rough approximation)
                        if path_d and path_d.strip() != 'M 0 0 Z':
                            print(f"    Using estimated width: 500")
                            x_offset += 500
                else:
                    # Estimate width (rough approximation)
                    if path_d and path_d.strip() != 'M 0 0 Z':
                        print(f"    Using estimated width: 500")
                        x_offset += 500
            except (KeyError, AttributeError, IndexError) as e:
                # Estimate width (rough approximation)
                if path_d and path_d.strip() != 'M 0 0 Z':
                    print(f"    Using estimated width: 500 (error: {e})")
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
    """
    Normalize SVG path coordinates to fit in viewBox with padding.
    Fonts use Y-up coordinates (Y increases upward), but SVG/Flutter use Y-down.
    So we first flip Y coordinates, then normalize.
    """
    # Step 1: Flip Y coordinates in original path
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', path_d)
    
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
    # Normalize the path (flip Y-axis and fit in viewBox)
    normalized_path = normalize_path(path_d, em)
    
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
        print("Usage: python3 extract_composite_telugu.py [am|aha|ksha|all]")
        print(f"\nAvailable composite characters: {', '.join(COMPOSITE_CHARS.keys())}")
        sys.exit(1)
    
    letter_name = sys.argv[1].lower()
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        # Default to output directory relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
    
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
    if letter_name == 'all':
        success_count = 0
        for name in COMPOSITE_CHARS.keys():
            if extract_composite(name, font_bytes, output_dir):
                success_count += 1
        print(f"\n✓ Successfully extracted {success_count}/{len(COMPOSITE_CHARS)} composite characters")
    else:
        if extract_composite(letter_name, font_bytes, output_dir):
            print(f"\n✓ Successfully extracted '{letter_name}'")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

