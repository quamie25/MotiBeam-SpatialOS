#!/bin/bash
# MotiBeam Spatial OS - Launch Script

echo "======================================"
echo "  MotiBeam Spatial OS"
echo "  Projection Operating System v1.0"
echo "======================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame --quiet
    if [ $? -ne 0 ]; then
        echo "Failed to install pygame. Please install manually:"
        echo "  sudo apt-get install python3-pygame"
        exit 1
    fi
fi

# Check pygame version
echo "Pygame version:"
python3 -c "import pygame; print(f'  {pygame.version.ver}')"
echo ""

# Set display environment for Pi
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0

# Launch the application
echo "Launching MotiBeam Spatial OS..."
echo ""
python3 spatial_os_pygame.py

EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Thank you for using MotiBeam Spatial OS."
else
    echo "Application exited with error code $EXIT_CODE"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Run: python3 test_display.py"
    echo "  2. Check display connection"
    echo "  3. Try: sudo python3 spatial_os_pygame.py"
fi
