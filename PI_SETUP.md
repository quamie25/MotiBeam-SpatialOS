# Raspberry Pi Setup Guide

## Quick Start

1. **Test pygame installation:**
   ```bash
   python3 test_display.py
   ```
   This will test if pygame can create a display on your Pi.

2. **Run MotiBeam Spatial OS:**
   ```bash
   ./run_pygame.sh
   ```
   or directly:
   ```bash
   python3 spatial_os_pygame.py
   ```

## Resolution

The app is configured for **1024×768** to match your Goodee projector.

## Troubleshooting

### No window appears

1. **Check if running in X11 (desktop environment):**
   ```bash
   echo $DISPLAY
   ```
   If it shows something like `:0`, you're in X11 mode (good!)

2. **Try running the test first:**
   ```bash
   python3 test_display.py
   ```

3. **If in console mode (no X11), try with sudo:**
   ```bash
   sudo python3 spatial_os_pygame.py
   ```

### Display driver issues

The app automatically tries multiple video drivers:
- **X11 mode**: x11 → directx → windib → automatic
- **Console mode**: fbcon → directfb → svgalib → automatic

You'll see output showing which driver succeeded.

## Display Features

- **Resolution**: 1024×768 (projector optimized)
- **Fullscreen**: Yes by default
- **Fonts**: Large sizes for 6-10 ft viewing distance
- **Emojis**: Enterprise-clean style on each realm card
- **Ticker**: Slow, comfortable scrolling speed

## Controls

- **Arrow Keys**: Navigate realm grid
- **Enter**: Select realm
- **1-9**: Quick-select realm
- **A**: Trigger severe weather alert
- **M**: Trigger medical reminder
- **C**: Clear alerts (return to calm)
- **Q**: Quit

## Performance

- Runs at 60 FPS
- Optimized for Raspberry Pi 3/4/5
- Low CPU usage for smooth projection
