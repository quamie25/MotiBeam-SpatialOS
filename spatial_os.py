#!/usr/bin/env python3
"""
MotiBeam Spatial OS - Clean Pygame Launcher (Framebuffer-Friendly)

- Uses the same style of framebuffer init as your working test_display.py
- 1024x768 fullscreen
- 4x3 realm grid
- Big fonts + emojis
- Arrow keys to move selection
- Enter to "select"
- Q or ESC to quit
"""

import os
import sys
import pygame
from datetime import datetime

# ---------------------------
# Config
# ---------------------------

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_COLS = 4
GRID_ROWS = 3

BG_COLOR = (10, 12, 20)
CARD_BG = (26, 30, 48)
CARD_BORDER = (80, 90, 140)
CARD_BORDER_SELECTED = (255, 200, 80)
HEADER_COLOR = (230, 235, 245)
FOOTER_COLOR = (200, 205, 215)
TEXT_PRIMARY = (245, 248, 255)
TEXT_SECONDARY = (170, 175, 190)

REALMS = [
    {"name": "CircleBeam", "subtitle": "Living relationships", "emoji": "👥"},
    {"name": "LegacyBeam", "subtitle": "Memory & legacy",      "emoji": "📖"},
    {"name": "LockboxBeam", "subtitle": "Secure vault",        "emoji": "🔐"},
    {"name": "Marketplace", "subtitle": "Wellness & goods",    "emoji": "🛒"},
    {"name": "Home",       "subtitle": "Smart home",           "emoji": "🏠"},
    {"name": "Clinical",   "subtitle": "Health & wellness",    "emoji": "🏥"},
    {"name": "Education",  "subtitle": "Learning hub",         "emoji": "📚"},
    {"name": "Emergency",  "subtitle": "Crisis response",      "emoji": "🚨"},
    {"name": "Transport",  "subtitle": "Automotive HUD",       "emoji": "🚗"},
    {"name": "Security",   "subtitle": "Surveillance",         "emoji": "🛡️"},
    {"name": "Aviation",   "subtitle": "Flight systems",       "emoji": "✈️"},
    {"name": "Maritime",   "subtitle": "Navigation",           "emoji": "⚓"},
]


# ---------------------------
# Display init (matching test_display.py style)
# ---------------------------

def init_display(width, height):
    """
    Super simple display init that mirrors the working behavior
    from test_display.py: let SDL choose the right driver.
    """

    print("Initializing pygame...")
    pygame.quit()
    pygame.display.quit()
    pygame.init()

    # Force SDL to pick the best driver automatically
    try:
        os.unsetenv("SDL_VIDEODRIVER")
    except Exception:
        os.putenv("SDL_VIDEODRIVER", "")

    pygame.display.init()
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    print(f"  ✓ Display created successfully ({width}x{height}, fullscreen)")
    pygame.display.set_caption("MotiBeam Spatial OS – Clean Build")

    return screen

    # Start fresh
    pygame.quit()
    pygame.display.quit()
    pygame.init()

    screen = None

    if not os.getenv("DISPLAY"):
        print("Console mode detected – trying framebuffer drivers...")
        drivers = ["fbcon", "directfb", "svgalib"]
        for driver in drivers:
            print(f"  Trying video driver: {driver}...")
            os.putenv("SDL_VIDEODRIVER", driver)
            try:
                pygame.display.init()
                screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                print(f"    ✓ Using driver: {driver}")
                break
            except pygame.error as e:
                print(f"    ✗ {driver} failed: {e}")
                pygame.display.quit()
                screen = None

        if screen is None:
            # This is the path that worked in test_display.py:
            # "Trying automatic driver selection... ✓"
            print("  Trying automatic driver selection...")
            # Clear SDL_VIDEODRIVER so SDL chooses
            try:
                os.unsetenv("SDL_VIDEODRIVER")
            except Exception:
                os.putenv("SDL_VIDEODRIVER", "")
            pygame.display.init()
            screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
            print("  ✓ Auto driver worked")
    else:
        # X11 / desktop
        print(f"DISPLAY is set ({os.getenv('DISPLAY')}), using normal X11 init")
        pygame.display.init()
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        print("  ✓ X11 display created")

    pygame.display.set_caption("MotiBeam Spatial OS")
    return screen

    # Now create the display
    flags = pygame.FULLSCREEN
    print(f"Creating display: {width}x{height} (fullscreen=True)")
    try:
        screen = pygame.display.set_mode((width, height), flags)
        print("  ✓ Display created successfully")
    except pygame.error as e:
        print(f"  ✗ Fullscreen failed: {e}")
        print("  → Falling back to windowed mode")
        screen = pygame.display.set_mode((width, height))
        print("  ✓ Windowed display created successfully")

    pygame.display.set_caption("MotiBeam Spatial OS")
    return screen


