#!/usr/bin/env python3
"""
MotiBeam Spatial OS - Pygame Main Application
Projection-optimized UI with realm grid, emojis, alerts, and ticker.
"""

import pygame
import sys
import os
from core.design_tokens import *
from core.notification_banner import NotificationBanner
from core.notification_ticker import NotificationTicker
from config.realms_config import REALMS
from scenes.productivity_realm import ProductivityRealm

class SpatialOS:
    def __init__(self, width=1024, height=768, fullscreen=True):
        # Initialize pygame - try multiple video drivers for Pi compatibility
        print("Initializing pygame...")

        # Auto-detect and set DISPLAY if not set but X is running
        if 'DISPLAY' not in os.environ:
            # Check if X server is running
            import subprocess
            try:
                result = subprocess.run(['pgrep', '-x', 'X'], capture_output=True, timeout=1)
                if result.returncode == 0:
                    print("X11 server detected, setting DISPLAY=:0")
                    os.environ['DISPLAY'] = ':0'
                else:
                    result = subprocess.run(['pgrep', '-x', 'Xorg'], capture_output=True, timeout=1)
                    if result.returncode == 0:
                        print("Xorg server detected, setting DISPLAY=:0")
                        os.environ['DISPLAY'] = ':0'
            except:
                pass

        # Try different SDL video drivers in order of preference
        drivers_to_try = []

        # If DISPLAY is set, we're likely in X11/desktop environment
        if 'DISPLAY' in os.environ:
            drivers_to_try = ['x11', 'directx', 'windib']
            print(f"X11 display detected ({os.environ.get('DISPLAY')})")
        else:
            # No X11, try framebuffer drivers
            drivers_to_try = ['fbcon', 'directfb', 'svgalib']
            print("Console mode detected, using framebuffer")
            if 'SDL_FBDEV' not in os.environ:
                os.environ['SDL_FBDEV'] = '/dev/fb0'

        # Try each driver until one works
        display_initialized = False
        for driver in drivers_to_try:
            try:
                os.environ['SDL_VIDEODRIVER'] = driver
                print(f"  Trying video driver: {driver}...")
                pygame.init()
                if pygame.display.get_init():
                    print(f"  ✓ Successfully initialized with {driver}")
                    display_initialized = True
                    break
            except Exception as e:
                print(f"  ✗ Driver {driver} failed: {e}")
                continue

        if not display_initialized:
            # Last resort - let SDL choose automatically
            print("  Trying automatic driver selection...")
            if 'SDL_VIDEODRIVER' in os.environ:
                del os.environ['SDL_VIDEODRIVER']
            pygame.init()
            if not pygame.display.get_init():
                print("FATAL: Could not initialize any video driver!")
                sys.exit(1)
            print("  ✓ Using automatic driver selection")

        # Create display window
        print(f"Creating display: {width}x{height} (fullscreen={fullscreen})")
        self.screen = None

        # Try fullscreen first if requested
        if fullscreen:
            try:
                self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                pygame.display.set_caption("MotiBeam Spatial OS")
                print("  ✓ Display created in fullscreen mode")
            except Exception as e:
                print(f"  ✗ Fullscreen failed: {e}")

        # Fall back to windowed mode
        if self.screen is None:
            try:
                self.screen = pygame.display.set_mode((width, height))
                pygame.display.set_caption("MotiBeam Spatial OS")
                print("  ✓ Display created in windowed mode")
            except Exception as e:
                print(f"FATAL: Could not create display window: {e}")
                print("\nTroubleshooting:")
                print("  1. Check if your display is connected")
                print("  2. Try running: python3 test_display.py")
                print("  3. Check if you need to run with sudo")
                sys.exit(1)

        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.running = True

        # Components
        self.banner = NotificationBanner(width)
        self.ticker = NotificationTicker(width, height)

        # Realm navigation
        self.selected_realm = 0
        self.realms = REALMS

        # Add sample ticker messages
        self.ticker.add_message("Weather: Sunny, 72°F • Traffic: Normal conditions on all routes")
        self.ticker.add_message("System Status: All realms operational • Last sync: 3 minutes ago")
        self.ticker.add_message("Calendar: Team meeting at 4:00 PM • No urgent tasks pending")

        # Selection animation
        self.selection_pulse = 0
        self.selection_pulse_direction = 1

    def handle_events(self):
        """Handle keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Navigation
                if event.key == pygame.K_LEFT:
                    if self.selected_realm % GRID_COLS > 0:
                        self.selected_realm -= 1

                elif event.key == pygame.K_RIGHT:
                    if self.selected_realm % GRID_COLS < GRID_COLS - 1 and self.selected_realm < len(self.realms) - 1:
                        self.selected_realm += 1

                elif event.key == pygame.K_UP:
                    if self.selected_realm >= GRID_COLS:
                        self.selected_realm -= GRID_COLS

                elif event.key == pygame.K_DOWN:
                    if self.selected_realm + GRID_COLS < len(self.realms):
                        self.selected_realm += GRID_COLS

                # Enter to select
                elif event.key == pygame.K_RETURN:
                    realm = self.realms[self.selected_realm]
                    print(f"Selected realm: {realm['name']}")
                    self.ticker.add_message(f"Entering {realm['name']} - {realm['tagline']}")

                    # Handle Productivity realm
                    if realm['id'] == 'productivity':
                        productivity = ProductivityRealm(self.screen)
                        productivity.run()
                        # Return to main grid after exiting productivity realm

                # Quick select with numbers
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    realm_num = event.key - pygame.K_1
                    if realm_num < len(self.realms):
                        self.selected_realm = realm_num

                # State changes
                elif event.key == pygame.K_a:
                    # Trigger severe weather alert
                    self.banner.clear_alerts()
                    self.banner.add_alert("severe", "⚠ SEVERE WEATHER WARNING", "Tornado spotted nearby. Take shelter immediately.")
                    self.banner.set_state("ALERT")
                    self.ticker.add_message("ALERT: Severe weather detected in your area")

                elif event.key == pygame.K_m:
                    # Trigger medical alert
                    self.banner.clear_alerts()
                    self.banner.add_alert("medical", "🏥 MEDICAL REMINDER", "Time to take medication - check MediBeam")
                    self.banner.set_state("ALERT")
                    self.ticker.add_message("Medical reminder active")

                elif event.key == pygame.K_c:
                    # Clear alerts, return to calm
                    self.banner.clear_alerts()
                    self.banner.set_state("CALM")
                    self.ticker.add_message("System returned to calm state")

                # Quit
                elif event.key == pygame.K_q:
                    self.running = False

    def update(self):
        """Update animations and state."""
        self.ticker.update()

        # Update selection pulse animation (subtle)
        self.selection_pulse += 0.02 * self.selection_pulse_direction
        if self.selection_pulse >= 1.0 or self.selection_pulse <= 0.0:
            self.selection_pulse_direction *= -1

    def draw(self):
        """Render the complete UI."""
        # Background
        self.screen.fill(BG_COLOR)

        # Header with alerts
        header_height = self.banner.draw(self.screen)

        # Realm grid
        grid_y_start = header_height + PADDING
        grid_height = self.height - header_height - TICKER_HEIGHT - PADDING * 2
        self.draw_realm_grid(grid_y_start, grid_height)

        # Footer ticker
        self.ticker.draw(self.screen)

        pygame.display.flip()

    def draw_realm_grid(self, y_start, available_height):
        """Draw the 4x3 grid of realm cards with emojis."""
        # Calculate card dimensions
        grid_width = self.width - PADDING * 2
        card_width = (grid_width - (GRID_COLS - 1) * CARD_SPACING) // GRID_COLS
        card_height = (available_height - (GRID_ROWS - 1) * CARD_SPACING) // GRID_ROWS

        for idx, realm in enumerate(self.realms):
            row = idx // GRID_COLS
            col = idx % GRID_COLS

            # Card position
            x = PADDING + col * (card_width + CARD_SPACING)
            y = y_start + row * (card_height + CARD_SPACING)

            self.draw_realm_card(realm, x, y, card_width, card_height, idx == self.selected_realm)

    def draw_realm_card(self, realm, x, y, width, height, is_selected):
        """Draw a single realm card with emoji, title, and tagline."""
        # Card background
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, BG_HEADER, card_rect, border_radius=CARD_RADIUS)

        # Border color
        border_color = REALM_COLORS.get(realm["id"], (100, 100, 110))

        # Selection highlight with pulse
        if is_selected:
            border_width = SELECTION_WIDTH
            # Pulse effect - vary opacity slightly
            pulse_alpha = int(200 + 55 * self.selection_pulse)
            selection_color = (*SELECTION_COLOR, pulse_alpha)

            # Draw thicker yellow border with subtle glow
            pygame.draw.rect(self.screen, SELECTION_COLOR, card_rect,
                           width=border_width, border_radius=CARD_RADIUS)

            # Inner subtle glow
            glow_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
            pygame.draw.rect(self.screen, SELECTION_COLOR, glow_rect,
                           width=1, border_radius=CARD_RADIUS)
        else:
            pygame.draw.rect(self.screen, border_color, card_rect,
                           width=2, border_radius=CARD_RADIUS)

        # Content positioning
        content_y = y + CARD_PADDING

        # Emoji (large and centered)
        emoji = realm.get("emoji", "")
        if emoji:
            try:
                font_emoji = pygame.font.Font(None, FONT_EMOJI_SIZE)
                emoji_surface = font_emoji.render(emoji, True, TEXT_PRIMARY)
                emoji_x = x + (width - emoji_surface.get_width()) // 2
                self.screen.blit(emoji_surface, (emoji_x, content_y))
                content_y += emoji_surface.get_height() + CARD_PADDING
            except Exception as e:
                print(f"Error rendering emoji for {realm['name']}: {e}")

        # Realm name (bold, large)
        font_title = pygame.font.Font(None, FONT_REALM_TITLE_SIZE)
        title_surface = font_title.render(realm["name"], True, TEXT_PRIMARY)
        title_x = x + (width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, content_y))
        content_y += title_surface.get_height() + 8

        # Tagline (smaller, muted)
        font_subtitle = pygame.font.Font(None, FONT_REALM_SUBTITLE_SIZE)
        subtitle_surface = font_subtitle.render(realm["tagline"], True, TEXT_SECONDARY)
        subtitle_x = x + (width - subtitle_surface.get_width()) // 2
        self.screen.blit(subtitle_surface, (subtitle_x, content_y))

    def run(self):
        """Main game loop."""
        print("MotiBeam Spatial OS - Starting projection interface...")
        print("Controls:")
        print("  Arrow Keys: Navigate realms")
        print("  Enter: Select realm")
        print("  1-9: Quick-select realm")
        print("  A: Trigger severe weather alert")
        print("  M: Trigger medical reminder")
        print("  C: Clear alerts (return to calm)")
        print("  Q: Quit")
        print()

        # Force initial draw to ensure window appears
        print("Rendering initial frame...")
        self.draw()
        pygame.display.update()
        print("UI should now be visible on the projector!")
        print()

        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(60)  # 60 FPS
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                self.running = False
            except Exception as e:
                print(f"ERROR in main loop: {e}")
                import traceback
                traceback.print_exc()
                self.running = False

        pygame.quit()
        print("MotiBeam Spatial OS - Shutdown complete.")

def main():
    # Default to Pi projector resolution (1024x768) and fullscreen
    app = SpatialOS(width=1024, height=768, fullscreen=True)
    app.run()

if __name__ == "__main__":
    main()
