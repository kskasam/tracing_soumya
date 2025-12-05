# SVG Generator for Telugu Letters

This folder contains scripts to extract SVG paths from Telugu fonts.

## extract_telugu_svg.py

Generic script to extract any Telugu letter from a TTF font and generate SVG paths.

### Installation

Install required dependencies:
```bash
python3 -m pip install --user fonttools requests
```

### Usage

#### Extract a specific letter (e.g., 'aa'):
```bash
python3 tools/svg_generator/extract_telugu_svg.py aa
```

#### Extract all Telugu letters:
```bash
python3 tools/svg_generator/extract_telugu_svg.py all
```

#### Extract with custom font path:
```bash
python3 tools/svg_generator/extract_telugu_svg.py aa /path/to/NotoSansTelugu-Regular.ttf
```

#### Extract with custom output directory:
```bash
python3 tools/svg_generator/extract_telugu_svg.py aa /path/to/font.ttf tools/svg_generator/output
```

### Available Letters

The script supports all common Telugu letters:
- Vowels: a, aa, i, ii, u, uu, e, ee, ai, o, oo, au
- Consonants: ka, kha, ga, gha, nga, cha, chha, ja, jha, nya, ta, tha, da, dha, na, ta2, tha2, da2, dha2, na2, pa, pha, ba, bha, ma, ya, ra, la, lla, va, sha, ssa, sa, ha

### Output

For each letter, the script generates:
1. `{letter_name}_extracted.svg` - Full SVG file with the letter path
2. `{letter_name}_path.txt` - Just the SVG path data (for copying to Dart code)

### Output Location

By default, files are saved to `tools/svg_generator/output/`

### Font Sources

The script will try to:
1. Use a font path provided as argument
2. Find `downloaded_font.ttf` in the workspace root
3. Search common system font directories
4. Download from Google Fonts if not found locally

### Example

```bash
# Extract 'aa' letter (ఆ)
python3 tools/svg_generator/extract_telugu_svg.py aa

# Output:
# Extracting ఆ (U+0C06) - aa...
#   ✓ Saved SVG to: tools/svg_generator/output/aa_extracted.svg
#   ✓ Saved path to: tools/svg_generator/output/aa_path.txt
#   ✓ Path: M 123.45 234.56 L 345.67 456.78...
# 
# ✓ Successfully extracted 'aa'
```

