#!/usr/bin/env python3
"""
Simple pygame display test for Raspberry Pi
"""
import pygame
import sys
import os

print("Testing Pygame on Raspberry Pi...")
print("=" * 50)

# Initialize - try different video drivers
print("1. Initializing pygame...")

# Detect environment
if 'DISPLAY' in os.environ:
    drivers = ['x11', 'directx', 'windib']
    print(f"   X11 display detected: {os.environ['DISPLAY']}")
else:
    drivers = ['fbcon', 'directfb', 'svgalib']
    print("   Console mode - trying framebuffer drivers")
    os.environ['SDL_FBDEV'] = '/dev/fb0'

# Try each driver
initialized = False
for driver in drivers:
    try:
        os.environ['SDL_VIDEODRIVER'] = driver
        print(f"   Trying {driver}...", end=' ')
        pygame.init()
        if pygame.display.get_init():
            print(f"✓")
            initialized = True
            break
        else:
            print("✗")
    except Exception as e:
        print(f"✗ ({e})")

# Fallback to automatic
if not initialized:
    print("   Trying automatic driver selection...", end=' ')
    if 'SDL_VIDEODRIVER' in os.environ:
        del os.environ['SDL_VIDEODRIVER']
    pygame.init()
    if pygame.display.get_init():
        print("✓")
        initialized = True
    else:
        print("✗")

if not initialized:
    print("   ✗ Pygame failed to initialize")
    sys.exit(1)

print("   ✓ Pygame initialized successfully")

# Create display
print("2. Creating 1024x768 fullscreen display...")
try:
    screen = pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
    print("   ✓ Display created successfully")
except Exception as e:
    print(f"   ✗ Failed to create display: {e}")
    print("   Trying windowed mode...")
    try:
        screen = pygame.display.set_mode((1024, 768))
        print("   ✓ Display created in windowed mode")
    except Exception as e2:
        print(f"   ✗ Failed: {e2}")
        sys.exit(1)

pygame.display.set_caption("Display Test")

# Draw test pattern
print("3. Drawing test pattern...")
screen.fill((30, 30, 35))  # Dark background

# Draw colored rectangles
pygame.draw.rect(screen, (220, 38, 38), (50, 50, 200, 150))    # Red
pygame.draw.rect(screen, (34, 197, 94), (300, 50, 200, 150))   # Green
pygame.draw.rect(screen, (59, 130, 246), (550, 50, 200, 150))  # Blue

# Draw text
font = pygame.font.Font(None, 48)
text = font.render("Display Test - Press Q to quit", True, (255, 255, 255))
screen.blit(text, (200, 300))

# Show smaller text
font_small = pygame.font.Font(None, 32)
text_small = font_small.render("If you can see this, pygame is working!", True, (180, 180, 190))
screen.blit(text_small, (200, 400))

pygame.display.flip()
print("   ✓ Test pattern drawn")
print()
print("If you see colored rectangles and text on the projector,")
print("pygame is working correctly! Press Q to quit.")
print()

# Event loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    clock.tick(30)

pygame.quit()
print("Test complete.")
