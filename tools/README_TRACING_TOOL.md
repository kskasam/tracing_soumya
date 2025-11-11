# Interactive SVG Tracing Tool - Quick Start Guide

## Step 1: Start the Server

Open a terminal in the project root and run:

```bash
cd /Users/shiva/Documents/flutter_tracing/flutter_tracing
python3 tools/run_trace_tool.py
```

You should see:
```
================================================================================
Interactive SVG Tracing Tool
================================================================================

Server starting on port 8000...

Open your browser to:
  http://localhost:8000/tools/interactive_trace_tool.html

Press Ctrl+C to stop the server
================================================================================
```

The browser should open automatically. If not, manually open:
**http://localhost:8000/tools/interactive_trace_tool.html**

## Step 2: Load a Telugu Letter

1. In the dropdown, select a Telugu letter (e.g., "అ (a)")
2. Click "Load from Telugu Letter"
   - This loads the SVG path from the Dart file
   - The letter will appear on the canvas

**OR** manually paste an SVG path:
1. Copy an SVG path from `lib/src/phontics_constants/telugu_shape_paths.dart`
2. Paste it in the "SVG Path Input" field
3. Click "Load SVG"

## Step 3: Trace the Letter

1. **Click "Start New Stroke"** to begin tracing
2. **Click on the SVG path** where you want to start
   - A red circle with number "0" appears
   - This is your first point
3. **Continue clicking** along the path in the direction you want to trace
   - Each click adds a numbered point
   - A blue line connects the points
4. **Click "Finish Current Stroke"** when done with this stroke
5. **Repeat** for additional strokes:
   - Click "Start New Stroke" again
   - Trace the next part of the letter
   - Click "Finish Current Stroke"

## Step 4: Generate JSON

1. After tracing all strokes, click **"Generate JSON"**
2. The JSON will appear in the output box
3. Click **"Copy JSON"** to copy it to clipboard
4. Paste it into your Telugu letter JSON file:
   ```
   lib/assets/phontics_assets_points/telugu_phontics/{letter}_big_PointsInfo.json
   ```

## Step 5: Verify

After saving the JSON, you can visualize it:
```bash
python3 tools/visualize_telugu_points.py {letter}
```

Then open the generated HTML file to see if the points align correctly.

## Tips

- **Click precisely**: The tool snaps your clicks to the nearest point on the path
- **Order matters**: Points are recorded in the order you click
- **Multiple strokes**: Use separate strokes for different parts of the letter
- **Clear and restart**: Use "Clear All" if you make a mistake

## Troubleshooting

**Server won't start?**
- Make sure port 8000 is not in use
- Try a different port by editing `run_trace_tool.py`

**Can't load Telugu letter?**
- Make sure the Dart file exists: `lib/src/phontics_constants/telugu_shape_paths.dart`
- Try pasting the SVG path manually

**Points not appearing?**
- Make sure you clicked "Start New Stroke" first
- Click directly on or near the SVG path

**JSON format wrong?**
- The tool generates the correct format automatically
- Make sure you clicked "Generate JSON" after tracing

