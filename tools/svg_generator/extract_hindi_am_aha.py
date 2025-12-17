#!/usr/bin/env python3
"""
extract_hindi_am_aha.py - Extract proper SVGs for अं (am) and अः (aha)

This script follows a similar approach to extract_am_aha.py (Telugu):
- Extract the base अ (U+0905)
- Extract anusvara (U+0902) for अं
- Extract visarga (U+0903) for अः

Then it positions the diacritic glyphs ABOVE the base character, centered
horizontally over अ and slightly above its top (matra), and finally normalizes
the combined path into a 0 0 1000 1000 viewBox.

Usage:
  python3 tools/svg_generator/extract_hindi_am_aha.py am
  python3 tools/svg_generator/extract_hindi_am_aha.py aha
  python3 tools/svg_generator/extract_hindi_am_aha.py both
"""

import sys
import os
import io
import re
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen

# Reuse font discovery and normalization from the main Hindi extractor
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import extract_hindi_svg as base  # type: ignore


# Unicode values (Devanagari)
A_BASE = 0x0905     # अ
ANUSVARA = 0x0902   # ं (anusvara) -> अं
VISARGA = 0x0903    # ः (visarga) -> अः


def load_font(font_path_or_url=None):
    """Load a Devanagari font, preferring Kohinoor Devanagari if available.

    Handles both regular TTF files and TTC collections (e.g. Kohinoor.ttc).
    """
    actual_font_path = None
    font_bytes = None

    if font_path_or_url:
        if os.path.isfile(font_path_or_url):
            print(f"Using specified font: {font_path_or_url}")
            actual_font_path = font_path_or_url
        else:
            font_bytes = base.download_font(font_path_or_url)
    else:
        local_font = base.find_local_hindi_font()
        if local_font:
            print(f"Using local font: {local_font}")
            if "Kohinoor" in local_font:
                print("  ✓ Found Kohinoor Devanagari (better ligature/mark support)")
            actual_font_path = local_font
        else:
            print("Downloading fallback font (Noto Sans Devanagari)...")
            print("  Note: Kohinoor Devanagari is recommended for better rendering")
            for url in base.DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = base.download_font(url)
                if font_bytes:
                    break

    if not actual_font_path and not font_bytes:
        print("\nError: Could not load font")
        print("Please provide a font path or URL as the second argument")
        sys.exit(1)

    # If we have a TTC path, let TTFont pick the first face via fontNumber=0
    if actual_font_path and actual_font_path.lower().endswith(".ttc"):
        return TTFont(actual_font_path, fontNumber=0)

    # Otherwise use bytes (from path or download)
    if not font_bytes and actual_font_path:
        with open(actual_font_path, "rb") as f:
            font_bytes = f.read()

    return TTFont(io.BytesIO(font_bytes))


def get_glyph_and_bounds(font, codepoint):
    """
    Extract glyph path and bounding box for a given codepoint.

    Returns:
        (path_d, (xmin, ymin, xmax, ymax), em)
    """
    cmap = font.getBestCmap()

    if codepoint not in cmap:
        for subtable in font["cmap"].tables:
            if codepoint in subtable.cmap:
                cmap = subtable.cmap
                break
        else:
            print(f"  ✗ Codepoint U+{codepoint:04X} not found in any cmap")
            return None

    glyph_name = cmap[codepoint]
    glyph_set = font.getGlyphSet()

    if glyph_name not in glyph_set:
        print(f"  ✗ Glyph {glyph_name} not in glyph set")
        return None

    glyph = glyph_set[glyph_name]

    # Record path commands and bounds in one pass
    rec_pen = RecordingPen()
    glyph.draw(rec_pen)

    x_coords = []
    y_coords = []
    for op, coords in rec_pen.value:
        for x, y in coords:
            x_coords.append(x)
            y_coords.append(y)

    if not x_coords or not y_coords:
        print(f"  ✗ Empty outline for glyph {glyph_name}")
        return None

    xmin = min(x_coords)
    xmax = max(x_coords)
    ymin = min(y_coords)
    ymax = max(y_coords)

    # Now get SVG path string
    svg_pen = SVGPathPen(glyph_set)
    glyph.draw(svg_pen)
    path_d = svg_pen.getCommands()

    if not path_d or path_d.strip() == "M 0 0 Z":
        print(f"  ✗ Empty path for glyph {glyph_name}")
        return None

    em = font["head"].unitsPerEm if "head" in font else 1000
    print(f"  ✓ Extracted {glyph_name}: bounds=({xmin}, {ymin}, {xmax}, {ymax}), em={em}")

    return path_d, (xmin, ymin, xmax, ymax), em


