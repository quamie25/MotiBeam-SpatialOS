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
import time
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
    {"name": "Home",         "subtitle": "Smart home",           "emoji": "🏠"},
    {"name": "Productivity", "subtitle": "Workflow layer",       "emoji": "⚡"},
    {"name": "Education",    "subtitle": "Learning hub",         "emoji": "📚"},
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


# ---------------------------
# Productivity Realm (Projection-Optimized)
# ---------------------------

class ProductivityRealm:
    """Projection-readable Productivity realm with licensing-first content"""

    # 2x3 grid of productivity modules
    MODULES = [
        {"name": "Focus Sprint",     "sublabel": "Pomodoro pacing",       "icon": "⏱️", "status": "READY"},
        {"name": "Task Board",       "sublabel": "Top 3 priorities",      "icon": "✓",  "status": "READY"},
        {"name": "Meeting Mode",     "sublabel": "Agenda + presence",     "icon": "👥", "status": "READY"},
        {"name": "Daily Brief",      "sublabel": "Schedule + signals",    "icon": "📅", "status": "READY"},
        {"name": "Ops Dashboard",    "sublabel": "Operational awareness", "icon": "📊", "status": "READY"},
        {"name": "Deep Work Audio",  "sublabel": "Focus soundscapes",     "icon": "🎧", "status": "READY"},
    ]

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        # Projection-readable fonts (HUGE for 10-15 feet)
        self.font_title = pygame.font.SysFont(None, 90)        # 84-96px: PRODUCTIVITY
        self.font_subtitle = pygame.font.SysFont(None, 44)     # 40-48px: Ambient Workflow Layer
        self.font_tile_name = pygame.font.SysFont(None, 58)    # 52-64px: Module names
        self.font_tile_sublabel = pygame.font.SysFont(None, 38) # 34-42px: Module sublabels
        self.font_tile_icon = pygame.font.SysFont(None, 76)    # Big module icons
        self.font_panel_headline = pygame.font.SysFont(None, 64) # 56-72px: Panel headlines
        self.font_panel_bullet = pygame.font.SysFont(None, 40)   # 38-44px: Panel bullets
        self.font_controls = pygame.font.SysFont(None, 32)       # 30-36px: Footer controls
        self.font_status_pill = pygame.font.SysFont(None, 30)    # Status pills
        self.font_demo_timer = pygame.font.SysFont(None, 190)    # 160-220px: HUGE demo timer

        # State
        self.selected_module = 0
        self.show_preview_panel = False
        self.demo_mode = False
        self.demo_timer = 30  # 30 second demo
        self.demo_paused = False
        self.demo_start_time = None
        self.running = True

    def handle_input(self):
        """Handle keyboard input for Productivity realm"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                # ESC - exit demo or return to home
                if event.key == pygame.K_ESCAPE:
                    if self.demo_mode:
                        self.demo_mode = False
                        self.demo_paused = False
                    else:
                        return "home"

                # Navigation (only when not in demo mode)
                elif not self.demo_mode:
                    if event.key == pygame.K_LEFT:
                        if self.selected_module % 2 > 0:
                            self.selected_module -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.selected_module % 2 < 1 and self.selected_module < 5:
                            self.selected_module += 1
                    elif event.key == pygame.K_UP:
                        if self.selected_module >= 2:
                            self.selected_module -= 2
                    elif event.key == pygame.K_DOWN:
                        if self.selected_module + 2 < 6:
                            self.selected_module += 2

                    # ENTER - toggle preview panel
                    elif event.key == pygame.K_RETURN:
                        self.show_preview_panel = not self.show_preview_panel

                    # S - start demo mode
                    elif event.key == pygame.K_s:
                        self.demo_mode = True
                        self.demo_start_time = time.time()
                        self.demo_timer = 30
                        self.demo_paused = False

                # Demo mode controls
                elif self.demo_mode:
                    if event.key == pygame.K_SPACE:
                        self.demo_paused = not self.demo_paused
                        if not self.demo_paused:
                            self.demo_start_time = time.time() - (30 - self.demo_timer)
                    elif event.key == pygame.K_r:
                        self.demo_timer = 30
                        self.demo_start_time = time.time()
                        self.demo_paused = False

        return None

    def update(self):
        """Update demo timer"""
        if self.demo_mode and not self.demo_paused and self.demo_start_time:
            elapsed = time.time() - self.demo_start_time
            self.demo_timer = max(0, 30 - int(elapsed))

    def draw(self):
        """Main draw function"""
        self.screen.fill((10, 12, 20))  # Dark background

        if self.demo_mode:
            self.draw_demo_overlay()
        else:
            self.draw_main_view()

        pygame.display.flip()

    def draw_main_view(self):
        """Draw main productivity view"""
        # Title (HUGE for projection)
        title_surf = self.font_title.render("PRODUCTIVITY", True, (245, 248, 255))
        self.screen.blit(title_surf, (40, 30))

        # Subtitle
        subtitle_surf = self.font_subtitle.render("Ambient Workflow Layer", True, (170, 175, 190))
        self.screen.blit(subtitle_surf, (40, 125))

        # Calculate grid area
        if self.show_preview_panel:
            grid_width = int(self.width * 0.58)  # 58% for grid, 40% for panel
        else:
            grid_width = self.width - 80

        grid_start_y = 190
        grid_height = self.height - grid_start_y - 100

        # Draw module grid
        self.draw_module_grid(40, grid_start_y, grid_width, grid_height)

        # Draw preview panel if active
        if self.show_preview_panel:
            panel_x = grid_width + 60
            panel_width = self.width - panel_x - 40
            self.draw_preview_panel(panel_x, grid_start_y, panel_width, grid_height)

        # Controls footer
        self.draw_controls_footer()

    def draw_module_grid(self, x, y, width, height):
        """Draw 2x3 grid of productivity modules"""
        spacing = 20
        tile_width = (width - spacing) // 2
        tile_height = (height - spacing * 2) // 3

        for idx, module in enumerate(self.MODULES):
            row = idx // 2
            col = idx % 2

            tile_x = x + col * (tile_width + spacing)
            tile_y = y + row * (tile_height + spacing)

            self.draw_module_tile(module, tile_x, tile_y, tile_width, tile_height,
                                 idx == self.selected_module)

    def draw_module_tile(self, module, x, y, width, height, is_selected):
        """Draw a single module tile with huge text"""
        tile_rect = pygame.Rect(x, y, width, height)

        # Background (dimmed if not selected)
        if is_selected:
            bg_color = (35, 40, 60)
        else:
            bg_color = (18, 21, 34)  # 70% dimmed

        pygame.draw.rect(self.screen, bg_color, tile_rect, border_radius=18)

        # Border with glow for selected
        if is_selected:
            # Thick yellow border
            pygame.draw.rect(self.screen, (255, 200, 80), tile_rect,
                           width=5, border_radius=18)
            # Inner glow
            glow_rect = pygame.Rect(x + 6, y + 6, width - 12, height - 12)
            pygame.draw.rect(self.screen, (255, 200, 80), glow_rect,
                           width=2, border_radius=15)
        else:
            pygame.draw.rect(self.screen, (80, 90, 140), tile_rect,
                           width=2, border_radius=18)

        # Content
        content_y = y + 30

        # Icon (centered, big)
        icon_surf = self.font_tile_icon.render(module["icon"], True, (245, 248, 255))
        icon_x = x + (width - icon_surf.get_width()) // 2
        self.screen.blit(icon_surf, (icon_x, content_y))
        content_y += icon_surf.get_height() + 20

        # Module name (centered, HUGE)
        name_surf = self.font_tile_name.render(module["name"], True, (245, 248, 255))
        name_x = x + (width - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, content_y))
        content_y += name_surf.get_height() + 12

        # Sublabel (centered)
        sublabel_surf = self.font_tile_sublabel.render(module["sublabel"], True, (170, 175, 190))
        sublabel_x = x + (width - sublabel_surf.get_width()) // 2
        self.screen.blit(sublabel_surf, (sublabel_x, content_y))
        content_y += sublabel_surf.get_height() + 20

        # Status pill
        self.draw_status_pill(module["status"], x, content_y, width)

    def draw_status_pill(self, status, x, y, tile_width):
        """Draw status pill"""
        pill_text = self.font_status_pill.render(status, True, (255, 255, 255))
        pill_width = pill_text.get_width() + 30
        pill_height = pill_text.get_height() + 12

        pill_x = x + (tile_width - pill_width) // 2
        pill_rect = pygame.Rect(pill_x, y, pill_width, pill_height)

        pygame.draw.rect(self.screen, (60, 200, 100), pill_rect,
                        border_radius=pill_height // 2)

        text_x = pill_x + (pill_width - pill_text.get_width()) // 2
        text_y = y + (pill_height - pill_text.get_height()) // 2
        self.screen.blit(pill_text, (text_x, text_y))

    def draw_preview_panel(self, x, y, width, height):
        """Draw licensing/OEM preview panel with HUGE readable text"""
        # Panel background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (20, 24, 38), panel_rect, border_radius=18)
        pygame.draw.rect(self.screen, (80, 90, 140), panel_rect, width=2, border_radius=18)

        # Content
        content_x = x + 30
        content_y = y + 30

        # Panel headline (HUGE)
        headline = self.font_panel_headline.render("Ambient Workflow Layer", True, (245, 248, 255))
        self.screen.blit(headline, (content_x, content_y))
        content_y += headline.get_height() + 40

        # Section 1: What it enables
        section1 = self.font_panel_bullet.render("What it enables:", True, (245, 248, 255))
        self.screen.blit(section1, (content_x, content_y))
        content_y += section1.get_height() + 20

        enables = [
            "• Focus pacing without screens",
            "• Ambient task awareness",
            "• Meeting presence signals",
            "• Ops & workflow visibility"
        ]

        for bullet in enables:
            bullet_surf = self.font_panel_bullet.render(bullet, True, (170, 175, 190))
            self.screen.blit(bullet_surf, (content_x, content_y))
            content_y += bullet_surf.get_height() + 10

        content_y += 30

        # Section 2: OEM / Partner hooks
        section2 = self.font_panel_bullet.render("OEM / Partner hooks:", True, (245, 248, 255))
        self.screen.blit(section2, (content_x, content_y))
        content_y += section2.get_height() + 20

        hooks = [
            "• White-label ready",
            "• Custom integrations",
            "• Partner API access",
            "• Enterprise deployment"
        ]

        for bullet in hooks:
            bullet_surf = self.font_panel_bullet.render(bullet, True, (170, 175, 190))
            self.screen.blit(bullet_surf, (content_x, content_y))
            content_y += bullet_surf.get_height() + 10

        # Demo script at bottom
        content_y = y + height - 80
        demo_label = self.font_controls.render("Demo script (10 seconds):", True, (245, 248, 255))
        self.screen.blit(demo_label, (content_x, content_y))
        content_y += demo_label.get_height() + 8

        demo_text = self.font_controls.render("Press S to see Focus Sprint", True, (170, 175, 190))
        self.screen.blit(demo_text, (content_x, content_y))

    def draw_demo_overlay(self):
        """Draw full-screen Focus Sprint demo with MASSIVE timer"""
        # Dark overlay
        self.screen.fill((8, 10, 18))

        center_x = self.width // 2
        center_y = self.height // 2

        # Title
        demo_title = self.font_panel_headline.render("FOCUS SPRINT", True, (245, 248, 255))
        title_x = center_x - demo_title.get_width() // 2
        self.screen.blit(demo_title, (title_x, 120))

        # MASSIVE timer (190px font = 160-220px range)
        minutes = self.demo_timer // 60
        seconds = self.demo_timer % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"

        timer_surf = self.font_demo_timer.render(timer_text, True, (255, 200, 80))
        timer_x = center_x - timer_surf.get_width() // 2
        timer_y = center_y - timer_surf.get_height() // 2
        self.screen.blit(timer_surf, (timer_x, timer_y))

        # Status
        if self.demo_paused:
            status_text = "PAUSED"
            status_color = (200, 100, 100)
        else:
            status_text = "ACTIVE"
            status_color = (100, 200, 100)

        status_surf = self.font_panel_bullet.render(status_text, True, status_color)
        status_x = center_x - status_surf.get_width() // 2
        status_y = timer_y + timer_surf.get_height() + 40
        self.screen.blit(status_surf, (status_x, status_y))

        # Calming message
        message = "Ambient pacing cues. No screens required."
        message_surf = self.font_panel_bullet.render(message, True, (170, 175, 190))
        message_x = center_x - message_surf.get_width() // 2
        self.screen.blit(message_surf, (message_x, self.height - 200))

        # Controls
        controls = "SPACE pause/resume  •  R reset  •  ESC exit"
        controls_surf = self.font_controls.render(controls, True, (170, 175, 190))
        controls_x = center_x - controls_surf.get_width() // 2
        self.screen.blit(controls_surf, (controls_x, self.height - 100))

    def draw_controls_footer(self):
        """Draw controls footer with readable text"""
        footer_y = self.height - 70

        # Background bar
        footer_rect = pygame.Rect(0, footer_y, self.width, 70)
        pygame.draw.rect(self.screen, (18, 20, 30), footer_rect)

        # Controls (BIG and readable)
        controls = "← → ↑ ↓ Navigate  |  ENTER Preview  |  S Start Demo  |  ESC Home"
        controls_surf = self.font_controls.render(controls, True, (200, 205, 215))
        controls_x = self.width // 2 - controls_surf.get_width() // 2
        self.screen.blit(controls_surf, (controls_x, footer_y + 18))

        # Disclaimer (single line, readable)
        disclaimer = "Designed for general productivity & workflow awareness."
        disclaimer_surf = self.font_controls.render(disclaimer, True, (140, 145, 160))
        disclaimer_x = self.width // 2 - disclaimer_surf.get_width() // 2
        self.screen.blit(disclaimer_surf, (disclaimer_x, footer_y + 18 + controls_surf.get_height() + 4))

    def run(self):
        """Main loop for Productivity realm"""
        clock = pygame.time.Clock()

        while self.running:
            result = self.handle_input()

            if result == "quit":
                pygame.quit()
                sys.exit(0)
            elif result == "home":
                return  # Return to main grid

            self.update()
            self.draw()
            clock.tick(30)


class MotiBeamOS:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.screen = init_display(width, height)
        self.width = width
        self.height = height

        # Fonts (projection friendly – large)
        self.font_header = pygame.font.SysFont(None, 42)
        self.font_header_meta = pygame.font.SysFont(None, 30)
        self.font_emoji = pygame.font.SysFont(None, 96)  # Increased from 64 to 96px for better visibility
        self.font_card_title = pygame.font.SysFont(None, 34)
        self.font_card_subtitle = pygame.font.SysFont(None, 22)
        self.font_footer = pygame.font.SysFont(None, 24)

        self.clock = pygame.time.Clock()
        self.selected_index = 0  # which card is selected

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
            pygame.quit()
            sys.exit(0)

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

            # Launch Productivity realm if selected
            if realm['name'] == "Productivity":
                productivity = ProductivityRealm(self.screen, self.width, self.height)
                productivity.run()
        elif pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            if idx < len(REALMS):
                self.selected_index = idx

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

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    app = MotiBeamOS(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    app.run()
