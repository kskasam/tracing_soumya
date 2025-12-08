#!/usr/bin/env python3
"""
Normalize the extracted am and aha paths to fit properly in viewBox 0 0 1000 1000
with Y-axis flipped (fonts use Y-up, SVG uses Y-down)
"""

import re
import sys

def normalize_path_full(path_d, em=1000, padding=0.1):
    """
    Normalize SVG path coordinates to fit in viewBox with padding.
    Fonts use Y-up coordinates (Y increases upward), but SVG/Flutter use Y-down.
    So we first flip Y coordinates, then normalize.
    """
    # Step 1: Flip Y coordinates in original path
    commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])\s*([-\d.,\s]+)?', path_d)
    
    flipped_commands = []
    for cmd, args in commands:
        if not args or cmd.upper() == 'Z':
            flipped_commands.append((cmd, args))
            continue
        
        cmd_upper = cmd.upper()
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        flipped_nums = []
        
        if cmd_upper == 'H':
            # Horizontal line: only X coordinate, no Y to flip
            flipped_nums = nums
        elif cmd_upper == 'V':
            # Vertical line: only Y coordinate, flip it
            for num in nums:
                try:
                    val = float(num)
                    val = em - val  # Flip Y
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper == 'C':
            # Cubic bezier: (x1, y1, x2, y2, x, y) - 6 numbers
            # Flip y1, y2, and y (indices 1, 3, 5)
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i % 2 == 1:  # Y coordinates (odd indices)
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        elif cmd_upper in ['S', 'Q', 'T', 'M', 'L']:
            # All use (x, y) pairs
            for i, num in enumerate(nums):
                try:
                    val = float(num)
                    if i % 2 == 1:  # Y coordinate (odd index)
                        val = em - val
                    flipped_nums.append(f"{val:.2f}")
                except ValueError:
                    flipped_nums.append(num)
        else:
            flipped_nums = nums
        
        flipped_args = ' '.join(flipped_nums)
        flipped_commands.append((cmd, flipped_args))
    
    # Step 2: Extract coordinates from flipped path for bounding box
    coords = []
    for cmd, args in flipped_commands:
        if not args or cmd.upper() == 'Z':
            continue
        nums = re.findall(r'[-+]?\d*\.?\d+', args)
        for num in nums:
            try:
                coords.append(float(num))
            except ValueError:
                pass
    
    if not coords:
        return ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
    
    # Find bounding box of flipped path
    x_coords = [coords[i] for i in range(0, len(coords), 2) if i < len(coords)]
    y_coords = [coords[i+1] for i in range(0, len(coords), 2) if i+1 < len(coords)]
    
    if not x_coords or not y_coords:
        return ' '.join([f"{cmd} {args}" if args else cmd for cmd, args in flipped_commands])
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x if max_x != min_x else em
    height = max_y - min_y if max_y != min_y else em
    
    print(f"  Bounding box: ({min_x:.2f}, {min_y:.2f}) to ({max_x:.2f}, {max_y:.2f})")
    print(f"  Size: {width:.2f} x {height:.2f}")
    
    # Calculate scale and offset to fit in em x em with padding
    scale = min(em * (1 - 2*padding) / width, em * (1 - 2*padding) / height) if width > 0 and height > 0 else 1
    offset_x = em * padding - min_x * scale
    offset_y = em * padding - min_y * scale
    
    print(f"  Scale: {scale:.4f}, Offset: ({offset_x:.2f}, {offset_y:.2f})")
    
    # Step 3: Normalize the flipped path
    def transform_coord(coord_str, is_x):
        try:
            val = float(coord_str)
            if is_x:
                return val * scale + offset_x
            else:
                return val * scale + offset_y
        except ValueError:
            return coord_str
    
    transformed_commands = []
    
    for cmd, args in flipped_commands:
        if not args or cmd.upper() == 'Z':
            transformed_commands.append(cmd)
            continue
        
        cmd_upper = cmd.upper()
        nums = re.findall(r'([-+]?\d*\.?\d+)', args)
        transformed_nums = []
        
        if cmd_upper == 'H':
            # Horizontal line: only X coordinate
            for num in nums:
                transformed_val = transform_coord(num, True)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper == 'V':
            # Vertical line: only Y coordinate
            for num in nums:
                transformed_val = transform_coord(num, False)
                transformed_nums.append(f"{transformed_val:.2f}")
        elif cmd_upper in ['C', 'S', 'Q', 'T', 'M', 'L']:
            # (x, y) pairs - standard case
            for i, num in enumerate(nums):
                is_x = (i % 2 == 0)
                transformed_val = transform_coord(num, is_x)
                transformed_nums.append(f"{transformed_val:.2f}")
        else:
            transformed_nums = nums
        
        transformed_args = ' '.join(transformed_nums)
        transformed_commands.append(f"{cmd} {transformed_args}")
    
    return ' '.join(transformed_commands)


def process_file(input_file, output_svg, output_txt):
    """Process a path file and generate normalized outputs."""
    print(f"\nProcessing {input_file}...")
    
    with open(input_file, 'r') as f:
        path_d = f.read().strip()
    
    print(f"  Original path length: {len(path_d)} chars")
    
    # Normalize the path
    normalized = normalize_path_full(path_d, em=1000, padding=0.1)
    
    print(f"  Normalized path length: {len(normalized)} chars")
    
    # Save SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <path d="{normalized}" fill="black" stroke="none"/>
</svg>'''
    
    with open(output_svg, 'w') as f:
        f.write(svg_content)
    print(f"  ✓ Saved: {output_svg}")
    
    # Save path text
    with open(output_txt, 'w') as f:
        f.write(normalized)
    print(f"  ✓ Saved: {output_txt}")


def main():
    output_dir = "tools/svg_generator/output"
    
    # Process am
    process_file(
        f"{output_dir}/am_path.txt",
        f"{output_dir}/am_extracted.svg",
        f"{output_dir}/am_path.txt"
    )
    
    # Process aha
    process_file(
        f"{output_dir}/aha_path.txt",
        f"{output_dir}/aha_extracted.svg",
        f"{output_dir}/aha_path.txt"
    )
    
    print("\n✓ Successfully normalized both paths")


if __name__ == "__main__":
    main()

