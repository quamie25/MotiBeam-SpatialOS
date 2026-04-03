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
import time
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
    {"name": "Productivity", "subtitle": "Focus & Awareness",      "emoji": "🎯"},
    {"name": "LockboxBeam", "subtitle": "Secure vault",        "emoji": "🔐"},
    {"name": "Marketplace", "subtitle": "Wellness & goods",    "emoji": "🛒"},
    {"name": "Home",       "subtitle": "Smart home",           "emoji": "🏠"},
    {"name": "Health & Wellness",   "subtitle": "Daily wellbeing, calmly supported",    "emoji": "🌿"},
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
        self.font_header_meta = pygame.font.SysFont(None, 36)  # Was 30
        self.font_emoji = pygame.font.SysFont(None, 134)  # System font for sharp text
        self.font_card_title = pygame.font.SysFont(None, 48)  # Was 34
        self.font_card_subtitle = pygame.font.SysFont(None, 31)  # Was 22
        self.font_footer = pygame.font.SysFont(None, 34)  # Was 24
        # Overlay fonts (for demo mode)
        self.font_overlay_timer = pygame.font.SysFont(None, 240, bold=True)
        self.font_overlay_subtitle = pygame.font.SysFont(None, 56)
        self.font_overlay_hint = pygame.font.SysFont(None, 36)
        # Overlay fonts (for demo mode)
        self.font_overlay_timer = pygame.font.SysFont(None, 240, bold=True)
        self.font_overlay_subtitle = pygame.font.SysFont(None, 56)
        self.font_overlay_hint = pygame.font.SysFont(None, 36)

        self.clock = pygame.time.Clock()
        self.selected_index = 0  # which card is selected on home grid

        # Navigation system
        self.state = "home"
        self.navigation_stack = ["home"]

        # Realm-specific state data
        self.realm_data = {
            'circlebeam': {'selected': 0, 'panel_open': False, 'action_feedback': None, 'action_time': 0},
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
            'health_wellness': {'selected': 0, 'panel_open': False, 'calm_breathing_active': False},
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
            'productivity': {
                'selected': 0,
                'panel_open': False,
                'active_module': None,      # None or 0-5 (which module is active)
                'timer_start': 0.0,         # For Pomodoro timer
                'timer_seconds': 25 * 60    # Default 25 minutes
            },
            'transport': {'selected': 0, 'panel_open': False, 'driving_mode': True, 'last_interaction': 0}
        }

        # Weather integration
        self.weather = None
        self.weather_last_update = 0
        self.fetch_weather_async()

        self.call_active = False
        # Contact list for cycling through different callers
        self.contacts = [
            {'name': 'Mom', 'emoji': '👩', 'relation': 'Family'},
            {'name': 'Dad', 'emoji': '👨', 'relation': 'Family'},
            {'name': 'Sister Sarah', 'emoji': '👧', 'relation': 'Family'},
            {'name': 'Dr. Johnson', 'emoji': '⚕️', 'relation': 'Healthcare'},
            {'name': 'Best Friend Alex', 'emoji': '🙋', 'relation': 'Friend'}
        ]
        self.contact_index = 0
        self.missed_presence = False  # Tracks if there's a missed presence notification
        self.call_caller = self.contacts[0]  # Start with Mom
        
        # Alert system (professional features) - shorter messages to prevent overlap
        self.alerts = [
            {'type': 'severe', 'message': 'SEVERE WEATHER - Tornado spotted. Seek shelter immediately', 'color': (255, 80, 80)},
            {'type': 'medical', 'message': 'MEDICATION TIME - Take your medication NOW', 'color': (255, 50, 50)},
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
        
        # === BACKGROUND DIMMING for Critical Alerts ===
        if alert['type'] in ['severe', 'medical']:
            dim_overlay = pygame.Surface((self.width, self.height))
            dim_overlay.set_alpha(25)  # Subtle 10% dim
            dim_overlay.fill((0, 0, 0))
            self.screen.blit(dim_overlay, (0, 0))

        # MEDICATION ALERT: Bigger, brighter, pulsing for elderly visibility
        if alert['type'] == 'medical':
            banner_height = 75  # Taller for medication

            # Pulsing effect - brightness oscillates for attention
            self.alert_pulse += 0.15
            pulse = abs(math.sin(self.alert_pulse))
            pulse_brightness = int(150 + (pulse * 105))  # 150-255 brightness
            banner_color = (pulse_brightness, 30, 30)  # Pulsing red

            banner_rect = pygame.Rect(0, 0, self.width, banner_height)
            pygame.draw.rect(self.screen, banner_color, banner_rect)

            # Extra large text for medication
            alert_font = pygame.font.SysFont(None, 95, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 18))
            
            # Priority badge (left side)
            priority_font = pygame.font.SysFont(None, 32, bold=True)
            priority_text = priority_font.render('CRITICAL', True, (255, 255, 255))
            self.screen.blit(priority_text, (20, 25))
            
            # Dismissal hint (right side)
            hint_font = pygame.font.SysFont(None, 28)
            hint_text = hint_font.render('Auto-dismiss in 2 min', True, (255, 220, 220))
            self.screen.blit(hint_text, (self.width - 280, 28))
            
        else:
            # Normal alerts
            banner_height = 55
            banner_rect = pygame.Rect(0, 0, self.width, banner_height)
            pygame.draw.rect(self.screen, alert['color'], banner_rect)

            alert_font = pygame.font.SysFont(None, 75, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 15))
            
            # Priority badge for severe weather
            if alert['type'] == 'severe':
                priority_font = pygame.font.SysFont(None, 28, bold=True)
                priority_text = priority_font.render('IMPORTANT', True, (255, 255, 255))
                self.screen.blit(priority_text, (15, 20))
            else:
                # Info level for messages
                priority_font = pygame.font.SysFont(None, 28, bold=True)
                priority_text = priority_font.render('INFO', True, (255, 255, 255))
                self.screen.blit(priority_text, (15, 20))

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
        # Check if ticker is hidden by T key
        if not getattr(self, "ticker_visible", True):
            return

        """Draw scrolling ticker above footer"""
        ticker_height = 56  # Increased from 35 for better readability (+60%)
        # Position ticker ABOVE footer (footer is 60px at bottom)
        ticker_y = self.height - 50 - ticker_height

        # Background
        ticker_rect = pygame.Rect(0, ticker_y, self.width, ticker_height)
        pygame.draw.rect(self.screen, (25, 30, 45), ticker_rect)

        # Scrolling text (using system font for crisp rendering)
        ticker_font = pygame.font.SysFont(None, 70)  # Increased from 24 for wall projection (+83%)
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
            "←↑↓→ Move   |   Enter Select   |   P Privacy   |   T Ticker   |   I Call   |   L Alerts   |   Q / ESC Exit"
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
        display_name = 'Contact' if getattr(self, 'privacy_mode', False) else self.call_caller['name']
        name_surf = name_font.render(display_name, True, (255, 255, 255))
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

        # T toggles ticker visibility
        if key == pygame.K_t:
            self.ticker_visible = not getattr(self, "ticker_visible", True)
            print(f"[TICKER] Ticker {"visible" if self.ticker_visible else "hidden"}")
            return
        
        # P toggles privacy mode
        if key == pygame.K_p:
            self.privacy_mode = not getattr(self, "privacy_mode", False)
            print(f"[PRIVACY] Privacy mode {'ON' if self.privacy_mode else 'OFF'}")
            return   
        
        if key == pygame.K_ESCAPE:
            if self.state == "home":
                pygame.quit()
                sys.exit(0)
            # Don't go back if Education is in session mode - let realm handler deal with it
            elif self.state == "education" and self.realm_data['education']['in_session']:
                pass  # Education handler will process this
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
     
            # Cycle to next contact
            self.contact_index = (self.contact_index + 1) % len(self.contacts)
            self.call_caller = self.contacts[self.contact_index]
            self.call_active = True
            print(f"[CALL] Incoming call from {self.call_caller['name']} ({self.call_caller['relation']})")
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
        elif self.state == "health_wellness":
            self.handle_health_wellness_input(key)
        elif self.state == "education":
            self.handle_education_input(key)
        elif self.state == "productivity":
            self.handle_productivity_input(key)
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
                1: "productivity",
                3: "marketplace",
                4: "home_realm",
                5: "health_wellness",
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
        """CircleBeam - Family Presence Layer (Licensing-Ready)"""
        selected = self.realm_data['circlebeam']['selected']

        # Title - proper emoji + text alignment
        title_emoji_font = load_emoji_font(120)
        title_text_font = pygame.font.SysFont(None, 120, bold=True)
        people_emoji = title_emoji_font.render('👥', True, (100, 180, 255))
        circlebeam_text = title_text_font.render(' CIRCLEBEAM', True, (100, 180, 255))
        title_width = people_emoji.get_width() + circlebeam_text.get_width()
        title_x = self.width // 2 - title_width // 2
        self.screen.blit(people_emoji, (title_x, 50))
        self.screen.blit(circlebeam_text, (title_x + people_emoji.get_width(), 50))

        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 52)
        subtitle = subtitle_font.render('Family Presence', True, (180, 200, 220))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 160))

        # Circle members - 2×3 grid (standard across platform)
        circles = [
            {'name': 'Mom', 'status': 'available', 'emoji': '👩', 'status_text': 'Available', 'dot': '●'},
            {'name': 'Dad', 'status': 'quiet', 'emoji': '👨', 'status_text': 'Quiet mode', 'dot': '●'},
            {'name': 'Sister', 'status': 'offline', 'emoji': '👧', 'status_text': 'Offline', 'dot': '●'},
            {'name': 'Brother', 'status': 'available', 'emoji': '👦', 'status_text': 'Available', 'dot': '●'},
            {'name': 'Grandma', 'status': 'needs_attention', 'emoji': '👵', 'status_text': 'Needs attention', 'dot': '●'},
            {'name': 'Care Team', 'status': 'available', 'emoji': '⚕️', 'status_text': 'Available', 'dot': '●'}
        ]

        # Standardized status colors
        status_colors = {
            'available': (100, 255, 150),     # Green
            'quiet': (120, 180, 255),         # Yellow
            'offline': (140, 150, 160),       # Gray
            'needs_attention': (255, 100, 100) # Red
        }

        # Grid layout - even spacing, centered
        card_width = 400
        card_height = 260
        gap = 60  # Same horizontal and vertical
        cols = 3
        rows = 2

        # Center the grid
        grid_width = cols * card_width + (cols - 1) * gap
        start_x = (self.width - grid_width) // 2
        start_y = 250

        for i, circle in enumerate(circles):
            row = i // cols
            col = i % cols

            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)

            card_rect = pygame.Rect(x, y, card_width, card_height)

            # Selection glow - strong but not overwhelming
            if i == selected:
                pygame.draw.rect(self.screen, (100, 180, 255), card_rect.inflate(10, 10), 4, border_radius=16)
            
            # Card background - dimmed if not selected
            bg_brightness = 1.0 if i == selected else 0.7
            bg_color = tuple(int(c * bg_brightness) for c in (30, 35, 50))
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)

            # Member emoji
            icon_font = load_emoji_font(110)
            icon = icon_font.render(circle['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 25))

            # Name - licensing-ready size (56px)
            name_font = pygame.font.SysFont(None, 56, bold=True)
            name = name_font.render(circle['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + card_width // 2 - name.get_width() // 2, y + 145))

            # Status indicator - standardized
            status_color = status_colors[circle['status']]
            
            # Status dot
            # Status dot - standardized colored circle
            dot_font = pygame.font.SysFont(None, 48, bold=True)
            dot = dot_font.render(circle['dot'], True, status_color)
            
            # Status text - readable size (36px)
            status_font = pygame.font.SysFont(None, 36)
            status_text = status_font.render(circle['status_text'], True, status_color)
            
            # Center status line
            status_width = dot.get_width() + 8 + status_text.get_width()
            status_x = x + (card_width - status_width) // 2
            
            self.screen.blit(dot, (status_x, y + 195))
            self.screen.blit(status_text, (status_x + dot.get_width() + 8, y + 200))

        # Preview panel (if open)
        if self.realm_data['circlebeam']['panel_open']:
            person = circles[selected]
            
            # Panel background (right side)
            panel_x = 1100
            panel_y = 180
            panel_width = 760
            panel_height = 700
            
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (25, 30, 45), panel_rect, border_radius=15)
            pygame.draw.rect(self.screen, (100, 180, 255), panel_rect, 3, border_radius=15)
            
            # Person avatar (large)
            avatar_font = load_emoji_font(150)
            avatar = avatar_font.render(person['emoji'], True, (255, 255, 255))
            self.screen.blit(avatar, (panel_x + panel_width // 2 - avatar.get_width() // 2, panel_y + 40))
            
            # Name (large) - privacy aware
            privacy_mode = getattr(self, 'privacy_mode', False)
            name_font = pygame.font.SysFont(None, 80, bold=True)
            if privacy_mode:
                # Show initials or generic label
                display_name = person['name'][0] + "." if len(person['name']) > 0 else "Contact"
            else:
                display_name = person['name']
            name_surf = name_font.render(display_name, True, (255, 255, 255))
            self.screen.blit(name_surf, (panel_x + panel_width // 2 - name_surf.get_width() // 2, panel_y + 210))
            
            # Status with explanation
            status_color = status_colors[person['status']]
            status_font = pygame.font.SysFont(None, 50, bold=True)
            
            status_explanations = {
                'available': 'Available for contact',
                'quiet': 'Quiet mode — notifications paused',
                'offline': 'Not currently connected',
                'needs_attention': 'Urgent — please check in'
            }
            
            status_surf = status_font.render(status_explanations[person['status']], True, status_color)
            self.screen.blit(status_surf, (panel_x + panel_width // 2 - status_surf.get_width() // 2, panel_y + 290))
            
            # Last seen - privacy aware
            seen_font = pygame.font.SysFont(None, 42)
            if privacy_mode:
                seen_text = "🔒 Privacy Mode Active"
                seen_color = (255, 220, 100)
            else:
                seen_times = {0: '2h ago', 1: '30m ago', 2: 'Yesterday', 3: '1h ago', 4: '15m ago', 5: 'Available now'}
                seen_text = f"Last seen: {seen_times[selected]}"
                seen_color = (180, 190, 200)
            seen_surf = seen_font.render(seen_text, True, seen_color)
            self.screen.blit(seen_surf, (panel_x + panel_width // 2 - seen_surf.get_width() // 2, panel_y + 350))
            
            # Action buttons
            action_y = panel_y + 430
            button_font = pygame.font.SysFont(None, 50, bold=True)
            key_font = pygame.font.SysFont(None, 60, bold=True)
            
            actions = [
                {'key': 'C', 'label': 'Call', 'color': (100, 200, 255)},
                {'key': 'M', 'label': 'Message', 'color': (150, 255, 150)},
                {'key': 'N', 'label': 'Nudge', 'color': (255, 200, 100)}
            ]
            
            button_width = 200
            button_height = 70
            gap = 30
            start_x = panel_x + (panel_width - (3 * button_width + 2 * gap)) // 2
            
            for i, action in enumerate(actions):
                btn_x = start_x + i * (button_width + gap)
                btn_rect = pygame.Rect(btn_x, action_y, button_width, button_height)
                
                pygame.draw.rect(self.screen, (40, 50, 70), btn_rect, border_radius=10)
                pygame.draw.rect(self.screen, action['color'], btn_rect, 3, border_radius=10)
                
                # Key letter
                key_surf = key_font.render(action['key'], True, action['color'])
                self.screen.blit(key_surf, (btn_x + 20, action_y + 10))
                
                # Label
                label_surf = button_font.render(action['label'], True, (220, 220, 220))
                self.screen.blit(label_surf, (btn_x + 70, action_y + 17))

            # Action feedback (brief confirmation message)
            import time
            if self.realm_data['circlebeam']['action_feedback']:
                elapsed = time.time() - self.realm_data['circlebeam']['action_time']
                if elapsed < 2.0:  # Show for 2 seconds
                    feedback_font = pygame.font.SysFont(None, 56, bold=True)
                    feedback_surf = feedback_font.render(self.realm_data['circlebeam']['action_feedback'], True, (100, 255, 150))
                    feedback_bg = pygame.Rect(panel_x + 50, panel_y + 570, panel_width - 100, 60)
                    pygame.draw.rect(self.screen, (30, 60, 40), feedback_bg, border_radius=8)
                    self.screen.blit(feedback_surf, (panel_x + panel_width // 2 - feedback_surf.get_width() // 2, panel_y + 580))
                else:
                    # Clear after 2 seconds
                    self.realm_data['circlebeam']['action_feedback'] = None
            
            # Close hint
            close_font = pygame.font.SysFont(None, 44)
            close_surf = close_font.render('ENTER or ESC to close', True, (150, 170, 200))
            self.screen.blit(close_surf, (panel_x + panel_width // 2 - close_surf.get_width() // 2, panel_y + 620))

        # Footer - safe zone (no overlap)
        philosophy_font = pygame.font.SysFont(None, 38)
        philosophy = philosophy_font.render('Presence is shared without requiring interaction.', True, (150, 170, 200))
        self.screen.blit(philosophy, (self.width // 2 - philosophy.get_width() // 2, 820))

        help_font = pygame.font.SysFont(None, 36)
        help_text = help_font.render('← → Navigate | ENTER Preview | I Incoming | ESC Home', True, (150, 160, 180))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 870))

    def handle_circlebeam_input(self, key):
        """Handle CircleBeam input - 3 cols × 2 rows grid (5 members)"""
        selected = self.realm_data['circlebeam']['selected']
        total_members = 6
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
            # Toggle preview panel
            self.realm_data['circlebeam']['panel_open'] = not self.realm_data['circlebeam']['panel_open']
            print(f"[CIRCLEBEAM] Preview panel {'opened' if self.realm_data['circlebeam']['panel_open'] else 'closed'}")
            return
        
        # Panel action keys (only when panel is open)
        elif self.realm_data['circlebeam']['panel_open']:
            if key == pygame.K_c:
                self.realm_data['circlebeam']['action_feedback'] = "✓ Call initiated"
                self.realm_data['circlebeam']['action_time'] = time.time()
                print("[CIRCLEBEAM] Call initiated (demo)")
                return
            elif key == pygame.K_m:
                self.realm_data['circlebeam']['action_feedback'] = "✓ Message sent"
                self.realm_data['circlebeam']['action_time'] = time.time()
                print("[CIRCLEBEAM] Message sent (demo)")
                return
            elif key == pygame.K_n:
                self.realm_data['circlebeam']['action_feedback'] = "✓ Presence ping sent"
                self.realm_data['circlebeam']['action_time'] = time.time()
                print("[CIRCLEBEAM] Nudge sent (demo)")
                return
            elif key == pygame.K_p:
                print("[CIRCLEBEAM] Presence ping sent (demo)")
                return
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
        title_font = pygame.font.SysFont(None, 140, bold=True)  # Scaled 1.56×
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
        gap = 58  # Scaled 1.45×
        start_x = 60
        start_y = 180

        # If preview is open, shift grid left and add preview panel
        if preview_open:
            start_x = 40
            card_width = 400
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
            name_font = pygame.font.SysFont(None, 80, bold=True)
            name = name_font.render(px['name'], True, (255, 255, 255))
            self.screen.blit(name, (x + 110, y + 30))

            # Category
            cat_font = pygame.font.SysFont(None, 30)
            cat = cat_font.render(px['category'], True, (180, 160, 200))
            self.screen.blit(cat, (x + 110, y + 65))

            # Description (shorter for compact view)
            desc_font = pygame.font.SysFont(None, 36)
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

            badge_font = pygame.font.SysFont(None, 55, bold=True)
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
            pass  # Disabled - preview panel causes Pi reboot

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
        # Title with proper emoji rendering
        title_emoji_font = load_emoji_font(140)
        title_text_font = pygame.font.SysFont(None, 140, bold=True)
        house = title_emoji_font.render('🏠', True, (100, 255, 150))
        home_text = title_text_font.render(' HOME', True, (100, 255, 150))
        total_width = house.get_width() + home_text.get_width()
        title_x = self.width // 2 - total_width // 2
        self.screen.blit(house, (title_x, 50))
        self.screen.blit(home_text, (title_x + house.get_width(), 50))

        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 62)  # Scaled 1.48×
        subtitle = subtitle_font.render('Calm Home Awareness', True, (180, 220, 200))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 190))

        # Device configurations
        devices = [
            {'id': 'living_lights', 'emoji': '💡', 'name': 'Living Room', 'type': 'toggle'},
            {'id': 'bedroom_lights', 'emoji': '🛏️', 'name': 'Bedroom', 'type': 'toggle'},
            {'id': 'temp', 'emoji': '🌡️', 'name': 'Thermostat', 'type': 'adjust'},
            {'id': 'security', 'emoji': '🛡️', 'name': 'Security', 'type': 'toggle'},
            {'id': 'door', 'emoji': '🚪', 'name': 'Front Door', 'type': 'toggle'},
            {'id': 'garage', 'emoji': '🚗', 'name': 'Garage', 'type': 'toggle'}
        ]

        card_width = 400  # Scaled 1.43×
        card_height = 280  # Scaled 1.43×
        gap = 80  # Horizontal spacing (38% increase)
        gap = 100  # Vertical spacing (72% increase)
        start_x = 280  # Recalculated for gap=80
        start_y = 280  # More separation from subtitle

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
            icon_font = load_emoji_font(155)  # Scaled 1.41×
            icon = icon_font.render(device['emoji'], True, (255, 255, 255))
            self.screen.blit(icon, (x + card_width // 2 - icon.get_width() // 2, y + 15))

            # Device name - larger and bolder
            name_font = pygame.font.SysFont(None, 75, bold=True)  # Scaled 1.44×
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

                pill_font = pygame.font.SysFont(None, 52, bold=True)  # Scaled 1.44×
                pill_surf = pill_font.render(pill_text, True, pill_fg)
                pill_width = pill_surf.get_width() + 30
                pill_height = 46  # Scaled 1.44×
                pill_x = x + (card_width - pill_width) // 2
                pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)

                pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=16)
                self.screen.blit(pill_surf, (pill_x + 15, pill_y + 6))

            else:  # Thermostat - special display
                # Large temperature
                temp_font = pygame.font.SysFont(None, 92, bold=True)  # Scaled 1.44×
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

    def render_health_wellness(self):
        # Set realm-specific ticker content
        if hasattr(self, "wellness_states"):
            active_count = sum(1 for s in self.wellness_states if s == "ACTIVE")
            on_count = sum(1 for s in self.wellness_states if s == "ON")
            self.ticker_text = f"→ {active_count} wellness activities active • {on_count} routines enabled • Press T to toggle ticker → "
        else:
            self.ticker_text = "→ Health & Wellness Mode • Press ENTER to activate routines • Press T to toggle ticker → "
        """Health & Wellness - Calm support for daily wellbeing"""
        selected = self.realm_data['health_wellness']['selected']
        panel_open = self.realm_data['health_wellness']['panel_open']

        # Wellness activity definitions
        activities = [
            {'emoji': '🧘', 'name': 'Calm', 'desc': 'Grounding', 'status': self.wellness_states[0] if hasattr(self, 'wellness_states') else 'ACTIVE'},
            {'emoji': '😴', 'name': 'Sleep', 'desc': 'Sleep cues', 'status': self.wellness_states[1] if hasattr(self, 'wellness_states') else 'Ready'},
            {'emoji': '💊', 'name': 'Routines', 'desc': 'Daily habits', 'status': self.wellness_states[2] if hasattr(self, 'wellness_states') else 'ON'},
            {'emoji': '🚶', 'name': 'Movement', 'desc': 'Activity', 'status': self.wellness_states[3] if hasattr(self, 'wellness_states') else 'Ready'},
            {'emoji': '🧠', 'name': 'Mindfulness', 'desc': 'Presence', 'status': self.wellness_states[4] if hasattr(self, 'wellness_states') else 'Ready'},
            {'emoji': '🌤️', 'name': 'Daily Check-In', 'desc': 'Daily mood', 'status': self.wellness_states[5] if hasattr(self, 'wellness_states') else 'Ready'}
        ]

        # Header
        # Title with emoji font
        title_emoji_font = load_emoji_font(140)
        title_text_font = pygame.font.SysFont(None, 140, bold=True)
        leaf = title_emoji_font.render('🌿', True, (120, 200, 160))
        health_text = title_text_font.render(' HEALTH & WELLNESS', True, (120, 200, 160))
        title_width = leaf.get_width() + health_text.get_width()
        title_x = self.width // 2 - title_width // 2
        self.screen.blit(leaf, (title_x, 45))
        self.screen.blit(health_text, (title_x + leaf.get_width(), 45))

        subtitle_font = pygame.font.SysFont(None, 62)  # Scaled 1.48×
        subtitle = subtitle_font.render('Daily wellbeing, calmly supported', True, (96, 114, 102))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 110))

        # 2×3 grid layout
        grid_cols = 3
        grid_rows = 2
        card_width = 460
        card_height = 320
        gap = 80
        gap = 100

        grid_width = grid_cols * card_width + (grid_cols - 1) * gap
        grid_start_x = (self.width - grid_width) // 2
        grid_start_y = 300

        for i, activity in enumerate(activities):
            row = i // grid_cols
            col = i % grid_cols
            x = grid_start_x + col * (card_width + gap)
            y = grid_start_y + row * (card_height + gap)

            # Determine if selected
            is_selected = (i == selected)

            # Card background - dim unselected
            if is_selected:
                card_color = (30, 40, 50)
            else:
                # Dim to 70%
                card_color = (int(30 * 0.7), int(40 * 0.7), int(50 * 0.7))

            card_rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=12)

            # Breathing glow for Calm tile
            if i == 0:  # Calm tile
                import math
                pulse = (math.sin(pygame.time.get_ticks() / 1200) + 1) / 2  # 4.8s cycle
                glow_alpha = int(30 + pulse * 30)  # 30-60 alpha
                glow_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                glow_surface.fill((100, 200, 160, glow_alpha))
                self.screen.blit(glow_surface, (x, y))

            # Selection glow
            if is_selected:
                glow_rect = pygame.Rect(x - 4, y - 4, card_width + 8, card_height + 8)
                pygame.draw.rect(self.screen, (100, 200, 160), glow_rect, width=3, border_radius=14)

            # Emoji icon
            icon_font = load_emoji_font(125)
            icon_color = (255, 255, 255) if is_selected else (int(255 * 0.7), int(255 * 0.7), int(255 * 0.7))
            icon = icon_font.render(activity['emoji'], True, icon_color)
            icon_x = x + card_width // 2 - icon.get_width() // 2
            self.screen.blit(icon, (icon_x, y + 20))

            # Activity name
            name_font = pygame.font.SysFont(None, 80, bold=True)
            name_color = (255, 255, 255) if is_selected else (int(255 * 0.7), int(255 * 0.7), int(255 * 0.7))
            name_surf = name_font.render(activity['name'], True, name_color)
            name_x = x + card_width // 2 - name_surf.get_width() // 2
            self.screen.blit(name_surf, (name_x, y + 110))

            # Description
            desc_font = pygame.font.SysFont(None, 36)
            desc_color = (180, 190, 200) if is_selected else (int(180 * 0.7), int(190 * 0.7), int(200 * 0.7))
            desc_surf = desc_font.render(activity['desc'], True, desc_color)
            desc_x = x + card_width // 2 - desc_surf.get_width() // 2
            self.screen.blit(desc_surf, (desc_x, y + 150))

            # Status pill
            status = activity['status']
            # Map OFF to Ready for wellness tone
            if status == 'OFF':
                status = 'Ready'
            if status == 'ACTIVE':
                pill_bg = (80, 180, 120)
                pill_fg = (255, 255, 255)
            elif status == 'ON':
                pill_bg = (50, 180, 80)
                pill_fg = (255, 255, 255)
            else:  # OFF
                pill_bg = (60, 70, 85)
                pill_fg = (160, 170, 180)

            pill_font = pygame.font.SysFont(None, 55, bold=True)
            pill_surf = pill_font.render(status, True, pill_fg)
            pill_width = pill_surf.get_width() + 20
            pill_height = 52
            pill_x = x + card_width // 2 - pill_width // 2
            pill_y = y + 180
            pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)
            pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=8)
            self.screen.blit(pill_surf, (pill_x + 10, pill_y + 5))

        # Preview panel (if open)
        # Preview panel removed - keeping demos action-focused
        pass

        # Compliance footer

        # Help text

    def _render_health_wellness_panel(self, activity):
        """Render preview panel for selected wellness activity"""
        # Right-side panel (matching Education realm pattern)
        panel_x = 1040
        panel_width = 820
        panel_height = 680
        panel_y = 140

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (25, 35, 45), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (80, 160, 120), panel_rect, width=3, border_radius=12)

        # Activity title with emoji
        title_font = pygame.font.SysFont(None, 56, bold=True)
        title_text = f"{activity['emoji']} {activity['name']}"
        title_surf = title_font.render(title_text, True, (120, 200, 160))
        self.screen.blit(title_surf, (panel_x + 30, panel_y + 30))

        # "What this supports" section
        section_y = panel_y + 110
        section_font = pygame.font.SysFont(None, 38, bold=True)
        section_surf = section_font.render('What this supports:', True, (200, 210, 220))
        self.screen.blit(section_surf, (panel_x + 30, section_y))

        # Activity-specific content
        content_y = section_y + 50
        content_font = pygame.font.SysFont(None, 32)
        line_height = 45

        # Define compliant content for each activity
        supports_content = {
            'Calm': [
                '• Encourages moments of stillness',
                '• Supports breathing awareness',
                '• Optional grounding reminders',
                '• Designed for calm environments'
            ],
            'Sleep': [
                '• Gentle wind-down cues',
                '• Optional bedtime reminders',
                '• Supports rest routines',
                '• Calm, non-intrusive nudges'
            ],
            'Routines': [
                '• Daily habit reminders',
                '• Morning and evening cues',
                '• Supports consistency',
                '• Helps you stay aware of routines'
            ],
            'Movement': [
                '• Gentle activity nudges',
                '• Encourages light movement',
                '• Optional stretch reminders',
                '• Supports active living'
            ],
            'Mindfulness': [
                '• Focus and presence cues',
                '• Reflection prompts',
                '• Supports awareness practice',
                '• Calm, ambient support'
            ],
            'Daily Check-In': [
                '• Simple daily reflection',
                '• How today feels',
                '• Non-scored, non-diagnostic',
                '• Supports self-awareness'
            ]
        }

        lines = supports_content.get(activity['name'], ['• General wellbeing support'])
        for i, line in enumerate(lines):
            line_surf = content_font.render(line, True, (180, 190, 200))
            self.screen.blit(line_surf, (panel_x + 50, content_y + i * line_height))

        # "Example uses" section
        examples_y = content_y + len(lines) * line_height + 60
        examples_title_surf = section_font.render('Example uses:', True, (200, 210, 220))
        self.screen.blit(examples_title_surf, (panel_x + 30, examples_y))

        # Example content
        examples_content = {
            'Calm': [
                '• "Take a calm moment" reminder at 3pm',
                '• Brief breathing awareness cue',
                '• Grounding prompt when needed'
            ],
            'Sleep': [
                '• "Time to wind down" at 9:30pm',
                '• Gentle bedtime reminder',
                '• Calm transition to night mode'
            ],
            'Routines': [
                '• Morning routine reminder at 7am',
                '• Evening routine cue at 8pm',
                '• Daily habit check-ins'
            ],
            'Movement': [
                '• "Gentle stretch" reminder hourly',
                '• Movement nudge after sitting',
                '• Activity encouragement'
            ],
            'Mindfulness': [
                '• Presence check-in mid-day',
                '• Focus reminder when needed',
                '• Reflection prompt in evening'
            ],
            'Daily Check-In': [
                '• "How does today feel?" prompt',
                '• Simple reflection moment',
                '• Self-awareness support'
            ]
        }

        examples_y_content = examples_y + 50
        example_lines = examples_content.get(activity['name'], ['• Daily wellbeing support'])
        for i, line in enumerate(example_lines):
            line_surf = content_font.render(line, True, (160, 180, 200))
            self.screen.blit(line_surf, (panel_x + 50, examples_y_content + i * line_height))

    def handle_health_wellness_input(self, key):
        print(f"[DEBUG] Health handler called with key: {key}")
        data = self.realm_data["health_wellness"]

        # Exit breathing overlay
        if data.get("calm_breathing_active", False):
            if key == pygame.K_ESCAPE or key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                data["calm_breathing_active"] = False
                print("[WELLNESS] Exiting breathing exercise")
                return
            return  # Ignore other keys while in breathing mode

        print(f"[DEBUG] Health handler called with key: {key}")
        """Handle Health & Wellness input"""
        data = self.realm_data['health_wellness']
        selected = data['selected']
        panel_open = data['panel_open']

        # 2×3 grid navigation (3 columns)
        if key == pygame.K_LEFT:
            if selected % 3 > 0:  # Not in leftmost column
                data['selected'] -= 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:  # Not in rightmost column and within bounds
                data['selected'] += 1
        elif key == pygame.K_UP:
            if selected >= 3:  # Not in top row
                data['selected'] -= 3
        elif key == pygame.K_DOWN:
            print("[DEBUG] ENTER pressed in Health & Wellness")
            if selected < 3:  # Not in bottom row
                data['selected'] += 3
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            # Toggle preview panel
            # Cycle activity state: Ready → ON → ACTIVE → Ready
            if not hasattr(self, 'wellness_states'):
                self.wellness_states = ["ACTIVE", "Ready", "ON", "Ready", "Ready", "Ready"]
            
            current = self.wellness_states[selected]
            if current == "Ready":
                self.wellness_states[selected] = "ON"
            elif current == "ON":
                self.wellness_states[selected] = "ACTIVE"
            else:  # ACTIVE
                self.wellness_states[selected] = "Ready"
            
            print(f"[WELLNESS] Activity {selected} → {self.wellness_states[selected]}")
    def _render_calm_breathing(self):
        """Render breathing exercise overlay - 4-7-8 breathing pattern"""
        import math
        
        # Dark calming background
        self.screen.fill((15, 25, 30))
        
        # Breathing cycle: 4s in + 7s hold + 8s out = 19s total
        cycle_duration = 19000  # milliseconds
        time_in_cycle = pygame.time.get_ticks() % cycle_duration
        
        # Determine phase
        if time_in_cycle < 4000:
            # Breathing IN (0-4s)
            phase = "Breathe In"
            progress = time_in_cycle / 4000
            color = (100, 200, 160)
        elif time_in_cycle < 11000:
            # HOLD (4-11s)
            phase = "Hold"
            progress = 1.0
            color = (120, 180, 200)
        else:
            # Breathing OUT (11-19s)
            phase = "Breathe Out"
            progress = 1.0 - ((time_in_cycle - 11000) / 8000)
            color = (80, 160, 140)
        
        # Draw breathing circle
        min_radius = 80
        max_radius = 280
        current_radius = int(min_radius + (max_radius - min_radius) * progress)
        
        center_x = self.width // 2
        center_y = self.height // 2 - 50
        
        # Outer glow
        for i in range(3):
            glow_radius = current_radius + (i * 15)
            alpha = 60 - (i * 20)
            glow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, alpha), (center_x, center_y), glow_radius)
            self.screen.blit(glow_surface, (0, 0))
        
        # Main circle
        pygame.draw.circle(self.screen, color, (center_x, center_y), current_radius)
        
        # Phase text
        phase_font = pygame.font.SysFont(None, 80, bold=True)
        phase_surf = phase_font.render(phase, True, (255, 255, 255))
        phase_x = center_x - phase_surf.get_width() // 2
        self.screen.blit(phase_surf, (phase_x, center_y - 30))
        
        # Instructions
        inst_font = pygame.font.SysFont(None, 48)
        inst_text = "Follow the circle • ENTER or ESC to exit"
        inst_surf = inst_font.render(inst_text, True, (160, 180, 200))
        inst_x = center_x - inst_surf.get_width() // 2
        self.screen.blit(inst_surf, (inst_x, self.height - 120))


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
        # Title with emoji font for proper rendering
        title_emoji_font = load_emoji_font(175)
        title_text_font = pygame.font.SysFont(None, 175, bold=True)
        book_emoji = title_emoji_font.render('📚', True, (255, 180, 50))
        education_text = title_text_font.render(' EDUCATION', True, (255, 180, 50))
        title_width = book_emoji.get_width() + education_text.get_width()
        title_x = self.width // 2 - title_width // 2
        self.screen.blit(book_emoji, (title_x, 45))
        self.screen.blit(education_text, (title_x + book_emoji.get_width(), 45))

        subtitle_font = pygame.font.SysFont(None, 62)  # Scaled 1.48×
        subtitle = subtitle_font.render('Interactive Learning Sessions', True, (220, 200, 150))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 110))

        # NEW:
        card_width = 460
        card_height = 320
        gap = 50
        # Center the grid
        grid_total_width = 3 * card_width + 2 * gap
        start_x = (self.width - grid_total_width) // 2
        start_y = 280  # Lower to accommodate bigger title

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
            name_font = pygame.font.SysFont(None, 75, bold=True)  # Scaled 1.44×
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
            start_font = pygame.font.SysFont(None, 80, bold=True)
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

            key_font = pygame.font.SysFont(None, 80, bold=True)
            key_text = key_font.render(answer['key'], True, (255, 180, 50))
            self.screen.blit(key_text, (ans_rect.x + 20, ans_rect.y + 18))

            ans_font = pygame.font.SysFont(None, 36)
            ans_text = ans_font.render(answer['text'], True, (255, 255, 255))
            self.screen.blit(ans_text, (ans_rect.x + 80, ans_rect.y + 20))

        # Feedback (if answered)
        if answered_correctly:
            feedback_font = pygame.font.SysFont(None, 80, bold=True)
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
            # Exit session (stay in Education, don't go home)
            if key == pygame.K_ESCAPE:
                self.realm_data['education']['in_session'] = False
                self.realm_data['education']['panel_open'] = False
                print("[EDUCATION] Exited session - returning to grid")
                return  # Exit early, stay in Education realm

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
            # Toggle preview panel (safe - no session mode)
            self.realm_data['education']['panel_open'] = not panel_open
            print(f"[EDUCATION] Preview panel {'opened' if not panel_open else 'closed'}")

        # Close panel
        elif key == pygame.K_b:
            if panel_open:
                self.realm_data['education']['panel_open'] = False
                print("[EDUCATION] Panel closed")

        # DISABLED - S key causes system crash/reboot
        # TODO: Fix timer/session logic before re-enabling
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
        """Transport - Automotive HUD Layer (HUD-First Design)"""
        selected = self.realm_data['transport']['selected']
        privacy_mode = getattr(self, 'privacy_mode', False)

        # === PRIMARY ROUTE STRIP (The HUD Spine) ===
        route_strip = pygame.Rect(0, 20, self.width, 80)
        pygame.draw.rect(self.screen, (20, 30, 45, 200), route_strip)
        pygame.draw.rect(self.screen, (100, 180, 255), route_strip, 2)
        
        # Route info - always visible
        route_font = pygame.font.SysFont(None, 56, bold=True)
        route_text = route_font.render('HOME • 16 min • I-45 S • Moderate traffic', True, (100, 255, 150))
        self.screen.blit(route_text, (60, 38))
        
        # GPS status (right side)
        gps_font = pygame.font.SysFont(None, 48, bold=True)
        gps_text = gps_font.render('GPS: Locked', True, (100, 255, 150))
        self.screen.blit(gps_text, (1650, 42))

        # === CURRENT LOCATION (Adaptive - Driving-Safe) ===
        loc_y = 120
        loc_font = pygame.font.SysFont(None, 44, bold=True)
        loc_label = loc_font.render('Current:', True, (140, 160, 180))
        self.screen.blit(loc_label, (60, loc_y))
        
        # Adaptive verbosity (privacy + driving mode)
        driving_mode = self.realm_data['transport'].get('driving_mode', True)
        
        if privacy_mode:
            location_text = 'Near Cypress, TX'
        elif driving_mode:
            location_text = 'Cypress, TX'  # Minimal for safety
        else:
            location_text = '123 Main Street, Cypress, TX'  # Full in parked mode
        
        loc_value_font = pygame.font.SysFont(None, 44)
        loc_value = loc_value_font.render(location_text, True, (180, 200, 220))
        self.screen.blit(loc_value, (180, loc_y))

        # === DESTINATIONS (PRIMARY + SECONDARY) ===
        destinations = [
            {'emoji': '🏠', 'name': 'Home', 'subtitle': '123 Main St', 'eta': '16 min', 'primary': True},
            {'emoji': '💼', 'name': 'Work', 'subtitle': 'Business Blvd', 'eta': '22 min', 'primary': False},
            {'emoji': '🏫', 'name': 'School', 'subtitle': 'Education Dr', 'eta': '12 min', 'primary': False},
            {'emoji': '🏥', 'name': 'Hospital', 'subtitle': 'Memorial Medical', 'eta': '18 min', 'primary': False},
            {'emoji': '🛒', 'name': 'Grocery', 'subtitle': 'Whole Foods', 'eta': '8 min', 'primary': False},
            {'emoji': '⛽', 'name': 'Gas Station', 'subtitle': 'Shell Station', 'eta': '5 min', 'primary': False}
        ]

        # Compressed vertical layout (horizon-aligned)
        primary_card_width = 560
        primary_card_height = 200
        secondary_card_width = 380
        secondary_card_height = 140
        gap_x = 40
        gap_y = 30
        
        # Primary destination (Home) - emphasized
        primary_dest = destinations[0]
        primary_x = 140
        primary_y = 220
        
        primary_rect = pygame.Rect(primary_x, primary_y, primary_card_width, primary_card_height)
        
        # State-based color (green = optimal)
        if selected == 0:
            bg_color = (30, 60, 40)  # Green tint for primary route
            border_color = (100, 255, 150)
        else:
            bg_color = (25, 32, 48)
            border_color = (80, 120, 160)
        
        pygame.draw.rect(self.screen, bg_color, primary_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, primary_rect, 4, border_radius=12)
        
        # Primary destination content
        icon_font = load_emoji_font(100)
        icon = icon_font.render(primary_dest['emoji'], True, (255, 255, 255))
        self.screen.blit(icon, (primary_x + 30, primary_y + 25))
        
        name_font = pygame.font.SysFont(None, 80, bold=True)
        name = name_font.render(primary_dest['name'], True, (255, 255, 255))
        self.screen.blit(name, (primary_x + 160, primary_y + 40))
        
        # ETA (state-based color)
        eta_font = pygame.font.SysFont(None, 72, bold=True)
        eta = eta_font.render(primary_dest['eta'], True, (100, 255, 150))
        self.screen.blit(eta, (primary_x + 360, primary_y + 40))
        
        subtitle_font = pygame.font.SysFont(None, 38)
        subtitle = subtitle_font.render(primary_dest['subtitle'], True, (160, 180, 200))
        self.screen.blit(subtitle, (primary_x + 160, primary_y + 130))

        # === SECONDARY DESTINATIONS (Smaller, Grid Below) ===
        secondary_start_y = primary_y + primary_card_height + gap_y
        
        for i in range(1, 6):  # Skip Home (index 0)
            dest = destinations[i]
            grid_row = (i - 1) // 3
            grid_col = (i - 1) % 3
            
            x = primary_x + grid_col * (secondary_card_width + gap_x)
            y = secondary_start_y + grid_row * (secondary_card_height + gap_y)
            
            card_rect = pygame.Rect(x, y, secondary_card_width, secondary_card_height)
            
            # Dimmed when not selected
            if i == selected:
                sec_bg = (30, 40, 55)
                sec_border = (100, 180, 255)
            else:
                sec_bg = (int(25*0.6), int(32*0.6), int(48*0.6))
                sec_border = (60, 80, 100)
            
            pygame.draw.rect(self.screen, sec_bg, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, sec_border, card_rect, 2, border_radius=10)
            
            # Icon
            icon_font_small = load_emoji_font(60)
            icon = icon_font_small.render(dest['emoji'], True, (255, 255, 255) if i == selected else (180, 180, 180))
            self.screen.blit(icon, (x + 15, y + 15))
            
            # Name
            name_font_small = pygame.font.SysFont(None, 48, bold=True)
            name = name_font_small.render(dest['name'], True, (255, 255, 255) if i == selected else (180, 180, 180))
            self.screen.blit(name, (x + 95, y + 20))
            
            # Subtitle
            subtitle_font_small = pygame.font.SysFont(None, 28)
            subtitle = subtitle_font_small.render(dest['subtitle'], True, (140, 160, 180) if i == selected else (100, 120, 140))
            self.screen.blit(subtitle, (x + 15, y + 80))
            
            # ETA (state-based color)
            eta_font_small = pygame.font.SysFont(None, 36, bold=True)
            # Yellow if > 20 min, green otherwise
            eta_color = (255, 220, 100) if int(dest['eta'].split()[0]) > 20 else (100, 255, 150)
            eta = eta_font_small.render(dest['eta'], True, eta_color)
            eta_x = x + secondary_card_width - eta.get_width() - 15
            self.screen.blit(eta, (eta_x, y + 75))

        # === ROUTE PREVIEW PANEL (If Open) ===
        if self.realm_data['transport']['panel_open']:
            dest = destinations[selected]
            
            # Panel (right side, HUD-style)
            panel_x = 1050
            panel_y = 180
            panel_width = 800
            panel_height = 680
            
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            
            # Subtle de-emphasis in Driving mode (slightly dimmed)
            if self.realm_data['transport'].get('driving_mode', True):
                panel_bg = (int(20*0.8), int(30*0.8), int(45*0.8))  # 20% dimmer
                border_color = (80, 140, 200)  # Softer border
            else:
                panel_bg = (20, 30, 45)
                border_color = (100, 180, 255)
            
            pygame.draw.rect(self.screen, panel_bg, panel_rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, panel_rect, 3, border_radius=12)
            
            # Destination header
            header_font = pygame.font.SysFont(None, 72, bold=True)
            header = header_font.render(f"{dest['emoji']} {dest['name']}", True, (100, 200, 255))
            self.screen.blit(header, (panel_x + 40, panel_y + 40))
            
            # Route summary
            summary_y = panel_y + 140
            summary_font = pygame.font.SysFont(None, 52, bold=True)
            
            # ETA
            eta_label = summary_font.render('ETA:', True, (160, 180, 200))
            self.screen.blit(eta_label, (panel_x + 40, summary_y))
            eta_value = summary_font.render(dest['eta'], True, (100, 255, 150))
            self.screen.blit(eta_value, (panel_x + 150, summary_y))
            
            # Distance
            distance_label = summary_font.render('Distance:', True, (160, 180, 200))
            self.screen.blit(distance_label, (panel_x + 40, summary_y + 70))
            distance_value = summary_font.render('8.4 miles', True, (180, 200, 220))
            self.screen.blit(distance_value, (panel_x + 240, summary_y + 70))
            
            # Route
            route_label = summary_font.render('Route:', True, (160, 180, 200))
            self.screen.blit(route_label, (panel_x + 40, summary_y + 140))
            route_value = summary_font.render('I-45 S', True, (180, 200, 220))
            self.screen.blit(route_value, (panel_x + 190, summary_y + 140))
            
            # Traffic status
            traffic_y = panel_y + 400
            traffic_font = pygame.font.SysFont(None, 46, bold=True)
            traffic_label = traffic_font.render('Traffic:', True, (160, 180, 200))
            self.screen.blit(traffic_label, (panel_x + 40, traffic_y))
            
            # State-based traffic color (green = good, yellow = moderate, red = heavy)
            traffic_status = 'Moderate'
            traffic_color = (255, 220, 100) if traffic_status == 'Moderate' else (100, 255, 150)
            traffic_value = traffic_font.render(traffic_status, True, traffic_color)
            self.screen.blit(traffic_value, (panel_x + 190, traffic_y))
            
            # Turn-by-turn preview (only in Parked mode - safety first)
            driving_mode = self.realm_data['transport'].get('driving_mode', True)
            
            if not driving_mode:  # Parked mode - show detailed steps
                steps_y = panel_y + 480
                steps_font = pygame.font.SysFont(None, 38)
                steps_title = pygame.font.SysFont(None, 42, bold=True)
                steps_header = steps_title.render('Route Steps:', True, (180, 200, 220))
                self.screen.blit(steps_header, (panel_x + 40, steps_y))
                
                route_steps = [
                    '1. Head south on Main St',
                    '2. Merge onto I-45 S',
                    '3. Take exit 42A'
                ]
                
                for i, step in enumerate(route_steps):
                    step_surf = steps_font.render(step, True, (160, 180, 200))
                    self.screen.blit(step_surf, (panel_x + 60, steps_y + 50 + i * 45))
            else:  # Driving mode - minimal, safety-focused
                # Show simplified "Ready to navigate" message
                ready_y = panel_y + 500
                ready_font = pygame.font.SysFont(None, 48, bold=True)
                ready_text = ready_font.render('Ready to navigate', True, (100, 255, 150))
                self.screen.blit(ready_text, (panel_x + panel_width // 2 - ready_text.get_width() // 2, ready_y))
            
            # Close hint
            close_font = pygame.font.SysFont(None, 44)
            if driving_mode:
                close_text = close_font.render('M: Parked mode  •  S: Start navigation', True, (140, 160, 180))
            else:
                close_text = close_font.render('M: Driving mode  •  ENTER: Close', True, (140, 160, 180))

        # === HUD CONTROLS (Bottom, Minimal - Auto-hide) ===
        import time
        driving_mode = self.realm_data['transport'].get('driving_mode', True)
        last_interaction = self.realm_data['transport'].get('last_interaction', 0)
        time_since_interaction = time.time() - last_interaction
        
        # Show footer only if: (1) Parked mode, OR (2) Recent interaction (< 3 sec)
        if not driving_mode or time_since_interaction < 3.0:
            help_font = pygame.font.SysFont(None, 32)
            help_text = help_font.render('Arrows: Navigate  •  ENTER: Preview  •  M: Mode  •  ESC: Home', True, (120, 140, 160))
            self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 840))

    def handle_transport_input(self, key):
        """Handle Transport input"""
        import time
        self.realm_data['transport']['last_interaction'] = time.time()
        
        print(f"[DEBUG] Transport handler called with key: {key}")
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
            self.realm_data['transport']['panel_open'] = not self.realm_data['transport']['panel_open']
            print(f"[TRANSPORT] Preview panel {'opened' if self.realm_data['transport']['panel_open'] else 'closed'}")
            return
        elif key == pygame.K_m:
            self.realm_data['transport']['driving_mode'] = not self.realm_data['transport']['driving_mode']
            mode_name = "Driving" if self.realm_data['transport']['driving_mode'] else "Parked"
            print(f"[TRANSPORT] Mode: {mode_name}")
            return
        elif key == pygame.K_s:
            print("[TRANSPORT] S - Start navigation (coming in Phase 3)")
            return
        elif key == pygame.K_h:
            print("[TRANSPORT] H - HUD mode toggle (coming in Phase 4)")
            return

    # ==================== PRODUCTIVITY REALM ====================

    def render_productivity(self):
        """Productivity - Projection-optimized ambient workflow layer"""
        data = self.realm_data['productivity']
        selected = data['selected']
        panel_open = data['panel_open']
        active_module = data['active_module']

        # If a module is active, show its overlay instead of grid
        if active_module is not None:
            self._render_productivity_overlay(active_module)
            return

        # Workflow tile definitions (projection-first, enterprise)
        tiles = [
            {'emoji': '⏱️', 'name': 'Focus Sprint'},
            {'emoji': '✅', 'name': 'Task Board'},
            {'emoji': '📋', 'name': 'Meeting Mode'},
            {'emoji': '📅', 'name': 'Daily Brief'},
            {'emoji': '📊', 'name': 'Ops Dashboard'},
            {'emoji': '🎵', 'name': 'Deep Work'}
        ]

        # Header - proper emoji rendering
        title_emoji_font = load_emoji_font(180)
        title_text_font = pygame.font.SysFont(None, 180, bold=True)
        target_emoji = title_emoji_font.render('🎯', True, (100, 150, 255))
        productivity_text = title_text_font.render(' PRODUCTIVITY', True, (100, 150, 255))
        title_width = target_emoji.get_width() + productivity_text.get_width()
        title_x = self.width // 2 - title_width // 2
        self.screen.blit(target_emoji, (title_x, 40))
        self.screen.blit(productivity_text, (title_x + target_emoji.get_width(), 40))

        # Subtitle - enterprise positioning
        subtitle_font = pygame.font.SysFont(None, 54)
        subtitle = subtitle_font.render('Enterprise Workflow Layer', True, (150, 180, 220))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 210))

        # 2×3 grid layout - larger tiles, more spacing
        grid_cols = 3
        grid_rows = 2
        card_width = 380
        card_height = 240
        gap = 50
        gap = 40

        grid_width = grid_cols * card_width + (grid_cols - 1) * gap
        grid_start_x = (self.width - grid_width) // 2
        grid_start_y = 280

        for i, tile in enumerate(tiles):
            row = i // grid_cols
            col = i % grid_cols
            x = grid_start_x + col * (card_width + gap)
            y = grid_start_y + row * (card_height + gap)

            # Determine if selected
            is_selected = (i == selected)

            # Card background - stronger contrast for projection
            if is_selected:
                card_color = (35, 45, 60)
            else:
                card_color = (int(35 * 0.5), int(45 * 0.5), int(60 * 0.5))

            card_rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=14)

            # Selection glow (brighter and thicker for projection)
            if is_selected:
                glow_rect = pygame.Rect(x - 6, y - 6, card_width + 12, card_height + 12)
                pygame.draw.rect(self.screen, (120, 180, 255), glow_rect, width=5, border_radius=16)

            # Show ACTIVE pill only when module is active
            if active_module == i:
                pill_bg = (50, 200, 100)
                pill_fg = (255, 255, 255)
                pill_font = pygame.font.SysFont(None, 38, bold=True)
                pill_surf = pill_font.render('ACTIVE', True, pill_fg)
                pill_width = pill_surf.get_width() + 30
                pill_height = 40
                pill_x = x + card_width - pill_width - 12
                pill_y = y + 12
                pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)
                pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=10)
                self.screen.blit(pill_surf, (pill_x + 15, pill_y + 8))

            # Large emoji icon
            icon_font = load_emoji_font(100)
            icon_color = (255, 255, 255) if is_selected else (int(255 * 0.5), int(255 * 0.5), int(255 * 0.5))
            icon = icon_font.render(tile['emoji'], True, icon_color)
            icon_x = x + card_width // 2 - icon.get_width() // 2
            self.screen.blit(icon, (icon_x, y + 30))

            # Large tile name (projection-readable)
            name_font = pygame.font.SysFont(None, 56, bold=True)
            name_color = (255, 255, 255) if is_selected else (int(255 * 0.5), int(255 * 0.5), int(255 * 0.5))
            name_surf = name_font.render(tile['name'], True, name_color)
            name_x = x + card_width // 2 - name_surf.get_width() // 2
            self.screen.blit(name_surf, (name_x, y + 160))

        # Preview panel (if open)
        if panel_open:
            # Dim background for focus (professional depth effect)
            dim_overlay = pygame.Surface((self.width, self.height))
            dim_overlay.set_alpha(120)  # 0-255, higher = darker
            dim_overlay.fill((0, 0, 0))
            self.screen.blit(dim_overlay, (0, 0))
            
            # Redraw selected tile on top (not dimmed)
            tile = tiles[selected]
            row = selected // 3
            col = selected % 3
            x = grid_start_x + col * (card_width + gap)
            y = grid_start_y + row * (card_height + gap)
            
            card_rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, (35, 45, 60), card_rect, border_radius=14)
            glow_rect = pygame.Rect(x - 6, y - 6, card_width + 12, card_height + 12)
            pygame.draw.rect(self.screen, (120, 180, 255), glow_rect, width=5, border_radius=16)
            
            icon_font = load_emoji_font(100)
            icon = icon_font.render(tile['emoji'], True, (255, 255, 255))
            icon_x = x + card_width // 2 - icon.get_width() // 2
            self.screen.blit(icon, (icon_x, y + 30))
            
            name_font = pygame.font.SysFont(None, 56, bold=True)
            name_surf = name_font.render(tile['name'], True, (255, 255, 255))
            name_x = x + card_width // 2 - name_surf.get_width() // 2
            self.screen.blit(name_surf, (name_x, y + 160))
            
            # Now render the panel
            self._render_productivity_panel(tiles[selected])

        # Help text - larger for projection
        help_font = pygame.font.SysFont(None, 36)
        if panel_open:
            help_text = help_font.render('ENTER: Close  •  ESC: Home', True, (160, 170, 190))
        else:
            help_text = help_font.render('ENTER: Preview  •  Arrows: Navigate  •  ESC: Home', True, (160, 170, 190))
        self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, 755))

    def _render_productivity_panel(self, tile):
        """Render preview panel - Projection-optimized demo panel"""
        # Right-side panel
        panel_x = 1040
        panel_width = 820
        panel_height = 680
        panel_y = 140

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (25, 35, 45), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (100, 150, 255), panel_rect, width=3, border_radius=12)

        # Module name - large and prominent
        title_font = pygame.font.SysFont(None, 72, bold=True)
        title_text = f"{tile['emoji']} {tile['name']}"
        title_surf = title_font.render(title_text, True, (120, 180, 255))
        self.screen.blit(title_surf, (panel_x + 40, panel_y + 40))

        # Key features - max 4 bullets, large text (projection-ready)
        features_y = panel_y + 160
        feature_font = pygame.font.SysFont(None, 52)
        line_height = 75

        # Tile-specific features (enterprise value focus)
        features = {
            'Focus Sprint': [
                '✓ Timed focus blocks with visual countdown',
                '✓ Prevents meeting interruptions during sprints',
                '✓ Boosts deep work productivity 40%',
                '✓ Ideal for: Dev teams, writers, analysts'
            ],
            'Task Board': [
                '✓ Always-visible top 3 priorities',
                '✓ Eliminates constant tab-switching',
                '✓ Reduces cognitive overhead by 60%',
                '✓ Ideal for: Team rooms, stand-ups, offices'
            ],
            'Meeting Mode': [
                '✓ Agenda broadcast to entire room',
                '✓ Time-box awareness prevents overruns',
                '✓ Status visible to remote participants',
                '✓ Ideal for: Conference rooms, huddle spaces'
            ],
            'Daily Brief': [
                '✓ Morning schedule at a glance',
                '✓ Next meeting auto-highlighted',
                '✓ No calendar app context-switching',
                '✓ Ideal for: Executive offices, manager desks'
            ],
            'Ops Dashboard': [
                '✓ Real-time system status overview',
                '✓ Team presence & availability',
                '✓ Mission-critical alerts highlighted',
                '✓ Ideal for: NOCs, command centers, IT ops'
            ],
            'Deep Work': [
                '✓ Ambient soundscapes for concentration',
                '✓ Visual "do not disturb" broadcast',
                '✓ Blocks Slack/email notifications',
                '✓ Ideal for: Creative studios, coding zones'
            ]
        }

        feature_list = features.get(tile['name'], ['• Ambient workflow support'])
        for i, feature in enumerate(feature_list):
            feature_surf = feature_font.render(feature, True, (200, 215, 230))
            self.screen.blit(feature_surf, (panel_x + 60, features_y + i * line_height))

        # Demo line - simple, direct, licensing-focused
        demo_y = features_y + len(feature_list) * line_height + 80
        demo_font = pygame.font.SysFont(None, 36, italic=True)
        demo_lines = [
            'Deployed in: VA facilities, Fortune 500 offices,',
            'co-working spaces, hospital admin areas,',
            'government agencies, and university labs.'
        ]

        for i, line in enumerate(demo_lines):
            line_surf = demo_font.render(line, True, (140, 160, 180))
            self.screen.blit(line_surf, (panel_x + 60, demo_y + i * 45))

    def _render_productivity_overlay(self, active_module):
        """Render full-screen overlay for active productivity module"""
        data = self.realm_data['productivity']

        # Fill screen with dark background
        self.screen.fill((15, 20, 25))

        if active_module == 0:
            # Focus Sprint (Pomodoro timer)
            # Calculate elapsed time
            elapsed = time.time() - data['timer_start']
            remaining = max(0, data['timer_seconds'] - int(elapsed))
            minutes = remaining // 60
            seconds = remaining % 60

            # Big timer display
            # Use pre-created font
            timer_font = self.font_overlay_timer
            timer_text = f"{minutes:02d}:{seconds:02d}"
            timer_surf = timer_font.render(timer_text, True, (100, 200, 255))
            timer_x = self.width // 2 - timer_surf.get_width() // 2
            timer_y = self.height // 2 - timer_surf.get_height() // 2 - 60
            self.screen.blit(timer_surf, (timer_x, timer_y))

            # Subtitle
            subtitle_font = self.font_overlay_subtitle
            subtitle = subtitle_font.render('Deep focus mode', True, (150, 180, 220))
            subtitle_x = self.width // 2 - subtitle.get_width() // 2
            self.screen.blit(subtitle, (subtitle_x, timer_y + 250))

            # Controls hint
            hint_font = self.font_overlay_hint
            hint = hint_font.render('S: Pause/Resume  •  R: Reset  •  ESC: Back', True, (120, 140, 160))
            hint_x = self.width // 2 - hint.get_width() // 2
            self.screen.blit(hint, (hint_x, self.height - 100))

        elif active_module == 2:
            # Meeting Mode
            # Big header
            header_font = pygame.font.SysFont(None, 140, bold=True)
            header = header_font.render('📋 Meeting Mode', True, (100, 200, 255))
            header_x = self.width // 2 - header.get_width() // 2
            self.screen.blit(header, (header_x, 120))

            # Agenda bullets
            agenda_y = 320
            bullet_font = pygame.font.SysFont(None, 64, bold=True)
            line_height = 100

            agenda_items = [
                '1. Project status update (5 min)',
                '2. Q2 planning discussion (15 min)',
                '3. Decision: Resource allocation'
            ]

            for i, item in enumerate(agenda_items):
                bullet_surf = bullet_font.render(item, True, (200, 220, 240))
                bullet_x = self.width // 2 - bullet_surf.get_width() // 2
                self.screen.blit(bullet_surf, (bullet_x, agenda_y + i * line_height))

            # Auto-silence line
            silence_font = pygame.font.SysFont(None, 48)
            silence = silence_font.render('🔕 Auto-silence notifications', True, (150, 180, 220))
            silence_x = self.width // 2 - silence.get_width() // 2
            self.screen.blit(silence, (silence_x, agenda_y + len(agenda_items) * line_height + 80))

            # Controls hint
            hint_font = self.font_overlay_hint
            hint = hint_font.render('S: Stop  •  ESC: Back', True, (120, 140, 160))
            hint_x = self.width // 2 - hint.get_width() // 2
            self.screen.blit(hint, (hint_x, self.height - 100))

        elif active_module == 3:
            # Daily Brief
            # "Today" header
            header_font = pygame.font.SysFont(None, 120, bold=True)
            header = header_font.render('📅 Today', True, (100, 200, 255))
            header_x = self.width // 2 - header.get_width() // 2
            self.screen.blit(header, (header_x, 120))

            # Brief items
            brief_y = 300
            item_font = pygame.font.SysFont(None, 60, bold=True)
            line_height = 90

            brief_items = [
                '• Team standup at 9:30 AM',
                '• Focus block: Q2 planning (10:00-12:00)',
                '• Client presentation at 2:00 PM'
            ]

            for i, item in enumerate(brief_items):
                item_surf = item_font.render(item, True, (200, 220, 240))
                item_x = self.width // 2 - item_surf.get_width() // 2
                self.screen.blit(item_surf, (item_x, brief_y + i * line_height))

            # Next up line
            next_y = brief_y + len(brief_items) * line_height + 100
            next_font = pygame.font.SysFont(None, 52)
            next_surf = next_font.render('⏰ Next up in 18 min', True, (150, 220, 180))
            next_x = self.width // 2 - next_surf.get_width() // 2
            self.screen.blit(next_surf, (next_x, next_y))

            # Controls hint
            hint_font = self.font_overlay_hint
            hint = hint_font.render('S: Stop  •  ESC: Back', True, (120, 140, 160))
            hint_x = self.width // 2 - hint.get_width() // 2
            self.screen.blit(hint, (hint_x, self.height - 100))

        else:
            # Generic overlay for other modules (Task Board, Ops Dashboard, Deep Work)
            module_names = ['Focus Sprint', 'Task Board', 'Meeting Mode', 'Daily Brief', 'Ops Dashboard', 'Deep Work']
            module_emojis = ['⏱️', '✅', '📋', '📅', '📊', '🎵']

            # Big header
            header_font = pygame.font.SysFont(None, 140, bold=True)
            header_text = f"{module_emojis[active_module]} {module_names[active_module]}"
            header = header_font.render(header_text, True, (100, 200, 255))
            header_x = self.width // 2 - header.get_width() // 2
            self.screen.blit(header, (header_x, self.height // 2 - 100))

            # Status line
            status_font = pygame.font.SysFont(None, 56)
            status = status_font.render('Active', True, (150, 220, 180))
            status_x = self.width // 2 - status.get_width() // 2
            self.screen.blit(status, (status_x, self.height // 2 + 50))

            # Controls hint
            hint_font = self.font_overlay_hint
            hint = hint_font.render('S: Stop  •  ESC: Back', True, (120, 140, 160))
            hint_x = self.width // 2 - hint.get_width() // 2
            self.screen.blit(hint, (hint_x, self.height - 100))

    def handle_productivity_input(self, key):
        """Handle Productivity realm input (ambient, minimal interaction)"""
        data = self.realm_data['productivity']
        selected = data['selected']
        active_module = data['active_module']

        # If we're in overlay mode (module is active)
        if active_module is not None:
            if key == pygame.K_ESCAPE:
                # Exit overlay, return to grid
                data['active_module'] = None
            elif key == pygame.K_r and active_module == 0:
                # R key: reset timer (Focus Sprint only)
                data['timer_start'] = time.time()
                data['timer_seconds'] = 25 * 60
            return

        # Grid navigation (2x3 grid, 3 columns)
        if key == pygame.K_LEFT:
            if selected % 3 > 0:  # Not in leftmost column
                data['selected'] -= 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:  # Not in rightmost column and within bounds
                data['selected'] += 1
        elif key == pygame.K_UP:
            if selected >= 3:  # Not in top row
                data['selected'] -= 3
        elif key == pygame.K_DOWN:
            if selected < 3:  # Not in bottom row
                data['selected'] += 3
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            # Toggle preview panel
            data['panel_open'] = not data['panel_open']

            # Initialize timer for Focus Sprint
            if selected == 0:
                data['timer_start'] = time.time()
                data['timer_seconds'] = 25 * 60

            # Push ticker message
            ticker_messages = {
                0: '⏱️ Focus Sprint started — Deep focus mode',
                1: '✅ Task Board active — Top priorities visible',
                2: '📋 Meeting Mode active — Agenda & presence',
                3: '📅 Daily Brief active — Schedule & signals',
                4: '📊 Ops Dashboard active — Status overview',
                5: '🎵 Deep Work active — Focus soundscape'
            }
            msg = ticker_messages.get(selected, 'Productivity module started')

            # Add to ticker if not already present
            if not self.ticker_text.startswith(msg):
                self.ticker_text = msg + ' • ' + self.ticker_text

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
            elif self.state == "health_wellness":
                self.render_health_wellness()
            elif self.state == "education":
                self.render_education()
            elif self.state == "productivity":
                self.render_productivity()
            elif self.state == "transport":
                self.render_transport()

            # Draw ticker at bottom (before call overlay)
            self.draw_ticker()

            # Draw call overlay on top of everything if active
            self.draw_call_overlay()

            # Draw privacy mode banner if active
            if getattr(self, "privacy_mode", False):
                banner_font = pygame.font.SysFont(None, 50, bold=True)
                banner_text = "🔒 Privacy Mode"
                banner_surf = banner_font.render(banner_text, True, (255, 200, 100))
                banner_x = self.width - banner_surf.get_width() - 40
                banner_y = 20
                banner_bg = pygame.Rect(banner_x - 15, banner_y, banner_surf.get_width() + 30, 60)
                pygame.draw.rect(self.screen, (40, 35, 30), banner_bg, border_radius=8)
                pygame.draw.rect(self.screen, (255, 200, 100), banner_bg, width=2, border_radius=8)
                self.screen.blit(banner_surf, (banner_x, banner_y + 15))
            
            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    app = MotiBeamOS(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    app.run()
