#!/usr/bin/env python3
"""
Process arrow and number placement JSON from HTML editor
and match them to SVG paths for use in Flutter app.
"""

import json
import sys
import os
from pathlib import Path
from xml.etree import ElementTree as ET
import re

def parse_svg_path(svg_file):
    """Parse SVG file and extract path data."""
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
        
        # Find all path elements
        paths = []
        for path_elem in root.findall('.//{http://www.w3.org/2000/svg}path'):
            path_data = path_elem.get('d', '')
            if path_data:
                paths.append(path_data)
        
        # If no paths found, try without namespace
        if not paths:
            for path_elem in root.findall('.//path'):
                path_data = path_elem.get('d', '')
                if path_data:
                    paths.append(path_data)
        
        # Get viewBox or dimensions
        viewbox = root.get('viewBox', '')
        if not viewbox:
            width = root.get('width', '200')
            height = root.get('height', '200')
            viewbox = f"0 0 {width} {height}"
        
        return {
            'paths': paths,
            'viewBox': viewbox,
            'root': root
        }
    except Exception as e:
        print(f"Error parsing SVG: {e}")
        return None

def normalize_coordinates(x, y, svg_viewbox, target_size=(200, 200)):
    """Normalize coordinates from SVG viewBox to target size (0-1 range)."""
    viewbox_parts = svg_viewbox.split()
    if len(viewbox_parts) == 4:
        vb_x, vb_y, vb_width, vb_height = map(float, viewbox_parts)
    else:
        vb_x, vb_y = 0, 0
        vb_width, vb_height = 200, 200
    
    # Normalize to 0-1 range
    norm_x = (x - vb_x) / vb_width
    norm_y = (y - vb_y) / vb_height
    
    # Scale to target size
    target_x = norm_x * target_size[0]
    target_y = norm_y * target_size[1]
    
    return target_x, target_y, norm_x, norm_y

def find_nearest_path_point(x, y, path_data, svg_viewbox):
    """Find the nearest point on the SVG path to the given coordinates."""
    # This is a simplified version - in practice, you'd need to:
    # 1. Parse the path data
    # 2. Sample points along the path
    # 3. Find the closest point
    
    # For now, return the input coordinates (you can enhance this)
    return x, y

def process_placement_json(json_file, svg_file, output_file=None):
    """Process the arrow/number placement JSON and generate Flutter-compatible data."""
    
    # Load placement JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        placement_data = json.load(f)
    
    # Parse SVG
    svg_data = parse_svg_path(svg_file)
    if not svg_data:
        print("Failed to parse SVG file")
        return None
    
    # Group items by stroke number (for numbers) and type
    arrows = []
    lines = []
    numbers_by_stroke = {}
    
    for item in placement_data.get('items', []):
        x, y = item['x'], item['y']
        
        # Normalize coordinates
        target_x, target_y, norm_x, norm_y = normalize_coordinates(
            x, y, 
            placement_data.get('svgViewBox', {}).get('viewBox', '0 0 200 200') or '0 0 200 200',
            target_size=(200, 200)
        )
        
        if item['type'] == 'arrow':
            arrows.append({
                'x': target_x,
                'y': target_y,
                'normalized_x': norm_x,
                'normalized_y': norm_y,
                'original_x': x,
                'original_y': y,
                'angle': item.get('angle', 0),
                'arrowType': item.get('arrowType', 'triangle')
            })
        elif item['type'] == 'line':
            x1, y1 = item['x1'], item['y1']
            target_x1, target_y1, norm_x1, norm_y1 = normalize_coordinates(
                x1, y1,
                placement_data.get('svgViewBox', {}).get('viewBox', '0 0 200 200') or '0 0 200 200',
                target_size=(200, 200)
            )
            lines.append({
                'x1': target_x1,
                'y1': target_y1,
                'x2': target_x,
                'y2': target_y,
                'normalized_x1': norm_x1,
                'normalized_y1': norm_y1,
                'normalized_x2': norm_x,
                'normalized_y2': norm_y,
                'original_x1': x1,
                'original_y1': y1,
                'original_x2': x,
                'original_y2': y,
                'angle': item.get('angle', 0),
                'arrowType': item.get('arrowType', 'triangle')
            })
        elif item['type'] == 'number':
            stroke_num = item.get('strokeNumber', 1)
            if stroke_num not in numbers_by_stroke:
                numbers_by_stroke[stroke_num] = []
            
            numbers_by_stroke[stroke_num].append({
                'x': target_x,
                'y': target_y,
                'normalized_x': norm_x,
                'normalized_y': norm_y,
                'original_x': x,
                'original_y': y,
                'strokeNumber': stroke_num
            })
    
    # Generate output structure
    output = {
        'arrows': arrows,
        'numbers': numbers_by_stroke,
        'lines': lines,
        'metadata': {
            'svg_file': str(svg_file),
            'placement_file': str(json_file),
            'total_arrows': len(arrows),
            'total_lines': len(lines),
            'total_numbers': sum(len(nums) for nums in numbers_by_stroke.values()),
            'strokes_with_numbers': list(numbers_by_stroke.keys())
        }
    }
    
    # Write output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"Output written to: {output_file}")
    else:
        # Print to stdout
        print(json.dumps(output, indent=2))
    
    return output

