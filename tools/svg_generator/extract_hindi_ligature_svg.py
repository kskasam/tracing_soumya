#!/usr/bin/env python3
"""
extract_hindi_ligature_svg.py - Extract SVG paths for Hindi ligatures/syllables

This script is intended for multi-codepoint sequences that rely on proper
shaping, such as:
  - ksha -> क्ष  (क् + ष)
  - tra  -> त्र  (त् + र)
  - gya  -> ज्ञ  (ज् + ञ)
  - am   -> अं   (अ + ं)
  - aha  -> अः  (अ + ः)

It uses HarfBuzz for text shaping and fontTools for extracting glyph outlines,
then normalizes and saves SVGs into the same folder as the other Hindi SVGs:
  tools/svg_generator/out_hin

Usage:
  python3 tools/svg_generator/extract_hindi_ligature_svg.py [name_or_text] [font_path_or_url] [output_dir]

Examples:
  # Using symbolic names
  python3 tools/svg_generator/extract_hindi_ligature_svg.py ksha
  python3 tools/svg_generator/extract_hindi_ligature_svg.py tra
  python3 tools/svg_generator/extract_hindi_ligature_svg.py gya
  python3 tools/svg_generator/extract_hindi_ligature_svg.py am
  python3 tools/svg_generator/extract_hindi_ligature_svg.py aha

  # Using direct Hindi text
  python3 tools/svg_generator/extract_hindi_ligature_svg.py क्ष

Dependencies:
  fonttools, uharfbuzz, requests

Install (example):
  python3 -m pip install --user fonttools uharfbuzz requests
"""

import sys
import os
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

# HarfBuzz Python bindings (pip package: uharfbuzz)
import uharfbuzz as hb

# Make sure we can import the base Hindi extractor utilities from the same folder
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import extract_hindi_svg as base  # type: ignore


# Map symbolic names to Hindi text sequences
HINDI_SYLLABLES = {
    # Conjuncts
    "ksha": "\u0915\u094D\u0937",  # क्ष = क् + ष
    "tra": "\u0924\u094D\u0930",   # त्र = त् + र
    "gya": "\u091C\u094D\u091E",   # ज्ञ = ज् + ञ
    # Vowel + marks
    "am": "\u0905\u0902",          # अं = अ + ं (anusvara)
    "aha": "\u0905\u0903",         # अः = अ + ः (visarga)
}

# Optional fine-tuning offsets for specific syllables (units: font design units)
# These let us nudge marks like visarga if the font's default placement
# doesn't look good for our tracing UI.
SYLLABLE_OFFSETS = {
    # For 'aha' (अः), move visarga dots slightly left so they align nicer
    # with the main character. You can tweak these numbers as needed.
    "aha": {
        "visarga_dx": -40.0,
        "visarga_dy": 0.0,
    },
}


