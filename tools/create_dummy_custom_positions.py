#!/usr/bin/env python3
"""Script to create dummy custom_positions.json files for all Telugu letters"""

import json
import os
from pathlib import Path

# Template for dummy JSON
DUMMY_TEMPLATE = {
    "svgViewBox": {
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 200
    },
    "svgBounds": {
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 200
    },
    "svgPath": "",
    "centerlinePath": "",
    "items": [],
    "exportDate": "2025-01-01T00:00:00.000Z"
}

# All Telugu letters mapping: (unicode_char, file_name)
TELUGU_LETTERS = [
    # Vowels
    ('అ', 'a'),
    ('ఆ', 'aa'),
    ('ఇ', 'i'),
    ('ఈ', 'ii'),
    ('ఉ', 'u'),
    ('ఊ', 'uu'),
    ('ఎ', 'e'),
    ('ఏ', 'ee'),
    ('ఐ', 'ai'),
    ('ఒ', 'o'),
    ('ఓ', 'oo'),
    ('ఔ', 'au'),
    ('ఋ', 'ru'),
    ('ౠ', 'ruu'),
    ('అం', 'am'),
    ('అః', 'aha'),
    # Consonants
    ('క', 'ka'),
    ('ఖ', 'kha'),
    ('గ', 'ga'),
    ('ఘ', 'gha'),
    ('చ', 'cha'),
    ('ఛ', 'chha'),
    ('జ', 'ja'),
    ('ఝ', 'jha'),
    ('ట', 'ta'),
    ('ఠ', 'tha'),
    ('డ', 'da'),
    ('ఢ', 'dha'),
    ('ణ', 'na'),
    ('త', 'ta2'),
    ('థ', 'tha2'),
    ('ద', 'da2'),
    ('ధ', 'dha2'),
    ('న', 'na2'),
    ('ప', 'pa'),
    ('ఫ', 'pha'),
    ('బ', 'ba'),
    ('భ', 'bha'),
    ('మ', 'ma'),
    ('య', 'ya'),
    ('ర', 'ra'),
    ('ల', 'la'),
    ('ళ', 'lla'),
    ('వ', 'va'),
    ('శ', 'sha'),
    ('ష', 'ssa'),
    ('స', 'sa'),
    ('హ', 'ha'),
]

def create_dummy_files():
    """Create dummy JSON files in both lib and assets paths"""
    base_dir = Path(__file__).parent.parent
    
    # Paths to create files in
    lib_path = base_dir / 'lib' / 'assets' / 'phontics_assets_points' / 'telugu_phontics'
    assets_path = base_dir / 'assets' / 'phontics_assets_points' / 'telugu_phontics'
    
    # Create directories if they don't exist
    lib_path.mkdir(parents=True, exist_ok=True)
    assets_path.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    for unicode_char, file_name in TELUGU_LETTERS:
        filename = f"{file_name}_custom_positions.json"
        
        # Create in lib path
        lib_file = lib_path / filename
        with open(lib_file, 'w', encoding='utf-8') as f:
            json.dump(DUMMY_TEMPLATE, f, indent=2, ensure_ascii=False)
        created_files.append(str(lib_file))
        print(f"Created: {lib_file}")
        
        # Create in assets path
        assets_file = assets_path / filename
        with open(assets_file, 'w', encoding='utf-8') as f:
            json.dump(DUMMY_TEMPLATE, f, indent=2, ensure_ascii=False)
        created_files.append(str(assets_file))
        print(f"Created: {assets_file}")
    
    print(f"\n✅ Created {len(created_files)} dummy JSON files")
    return TELUGU_LETTERS

if __name__ == '__main__':
    letters = create_dummy_files()
    print(f"\n📝 Letters processed: {len(letters)}")

