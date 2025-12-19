#!/usr/bin/env python3
"""
MotiBeam Spatial OS - Clean Pygame Launcher (Framebuffer-Friendly)

- Uses the same style of framebuffer init as your working test_display.py
- 1920x1080 fullscreen
- 4x3 realm grid
- Big fonts + emojis
- Arrow keys to move selection
- Enter to "select"
- Q or ESC to quit
"""

import os
import sys
import pygame
import requests
import json
from datetime import datetime

# ---------------------------
# Emoji Font Loading with Fallback
# ---------------------------

def load_emoji_font(size=96):
    """
    Load emoji font with graceful fallback.
    Tries NotoColorEmoji first, falls back to default if not available.
    """
    emoji_font_paths = [
        '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
        '/System/Library/Fonts/Apple Color Emoji.ttc',  # macOS
        'C:\\Windows\\Fonts\\seguiemj.ttf',  # Windows
    ]

    for font_path in emoji_font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                pass

    # Fallback to default system font
    return pygame.font.Font(None, size)

# ---------------------------
# Weather Integration
# ---------------------------

def fetch_weather(api_key=None, city="Houston,US"):
    """
    Fetch current weather from OpenWeather API.
    Returns weather description or None if unavailable.
    """
    if not api_key:
        api_key = os.getenv('OPENWEATHER_API_KEY')

    if not api_key:
        return None

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            temp = int(data['main']['temp'])
            description = data['weather'][0]['description'].title()
            return f"{temp}°F • {description}"
    except:
        pass

    return None

# ---------------------------
# Config
# ---------------------------

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
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
    {"name": "CircleBeam", "subtitle": "Family presence", "emoji": "👥"},
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