def generate_dart_code(output_data, letter_name):
    """Generate Dart code for use in Flutter app."""
    
    dart_code = f"""
// Auto-generated arrow and number positions for {letter_name}
// DO NOT EDIT - Generated from arrow_number_editor

class {letter_name.capitalize()}ArrowNumbers {{
  // Arrow positions (normalized coordinates 0-1)
  static final List<Map<String, double>> arrows = [
"""
    
    for arrow in output_data['arrows']:
        arrow_type = arrow.get('arrowType', 'triangle')
        angle = arrow.get('angle', 0)
        dart_code += f"    {{'x': {arrow['normalized_x']:.4f}, 'y': {arrow['normalized_y']:.4f}, 'angle': {angle:.4f}, 'type': '{arrow_type}'}},\n"
    
    dart_code += "  ];\n\n"
    dart_code += "  // Number positions by stroke (normalized coordinates 0-1)\n"
    dart_code += "  static final Map<int, List<Map<String, double>>> numbers = {\n"
    
    for stroke_num in sorted(output_data['numbers'].keys()):
        dart_code += f"    {stroke_num}: [\n"
        for num_pos in output_data['numbers'][stroke_num]:
            dart_code += f"      {{'x': {num_pos['normalized_x']:.4f}, 'y': {num_pos['normalized_y']:.4f}}},\n"
        dart_code += "    ],\n"
    
    dart_code += "  };\n"
    dart_code += "\n"
    dart_code += "  // Lines with arrow (normalized coordinates 0-1)\n"
    dart_code += "  static final List<Map<String, double>> lines = [\n"
    for line in output_data.get('lines', []):
        arrow_type = line.get('arrowType', 'triangle')
        angle = line.get('angle', 0)
        dart_code += (
            f"    {{'x1': {line['normalized_x1']:.4f}, 'y1': {line['normalized_y1']:.4f}, "
            f"'x2': {line['normalized_x2']:.4f}, 'y2': {line['normalized_y2']:.4f}, "
            f"'angle': {angle:.4f}, 'type': '{arrow_type}'}},\n"
        )
    dart_code += "  ];\n"
    dart_code += "}\n"
    
    return dart_code

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_arrow_numbers.py <placement_json> <svg_file> [output_json] [output_dart] [letter_name]")
        print("\nExample:")
        print("  python process_arrow_numbers.py placement.json letter.svg output.json output.dart ka")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    svg_file = Path(sys.argv[2])
    output_json = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    output_dart = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    letter_name = sys.argv[5] if len(sys.argv) > 5 else 'letter'
    
    if not json_file.exists():
        print(f"Error: Placement JSON file not found: {json_file}")
        sys.exit(1)
    
    if not svg_file.exists():
        print(f"Error: SVG file not found: {svg_file}")
        sys.exit(1)
    
    # Process the data
    output_data = process_placement_json(json_file, svg_file, output_json)
    
    if output_data and output_dart:
        dart_code = generate_dart_code(output_data, letter_name)
        with open(output_dart, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        print(f"Dart code written to: {output_dart}")
    
    print("\nProcessing complete!")

if __name__ == '__main__':
    main()

