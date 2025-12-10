# Arrow & Number Placement Editor

This tool allows you to manually place arrows and numbers on SVG letters for the tracing game.

## How to Use

### 1. Open the HTML Editor

Open `arrow_number_editor.html` in a web browser (Chrome, Firefox, or Edge recommended).

### 2. Load Your SVG Paths

1. **Paste SVG Path Data:**
   - Copy the SVG path string from your Dart constants (e.g., from `telugu_shape_paths.dart`)
   - Paste it into the "SVG Path" textarea
   
2. **Paste Centerline Path (Optional):**
   - Copy the centerline/dotted path string
   - Paste it into the "Centerline Path" textarea
   
3. **Set ViewBox:**
   - Enter the viewBox dimensions (default: "0 0 200 200")
   
4. **Click "Load Paths"** to render the paths

### 3. Place Arrows and Numbers

1. **Select Mode:**
   - Choose "Place Arrow" to add directional arrows
   - Choose "Place Number" to add stroke numbers

2. **For Arrows:**
   - Select arrow type from dropdown (Triangle, Chevron, Diamond, etc.)
   - **Move your mouse** over the canvas to see a preview of the arrow
   - Click where you want to place the arrow

3. **For Numbers:**
   - Set the stroke number (1, 2, 3, etc.) before placing
   - Click on the SVG where you want the number to appear

4. **Remove Items:**
   - Click "Remove" next to any item in the list to delete it

### 4. Export Your Work

1. Click "Export JSON" to save your placement data
2. This creates a `arrow_number_placement.json` file

### 5. Process with Python Script

Run the Python script to convert your placements to Flutter-compatible format:

```bash
python process_arrow_numbers.py placement.json letter.svg output.json output.dart ka
```

Arguments:
- `placement.json` - The JSON file exported from the HTML editor
- `letter.svg` - The SVG file you used (e.g., `ka_extracted.svg`)
- `output.json` - Output JSON file (optional)
- `output.dart` - Output Dart code file (optional)
- `ka` - Letter name for Dart class (optional)

### 6. Integration into Flutter App

The generated Dart code can be integrated into the Flutter app to use your custom arrow and number positions.

## Arrow Types

The editor supports multiple arrow styles:
- **Triangle (Filled)**: Solid filled triangle arrow
- **Triangle (Outline)**: Outlined triangle arrow
- **Chevron**: V-shaped arrow
- **Arrow Line**: Line with arrowhead marker
- **Diamond**: Diamond-shaped arrow

## Tips

- **Preview before placing:** Move your mouse to see arrow preview before clicking
- **Place numbers at arrow heads:** Click where arrows point to place numbers
- **Use consistent spacing:** Try to maintain similar spacing between arrows
- **One number per arrow:** For strokes with 2 arrows, place 2 numbers (same stroke number)
- **Test placement:** Export and check the coordinates before finalizing

## File Structure

```
tools/arrow_number_editor/
├── arrow_number_editor.html    # Interactive editor
├── process_arrow_numbers.py    # Processing script
└── README.md                   # This file
```

## Output Format

The processed JSON contains:
- `arrows`: List of arrow positions (normalized 0-1 coordinates)
- `numbers`: Map of stroke numbers to their positions
- `metadata`: Information about the placement

The Dart code provides static constants that can be used in the Flutter app.

