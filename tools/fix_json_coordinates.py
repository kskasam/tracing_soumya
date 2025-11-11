#!/usr/bin/env python3
"""
Fix JSON coordinates by normalizing them to 0-1 range.

This script takes a JSON file with potentially negative coordinates
and normalizes them to the 0-1 range.
"""

import json
import sys
import os

def normalize_coordinates(json_file):
    """Normalize all coordinates in JSON to 0-1 range."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all coordinates to find min/max
    all_x = []
    all_y = []
    
    for stroke in data.get('strokes', []):
        for point_str in stroke.get('points', []):
            x, y = map(float, point_str.split(','))
            all_x.append(x)
            all_y.append(y)
    
    if not all_x or not all_y:
        print("No points found in JSON")
        return False
    
    # Find min and max
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Calculate ranges
    range_x = max_x - min_x if max_x != min_x else 1
    range_y = max_y - min_y if max_y != min_y else 1
    
    print(f"Original range: X=[{min_x:.4f}, {max_x:.4f}], Y=[{min_y:.4f}, {max_y:.4f}]")
    
    # Normalize all points
    normalized_strokes = []
    for stroke in data.get('strokes', []):
        normalized_points = []
        for point_str in stroke.get('points', []):
            x, y = map(float, point_str.split(','))
            # Normalize to 0-1
            norm_x = (x - min_x) / range_x
            norm_y = (y - min_y) / range_y
            # Clamp to 0-1
            norm_x = max(0, min(1, norm_x))
            norm_y = max(0, min(1, norm_y))
            normalized_points.append(f"{norm_x:.4f},{norm_y:.4f}")
        normalized_strokes.append({"points": normalized_points})
    
    # Update data
    data['strokes'] = normalized_strokes
    
    # Save back
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Normalized range: X=[0.0000, 1.0000], Y=[0.0000, 1.0000]")
    print(f"✓ Fixed {json_file}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 tools/fix_json_coordinates.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        sys.exit(1)
    
    normalize_coordinates(json_file)

