#!/usr/bin/env python3
"""
Helper script to manually split strokes in Telugu JSON files for better direction indicators.

Usage:
    python3 tools/manually_split_strokes.py <json_file> <split_indices>
    
Example:
    python3 tools/manually_split_strokes.py lib/assets/phontics_assets_points/telugu_phontics/a_big_PointsInfo.json 10 20
    
This will split the first stroke at indices 10 and 20, creating 3 strokes total.
"""

import json
import sys
import os

def split_stroke(json_file, split_indices):
    """Split a stroke in a JSON file at specified indices."""
    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        return False
    
    # Read the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data.get('strokes') or len(data['strokes']) == 0:
        print(f"Error: No strokes found in {json_file}")
        return False
    
    # Get the first stroke (usually the main one)
    first_stroke = data['strokes'][0]['points']
    
    if not first_stroke:
        print(f"Error: First stroke is empty")
        return False
    
    # Sort split indices and validate
    split_indices = sorted([int(idx) for idx in split_indices])
    split_indices = [idx for idx in split_indices if 0 < idx < len(first_stroke)]
    
    if not split_indices:
        print(f"Error: No valid split indices. Stroke has {len(first_stroke)} points.")
        return False
    
    # Create new strokes
    new_strokes = []
    start_idx = 0
    
    for split_idx in split_indices:
        # Extract points from start to split
        new_stroke_points = first_stroke[start_idx:split_idx + 1]  # Include split point
        if new_stroke_points:
            new_strokes.append({"points": new_stroke_points})
        start_idx = split_idx
    
    # Add the remaining points
    if start_idx < len(first_stroke):
        remaining_points = first_stroke[start_idx:]
        if remaining_points:
            new_strokes.append({"points": remaining_points})
    
    # Add any existing additional strokes (keep them)
    if len(data['strokes']) > 1:
        new_strokes.extend(data['strokes'][1:])
    
    # Update the data
    data['strokes'] = new_strokes
    
    # Write back
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Split {json_file} into {len(new_strokes)} strokes")
    print(f"  Split at indices: {split_indices}")
    return True

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nExample:")
        print("  python3 tools/manually_split_strokes.py lib/assets/phontics_assets_points/telugu_phontics/a_big_PointsInfo.json 10 20")
        sys.exit(1)
    
    json_file = sys.argv[1]
    split_indices = sys.argv[2:]
    
    split_stroke(json_file, split_indices)

if __name__ == '__main__':
    main()

