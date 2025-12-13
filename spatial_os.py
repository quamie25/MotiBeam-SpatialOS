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
            'marketplace': {'selected': 0, 'scroll': 0},
            'home_realm': {
                'selected': 0,
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
            'education': {'selected': 0},
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
            'status': 'CircleBeam Call',
            'location': 'Home'
        }

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
        self.ticker_text = "→ Scheduling CircleBeam → Listing schematica → Missed call from Dad → Traffic alert: I-45 delay 15min → Weather update: Clear skies → "
        self.ticker_offset = 0
        self.ticker_speed = 2  # pixels per frame

        # System state (ALERT vs CALM)
        self.system_state = "CALM"  # or "ALERT"

        # Precompute grid cell sizes (adjusted for alert banner and ticker)
        self.grid_top = 180  # Was 140, pushed down for alert banner
        self.grid_bottom = self.height - 140  # Adjusted for ticker
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
        ticker_height = 35
        # Position ticker ABOVE footer (footer is 60px at bottom)
        ticker_y = self.height - 60 - ticker_height

        # Background
        ticker_rect = pygame.Rect(0, ticker_y, self.width, ticker_height)
        pygame.draw.rect(self.screen, (25, 30, 45), ticker_rect)

        # Scrolling text (using system font for crisp rendering)
        ticker_font = pygame.font.SysFont(None, 24)
        ticker_surf = ticker_font.render(self.ticker_text, True, (180, 200, 220))

        # Update offset for scrolling effect
        self.ticker_offset -= self.ticker_speed
        if self.ticker_offset < -ticker_surf.get_width():
            self.ticker_offset = self.width

        self.screen.blit(ticker_surf, (self.ticker_offset, ticker_y + 7))

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
        """Draw incoming call simulation overlay"""
        if not self.call_active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((20, 25, 35))
        self.screen.blit(overlay, (0, 0))

        # Call card
        card_width = 600
        card_height = 400
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, (35, 40, 55), card_rect, border_radius=20)
        pygame.draw.rect(self.screen, (100, 180, 255), card_rect, width=4, border_radius=20)

        # Caller emoji (large) - use emoji font for proper rendering
        caller_emoji_font = load_emoji_font(252)
        caller_emoji = caller_emoji_font.render(self.call_caller['emoji'], True, (255, 255, 255))
        emoji_x = card_x + (card_width - caller_emoji.get_width()) // 2
        self.screen.blit(caller_emoji, (emoji_x, card_y + 40))

        # Caller name
        name_font = pygame.font.SysFont(None, 67, bold=True)  # Was 48
        name_surf = name_font.render(self.call_caller['name'], True, (255, 255, 255))
        name_x = card_x + (card_width - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, card_y + 230))

        # Call status
        status_font = pygame.font.SysFont(None, 39)  # Was 28
        status_surf = status_font.render(self.call_caller['status'], True, (150, 200, 255))
        status_x = card_x + (card_width - status_surf.get_width()) // 2
        self.screen.blit(status_surf, (status_x, card_y + 275))

        # Action buttons
        button_y = card_y + 320

        # Accept button
        accept_rect = pygame.Rect(card_x + 80, button_y, 200, 50)
        pygame.draw.rect(self.screen, (50, 200, 100), accept_rect, border_radius=10)
        accept_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
        accept_text = accept_font.render('📞 Accept (A)', True, (255, 255, 255))
        accept_x = accept_rect.centerx - accept_text.get_width() // 2
        accept_y = accept_rect.centery - accept_text.get_height() // 2
        self.screen.blit(accept_text, (accept_x, accept_y))

        # Decline button
        decline_rect = pygame.Rect(card_x + 320, button_y, 200, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), decline_rect, border_radius=10)
        decline_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
        decline_text = decline_font.render('❌ Decline (D)', True, (255, 255, 255))
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
            print("[CALL] Call accepted")
            self.call_active = False
            return

        if key == pygame.K_d and self.call_active:
            print("[CALL] Call declined")
            self.call_active = False
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
        """CircleBeam - Family telepresence"""
        selected = self.realm_data['circlebeam']['selected']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('👥 CIRCLEBEAM', True, (100, 180, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))

        subtitle_font = pygame.font.SysFont(None, 45)  # Was 32
        subtitle = subtitle_font.render('Stay Connected, Always', True, (180, 200, 220))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 130))

        # Three circle members
        circles = [
            {'name': 'Mom', 'status': 'Available', 'emoji': '👩', 'color': (50, 255, 100)},
            {'name': 'Dad', 'status': 'Away', 'emoji': '👨', 'color': (255, 200, 50)},
            {'name': 'Sister', 'status': 'Do Not Disturb', 'emoji': '👧', 'color': (255, 100, 100)}
        ]

        # Card layout
        card_width = 250
        card_height = 320
        gap = 50
        start_x = self.width // 2 - (3 * card_width + 2 * gap) // 2
        y = 220

        for i, circle in enumerate(circles):
            x = start_x + i * (card_width + gap)
            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight if selected
            if i == selected:
                pygame.draw.rect(self.screen, (255, 255, 255), card_rect.inflate(8, 8), 4, border_radius=15)

            # Card background
            pygame.draw.rect(self.screen, (30, 35, 50), card_rect, border_radius=15)

            # Circle emoji (large, colored by status) - use emoji font
            icon_font = load_emoji_font(168)
            icon = icon_font.render(circle['emoji'], True, circle['color'])
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 30))

            # Name
            name_font = pygame.font.SysFont(None, 56, bold=True)  # Was 40
            name = name_font.render(circle['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 140))

            # Status with colored dot
            status_font = pygame.font.SysFont(None, 34)  # Was 24
            status = status_font.render(circle['status'], True, circle['color'])
            self.screen.blit(status, (x + card_width // 2 - status.get_width() // 2, y + 190))

            # Action button
            button_text = '📞 CALL' if circle['status'] != 'Do Not Disturb' else '✉️ MESSAGE'
            button_font = pygame.font.SysFont(None, 39, bold=True)  # Was 28
            button = button_font.render(button_text, True, (200, 220, 255))
            self.screen.blit(button, (x + card_width // 2 - button.get_width() // 2, y + 240))

        # Emergency button at bottom
        emergency_rect = pygame.Rect(self.width // 2 - 200, 600, 400, 60)
        pygame.draw.rect(self.screen, (120, 30, 30), emergency_rect, border_radius=10)
        emergency_font = pygame.font.SysFont(None, 50, bold=True)  # Was 36
        emergency = emergency_font.render('🚨 EMERGENCY CONTACT', True, (255, 80, 80))
        self.screen.blit(emergency, (self.width // 2 - emergency.get_width() // 2, 615))

        # Help text
        help_font = pygame.font.SysFont(None, 31)  # Was 22
        help_text = help_font.render('Arrow Keys: Select | ENTER: Call/Message | ESC: Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 710))

        # Show action feedback (calling/messaging notification)
        import time
        feedback_text = self.realm_data['circlebeam']['action_feedback']
        feedback_time = self.realm_data['circlebeam']['action_time']
        if feedback_text and time.time() - feedback_time < 2.5:  # Show for 2.5 seconds
            feedback_font = pygame.font.SysFont(None, 48, bold=True)
            feedback_surf = feedback_font.render(feedback_text, True, (100, 255, 200))
            # Draw semi-transparent overlay
            overlay_rect = pygame.Rect(self.width // 2 - 220, 770, 440, 70)
            overlay = pygame.Surface((440, 70), pygame.SRCALPHA)
            overlay.fill((20, 25, 35, 220))
            self.screen.blit(overlay, (overlay_rect.x, overlay_rect.y))
            pygame.draw.rect(self.screen, (100, 255, 200), overlay_rect, 3, border_radius=12)
            self.screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 785))

    def handle_circlebeam_input(self, key):
        """Handle CircleBeam input"""
        selected = self.realm_data['circlebeam']['selected']

        if key == pygame.K_LEFT:
            self.realm_data['circlebeam']['selected'] = max(0, selected - 1)
        elif key == pygame.K_RIGHT:
            self.realm_data['circlebeam']['selected'] = min(2, selected + 1)
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            circles = ['Mom', 'Dad', 'Sister']
            actions = ['Calling', 'Calling', 'Messaging']
            # Set visual feedback
            import time
            self.realm_data['circlebeam']['action_feedback'] = f"{actions[selected]} {circles[selected]}..."
            self.realm_data['circlebeam']['action_time'] = time.time()
            print(f"[CIRCLEBEAM] {actions[selected]} {circles[selected]}...")

    def render_marketplace(self):
        """Marketplace - PX store with scrollable grid"""
        selected = self.realm_data['marketplace']['selected']
        scroll_offset = self.realm_data['marketplace']['scroll']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('🛒 MARKETPLACE', True, (180, 100, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        subtitle_font = pygame.font.SysFont(None, 39)  # Was 28
        subtitle = subtitle_font.render('Projection Experiences', True, (200, 180, 255))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 115))

        # PX Database
        pxs = [
            {'emoji': '🧘', 'name': 'Yoga Flow', 'category': 'Wellness', 'price': '$4.99', 'rating': '★★★★★'},
            {'emoji': '⏱️', 'name': 'Focus Timer', 'category': 'Productivity', 'price': '$2.99', 'rating': '★★★★'},
            {'emoji': '🎵', 'name': 'Jazz Lounge', 'category': 'Entertainment', 'price': '$3.99', 'rating': '★★★★★'},
            {'emoji': '🏃', 'name': 'HIIT Workout', 'category': 'Fitness', 'price': '$5.99', 'rating': '★★★★'},
            {'emoji': '📚', 'name': 'Story Time', 'category': 'Education', 'price': '$2.99', 'rating': '★★★★★'},
            {'emoji': '🌊', 'name': 'Ocean Sounds', 'category': 'Relaxation', 'price': '$1.99', 'rating': '★★★★'},
            {'emoji': '🧠', 'name': 'Brain Training', 'category': 'Education', 'price': '$6.99', 'rating': '★★★★'},
            {'emoji': '🎨', 'name': 'Art Gallery', 'category': 'Culture', 'price': '$4.99', 'rating': '★★★★★'},
            {'emoji': '☕', 'name': 'Coffee Shop', 'category': 'Ambiance', 'price': '$2.99', 'rating': '★★★★'},
            {'emoji': '✨', 'name': 'Starfield', 'category': 'Relaxation', 'price': '$3.99', 'rating': '★★★★★'},
            {'emoji': '🎯', 'name': 'Goal Tracker', 'category': 'Productivity', 'price': '$4.99', 'rating': '★★★★'},
            {'emoji': '🌲', 'name': 'Forest Walk', 'category': 'Nature', 'price': '$2.99', 'rating': '★★★★★'},
        ]

        # Show 9 PXs at a time (3x3 grid)
        visible_pxs = pxs[scroll_offset:scroll_offset + 9]

        card_width = 280
        card_height = 180
        gap = 30
        start_x = 80
        start_y = 180

        for i, px in enumerate(visible_pxs):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(self.screen, (255, 255, 255), card_rect.inflate(6, 6), 3, border_radius=12)

            pygame.draw.rect(self.screen, (35, 30, 55), card_rect, border_radius=12)

            # PX emoji - use emoji font
            icon_font = load_emoji_font(101)
            icon = icon_font.render(px['emoji'], True, (100, 200, 255))
            self.screen.blit(icon, (x + 15, y + 15))

            # PX name
            name_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
            name = name_font.render(px['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + 90, y + 20))

            # Category
            cat_font = pygame.font.SysFont(None, 28)  # Was 20
            cat = cat_font.render(px['category'], True, (180, 160, 200))
            self.screen.blit(cat, (x + 90, y + 50))

            # Price
            price_font = pygame.font.SysFont(None, 50, bold=True)  # Was 36
            price = price_font.render(px['price'], True, (100, 255, 150))
            self.screen.blit(price, (x + 15, y + 115))

            # Rating
            rating_font = pygame.font.SysFont(None, 31)  # Was 22
            rating = rating_font.render(px['rating'], True, (255, 200, 50))
            self.screen.blit(rating, (x + 15, y + 150))

        # Scroll indicator
        if scroll_offset + 9 < len(pxs):
            arrow_font = pygame.font.SysFont(None, 39)  # Was 28
            arrow_down = arrow_font.render('v More PXs Below (Down Arrow)', True, (150, 150, 200))
            self.screen.blit(arrow_down, (self.width // 2 - arrow_down.get_width() // 2, 680))

        # Help
        help_font = pygame.font.SysFont(None, 28)  # Was 20
        help_text = help_font.render('Arrow Keys: Navigate | ENTER: Install | ESC: Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 720))

    def handle_marketplace_input(self, key):
        """Handle Marketplace input"""
        selected = self.realm_data['marketplace']['selected']
        scroll_offset = self.realm_data['marketplace']['scroll']

        total_pxs = 12  # Total in database
        visible_count = 9  # Show 9 at a time

        if key == pygame.K_LEFT:
            if selected % 3 > 0:
                self.realm_data['marketplace']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < min(visible_count, total_pxs - scroll_offset) - 1:
                self.realm_data['marketplace']['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= 3:
                self.realm_data['marketplace']['selected'] = selected - 3
        elif key == pygame.K_DOWN:
            if selected + 3 < min(visible_count, total_pxs - scroll_offset):
                self.realm_data['marketplace']['selected'] = selected + 3
            elif scroll_offset + visible_count < total_pxs:
                # Scroll down to next page
                self.realm_data['marketplace']['scroll'] = min(scroll_offset + 3, total_pxs - visible_count)
                self.realm_data['marketplace']['selected'] = 0
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            px_names = ['Yoga Flow', 'Focus Timer', 'Jazz Lounge', 'HIIT Workout', 'Story Time',
                       'Ocean Sounds', 'Brain Training', 'Art Gallery', 'Coffee Shop',
                       'Starfield', 'Goal Tracker', 'Forest Walk']
            actual_index = scroll_offset + selected
            if actual_index < len(px_names):
                print(f"[MARKETPLACE] Installing {px_names[actual_index]}...")

    def render_home_realm(self):
        """Home - Smart home control"""
        selected = self.realm_data['home_realm']['selected']
        devices_state = self.realm_data['home_realm']['devices']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('🏠 HOME CONTROL', True, (100, 255, 150))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

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
        card_height = 220
        gap = 40
        start_x = 120
        start_y = 160

        for i, device in enumerate(devices):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(self.screen, (255, 255, 255), card_rect.inflate(6, 6), 3, border_radius=15)

            # Color based on state
            state = devices_state[device['id']]
            if device['type'] == 'toggle':
                bg_color = (50, 100, 50) if state else (50, 50, 60)
            else:  # adjust (thermostat)
                bg_color = (60, 80, 120)

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)

            # Emoji - use emoji font
            icon_font = load_emoji_font(134)
            icon = icon_font.render(device['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 20))

            # Name
            name_font = pygame.font.SysFont(None, 45, bold=True)  # Was 32
            name = name_font.render(device['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 110))

            # State display
            if device['type'] == 'toggle':
                state_text = 'ON' if state else 'OFF'
                state_color = (100, 255, 100) if state else (150, 150, 150)
            else:  # adjust (temperature)
                state_text = f"{state}°F"
                state_color = (100, 200, 255)

            state_font = pygame.font.SysFont(None, 59, bold=True)  # Was 42
            state_surf = state_font.render(state_text, True, state_color)
            self.screen.blit(state_surf, (x + card_width // 2 - state_surf.get_width() // 2, y + 155))

        # Help
        help_font = pygame.font.SysFont(None, 28)  # Was 20
        help_text = help_font.render('Arrow Keys: Navigate | ENTER: Toggle/Adjust | ESC: Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 720))

    def handle_home_realm_input(self, key):
        """Handle Home realm input"""
        selected = self.realm_data['home_realm']['selected']
        devices_state = self.realm_data['home_realm']['devices']

        device_ids = ['living_lights', 'bedroom_lights', 'temp', 'security', 'door', 'garage']
        device_names = ['Living Room Lights', 'Bedroom Lights', 'Thermostat', 'Security System', 'Front Door Lock', 'Garage Door']

        if key == pygame.K_LEFT:
            if selected % 3 > 0:
                self.realm_data['home_realm']['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:
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
                # Adjust temperature up by 1
                current_temp = devices_state[device_id]
                devices_state[device_id] = min(85, current_temp + 1)
                print(f"[HOME] {device_names[selected]} adjusted to {devices_state[device_id]}°F")
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

    def render_education(self):
        """Education - Interactive learning hub"""
        selected = self.realm_data['education']['selected']

        # Header
        title_font = pygame.font.SysFont(None, 90, bold=True)  # Was 64
        title = title_font.render('📚 EDUCATION', True, (255, 180, 50))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 45))

        subtitle_font = pygame.font.SysFont(None, 39)  # Was 28
        subtitle = subtitle_font.render('Interactive Learning Sessions', True, (220, 200, 150))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 110))

        # Subjects
        subjects = [
            {'emoji': '🔢', 'name': 'Mathematics', 'progress': 75, 'level': 'Grade 5'},
            {'emoji': '📖', 'name': 'Reading', 'progress': 82, 'level': 'Advanced'},
            {'emoji': '🔬', 'name': 'Science', 'progress': 68, 'level': 'Grade 5'},
            {'emoji': '🗺️', 'name': 'History', 'progress': 55, 'level': 'Grade 4'},
            {'emoji': '🌍', 'name': 'Geography', 'progress': 90, 'level': 'Grade 5'},
            {'emoji': '🎨', 'name': 'Art', 'progress': 45, 'level': 'Beginner'}
        ]

        card_width = 280
        card_height = 240
        gap = 40
        start_x = 120
        start_y = 175

        for i, subject in enumerate(subjects):
            row = i // 3
            col = i % 3

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(self.screen, (255, 255, 255), card_rect.inflate(6, 6), 3, border_radius=15)

            pygame.draw.rect(self.screen, (30, 35, 50), card_rect, border_radius=15)

            # Emoji - use emoji font
            icon_font = load_emoji_font(118)
            icon = icon_font.render(subject['emoji'], True, (100, 200, 255))
            self.screen.blit(icon, (x + 20, y + 20))

            # Subject name
            name_font = pygame.font.SysFont(None, 48, bold=True)  # Was 34
            name = name_font.render(subject['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + 95, y + 28))

            # Level
            level_font = pygame.font.SysFont(None, 28)  # Was 20
            level = level_font.render(subject['level'], True, (180, 190, 200))
            self.screen.blit(level, (x + 95, y + 62))

            # Progress bar background
            progress_bg = pygame.Rect(x + 20, y + 115, card_width - 40, 28)
            pygame.draw.rect(self.screen, (50, 55, 70), progress_bg, border_radius=6)

            # Progress bar fill
            progress_fill_width = int((card_width - 40) * subject['progress'] / 100)
            progress_fill = pygame.Rect(x + 20, y + 115, progress_fill_width, 28)
            pygame.draw.rect(self.screen, (100, 200, 255), progress_fill, border_radius=6)

            # Progress text
            progress_font = pygame.font.SysFont(None, 28, bold=True)  # Was 20
            progress_text = progress_font.render(f"{subject['progress']}%", True, (255, 255, 255))
            self.screen.blit(progress_text, (x + card_width // 2 - progress_text.get_width() // 2, y + 119))

            # Start button
            btn_font = pygame.font.SysFont(None, 36, bold=True)  # Was 26
            btn_text = btn_font.render('▶️ Start Session', True, (150, 220, 150))
            self.screen.blit(btn_text, (x + card_width // 2 - btn_text.get_width() // 2, y + 175))

        # Help
        help_font = pygame.font.SysFont(None, 28)  # Was 20
        help_text = help_font.render('Arrow Keys: Navigate | ENTER: Start Session | ESC: Back', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 720))

    def handle_education_input(self, key):
        """Handle Education input"""
        selected = self.realm_data['education']['selected']

        subject_names = ['Mathematics', 'Reading', 'Science', 'History', 'Geography', 'Art']

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
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            print(f"[EDUCATION] Starting {subject_names[selected]} session...")

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
