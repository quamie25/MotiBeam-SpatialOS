#!/usr/bin/env python3
"""
Enhance all realm visuals with futuristic theme
"""

# Enhanced font sizes (much larger for projector readability)
FONT_CONFIG = """
        try:
            title_font = pygame.font.Font(None, 110)      # Was 84
            subtitle_font = pygame.font.Font(None, 58)    # Was 48
            section_font = pygame.font.Font(None, 46)     # Was 36
            item_font = pygame.font.Font(None, 38)        # Was 28
        except:
            title_font = pygame.font.SysFont('arial', 110, bold=True)
            subtitle_font = pygame.font.SysFont('arial', 58)
            section_font = pygame.font.SysFont('arial', 46, bold=True)
            item_font = pygame.font.SysFont('arial', 38)
"""

# Futuristic color schemes for each realm
COLOR_SCHEMES = {
    'home_realm.py': {
        'bg': '(8, 12, 20)',
        'accent': '(0, 220, 255)',      # Cyan
        'highlight': '(100, 255, 200)',  # Mint
        'glow': '(0, 180, 255)'
    },
    'clinical_realm.py': {
        'bg': '(12, 8, 20)',
        'accent': '(0, 255, 180)',      # Teal
        'highlight': '(100, 255, 220)',
        'glow': '(0, 220, 180)'
    },
    'education_realm.py': {
        'bg': '(15, 10, 25)',
        'accent': '(150, 100, 255)',    # Purple
        'highlight': '(200, 150, 255)',
        'glow': '(130, 80, 255)'
    },
    'transport_realm.py': {
        'bg': '(5, 15, 25)',
        'accent': '(0, 240, 200)',      # Aqua
        'highlight': '(100, 255, 230)',
        'glow': '(0, 200, 180)'
    },
    'emergency_realm.py': {
        'bg': '(25, 5, 5)',
        'accent': '(255, 50, 80)',      # Red
        'highlight': '(255, 100, 120)',
        'glow': '(255, 30, 60)'
    },
    'security_realm.py': {
        'bg': '(8, 15, 25)',
        'accent': '(0, 200, 255)',      # Blue
        'highlight': '(100, 220, 255)',
        'glow': '(0, 160, 255)'
    },
    'enterprise_realm.py': {
        'bg': '(10, 15, 22)',
        'accent': '(100, 200, 255)',    # Sky blue
        'highlight': '(150, 220, 255)',
        'glow': '(80, 180, 255)'
    },
    'aviation_realm.py': {
        'bg': '(5, 10, 20)',
        'accent': '(0, 180, 255)',      # Aviation blue
        'highlight': '(100, 200, 255)',
        'glow': '(0, 150, 255)'
    },
    'maritime_realm.py': {
        'bg': '(5, 15, 20)',
        'accent': '(0, 200, 220)',      # Ocean
        'highlight': '(100, 230, 240)',
        'glow': '(0, 180, 200)'
    }
}

import re

for filename, colors in COLOR_SCHEMES.items():
    filepath = f'scenes/{filename}'
    print(f"Enhancing {filename}...")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Update background color
        content = re.sub(
            r'BG = \(\d+, \d+, \d+\)',
            f'BG = {colors["bg"]}',
            content
        )
        
        # Update font sizes (find the try block with font definitions)
        content = re.sub(
            r'try:\s+title_font = pygame\.font\.Font\(None, \d+\).*?except:.*?small_font = pygame\.font\.SysFont\([^)]+\)',
            FONT_CONFIG.strip(),
            content,
            flags=re.DOTALL
        )
        
        # Replace small_font with item_font throughout
        content = content.replace('small_font', 'item_font')
        content = content.replace('text_font', 'section_font')
        
        # Update ACCENT color if it exists
        if 'ACCENT' in content:
            content = re.sub(
                r'ACCENT = \(\d+, \d+, \d+\)',
                f'ACCENT = {colors["accent"]}',
                content
            )
        
        # Add GLOW color for highlights
        if 'ACCENT = ' in content and 'GLOW = ' not in content:
            content = content.replace(
                f'ACCENT = {colors["accent"]}',
                f'ACCENT = {colors["accent"]}\n        GLOW = {colors["glow"]}'
            )
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Enhanced {filename}")
        
    except Exception as e:
        print(f"  ✗ Failed to enhance {filename}: {e}")

print("\n✓ All realms enhanced with futuristic theme!")
print("  - Larger fonts (110, 58, 46, 38)")
print("  - Modern color schemes")
print("  - Better readability on projector")