class MotiBeamOS:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.screen = init_display(width, height)
        self.width = width
        self.height = height

        # Fonts (projection friendly – large)
        self.font_header = pygame.font.SysFont(None, 42)
        self.font_header_meta = pygame.font.SysFont(None, 30)
        # Use NotoColorEmoji for proper emoji rendering
        try:
            self.font_emoji = pygame.font.Font('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 96)
        except:
            self.font_emoji = pygame.font.SysFont(None, 96)  # Fallback
        self.font_card_title = pygame.font.SysFont(None, 34)
        self.font_card_subtitle = pygame.font.SysFont(None, 22)
        self.font_footer = pygame.font.SysFont(None, 24)

        self.clock = pygame.time.Clock()
        self.selected_index = 0  # which card is selected
        self.show_call_overlay = False  # call simulation overlay

        # Precompute grid cell sizes
        self.grid_top = 140
        self.grid_bottom = self.height - 120
        available_height = self.grid_bottom - self.grid_top
        available_width = self.width - 120

        self.cell_w = available_width // GRID_COLS
        self.cell_h = available_height // GRID_ROWS

    def draw_header(self):
        # Left: title
        title_text = self.font_header.render("MOTIBEAM SPATIAL OS", True, HEADER_COLOR)
        self.screen.blit(title_text, (40, 30))

        # Right: time + date
        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip("0")
        date_str = now.strftime("%a • %b %d")

        time_surf = self.font_header_meta.render(time_str, True, HEADER_COLOR)
        date_surf = self.font_header_meta.render(date_str, True, HEADER_COLOR)

        tx = self.width - time_surf.get_width() - 40
        ty = 26
        self.screen.blit(time_surf, (tx, ty))
        self.screen.blit(date_surf, (tx, ty + time_surf.get_height() + 4))

    def draw_footer(self):
        # Simple footer strip
        footer_rect = pygame.Rect(0, self.height - 60, self.width, 60)
        pygame.draw.rect(self.screen, (18, 20, 30), footer_rect)

        footer_text = (
            "←↑↓→ Move   |   Enter Select   |   Q / ESC Exit   |   1–9 Quick Jump"
        )
        surf = self.font_footer.render(footer_text, True, FOOTER_COLOR)
        self.screen.blit(
            surf,
            (self.width // 2 - surf.get_width() // 2,
             self.height - 60 + 18),
        )

    def draw_grid(self):
        for i, realm in enumerate(REALMS):
            row = i // GRID_COLS
            col = i % GRID_COLS

            x = 60 + col * self.cell_w
            y = self.grid_top + row * self.cell_h

            card_rect = pygame.Rect(
                x + 10, y + 10, self.cell_w - 20, self.cell_h - 20
            )

            # Card background
            pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=18)

            # Card border (selected or normal)
            if i == self.selected_index:
                pygame.draw.rect(
                    self.screen,
                    CARD_BORDER_SELECTED,
                    card_rect,
                    width=4,
                    border_radius=18,
                )
            else:
                pygame.draw.rect(
                    self.screen,
                    CARD_BORDER,
                    card_rect,
                    width=2,
                    border_radius=18,
                )

            # Emoji (larger 96px size)
            emoji_surf = self.font_emoji.render(realm["emoji"], True, TEXT_PRIMARY)
            ex = card_rect.centerx - emoji_surf.get_width() // 2
            ey = card_rect.y + 12  # Reduced from 18 to 12 for better vertical centering
            self.screen.blit(emoji_surf, (ex, ey))

            # Title
            title_surf = self.font_card_title.render(
                realm["name"], True, TEXT_PRIMARY
            )
            tx = card_rect.centerx - title_surf.get_width() // 2
            ty = ey + emoji_surf.get_height() + 8  # Reduced from 10 to 8 for tighter spacing
            self.screen.blit(title_surf, (tx, ty))

            # Subtitle
            subtitle_surf = self.font_card_subtitle.render(
                realm["subtitle"], True, TEXT_SECONDARY
            )
            sx = card_rect.centerx - subtitle_surf.get_width() // 2
            sy = ty + title_surf.get_height() + 4
            self.screen.blit(subtitle_surf, (sx, sy))

    def move_selection(self, dx, dy):
        index = self.selected_index
        row = index // GRID_COLS
        col = index % GRID_COLS

        row = max(0, min(GRID_ROWS - 1, row + dy))
        col = max(0, min(GRID_COLS - 1, col + dx))

        new_index = row * GRID_COLS + col
        if new_index < len(REALMS):
            self.selected_index = new_index

    def handle_key(self, key):
        if key in (pygame.K_q, pygame.K_ESCAPE):
            if self.show_call_overlay:
                # ESC cancels the call overlay
                self.show_call_overlay = False
            else:
                pygame.quit()
                sys.exit(0)

        # Call overlay handlers
        if key == pygame.K_i:
            self.show_call_overlay = not self.show_call_overlay
        elif key == pygame.K_a and self.show_call_overlay:
            print("Call accepted from Mom")
            self.show_call_overlay = False
        elif key == pygame.K_d and self.show_call_overlay:
            print("Call declined from Mom")
            self.show_call_overlay = False

        # Navigation (disabled during call overlay)
        if not self.show_call_overlay:
            if key == pygame.K_LEFT:
                self.move_selection(-1, 0)
            elif key == pygame.K_RIGHT:
                self.move_selection(1, 0)
            elif key == pygame.K_UP:
                self.move_selection(0, -1)
            elif key == pygame.K_DOWN:
                self.move_selection(0, 1)
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                realm = REALMS[self.selected_index]
                print(f"[SELECT] {realm['name']} – {realm['subtitle']}")
            elif pygame.K_1 <= key <= pygame.K_9:
                idx = key - pygame.K_1
                if idx < len(REALMS):
                    self.selected_index = idx

    def render_call_overlay(self):
        """Render incoming call overlay with dimmed background"""
        # Dim background
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Call card (centered)
        card_w, card_h = 500, 300
        card_x = (self.width - card_w) // 2
        card_y = (self.height - card_h) // 2

        pygame.draw.rect(self.screen, (40, 40, 50),
                         (card_x, card_y, card_w, card_h), border_radius=15)

        # "Incoming Call" label
        label_surf = self.font_card_title.render("Incoming Call", True, (200, 200, 210))
        label_x = card_x + card_w // 2 - label_surf.get_width() // 2
        label_y = card_y + 40
        self.screen.blit(label_surf, (label_x, label_y))

        # Caller name "Mom"
        name_surf = self.font_header.render("Mom", True, (255, 255, 255))
        name_x = card_x + card_w // 2 - name_surf.get_width() // 2
        name_y = label_y + 60
        self.screen.blit(name_surf, (name_x, name_y))

        # Instructions
        instruction_surf = self.font_footer.render("A - Accept  |  D - Decline  |  ESC - Cancel",
                                                    True, (170, 175, 190))
        inst_x = card_x + card_w // 2 - instruction_surf.get_width() // 2
        inst_y = card_y + card_h - 50
        self.screen.blit(instruction_surf, (inst_x, inst_y))

    def run(self):
        print("MotiBeam Spatial OS – clean launcher running (framebuffer-friendly)")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            self.screen.fill(BG_COLOR)
            self.draw_header()
            self.draw_grid()
            self.draw_footer()

            # Render call overlay on top if active
            if self.show_call_overlay:
                self.render_call_overlay()

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    app = MotiBeamOS(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    app.run()
