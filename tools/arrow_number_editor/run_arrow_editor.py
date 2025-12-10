#!/usr/bin/env python3
"""
Runner script to open the arrow/number placement editor in a browser.
"""

import webbrowser
import os
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    html_file = script_dir / 'arrow_number_editor.html'
    
    if not html_file.exists():
        print(f"Error: HTML file not found at {html_file}")
        return
    
    # Convert to file:// URL
    html_path = html_file.absolute()
    file_url = f"file://{html_path}"
    
    print(f"Opening arrow/number editor...")
    print(f"File: {html_path}")
    print("\nInstructions:")
    print("1. Load an SVG file")
    print("2. Click to place arrows and numbers")
    print("3. Export JSON when done")
    print("4. Run: python process_arrow_numbers.py <json> <svg> [output]")
    
    # Open in default browser
    webbrowser.open(file_url)

if __name__ == '__main__':
    main()

