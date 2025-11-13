#!/usr/bin/env python3
"""
Generate dotted direction paths for Telugu letters from JSON points.
This creates simplified SVG paths showing the tracing direction with arrows.
"""

import json
import os
from pathlib import Path

def json_to_dotted_svg(json_file_path, svg_bounds):
    """Convert JSON points to a simple dotted SVG path for direction indicators."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    if 'strokes' not in data or not data['strokes']:
        return "M 0 0"  # Empty path
    
    # Get bounding box for denormalization
    x_min, y_min = svg_bounds['x'], svg_bounds['y']
    width, height = svg_bounds['width'], svg_bounds['height']
    
    path_commands = []
    
    for stroke_idx, stroke in enumerate(data['strokes']):
        if 'points' not in stroke or not stroke['points']:
            continue
        
        points = []
        for point_str in stroke['points']:
            norm_x, norm_y = map(float, point_str.split(','))
            # Denormalize: convert 0-1 back to SVG coordinates
            svg_x = norm_x * width + x_min
            svg_y = norm_y * height + y_min
            points.append((svg_x, svg_y))
        
        if not points:
            continue
        
        # Create a simplified path - just connect the points with lines
        # Use every Nth point to make it less dense
        step = max(1, len(points) // 15)  # Max 15 points per stroke
        simplified_points = points[::step]
        if points[-1] not in simplified_points:
            simplified_points.append(points[-1])  # Always include last point
        
        # Build path
        for i, (x, y) in enumerate(simplified_points):
            if i == 0:
                path_commands.append(f'M {x:.2f} {y:.2f}')
            else:
                path_commands.append(f'L {x:.2f} {y:.2f}')
    
    return ' '.join(path_commands) if path_commands else "M 0 0"


def main():
    workspace = Path(__file__).parent.parent
    json_dir = workspace / 'lib' / 'assets' / 'phontics_assets_points' / 'telugu_phontics'
    telugu_paths_file = workspace / 'lib' / 'src' / 'phontics_constants' / 'telugu_shape_paths.dart'
    
    # Telugu letter bounding boxes (all use same bounds from the TTF font)
    svg_bounds = {
        'x': 100,
        'y': 302.05,
        'width': 747.69,
        'height': 525.13
    }
    
    # Read existing file to get letter names
    with open(telugu_paths_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Telugu letters mapping (from your previous script)
    telugu_letters = {
        'a': 'అ', 'aa': 'ఆ', 'ai': 'ఐ', 'au': 'ఔ', 'e': 'ఎ', 'ee': 'ఏ',
        'i': 'ఇ', 'ii': 'ఈ', 'o': 'ఒ', 'oo': 'ఓ', 'u': 'ఉ', 'uu': 'ఊ',
        'ru': 'ఋ', 'ka': 'క', 'kha': 'ఖ', 'ga': 'గ', 'gha': 'ఘ', 'nga': 'ఙ',
        'cha': 'చ', 'chha': 'ఛ', 'ja': 'జ', 'jha': 'ఝ', 'nya': 'ఞ',
        'ta': 'ట', 'tha': 'ఠ', 'da': 'డ', 'dha': 'ఢ', 'na': 'ణ',
        'tha2': 'థ', 'ta2': 'త', 'da2': 'ద', 'dha2': 'ధ', 'na2': 'న',
        'pa': 'ప', 'pha': 'ఫ', 'ba': 'బ', 'bha': 'భ', 'ma': 'మ',
        'ya': 'య', 'ra': 'ర', 'la': 'ల', 'va': 'వ',
        'sha': 'శ', 'shha': 'ష', 'sa': 'స', 'ha': 'హ', 'lla': 'ళ', 'rra': 'ఱ'
    }
    
    print("Generating dotted paths for Telugu letters...")
    
    updated_lines = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        updated_lines.append(line)
        
        # Check if this is a dotted path definition that needs updating
        for name, char in telugu_letters.items():
            dotted_const_name = f"static const {name}Dotted ="
            if dotted_const_name in line:
                # Find the JSON file
                json_file = json_dir / f'{name}_big_PointsInfo.json'
                
                if json_file.exists():
                    print(f"  Processing {char} ({name})...")
                    
                    # Generate dotted path
                    dotted_path = json_to_dotted_svg(json_file, svg_bounds)
                    
                    # Replace the path (skip current line content until the closing ''';)
                    updated_lines[-1] = f"  {dotted_const_name} '''{dotted_path}''';"
                    
                    # Skip old path lines until we find the closing ''';
                    i += 1
                    while i < len(lines) and "''';" not in lines[i]:
                        i += 1
                    # Don't add the old closing line, we already added it above
                else:
                    print(f"  Warning: JSON file not found for {name}")
                break
        
        i += 1
    
    # Write updated content
    with open(telugu_paths_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"\n✅ Updated {telugu_paths_file}")
    print("Dotted paths have been generated from JSON points!")
    print("\nNow run 'flutter pub get' and restart your app to see the direction indicators.")


if __name__ == '__main__':
    main()

