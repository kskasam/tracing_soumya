#!/usr/bin/env python3
"""
extract_composite_hindi.py - Extract composite Hindi characters (अं, अः, क्ष, त्र, ज्ञ) as SVG paths

Usage:
  python3 tools/svg_generator/extract_composite_hindi.py [am|aha|ksha|tra|gya|all]

This is analogous to extract_composite_telugu.py but for Devanagari. It:
  - Shapes the full text (e.g. "अः", "क्ष") using HarfBuzz
  - Draws the resulting glyph sequence with fontTools
  - Normalizes the combined outline into a 0 0 1000 1000 viewBox using
    the same normalize_path_coordinates used by other Hindi SVG tools.
"""

import sys
import os
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

import uharfbuzz as hb

# Reuse font discovery and normalization from Hindi extractor
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import extract_hindi_svg as base  # type: ignore


COMPOSITE_CHARS = {
    "am": "अं",    # अ + ं (anusvara)
    "aha": "अः",   # अ + ः (visarga)
    "ksha": "क्ष",  # क् + ष
    "tra": "त्र",   # त् + र
    "gya": "ज्ञ",   # ज् + ञ
}


def load_font_bytes(font_path_or_url=None):
    """Load Devanagari font bytes (TTF or TTC) similarly to extract_hindi_svg."""
    font_bytes = None
    actual_font_path = None

    if font_path_or_url:
        if os.path.isfile(font_path_or_url):
            actual_font_path = font_path_or_url
            with open(font_path_or_url, "rb") as f:
                font_bytes = f.read()
        else:
            font_bytes = base.download_font(font_path_or_url)
    else:
        local_font = base.find_local_hindi_font()
        if local_font:
            print(f"Using local font: {local_font}")
            actual_font_path = local_font
            with open(local_font, "rb") as f:
                font_bytes = f.read()
        else:
            print("Downloading fallback font (Noto Sans Devanagari)...")
            print("  Note: Kohinoor Devanagari is recommended for better rendering")
            for url in base.DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = base.download_font(url)
                if font_bytes:
                    break

    if not font_bytes:
        print("\nError: Could not load font")
        print("Please provide a font path or URL as the second argument")
        sys.exit(1)

    return font_bytes, actual_font_path


def shape_text_to_path(text, font_bytes, font_path=None):
    """Shape a Hindi text string with HarfBuzz and combine all glyph outlines."""
    if not text:
        raise ValueError("Empty text")

    blob = hb.Blob(font_bytes)
    face = hb.Face(blob, 0)
    font = hb.Font(face)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    buf.script = "deva"
    buf.language = "hi"
    hb.shape(font, buf, {})

    infos = buf.glyph_infos
    positions = buf.glyph_positions
    if not infos:
        raise RuntimeError("HarfBuzz returned no glyphs")

    # Open font with fontTools (handle TTC collections)
    if font_path and font_path.lower().endswith(".ttc"):
        ttfont = TTFont(font_path, fontNumber=0)
    else:
        ttfont = TTFont(io.BytesIO(font_bytes))

    glyph_order = ttfont.getGlyphOrder()
    glyph_set = ttfont.getGlyphSet()
    em = ttfont["head"].unitsPerEm if "head" in ttfont else 1000

    FIXED_26_6 = 64.0

    pen = SVGPathPen(glyph_set)
    x_cursor = 0.0
    y_cursor = 0.0

    for info, pos in zip(infos, positions):
        gid = info.codepoint
        if gid < 0 or gid >= len(glyph_order):
            continue
        glyph_name = glyph_order[gid]
        if glyph_name not in glyph_set:
            continue

        glyph = glyph_set[glyph_name]

        x_offset = pos.x_offset / FIXED_26_6
        y_offset = pos.y_offset / FIXED_26_6

        tx = x_cursor + x_offset
        ty = y_cursor + y_offset

        # Translate by (tx, ty) using a nested pen
        from fontTools.pens.transformPen import TransformPen

        tpen = TransformPen(pen, (1, 0, 0, 1, tx, ty))
        glyph.draw(tpen)

        x_cursor += pos.x_advance / FIXED_26_6
        y_cursor += pos.y_advance / FIXED_26_6

    path_d = pen.getCommands()
    if not path_d or path_d.strip() == "M 0 0 Z":
        raise RuntimeError("Empty path from shaping")

    return path_d, em


def save_svg(path_d, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{path_d}" fill="black" stroke="none"/>
</svg>'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"  ✓ Saved SVG: {output_path}")


def extract_composite(name, font_bytes, font_path, output_dir):
    if name not in COMPOSITE_CHARS:
        print(f"Error: Unknown composite '{name}'")
        print("Available:", ", ".join(COMPOSITE_CHARS.keys()))
        return False

    text = COMPOSITE_CHARS[name]
    print(f"\nExtracting {text} ({name})...")

    try:
        raw_path, em = shape_text_to_path(text, font_bytes, font_path)
    except Exception as e:
        print(f"  ✗ Failed to shape/draw: {e}")
        return False

    normalized = base.normalize_path_coordinates(raw_path, em)

    svg_path = os.path.join(output_dir, f"{name}_extracted.svg")
    save_svg(normalized, svg_path)

    txt_path = os.path.join(output_dir, f"{name}_path.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(normalized)
    print(f"  ✓ Saved path: {txt_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_composite_hindi.py [am|aha|ksha|tra|gya|all] [font_path_or_url] [output_dir]")
        sys.exit(1)

    which = sys.argv[1].lower()
    font_arg = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/svg_generator/out_hin"

    font_bytes, actual_font_path = load_font_bytes(font_arg)

    if which == "all":
        ok_count = 0
        for name in COMPOSITE_CHARS.keys():
            if extract_composite(name, font_bytes, actual_font_path, output_dir):
                ok_count += 1
        print(f"\n✓ Extracted {ok_count}/{len(COMPOSITE_CHARS)} composites")
        if ok_count != len(COMPOSITE_CHARS):
            sys.exit(1)
    else:
        if not extract_composite(which, font_bytes, actual_font_path, output_dir):
            sys.exit(1)


if __name__ == "__main__":
    main()


