#!/bin/bash
echo "Fixing for 1024x768 resolution..."

# Update resolution
sed -i 's/SCREEN_WIDTH = 1280/SCREEN_WIDTH = 1024/' spatial_os.py
sed -i 's/SCREEN_HEIGHT = 720/SCREEN_HEIGHT = 768/' spatial_os.py

# Optimize layout for 1024px
sed -i 's/HEADER_HEIGHT = 120/HEADER_HEIGHT = 100/' spatial_os.py
sed -i 's/FOOTER_HEIGHT = 50/FOOTER_HEIGHT = 60/' spatial_os.py
sed -i 's/GRID_MARGIN = 15/GRID_MARGIN = 12/' spatial_os.py
sed -i 's/GRID_PADDING = 6/GRID_PADDING = 4/' spatial_os.py

# Slightly smaller fonts for narrower screen
sed -i 's/TITLE_FONT_SIZE = 56/TITLE_FONT_SIZE = 52/' spatial_os.py
sed -i 's/CLOCK_FONT_SIZE = 48/CLOCK_FONT_SIZE = 44/' spatial_os.py
sed -i 's/REALM_EMOJI_SIZE = 64/REALM_EMOJI_SIZE = 60/' spatial_os.py

echo "Updated for 1024x768"
echo "Expected card width: $(( (1024 - 24) / 3 - 4 ))px"
