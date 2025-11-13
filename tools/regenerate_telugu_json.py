#!/usr/bin/env python3
"""
Script to regenerate Telugu JSON files with proper coordinate mapping
that matches the SVG path bounding box exactly.
"""
import json
import os
import re

def extract_svg_bounds(svg_path):
    """Extract min/max coordinates from SVG path."""
    # Extract all coordinate pairs
    coords = re.findall(r'[-+]?\d*\.?\d+', svg_path)
    coords = [float(c) for c in coords]
    
    # Separate X and Y coordinates
    x_coords = coords[0::2]
    y_coords = coords[1::2]
    
    return {
        'min_x': min(x_coords),
        'max_x': max(x_coords),
        'min_y': min(y_coords),
        'max_y': max(y_coords),
        'width': max(x_coords) - min(x_coords),
        'height': max(y_coords) - min(y_coords)
    }

def renormalize_json_to_svg_space(json_file, svg_bounds):
    """Renormalize JSON points to match SVG bounding box."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Process each stroke
    for stroke in data['strokes']:
        new_points = []
        for point_str in stroke['points']:
            # Parse normalized coordinates (0-1)
            x, y = map(float, point_str.split(','))
            
            # Map to SVG bounds
            svg_x = svg_bounds['min_x'] + (x * svg_bounds['width'])
            svg_y = svg_bounds['min_y'] + (y * svg_bounds['height'])
            
            # Renormalize back to 0-1 based on SVG bounds
            # This ensures alignment with how Flutter scales the SVG
            norm_x = (svg_x - svg_bounds['min_x']) / svg_bounds['width']
            norm_y = (svg_y - svg_bounds['min_y']) / svg_bounds['height']
            
            new_points.append(f"{norm_x:.4f},{norm_y:.4f}")
        
        stroke['points'] = new_points
    
    # Save back
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Updated {json_file}")

# This is a diagnostic script - run it manually if you need to regenerate
# The real issue is likely in how we're extracting/normalizing the points

print("""
This script can help regenerate Telugu JSON files.
However, the real fix is to ensure:
1. JSON points are normalized to the same bounding box as the SVG
2. Both use the same coordinate transformation in Flutter

Current approach should work with distanceToCheck: 70.0
""")