def translate_path_xy(path_d, dx, dy):
    """Translate all coordinates by (dx, dy) in a simple SVG path string."""

    def transform(match):
        cmd = match.group(1)
        args = match.group(2) or ""
        cmd_upper = cmd.upper()

        if not args or cmd_upper == "Z":
            return cmd

        nums = re.findall(r"([-+]?\d*\.?\d+)", args)
        transformed = []

        if cmd_upper == "H":
            # Horizontal: only X
            for num in nums:
                try:
                    transformed.append(f"{float(num) + dx:.2f}")
                except ValueError:
                    transformed.append(num)
        elif cmd_upper == "V":
            # Vertical: only Y
            for num in nums:
                try:
                    transformed.append(f"{float(num) + dy:.2f}")
                except ValueError:
                    transformed.append(num)
        else:
            # Commands with (x, y) pairs
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i % 2 == 0:  # X
                        val += dx
                    else:           # Y
                        val += dy
                    transformed.append(f"{val:.2f}")
                except ValueError:
                    transformed.append(num)

        return f"{cmd} {' '.join(transformed)}"

    return re.sub(r"([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]*)", transform, path_d)


def position_mark_above_base(base_bounds, mark_bounds, gap, center_factor=0.5):
    """
    Compute (dx, dy) to place a mark ABOVE the base, centered horizontally.

    base_bounds: (bxmin, bymin, bxmax, bymax)
    mark_bounds: (mxmin, mymin, mxmax, mymax)
    gap: extra gap above base top (same units as glyph coordinates)
    """
    bxmin, bymin, bxmax, bymax = base_bounds
    mxmin, mymin, mxmax, mymax = mark_bounds

    # Choose a horizontal anchor between left (0.0) and right (1.0) of base.
    # 0.5 = center, >0.5 moves towards right; we use ~0.75 for अं/अः
    base_cx = bxmin + (bxmax - bxmin) * center_factor
    mark_cx = (mxmin + mxmax) / 2.0

    dx = base_cx - mark_cx

    # Place bottom of mark (mymin + dy) at bymax + gap
    dy = (bymax + gap) - mymin

    return dx, dy


def extract_am(font, output_dir):
    """Extract अं (am)."""
    print("\nExtracting अं (am)...")

    print("  Extracting base 'a' (U+0905)...")
    base_result = get_glyph_and_bounds(font, A_BASE)
    if not base_result:
        print("  ✗ Failed to extract base 'a'")
        return False

    base_path, base_bounds, em = base_result

    print("  Extracting anusvara (U+0902)...")
    mark_result = get_glyph_and_bounds(font, ANUSVARA)
    if not mark_result:
        print("  ✗ Failed to extract anusvara")
        return False

    mark_path, mark_bounds, _ = mark_result

    # Compute translation to put anusvara above base, with small gap
    gap = em * 0.05
    # Place anusvara slightly towards the right side of the base
    dx, dy = position_mark_above_base(base_bounds, mark_bounds, gap, center_factor=0.75)
    print(f"  Positioning anusvara with dx={dx:.2f}, dy={dy:.2f}")

    translated_mark = translate_path_xy(mark_path, dx, dy)

    combined = f"{base_path} {translated_mark}"
    normalized = base.normalize_path_coordinates(combined, em)

    save_svg_and_path(normalized, "am", output_dir, "अं")
    return True


def extract_aha(font, output_dir):
    """Extract अः (aha)."""
    print("\nExtracting अः (aha)...")

    print("  Extracting base 'a' (U+0905)...")
    base_result = get_glyph_and_bounds(font, A_BASE)
    if not base_result:
        print("  ✗ Failed to extract base 'a'")
        return False

    base_path, base_bounds, em = base_result

    print("  Extracting visarga (U+0903)...")
    mark_result = get_glyph_and_bounds(font, VISARGA)
    if not mark_result:
        print("  ✗ Failed to extract visarga")
        return False

    mark_path, mark_bounds, _ = mark_result

    # For visarga, tuck the two dots close to the right edge of अ
    gap = em * 0.05
    dx, dy = position_mark_above_base(base_bounds, mark_bounds, gap, center_factor=1.0)
    print(f"  Positioning visarga with dx={dx:.2f}, dy={dy:.2f}")

    translated_mark = translate_path_xy(mark_path, dx, dy)

    combined = f"{base_path} {translated_mark}"
    normalized = base.normalize_path_coordinates(combined, em)

    save_svg_and_path(normalized, "aha", output_dir, "अः")
    return True


def save_svg_and_path(path_d, letter_name, output_dir, label_char):
    """Save SVG and path text files into tools/svg_generator/out_hin."""
    if not output_dir:
        output_dir = "tools/svg_generator/out_hin"

    os.makedirs(output_dir, exist_ok=True)

    svg_path = os.path.join(output_dir, f"{letter_name}_extracted.svg")
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{path_d}" fill="black" stroke="none"/>
</svg>'''
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"  ✓ Saved SVG: {svg_path}")

    txt_path = os.path.join(output_dir, f"{letter_name}_path.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(path_d)
    print(f"  ✓ Saved path: {txt_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_hindi_am_aha.py [am|aha|both] [font_path_or_url] [output_dir]")
        sys.exit(1)

    which = sys.argv[1].lower()
    font_arg = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/svg_generator/out_hin"

    font = load_font(font_arg)

    ok = True
    if which in ("am", "both"):
        ok = extract_am(font, output_dir) and ok
    if which in ("aha", "both"):
        ok = extract_aha(font, output_dir) and ok

    if not ok:
        sys.exit(1)

    print("\n✓ Done")


if __name__ == "__main__":
    main()


