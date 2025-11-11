#!/usr/bin/env python3
"""
Visualize Telugu letter with all points labeled for manual stroke ordering.
Creates an HTML file that can be opened in a browser.

Usage:
    python3 tools/visualize_telugu_points.py <letter_name>
    
Example:
    python3 tools/visualize_telugu_points.py a
"""

import json
import sys
import os
import re

def load_telugu_path(letter_name):
    """Load the SVG path for a Telugu letter."""
    dart_file = "lib/src/phontics_constants/telugu_shape_paths.dart"
    
    if not os.path.exists(dart_file):
        print(f"Error: {dart_file} not found")
        return None
    
    with open(dart_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the big path for this letter
    pattern = rf'{letter_name}Big\s*=\s*\'\'\'([^\']+)\'\'\''
    match = re.search(pattern, content)
    
    if not match:
        print(f"Error: Could not find path for {letter_name}")
        return None
    
    return match.group(1).strip()

def load_english_path(letter_name):
    """Load the SVG path for an English letter."""
    # Try uppercase first
    letter_upper = letter_name.upper()
    letter_lower = letter_name.lower()
    dart_file = "lib/src/phontics_constants/english_shape_path2.dart"
    
    if not os.path.exists(dart_file):
        print(f"Error: {dart_file} not found")
        return None
    
    with open(dart_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try different patterns for English letters
    patterns = [
        rf'{letter_lower}ShapeBigShape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_upper}ShapeBigShape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_lower}BigShape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_upper}BigShape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_lower}Shape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_lower}lowerShape\s*=\s*\'\'\'([^\']+)\'\'\'',
        rf'{letter_lower}LoweCaseShape\s*=\s*\'\'\'([^\']+)\'\'\'',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    print(f"Error: Could not find path for {letter_name}")
    return None

def load_json_points(letter_name, is_english=False):
    """Load points from JSON file."""
    if is_english:
        # Try uppercase first
        json_file = f"lib/assets/phontics_assets_points/english_phontics/{letter_name.upper()}_PointsInfo.json"
        if not os.path.exists(json_file):
            json_file = f"lib/assets/phontics_assets_points/english_upper_phonetics/{letter_name.upper()}_PointsInfo.json"
    else:
        json_file = f"lib/assets/phontics_assets_points/telugu_phontics/{letter_name}_big_PointsInfo.json"
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return None
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    strokes = data.get('strokes', [])
    if not strokes and 'char' in data:
        # Alternative format with 'char' field
        strokes = data.get('strokes', [])
    
    all_points = []
    for stroke_idx, stroke in enumerate(strokes):
        points_list = stroke.get('points', []) if isinstance(stroke, dict) else stroke
        for point_idx, point_str in enumerate(points_list):
            x, y = map(float, point_str.split(','))
            all_points.append({
                'x': x,
                'y': y,
                'stroke': stroke_idx,
                'point_idx': point_idx,
                'point_str': point_str,
                'global_idx': len(all_points)
            })
    
    return all_points, data

def extract_svg_bounds(svg_path):
    """Extract bounding box from SVG path."""
    # Extract all coordinates
    coords = []
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', svg_path)
    
    for cmd, args in commands:
        if not args or cmd.upper() == 'Z':
            continue
        nums = re.findall(r'[-+]?\d*\.?\d+', args)
        for num in nums:
            try:
                coords.append(float(num))
            except ValueError:
                pass
    
    if not coords:
        return 0, 0, 1000, 1000  # Default
    
    x_coords = [coords[i] for i in range(0, len(coords), 2) if i < len(coords)]
    y_coords = [coords[i+1] for i in range(0, len(coords), 2) if i+1 < len(coords)]
    
    if not x_coords or not y_coords:
        return 0, 0, 1000, 1000
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Add padding
    padding = (max_x - min_x) * 0.1 if max_x != min_x else 100
    return min_x - padding, min_y - padding, max_x + padding, max_y + padding

def create_html_visualization(letter_name, svg_path, points_data):
    """Create HTML visualization with SVG and labeled points."""
    points, json_data = points_data
    
    # Get SVG bounds
    min_x, min_y, max_x, max_y = extract_svg_bounds(svg_path)
    width = max_x - min_x
    height = max_y - min_y
    
    # Use SVG bounds for viewBox
    viewbox_x = min_x
    viewbox_y = min_y
    viewbox_width = width
    viewbox_height = height
    
    # Create HTML with SVG
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Telugu Letter {letter_name.upper()} - Point Visualization</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .svg-container {{
            border: 2px solid #ddd;
            background: white;
            margin: 20px auto;
            display: block;
        }}
        .point {{
            cursor: pointer;
        }}
        .point circle {{
            fill: red;
            stroke: darkred;
            stroke-width: 2;
        }}
        .point text {{
            font-size: 12px;
            font-weight: bold;
            fill: black;
            text-anchor: middle;
            dominant-baseline: middle;
        }}
        .point:hover circle {{
            fill: orange;
            r: 8;
        }}
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .stroke-info {{
            margin: 10px 0;
            padding: 10px;
            background: #e8f4f8;
            border-left: 4px solid #2196F3;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Telugu Letter '{letter_name.upper()}' - Point Visualization</h1>
        <p style="text-align: center; color: #666;">
            <strong>How to read:</strong> Each numbered circle shows the <strong>Global Index</strong> (0, 1, 2, ...) 
            which corresponds to the order in the JSON file. Points are color-coded by stroke. 
            Hover or click on points to see details. The number on each point is its position in the JSON array.
        </p>
        <p style="text-align: center; color: #888; font-size: 0.9em;">
            <strong>JSON Mapping:</strong> The first point in stroke 0 = index 0, 
            first point in stroke 1 = index (number of points in stroke 0), etc.
        </p>
        
        <svg class="svg-container" viewBox="{viewbox_x} {viewbox_y} {viewbox_width} {viewbox_height}" width="800" height="800">
            <!-- Letter path -->
            <path d="{svg_path}" 
                  fill="lightblue" 
                  stroke="black" 
                  stroke-width="3" 
                  opacity="0.3"/>
            
            <!-- Points -->
"""
    
    # Add points to SVG - scale normalized points (0-1) to SVG coordinate system
    # The JSON points are normalized 0-1, but we need to map them to the actual SVG path bounds
    # Since both the path and points were normalized from the same original, they should align
    # But we need to account for the actual bounds of the normalized path
    
    # Calculate the actual bounds of points in normalized space to understand the mapping
    point_x_coords = [p['x'] for p in points]
    point_y_coords = [p['y'] for p in points]
    point_min_x, point_max_x = min(point_x_coords), max(point_x_coords)
    point_min_y, point_max_y = min(point_y_coords), max(point_y_coords)
    point_width = point_max_x - point_min_x if point_max_x != point_min_x else 1
    point_height = point_max_y - point_min_y if point_max_y != point_min_y else 1
    
    # Scale points to match SVG coordinate system
    # The normalized path is typically in 0-1000 range, so we scale 0-1 to that range
    # But we need to match the actual SVG bounds
    for point in points:
        # Scale normalized 0-1 points to SVG coordinate system
        # Map from [point_min_x, point_max_x] to [viewbox_x, viewbox_x + viewbox_width]
        x = viewbox_x + ((point['x'] - point_min_x) / point_width * viewbox_width) if point_width > 0 else viewbox_x + point['x'] * viewbox_width
        y = viewbox_y + ((point['y'] - point_min_y) / point_height * viewbox_height) if point_height > 0 else viewbox_y + point['y'] * viewbox_height
        idx = point['global_idx']
        stroke = point['stroke']
        point_idx = point['point_idx']
        
        # Color code by stroke
        stroke_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        color = stroke_colors[stroke % len(stroke_colors)]
        
        html_content += f"""            <g class="point" data-index="{idx}" data-stroke="{stroke}" data-point-index="{point_idx}">
                <circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="white" stroke-width="1"/>
                <text x="{x}" y="{y}" font-size="9" fill="white" text-anchor="middle" dominant-baseline="central" font-weight="bold">{idx}</text>
                <title>Global Index: {idx}, Stroke: {stroke}, Point in Stroke: {point_idx}, Coords: {point['point_str']}</title>
            </g>
"""
    
    html_content += """        </svg>
        
        <div class="info">
            <h2>Point Details</h2>
            <p><strong>Total Points:</strong> """ + str(len(points)) + """</p>
            <p><strong>Total Strokes:</strong> """ + str(len(json_data.get('strokes', []))) + """</p>
            
            <h3>Current Stroke Structure:</h3>
"""
    
    # Add stroke information
    for stroke_idx, stroke in enumerate(json_data.get('strokes', [])):
        stroke_points = stroke.get('points', [])
        html_content += f"""
            <div class="stroke-info">
                <strong>Stroke {stroke_idx + 1}</strong> ({len(stroke_points)} points):
                <table>
                    <tr>
                        <th>Global Index</th>
                        <th>Point Index</th>
                        <th>Coordinates</th>
                        <th>X</th>
                        <th>Y</th>
                    </tr>
"""
        global_idx = 0
        for prev_stroke in json_data.get('strokes', [])[:stroke_idx]:
            global_idx += len(prev_stroke.get('points', []))
        
        for point_idx, point_str in enumerate(stroke_points):
            x, y = map(float, point_str.split(','))
            # Highlight the first and last points of each stroke
            is_first = point_idx == 0
            is_last = point_idx == len(stroke_points) - 1
            row_style = 'background-color: #fff3cd; font-weight: bold;' if is_first else ('background-color: #d1ecf1; font-weight: bold;' if is_last else '')
            marker = '→ START' if is_first else ('→ END' if is_last else '')
            html_content += f"""
                    <tr style="{row_style}">
                        <td><strong>{global_idx}</strong> {marker}</td>
                        <td>{point_idx}</td>
                        <td><code>{point_str}</code></td>
                        <td>{x:.4f}</td>
                        <td>{y:.4f}</td>
                    </tr>
"""
            global_idx += 1
        
        html_content += """                </table>
            </div>
"""
    
    html_content += """
            <h3>All Points (for reference):</h3>
            <table>
                <tr>
                    <th>Index</th>
                    <th>Stroke</th>
                    <th>Coordinates</th>
                    <th>X</th>
                    <th>Y</th>
                </tr>
"""
    
    for point in points:
        html_content += f"""
                <tr>
                    <td>{point['global_idx']}</td>
                    <td>{point['stroke']}</td>
                    <td><code>{point['point_str']}</code></td>
                    <td>{point['x']:.4f}</td>
                    <td>{point['y']:.4f}</td>
                </tr>
"""
    
    html_content += """            </table>
        </div>
    </div>
    
    <script>
        // Add click handlers to show point details
        document.querySelectorAll('.point').forEach(point => {
            point.addEventListener('click', function() {
                const idx = this.getAttribute('data-index');
                const stroke = this.getAttribute('data-stroke');
                alert(`Point Index: ${idx}\\nStroke: ${stroke}\\nUse this index when creating stroke order.`);
            });
        });
    </script>
</body>
</html>
"""
    
    return html_content

def visualize_letter(letter_name, is_english=False):
    """Create visualization of letter with all points labeled."""
    # Load SVG path
    if is_english:
        svg_path = load_english_path(letter_name)
    else:
        svg_path = load_telugu_path(letter_name)
    
    if not svg_path:
        return
    
    # Load JSON points
    points_data = load_json_points(letter_name, is_english=is_english)
    if not points_data:
        return
    
    # Create HTML visualization
    html_content = create_html_visualization(letter_name, svg_path, points_data)
    
    # Save HTML file
    output_file = f'tools/{letter_name}_points_visualization.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Visualization created: {output_file}")
    print(f"  Open this file in your browser to see the letter with all points labeled")
    print(f"  Use the point indices to create your stroke order")
    
    # Print summary
    points, json_data = points_data
    print(f"\nSummary:")
    print(f"  Total points: {len(points)}")
    print(f"  Current strokes: {len(json_data.get('strokes', []))}")
    print(f"\nPoint indices range: 0 to {len(points) - 1}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print("  python3 tools/visualize_telugu_points.py a          # Telugu letter")
        print("  python3 tools/visualize_telugu_points.py A --english # English capital A")
        sys.exit(1)
    
    letter_name = sys.argv[1]
    is_english = '--english' in sys.argv or '-e' in sys.argv
    visualize_letter(letter_name, is_english=is_english)

if __name__ == '__main__':
    main()
