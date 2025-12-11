#!/bin/bash
# Display Diagnostics for Raspberry Pi

echo "======================================"
echo "  Display Diagnostics"
echo "======================================"
echo ""

echo "1. X11 Server Status:"
if pgrep -x "X" > /dev/null || pgrep -x "Xorg" > /dev/null; then
    echo "   ✓ X11 is running (PID: $(pgrep -x X || pgrep -x Xorg))"
else
    echo "   ✗ X11 is NOT running"
    echo "   → You need to start the desktop environment"
fi
echo ""

echo "2. DISPLAY Environment Variable:"
if [ -z "$DISPLAY" ]; then
    echo "   ✗ DISPLAY is not set"
    echo "   → Try: export DISPLAY=:0"
else
    echo "   ✓ DISPLAY=$DISPLAY"
fi
echo ""

echo "3. X11 Connection Test:"
if command -v xdpyinfo &> /dev/null; then
    if xdpyinfo >/dev/null 2>&1; then
        echo "   ✓ Can connect to X11 display"
        echo "   Display info:"
        xdpyinfo | grep -E "dimensions|resolution" | sed 's/^/   /'
    else
        echo "   ✗ Cannot connect to X11 display"
        echo "   → May need: xhost +local:"
    fi
else
    echo "   ⚠ xdpyinfo not installed (can't test)"
fi
echo ""

echo "4. Current Desktop Session:"
if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    echo "   ✓ Desktop: $XDG_CURRENT_DESKTOP"
elif [ -n "$DESKTOP_SESSION" ]; then
    echo "   ✓ Session: $DESKTOP_SESSION"
else
    echo "   ✗ No desktop session detected"
    echo "   → You may be in console/SSH mode"
fi
echo ""

echo "5. Display Outputs (framebuffer):"
if [ -e /dev/fb0 ]; then
    echo "   ✓ /dev/fb0 exists"
    if [ -r /dev/fb0 ] && [ -w /dev/fb0 ]; then
        echo "   ✓ /dev/fb0 is readable and writable"
    else
        echo "   ✗ /dev/fb0 exists but no permissions"
        echo "   → Try running with sudo"
    fi
else
    echo "   ✗ /dev/fb0 not found"
fi
echo ""

echo "6. Pygame Test:"
python3 -c "
import pygame
import os
print('   Pygame version:', pygame.version.ver)
print('   SDL version:', pygame.version.SDL)
print('   Available video drivers:', pygame.display.get_driver())
" 2>/dev/null
echo ""

echo "======================================"
echo "Recommendations:"
echo "======================================"
if pgrep -x "X" > /dev/null || pgrep -x "Xorg" > /dev/null; then
    if [ -z "$DISPLAY" ]; then
        echo "✓ X11 is running - just set DISPLAY:"
        echo "  export DISPLAY=:0"
        echo "  ./run_with_display.sh"
    else
        echo "✓ Everything looks good! Try:"
        echo "  ./run_with_display.sh"
    fi
else
    echo "You need to start the desktop environment:"
    echo ""
    echo "Option 1 - Boot to desktop (permanent):"
    echo "  sudo raspi-config"
    echo "  → System Options → Boot / Auto Login → Desktop Autologin"
    echo "  → Reboot"
    echo ""
    echo "Option 2 - Start desktop now (temporary):"
    echo "  startx"
    echo "  → Then run the app from the desktop terminal"
    echo ""
    echo "Option 3 - If SSH'd in:"
    echo "  → Open terminal directly on the Pi (keyboard+mouse)"
    echo "  → The app needs to run in the graphical session"
fi
