"""
MotiBeam Spatial OS - Patent Display Manager (Simplified)

This version forces a real visible display:
- Uses SDL_VIDEODRIVER=x11
- Uses DISPLAY=:0
- Tries 1920x1080 fullscreen, then 1280x720, then 800x600 windowed
"""

import os
import pygame

class PatentDisplayManager:
    def __init__(self):
        # Force sane defaults for Pi desktop
        os.environ.setdefault("SDL_VIDEODRIVER", "x11")
        os.environ.setdefault("DISPLAY", ":0")

        pygame.display.init()

        self.width = 1920
        self.height = 1080
        self.screen = None
        self.fullscreen = True

        # Try 1920x1080 fullscreen
        try:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
            print(f"[DISPLAY] 1920x1080 FULLSCREEN OK (driver: {pygame.display.get_driver()})")
        except Exception as e1:
            print(f"[DISPLAY] 1920x1080 fullscreen failed: {e1}")
            # Fallback to 1280x720 fullscreen
            self.width, self.height = 1280, 720
            try:
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                print(f"[DISPLAY] 1280x720 FULLSCREEN OK (driver: {pygame.display.get_driver()})")
            except Exception as e2:
                print(f"[DISPLAY] 1280x720 fullscreen failed: {e2}")
                # Final fallback: 800x600 windowed
                self.width, self.height = 800, 600
                self.fullscreen = False
                self.screen = pygame.display.set_mode((self.width, self.height))
                print(f"[DISPLAY] 800x600 WINDOWED OK (driver: {pygame.display.get_driver()})")

        pygame.display.set_caption("MotiBeam Spatial OS")

    def get_screen(self):
        return self.screen

    def get_dimensions(self):
        return self.width, self.height

# Simple global accessor (what the rest of the code expects)
_display_manager_instance = None

def get_display_manager():
    global _display_manager_instance
    if _display_manager_instance is None:
        _display_manager_instance = PatentDisplayManager()
    return _display_manager_instance
