#!/usr/bin/env python3
"""
Script to generate Hindi files similar to Telugu structure
"""
import os
import json
import re

# Read all path files
out_dir = 'tools/svg_generator/out_hin'
letters = {}
for f in sorted(os.listdir(out_dir)):
    if f.endswith('_path.txt'):
        letter = f.replace('_path.txt', '')
        with open(os.path.join(out_dir, f), 'r') as file:
            path = file.read().strip()
            letters[letter] = path

print(f"Found {len(letters)} Hindi letters")

# Convert letter name to camelCase
def to_camel_case(snake_str):
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

# Generate hindi_shape_paths.dart
dart_lines = ['class HindiShapePaths {']
for letter in sorted(letters.keys()):
    path = letters[letter]
    # Escape single quotes in path
    path_escaped = path.replace("'", "\\'")
    
    # Convert to camelCase
    camel_name = to_camel_case(letter)
    
    dart_lines.append(f'  // {letter}')
    dart_lines.append(f"  static const {camel_name}Big = '''{path_escaped}''';")
    dart_lines.append('')
    dart_lines.append(f"  static const {camel_name}Small = '''{path_escaped}''';")
    dart_lines.append('')
    dart_lines.append(f'  // Dotted path for {letter} (will be generated from JSON points)')
    dart_lines.append(f"  static const {camel_name}Dotted = '''''';")
    dart_lines.append('')

dart_lines.append('}')

dart_content = '\n'.join(dart_lines)
print(f"Generated Dart file with {len(dart_lines)} lines")

# Write to file
with open('lib/src/phontics_constants/hindi_shape_paths.dart', 'w', encoding='utf-8') as f:
    f.write(dart_content)
print("Created lib/src/phontics_constants/hindi_shape_paths.dart")