def load_font(font_path_or_url=None):
    """
    Load a Devanagari font, preferring Kohinoor Devanagari if available.

    Returns:
        (font_bytes, actual_font_path)
    """
    font_bytes = None
    actual_font_path = None

    if font_path_or_url:
        if os.path.isfile(font_path_or_url):
            print(f"Using specified font: {font_path_or_url}")
            actual_font_path = font_path_or_url
            # For TTC we use the path directly; otherwise read bytes
            if not font_path_or_url.lower().endswith(".ttc"):
                with open(font_path_or_url, "rb") as f:
                    font_bytes = f.read()
        else:
            font_bytes = base.download_font(font_path_or_url)
    else:
        # Prefer local Kohinoor / Devanagari fonts
        local_font = base.find_local_hindi_font()
        if local_font:
            print(f"Using local font: {local_font}")
            if "Kohinoor" in local_font:
                print("  ✓ Found Kohinoor Devanagari (better ligature/conjunct support)")
            actual_font_path = local_font
            if not local_font.lower().endswith(".ttc"):
                with open(local_font, "rb") as f:
                    font_bytes = f.read()
        else:
            print("Downloading fallback font (Noto Sans Devanagari)...")
            print("  Note: Kohinoor Devanagari is recommended for better letter rendering")
            for url in base.DEFAULT_FONT_URLS:
                print(f"Trying: {url}")
                font_bytes = base.download_font(url)
                if font_bytes:
                    break

    if not font_bytes and not actual_font_path:
        print("\nError: Could not load font")
        print("Please provide a font path or URL as the second argument")
        print("\nRecommended: Use Kohinoor Devanagari (often pre-installed on macOS)")
        print("Fallback: Download NotoSansDevanagari-Regular.ttf from:")
        print("https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
        sys.exit(1)

    # Ensure we have raw font bytes for HarfBuzz, even for TTC paths
    if font_bytes is None and actual_font_path:
        with open(actual_font_path, "rb") as f:
            font_bytes = f.read()

    return font_bytes, actual_font_path


def shape_text_to_path(text, font_bytes, font_path=None):
    """
    Shape a Hindi text sequence with HarfBuzz and return a combined SVG path.

    This will:
      - Shape the text into glyph IDs and positions
      - Use fontTools to draw each glyph outline
      - Apply the HarfBuzz positioning and combine into a single path

    Returns:
      (path_d, em)  where em is unitsPerEm from the font
    """
    if not text:
        raise ValueError("Empty text sequence")

    # Create HarfBuzz face/font from bytes
    blob = hb.Blob(font_bytes)
    face = hb.Face(blob, 0)
    font = hb.Font(face)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    # Force Devanagari script and Hindi language for better shaping
    buf.script = "deva"
    buf.language = "hi"
    hb.shape(font, buf, {})

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    if not infos:
        raise RuntimeError("HarfBuzz returned no glyphs for text: %r" % text)

    # Open the font with fontTools for glyph outlines
    # For TTC collections, we use fontNumber=0, which is where Devanagari lives
    if font_path and font_path.lower().endswith(".ttc"):
        ttfont = TTFont(font_path, fontNumber=0)
    else:
        ttfont = TTFont(io.BytesIO(font_bytes))

    glyph_order = ttfont.getGlyphOrder()
    glyph_set = ttfont.getGlyphSet()

    # unitsPerEm for later normalization
    em = ttfont["head"].unitsPerEm if "head" in ttfont else 1000

    # HarfBuzz uses 26.6 fixed-point for positions; convert to float
    FIXED_26_6 = 64.0

    combined_pen = SVGPathPen(glyph_set)

    x_cursor = 0.0
    y_cursor = 0.0

    # Special handling for visarga position in "aha" (अः)
    adjust_visarga = False
    visarga_dx = visarga_dy = 0.0
    # Detect our configured 'aha' sequence by exact match
    if text == HINDI_SYLLABLES.get("aha"):
        adjust_visarga = True
        conf = SYLLABLE_OFFSETS.get("aha", {})
        visarga_dx = float(conf.get("visarga_dx", 0.0))
        visarga_dy = float(conf.get("visarga_dy", 0.0))
        # Compute UTF‑8 byte index of the visarga character for cluster matching
        # text = [अ, ः], so second_char_start is len(first_char_utf8)
        first_char_utf8 = text[0].encode("utf-8")
        visarga_cluster_start = len(first_char_utf8)
    else:
        visarga_cluster_start = -1

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

        # If this glyph belongs to the visarga in "aha", apply a small offset tweak
        if adjust_visarga and info.cluster >= visarga_cluster_start:
            x_offset += visarga_dx
            y_offset += visarga_dy

        # In font coordinates, Y-positive is up. We'll flip later in normalization,
        # so we apply the offsets in the same coordinate system here.
        tx = x_cursor + x_offset
        ty = y_cursor + y_offset

        # Draw glyph with translation applied
        tpen = TransformPen(combined_pen, (1, 0, 0, 1, tx, ty))
        glyph.draw(tpen)

        x_cursor += pos.x_advance / FIXED_26_6
        y_cursor += pos.y_advance / FIXED_26_6

    path_d = combined_pen.getCommands()
    if not path_d or path_d.strip() == "M 0 0 Z":
        raise RuntimeError("Empty path generated for text: %r" % text)

    return path_d, em


def extract_syllable(name_or_text, font_bytes, output_dir, font_path=None):
    """
    Extract a Hindi syllable/ligature as SVG.

    Args:
        name_or_text: symbolic name (ksha/tra/gya/am/aha) or direct Hindi text
        font_bytes:   font file bytes
        output_dir:   output directory for SVG/TXT
        font_path:    path to font file (for TTC collections)
    """
    key = name_or_text.lower()
    if key in HINDI_SYLLABLES:
        text = HINDI_SYLLABLES[key]
        label = key
    else:
        # Treat as direct Hindi text
        text = name_or_text
        label = name_or_text

    print(f"\nShaping text '{text}' for '{label}'...")

    try:
        path_d, em = shape_text_to_path(text, font_bytes, font_path)
    except Exception as e:
        print(f"  ✗ Failed to shape/extract: {e}")
        return False

    normalized_path = base.normalize_path_coordinates(path_d, em)

    # Use same naming style as the base extractor
    safe_label = label
    # Avoid problematic filename characters
    for ch in (' ', '/', '\\'):
        safe_label = safe_label.replace(ch, "_")

    svg_output = os.path.join(output_dir, f"{safe_label}_extracted.svg")
    # Use the first character of the text for the char label, if available
    char_for_label = text[0]
    base.save_svg_file(normalized_path, svg_output, label, char_for_label)

    path_output = os.path.join(output_dir, f"{safe_label}_path.txt")
    os.makedirs(os.path.dirname(path_output), exist_ok=True)
    with open(path_output, "w", encoding="utf-8") as f:
        f.write(normalized_path)

    print(f"  ✓ Saved path to: {path_output}")
    print(f"  ✓ Path (first 100 chars): {normalized_path[:100]}...")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_hindi_ligature_svg.py [name_or_text] [font_path_or_url] [output_dir]")
        print("\nSymbolic names supported:")
        print("  " + ", ".join(sorted(HINDI_SYLLABLES.keys())))
        print("\nExamples:")
        print("  python3 extract_hindi_ligature_svg.py ksha")
        print("  python3 extract_hindi_ligature_svg.py क्ष")
        print("  python3 extract_hindi_ligature_svg.py am")
        sys.exit(1)

    name_or_text = sys.argv[1]
    font_arg = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/svg_generator/out_hin"

    font_bytes, actual_font_path = load_font(font_arg)

    if extract_syllable(name_or_text, font_bytes, output_dir, actual_font_path):
        print(f"\n✓ Successfully extracted '{name_or_text}'")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()


