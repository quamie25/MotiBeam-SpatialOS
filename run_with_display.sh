#!/bin/bash
# MotiBeam Spatial OS - Display-Aware Launch Script

echo "======================================"
echo "  MotiBeam Spatial OS"
echo "  Projection Operating System v1.0"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Check pygame installation
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame --quiet
fi

# Detect display environment
echo "Detecting display environment..."

# Check if X11 is running
if pgrep -x "X" > /dev/null || pgrep -x "Xorg" > /dev/null; then
    echo "✓ X11 server is running"

    # Set DISPLAY if not already set
    if [ -z "$DISPLAY" ]; then
        echo "  Setting DISPLAY=:0"
        export DISPLAY=:0
    else
        echo "  Using DISPLAY=$DISPLAY"
    fi

    # Verify we can connect to the display
    if xdpyinfo >/dev/null 2>&1; then
        echo "✓ Can connect to X11 display"
    else
        echo "⚠ Warning: Cannot connect to X11 display"
        echo "  You may need to run: xhost +local:"
    fi
else
    echo "⚠ X11 server not detected"
    echo ""
    echo "Options:"
    echo "  1. Start desktop environment: startx"
    echo "  2. Or run from desktop (if already booted to GUI)"
    echo "  3. Or try with sudo for framebuffer access"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Launching MotiBeam Spatial OS..."
echo ""

# Launch with display debugging
python3 spatial_os_pygame.py

EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Thank you for using MotiBeam Spatial OS."
else
    echo "Application exited with error code $EXIT_CODE"
fi