class MotiBeamOS:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.screen = init_display(width, height)
        self.width = width
        self.height = height

        # Show boot splash screen on projector
        self.show_boot_splash()

        # Fonts (projection friendly – large, 40% larger for 10-15ft viewing)
        # Use system fonts for crisp rendering quality
        self.font_header = pygame.font.SysFont(None, 59)  # Was 42
        self.font_header_meta = pygame.font.SysFont(None, 42)  # Was 30
        self.font_emoji = pygame.font.SysFont(None, 134)  # System font for sharp text
        self.font_card_title = pygame.font.SysFont(None, 48)  # Was 34
        self.font_card_subtitle = pygame.font.SysFont(None, 31)  # Was 22
        self.font_footer = pygame.font.SysFont(None, 34)  # Was 24

        self.clock = pygame.time.Clock()
        self.selected_index = 0  # which card is selected on home grid

        # Navigation system
        self.state = "home"
        self.navigation_stack = ["home"]

        # Realm-specific state data
        self.realm_data = {
            'circlebeam': {'selected': 0, 'action_feedback': None, 'action_time': 0},
            'marketplace': {
                'selected': 0,
                'preview_open': False,
                'installed': set(),   # demo-only, resets on restart
            },
            'home_realm': {
                'selected': 0,
                'temp_changed_time': 0,  # Track last temp change for visual feedback
                'devices': {
                    'living_lights': True,
                    'bedroom_lights': False,
                    'temp': 72,
                    'security': False,
                    'door': True,
                    'garage': False
                }
            },
            'clinical': {'selected': 0},
            'education': {
                'selected': 0,
                'panel_open': False,
                'in_session': False,
                'subject_index': 0,
                'q_index': 0,
                'session_start_time': 0,
                'answered_correctly': False,
                'last_ticker_msg': ''
            },
            'transport': {'selected': 0}
        }

        # Weather integration
        self.weather = None
        self.weather_last_update = 0
        self.fetch_weather_async()

        # Call simulation state
        self.call_active = False
        self.call_caller = {
            'name': 'Mom',
            'emoji': '👩',
            'status': 'Incoming Presence Call',
            'location': 'Home'
        }
        self.missed_presence = False  # Tracks if there's a missed presence notification

        # Alert system (professional features) - shorter messages to prevent overlap
        self.alerts = [
            {'type': 'severe', 'message': 'SEVERE WEATHER - Tornado spotted. Seek shelter immediately', 'color': (255, 80, 80)},
            {'type': 'medical', 'message': '💊 MEDICATION TIME - Take your medication NOW', 'color': (255, 50, 50)},  # Bright red, critical
            {'type': 'message', 'message': 'NEW MESSAGES - 3 unread from CircleBeam', 'color': (100, 180, 255)},
        ]
        self.current_alert_index = 0
        self.alert_change_time = 0
        self.alert_duration = 8  # seconds per alert
        self.alert_enabled = False  # Toggle with 'A' key for simulation
        self.alert_pulse = 0  # For pulsing effect on critical alerts

        # Ticker system (scrolling updates at bottom)
        self.ticker_text = "→ Scheduling CircleBeam → Listing schematica → Missed presence from Dad → Traffic alert: I-45 delay 15min → Weather update: Clear skies → "
        self.ticker_offset = 0
        self.ticker_speed = 2  # pixels per frame

        # System state (ALERT vs CALM)
        self.system_state = "CALM"  # or "ALERT"

        # Precompute grid cell sizes (adjusted for alert banner and ticker)
        self.grid_top = 180  # Was 140, pushed down for alert banner
        self.grid_bottom = self.height - 161  # Adjusted for ticker (60px footer + 56px ticker + 45px margin)
        available_height = self.grid_bottom - self.grid_top
        available_width = self.width - 120

        self.cell_w = available_width // GRID_COLS
        self.cell_h = available_height // GRID_ROWS

    def fetch_weather_async(self):
        """Fetch weather in non-blocking way"""
        import time
        current_time = time.time()

        # Update weather every 10 minutes
        if current_time - self.weather_last_update > 600:
            self.weather = fetch_weather()
            self.weather_last_update = current_time

    def show_boot_splash(self):
        """Show professional boot splash on projector for 2 seconds"""
        # Fill background
        self.screen.fill((15, 20, 30))

        # Create fonts for splash
        logo_font = pygame.font.SysFont(None, 120, bold=True)
        subtitle_font = pygame.font.SysFont(None, 48)
        version_font = pygame.font.SysFont(None, 36)

        # MOTIBEAM text
        moti_text = logo_font.render("MOTIBEAM", True, (100, 180, 255))
        moti_rect = moti_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.screen.blit(moti_text, moti_rect)

        # SPATIAL OS text
        spatial_text = subtitle_font.render("SPATIAL OS", True, (180, 200, 220))
        spatial_rect = spatial_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(spatial_text, spatial_rect)

        # Version and tagline
        version_text = version_font.render("v1.0 • Human-Centered Computing Platform", True, (120, 140, 160))
        version_rect = version_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(version_text, version_rect)

        # Loading bar
        bar_width = 400
        bar_height = 8
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2 + 140

        # Background bar
        pygame.draw.rect(self.screen, (40, 50, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

        # Animated loading bar (slower, more visible)
        for i in range(0, 101, 2):
            fill_width = int(bar_width * i / 100)
            pygame.draw.rect(self.screen, (100, 180, 255), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
            pygame.display.flip()
            pygame.time.wait(30)  # Total animation: 30ms * 50 steps = 1500ms

        # Hold final screen longer for visibility
        pygame.time.wait(2500)  # Total splash time: 1500ms + 2500ms = 4 seconds

    def draw_alert_banner(self):
        """Draw rotating alert banner at top of screen (toggle with 'A' key)"""
        if not self.alert_enabled:
            return  # Don't draw if alerts are disabled

        import time
        import math
        current_time = time.time()

        # Rotate alerts every N seconds
        if current_time - self.alert_change_time > self.alert_duration:
            self.current_alert_index = (self.current_alert_index + 1) % len(self.alerts)
            self.alert_change_time = current_time
            # Update system state based on alert type
            current_alert = self.alerts[self.current_alert_index]
            self.system_state = "ALERT" if current_alert['type'] in ['severe', 'medical'] else "CALM"

        # Draw current alert
        alert = self.alerts[self.current_alert_index]

        # MEDICATION ALERT: Bigger, brighter, pulsing for elderly visibility
        if alert['type'] == 'medical':
            banner_height = 65  # Taller for medication

            # Pulsing effect - brightness oscillates for attention
            self.alert_pulse += 0.15
            pulse = abs(math.sin(self.alert_pulse))
            pulse_brightness = int(150 + (pulse * 105))  # 150-255 brightness
            banner_color = (pulse_brightness, 30, 30)  # Pulsing red

            banner_rect = pygame.Rect(0, 0, self.width, banner_height)
            pygame.draw.rect(self.screen, banner_color, banner_rect)

            # Extra large text for medication
            alert_font = pygame.font.SysFont(None, 48, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 15))
        else:
            # Normal alerts
            banner_height = 45
            banner_rect = pygame.Rect(0, 0, self.width, banner_height)
            pygame.draw.rect(self.screen, alert['color'], banner_rect)

            alert_font = pygame.font.SysFont(None, 32, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 10))

    def draw_state_indicator(self):
        """Draw STATE indicator in top right corner of alert banner"""
        if not self.alert_enabled:
            return  # Don't draw if alerts are disabled

        state_color = (255, 255, 255) if self.system_state == "ALERT" else (255, 255, 255)
        state_font = pygame.font.SysFont(None, 26, bold=True)
        state_text = f"STATE: {self.system_state}"
        state_surf = state_font.render(state_text, True, state_color)
        # Position inside alert banner at far right
        self.screen.blit(state_surf, (self.width - state_surf.get_width() - 15, 12))

    def draw_ticker(self):
        """Draw scrolling ticker above footer"""
        ticker_height = 56  # Increased from 35 for better readability (+60%)
        # Position ticker ABOVE footer (footer is 60px at bottom)
        ticker_y = self.height - 60 - ticker_height

        # Background
        ticker_rect = pygame.Rect(0, ticker_y, self.width, ticker_height)
        pygame.draw.rect(self.screen, (25, 30, 45), ticker_rect)

        # Scrolling text (using system font for crisp rendering)
        ticker_font = pygame.font.SysFont(None, 44)  # Increased from 24 for wall projection (+83%)
        ticker_surf = ticker_font.render(self.ticker_text, True, (180, 200, 220))

        # Update offset for scrolling effect
        self.ticker_offset -= self.ticker_speed
        if self.ticker_offset < -ticker_surf.get_width():
            self.ticker_offset = self.width

        self.screen.blit(ticker_surf, (self.ticker_offset, ticker_y + 12))  # Adjusted vertical centering

    def draw_header(self):
        # Left: title (pushed down to account for alert banner)
        title_text = self.font_header.render("MOTIBEAM SPATIAL OS", True, HEADER_COLOR)
        self.screen.blit(title_text, (40, 75))

        # Right: time + date + weather
        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip("0")
        date_str = now.strftime("%a • %b %d")

        # Weather info
        weather_str = self.weather if self.weather else "Weather: --"

        time_surf = self.font_header_meta.render(time_str, True, HEADER_COLOR)
        date_surf = self.font_header_meta.render(date_str, True, HEADER_COLOR)
        weather_surf = self.font_header_meta.render(weather_str, True, (150, 200, 255))

        tx = self.width - max(time_surf.get_width(), date_surf.get_width(), weather_surf.get_width()) - 40
        ty = 65  # Pushed down to account for alert banner
        self.screen.blit(time_surf, (tx, ty))
        self.screen.blit(date_surf, (tx, ty + time_surf.get_height() + 2))
        self.screen.blit(weather_surf, (tx, ty + time_surf.get_height() + date_surf.get_height() + 4))

    def draw_footer(self):
        # Simple footer strip
        footer_rect = pygame.Rect(0, self.height - 60, self.width, 60)
        pygame.draw.rect(self.screen, (18, 20, 30), footer_rect)

        footer_text = (
            "←↑↓→ Move   |   Enter Select   |   I Incoming Call   |   L Alerts   |   Q / ESC Exit   |   1–9 Quick Jump"
        )
        surf = self.font_footer.render(footer_text, True, FOOTER_COLOR)
        self.screen.blit(
            surf,
            (self.width // 2 - surf.get_width() // 2,
             self.height - 60 + 18),
        )

    def draw_call_overlay(self):
        """Draw incoming presence call overlay (CircleBeam v1.1)"""
        if not self.call_active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((20, 25, 35))
        self.screen.blit(overlay, (0, 0))

        # Call card
        card_width = 640
        card_height = 480
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, (35, 40, 55), card_rect, border_radius=20)
        pygame.draw.rect(self.screen, (100, 180, 255), card_rect, width=4, border_radius=20)

        # Header text
        header_font = pygame.font.SysFont(None, 42, bold=True)
        header_surf = header_font.render('Incoming Presence Call', True, (100, 180, 255))
        header_x = card_x + (card_width - header_surf.get_width()) // 2
        self.screen.blit(header_surf, (header_x, card_y + 30))

        # Caller emoji (large) - use emoji font for proper rendering
        caller_emoji_font = load_emoji_font(180)
        caller_emoji = caller_emoji_font.render(self.call_caller['emoji'], True, (255, 255, 255))
        emoji_x = card_x + (card_width - caller_emoji.get_width()) // 2
        self.screen.blit(caller_emoji, (emoji_x, card_y + 100))

        # Caller name
        name_font = pygame.font.SysFont(None, 72, bold=True)
        name_surf = name_font.render(self.call_caller['name'], True, (255, 255, 255))
        name_x = card_x + (card_width - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, card_y + 260))

        # Subtext
        subtext_font = pygame.font.SysFont(None, 36)
        subtext_surf = subtext_font.render('Tap to connect or dismiss', True, (180, 200, 220))
        subtext_x = card_x + (card_width - subtext_surf.get_width()) // 2
        self.screen.blit(subtext_surf, (subtext_x, card_y + 320))

        # Action buttons
        button_y = card_y + 380

        # Accept button
        accept_rect = pygame.Rect(card_x + 100, button_y, 200, 56)
        pygame.draw.rect(self.screen, (50, 200, 100), accept_rect, border_radius=10)
        accept_font = pygame.font.SysFont(None, 42, bold=True)
        accept_text = accept_font.render('Accept (A)', True, (255, 255, 255))
        accept_x = accept_rect.centerx - accept_text.get_width() // 2
        accept_y = accept_rect.centery - accept_text.get_height() // 2
        self.screen.blit(accept_text, (accept_x, accept_y))

        # Decline button
        decline_rect = pygame.Rect(card_x + 340, button_y, 200, 56)
        pygame.draw.rect(self.screen, (200, 50, 50), decline_rect, border_radius=10)
        decline_font = pygame.font.SysFont(None, 42, bold=True)
        decline_text = decline_font.render('Decline (D)', True, (255, 255, 255))
        decline_x = decline_rect.centerx - decline_text.get_width() // 2
        decline_y = decline_rect.centery - decline_text.get_height() // 2
        self.screen.blit(decline_text, (decline_x, decline_y))

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

            # Emoji icon (134px size) - use emoji font for proper rendering
            emoji_font = load_emoji_font(134)
            icon_surf = emoji_font.render(realm["emoji"], True, TEXT_PRIMARY)
            ex = card_rect.centerx - icon_surf.get_width() // 2
            ey = card_rect.y + 12  # Reduced from 18 to 12 for better vertical centering
            self.screen.blit(icon_surf, (ex, ey))

            # Title
            title_surf = self.font_card_title.render(
                realm["name"], True, TEXT_PRIMARY
            )
            tx = card_rect.centerx - title_surf.get_width() // 2
            ty = ey + icon_surf.get_height() + 8  # Reduced from 10 to 8 for tighter spacing
            self.screen.blit(title_surf, (tx, ty))

            # Subtitle
            subtitle_surf = self.font_card_subtitle.render(
                realm["subtitle"], True, TEXT_SECONDARY
            )
            sx = card_rect.centerx - subtitle_surf.get_width() // 2
            sy = ty + title_surf.get_height() + 4
            self.screen.blit(subtitle_surf, (sx, sy))

            # Missed presence badge for CircleBeam (index 0)
            if i == 0 and self.missed_presence:
                badge_size = 24
                badge_x = card_rect.right - badge_size - 12
                badge_y = card_rect.top + 12
                # Draw badge circle
                pygame.draw.circle(self.screen, (255, 100, 100), (badge_x, badge_y), badge_size // 2)
                # Draw dot emoji in badge
                dot_font = load_emoji_font(16)
                dot_text = dot_font.render('●', True, (255, 255, 255))
                dot_x = badge_x - dot_text.get_width() // 2
                dot_y = badge_y - dot_text.get_height() // 2
                self.screen.blit(dot_text, (dot_x, dot_y))

    def move_selection(self, dx, dy):
        index = self.selected_index
        row = index // GRID_COLS
        col = index % GRID_COLS

        row = max(0, min(GRID_ROWS - 1, row + dy))
        col = max(0, min(GRID_COLS - 1, col + dx))

        new_index = row * GRID_COLS + col
        if new_index < len(REALMS):
            self.selected_index = new_index

    def enter_realm(self, realm_name):
        """Navigate into a realm"""
        self.navigation_stack.append(realm_name)
        self.state = realm_name
        print(f"[NAVIGATE] Entered {realm_name}")

        # Clear missed presence indicator when entering CircleBeam
        if realm_name == 'circlebeam':
            self.missed_presence = False

    def go_back(self):
        """Navigate back one level"""
        if len(self.navigation_stack) > 1:
            self.navigation_stack.pop()
            self.state = self.navigation_stack[-1]
            print(f"[NAVIGATE] Back to {self.state}")
            return True
        return False

    def handle_key(self, key):
        # Q always quits
        if key == pygame.K_q:
            pygame.quit()
            sys.exit(0)

        # ESC behavior depends on current state
        if key == pygame.K_ESCAPE:
            if self.state == "home":
                pygame.quit()
                sys.exit(0)
            else:
                self.go_back()
                return

        # Alert banner toggle (L = toggle aLerts)
        if key == pygame.K_l:
            self.alert_enabled = not self.alert_enabled
            import time
            self.alert_change_time = time.time()  # Reset timer when toggling
            status = "ON" if self.alert_enabled else "OFF"
            print(f"[ALERTS] Alert banner simulation {status}")
            return

        # Call simulation keys (I = incoming, A = accept, D = decline)
        if key == pygame.K_i:
            self.call_active = True
            print("[CALL] Incoming call from " + self.call_caller['name'])
            return

        if key == pygame.K_a and self.call_active:
            print("[PRESENCE] Presence call accepted")
            self.call_active = False
            # Could add ticker message for accepted call if desired
            return

        if key == pygame.K_d and self.call_active:
            print("[PRESENCE] Presence call declined")
            self.call_active = False
            # Add missed presence indicator
            self.missed_presence = True
            # Add ticker message (de-duped to prevent spam)
            missed_msg = f"→ Missed presence from {self.call_caller['name']} → "
            if not self.ticker_text.startswith(missed_msg):
                self.ticker_text = missed_msg + self.ticker_text
            return

        # Route to state-specific handlers
        if self.state == "home":
            self.handle_home_input(key)
        elif self.state == "circlebeam":
            self.handle_circlebeam_input(key)
        elif self.state == "marketplace":
            self.handle_marketplace_input(key)
        elif self.state == "home_realm":
            self.handle_home_realm_input(key)
        elif self.state == "clinical":
            self.handle_clinical_input(key)
        elif self.state == "education":
            self.handle_education_input(key)
        elif self.state == "transport":
            self.handle_transport_input(key)

    def handle_home_input(self, key):
        """Handle input on home grid"""
        if key == pygame.K_LEFT:
            self.move_selection(-1, 0)
        elif key == pygame.K_RIGHT:
            self.move_selection(1, 0)
        elif key == pygame.K_UP:
            self.move_selection(0, -1)
        elif key == pygame.K_DOWN:
            self.move_selection(0, 1)
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            # Map realm index to realm state name
            realm_map = {
                0: "circlebeam",
                3: "marketplace",
                4: "home_realm",
                5: "clinical",
                6: "education",
                8: "transport"
            }
            if self.selected_index in realm_map:
                self.enter_realm(realm_map[self.selected_index])
            else:
                # Show "Coming Soon" for unimplemented realms
                realm = REALMS[self.selected_index]
                print(f"[COMING SOON] {realm['name']} – Not yet implemented")
        elif pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            if idx < len(REALMS):
                self.selected_index = idx

    # ==================== REALM IMPLEMENTATIONS ====================

    def render_circlebeam(self):
        """CircleBeam - Family Presence Layer (v1.1)"""
        selected = self.realm_data['circlebeam']['selected']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)
        title = title_font.render('👥 CIRCLEBEAM', True, (100, 180, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))

        subtitle_font = pygame.font.SysFont(None, 45)
        subtitle = subtitle_font.render('Family Presence', True, (180, 200, 220))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 130))

        # Circle members - presence focused (max 6, showing 5 for demo)
        circles = [
            {'name': 'Mom', 'status': 'available', 'emoji': '👩', 'status_text': 'Available', 'dot': '🟢'},
            {'name': 'Dad', 'status': 'quiet', 'emoji': '👨', 'status_text': 'Quiet mode', 'dot': '🌙'},
            {'name': 'Sister', 'status': 'offline', 'emoji': '👧', 'status_text': 'Offline', 'dot': '⚪'},
            {'name': 'Brother', 'status': 'available', 'emoji': '👦', 'status_text': 'Available', 'dot': '🟢'},
            {'name': 'Grandma', 'status': 'away', 'emoji': '👵', 'status_text': 'Away', 'dot': '⏰'}
        ]

        # Status colors
        status_colors = {
            'available': (100, 255, 150),
            'quiet': (180, 160, 220),
            'offline': (120, 130, 150),
            'away': (255, 200, 100)
        }

        # Card layout - 3 columns, 2 rows for up to 6 members
        card_width = 280
        card_height = 280
        gap = 60
        cols = 3
        rows = 2

        # Center the grid
        grid_width = cols * card_width + (cols - 1) * gap
        start_x = (self.width - grid_width) // 2
        start_y = 220

        for i, circle in enumerate(circles):
            row = i // cols
            col = i % cols

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight if selected
            if i == selected:
                pygame.draw.rect(self.screen, (100, 180, 255), card_rect.inflate(8, 8), 4, border_radius=15)

            # Card background
            pygame.draw.rect(self.screen, (30, 35, 50), card_rect, border_radius=15)

            # Member emoji - use emoji font
            icon_font = load_emoji_font(120)
            icon = icon_font.render(circle['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 30))

            # Name
            name_font = pygame.font.SysFont(None, 52, bold=True)
            name = name_font.render(circle['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 150))

            # Status dot + text
            status_color = status_colors[circle['status']]

            # Status dot emoji
            dot_font = load_emoji_font(36)
            dot = dot_font.render(circle['dot'], True, status_color)

            # Status text
            status_font = pygame.font.SysFont(None, 32)
            status = status_font.render(circle['status_text'], True, status_color)

            # Center the status line (dot + text)
            status_width = dot.get_width() + 8 + status.get_width()
            status_x = x + (card_width - status_width) // 2

            self.screen.blit(dot, (status_x, y + 205))
            self.screen.blit(status, (status_x + dot.get_width() + 8, y + 210))

        # Presence philosophy text
        philosophy_font = pygame.font.SysFont(None, 34)
        philosophy = philosophy_font.render('Presence is shared without requiring interaction.', True, (150, 170, 200))
        self.screen.blit(philosophy, (self.width // 2 - philosophy.get_width() // 2, 830))

        # Help text
        help_font = pygame.font.SysFont(None, 31)
        help_text = help_font.render('← → Navigate | I Incoming | ESC Home', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 880))

    def handle_circlebeam_input(self, key):
        """Handle CircleBeam input - 3 cols × 2 rows grid (5 members)"""
        selected = self.realm_data['circlebeam']['selected']
        total_members = 5
        cols = 3

        # Grid navigation: [0][1][2]
        #                  [3][4]
        if key == pygame.K_LEFT:
            if selected % cols > 0:  # Can move left
                self.realm_data['circlebeam']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % cols < cols - 1 and selected < total_members - 1:  # Can move right
                self.realm_data['circlebeam']['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= cols:  # Can move up
                self.realm_data['circlebeam']['selected'] = selected - cols
        elif key == pygame.K_DOWN:
            if selected + cols < total_members:  # Can move down
                self.realm_data['circlebeam']['selected'] = selected + cols
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            # ENTER just highlights - no action in presence mode
            # This is intentionally minimal - presence, not interaction
            pass

    def render_marketplace(self):
        """Marketplace - Investor-ready PX Store (2 rows × 3 cols, no commerce language)"""
        selected = self.realm_data['marketplace']['selected']
        preview_open = self.realm_data['marketplace']['preview_open']
        installed = self.realm_data['marketplace']['installed']

        # Debug confirmation - Marketplace V2 active
        print("MARKETPLACE V2 ACTIVE")

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)
        title = title_font.render('🛒 MARKETPLACE', True, (180, 100, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        subtitle_font = pygame.font.SysFont(None, 39)
        subtitle = subtitle_font.render('Projection Experiences', True, (200, 180, 255))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 115))

        # PX Database - 6 investor-focused items (2 rows × 3 cols)
        pxs = [
            {
                'emoji': '🌙',
                'name': 'Sleep PX',
                'category': 'Wellness',
                'description': 'Guided relaxation and sleep routines',
                'features': ['Calming visuals', 'Breathing exercises', 'Sleep timer', 'Ambient sounds'],
                'status': 'INSTALLED' if 'Sleep PX' in installed else 'AVAILABLE'
            },
            {
                'emoji': '🎯',
                'name': 'Focus PX',
                'category': 'Productivity',
                'description': 'Distraction-free work environment',
                'features': ['Pomodoro timer', 'Focus music', 'Task tracking', 'Progress visualization'],
                'status': 'INSTALLED' if 'Focus PX' in installed else 'AVAILABLE'
            },
            {
                'emoji': '👨‍👩‍👧',
                'name': 'Family PX',
                'category': 'Social',
                'description': 'Shared experiences for families',
                'features': ['Story time', 'Game night', 'Family calendar', 'Photo memories'],
                'status': 'INSTALLED' if 'Family PX' in installed else 'AVAILABLE'
            },
            {
                'emoji': '📚',
                'name': 'Education PX',
                'category': 'Learning',
                'description': 'Interactive learning experiences',
                'features': ['Language lessons', 'Science demos', 'History tours', 'Math games'],
                'status': 'INSTALLED' if 'Education PX' in installed else 'AVAILABLE'
            },
            {
                'emoji': '🏠',
                'name': 'Home PX',
                'category': 'Lifestyle',
                'description': 'Smart home visualization',
                'features': ['Energy dashboard', 'Device control', 'Security feed', 'Climate zones'],
                'status': 'INSTALLED' if 'Home PX' in installed else 'COMING SOON'
            },
            {
                'emoji': '⭐',
                'name': 'Featured Today',
                'category': 'Special',
                'description': 'Curated daily experiences',
                'features': ['Meditation garden', 'Virtual travel', 'Art gallery', 'Nature sounds'],
                'status': 'COMING SOON'
            }
        ]

        # 2 rows × 3 cols grid layout - larger tiles
        card_width = 380
        card_height = 240
        gap = 40
        start_x = 60
        start_y = 180

        # If preview is open, shift grid left and add preview panel
        if preview_open:
            start_x = 40
            card_width = 320
            gap = 30

        for i, px in enumerate(pxs):
            row = i // 3  # 3 columns per row
            col = i % 3   # columns: 0, 1, 2

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(self.screen, (100, 180, 255), card_rect.inflate(6, 6), 4, border_radius=12)

            pygame.draw.rect(self.screen, (35, 30, 55), card_rect, border_radius=12)

            # PX emoji - use emoji font
            icon_font = load_emoji_font(80)
            icon = icon_font.render(px['emoji'], True, (100, 200, 255))
            self.screen.blit(icon, (x + 20, y + 20))

            # PX name
            name_font = pygame.font.SysFont(None, 48, bold=True)
            name = name_font.render(px['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + 110, y + 30))

            # Category
            cat_font = pygame.font.SysFont(None, 30)
            cat = cat_font.render(px['category'], True, (180, 160, 200))
            self.screen.blit(cat, (x + 110, y + 65))

            # Description (shorter for compact view)
            desc_font = pygame.font.SysFont(None, 26)
            desc = desc_font.render(px['description'][:45] + '...', True, (150, 150, 170))
            self.screen.blit(desc, (x + 20, y + 130))

            # Status badge
            status = px['status']
            if status == 'INSTALLED':
                badge_color = (100, 255, 150)
                badge_bg = (20, 80, 40)
            elif status == 'COMING SOON':
                badge_color = (255, 200, 100)
                badge_bg = (80, 60, 20)
            else:  # AVAILABLE
                badge_color = (100, 180, 255)
                badge_bg = (20, 40, 80)

            badge_font = pygame.font.SysFont(None, 28, bold=True)
            badge_text = badge_font.render(status, True, badge_color)
            badge_rect = pygame.Rect(x + 20, y + 180, badge_text.get_width() + 20, 35)
            pygame.draw.rect(self.screen, badge_bg, badge_rect, border_radius=6)
            self.screen.blit(badge_text, (x + 30, y + 187))

        # Preview panel on right side
        if preview_open:
            selected_px = pxs[selected]
            panel_x = 740
            panel_y = 180
            panel_width = 1120
            panel_height = 800

            # Panel background
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (25, 25, 45), panel_rect, border_radius=12)
            pygame.draw.rect(self.screen, (100, 180, 255), panel_rect, 3, border_radius=12)

            # Preview header
            preview_title_font = pygame.font.SysFont(None, 56, bold=True)
            preview_emoji_font = load_emoji_font(70)

            preview_emoji = preview_emoji_font.render(selected_px['emoji'], True, (100, 200, 255))
            self.screen.blit(preview_emoji, (panel_x + 30, panel_y + 30))

            preview_title = preview_title_font.render(selected_px['name'], True, (255, 255, 255))
            self.screen.blit(preview_title, (panel_x + 120, panel_y + 40))

            # Category
            preview_cat_font = pygame.font.SysFont(None, 34)
            preview_cat = preview_cat_font.render(selected_px['category'], True, (180, 160, 200))
            self.screen.blit(preview_cat, (panel_x + 120, panel_y + 85))

            # Description
            preview_desc_font = pygame.font.SysFont(None, 36)
            preview_desc = preview_desc_font.render(selected_px['description'], True, (200, 200, 220))
            self.screen.blit(preview_desc, (panel_x + 30, panel_y + 160))

            # Features list
            features_label_font = pygame.font.SysFont(None, 40, bold=True)
            features_label = features_label_font.render('Features:', True, (100, 180, 255))
            self.screen.blit(features_label, (panel_x + 30, panel_y + 230))

            feature_font = pygame.font.SysFont(None, 32)
            for i, feature in enumerate(selected_px['features']):
                feature_text = feature_font.render(f'• {feature}', True, (180, 180, 200))
                self.screen.blit(feature_text, (panel_x + 50, panel_y + 290 + i * 50))

            # Status badge in preview
            status_label_font = pygame.font.SysFont(None, 40, bold=True)
            status_label = status_label_font.render('Status:', True, (100, 180, 255))
            self.screen.blit(status_label, (panel_x + 30, panel_y + 520))

            status = selected_px['status']
            if status == 'INSTALLED':
                status_color = (100, 255, 150)
                status_bg = (20, 80, 40)
            elif status == 'COMING SOON':
                status_color = (255, 200, 100)
                status_bg = (80, 60, 20)
            else:
                status_color = (100, 180, 255)
                status_bg = (20, 40, 80)

            status_font = pygame.font.SysFont(None, 38, bold=True)
            status_text = status_font.render(status, True, status_color)
            status_rect = pygame.Rect(panel_x + 30, panel_y + 580, status_text.get_width() + 30, 45)
            pygame.draw.rect(self.screen, status_bg, status_rect, border_radius=8)
            self.screen.blit(status_text, (panel_x + 45, panel_y + 590))

            # Demo install hint
            if status == 'AVAILABLE':
                hint_font = pygame.font.SysFont(None, 32)
                hint_text = hint_font.render('Press D to demo install', True, (100, 180, 255))
                self.screen.blit(hint_text, (panel_x + 30, panel_y + 680))

        # Footer help
        help_font = pygame.font.SysFont(None, 28)
        if preview_open:
            help_text = help_font.render('← → Navigate | B Back to Grid | D Demo Install', True, (150, 160, 180))
        else:
            help_text = help_font.render('← → Navigate | Enter Preview | B Back | D Demo Install', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 1000))

        # Debug indicator - Marketplace v2
        debug_font = pygame.font.SysFont(None, 24)
        debug_text = debug_font.render('Marketplace v2', True, (80, 100, 120))
        self.screen.blit(debug_text, (10, self.height - 30))

    def handle_marketplace_input(self, key):
        """Handle Marketplace input - 2 rows × 3 cols grid with preview panel"""
        selected = self.realm_data['marketplace']['selected']
        preview_open = self.realm_data['marketplace']['preview_open']
        installed = self.realm_data['marketplace']['installed']

        # PX names for reference (matches order in pxs list)
        px_names = ['Sleep PX', 'Focus PX', 'Family PX', 'Education PX', 'Home PX', 'Featured Today']
        total_pxs = 6  # 2 rows × 3 cols = 6 tiles
        cols = 3
        rows = 2

        # Navigation (works in both grid and preview modes)
        # Grid layout: [0][1][2]
        #              [3][4][5]
        if key == pygame.K_LEFT:
            if selected % cols > 0:  # Can move left (not in leftmost column)
                self.realm_data['marketplace']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % cols < cols - 1 and selected < total_pxs - 1:  # Can move right
                self.realm_data['marketplace']['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= cols:  # Can move up (not in top row)
                self.realm_data['marketplace']['selected'] = selected - cols
        elif key == pygame.K_DOWN:
            if selected + cols < total_pxs:  # Can move down (not in bottom row)
                self.realm_data['marketplace']['selected'] = selected + cols

        # Toggle preview panel
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self.realm_data['marketplace']['preview_open'] = not preview_open

        # Back button - close preview if open, otherwise go back to home
        elif key == pygame.K_b:
            if preview_open:
                self.realm_data['marketplace']['preview_open'] = False
            # If preview is closed, ESC will handle going back to home

        # Demo install with 'D' key
        elif key == pygame.K_d:
            selected_px = px_names[selected]
            # Only install if AVAILABLE (not already installed or coming soon)
            if selected_px not in installed and selected_px != 'Featured Today':
                installed.add(selected_px)
                # Update ticker with install message
                install_msg = f"→ Installing {selected_px}... → {selected_px} installed successfully! → "
                self.ticker_text = install_msg + self.ticker_text
                print(f"[MARKETPLACE] Demo install: {selected_px}")

    def render_home_realm(self):
        """Home - Ambient Control (polished for wall projection)"""
        selected = self.realm_data['home_realm']['selected']
        devices_state = self.realm_data['home_realm']['devices']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)
        title = title_font.render('🏠 HOME', True, (100, 255, 150))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 42)
        subtitle = subtitle_font.render('Calm Home Awareness', True, (180, 220, 200))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 120))

        # Device configurations
        devices = [
            {'id': 'living_lights', 'emoji': '💡', 'name': 'Living Room', 'type': 'toggle'},
            {'id': 'bedroom_lights', 'emoji': '🛏️', 'name': 'Bedroom', 'type': 'toggle'},
            {'id': 'temp', 'emoji': '🌡️', 'name': 'Thermostat', 'type': 'adjust'},
            {'id': 'security', 'emoji': '🛡️', 'name': 'Security', 'type': 'toggle'},
            {'id': 'door', 'emoji': '🚪', 'name': 'Front Door', 'type': 'toggle'},
            {'id': 'garage', 'emoji': '🚗', 'name': 'Garage', 'type': 'toggle'}
        ]

        card_width = 280
        card_height = 230
        gap = 40
        start_x = 120
        start_y = 200

        for i, device in enumerate(devices):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Get device state
            state = devices_state[device['id']]

            # Background color - dimmed for unselected
            if device['type'] == 'toggle':
                bg_color = (50, 100, 50) if state else (50, 50, 60)
            else:  # adjust (thermostat)
                bg_color = (60, 80, 120)

            # Dim unselected tiles
            if i != selected:
                bg_color = tuple(int(c * 0.7) for c in bg_color)

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)

            # Selection styling - thicker outline with subtle glow
            if i == selected:
                # Outer glow
                pygame.draw.rect(self.screen, (100, 255, 150, 80), card_rect.inflate(12, 12), 6, border_radius=18)
                # Main border
                pygame.draw.rect(self.screen, (100, 255, 150), card_rect.inflate(6, 6), 4, border_radius=15)

            # Emoji - use emoji font
            icon_font = load_emoji_font(110)
            icon = icon_font.render(device['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 15))

            # Device name - larger and bolder
            name_font = pygame.font.SysFont(None, 52, bold=True)
            name = name_font.render(device['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 105))

            # Status pill at bottom
            pill_y = y + card_height - 40

            if device['type'] == 'toggle':
                # Status pill - use OPEN/CLOSED for door/garage, ON/OFF for others
                is_door_or_garage = device['id'] in ['door', 'garage']

                if state:
                    pill_text = 'OPEN' if is_door_or_garage else 'ON'
                    pill_bg = (50, 180, 80)
                    pill_fg = (255, 255, 255)
                else:
                    pill_text = 'CLOSED' if is_door_or_garage else 'OFF'
                    pill_bg = (60, 70, 85)
                    pill_fg = (160, 170, 180)

                pill_font = pygame.font.SysFont(None, 36, bold=True)
                pill_surf = pill_font.render(pill_text, True, pill_fg)
                pill_width = pill_surf.get_width() + 30
                pill_height = 32
                pill_x = x + (card_width - pill_width) // 2
                pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)

                pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=16)
                self.screen.blit(pill_surf, (pill_x + 15, pill_y + 6))

            else:  # Thermostat - special display
                # Large temperature
                temp_font = pygame.font.SysFont(None, 64, bold=True)
                temp_surf = temp_font.render(f"{state}°F", True, (100, 200, 255))
                temp_x = x + card_width // 2 - temp_surf.get_width() // 2
                temp_y = y + 145
                self.screen.blit(temp_surf, (temp_x, temp_y))

                # Micro-feedback: brief pulse when temp changes
                import time
                temp_changed_time = self.realm_data['home_realm']['temp_changed_time']
                time_since_change = time.time() - temp_changed_time
                pulse_duration = 0.6  # 600ms pulse

                if time_since_change < pulse_duration:
                    # Fade out glow over pulse duration
                    fade_progress = time_since_change / pulse_duration
                    alpha = int(120 * (1 - fade_progress))  # Fade from 120 to 0

                    # Draw subtle glow around temperature
                    glow_rect = pygame.Rect(temp_x - 10, temp_y - 5, temp_surf.get_width() + 20, temp_surf.get_height() + 10)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    glow_surface.fill((100, 200, 255, alpha))
                    self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y))

                    # Re-draw temperature on top of glow
                    self.screen.blit(temp_surf, (temp_x, temp_y))

                # Mode pill
                mode_text = 'AUTO'
                pill_bg = (40, 80, 120)
                pill_fg = (150, 200, 255)

                pill_font = pygame.font.SysFont(None, 30, bold=True)
                pill_surf = pill_font.render(mode_text, True, pill_fg)
                pill_width = pill_surf.get_width() + 24
                pill_height = 28
                pill_x = x + (card_width - pill_width) // 2
                pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)

                pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=14)
                self.screen.blit(pill_surf, (pill_x + 12, pill_y + 4))

        # Help text - changes based on thermostat selection
        help_font = pygame.font.SysFont(None, 30)
        if devices[selected]['type'] == 'adjust':
            # Thermostat selected - show temperature controls
            help_text = help_font.render('↑ ↓ Navigate   |   ← → Adjust Temp   |   ESC Back', True, (150, 160, 180))
        else:
            # Regular device selected
            help_text = help_font.render('← → ↑ ↓ Navigate   |   Enter Toggle   |   ESC Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 880))

    def handle_home_realm_input(self, key):
        """Handle Home realm input with thermostat LEFT/RIGHT controls"""
        selected = self.realm_data['home_realm']['selected']
        devices_state = self.realm_data['home_realm']['devices']

        device_ids = ['living_lights', 'bedroom_lights', 'temp', 'security', 'door', 'garage']
        device_names = ['Living Room Lights', 'Bedroom Lights', 'Thermostat', 'Security System', 'Front Door Lock', 'Garage Door']

        # Special handling for thermostat (index 2)
        is_thermostat_selected = (selected == 2)

        if key == pygame.K_LEFT:
            if is_thermostat_selected:
                # Decrease temperature
                import time
                current_temp = devices_state['temp']
                new_temp = max(60, current_temp - 1)
                if new_temp != current_temp:  # Only update if temp actually changed
                    devices_state['temp'] = new_temp
                    self.realm_data['home_realm']['temp_changed_time'] = time.time()
                print(f"[HOME] Thermostat adjusted to {devices_state['temp']}°F")
            elif selected % 3 > 0:
                # Navigate left
                self.realm_data['home_realm']['selected'] = selected - 1

        elif key == pygame.K_RIGHT:
            if is_thermostat_selected:
                # Increase temperature
                import time
                current_temp = devices_state['temp']
                new_temp = min(85, current_temp + 1)
                if new_temp != current_temp:  # Only update if temp actually changed
                    devices_state['temp'] = new_temp
                    self.realm_data['home_realm']['temp_changed_time'] = time.time()
                print(f"[HOME] Thermostat adjusted to {devices_state['temp']}°F")
            elif selected % 3 < 2 and selected < 5:
                # Navigate right
                self.realm_data['home_realm']['selected'] = selected + 1

        elif key == pygame.K_UP:
            if selected >= 3:
                self.realm_data['home_realm']['selected'] = selected - 3

        elif key == pygame.K_DOWN:
            if selected < 3:
                self.realm_data['home_realm']['selected'] = selected + 3

        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            device_id = device_ids[selected]
            if device_id == 'temp':
                # For thermostat, ENTER does nothing (temp controlled by LEFT/RIGHT)
                # Could add mode toggle here if desired, but keeping it simple
                print(f"[HOME] Thermostat: Use ← → to adjust temperature")
            else:
                # Toggle device
                devices_state[device_id] = not devices_state[device_id]
                state_str = "ON" if devices_state[device_id] else "OFF"
                print(f"[HOME] {device_names[selected]} turned {state_str}")

    def render_clinical(self):
        """Clinical - Health monitoring dashboard"""
        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('🏥 CLINICAL MONITOR', True, (255, 120, 140))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 35))

        # === VITALS SECTION ===
        vitals_y = 100
        vitals = [
            {'emoji': '❤️', 'label': 'Heart Rate', 'value': '72 bpm', 'color': (100, 255, 150)},
            {'emoji': '🩸', 'label': 'Blood Pressure', 'value': '120/80', 'color': (100, 255, 150)},
            {'emoji': '🫁', 'label': 'O2 Saturation', 'value': '98%', 'color': (100, 255, 150)},
            {'emoji': '🌡️', 'label': 'Temperature', 'value': '98.6°F', 'color': (100, 255, 150)}
        ]

        vital_width = 220
        vital_gap = 20
        vital_start_x = self.width // 2 - (4 * vital_width + 3 * vital_gap) // 2

        for i, vital in enumerate(vitals):
            x = vital_start_x + i * (vital_width + vital_gap)
            card_rect = pygame.Rect(x, vitals_y, vital_width, 85)
            pygame.draw.rect(self.screen, (25, 30, 40), card_rect, border_radius=10)

            # Emoji - use emoji font
            icon_font = load_emoji_font(56)
            icon = icon_font.render(vital['emoji'], True, vital['color'])
            self.screen.blit(icon, (x + 10, vitals_y + 10))

            # Label
            label_font = pygame.font.SysFont(None, 25)  # Was 18
            label = label_font.render(vital['label'], True, (180, 190, 200))
            self.screen.blit(label, (x + 65, vitals_y + 15))

            # Value
            value_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
            value = value_font.render(vital['value'], True, vital['color'])
            self.screen.blit(value, (x + 65, vitals_y + 45))

        # === MEDICATION SECTION ===
        med_y = 220
        med_title_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
        med_title = med_title_font.render('Medication Schedule', True, (200, 210, 220))
        self.screen.blit(med_title, (50, med_y))

        medications = [
            {'name': 'Metformin', 'dose': '500mg', 'time': '08:00 AM', 'taken': True},
            {'name': 'Lisinopril', 'dose': '10mg', 'time': '08:00 AM', 'taken': True},
            {'name': 'Metformin', 'dose': '500mg', 'time': '06:00 PM', 'taken': False},
            {'name': 'Atorvastatin', 'dose': '20mg', 'time': '09:00 PM', 'taken': False}
        ]

        for i, med in enumerate(medications):
            y = med_y + 45 + i * 45

            # Status emoji - use emoji font
            status_icon = '✅' if med['taken'] else '⏰'
            icon_font = load_emoji_font(39)
            icon_color = (100, 255, 100) if med['taken'] else (150, 150, 150)
            icon = icon_font.render(status_icon, True, icon_color)
            self.screen.blit(icon, (70, y))

            # Med name
            name_font = pygame.font.SysFont(None, 39, bold=True)  # Was 28
            name = name_font.render(med['name'], True, (255, 255, 255))
            self.screen.blit(name, (110, y))

            # Dose
            dose_font = pygame.font.SysFont(None, 31)  # Was 22
            dose = dose_font.render(med['dose'], True, (180, 200, 220))
            self.screen.blit(dose, (260, y + 4))

            # Time
            time_font = pygame.font.SysFont(None, 34)  # Was 24
            time_surf = time_font.render(med['time'], True, (100, 180, 255))
            self.screen.blit(time_surf, (360, y + 2))

        # === CDI SECTION ===
        cdi_y = 480
        cdi_title_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
        cdi_title = cdi_title_font.render('Clinical Deterioration Index', True, (200, 210, 220))
        self.screen.blit(cdi_title, (50, cdi_y))

        # CDI Score (Low risk = 2)
        cdi_score = 2
        cdi_status = 'LOW RISK'
        cdi_color = (100, 255, 100)
        cdi_emoji = '✅'

        cdi_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        cdi_display = cdi_font.render(f'{cdi_emoji} {cdi_status}', True, cdi_color)
        self.screen.blit(cdi_display, (50, cdi_y + 45))

        # Guardian contact button
        guardian_btn = pygame.Rect(550, cdi_y + 35, 400, 70)
        pygame.draw.rect(self.screen, (50, 100, 200), guardian_btn, border_radius=12)
        btn_font = pygame.font.SysFont(None, 50, bold=True)  # Was 36
        btn_text = btn_font.render('📞 Contact Guardian', True, (255, 255, 255))
        self.screen.blit(btn_text, (guardian_btn.centerx - btn_text.get_width() // 2, guardian_btn.centery - 18))

        # === CHART VISUALIZATION (simple bars) ===
        chart_y = 600
        chart_title_font = pygame.font.SysFont(None, 34, bold=True)  # Was 24
        chart_title = chart_title_font.render('24-Hour Vital Trends', True, (180, 190, 200))
        self.screen.blit(chart_title, (50, chart_y))

        # Simple bar chart representation
        bars = [75, 80, 72, 68, 71, 73, 75, 72]  # Heart rate trend
        bar_width = 40
        bar_gap = 15
        bar_start_x = 60

        for i, height in enumerate(bars):
            x = bar_start_x + i * (bar_width + bar_gap)
            bar_height = int(height * 0.8)  # Scale for display
            bar_rect = pygame.Rect(x, chart_y + 80 - bar_height, bar_width, bar_height)
            pygame.draw.rect(self.screen, (100, 180, 255), bar_rect, border_radius=4)

        # Help
        help_font = pygame.font.SysFont(None, 28)  # Was 20
        help_text = help_font.render('ESC: Back to Home', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 735))

    def handle_clinical_input(self, key):
        """Handle Clinical input (read-only for demo)"""
        # Clinical is a dashboard view - no interactive elements needed for demo
        pass

    def get_education_questions(self):
        """Get hardcoded Q&A content for each subject"""
        return {
            0: [  # Mathematics
                {'q': 'What is 7 × 8?', 'a': '56', 'b': '54', 'c': '64', 'correct': 'a'},
                {'q': 'What is 15 + 27?', 'a': '41', 'b': '42', 'c': '43', 'correct': 'b'},
                {'q': 'What is 100 - 37?', 'a': '73', 'b': '63', 'c': '67', 'correct': 'b'}
            ],
            1: [  # Reading
                {'q': 'A synonym for "happy" is:', 'a': 'Sad', 'b': 'Joyful', 'c': 'Angry', 'correct': 'b'},
                {'q': 'Which is a noun?', 'a': 'Run', 'b': 'Quickly', 'c': 'Table', 'correct': 'c'},
                {'q': 'An antonym for "hot" is:', 'a': 'Warm', 'b': 'Cold', 'c': 'Sunny', 'correct': 'b'}
            ],
            2: [  # Science
                {'q': 'Water freezes at:', 'a': '0°C', 'b': '100°C', 'c': '50°C', 'correct': 'a'},
                {'q': 'Plants make food using:', 'a': 'Soil', 'b': 'Sunlight', 'c': 'Wind', 'correct': 'b'},
                {'q': 'Earth has how many moons?', 'a': 'Two', 'b': 'None', 'c': 'One', 'correct': 'c'}
            ],
            3: [  # History
                {'q': 'Who invented the lightbulb?', 'a': 'Tesla', 'b': 'Edison', 'c': 'Bell', 'correct': 'b'},
                {'q': 'The Great Wall is in:', 'a': 'Japan', 'b': 'India', 'c': 'China', 'correct': 'c'},
                {'q': 'First man on the moon:', 'a': 'Armstrong', 'b': 'Aldrin', 'c': 'Collins', 'correct': 'a'}
            ],
            4: [  # Geography
                {'q': 'Largest ocean:', 'a': 'Atlantic', 'b': 'Pacific', 'c': 'Indian', 'correct': 'b'},
                {'q': 'Capital of France:', 'a': 'London', 'b': 'Berlin', 'c': 'Paris', 'correct': 'c'},
                {'q': 'How many continents?', 'a': 'Five', 'b': 'Six', 'c': 'Seven', 'correct': 'c'}
            ],
            5: [  # Creative/Art
                {'q': 'Primary colors include:', 'a': 'Green', 'b': 'Red', 'c': 'Purple', 'correct': 'b'},
                {'q': 'Who painted Mona Lisa?', 'a': 'Picasso', 'b': 'Da Vinci', 'c': 'Monet', 'correct': 'b'},
                {'q': 'A sculpture is:', 'a': '2D art', 'b': '3D art', 'c': 'Music', 'correct': 'b'}
            ]
        }

    def render_education(self):
        """Education v1.0 - Interactive learning sessions with Q&A"""
        selected = self.realm_data['education']['selected']
        panel_open = self.realm_data['education']['panel_open']
        in_session = self.realm_data['education']['in_session']

        # Subject definitions
        subjects = [
            {'emoji': '🔢', 'name': 'Mathematics', 'desc': 'Math practice and problem solving'},
            {'emoji': '📖', 'name': 'Reading', 'desc': 'Vocabulary and comprehension'},
            {'emoji': '🔬', 'name': 'Science', 'desc': 'Science facts and concepts'},
            {'emoji': '🏛️', 'name': 'History', 'desc': 'Historical events and figures'},
            {'emoji': '🌍', 'name': 'Geography', 'desc': 'World geography and landmarks'},
            {'emoji': '🎨', 'name': 'Creative', 'desc': 'Art and creative thinking'}
        ]

        # If in session mode, show full overlay
        if in_session:
            self._render_education_session(subjects)
            return

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)
        title = title_font.render('📚 EDUCATION', True, (255, 180, 50))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 45))

        subtitle_font = pygame.font.SysFont(None, 42)
        subtitle = subtitle_font.render('Interactive Learning Sessions', True, (220, 200, 150))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 110))

        # 2×3 grid layout
        card_width = 320 if panel_open else 380
        card_height = 240
        gap = 30 if panel_open else 40
        start_x = 40 if panel_open else 60
        start_y = 200

        for i, subject in enumerate(subjects):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Background - dimmed if not selected
            bg_color = (30, 35, 50)
            if i != selected:
                bg_color = tuple(int(c * 0.7) for c in bg_color)

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)

            # Selection styling
            if i == selected:
                pygame.draw.rect(self.screen, (255, 180, 50, 80), card_rect.inflate(12, 12), 6, border_radius=18)
                pygame.draw.rect(self.screen, (255, 180, 50), card_rect.inflate(6, 6), 4, border_radius=15)

            # Emoji
            icon_font = load_emoji_font(100)
            icon = icon_font.render(subject['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 20))

            # Subject name
            name_font = pygame.font.SysFont(None, 52, bold=True)
            name = name_font.render(subject['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 120))

            # "Start Session" pill
            pill_text = 'Start Session'
            pill_font = pygame.font.SysFont(None, 30, bold=True)
            pill_surf = pill_font.render(pill_text, True, (180, 220, 180))
            pill_width = pill_surf.get_width() + 24
            pill_height = 28
            pill_x = x + (card_width - pill_width) // 2
            pill_y = y + card_height - 45
            pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)

            pygame.draw.rect(self.screen, (40, 80, 40), pill_rect, border_radius=14)
            self.screen.blit(pill_surf, (pill_x + 12, pill_y + 4))

        # Preview panel (right side)
        if panel_open:
            selected_subject = subjects[selected]
            panel_x = 1040
            panel_y = 180
            panel_width = 820
            panel_height = 800

            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (25, 25, 45), panel_rect, border_radius=12)
            pygame.draw.rect(self.screen, (255, 180, 50), panel_rect, 3, border_radius=12)

            # Panel header
            preview_emoji_font = load_emoji_font(70)
            preview_emoji = preview_emoji_font.render(selected_subject['emoji'], True, (255, 180, 50))
            self.screen.blit(preview_emoji, (panel_x + 30, panel_y + 30))

            preview_title_font = pygame.font.SysFont(None, 56, bold=True)
            preview_title = preview_title_font.render(selected_subject['name'], True, (255, 255, 255))
            self.screen.blit(preview_title, (panel_x + 120, panel_y + 40))

            # Description
            desc_font = pygame.font.SysFont(None, 34)
            desc = desc_font.render(selected_subject['desc'], True, (200, 200, 220))
            self.screen.blit(desc, (panel_x + 30, panel_y + 120))

            # "Today's Session"
            session_label_font = pygame.font.SysFont(None, 40, bold=True)
            session_label = session_label_font.render("Today's Session:", True, (255, 180, 50))
            self.screen.blit(session_label, (panel_x + 30, panel_y + 200))

            # What you'll do bullets
            bullet_font = pygame.font.SysFont(None, 32)
            bullets = [
                '• Answer 3 questions',
                '• Test your knowledge',
                '• Track your progress'
            ]
            for i, bullet in enumerate(bullets):
                bullet_surf = bullet_font.render(bullet, True, (180, 180, 200))
                self.screen.blit(bullet_surf, (panel_x + 50, panel_y + 270 + i * 50))

            # Start hint
            start_font = pygame.font.SysFont(None, 48, bold=True)
            start_text = start_font.render('Press S to Start', True, (180, 220, 180))
            self.screen.blit(start_text, (panel_x + 30, panel_y + 500))

            # Close hint
            close_font = pygame.font.SysFont(None, 32)
            close_text = close_font.render('Press B to close panel', True, (150, 160, 180))
            self.screen.blit(close_text, (panel_x + 30, panel_y + 680))

        # Help text
        help_font = pygame.font.SysFont(None, 30)
        if panel_open:
            help_text = help_font.render('S Start | B Back | ESC Home', True, (150, 160, 180))
        else:
            help_text = help_font.render('← → ↑ ↓ Navigate | ENTER Preview | ESC Home', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 880))

    def _render_education_session(self, subjects):
        """Render the Q&A session overlay"""
        subject_index = self.realm_data['education']['subject_index']
        q_index = self.realm_data['education']['q_index']
        session_start_time = self.realm_data['education']['session_start_time']
        answered_correctly = self.realm_data['education']['answered_correctly']

        subject = subjects[subject_index]
        questions = self.get_education_questions()
        current_q = questions[subject_index][q_index]

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(220)
        overlay.fill((15, 20, 30))
        self.screen.blit(overlay, (0, 0))

        # Session card
        card_width = 1200
        card_height = 700
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, (35, 40, 55), card_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 180, 50), card_rect, 4, border_radius=20)

        # Subject header
        header_emoji_font = load_emoji_font(60)
        header_emoji = header_emoji_font.render(subject['emoji'], True, (255, 180, 50))
        self.screen.blit(header_emoji, (card_x + 40, card_y + 30))

        header_font = pygame.font.SysFont(None, 56, bold=True)
        header_text = header_font.render(subject['name'], True, (255, 255, 255))
        self.screen.blit(header_text, (card_x + 120, card_y + 40))

        # Timer
        import time
        elapsed = int(time.time() - session_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_font = pygame.font.SysFont(None, 40)
        timer_text = timer_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (180, 200, 220))
        self.screen.blit(timer_text, (card_x + card_width - 200, card_y + 45))

        # Progress indicator
        progress_font = pygame.font.SysFont(None, 36)
        progress_text = progress_font.render(f"Question {q_index + 1}/3", True, (200, 200, 220))
        self.screen.blit(progress_text, (card_x + 40, card_y + 110))

        # Question
        question_font = pygame.font.SysFont(None, 52, bold=True)
        question_text = question_font.render(current_q['q'], True, (255, 255, 255))
        self.screen.blit(question_text, (card_x + 40, card_y + 200))

        # Answer options
        answers = [
            {'key': 'A', 'text': current_q['a'], 'y_offset': 0},
            {'key': 'B', 'text': current_q['b'], 'y_offset': 100},
            {'key': 'C', 'text': current_q['c'], 'y_offset': 200}
        ]

        for answer in answers:
            ans_y = card_y + 300 + answer['y_offset']
            ans_rect = pygame.Rect(card_x + 60, ans_y, card_width - 120, 70)

            pygame.draw.rect(self.screen, (50, 55, 70), ans_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 110, 130), ans_rect, 2, border_radius=10)

            key_font = pygame.font.SysFont(None, 48, bold=True)
            key_text = key_font.render(answer['key'], True, (255, 180, 50))
            self.screen.blit(key_text, (ans_rect.x + 20, ans_rect.y + 18))

            ans_font = pygame.font.SysFont(None, 42)
            ans_text = ans_font.render(answer['text'], True, (255, 255, 255))
            self.screen.blit(ans_text, (ans_rect.x + 80, ans_rect.y + 20))

        # Feedback (if answered)
        if answered_correctly:
            feedback_font = pygame.font.SysFont(None, 48, bold=True)
            feedback_text = feedback_font.render('Correct! ✅ Press N for next', True, (100, 255, 150))
            self.screen.blit(feedback_text, (card_x + 40, card_y + 620))

        # Controls hint
        controls_font = pygame.font.SysFont(None, 32)
        if not answered_correctly:
            controls_text = controls_font.render('A/B/C Answer | ESC Exit', True, (150, 160, 180))
        else:
            controls_text = controls_font.render('N Next | ESC Exit', True, (150, 160, 180))
        self.screen.blit(controls_text, (card_x + card_width - 400, card_y + 620))

    def handle_education_input(self, key):
        """Handle Education input - grid, panel, session modes"""
        selected = self.realm_data['education']['selected']
        panel_open = self.realm_data['education']['panel_open']
        in_session = self.realm_data['education']['in_session']

        subject_names = ['Mathematics', 'Reading', 'Science', 'History', 'Geography', 'Creative']

        # Session mode controls
        if in_session:
            q_index = self.realm_data['education']['q_index']
            subject_index = self.realm_data['education']['subject_index']
            answered_correctly = self.realm_data['education']['answered_correctly']
            questions = self.get_education_questions()
            current_q = questions[subject_index][q_index]

            # Answer selection (A/B/C)
            if not answered_correctly:
                if key == pygame.K_a:
                    if current_q['correct'] == 'a':
                        self.realm_data['education']['answered_correctly'] = True
                        print("[EDUCATION] Correct answer!")
                    else:
                        print("[EDUCATION] Try again")
                elif key == pygame.K_b:
                    if current_q['correct'] == 'b':
                        self.realm_data['education']['answered_correctly'] = True
                        print("[EDUCATION] Correct answer!")
                    else:
                        print("[EDUCATION] Try again")
                elif key == pygame.K_c:
                    if current_q['correct'] == 'c':
                        self.realm_data['education']['answered_correctly'] = True
                        print("[EDUCATION] Correct answer!")
                    else:
                        print("[EDUCATION] Try again")

            # Next question (N)
            elif key == pygame.K_n:
                if q_index < 2:
                    # Move to next question
                    self.realm_data['education']['q_index'] = q_index + 1
                    self.realm_data['education']['answered_correctly'] = False
                    print(f"[EDUCATION] Question {q_index + 2}/3")
                else:
                    # Session complete
                    import time
                    elapsed = int(time.time() - self.realm_data['education']['session_start_time'])
                    minutes = elapsed // 60
                    seconds = elapsed % 60

                    self.realm_data['education']['in_session'] = False
                    self.realm_data['education']['panel_open'] = False

                    # Add completion ticker message (de-duped)
                    complete_msg = f"→ Session complete: {subject_names[subject_index]} ({minutes:02d}:{seconds:02d}) →"
                    if not self.ticker_text.startswith(complete_msg):
                        self.ticker_text = complete_msg + self.ticker_text

                    print(f"[EDUCATION] Session complete! Time: {minutes:02d}:{seconds:02d}")

            # Exit session
            if key == pygame.K_ESCAPE:
                self.realm_data['education']['in_session'] = False
                self.realm_data['education']['panel_open'] = False
                print("[EDUCATION] Exited session")

            return

        # Grid navigation (when not in session)
        if key == pygame.K_LEFT:
            if selected % 3 > 0:
                self.realm_data['education']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:
                self.realm_data['education']['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= 3:
                self.realm_data['education']['selected'] = selected - 3
        elif key == pygame.K_DOWN:
            if selected < 3:
                self.realm_data['education']['selected'] = selected + 3

        # Toggle preview panel
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self.realm_data['education']['panel_open'] = not panel_open
            print(f"[EDUCATION] Preview panel {'opened' if not panel_open else 'closed'}")

        # Close panel
        elif key == pygame.K_b:
            if panel_open:
                self.realm_data['education']['panel_open'] = False
                print("[EDUCATION] Panel closed")

        # Start session (S key)
        elif key == pygame.K_s:
            if panel_open:
                import time
                self.realm_data['education']['in_session'] = True
                self.realm_data['education']['subject_index'] = selected
                self.realm_data['education']['q_index'] = 0
                self.realm_data['education']['session_start_time'] = time.time()
                self.realm_data['education']['answered_correctly'] = False

                # Add ticker message (de-duped)
                start_msg = f"→ Starting {subject_names[selected]} session →"
                if not self.ticker_text.startswith(start_msg):
                    self.ticker_text = start_msg + self.ticker_text

                print(f"[EDUCATION] Starting {subject_names[selected]} session")

    def render_transport(self):
        """Transport - Mobility and navigation"""
        selected = self.realm_data['transport']['selected']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('🚗 TRANSPORT', True, (100, 180, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 40))

        # Current location section
        loc_section = pygame.Rect(80, 115, 900, 80)
        pygame.draw.rect(self.screen, (25, 30, 45), loc_section, border_radius=12)

        loc_label_font = pygame.font.SysFont(None, 34)  # Was 24
        loc_label = loc_label_font.render('Current Location:', True, (180, 190, 200))
        self.screen.blit(loc_label, (100, 130))

        loc_value_font = pygame.font.SysFont(None, 50, bold=True)  # Was 36
        loc_value = loc_value_font.render('📍 123 Main Street, Cypress, TX 77433', True, (100, 200, 255))
        self.screen.blit(loc_value, (100, 160))

        # Destinations label
        dest_label_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
        dest_label = dest_label_font.render('Quick Destinations', True, (220, 230, 240))
        self.screen.blit(dest_label, (80, 230))

        # Destinations
        destinations = [
            {'emoji': '🏠', 'name': 'Home', 'address': '123 Main St', 'eta': '0 min'},
            {'emoji': '💼', 'name': 'Work', 'address': '456 Business Blvd', 'eta': '15 min'},
            {'emoji': '🏫', 'name': 'School', 'address': '789 Education Dr', 'eta': '8 min'},
            {'emoji': '🏥', 'name': 'Hospital', 'address': 'Memorial Medical Ctr', 'eta': '12 min'},
            {'emoji': '🛒', 'name': 'Grocery', 'address': 'Whole Foods Market', 'eta': '5 min'},
            {'emoji': '⛽', 'name': 'Gas Station', 'address': 'Shell Station', 'eta': '3 min'}
        ]

        card_width = 280
        card_height = 140
        gap = 35
        start_x = 120
        start_y = 290

        for i, dest in enumerate(destinations):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(self.screen, (255, 255, 255), card_rect.inflate(6, 6), 3, border_radius=12)

            pygame.draw.rect(self.screen, (30, 40, 60), card_rect, border_radius=12)

            # Emoji - use emoji font
            icon_font = load_emoji_font(101)
            icon = icon_font.render(dest['emoji'], True, (100, 200, 255))
            self.screen.blit(icon, (x + 15, y + 15))

            # Name
            name_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
            name = name_font.render(dest['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + 80, y + 20))

            # Address
            address_font = pygame.font.SysFont(None, 25)  # Was 18
            address = address_font.render(dest['address'], True, (180, 190, 210))
            self.screen.blit(address, (x + 15, y + 75))

            # ETA
            eta_font = pygame.font.SysFont(None, 36, bold=True)  # Was 26
            eta = eta_font.render(f"🕐 {dest['eta']}", True, (100, 255, 150))
            self.screen.blit(eta, (x + 15, y + 105))

        # Help
        help_font = pygame.font.SysFont(None, 28)  # Was 20
        help_text = help_font.render('Arrow Keys: Navigate | ENTER: Navigate to Destination | ESC: Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 720))

    def handle_transport_input(self, key):
        """Handle Transport input"""
        selected = self.realm_data['transport']['selected']

        dest_names = ['Home', 'Work', 'School', 'Hospital', 'Grocery Store', 'Gas Station']

        if key == pygame.K_LEFT:
            if selected % 3 > 0:
                self.realm_data['transport']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:
                self.realm_data['transport']['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= 3:
                self.realm_data['transport']['selected'] = selected - 3
        elif key == pygame.K_DOWN:
            if selected < 3:
                self.realm_data['transport']['selected'] = selected + 3
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            print(f"[TRANSPORT] Calculating route to {dest_names[selected]}...")

    # ==================== MAIN LOOP ====================

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

            # Professional platform features - draw alert banner and STATE indicator first
            self.draw_alert_banner()
            self.draw_state_indicator()

            # Route rendering based on current state
            if self.state == "home":
                self.draw_header()
                self.draw_grid()
                self.draw_footer()
            elif self.state == "circlebeam":
                self.render_circlebeam()
            elif self.state == "marketplace":
                self.render_marketplace()
            elif self.state == "home_realm":
                self.render_home_realm()
            elif self.state == "clinical":
                self.render_clinical()
            elif self.state == "education":
                self.render_education()
            elif self.state == "transport":
                self.render_transport()

            # Draw ticker at bottom (before call overlay)
            self.draw_ticker()

            # Draw call overlay on top of everything if active
            self.draw_call_overlay()

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    app = MotiBeamOS(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    app.run()
