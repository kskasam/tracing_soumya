#!/usr/bin/env python3
"""Script to update Dart file to include customPositionsJsonFile for all letters"""

import re

# Mapping of letter cases to file names
LETTER_MAPPING = {
    "'అ'": 'a',
    "'ఆ'": 'aa',
    "'ఇ'": 'i',
    "'ఈ'": 'ii',
    "'ఉ'": 'u',
    "'ఊ'": 'uu',
    "'ఎ'": 'e',
    "'ఏ'": 'ee',
    "'ఐ'": 'ai',
    "'ఒ'": 'o',
    "'ఓ'": 'oo',
    "'ఔ'": 'au',
    "'ఋ'": 'ru',
    "'ౠ'": 'ruu',
    "'అం'": 'am',
    "'అః'": 'aha',
    "'క'": 'ka',
    "'ఖ'": 'kha',
    "'గ'": 'ga',
    "'ఘ'": 'gha',
    "'చ'": 'cha',
    "'ఛ'": 'chha',
    "'జ'": 'ja',
    "'ఝ'": 'jha',
    "'ట'": 'ta',
    "'ఠ'": 'tha',
    "'డ'": 'da',
    "'ఢ'": 'dha',
    "'ణ'": 'na',
    "'త'": 'ta2',
    "'థ'": 'tha2',
    "'ద'": 'da2',
    "'ధ'": 'dha2',
    "'న'": 'na2',
    "'ప'": 'pa',
    "'ఫ'": 'pha',
    "'బ'": 'ba',
    "'భ'": 'bha',
    "'మ'": 'ma',
    "'య'": 'ya',
    "'ర'": 'ra',
    "'ల'": 'la',
    "'ళ'": 'lla',
    "'వ'": 'va',
    "'శ'": 'sha',
    "'ష'": 'ssa',
    "'స'": 'sa',
    "'హ'": 'ha',
}

def update_dart_file():
    """Update the Dart file to add customPositionsJsonFile to all cases"""
    file_path = 'lib/src/get_shape_helper/enum_of_arabic_and_numbers_letters.dart'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match a case block that doesn't have customPositionsJsonFile yet
    # We'll look for the pattern: isBig: true,\n        ));
    pattern = r"(case\s+('అ'|'ఆ'|'ఇ'|'ఈ'|'ఉ'|'ఊ'|'ఎ'|'ఏ'|'ఐ'|'ఒ'|'ఓ'|'ఔ'|'ఋ'|'ౠ'|'అం'|'అః'|'క'|'ఖ'|'గ'|'ఘ'|'చ'|'ఛ'|'జ'|'ఝ'|'ట'|'ఠ'|'డ'|'ఢ'|'ణ'|'త'|'థ'|'ద'|'ధ'|'న'|'ప'|'ఫ'|'బ'|'భ'|'మ'|'య'|'ర'|'ల'|'ళ'|'వ'|'శ'|'ష'|'స'|'హ'):[^)]+isBig:\s+true,\s*)(\)\);)"
    
    def replace_func(match):
        case_line = match.group(1)
        closing = match.group(2)
        
        # Extract the letter from the case statement
        case_match = re.search(r"case\s+('.*?'):", case_line)
        if case_match:
            letter = case_match.group(1)
            file_name = LETTER_MAPPING.get(letter)
            if file_name:
                # Check if customPositionsJsonFile is already there
                if 'customPositionsJsonFile' not in case_line:
                    # Add the customPositionsJsonFile line before the closing
                    return f"{case_line}          customPositionsJsonFile: _getCustomPositionsPath('{file_name}'),\n        {closing}"
        
        return match.group(0)
    
    # Replace all matching cases
    new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # Special case for 'au' which already has customPositionsJsonFile - update it
    new_content = re.sub(
        r"customPositionsJsonFile:\s*'assets/phontics_assets_points/telugu_phontics/au_custom_positions\.json',",
        "customPositionsJsonFile: _getCustomPositionsPath('au'),",
        new_content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated {file_path}")

if __name__ == '__main__':
    update_dart_file()

