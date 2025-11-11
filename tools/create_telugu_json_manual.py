#!/usr/bin/env python3
"""
Helper script to manually create Telugu letter JSON files.

This script helps you create a JSON file by:
1. Loading all points from the existing auto-generated JSON
2. Allowing you to specify which points belong to which stroke
3. Generating the final JSON with your custom stroke order

Usage:
    python3 tools/create_telugu_json_manual.py <letter_name>
    
Example:
    python3 tools/create_telugu_json_manual.py a
    
This will:
- Load points from a_big_PointsInfo.json
- Show you all available points with their indices
- Let you specify stroke boundaries
- Generate a new JSON file
"""

import json
import sys
import os

def load_existing_points(json_file):
    """Load all points from existing JSON file."""
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return None
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_points = []
    for stroke_idx, stroke in enumerate(data.get('strokes', [])):
        for point_str in stroke.get('points', []):
            x, y = map(float, point_str.split(','))
            all_points.append({
                'x': x,
                'y': y,
                'point_str': point_str,
                'global_idx': len(all_points)
            })
    
    return all_points, data

def print_points_table(points):
    """Print a table of all available points."""
    print("\n" + "="*80)
    print("ALL AVAILABLE POINTS (use these indices to create your strokes)")
    print("="*80)
    print(f"{'Index':<8} {'X':<12} {'Y':<12} {'Coordinates':<20}")
    print("-"*80)
    
    for i, point in enumerate(points):
        print(f"{i:<8} {point['x']:<12.4f} {point['y']:<12.4f} {point['point_str']:<20}")
    
    print("="*80)
    print(f"\nTotal points: {len(points)}")
    print("\nTo create strokes, specify ranges like: 0-8,9-22,23-39")
    print("(This means: stroke 1 = points 0-8, stroke 2 = points 9-22, stroke 3 = points 23-39)")

def parse_stroke_ranges(ranges_str, total_points):
    """Parse stroke ranges from user input.
    
    Examples:
        "0-8,9-22,23-39" -> [[0,1,2,...,8], [9,10,...,22], [23,24,...,39]]
        "0-5,6-10" -> [[0,1,2,3,4,5], [6,7,8,9,10]]
    """
    strokes = []
    ranges = ranges_str.split(',')
    
    for range_str in ranges:
        range_str = range_str.strip()
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            stroke_indices = list(range(start, end + 1))
        else:
            # Single index
            stroke_indices = [int(range_str)]
        
        # Validate indices
        for idx in stroke_indices:
            if idx < 0 or idx >= total_points:
                print(f"Error: Index {idx} is out of range (0-{total_points-1})")
                return None
        
        strokes.append(stroke_indices)
    
    return strokes

def create_json_from_strokes(points, stroke_indices_list):
    """Create JSON structure from points and stroke indices."""
    strokes = []
    
    for stroke_indices in stroke_indices_list:
        stroke_points = []
        for idx in stroke_indices:
            if idx < len(points):
                stroke_points.append(points[idx]['point_str'])
        strokes.append({"points": stroke_points})
    
    return {"strokes": strokes}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    letter_name = sys.argv[1]
    json_file = f"lib/assets/phontics_assets_points/telugu_phontics/{letter_name}_big_PointsInfo.json"
    
    # Load existing points
    result = load_existing_points(json_file)
    if not result:
        sys.exit(1)
    
    points, original_data = result
    
    # Print all available points
    print_points_table(points)
    
    # Get stroke ranges from user
    print("\n" + "="*80)
    print("STEP 1: Define your stroke ranges")
    print("="*80)
    print("\nEnter stroke ranges (comma-separated):")
    print("Example: 0-8,9-22,23-39")
    print("Or: 0-5,6-10,11-15")
    print("\nYou can also specify individual points: 0,1,2,3-5,6,7")
    print("\nInput: ", end='')
    
    ranges_str = input().strip()
    
    if not ranges_str:
        print("Error: No ranges specified")
        sys.exit(1)
    
    # Parse stroke ranges
    stroke_indices_list = parse_stroke_ranges(ranges_str, len(points))
    if not stroke_indices_list:
        sys.exit(1)
    
    # Show what will be created
    print("\n" + "="*80)
    print("STEP 2: Review your stroke structure")
    print("="*80)
    for stroke_idx, stroke_indices in enumerate(stroke_indices_list):
        print(f"\nStroke {stroke_idx + 1}: {len(stroke_indices)} points")
        print(f"  Indices: {stroke_indices[0]} to {stroke_indices[-1]}")
        print(f"  First point: {points[stroke_indices[0]]['point_str']}")
        print(f"  Last point: {points[stroke_indices[-1]]['point_str']}")
    
    # Ask for confirmation
    print("\n" + "="*80)
    print("STEP 3: Confirm and save")
    print("="*80)
    print("\nCreate JSON file? (y/n): ", end='')
    confirm = input().strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Create JSON
    new_json = create_json_from_strokes(points, stroke_indices_list)
    
    # Save to file
    output_file = json_file  # Overwrite original, or you can change this
    print(f"\nSaving to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_json, f, indent=2, ensure_ascii=False)
    
    print("✓ JSON file created successfully!")
    print(f"\nYou can now visualize it with:")
    print(f"  python3 tools/visualize_telugu_points.py {letter_name}")

if __name__ == '__main__':
    main()

