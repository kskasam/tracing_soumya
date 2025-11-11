#!/usr/bin/env python3
"""
generate_telugu_svg.py - Generates SVG for Telugu letter అ
"""

# SVG path data for Telugu letter అ
TELUGU_A_PATH = """M 400 300
C 450 300 500 325 525 375
  550 425 550 500 525 575
  500 650 450 700 375 725
  300 750 225 750 175 700
  125 650 125 575 175 525
  225 475 300 450 375 475
  450 500 500 550 525 625
  550 700 575 750 625 775
  675 800 725 775 750 725
  775 675 775 600 750 525
  725 450 675 400 600 375
  525 350 450 350 400 375
  350 400 325 450 350 500
  375 550 425 575 475 575
  525 575 575 550 600 500 Z"""

def generate_svg(path_data, size=1000):
    """Generate SVG with the given path data."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <path d="{path_data}" fill="black"/>
</svg>'''
    return svg

def main():
    # Generate SVG
    svg = generate_svg(TELUGU_A_PATH)
    
    # Write to file
    with open("a_extracted.svg", "w") as f:
        f.write(svg)
    print("Generated a_extracted.svg")
    
    # Also print the path data
    print("\nPath data (d attribute):\n")
    print(TELUGU_A_PATH)

if __name__ == "__main__":
    main()