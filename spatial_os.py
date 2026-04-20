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
import queue
import threading
import sys as _sys
import queue
import threading
_sys.path.insert(0, '/home/motibeam')
try:
    from voice_pipeline import VoicePipeline
    VOICE_ENABLED = True
except Exception as e:
    print(f"[Voice] Pipeline not available: {e}")
    VOICE_ENABLED = False
try:
    from presence_node import PresenceNode
    PRESENCE_ENABLED = True
except Exception as e:
    print(f"[Presence] Not available: {e}")
    PRESENCE_ENABLED = False
import time
import pygame
import requests
import json
from datetime import datetime

# ---------------------------
# Emoji Font Loading with Fallback
# ---------------------------


# ── Global font cache — prevents per-frame SysFont crashes on Pi 4 ──
_FONT_CACHE = {}
def get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(None, size, bold=bold)
    return _FONT_CACHE[key]

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

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_COLS = 3
GRID_ROWS = 2

BG_COLOR = (10, 12, 20)
CARD_BG = (26, 30, 48)
CARD_BORDER = (80, 90, 140)
CARD_BORDER_SELECTED = (255, 200, 80)
HEADER_COLOR = (230, 235, 245)
FOOTER_COLOR = (200, 205, 215)
TEXT_PRIMARY = (245, 248, 255)
TEXT_SECONDARY = (170, 175, 190)

REALMS = [
    {"name": "CircleBeam",      "subtitle": "Family presence",    "emoji": "👥"},
    {"name": "Home",            "subtitle": "Smart home",         "emoji": "🏠"},
    {"name": "Education",       "subtitle": "Learning hub",       "emoji": "📚"},
    {"name": "Health & Wellness","subtitle": "Daily wellbeing",   "emoji": "🌿"},
    {"name": "Productivity",    "subtitle": "Focus & Awareness",  "emoji": "🎯"},
    {"name": "Marketplace",     "subtitle": "Wellness & goods",   "emoji": "🛒"},
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
    # Initialize audio mixer for voice tones — route to 3.5mm jack (card 2)
    import os as _os
    _os.environ['SDL_AUDIODRIVER'] = 'alsa'
    _os.environ['AUDIODEV'] = 'hw:2,0'
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024, devicename='hw:2,0')
        print("  ✓ Audio mixer initialized on hw:2,0")
    except Exception as _me:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            print("  ✓ Audio mixer initialized (default)")
        except Exception as _me2:
            print(f"  Audio mixer failed: {_me2} — voice tones disabled")
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
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
        self.font_header_meta = get_font(36)  # Was 30
        self.font_emoji = get_font(80)  # System font for sharp text
        self.font_card_title = get_font(48)  # Was 34
        self.font_card_subtitle = pygame.font.SysFont(None, 31)  # Was 22
        self.font_footer = get_font(34)  # Was 24
        # Overlay fonts (for demo mode)
        self.font_overlay_timer = pygame.font.SysFont(None, 240, bold=True)
        self.font_overlay_subtitle = get_font(56)
        self.font_overlay_hint = get_font(36)
        # Overlay fonts (for demo mode)
        self.font_overlay_timer = pygame.font.SysFont(None, 240, bold=True)
        self.font_overlay_subtitle = get_font(56)
        self.font_overlay_hint = get_font(36)

        self.clock = pygame.time.Clock()
        # Voice pipeline
        self.voice_queue = queue.Queue()
        if VOICE_ENABLED:
            self.voice = VoicePipeline(self.voice_queue)
            try:
                self.voice.start()
            except Exception as e:
                print(f"[Voice] Start failed: {e} — running without voice")
                self.voice = None
        else:
            self.voice = None

        # Presence client
        self.presence_queue = queue.Queue()
        if PRESENCE_ENABLED:
            self.presence = PresenceNode(my_port=5555, peer_host="192.168.1.156", peer_port=5557, node_name="Pi4")
            self.presence.start(event_queue=self.presence_queue)
        else:
            self.presence = None
        self.selected_index = 0  # which card is selected on home grid
        self.circlebeam_active = False
        self.circlebeam_target = None
        self._cb_hint_time     = 0   # tracks last interaction for nav fade
        self.corner_alert = None
        self.corner_alert_time = 0

        # Navigation system
        self.state = "home"
        self.navigation_stack = ["home"]

        # Realm-specific state data
        self.realm_data = {
            'circlebeam': {
                'selected': 0,
                'panel_open': False,
                'action_feedback': None,
                'action_time': 0,
                'presence_state': None,
                'presence_target': None,
                'presence_emoji':  None,
                'presence_start':  0,
                'presence_status': None,
                'nav_hint_time':   0,
            },
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
                'module': None,
                'preview_open': False,
                'flashcard_index': 0,
                'flashcard_revealed': False,
                'math_index': 0,
                'math_answered': False,
                'math_selected': None,
                'vocab_index': 0,
                'vocab_revealed': False,
                'quiz_index': 0,
                'quiz_selected': None,
                'quiz_answered': False,
                'quiz_score': 0,
                'timer_running': False,
                'timer_mode': 0,
                'timer_start': 0,
                'timer_elapsed': 0,
                'ambient_mode': False,
                'ambient_start': 0,
                'last_input_time': 0,
                'live_question': None,
                'live_question_active': False,
                'live_answered': False,
                'live_correct': None,
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
        self.ticker_text = "MotiBeam OS — Loading... "
        self.ticker_offset = 0
        # Weather cache
        self._weather_text = ""
        self._start_time = __import__("time").time()
        self._weather_last  = 0
        self._weather_thread = None
        # Weather fetched lazily after 30s
        self._weather_last = 0
        self.ticker_speed = 2  # pixels per frame

        # System state (ALERT vs CALM)
        self.system_state = "CALM"  # or "ALERT"

        # Precompute grid cell sizes (adjusted for alert banner and ticker)
        self.grid_top = 160  # Was 140, pushed down for alert banner
        self.grid_bottom = self.height - 120  # Adjusted for ticker (60px footer + 56px ticker + 45px margin)
        available_height = self.grid_bottom - self.grid_top
        available_width = self.width - 180

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
        logo_font = get_font(80, bold=True)
        subtitle_font = get_font(48)
        version_font = get_font(36)

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
            # Use cached overlay surface — no per-frame Surface creation
            if not hasattr(self, '_dim_overlay'):
                self._dim_overlay = pygame.Surface((self.width, self.height))
                self._dim_overlay.set_alpha(25)
                self._dim_overlay.fill((0, 0, 0))
            self.screen.blit(self._dim_overlay, (0, 0))

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
            alert_font = get_font(95, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 18))
            
            # Priority badge (left side)
            priority_font = get_font(32, bold=True)
            priority_text = priority_font.render('CRITICAL', True, (255, 255, 255))
            self.screen.blit(priority_text, (20, 25))
            
            # Dismissal hint (right side)
            hint_font = get_font(28)
            hint_text = hint_font.render('Auto-dismiss in 2 min', True, (255, 220, 220))
            self.screen.blit(hint_text, (self.width - 280, 28))
            
        else:
            # Normal alerts
            banner_height = 55
            banner_rect = pygame.Rect(0, 0, self.width, banner_height)
            pygame.draw.rect(self.screen, alert['color'], banner_rect)

            alert_font = get_font(75, bold=True)
            alert_surf = alert_font.render(alert['message'], True, (255, 255, 255))
            text_x = (self.width - alert_surf.get_width()) // 2
            self.screen.blit(alert_surf, (text_x, 15))
            
            # Priority badge for severe weather
            if alert['type'] == 'severe':
                priority_font = get_font(28, bold=True)
                priority_text = priority_font.render('IMPORTANT', True, (255, 255, 255))
                self.screen.blit(priority_text, (15, 20))
            else:
                # Info level for messages
                priority_font = get_font(28, bold=True)
                priority_text = priority_font.render('INFO', True, (255, 255, 255))
                self.screen.blit(priority_text, (15, 20))

    def draw_state_indicator(self):
        """Draw STATE indicator in top right corner of alert banner"""
        if not self.alert_enabled:
            return  # Don't draw if alerts are disabled

        state_color = (255, 255, 255) if self.system_state == "ALERT" else (255, 255, 255)
        state_font = get_font(26, bold=True)
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

        # Scrolling text — cached font (never create fonts per frame)
        if not hasattr(self, '_ticker_font'):
            self._ticker_font = get_font(70)
        ticker_surf = self._ticker_font.render(self.ticker_text, True, (180, 200, 220))

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

        # Semi-transparent overlay — cached
        if not hasattr(self, '_call_overlay'):
            self._call_overlay = pygame.Surface((self.width, self.height))
            self._call_overlay.set_alpha(200)
            self._call_overlay.fill((20, 25, 35))
        self.screen.blit(self._call_overlay, (0, 0))

        # Call card
        card_width = 640
        card_height = 480
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, (35, 40, 55), card_rect, border_radius=20)
        pygame.draw.rect(self.screen, (100, 180, 255), card_rect, width=4, border_radius=20)

        # Header text
        header_font = get_font(42, bold=True)
        header_surf = header_font.render('Incoming Presence Call', True, (100, 180, 255))
        header_x = card_x + (card_width - header_surf.get_width()) // 2
        self.screen.blit(header_surf, (header_x, card_y + 30))

        # Caller emoji (large) - use emoji font for proper rendering
        caller_emoji_font = load_emoji_font(180)
        caller_emoji = caller_emoji_font.render(self.call_caller['emoji'], True, (255, 255, 255))
        emoji_x = card_x + (card_width - caller_emoji.get_width()) // 2
        self.screen.blit(caller_emoji, (emoji_x, card_y + 100))

        # Caller name
        name_font = get_font(72, bold=True)
        display_name = 'Contact' if getattr(self, 'privacy_mode', False) else self.call_caller['name']
        name_surf = name_font.render(display_name, True, (255, 255, 255))
        name_x = card_x + (card_width - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, card_y + 260))

        # Subtext
        subtext_font = get_font(36)
        subtext_surf = subtext_font.render('Tap to connect or dismiss', True, (180, 200, 220))
        subtext_x = card_x + (card_width - subtext_surf.get_width()) // 2
        self.screen.blit(subtext_surf, (subtext_x, card_y + 320))

        # Action buttons
        button_y = card_y + 380

        # Accept button
        accept_rect = pygame.Rect(card_x + 100, button_y, 200, 56)
        pygame.draw.rect(self.screen, (50, 200, 100), accept_rect, border_radius=10)
        accept_font = get_font(42, bold=True)
        accept_text = accept_font.render('Accept (A)', True, (255, 255, 255))
        accept_x = accept_rect.centerx - accept_text.get_width() // 2
        accept_y = accept_rect.centery - accept_text.get_height() // 2
        self.screen.blit(accept_text, (accept_x, accept_y))

        # Decline button
        decline_rect = pygame.Rect(card_x + 340, button_y, 200, 56)
        pygame.draw.rect(self.screen, (200, 50, 50), decline_rect, border_radius=10)
        decline_font = get_font(42, bold=True)
        decline_text = decline_font.render('Decline (D)', True, (255, 255, 255))
        decline_x = decline_rect.centerx - decline_text.get_width() // 2
        decline_y = decline_rect.centery - decline_text.get_height() // 2
        self.screen.blit(decline_text, (decline_x, decline_y))

    def draw_grid(self):
        for i, realm in enumerate(REALMS):
            row = i // GRID_COLS
            col = i % GRID_COLS

            x = 110 + col * self.cell_w
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

            # Emoji icon - sized to fit tile with room for text
            emoji_font = load_emoji_font(90)
            icon_surf = emoji_font.render(realm["emoji"], True, TEXT_PRIMARY)

            # Calculate total stack height to center vertically in tile
            title_surf = self.font_card_title.render(realm["name"], True, TEXT_PRIMARY)
            subtitle_surf = self.font_card_subtitle.render(realm["subtitle"], True, TEXT_SECONDARY)
            gap1, gap2 = 6, 4
            total_h = icon_surf.get_height() + gap1 + title_surf.get_height() + gap2 + subtitle_surf.get_height()
            start_y = card_rect.centery - total_h // 2

            # Emoji
            ex = card_rect.centerx - icon_surf.get_width() // 2
            self.screen.blit(icon_surf, (ex, start_y))

            # Title
            tx = card_rect.centerx - title_surf.get_width() // 2
            ty = start_y + icon_surf.get_height() + gap1
            self.screen.blit(title_surf, (tx, ty))

            # Subtitle
            sx = card_rect.centerx - subtitle_surf.get_width() // 2
            sy = ty + title_surf.get_height() + gap2
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
            self._cb_hint_time = __import__('time').time()

    def go_back(self):
        """Navigate back one level"""
        if len(self.navigation_stack) > 1:
            self.navigation_stack.pop()
            self.state = self.navigation_stack[-1]
            print(f"[NAVIGATE] Back to {self.state}")
            return True
        return False

    def _fetch_weather(self):
        """Fetch weather for Cypress TX in background thread"""
        import threading, time as _t2
        def _do_fetch():
            try:
                import urllib.request
                url = 'https://wttr.in/Cypress+TX?format=%t+%C&u'
                req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.0'})
                with urllib.request.urlopen(req, timeout=8) as r:
                    raw = r.read().decode('utf-8').strip()
                    raw = raw.split('\n')[0].strip()
                    self._weather_text = f"Cypress TX  {raw}"
            except Exception:
                self._weather_text = "Cypress TX  Weather unavailable"
            self._weather_last = _t2.time()
        try:
            t = threading.Thread(target=_do_fetch, daemon=True)
            t.start()
        except Exception:
            self._weather_text = "Cypress TX  Weather unavailable"
            self._weather_last = _t2.time()

    def _build_ticker(self):
        """Build live ticker text from system state"""
        import time as _t3
        # Refresh weather every 10 min
        if _t3.time() - self._weather_last > 600:
            self._fetch_weather()

        parts = []

        # Weather
        parts.append(self._weather_text)

        # CircleBeam status
        if getattr(self, 'presence', None):
            parts.append("CircleBeam: Connected")
        else:
            parts.append("CircleBeam: Standby")

        # Home mode
        home_mode = self.realm_data.get('home_realm', {}).get('ambient_mode', 'home')
        mode_labels = {'home': 'Home: Secure', 'away': 'Home: Away Mode', 'night': 'Home: Night Watch'}
        parts.append(mode_labels.get(home_mode, 'Home: Active'))

        # Active marketplace experiences
        if hasattr(self, 'active_experiences') and self.active_experiences:
            exp_names = {
                'breathing': 'Guided Breathing Active',
                'focus':     'Focus Mode Active',
                'decor':     'Holiday Lights Active',
                'education': 'Flashcards Active',
                'security':  'Front Door Pack Active',
                'motivation':'Morning Motivation Active',
            }
            for key, label in exp_names.items():
                if self.active_experiences.get(key):
                    parts.append(label)

        # Temperature from home realm
        thermo = self.realm_data.get('home_realm', {}).get('_thermo_base', 71.0)
        import math as _mth
        import time as _t4
        drift = _mth.sin(_t4.time() * 0.04) * 1.8
        temp  = thermo + drift
        parts.append(f"Indoor Temp: {temp:.1f}F")

        # Any active home alert
        home_state = self.realm_data.get('home_realm', {}).get('home_state', 'IDLE')
        if home_state != 'IDLE':
            event = self.realm_data.get('home_realm', {}).get('event')
            if event:
                parts.append(f"ALERT: {event.get('passive', 'Event active')}")

        return "   →   ".join(parts) + "   →   "

    def handle_key(self, key):
        # Q always quits
        if key == pygame.K_q:
            # Require CTRL+SHIFT+Q to quit - prevents accidental exit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT]:
                pygame.quit()
                sys.exit(0)
            return

        # ESC behavior depends on current state

        # T toggles ticker visibility
        if key == pygame.K_t:
            self.ticker_visible = not getattr(self, "ticker_visible", True)
            print(f"[TICKER] Ticker {'visible' if self.ticker_visible else 'hidden'}")
            return
        
        # P toggles privacy mode
        if key == pygame.K_p:
            self.privacy_mode = not getattr(self, "privacy_mode", False)
            print(f"[PRIVACY] Privacy mode {'ON' if self.privacy_mode else 'OFF'}")
            return   
        
        if key == pygame.K_ESCAPE:
            if self.state == "home":
                return  # ESC fully disabled on home screen
            elif self.state == "home_realm":
                return  # home_realm handles ESC via _home_poll_keys
            # Don't go back if Education is in session mode - let realm handler deal with it
            elif self.state == "education" and self.realm_data['education'].get('module') is not None:
                pass  # Education handler will process this
            # CircleBeam handles ESC internally (panel close, presence exit, then realm exit)
            elif self.state == "circlebeam":
                pass  # CircleBeam handler will process this
            else:
                self.go_back()
                return

        # Alert banner toggle (L = toggle aLerts)
        if key == pygame.K_l:
            self.alert_enabled = not self.alert_enabled
            import time
            self.alert_change_time = time.time()
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
                1: "home_realm",
                2: "education",
                3: "health_wellness",
                4: "productivity",
                5: "marketplace",
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
        import math as _cm, time as _ct
        cd       = self.realm_data['circlebeam']
        selected = cd['selected']
        pstate   = cd.get('presence_state')

        # Route to presence flow if active
        if pstate in ('calling', 'connecting', 'connected', 'active'):
            self._render_circlebeam_presence(cd)
            return

        # Title — compact to give grid more room
        title_emoji_font = load_emoji_font(64)
        title_text_font  = get_font(64, bold=True)
        people_emoji     = title_emoji_font.render('👥', True, (100, 180, 255))
        circlebeam_text  = title_text_font.render(' CIRCLEBEAM', True, (100, 180, 255))
        title_width = people_emoji.get_width() + circlebeam_text.get_width()
        title_x     = self.width // 2 - title_width // 2
        self.screen.blit(people_emoji,    (title_x, 28))
        self.screen.blit(circlebeam_text, (title_x + people_emoji.get_width(), 28))

        # Subtitle
        subtitle_font = get_font(36)
        subtitle = subtitle_font.render('Family Presence', True, (140, 165, 195))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 105))

        # ── CONTACT DATA ──────────────────────────────────────────
        circles = [
            {'name': 'Mom',       'status': 'available',       'emoji': '👩', 'status_text': 'Available',       'dot': '●'},
            {'name': 'Dad',       'status': 'quiet',           'emoji': '👨', 'status_text': 'Quiet mode',      'dot': '●'},
            {'name': 'Sister',    'status': 'offline',         'emoji': '👧', 'status_text': 'Offline',         'dot': '●'},
            {'name': 'Brother',   'status': 'available',       'emoji': '👦', 'status_text': 'Available',       'dot': '●'},
            {'name': 'Grandma',   'status': 'needs_attention', 'emoji': '👵', 'status_text': 'Needs attention', 'dot': '●'},
            {'name': 'Care Team', 'status': 'available',       'emoji': '⚕️', 'status_text': 'Available',       'dot': '●'},
        ]
        status_colors = {
            'available':       (100, 255, 150),
            'quiet':           (120, 180, 255),
            'offline':         (140, 150, 160),
            'needs_attention': (255, 100, 100),
        }

        # ── GRID ──────────────────────────────────────────────────
        card_w, card_h = 320, 185
        gap_x, gap_y   = 48, 20
        cols           = 3
        grid_w         = cols * card_w + (cols - 1) * gap_x
        start_x        = (self.width - grid_w) // 2
        start_y        = 136
        now_t          = _ct.time()

        for i, circle in enumerate(circles):
            row = i // cols
            col = i % cols
            x   = start_x + col * (card_w + gap_x)
            y   = start_y + row * (card_h + gap_y)
            card_rect = pygame.Rect(x, y, card_w, card_h)

            if circle['status'] == 'needs_attention':
                _na = (_cm.sin(now_t * 1.8) + 1) / 2
                _gs = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
                _gs.fill((255, 80, 80, int(35 + _na * 45)))
                self.screen.blit(_gs, (x - 10, y - 10))

            if i == selected:
                _br = (_cm.sin(now_t * 2.0) + 1) / 2
                _gr = int(80  + _br * 80)
                _gg = int(160 + _br * 60)
                _bw = int(3   + _br * 3)
                _inf = int(5  + _br * 7)
                pygame.draw.rect(self.screen, (_gr, _gg, 255),
                                 card_rect.inflate(_inf, _inf), _bw, border_radius=15)
            elif circle['status'] == 'needs_attention':
                _na2 = (_cm.sin(now_t * 1.8) + 1) / 2
                pygame.draw.rect(self.screen, (255, int(60+_na2*40), 60),
                                 card_rect.inflate(4, 4), int(2+_na2*2), border_radius=15)

            if circle['status'] == 'offline':
                bg_col = (18, 20, 30)
            elif i == selected:
                bg_col = (30, 36, 54)
            else:
                bg_col = (22, 26, 40)
            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=13)

            icon_font = load_emoji_font(88)
            icon = icon_font.render(circle['emoji'], True, (255, 255, 255))
            if circle['status'] == 'offline':
                icon.set_alpha(110)
            self.screen.blit(icon, (x + card_w//2 - icon.get_width()//2, y + 14))

            nc  = (155, 160, 170) if circle['status'] == 'offline' else (232, 238, 255)
            ns0 = get_font(44, bold=True).render(circle['name'], True, nc)
            self.screen.blit(ns0, (x + card_w//2 - ns0.get_width()//2, y + 116))

            sc = status_colors[circle['status']]
            if circle['status'] in ('available', 'needs_attention'):
                _dp = (_cm.sin(now_t * 2.5 + i) + 1) / 2
                _dc = tuple(min(255, int(c*(0.55+_dp*0.45))) for c in sc)
            else:
                _dc = sc
            dots = get_font(36, bold=True).render('●', True, _dc)
            sts  = get_font(28).render(circle['status_text'], True, sc)
            sw   = dots.get_width() + 5 + sts.get_width()
            sx   = x + (card_w - sw) // 2
            self.screen.blit(dots, (sx, y + 152))
            self.screen.blit(sts,  (sx + dots.get_width() + 5, y + 156))

        # ── BOTTOM OVERLAY PANEL ──────────────────────────────────
        if cd['panel_open']:
            person       = circles[selected]
            status_color = status_colors[person['status']]
            panel_h = 205
            panel_y = self.height - panel_h - 46
            panel_x = 34
            panel_w = self.width - 68
            margin  = 26

            ps2 = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            ps2.fill((12, 16, 32, 238))
            self.screen.blit(ps2, (panel_x, panel_y))
            pygame.draw.rect(self.screen, status_color,
                             pygame.Rect(panel_x, panel_y, panel_w, 3), border_radius=3)
            pygame.draw.rect(self.screen, (52, 78, 126),
                             pygame.Rect(panel_x, panel_y, panel_w, panel_h), 2, border_radius=10)

            av2  = load_emoji_font(85).render(person['emoji'], True, (255, 255, 255))
            ax2  = panel_x + margin
            ay2  = panel_y + (panel_h - av2.get_height()) // 2
            self.screen.blit(av2, (ax2, ay2))

            tx2  = ax2 + av2.get_width() + 16
            priv = getattr(self, 'privacy_mode', False)
            dn2  = (person['name'][0]+'.') if priv else person['name']
            pns  = get_font(46, bold=True).render(dn2, True, (243, 246, 255))
            self.screen.blit(pns, (tx2, panel_y + 26))

            expl2 = {
                'available':       'Available for contact',
                'quiet':           'Quiet mode — notifications paused',
                'offline':         'Not currently connected',
                'needs_attention': 'Urgent — please check in',
            }
            pes = get_font(31, bold=True).render(expl2[person['status']], True, status_color)
            self.screen.blit(pes, (tx2, panel_y + 86))

            sm2 = {0:'2h ago',1:'30m ago',2:'Yesterday',3:'1h ago',4:'15m ago',5:'Available now'}
            st2 = '🔒 Privacy' if priv else f"Last seen: {sm2.get(selected,'—')}"
            sc2 = (255,220,100) if priv else (148,162,182)
            self.screen.blit(get_font(28).render(st2, True, sc2), (tx2, panel_y + 134))

            acts2 = [
                {'key':'C','label':'Call',    'color':(100,200,255)},
                {'key':'M','label':'Message', 'color':(150,255,150)},
                {'key':'N','label':'Nudge',   'color':(255,200,100)},
            ]
            bw3,bh3,bg3 = 178,56,14
            tbw3 = len(acts2)*bw3+(len(acts2)-1)*bg3
            bsx3 = panel_x+panel_w-margin-tbw3
            by3  = panel_y+(panel_h-bh3)//2
            kf3  = get_font(34, bold=True)
            lf3  = get_font(32)
            for idx3, act3 in enumerate(acts2):
                bx3 = bsx3+idx3*(bw3+bg3)
                br3 = pygame.Rect(bx3, by3, bw3, bh3)
                pygame.draw.rect(self.screen, (26,33,52), br3, border_radius=9)
                pygame.draw.rect(self.screen, act3['color'], br3, 2, border_radius=9)
                ks3 = kf3.render(act3['key'],   True, act3['color'])
                ls3 = lf3.render(act3['label'], True, (202,208,218))
                self.screen.blit(ks3, (bx3+11, by3+(bh3-ks3.get_height())//2))
                self.screen.blit(ls3, (bx3+11+ks3.get_width()+9, by3+(bh3-ls3.get_height())//2))

            if cd['action_feedback']:
                import time as _fbt
                if _fbt.time()-cd['action_time'] < 2.0:
                    fbs2 = get_font(34, bold=True).render(cd['action_feedback'], True, (100,255,150))
                    self.screen.blit(fbs2,(panel_x+panel_w//2-fbs2.get_width()//2, panel_y+panel_h-38))
                else:
                    cd['action_feedback'] = None

            hs4 = get_font(24).render('ENTER or ESC to close', True, (88,102,132))
            self.screen.blit(hs4,(panel_x+panel_w-hs4.get_width()-margin, panel_y+panel_h-hs4.get_height()-7))

        # ── FOOTER — auto-fade after 4s inactivity ─────────────────
        _ht = getattr(self, '_cb_hint_time', 0)
        _age = _ct.time() - _ht
        _fade_dur = 1.2
        _show_dur = 4.0
        if _age < _show_dur:
            _halpha = 255
        elif _age < _show_dur + _fade_dur:
            _halpha = int(255 * (1.0 - (_age - _show_dur) / _fade_dur))
        else:
            _halpha = 0
        if _halpha > 0:
            _hsurf = get_font(28).render(
                '← → ↑ ↓  Navigate   |   ENTER  Open   |   C  Call   M  Message   N  Nudge   |   ESC  Back',
                True, (100, 115, 145))
            _hsurf.set_alpha(_halpha)
            self.screen.blit(_hsurf, (self.width//2 - _hsurf.get_width()//2, self.height - 88))

    def _render_circlebeam_presence(self, cd):
        """Presence flow: calling → connecting → connected → active"""
        import math as _pm, time as _pt
        pstate  = cd['presence_state']
        name    = cd.get('presence_target', '')
        emoji   = cd.get('presence_emoji',  '👤')
        elapsed = _pt.time() - cd.get('presence_start', _pt.time())
        W, H    = self.width, self.height
        cx      = W // 2

        if pstate == 'calling'    and elapsed > 1.4:
            cd['presence_state'] = 'connecting'
            cd['presence_start'] = _pt.time()
            return
        if pstate == 'connecting' and elapsed > 1.8:
            cd['presence_state'] = 'connected'
            cd['presence_start'] = _pt.time()
            self.circlebeam_active = True
            self.circlebeam_target = name
            self._cb_presence_start = _pt.time()
            # Sound hook: soft connected cue
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.stop()
            except Exception:
                pass
            return
        if pstate == 'connected'  and elapsed > 1.2:
            cd['presence_state'] = 'active'
            cd['presence_start'] = _pt.time()
            return

        pulse  = (_pm.sin(_pt.time() * 1.6) + 1) / 2
        pulse2 = (_pm.sin(_pt.time() * 0.5) + 1) / 2

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((8,10,20,245) if pstate=='active' else (10,14,26,215))
        self.screen.blit(dim, (0, 0))

        if pstate == 'calling':
            ring_r = int(88+pulse*18)
            rs = pygame.Surface((ring_r*2+4,ring_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(rs,(100,180,255,int(55+pulse*80)),(ring_r+2,ring_r+2),ring_r,3)
            self.screen.blit(rs,(cx-ring_r-2,H//2-185-ring_r-2))
            av = load_emoji_font(138).render(emoji,True,(255,255,255))
            self.screen.blit(av,(cx-av.get_width()//2,H//2-285))
            cv = int(195+pulse*60)
            cs = get_font(66,bold=True).render('Calling...', True,(cv,cv,255))
            self.screen.blit(cs,(cx-cs.get_width()//2,H//2-58))
            ns = get_font(50).render(name,True,(175,198,228))
            self.screen.blit(ns,(cx-ns.get_width()//2,H//2+22))
            dc = int(_pt.time()*1.5)%4
            ds = get_font(40).render('●'*dc+'○'*(3-dc),True,(75,125,195))
            self.screen.blit(ds,(cx-ds.get_width()//2,H//2+88))

        elif pstate == 'connecting':
            for ri in range(3):
                rr = int(68+ri*44+pulse*24)
                ra = max(0,int(78-ri*20+pulse*28))
                rsurf = pygame.Surface((rr*2+4,rr*2+4),pygame.SRCALPHA)
                pygame.draw.circle(rsurf,(78,158,255,ra),(rr+2,rr+2),rr,2)
                self.screen.blit(rsurf,(cx-rr-2,H//2-162-rr-2))
            av2 = load_emoji_font(118).render(emoji,True,(255,255,255))
            self.screen.blit(av2,(cx-av2.get_width()//2,H//2-252))
            cv2 = int(175+pulse*78)
            cs2 = get_font(60,bold=True).render('Connecting...',True,(cv2,cv2,255))
            self.screen.blit(cs2,(cx-cs2.get_width()//2,H//2-48))
            ss3 = get_font(36).render('CircleBeam: Establishing presence',True,(95,145,208))
            self.screen.blit(ss3,(cx-ss3.get_width()//2,H//2+28))

        elif pstate == 'connected':
            av3 = load_emoji_font(128).render(emoji,True,(255,255,255))
            self.screen.blit(av3,(cx-av3.get_width()//2,H//2-262))
            gv = int(175+pulse*78)
            cs3 = get_font(70,bold=True).render('Connected',True,(75,gv,135))
            self.screen.blit(cs3,(cx-cs3.get_width()//2,H//2-48))
            ss4 = get_font(40).render('Live Circle Active',True,(95,198,148))
            self.screen.blit(ss4,(cx-ss4.get_width()//2,H//2+36))
            ns2 = get_font(46).render(name,True,(198,218,242))
            self.screen.blit(ns2,(cx-ns2.get_width()//2,H//2+92))

        elif pstate == 'active':
            aura_r = int(128+pulse2*28)
            sk = cd.get('presence_status','available')
            ac = {'available':(78,198,118),'quiet':(78,138,255),
                  'offline':(118,128,138),'needs_attention':(255,78,78)}.get(sk,(78,178,255))
            for layer in range(4):
                lr = aura_r+layer*22
                la = max(0,int(18+pulse2*22)-layer*4)
                asurf = pygame.Surface((lr*2,lr*2),pygame.SRCALPHA)
                pygame.draw.circle(asurf,(*ac,la),(lr,lr),lr)
                self.screen.blit(asurf,(cx-lr,H//2-202-lr))
            av4 = load_emoji_font(168).render(emoji,True,(255,255,255))
            self.screen.blit(av4,(cx-av4.get_width()//2,H//2-332))
            pv = int(208+pulse2*47)
            ps3 = get_font(62,bold=True).render(f'{name} is present',True,(pv,pv,255))
            self.screen.blit(ps3,(cx-ps3.get_width()//2,H//2-28))
            # Secondary emotional line
            ev2 = int(140+pulse2*40)
            es2 = get_font(36).render(f'Live with {name}',True,(ev2,ev2+30,ev2+20))
            self.screen.blit(es2,(cx-es2.get_width()//2,H//2+42))
            lv5 = int(100+pulse2*40)
            ls5 = get_font(28).render('Live presence active',True,(60,lv5,90))
            self.screen.blit(ls5,(cx-ls5.get_width()//2,H//2+92))
            # ESC hint — fades with inactivity
            _ph = getattr(self, '_cb_hint_time', 0)
            _page = _pt.time() - _ph
            _pa = 255 if _page < 4.0 else max(0,int(255*(1-(_page-4.0)/1.2)))
            if _pa > 0:
                ef = get_font(26).render('ESC  End presence   |   H  Go to Home',True,(78,88,112))
                ef.set_alpha(_pa)
                self.screen.blit(ef,(cx-ef.get_width()//2,H-98))

    def handle_circlebeam_input(self, key):
        """Handle CircleBeam input — grid nav, panel, presence flow"""
        import time as _cht
        cd       = self.realm_data['circlebeam']
        selected = cd['selected']
        cols     = 3
        total    = 6
        pstate   = cd.get('presence_state')

        circles = [
            {'name': 'Mom',       'status': 'available',       'emoji': '👩'},
            {'name': 'Dad',       'status': 'quiet',           'emoji': '👨'},
            {'name': 'Sister',    'status': 'offline',         'emoji': '👧'},
            {'name': 'Brother',   'status': 'available',       'emoji': '👦'},
            {'name': 'Grandma',   'status': 'needs_attention', 'emoji': '👵'},
            {'name': 'Care Team', 'status': 'available',       'emoji': '⚕️'},
        ]

        # Presence active — ESC/B ends, H goes to Home keeping session alive
        if pstate in ('calling', 'connecting', 'connected', 'active'):
            if key in (pygame.K_ESCAPE, pygame.K_b):
                cd['presence_state']  = None
                cd['presence_target'] = None
                self.circlebeam_active = False
                self.circlebeam_target = None
                print('[CIRCLEBEAM] Presence ended')
                self.state = "home"
                self.navigation_stack = ["home"]
            elif key == pygame.K_h:
                # Go to Home while keeping presence session alive
                self.state = "home"
                self.navigation_stack = ["home", "circlebeam"]
                print('[CIRCLEBEAM] Moved to Home — presence still active')
            return

        # Panel open — action keys
        if cd['panel_open']:
            if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                cd['panel_open'] = False
                return
            elif key == pygame.K_c:
                person = circles[selected]
                cd['panel_open']      = False
                cd['presence_state']  = 'calling'
                cd['presence_target'] = person['name']
                cd['presence_emoji']  = person['emoji']
                cd['presence_status'] = person['status']
                cd['presence_start']  = _cht.time()
                self._cb_hint_time    = _cht.time()
                # Sound hook: soft call-start cue
                try:
                    if pygame.mixer.get_init():
                        pass  # wire tone here: pygame.mixer.Sound('assets/call_start.wav').play()
                except Exception:
                    pass
                print(f'[CIRCLEBEAM] Call → {person["name"]}')
                return
            elif key == pygame.K_m:
                cd['action_feedback'] = '✓ Message sent'
                cd['action_time']     = _cht.time()
                return
            elif key == pygame.K_n:
                cd['action_feedback'] = '✓ Nudge sent'
                cd['action_time']     = _cht.time()
                return
            return

        # Reset nav hint timer on any interaction
        self._cb_hint_time = _cht.time()

        # Grid navigation
        if key == pygame.K_LEFT:
            if selected % cols > 0:
                cd['selected'] = selected - 1
        elif key == pygame.K_RIGHT:
            if selected % cols < cols - 1 and selected < total - 1:
                cd['selected'] = selected + 1
        elif key == pygame.K_UP:
            if selected >= cols:
                cd['selected'] = selected - cols
        elif key == pygame.K_DOWN:
            if selected + cols < total:
                cd['selected'] = selected + cols
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            cd['panel_open'] = True
            print(f'[CIRCLEBEAM] Panel → {circles[selected]["name"]}')
        elif key == pygame.K_ESCAPE:
            self.state = "home"
            self.navigation_stack = ["home"]

    def render_marketplace(self):
        """Marketplace - Projection Experience Platform — Upgraded"""
        import math as _m
        import time as _t
        data     = self.realm_data['marketplace']
        selected = data.get('selected', 0)
        installed= data.get('installed', set())
        preview  = data.get('preview_open', False)
        prev_idx = data.get('preview_idx', 0)
        activating = data.get('activating', False)
        act_start  = data.get('act_start', 0)
        now      = _t.time()
        pulse    = (_m.sin(now * 0.8) + 1) / 2
        pulse2   = (_m.sin(now * 1.6) + 1) / 2

        W, H = self.width, self.height
        cx, cy = W//2, H//2

        pxs = [
            {
                'name': 'Guided Breathing',
                'category': 'Wellness',
                'desc': 'Calm your space with ambient breath cycles',
                'color': (60, 180, 200),
                'key': 'breathing',
                'preview': 'breathing',
            },
            {
                'name': 'Morning Motivation',
                'category': 'Wellness',
                'desc': 'Daily affirmations projected at sunrise',
                'color': (220, 160, 50),
                'key': 'motivation',
                'preview': 'motivation',
            },
            {
                'name': 'Kids Flashcards',
                'category': 'Education',
                'desc': 'Interactive learning on any wall surface',
                'color': (80, 200, 120),
                'key': 'education',
                'preview': 'flashcards',
            },
            {
                'name': 'Focus Timer Theme',
                'category': 'Productivity',
                'desc': 'Deep work environment with ambient visuals',
                'color': (100, 140, 220),
                'key': 'focus',
                'preview': 'focus',
            },
            {
                'name': 'Holiday Lights',
                'category': 'Seasonal',
                'desc': 'Festive projection decor for any room',
                'color': (220, 80, 80),
                'key': 'decor',
                'preview': 'holiday',
            },
            {
                'name': 'Front Door Pack',
                'category': 'Security',
                'desc': 'Enhanced visitor alerts and response flows',
                'color': (200, 130, 50),
                'key': 'security',
                'preview': 'security',
            },
        ]

        if not hasattr(self, '_mf'):
            self._mf = {
                'title': get_font(72, bold=True),
                'sub':   get_font(36),
                'name':  get_font(44, bold=True),
                'cat':   get_font(30),
                'desc':  get_font(32),
                'hint':  get_font(28),
                'big':   get_font(90, bold=True),
                'med':   get_font(56, bold=True),
                'label': get_font(34),
                'small': get_font(30),
            }
        titf = self._mf['title']
        subf = self._mf['sub']
        namf = self._mf['name']
        catf = self._mf['cat']
        desf = self._mf['desc']
        hif  = self._mf['hint']
        bigf = self._mf['big']
        medf = self._mf['med']
        lblf = self._mf['label']
        smf  = self._mf['small']

        # ── Active experiences global state ───────────────────────
        if not hasattr(self, 'active_experiences'):
            self.active_experiences = {}

        # ══════════════════════════════════════════════════════════
        # ACTIVATION ANIMATION
        # ══════════════════════════════════════════════════════════
        if activating:
            elapsed = now - act_start
            if elapsed > 1.0:
                data['activating'] = False
                data['preview_open'] = False
                return
            px  = pxs[prev_idx]
            ac  = px['color']
            self.screen.fill((6, 8, 14))
            # Expanding rings
            for ri in range(5):
                rr = int(elapsed * 400 + ri * 80)
                ra = max(0, 80 - int(rr * 0.12) - ri*8)
                if ra > 0 and rr > 0 and rr < 700:
                    rc = (min(255,ac[0]//2+ra), min(255,ac[1]//2+ra), min(255,ac[2]//2+ra))
                    pygame.draw.circle(self.screen, rc, (cx, cy), rr, width=2)
            # Activated text
            av = int(elapsed * 255)
            if av > 0:
                ms = medf.render('Activated', True, (min(255,av), min(255,av), min(255,av)))
                self.screen.blit(ms, (cx-ms.get_width()//2, cy-30))
                ns = lblf.render(px['name'], True, (min(255,ac[0]), min(255,ac[1]), min(255,ac[2])))
                self.screen.blit(ns, (cx-ns.get_width()//2, cy+40))
            return

        # ══════════════════════════════════════════════════════════
        # PREVIEW MODE — animated per experience type
        # ══════════════════════════════════════════════════════════
        if preview and 0 <= prev_idx < len(pxs):
            px      = pxs[prev_idx]
            ac      = px['color']
            ptype   = px['preview']
            is_inst = px['name'] in installed

            self.screen.fill((6, 8, 14))

            # ── Guided Breathing ──────────────────────────────────
            if ptype == 'breathing':
                breath_cycle = 6.0
                t_in_cycle   = now % breath_cycle
                if t_in_cycle < 2.5:
                    phase = t_in_cycle / 2.5
                    label = 'Breathe In...'
                elif t_in_cycle < 3.5:
                    phase = 1.0
                    label = 'Hold...'
                else:
                    phase = 1.0 - (t_in_cycle - 3.5) / 2.5
                    label = 'Breathe Out...'
                r = int(60 + phase * 160)
                alpha_val = int(40 + phase * 60)
                for ri in range(4):
                    rr2 = r - ri * 18
                    if rr2 > 0:
                        cv = alpha_val - ri*8
                        if cv > 0:
                            cc = (min(255,ac[0]//3+cv), min(255,ac[1]//3+cv), min(255,ac[2]//3+cv))
                            pygame.draw.circle(self.screen, cc, (cx, cy), rr2, width=2)
                pygame.draw.circle(self.screen, (min(255,ac[0]//2+80),min(255,ac[1]//2+80),min(255,ac[2]//2+80)), (cx,cy), r-8)
                ls = medf.render(label, True, (200,220,240))
                self.screen.blit(ls, (cx-ls.get_width()//2, cy+200))

            # ── Motivation ────────────────────────────────────────
            elif ptype == 'motivation':
                quotes = ['You are capable.', 'Today is yours.', 'Stay focused.', 'Make it happen.']
                qi     = int(now / 3) % len(quotes)
                fade   = (_m.sin(now * _m.pi / 3) + 1) / 2
                tv2    = int(120 + fade * 135)
                qs     = bigf.render(quotes[qi], True, (tv2, int(tv2*0.9), int(tv2*0.6)))
                self.screen.blit(qs, (cx-qs.get_width()//2, cy-40))
                # Subtle sunburst lines
                for li in range(12):
                    angle = li * 30 * _m.pi / 180 + now * 0.1
                    llen  = int(80 + pulse * 30)
                    lx1   = cx + int(_m.cos(angle) * 40)
                    ly1   = cy - 60 + int(_m.sin(angle) * 40)
                    lx2   = cx + int(_m.cos(angle) * (40+llen))
                    ly2   = cy - 60 + int(_m.sin(angle) * (40+llen))
                    lv    = int(30 + pulse * 20)
                    pygame.draw.line(self.screen, (lv+int(ac[0]*0.3), lv+int(ac[1]*0.2), lv), (lx1,ly1), (lx2,ly2), 1)

            # ── Flashcards ────────────────────────────────────────
            elif ptype == 'flashcards':
                cards = [('5 x 6 = ?','30'),('A is for...','Apple'),('3 + 7 = ?','10'),('What is H2O?','Water')]
                ci    = int(now / 4) % len(cards)
                q, a  = cards[ci]
                t_in  = now % 4
                show_a = t_in > 2.0
                # Card
                cw4, ch4 = 500, 280
                pygame.draw.rect(self.screen, (18,22,32), (cx-cw4//2, cy-ch4//2, cw4, ch4), border_radius=16)
                pygame.draw.rect(self.screen, ac, (cx-cw4//2-2,cy-ch4//2-2,cw4+4,ch4+4), width=2, border_radius=18)
                qs2 = medf.render(q, True, (220,230,245))
                self.screen.blit(qs2, (cx-qs2.get_width()//2, cy-50))
                if show_a:
                    av2 = min(255, int((t_in-2.0)*300))
                    ac2 = (min(255,ac[0]), min(255,ac[1]), min(255,ac[2]))
                    ans = bigf.render(a, True, (av2,av2,av2))
                    self.screen.blit(ans, (cx-ans.get_width()//2, cy+20))

            # ── Focus ─────────────────────────────────────────────
            elif ptype == 'focus':
                # Minimal dark room with slow particles
                for pi2 in range(6):
                    px2 = int((W*(0.1+pi2*0.15) + _m.sin(now*0.1+pi2)*20)) % W
                    py2 = int((H*(0.2+pi2*0.12) + _m.cos(now*0.08+pi2)*15)) % H
                    pv2 = int(20 + pulse*15)
                    pygame.draw.circle(self.screen,(min(255,ac[0]//3+pv2),min(255,ac[1]//3+pv2),min(255,ac[2]//3+pv2)),(px2,py2),2)
                ms3 = bigf.render('Deep Focus', True, (int(160+pulse*40),int(170+pulse*30),int(200+pulse*25)))
                self.screen.blit(ms3, (cx-ms3.get_width()//2, cy-50))
                ts4 = medf.render('25:00', True, (80,100,160))
                self.screen.blit(ts4, (cx-ts4.get_width()//2, cy+60))

            # ── Holiday ───────────────────────────────────────────
            elif ptype == 'holiday':
                colors_h = [(220,60,60),(60,180,60),(220,180,50),(60,120,220),(180,60,180)]
                for hi in range(18):
                    hx = int(W*(0.05+hi*0.055) + _m.sin(now*0.4+hi*0.7)*12)
                    hy = int(H*(0.2+hi*0.04) + _m.sin(now*0.6+hi*0.5)*20)
                    hc = colors_h[hi % len(colors_h)]
                    hv = int(100+_m.sin(now*1.2+hi)*80)
                    hr = int(6+_m.sin(now*0.8+hi)*3)
                    pygame.draw.circle(self.screen,(min(255,hc[0]//2+hv//2),min(255,hc[1]//2+hv//2),min(255,hc[2]//2+hv//2)),(hx,hy),hr)
                ms4 = medf.render("Season's Greetings", True, (220,180,80))
                self.screen.blit(ms4, (cx-ms4.get_width()//2, cy-20))

            # ── Security ──────────────────────────────────────────
            elif ptype == 'security':
                for ri2 in range(3):
                    rphase = now*0.8 + ri2*1.0
                    rr3    = int(80+ri2*90+_m.sin(rphase)*15)
                    rv     = int(60+_m.sin(rphase)*40)
                    pygame.draw.circle(self.screen,(min(255,ac[0]//2+rv),min(255,ac[1]//4+rv//2),0),(cx,cy),rr3,width=2)
                ms5 = medf.render('Front Door Awareness', True, (220,160,80))
                self.screen.blit(ms5, (cx-ms5.get_width()//2, cy-30))
                ss5 = lblf.render('Enhanced alerts enabled', True, (120,100,60))
                self.screen.blit(ss5, (cx-ss5.get_width()//2, cy+40))

            # ── Common preview chrome ─────────────────────────────
            # Top: category + name
            pygame.draw.rect(self.screen, ac, (0,0,W,3))
            cat_s = catf.render(px['category'].upper(), True, ac)
            cw5   = cat_s.get_width()+22
            pygame.draw.rect(self.screen,(ac[0]//4,ac[1]//4,ac[2]//4),(cx-cw5//2,18,cw5,34),border_radius=8)
            pygame.draw.rect(self.screen,ac,(cx-cw5//2-1,17,cw5+2,36),width=1,border_radius=8)
            self.screen.blit(cat_s,(cx-cat_s.get_width()//2,24))
            ns2 = namf.render(px['name'], True, (220,225,240))
            self.screen.blit(ns2, (cx-ns2.get_width()//2, 60))

            # Bottom: activate button
            btn_txt = 'Deactivate' if is_inst else 'Activate'
            btn_c   = (50,160,80) if is_inst else ac
            bw3,bh3 = 240,56
            bx3     = cx-bw3//2
            by3     = H-110
            pygame.draw.rect(self.screen,(btn_c[0]//4,btn_c[1]//4,btn_c[2]//4),(bx3,by3,bw3,bh3),border_radius=10)
            pygame.draw.rect(self.screen,btn_c,(bx3-2,by3-2,bw3+4,bh3+4),width=2,border_radius=12)
            bs2 = lblf.render(btn_txt, True, (255,255,255))
            self.screen.blit(bs2,(bx3+bw3//2-bs2.get_width()//2,by3+bh3//2-bs2.get_height()//2))

            hint = hif.render('SPACE: Activate / Deactivate   ESC: Back', True, (45,50,65))
            self.screen.blit(hint,(cx-hint.get_width()//2,H-44))
            return

        # ══════════════════════════════════════════════════════════
        # MAIN GRID
        # ══════════════════════════════════════════════════════════
        self.screen.fill((6, 8, 14))

        # Top gradient
        for gy2 in range(100):
            av3 = int((1-gy2/100)*14)
            pygame.draw.line(self.screen,(av3,av3,av3*2),(0,gy2),(W,gy2))

        # Header
        ts5 = titf.render('MARKETPLACE', True, (200,170,255))
        self.screen.blit(ts5,(W//2-ts5.get_width()//2,26))
        ss6 = subf.render('Projection Experience Platform', True, (80,65,110))
        self.screen.blit(ss6,(W//2-ss6.get_width()//2,100))
        pygame.draw.line(self.screen,(40,32,60),(80,132),(W-80,132),1)

        # Active experience count indicator
        act_count = len(self.active_experiences) if hasattr(self,'active_experiences') else 0
        if act_count > 0:
            ac_lbl = smf.render(f'{act_count} Active', True, (60,180,90))
            pygame.draw.rect(self.screen,(15,40,20),(W-130,22,110,32),border_radius=8)
            self.screen.blit(ac_lbl,(W-125,28))

        # Grid
        cols2,rows2 = 3,2
        cw6,ch6     = 360,166
        gx6,gy6     = 30,26
        sw6         = cols2*cw6+(cols2-1)*gx6
        sx6         = W//2-sw6//2
        sy6         = 148

        for i,px3 in enumerate(pxs):
            col6   = i%cols2
            row6   = i//cols2
            x6     = sx6+col6*(cw6+gx6)
            y6     = sy6+row6*(ch6+gy6)
            is_sel = (i==selected)
            is_inst2 = px3['name'] in installed
            ac5    = px3['color']

            bg6 = (16,18,28) if is_sel else (10,11,18)
            pygame.draw.rect(self.screen,bg6,(x6,y6,cw6,ch6),border_radius=10)

            if is_sel:
                bv3 = int(100+pulse*90)
                bc5 = (min(255,ac5[0]//2+bv3//2),min(255,ac5[1]//2+bv3//2),min(255,ac5[2]//2+bv3//2))
                pygame.draw.rect(self.screen,bc5,(x6-2,y6-2,cw6+4,ch6+4),width=2,border_radius=12)
            else:
                pygame.draw.rect(self.screen,(20,22,32),(x6-1,y6-1,cw6+2,ch6+2),width=1,border_radius=10)

            # Color top bar
            bar_c2 = ac5 if is_sel else (ac5[0]//3,ac5[1]//3,ac5[2]//3)
            pygame.draw.rect(self.screen,bar_c2,(x6,y6,cw6,3),border_radius=2)

            # Category
            cl2 = catf.render(px3['category'], True, (ac5[0]//2+50,ac5[1]//2+50,ac5[2]//2+50))
            self.screen.blit(cl2,(x6+14,y6+10))

            # Name
            nc2 = (240,245,255) if is_sel else (150,160,180)
            nl2 = namf.render(px3['name'],True,nc2)
            self.screen.blit(nl2,(x6+14,y6+38))

            # Desc
            dt  = px3['desc'][:42]+('...' if len(px3['desc'])>42 else '')
            dl2 = desf.render(dt,True,(55,60,78))
            self.screen.blit(dl2,(x6+14,y6+86))

            # Status badge
            if is_inst2:
                badge_c2 = (40,150,65)
                badge_t2 = 'Active'
            else:
                badge_c2 = (40,42,58)
                badge_t2 = 'Available'
            bt2  = smf.render(badge_t2,True,badge_c2)
            btw2 = bt2.get_width()+14
            pygame.draw.rect(self.screen,(badge_c2[0]//4,badge_c2[1]//4,badge_c2[2]//4),(x6+cw6-btw2-8,y6+ch6-30,btw2,22),border_radius=5)
            self.screen.blit(bt2,(x6+cw6-btw2-1,y6+ch6-27))

        hint3 = hif.render('Arrow Keys: Navigate   ENTER: Preview   SPACE: Activate   ESC: Back', True,(36,38,54))
        self.screen.blit(hint3,(W//2-hint3.get_width()//2,H-32))

    def handle_marketplace_input(self, key):
        """Marketplace input"""
        data     = self.realm_data['marketplace']
        selected = data.get('selected', 0)
        preview  = data.get('preview_open', False)
        px_names = ['Guided Breathing','Morning Motivation','Kids Flashcards',
                    'Focus Timer Theme','Holiday Lights','Front Door Pack']
        px_keys  = ['breathing','motivation','education','focus','decor','security']

        if not hasattr(self, 'active_experiences'):
            self.active_experiences = {}

        if data.get('activating'):
            return

        if preview:
            if key in (pygame.K_b, pygame.K_ESCAPE):
                data['preview_open'] = False
            elif key == pygame.K_SPACE:
                import time as _t2
                px_name = px_names[data.get('preview_idx',0)]
                px_key  = px_keys[data.get('preview_idx',0)]
                inst    = data.get('installed', set())
                if px_name in inst:
                    inst.discard(px_name)
                    self.active_experiences.pop(px_key, None)
                else:
                    inst.add(px_name)
                    self.active_experiences[px_key] = True
                data['installed']   = inst
                data['activating']  = True
                data['act_start']   = _t2.time()
            return

        if key == pygame.K_LEFT:
            if selected % 3 > 0: data['selected'] = selected-1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5: data['selected'] = selected+1
        elif key == pygame.K_UP:
            if selected >= 3: data['selected'] = selected-3
        elif key == pygame.K_DOWN:
            if selected < 3: data['selected'] = selected+3
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            data['preview_open'] = True
            data['preview_idx']  = selected
        elif key == pygame.K_SPACE:
            import time as _t3
            px_name = px_names[selected]
            px_key  = px_keys[selected]
            inst    = data.get('installed', set())
            if px_name in inst:
                inst.discard(px_name)
                self.active_experiences.pop(px_key, None)
            else:
                inst.add(px_name)
                self.active_experiences[px_key] = True
            data['installed']  = inst
            data['preview_idx']= selected
            data['activating'] = True
            import time as _t4
            data['act_start']  = _t4.time()
        elif key in (pygame.K_b, pygame.K_ESCAPE):
            self.go_back()


    def _home_poll_keys(self):
        """Poll keys every frame — no focus dependency"""
        import time as _t
        data  = self.realm_data['home_realm']
        now   = _t.time()
        last  = data.get('_last_key_time', 0)
        if now - last < 0.18:   # 180ms debounce
            return
        keys = pygame.key.get_pressed()

        def hit(k):
            return keys[k]

        fired = None
        if hit(pygame.K_1):       fired = '1'
        elif hit(pygame.K_2):     fired = '2'
        elif hit(pygame.K_3):     fired = '3'
        elif hit(pygame.K_4):     fired = '4'
        elif hit(pygame.K_h):     fired = 'h'
        elif hit(pygame.K_a):     fired = 'a'
        elif hit(pygame.K_n):     fired = 'n'
        elif hit(pygame.K_RETURN) or hit(pygame.K_KP_ENTER): fired = 'enter'
        elif hit(pygame.K_ESCAPE): fired = 'esc'
        elif hit(pygame.K_r):     fired = 'r'
        elif hit(pygame.K_b):     fired = 'b'
        elif hit(pygame.K_LEFT):  fired = 'left'
        elif hit(pygame.K_RIGHT): fired = 'right'

        if fired:
            data['_last_key_time'] = now
            self._home_handle(fired)

    def _home_handle(self, key):
        """Clean Home realm input handler"""
        import time as _t
        data  = self.realm_data['home_realm']
        state = data.get('home_state', 'IDLE')
        mode  = data.get('ambient_mode', 'home')

        def fire_event(etype):
            events = {
                'garage_open': {
                    'type': 'garage_open',
                    'passive': 'Garage door opened',
                    'medium': 'Garage Door Opened',
                    'medium_sub': 'No motion detected inside',
                    'priority': 'GARAGE OPEN',
                    'priority_sub': 'Check your garage',
                    'color': (200, 170, 60),
                    'escalate': 'MEDIUM',
                },
                'motion_detected': {
                    'type': 'motion_detected',
                    'passive': 'Motion — Backyard',
                    'medium': 'Motion Detected',
                    'medium_sub': 'Backyard sensor triggered',
                    'priority': 'MOTION DETECTED',
                    'priority_sub': 'Backyard — Review activity',
                    'color': (80, 160, 220),
                    'escalate': 'MEDIUM',
                },
                'visitor_front_door': {
                    'type': 'visitor_front_door',
                    'passive': 'Doorbell activity detected',
                    'medium': 'Someone Rang Your Doorbell',
                    'medium_sub': 'Motion at front door',
                    'priority': 'SOMEONE AT YOUR DOOR',
                    'priority_sub': 'FRONT DOOR',
                    'color': (255, 110, 60),
                    'escalate': 'PRIORITY',
                },
                'water_leak': {
                    'type': 'water_leak',
                    'passive': 'Moisture sensor triggered',
                    'medium': 'Water Leak Detected',
                    'medium_sub': 'Kitchen sensor',
                    'priority': 'WATER LEAK DETECTED',
                    'priority_sub': 'KITCHEN — Act immediately',
                    'color': (60, 180, 220),
                    'escalate': 'PRIORITY',
                },
            }
            ev = events.get(etype)
            if ev:
                data['event'] = ev
                data['home_state'] = 'PASSIVE_ALERT'
                data['alert_start'] = _t.time()
                data['btn_sel'] = 0

        def clear():
            data['home_state'] = 'IDLE'
            data['event'] = None
            data['btn_sel'] = 0
            data['_auto_fired'] = False

        # ── State: IDLE ──
        if state == 'IDLE':
            if key == '1':   fire_event('garage_open')
            elif key == '2': fire_event('motion_detected')
            elif key == '3': fire_event('visitor_front_door')
            elif key == '4': fire_event('water_leak')
            elif key == 'h': data['ambient_mode'] = 'home'
            elif key == 'a': data['ambient_mode'] = 'away'
            elif key == 'n': data['ambient_mode'] = 'night'
            elif key in ('esc', 'b'):
                self.state = 'home'
                self.navigation_stack = ['home']

        # ── State: PASSIVE_ALERT ──
        elif state == 'PASSIVE_ALERT':
            if key == 'esc':   clear()
            elif key == 'enter': data['home_state'] = 'MEDIUM_ALERT'

        # ── State: MEDIUM_ALERT ──
        elif state == 'MEDIUM_ALERT':
            if key == 'esc':   clear()
            elif key == 'enter':
                ev = data.get('event', {})
                if ev.get('escalate') == 'PRIORITY':
                    data['home_state'] = 'PRIORITY_ALERT'

        # ── State: PRIORITY_ALERT ──
        elif state == 'PRIORITY_ALERT':
            if key == 'left':  data['btn_sel'] = max(0, data.get('btn_sel', 0) - 1)
            elif key == 'right': data['btn_sel'] = min(1, data.get('btn_sel', 0) + 1)
            elif key == 'esc': clear()
            elif key in ('enter', 'r'):
                btn = data.get('btn_sel', 0)
                ev  = data.get('event', {})
                if btn == 0 or key == 'r':  # Respond
                    if ev.get('type') == 'visitor_front_door':
                        self.incoming_call   = True
                        self.incoming_caller = 'Front Door'
                    data['home_state'] = 'CIRCLEBEAM_RESPONSE'
                    data['cb_start']   = _t.time()
                else:
                    clear()

        # ── State: CIRCLEBEAM_RESPONSE ──
        elif state == 'CIRCLEBEAM_RESPONSE':
            if key in ('esc', 'b', 'enter'): clear()

    def render_home_realm(self):
        """Home - Ambient Awareness Engine — OEM Edition"""
        import time as _t, math, datetime
        data   = self.realm_data['home_realm']
        mode   = data.get('ambient_mode', 'home')
        state  = data.get('home_state', 'IDLE')
        event  = data.get('event')
        now    = _t.time()
        now_dt = datetime.datetime.now()
        hour   = now_dt.hour
        pulse  = (math.sin(now * 0.6) + 1) / 2
        pulse2 = (math.sin(now * 1.3) + 1) / 2
        pulse3 = (math.sin(now * 0.25) + 1) / 2

        # ── Auto-escalate ─────────────────────────────────────────
        alert_start = data.get('alert_start', now)
        elapsed     = now - alert_start
        if state == 'PASSIVE_ALERT' and elapsed > 2.0:
            data['home_state'] = 'MEDIUM_ALERT'
            state = 'MEDIUM_ALERT'
        if state == 'MEDIUM_ALERT' and elapsed > 5.0:
            if event and event.get('escalate') == 'PRIORITY':
                data['home_state'] = 'PRIORITY_ALERT'
                state = 'PRIORITY_ALERT'

        # Auto-fire disabled — idle screen is the ambient living wall

        # ── Init & poll ───────────────────────────────────────────
        if data.get('_last_key_time', 0) == 0:
            data['_last_key_time'] = now
            data['_auto_fired'] = False
        self._home_poll_keys()

        # ── Font cache ────────────────────────────────────────────
        if not hasattr(self, '_hf'):
            self._hf = {
                'time':  get_font(120, bold=True),
                'sub':   get_font(40),
                'greet': get_font(44),
                'head':  pygame.font.SysFont(None, 54, bold=True),
                'body':  get_font(40),
                'small': get_font(32),
                'hint':  pygame.font.SysFont(None, 27),
                'huge':  get_font(108, bold=True),
                'giant': get_font(84, bold=True),
                'med':   get_font(44),
                'label': get_font(28),
            }
        tf  = self._hf['time']
        sf  = self._hf['sub']
        grf = self._hf['greet']
        hf  = self._hf['head']
        bf  = self._hf['body']
        smf = self._hf['small']
        hif = self._hf['hint']
        huf = self._hf['huge']
        gif = self._hf['giant']
        mf  = self._hf['med']
        lf  = self._hf['label']

        W, H = self.width, self.height

        # ══════════════════════════════════════════════════════════
        # PRIORITY ALERT — full takeover
        # ══════════════════════════════════════════════════════════
        if state == 'PRIORITY_ALERT':
            ev = event or {}
            ac = ev.get('color', (255, 80, 60))
            # Dark background with subtle color tint
            bg_r = min(255, 10 + int(pulse * 12))
            bg_g = min(255, 8  + int(pulse * 6))
            bg_b = min(255, 8  + int(pulse * 4))
            self.screen.fill((bg_r, bg_g, bg_b))

            # Full-width color bar at top — pulsing thickness
            bar_h = int(6 + pulse2 * 6)
            pygame.draw.rect(self.screen, ac, (0, 0, W, bar_h))
            pygame.draw.rect(self.screen, ac, (0, H-bar_h, W, bar_h))

            # Vertical accent lines
            for vx in [0, W-4]:
                pygame.draw.rect(self.screen, ac, (vx, 0, 4, H))

            # Main alert text — centered, dominant
            tv = int(215 + pulse * 40)
            ms = huf.render(ev.get('priority', 'ALERT'), True, (tv, tv, tv))
            self.screen.blit(ms, (W//2 - ms.get_width()//2, H//2 - 130))

            # Location/sub label
            sub = ev.get('priority_sub', '')
            if sub:
                ac2 = (min(255,ac[0]+80), min(255,ac[1]+60), min(255,ac[2]+40))
                ss  = hf.render(sub, True, ac2)
                self.screen.blit(ss, (W//2 - ss.get_width()//2, H//2 + 10))

            # Thin separator
            sep_y = H//2 + 70
            pygame.draw.line(self.screen, (ac[0]//3, ac[1]//3, ac[2]//3), (W//4, sep_y), (3*W//4, sep_y), 1)

            # Buttons — clean, minimal
            btn_sel = data.get('btn_sel', 0)
            bw2, bh = 260, 62
            gap_b   = 60
            bx0     = W//2 - (bw2*2+gap_b)//2
            by      = H//2 + 92

            # Respond — filled, primary
            r_alpha = int(180 + pulse2 * 75) if btn_sel == 0 else 130
            r_bg    = (min(255,ac[0]//2+r_alpha//3), min(255,ac[1]//4), min(255,ac[2]//4))
            pygame.draw.rect(self.screen, r_bg, (bx0, by, bw2, bh), border_radius=8)
            if btn_sel == 0:
                pygame.draw.rect(self.screen, ac, (bx0-2, by-2, bw2+4, bh+4), width=2, border_radius=10)
            rs = bf.render('Respond', True, (255, 255, 255))
            self.screen.blit(rs, (bx0+bw2//2-rs.get_width()//2, by+bh//2-rs.get_height()//2))

            # Dismiss — outline only, secondary
            pygame.draw.rect(self.screen, (40, 38, 36), (bx0+bw2+gap_b, by, bw2, bh), border_radius=8)
            d_border = (120, 115, 110) if btn_sel == 1 else (55, 52, 50)
            pygame.draw.rect(self.screen, d_border, (bx0+bw2+gap_b-1, by-1, bw2+2, bh+2), width=1, border_radius=8)
            ds2 = bf.render('Dismiss', True, (150, 145, 140) if btn_sel == 1 else (90, 88, 86))
            self.screen.blit(ds2, (bx0+bw2+gap_b+bw2//2-ds2.get_width()//2, by+bh//2-ds2.get_height()//2))

            ht = hif.render('← →  Select   ENTER / R  Confirm   ESC  Dismiss', True, (70, 68, 66))
            self.screen.blit(ht, (W//2-ht.get_width()//2, H-36))
            return

        # ══════════════════════════════════════════════════════════
        # CIRCLEBEAM RESPONSE
        # ══════════════════════════════════════════════════════════
        if state == 'CIRCLEBEAM_RESPONSE':
            cb_elapsed = now - data.get('cb_start', now)
            connecting = cb_elapsed < 1.5
            ac4        = (60, 200, 130)
            self.screen.fill((4, 12, 8))

            # Top bar
            pygame.draw.rect(self.screen, ac4, (0, 0, W, 4))
            pygame.draw.rect(self.screen, ac4, (0, H-4, W, 4))

            # Expanding ripple from center — clean circles
            for ri in range(6):
                rr = int((cb_elapsed * 100 + ri * 90) % 460)
                ra = max(0, 55 - int(rr * 0.12))
                if ra > 0 and rr > 0:
                    rc = (ac4[0]//3+ra//3, ac4[1]//3+ra//2, ac4[2]//3+ra//3)
                    pygame.draw.circle(self.screen, rc, (W//2, H//2), rr, width=1)

            if connecting:
                dots = '.' * (int(cb_elapsed * 3) % 4)
                ms2  = hf.render(f'Connecting{dots}', True, (100, 180, 140))
                self.screen.blit(ms2, (W//2-ms2.get_width()//2, H//2-50))
                sub5 = sf.render('CircleBeam — Front Door', True, (50, 100, 70))
                self.screen.blit(sub5, (W//2-sub5.get_width()//2, H//2+20))
            else:
                # Connected state
                cv = int(180 + pulse * 75)
                cc = (min(255,ac4[0]//2+cv//3), min(255,ac4[1]//2+cv//2), min(255,ac4[2]//2+cv//3))
                ms3 = lf.render('CIRCLEBEAM', True, cc)
                self.screen.blit(ms3, (W//2-ms3.get_width()//2, H//2-110))
                ms4 = gif.render('Live Circle Active', True, (255, 255, 255))
                self.screen.blit(ms4, (W//2-ms4.get_width()//2, H//2-60))
                loc2 = hf.render('Front Door', True, ac4)
                self.screen.blit(loc2, (W//2-loc2.get_width()//2, H//2+50))
                # Pulsing dot indicator
                dr = int(10 + pulse * 7)
                pygame.draw.circle(self.screen, ac4, (W//2, H//2+128), dr)
                pygame.draw.circle(self.screen, (200,255,220), (W//2, H//2+128), dr, width=2)

            ht2 = hif.render('ESC  Dismiss', True, (30, 55, 40))
            self.screen.blit(ht2, (W//2-ht2.get_width()//2, H-36))
            if cb_elapsed > 8:
                data['home_state'] = 'IDLE'
                data['event']      = None
                data['_auto_fired']= False
            return

        # ══════════════════════════════════════════════════════════
        # MEDIUM ALERT
        # ══════════════════════════════════════════════════════════
        if state == 'MEDIUM_ALERT':
            ev  = event or {}
            ac  = ev.get('color', (60, 180, 120))
            # Dark background, keep rings off
            self.screen.fill((8, 12, 18))

            # Dim time — ghost
            ts2 = tf.render(now_dt.strftime('%I:%M'), True,
                            (30, 35, 50))
            self.screen.blit(ts2, (W//2-ts2.get_width()//2, 18))

            # Clean alert card — no clutter
            pw, ph  = 800, 196
            px2     = W//2 - pw//2
            py2     = H//2 - ph//2
            # Card background
            pygame.draw.rect(self.screen, (14, 18, 26), (px2, py2, pw, ph), border_radius=12)
            # Left accent bar — color of event
            bpv = int(3 + pulse * 3)
            pygame.draw.rect(self.screen, ac, (px2, py2, bpv, ph), border_radius=4)
            # Subtle border
            pygame.draw.rect(self.screen, (ac[0]//4, ac[1]//4, ac[2]//4),
                             (px2-1, py2-1, pw+2, ph+2), width=1, border_radius=12)

            # Pulsing corner dot
            dv = int(120 + pulse2 * 135)
            dc = (min(255,ac[0]//2+dv//2), min(255,ac[1]//2+dv//2), min(255,ac[2]//2+dv//2))
            pygame.draw.circle(self.screen, dc, (px2+pw-24, py2+24), int(6+pulse2*3))

            # Text
            ms5 = hf.render(ev.get('medium', 'Alert'), True, (240, 245, 255))
            self.screen.blit(ms5, (px2+bpv+24, py2+26))
            sub7 = ev.get('medium_sub', '')
            if sub7:
                ss5 = bf.render(sub7, True, (ac[0]//2+60, ac[1]//2+60, ac[2]//2+60))
                self.screen.blit(ss5, (px2+bpv+24, py2+104))

            ht3 = hif.render('ESC  Dismiss    ENTER  Expand', True, (45, 50, 65))
            self.screen.blit(ht3, (W//2-ht3.get_width()//2, H-36))
            return

        # ══════════════════════════════════════════════════════════
        # IDLE + PASSIVE — THE OEM MOMENT
        # ══════════════════════════════════════════════════════════

        # Background — very dark, near black, clean
        self.screen.fill((6, 8, 14))

        # Subtle center glow — 3 bands only (Pi 4 safe)
        for gy, gv in [(H//2-60, 6),(H//2, 9),(H//2+60, 6)]:
            pygame.draw.line(self.screen, (6+gv, 8+gv, 14+gv*2), (0, gy), (W, gy))

        # Single slow horizontal breath line
        breath_y = int(H * 0.58 + math.sin(now * 0.4) * 6)
        for bly in range(2):
            bla = 22 - bly * 8
            if bla > 0:
                pygame.draw.line(self.screen, (20, 35, 70), (0, breath_y+bly), (W, breath_y+bly))

        # ── TOP ZONE: Time ────────────────────────────────────────
        time_str = now_dt.strftime('%I:%M')
        ampm_str = now_dt.strftime('%p')
        date_str = now_dt.strftime('%A, %B %d')

        tv2 = int(190 + pulse3 * 25)
        tc2 = (tv2, tv2+10, min(255, tv2+30))
        ts3 = tf.render(time_str, True, tc2)
        ap3 = sf.render(ampm_str, True, (tv2//3, tv2//3, tv2//2))
        tx3 = W//2 - (ts3.get_width()+ap3.get_width()+10)//2
        self.screen.blit(ts3, (tx3, 22))
        self.screen.blit(ap3, (tx3+ts3.get_width()+8, 64))

        ds3 = sf.render(date_str, True, (55, 65, 90))
        self.screen.blit(ds3, (W//2-ds3.get_width()//2, 152))

        if hour < 12:   greeting = 'Good morning, Quamie.'
        elif hour < 17: greeting = 'Good afternoon, Quamie.'
        else:           greeting = 'Good evening, Quamie.'
        gv2 = int(100 + pulse3 * 20)
        gc3 = (gv2, gv2+10, min(255, gv2+40))
        gs3 = grf.render(greeting, True, gc3)
        self.screen.blit(gs3, (W//2-gs3.get_width()//2, 196))

        # ── MIDDLE ZONE: Status cards ─────────────────────────────
        if state == 'PASSIVE_ALERT' and event:
            # Passive banner — clean, minimal
            ac6   = event.get('color', (60, 180, 120))
            bar_y = 258
            bpv2  = int(2 + pulse * 2)
            # Thin left-accent card
            pygame.draw.rect(self.screen, (12,16,22), (W//2-400, bar_y, 800, 52), border_radius=8)
            pygame.draw.rect(self.screen, ac6, (W//2-400, bar_y, bpv2+1, 52), border_radius=4)
            # Pulsing dot
            dv4 = int(140 + pulse2 * 115)
            dc4 = (min(255,ac6[0]//2+dv4//3), min(255,ac6[1]//2+dv4//2), min(255,ac6[2]//2+dv4//3))
            pygame.draw.circle(self.screen, dc4, (W//2-370, bar_y+26), int(5+pulse2*3))
            ps4 = bf.render(event.get('passive','Event detected'), True, (210,220,240))
            self.screen.blit(ps4, (W//2-ps4.get_width()//2, bar_y+12))
        else:
            # Status row — 4 clean status cards side by side
            mode_status = {'home':'All Clear','away':'Monitoring','night':'Night Watch'}
            mode_color  = {'home':(50,180,90),'away':(200,140,50),'night':(70,100,180)}
            sc3  = mode_color.get(mode,(100,120,140))
            dv3  = int(100 + pulse * 120)
            dc3  = (min(255,sc3[0]//2+dv3//2), min(255,sc3[1]//2+dv3//2), min(255,sc3[2]//2+dv3//2))

            # Main status line with breathing dot
            sts  = bf.render(mode_status.get(mode,'Systems Normal'), True, sc3)
            dot_x3 = W//2-sts.get_width()//2-22
            pygame.draw.circle(self.screen, dc3, (dot_x3, 278), int(7+pulse*4))
            self.screen.blit(sts, (W//2-sts.get_width()//2, 265))

            # 4 status indicator tiles
            # ── Live simulated thermostat ──────────────────────
            import math as _math
            if '_thermo_base' not in data:
                data['_thermo_base'] = 71.0
                data['_thermo_dir']  = 0.003
            # Drift temp slowly ±2°F from base
            base  = data['_thermo_base']
            drift = _math.sin(now * 0.04) * 1.8
            # Mode affects target temp
            mode_offset = {'home': 0.0, 'away': 1.4, 'night': -1.2}
            temp_f = base + drift + mode_offset.get(mode, 0.0)
            temp_display = f'{temp_f:.1f}F'
            # Color shifts warm/cool
            if temp_f >= 74:
                thermo_color = (220, 120, 50)
            elif temp_f <= 69:
                thermo_color = (60, 140, 220)
            else:
                thermo_color = (60, 200, 140)

            # Ambient tile cycling — activity rotates every 6s
            cycle_t  = int(now / 6) % 4
            activity_log = [
                ('ENTRY',   True,  (50,200,100),  'Secured',     '2m ago'),
                ('GARAGE',  False, (180,140,50),  'Closed',      '14m ago'),
                ('BACKYARD',False, (50,130,210),  'Clear',       'No motion'),
                ('NETWORK', True,  (50,150,220),  'Online',      '100% uptime'),
            ]
            # Highlight rotating tile
            tiles_display = []
            for ti, (tn, ta, tc, ts2, ta2) in enumerate(activity_log):
                is_active_cycle = (ti == cycle_t)
                display_status  = ta2 if is_active_cycle else ts2
                pulse_override  = is_active_cycle
                tiles_display.append((tn, ta or pulse_override, tc, display_status))
            tiles_display.append(('TEMP', True, thermo_color, temp_display))
            tiles = tiles_display
            tile_w, tile_h = 130, 72
            gap_t          = 12
            total_tw       = len(tiles)*tile_w + (len(tiles)-1)*gap_t
            tile_x         = W//2 - total_tw//2
            tile_y         = 302

            for tname, tactive, tcolor, tstatus in tiles:
                # Tile background
                pygame.draw.rect(self.screen, (10, 13, 20),
                                 (tile_x, tile_y, tile_w, tile_h), border_radius=8)
                # Active tile: colored top border
                if tactive:
                    tv3 = int(80 + pulse2 * 60)
                    tc3 = (min(255,tcolor[0]//2+tv3//2),
                           min(255,tcolor[1]//2+tv3//2),
                           min(255,tcolor[2]//2+tv3//2))
                    pygame.draw.rect(self.screen, tc3, (tile_x, tile_y, tile_w, 3), border_radius=2)
                else:
                    pygame.draw.rect(self.screen, (25,28,36),
                                     (tile_x, tile_y, tile_w, 3), border_radius=2)

                # Tile label
                tl = lf.render(tname, True, (50,55,70) if not tactive else (80,90,110))
                self.screen.blit(tl, (tile_x+12, tile_y+10))

                # Status value
                sv_col = (min(255,tcolor[0]+40), min(255,tcolor[1]+40), min(255,tcolor[2]+40)) if tactive else (45,50,60)
                sl = smf.render(tstatus, True, sv_col)
                self.screen.blit(sl, (tile_x+12, tile_y+38))

                # Active indicator dot
                if tactive:
                    da = int(160 + pulse * 95)
                    pygame.draw.circle(self.screen,
                                       (min(255,tcolor[0]//2+da//2), min(255,tcolor[1]//2+da//2), min(255,tcolor[2]//2+da//2)),
                                       (tile_x+tile_w-16, tile_y+16), int(4+pulse*2))

                tile_x += tile_w + gap_t

        # ── BOTTOM ZONE: System info ───────────────────────────────
        # CircleBeam status — single clean line
        pres    = getattr(self, 'presence', None)
        cb_c2   = (50,170,100) if pres else (40,52,48)
        cb_dot  = int(100+pulse*120) if pres else 40
        cb_dc   = (0, min(255,cb_dot), 0) if pres else (40,48,44)
        cb_txt2 = 'CircleBeam  Connected' if pres else 'CircleBeam  Standby'
        cbs2    = smf.render(cb_txt2, True, cb_c2)
        pygame.draw.circle(self.screen, cb_dc,
                           (W//2-cbs2.get_width()//2-16, 394), int(5+pulse*3) if pres else 4)
        self.screen.blit(cbs2, (W//2-cbs2.get_width()//2, 386))

        # Mode indicator — minimal pill
        mc_map2 = {'home':(40,130,65),'away':(150,85,25),'night':(45,65,135)}
        mc2     = mc_map2.get(mode,(60,65,75))
        badge2  = lf.render(mode.upper(), True, mc2)
        bw6     = badge2.get_width()+20
        bx5     = W//2 - bw6//2
        pygame.draw.rect(self.screen, (mc2[0]//4,mc2[1]//4,mc2[2]//4), (bx5,416,bw6,28), border_radius=6)
        pygame.draw.rect(self.screen, (mc2[0]//2,mc2[1]//2,mc2[2]//2), (bx5-1,415,bw6+2,30), width=1, border_radius=6)
        self.screen.blit(badge2, (W//2-badge2.get_width()//2, 420))

        # Simulate strip — very subtle, not prominent
        sim_items2 = [('1','Garage',(140,120,40)),('2','Motion',(40,110,170)),
                      ('3','Front Door',(160,70,30)),('4','Leak',(30,130,160))]
        sx2 = W//2 - 340
        sy2 = 460
        sim_lbl2 = lf.render('SIMULATE  ', True, (30,35,50))
        self.screen.blit(sim_lbl2, (sx2, sy2))
        sx2 += sim_lbl2.get_width()
        for kl2,nm2,dc4 in sim_items2:
            fc2 = (dc4[0]//3+25, dc4[1]//3+25, dc4[2]//3+25)
            ks3 = lf.render(f'[{kl2}] {nm2}', True, fc2)
            self.screen.blit(ks3, (sx2, sy2))
            sx2 += ks3.get_width()+22

        ht5 = hif.render('H / A / N   Mode      ESC   Back', True, (24, 28, 44))
        self.screen.blit(ht5, (W//2-ht5.get_width()//2, H-34))

        # CircleBeam live session banner — drawn last so nothing overwrites it
        if getattr(self, 'circlebeam_active', False) and getattr(self, 'circlebeam_target', None):
            import math as _hcm, time as _hct
            _hp = (_hcm.sin(_hct.time() * 1.2) + 1) / 2
            _bsurf = pygame.Surface((W - 60, 54), pygame.SRCALPHA)
            _bsurf.fill((10, 48, 28, int(200 + _hp * 40)))
            self.screen.blit(_bsurf, (30, 10))
            pygame.draw.rect(self.screen, (50, int(185+_hp*55), 90),
                             pygame.Rect(30, 10, W - 60, 54), 2, border_radius=8)
            _bts = get_font(34, bold=True).render(
                f'● Live Circle Active — {self.circlebeam_target}',
                True, (80, int(205+_hp*50), 125))
            self.screen.blit(_bts, (W//2 - _bts.get_width()//2, 20))


    def handle_home_realm_input(self, key):
        """Delegated — actual input handled by _home_poll_keys each frame"""
        pass


    def render_health_wellness(self):
        """Health & Wellness realm"""
        hw = self.realm_data['health_wellness']
        module = hw.get('module')
        import time as _ta, math
        if hw.get('last_input_time', 0) == 0:
            hw['last_input_time'] = _ta.time()
        idle = _ta.time() - hw['last_input_time']
        if idle > 90:
            if not hw.get('ambient_mode'):
                hw['ambient_mode'] = True
                hw['ambient_start'] = _ta.time()
            self._hw_ambient()
            return
        else:
            hw['ambient_mode'] = False
        if module == 'checkin': self._hw_checkin(); return
        elif module == 'mood': self._hw_mood(); return
        elif module == 'breathing': self._hw_breathing(); return
        elif module == 'routines': self._hw_routines(); return
        elif module == 'activity': self._hw_activity(); return
        elif module == 'insights': self._hw_insights(); return
        self.screen.fill((10,16,22))
        title_font = get_font(68, bold=True)
        title = title_font.render("HEALTH & WELLNESS", True, (100,210,160))
        self.screen.blit(title, (self.width//2-title.get_width()//2, 28))
        sub_font = get_font(38)
        sub = sub_font.render("Stay Balanced. Stay Aware.", True, (140,175,160))
        self.screen.blit(sub, (self.width//2-sub.get_width()//2, 108))
        tiles = [
            {'id':'checkin',   'emoji':'🌿', 'name':'Daily Check-In',    'desc':'How are you today?'},
            {'id':'mood',      'emoji':'💭', 'name':'Mood & Energy',     'desc':'Your current state'},
            {'id':'breathing', 'emoji':'🌬', 'name':'Breathing',         'desc':'Calm and focus'},
            {'id':'routines',  'emoji':'🔔', 'name':'Routine Reminders', 'desc':'Daily habits'},
            {'id':'activity',  'emoji':'🚶', 'name':'Activity',          'desc':'Movement prompts'},
            {'id':'insights',  'emoji':'💡', 'name':'Wellness Insights', 'desc':'Your daily summary'},
        ]
        cols, cw, ch, gap = 3, 340, 178, 22
        grid_w = cols*cw+(cols-1)*gap
        sx = (self.width-grid_w)//2
        sy = 158
        selected = hw.get('selected', 0)
        for i, tile in enumerate(tiles):
            row, col = i//cols, i%cols
            x = sx+col*(cw+gap); y = sy+row*(ch+gap)
            is_sel = i==selected
            bg = (20,42,36) if is_sel else (14,26,22)
            bc = (100,210,160) if is_sel else (40,75,62)
            rect = pygame.Rect(x,y,cw,ch)
            pygame.draw.rect(self.screen, bg, rect, border_radius=14)
            pygame.draw.rect(self.screen, bc, rect, 3 if is_sel else 1, border_radius=14)
            ef = load_emoji_font(48)
            em = ef.render(tile['emoji'], True, (255,255,255))
            self.screen.blit(em, (x+cw//2-em.get_width()//2, y+14))
            nf = get_font(38, bold=True)
            nc = (140,230,190) if is_sel else (180,210,195)
            nm = nf.render(tile['name'], True, nc)
            self.screen.blit(nm, (x+cw//2-nm.get_width()//2, y+76))
            df = get_font(28)
            dm = df.render(tile['desc'], True, (90,130,115))
            self.screen.blit(dm, (x+cw//2-dm.get_width()//2, y+120))
        hf = get_font(28)
        hint = hf.render("Arrow keys Navigate  |  ENTER Open  |  ESC Back", True, (60,90,78))
        self.screen.blit(hint, (self.width//2-hint.get_width()//2, self.height-48))

    def _hw_ambient(self):
        import time as _ta, math
        hw = self.realm_data['health_wellness']
        t = _ta.time()
        pulse = 0.7+0.3*math.sin(t*0.6)
        self.screen.fill((8,12,18))
        cx, cy = self.width//2, self.height//2-40
        phase = (math.sin(t*0.4)+1)/2
        r = int(60+phase*80)
        surf = pygame.Surface((400,400), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80,180,130,int(40+phase*60)), (200,200), r)
        self.screen.blit(surf, (cx-200,cy-200))
        pygame.draw.circle(self.screen, (60,150,110), (cx,cy), r, 2)
        msg = "Breathe in..." if phase > 0.5 else "Breathe out..."
        mf = get_font(52, bold=True)
        mm = mf.render(msg, True, (int(100*pulse),int(200*pulse),int(150*pulse)))
        self.screen.blit(mm, (self.width//2-mm.get_width()//2, cy+110))
        hf = get_font(28)
        hm = hf.render("Press any key to interact", True, (40,62,52))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, self.height-32))

    def _hw_checkin(self):
        hw = self.realm_data['health_wellness']
        step = hw.get('checkin_step', 0)
        answers = hw.get('checkin_answers', [])
        self.screen.fill((10,16,22))
        hf = get_font(52, bold=True)
        hm = hf.render("DAILY CHECK-IN", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 28))
        questions = [
            ('How are you feeling today?', ['Great','Good','Okay','Tired','Not well']),
            ('Energy level?', ['High','Good','Moderate','Low','Very low']),
            ('Stress level?', ['None','Mild','Moderate','High','Very high']),
        ]
        if step >= len(questions):
            self.screen.fill((10,16,22))
            tf = get_font(56, bold=True)
            tm = tf.render("Check-In Complete!", True, (100,210,160))
            self.screen.blit(tm, (self.width//2-tm.get_width()//2, 140))
            labels = ['Feeling','Energy','Stress']
            for i,(label,ans_idx) in enumerate(zip(labels,answers)):
                ans = questions[i][1][ans_idx]
                lf = get_font(44)
                lm = lf.render(f"{label}: {ans}", True, (160,210,190))
                self.screen.blit(lm, (self.width//2-lm.get_width()//2, 240+i*60))
            feeling = answers[0] if answers else 2
            energy = answers[1] if len(answers)>1 else 2
            if feeling<=1 and energy<=1: insight="You're doing great today! Keep it up."
            elif feeling>=3 or energy>=3: insight="Take it easy today. Rest and hydrate."
            else: insight="Good day ahead. Stay balanced."
            inf = get_font(38)
            im = inf.render(insight, True, (120,190,155))
            self.screen.blit(im, (self.width//2-im.get_width()//2, 440))
            ff = get_font(30)
            fm = ff.render("B Back to Wellness", True, (60,90,78))
            self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))
            return
        q, opts = questions[step]
        qf = get_font(46, bold=True)
        qm = qf.render(q, True, (200,230,215))
        self.screen.blit(qm, (self.width//2-qm.get_width()//2, 110))
        sel = hw.get('checkin_sel', 0)
        ow, oh = 200, 72
        total_w = len(opts)*(ow+16)-16
        ox_start = (self.width-total_w)//2
        for i,opt in enumerate(opts):
            ox = ox_start+i*(ow+16); oy = 210
            is_sel = i==sel
            bg = (20,55,42) if is_sel else (14,28,22)
            bc = (100,210,160) if is_sel else (40,80,65)
            orect = pygame.Rect(ox,oy,ow,oh)
            pygame.draw.rect(self.screen, bg, orect, border_radius=12)
            pygame.draw.rect(self.screen, bc, orect, 3 if is_sel else 2, border_radius=12)
            of = pygame.font.SysFont(None, 36, bold=is_sel)
            oc = (140,230,190) if is_sel else (120,165,148)
            om = of.render(opt, True, oc)
            self.screen.blit(om, (ox+ow//2-om.get_width()//2, oy+oh//2-om.get_height()//2))
        pf = get_font(32)
        pm = pf.render(f"Question {step+1} of {len(questions)}", True, (80,120,105))
        self.screen.blit(pm, (self.width//2-pm.get_width()//2, 320))
        ff = get_font(30)
        fm = ff.render("LEFT/RIGHT Select  |  ENTER Confirm  |  B Back", True, (60,90,78))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _hw_mood(self):
        hw = self.realm_data['health_wellness']
        answers = hw.get('checkin_answers', [2,2,2])
        self.screen.fill((10,16,22))
        hf = get_font(52, bold=True)
        hm = hf.render("MOOD & ENERGY", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 28))
        metrics = [
            ('Feeling', answers[0] if answers else 2, ['Great','Good','Okay','Tired','Low'], (100,210,160)),
            ('Energy',  answers[1] if len(answers)>1 else 2, ['High','Good','Moderate','Low','Very Low'], (100,180,255)),
            ('Stress',  answers[2] if len(answers)>2 else 2, ['None','Mild','Moderate','High','Very High'], (255,180,80)),
        ]
        for i,(label,val,levels,color) in enumerate(metrics):
            y = 140+i*150
            lf = get_font(42, bold=True)
            lm = lf.render(label, True, color)
            self.screen.blit(lm, (160,y))
            bar_x,bar_y = 320,y+8
            bar_w,bar_h = 600,36
            pygame.draw.rect(self.screen, (20,35,28), pygame.Rect(bar_x,bar_y,bar_w,bar_h), border_radius=10)
            fill = bar_w-int((val/4)*bar_w) if label!='Stress' else int((val/4)*bar_w)
            pygame.draw.rect(self.screen, color, pygame.Rect(bar_x,bar_y,fill,bar_h), border_radius=10)
            vf = get_font(36)
            vm = vf.render(levels[val], True, (160,200,180))
            self.screen.blit(vm, (bar_x+bar_w+20,y+5))
        tips = ["You seem well today. Keep up the good habits.","Moderate day - stay hydrated.","Consider a short walk or breathing exercise.","Rest and recovery recommended today."]
        avg = sum(answers[:3])//3 if answers else 2
        tf = get_font(36)
        tm = tf.render(tips[min(avg,len(tips)-1)], True, (100,160,138))
        self.screen.blit(tm, (self.width//2-tm.get_width()//2, 610))
        ff = get_font(30)
        fm = ff.render("Complete Daily Check-In for accurate data  |  B Back", True, (60,90,78))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _hw_breathing(self):
        import time as _ta, math
        hw = self.realm_data['health_wellness']
        running = hw.get('breath_running', False)
        self.screen.fill((8,12,20))
        hf = get_font(52, bold=True)
        hm = hf.render("BREATHING", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 22))
        if not running:
            sf = get_font(42)
            sm = sf.render("Press S to begin guided breathing", True, (120,175,155))
            self.screen.blit(sm, (self.width//2-sm.get_width()//2, 120))
            cx, cy = self.width//2, self.height//2
            pygame.draw.circle(self.screen, (20,50,40), (cx,cy), 140)
            pygame.draw.circle(self.screen, (60,150,110), (cx,cy), 140, 3)
            bf = get_font(52, bold=True)
            bm = bf.render("Breathe", True, (100,210,160))
            self.screen.blit(bm, (cx-bm.get_width()//2, cy-bm.get_height()//2))
        else:
            t = _ta.time()-hw.get('breath_start',_ta.time())
            cycle = 12.0
            phase_t = t%cycle
            if phase_t<4: phase="Breathe In"; r=int(80+phase_t/4*100); color=(80,200,150)
            elif phase_t<8: phase="Hold"; r=180; color=(100,180,220)
            else: phase="Breathe Out"; r=int(180-(phase_t-8)/4*100); color=(80,160,200)
            cx, cy = self.width//2, self.height//2+20
            surf = pygame.Surface((500,500), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color,40), (250,250), r+30)
            self.screen.blit(surf, (cx-250,cy-250))
            pygame.draw.circle(self.screen, color, (cx,cy), r)
            pygame.draw.circle(self.screen, (200,240,220), (cx,cy), r, 3)
            pf = get_font(72, bold=True)
            pm = pf.render(phase, True, (220,245,232))
            self.screen.blit(pm, (cx-pm.get_width()//2, cy-pm.get_height()//2))
            cycles = int(t/cycle)
            cf = get_font(34)
            cm = cf.render(f"Cycle {cycles+1}", True, (80,130,110))
            self.screen.blit(cm, (self.width//2-cm.get_width()//2, 110))
        ff = get_font(30)
        fm = ff.render("S Start/Stop  |  B Back", True, (50,80,65))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _hw_routines(self):
        hw = self.realm_data['health_wellness']
        self.screen.fill((10,16,22))
        hf = get_font(52, bold=True)
        hm = hf.render("ROUTINE REMINDERS", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 28))
        routines = [
            ('💧','Drink Water','Stay hydrated - 8 glasses a day'),
            ('💊','Medication','Take your scheduled medication'),
            ('🧘','Stretch','5-minute stretch recommended'),
            ('🪑','Check Posture','Sit up straight, relax shoulders'),
            ('🌙','Wind Down','Limit screens 1hr before bed'),
            ('🍎','Healthy Snack','Choose fruit or nuts over sugar'),
        ]
        completed = hw.get('routines_done', set())
        selected = hw.get('routine_sel', 0)
        rw, rh = 900, 68
        rx = (self.width-rw)//2
        for i,(emoji,name,desc) in enumerate(routines):
            ry = 110+i*82
            done = i in completed
            is_sel = i==selected
            bg = (14,35,26) if is_sel else (10,22,18)
            bc = (100,210,160) if is_sel else (30,62,50)
            pygame.draw.rect(self.screen, bg, pygame.Rect(rx,ry,rw,rh), border_radius=12)
            pygame.draw.rect(self.screen, bc, pygame.Rect(rx,ry,rw,rh), 2, border_radius=12)
            ef = load_emoji_font(36)
            em = ef.render(emoji, True, (255,255,255))
            self.screen.blit(em, (rx+18,ry+rh//2-em.get_height()//2))
            nf = get_font(36, bold=True)
            nm = nf.render(name, True, (140,230,190) if is_sel else (160,200,180))
            self.screen.blit(nm, (rx+70,ry+10))
            df = get_font(28)
            dm = df.render(desc, True, (80,120,105))
            self.screen.blit(dm, (rx+70,ry+38))
            if done:
                cf = get_font(36, bold=True)
                cm = cf.render("Done!", True, (80,200,130))
                self.screen.blit(cm, (rx+rw-80,ry+rh//2-cm.get_height()//2))
        ff = get_font(30)
        fm = ff.render("UP/DOWN Navigate  |  SPACE Complete  |  B Back", True, (60,90,78))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _hw_activity(self):
        hw = self.realm_data['health_wellness']
        self.screen.fill((10,16,22))
        hf = get_font(52, bold=True)
        hm = hf.render("ACTIVITY & MOVEMENT", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 28))
        prompts = [
            ('🚶','Take a short walk','5 minutes outside does wonders'),
            ('🤸','Quick stretch','Reach up, touch toes, roll your neck'),
            ('💪','10 pushups','Build strength - you can do it!'),
            ('🧘','Standing stretch','Arms overhead, hold 10 seconds'),
            ('🏃','March in place','2 minutes gets the blood moving'),
            ('🌿','Step outside','Fresh air and natural light boost mood'),
        ]
        sel = hw.get('activity_sel', 0)
        acknowledged = hw.get('activity_done', set())
        for i,(emoji,title,desc) in enumerate(prompts):
            y = 110+i*82
            done = i in acknowledged
            is_sel = i==sel
            pw, ph = 900, 68
            px = (self.width-pw)//2
            bg = (14,35,26) if is_sel else (10,22,18)
            bc = (100,210,160) if is_sel else (30,62,50)
            pygame.draw.rect(self.screen, bg, pygame.Rect(px,y,pw,ph), border_radius=12)
            pygame.draw.rect(self.screen, bc, pygame.Rect(px,y,pw,ph), 2, border_radius=12)
            ef = load_emoji_font(36)
            em = ef.render(emoji, True, (255,255,255))
            self.screen.blit(em, (px+18,y+ph//2-em.get_height()//2))
            nf = get_font(36, bold=True)
            nm = nf.render(title, True, (140,230,190) if is_sel else (160,200,180))
            self.screen.blit(nm, (px+70,y+8))
            df = get_font(28)
            dm = df.render(desc, True, (80,120,105))
            self.screen.blit(dm, (px+70,y+38))
            if done:
                cf = get_font(34, bold=True)
                cm = cf.render("Done!", True, (80,200,130))
                self.screen.blit(cm, (px+pw-80,y+ph//2-cm.get_height()//2))
        ff = get_font(30)
        fm = ff.render("UP/DOWN Navigate  |  SPACE Acknowledge  |  B Back", True, (60,90,78))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _hw_insights(self):
        hw = self.realm_data['health_wellness']
        self.screen.fill((10,16,22))
        hf = get_font(52, bold=True)
        hm = hf.render("WELLNESS INSIGHTS", True, (100,210,160))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 28))
        answers = hw.get('checkin_answers', [])
        routines_done = len(hw.get('routines_done', set()))
        activity_done = len(hw.get('activity_done', set()))
        insights = []
        if not answers:
            insights.append(('💭','No check-in data yet','Complete Daily Check-In for personalized insights'))
        else:
            feeling = answers[0] if answers else 2
            energy = answers[1] if len(answers)>1 else 2
            stress = answers[2] if len(answers)>2 else 2
            if feeling<=1: insights.append(('😊',"You're feeling great today!",'Keep up whatever you are doing'))
            elif feeling>=3: insights.append(('🌿','Take it easy today','Rest and gentle movement recommended'))
            else: insights.append(('👍','Decent day ahead','Stay consistent with your habits'))
            if energy<=1: insights.append(('⚡','Energy is high','Great time for activity or focus work'))
            elif energy>=3: insights.append(('💧','Low energy detected','Hydrate and consider a short rest'))
            if stress>=3: insights.append(('🧘','Stress is elevated','Try the Breathing module for calm'))
            else: insights.append(('✅','Stress is manageable','You are handling things well'))
        if routines_done>0: insights.append(('🔔',f'{routines_done} routines completed','Great habit building today'))
        if activity_done>0: insights.append(('🏃',f'{activity_done} activities done','You are staying active - excellent!'))
        for i,(emoji,title,desc) in enumerate(insights[:5]):
            y = 110+i*96
            iw, ih = 900, 74
            ix = (self.width-iw)//2
            pygame.draw.rect(self.screen, (12,24,20), pygame.Rect(ix,y,iw,ih), border_radius=12)
            pygame.draw.rect(self.screen, (35,75,60), pygame.Rect(ix,y,iw,ih), 1, border_radius=12)
            ef = load_emoji_font(40)
            em = ef.render(emoji, True, (255,255,255))
            self.screen.blit(em, (ix+18,y+ih//2-em.get_height()//2))
            nf = get_font(38, bold=True)
            nm = nf.render(title, True, (140,220,185))
            self.screen.blit(nm, (ix+72,y+8))
            df = get_font(28)
            dm = df.render(desc, True, (80,120,105))
            self.screen.blit(dm, (ix+72,y+44))
        ff = get_font(30)
        fm = ff.render("B  Back to Wellness", True, (60,90,78))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def handle_health_wellness_input(self, key):
        import time as _t
        hw = self.realm_data['health_wellness']
        hw['last_input_time'] = _t.time()
        if hw.get('ambient_mode'):
            hw['ambient_mode'] = False
            return
        module = hw.get('module')
        if module is None:
            sel = hw.get('selected', 0)
            if key == pygame.K_LEFT: hw['selected'] = max(0, sel-1)
            elif key == pygame.K_RIGHT: hw['selected'] = min(5, sel+1)
            elif key == pygame.K_UP: hw['selected'] = max(0, sel-3)
            elif key == pygame.K_DOWN: hw['selected'] = min(5, sel+3)
            elif key == pygame.K_RETURN:
                mods = ['checkin','mood','breathing','routines','activity','insights']
                hw['module'] = mods[hw.get('selected',0)]
                m = hw['module']
                if m=='checkin': hw['checkin_step']=0; hw['checkin_sel']=0; hw['checkin_answers']=[]
                elif m=='breathing': hw['breath_running']=False
                elif m=='routines': hw['routine_sel']=0; hw.setdefault('routines_done',set())
                elif m=='activity': hw['activity_sel']=0; hw.setdefault('activity_done',set())
            elif key == pygame.K_ESCAPE: self.go_back()
            return
        if module=='checkin':
            questions=[('',5),('',5),('',5)]
            step=hw.get('checkin_step',0); sel=hw.get('checkin_sel',0)
            if step<len(questions):
                if key==pygame.K_LEFT: hw['checkin_sel']=max(0,sel-1)
                elif key==pygame.K_RIGHT: hw['checkin_sel']=min(4,sel+1)
                elif key==pygame.K_RETURN:
                    hw.setdefault('checkin_answers',[]).append(sel)
                    hw['checkin_step']=step+1; hw['checkin_sel']=0
                    if self.presence and step==2:
                        self.presence.broadcast({'type':'WELLNESS_RESPONSE','from':'Daughter','data':hw['checkin_answers']})
            if key in (pygame.K_b,pygame.K_ESCAPE): hw['module']=None
        elif module=='breathing':
            import time as _tb
            if key==pygame.K_s:
                if hw.get('breath_running'): hw['breath_running']=False
                else: hw['breath_running']=True; hw['breath_start']=_tb.time()
            elif key in (pygame.K_b,pygame.K_ESCAPE): hw['breath_running']=False; hw['module']=None
        elif module=='routines':
            sel=hw.get('routine_sel',0)
            if key==pygame.K_UP: hw['routine_sel']=max(0,sel-1)
            elif key==pygame.K_DOWN: hw['routine_sel']=min(5,sel+1)
            elif key==pygame.K_SPACE: hw.setdefault('routines_done',set()).add(sel)
            elif key in (pygame.K_b,pygame.K_ESCAPE): hw['module']=None
        elif module=='activity':
            sel=hw.get('activity_sel',0)
            if key==pygame.K_UP: hw['activity_sel']=max(0,sel-1)
            elif key==pygame.K_DOWN: hw['activity_sel']=min(5,sel+1)
            elif key==pygame.K_SPACE: hw.setdefault('activity_done',set()).add(sel)
            elif key in (pygame.K_b,pygame.K_ESCAPE): hw['module']=None
        elif module in ('mood','insights'):
            if key in (pygame.K_b,pygame.K_ESCAPE): hw['module']=None


    def render_education(self):
        """Education realm - 6 projection-optimized learning modules"""
        ed = self.realm_data['education']
        module = ed['module']
        # Ambient sleep mode - triggers after 60s of no input
        import time as _ta
        if ed['last_input_time'] == 0:
            ed['last_input_time'] = _ta.time()
        idle = _ta.time() - ed['last_input_time']
        if idle > 60 and not ed.get('live_question_active'):
            if not ed['ambient_mode']:
                ed['ambient_mode'] = True
                ed['ambient_start'] = _ta.time()
            self._edu_ambient()
            return
        else:
            ed['ambient_mode'] = False

        if ed.get('live_question_active'):
            self._render_live_question()
            return
        if module == 'flashcards':
            self._edu_flashcards(); return
        elif module == 'math':
            self._edu_math(); return
        elif module == 'vocab':
            self._edu_vocab(); return
        elif module == 'timer':
            self._edu_timer(); return
        elif module == 'quiz':
            self._edu_quiz(); return
        elif module == 'daily':
            self._edu_daily(); return

        self.screen.fill(BG_COLOR)
        title_font = get_font(72, bold=True)
        title = title_font.render("EDUCATION", True, (255, 180, 50))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 30))
        sub_font = get_font(42)
        sub = sub_font.render("Learn Anywhere", True, (180, 200, 220))
        self.screen.blit(sub, (self.width//2 - sub.get_width()//2, 115))

        tiles = [
            {'id': 'flashcards', 'emoji': '🃏', 'name': 'Flashcards',    'desc': 'Terms & concepts'},
            {'id': 'math',       'emoji': '🔢', 'name': 'Math Practice', 'desc': 'Problems & answers'},
            {'id': 'vocab',      'emoji': '📖', 'name': 'Vocabulary',    'desc': 'Words & definitions'},
            {'id': 'timer',      'emoji': '⏱', 'name': 'Study Timer',   'desc': 'Focus sessions'},
            {'id': 'quiz',       'emoji': '❓', 'name': 'Quiz Mode',     'desc': 'Test your knowledge'},
            {'id': 'daily',      'emoji': '📅', 'name': 'Daily Lesson',  'desc': "Today's focus"},
        ]
        cols, cw, ch, gap = 3, 340, 185, 22
        grid_w = cols * cw + (cols-1) * gap
        sx = (self.width - grid_w) // 2
        sy = 165
        selected = ed['selected']
        for i, tile in enumerate(tiles):
            row, col = i // cols, i % cols
            x = sx + col * (cw + gap)
            y = sy + row * (ch + gap)
            is_sel = i == selected
            bg = (35, 50, 75) if is_sel else (25, 32, 48)
            bc = (255, 180, 50) if is_sel else (60, 80, 110)
            rect = pygame.Rect(x, y, cw, ch)
            pygame.draw.rect(self.screen, bg, rect, border_radius=14)
            pygame.draw.rect(self.screen, bc, rect, 3 if is_sel else 1, border_radius=14)
            ef = load_emoji_font(52)
            em = ef.render(tile['emoji'], True, (255,255,255))
            self.screen.blit(em, (x + cw//2 - em.get_width()//2, y + 18))
            nf = get_font(40, bold=True)
            nc = (255, 220, 100) if is_sel else (220, 230, 245)
            nm = nf.render(tile['name'], True, nc)
            self.screen.blit(nm, (x + cw//2 - nm.get_width()//2, y + 88))
            df = get_font(28)
            dm = df.render(tile['desc'], True, (140, 155, 175))
            self.screen.blit(dm, (x + cw//2 - dm.get_width()//2, y + 130))

        if ed['preview_open']:
            self._edu_preview(tiles[selected])

        hf = get_font(28)
        hint = hf.render("Arrow keys Navigate  |  ENTER Open  |  P Preview  |  ESC Back", True, (100, 115, 135))
        self.screen.blit(hint, (self.width//2 - hint.get_width()//2, self.height - 52))

    def _edu_preview(self, tile):
        pw, ph = 480, 320
        px = self.width//2 - pw//2
        py = self.height//2 - ph//2
        # Dark background instead of SRCALPHA overlay (Pi 4 safe)
        self.screen.fill((8, 10, 18))
        rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, (28, 38, 58), rect, border_radius=18)
        pygame.draw.rect(self.screen, (255, 180, 50), rect, 3, border_radius=18)
        ef = load_emoji_font(56)
        em = ef.render(tile['emoji'], True, (255,255,255))
        self.screen.blit(em, (px + pw//2 - em.get_width()//2, py + 16))
        tf = get_font(48, bold=True)
        tm = tf.render(tile['name'], True, (255, 220, 100))
        self.screen.blit(tm, (px + pw//2 - tm.get_width()//2, py + 90))
        previews = {
            'flashcards': ['10 built-in study cards', 'SPACE to reveal answer', 'N to advance'],
            'math':       ['10 5th-grade problems', 'A/B/C to answer', 'Score tracking'],
            'vocab':      ['10 vocabulary words', 'SPACE to reveal definition', 'N to advance'],
            'timer':      ['Focus / Break / Review modes', 'S to start or pause', 'Large wall display'],
            'quiz':       ['5 demo questions', 'A/B/C/D to answer', 'Instant feedback'],
            'daily':      ["Today's recommended focus", 'Auto-selected by day', 'Projected on wall'],
        }
        lf = get_font(32)
        for i, line in enumerate(previews.get(tile['id'], [])):
            lm = lf.render("• " + line, True, (200, 210, 230))
            self.screen.blit(lm, (px + 36, py + 150 + i * 42))
        cf = get_font(28)
        cm = cf.render("ENTER to open  |  P to close", True, (110, 125, 148))
        self.screen.blit(cm, (px + pw//2 - cm.get_width()//2, py + ph - 32))

    def _edu_flashcards(self):
        cards = [
            ('What is photosynthesis?', 'Plants converting sunlight into food using CO2 and water'),
            ('Define: Democracy', 'A system of government where citizens vote for representatives'),
            ('What is the water cycle?', 'Evaporation to Condensation to Precipitation to Collection'),
            ('Who was Abraham Lincoln?', '16th US President who ended slavery during the Civil War'),
            ('What is an ecosystem?', 'A community of living things interacting with their environment'),
            ('Define: Fraction', 'A number representing part of a whole, written as a/b'),
            ('What is gravity?', 'The force that pulls objects toward each other'),
            ('What is a metaphor?', 'A direct comparison between two unlike things without like/as'),
            ('Define: Migration', 'The seasonal movement of animals from one region to another'),
            ('What is the Constitution?', 'The supreme law of the United States, written in 1787'),
        ]
        ed = self.realm_data['education']
        idx = ed['flashcard_index'] % len(cards)
        revealed = ed['flashcard_revealed']
        card = cards[idx]
        self.screen.fill((12, 18, 30))
        hf = get_font(48, bold=True)
        self.screen.blit(hf.render("FLASHCARDS", True, (255,180,50)), (self.width//2 - hf.size("FLASHCARDS")[0]//2, 25))
        pf = get_font(36)
        pm = pf.render(f"Card {idx+1} of {len(cards)}", True, (140,160,185))
        self.screen.blit(pm, (self.width//2 - pm.get_width()//2, 85))
        cw, ch = 1000, 360
        cx = (self.width - cw) // 2
        cy = 130
        pygame.draw.rect(self.screen, (22,32,52), pygame.Rect(cx,cy,cw,ch), border_radius=20)
        pygame.draw.rect(self.screen, (255,180,50), pygame.Rect(cx,cy,cw,ch), 3, border_radius=20)
        qf = get_font(52, bold=True)
        words = card[0].split()
        lines, line = [], []
        for w in words:
            test = ' '.join(line + [w])
            if qf.size(test)[0] > cw-80: lines.append(' '.join(line)); line=[w]
            else: line.append(w)
        if line: lines.append(' '.join(line))
        for i, ln in enumerate(lines):
            lm = qf.render(ln, True, (255,255,255))
            self.screen.blit(lm, (cx+cw//2-lm.get_width()//2, cy+28+i*58))
        if revealed:
            pygame.draw.line(self.screen, (60,80,110), (cx+40,cy+165), (cx+cw-40,cy+165), 2)
            af = get_font(38)
            awords = card[1].split()
            alines, aline = [], []
            for w in awords:
                test = ' '.join(aline + [w])
                if af.size(test)[0] > cw-80: alines.append(' '.join(aline)); aline=[w]
                else: aline.append(w)
            if aline: alines.append(' '.join(aline))
            for i, ln in enumerate(alines):
                lm = af.render(ln, True, (100,220,160))
                self.screen.blit(lm, (cx+cw//2-lm.get_width()//2, cy+182+i*46))
        else:
            hint = get_font(38)
            hm = hint.render("Press SPACE to reveal answer", True, (100,120,150))
            self.screen.blit(hm, (cx+cw//2-hm.get_width()//2, cy+185))
        ff = get_font(30)
        fm = ff.render("SPACE Reveal  |  N Next card  |  B Back", True, (90,105,125))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _edu_math(self):
        problems = [
            {'q':'What is 12 x 13?','a':'144','b':'156','c':'169','correct':'b'},
            {'q':'What is 25% of 200?','a':'25','b':'50','c':'75','correct':'b'},
            {'q':'What is 4 squared?','a':'8','b':'12','c':'16','correct':'c'},
            {'q':'Solve: 3x = 24, x=?','a':'6','b':'8','c':'9','correct':'b'},
            {'q':'Area of 6x4 rectangle?','a':'20','b':'24','c':'28','correct':'b'},
            {'q':'What is 144 divided by 12?','a':'10','b':'11','c':'12','correct':'c'},
            {'q':'What is 15% of 80?','a':'10','b':'12','c':'15','correct':'b'},
            {'q':'Square root of 64?','a':'6','b':'7','c':'8','correct':'c'},
            {'q':'What is 7 cubed?','a':'343','b':'147','c':'49','correct':'a'},
            {'q':'Perimeter of 5x3 rectangle?','a':'15','b':'16','c':'20','correct':'b'},
        ]
        ed = self.realm_data['education']
        idx = ed['math_index'] % len(problems)
        p = problems[idx]
        answered = ed['math_answered']
        selected = ed['math_selected']
        self.screen.fill((12,18,30))
        hf = get_font(48, bold=True)
        hm = hf.render("MATH PRACTICE", True, (100,200,255))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 25))
        pf = get_font(36)
        pm = pf.render(f"Problem {idx+1} of {len(problems)}", True, (140,160,185))
        self.screen.blit(pm, (self.width//2-pm.get_width()//2, 82))
        qw, qh = 900, 120
        qx = (self.width-qw)//2
        pygame.draw.rect(self.screen, (22,35,58), pygame.Rect(qx,125,qw,qh), border_radius=16)
        pygame.draw.rect(self.screen, (100,160,255), pygame.Rect(qx,125,qw,qh), 2, border_radius=16)
        qf2 = get_font(58, bold=True)
        qm2 = qf2.render(p['q'], True, (255,255,255))
        self.screen.blit(qm2, (self.width//2-qm2.get_width()//2, 158))
        answers = [('A',p['a']),('B',p['b']),('C',p['c'])]
        aw, ah = 260, 88
        gap2 = 28
        total_w = 3*aw+2*gap2
        ax_start = (self.width-total_w)//2
        ay = 285
        for i,(key,val) in enumerate(answers):
            ax = ax_start + i*(aw+gap2)
            is_correct = key == p['correct'].upper()
            is_sel = key == (selected or '').upper()
            if answered:
                bg = (40,160,80) if is_correct else (160,40,40) if is_sel else (22,32,50)
                bc = (80,220,120) if is_correct else (220,80,80) if is_sel else (50,65,90)
            elif is_sel:
                bg = (40,60,100); bc = (100,160,255)
            else:
                bg = (22,32,50); bc = (60,80,110)
            arect = pygame.Rect(ax,ay,aw,ah)
            pygame.draw.rect(self.screen, bg, arect, border_radius=14)
            pygame.draw.rect(self.screen, bc, arect, 2, border_radius=14)
            kf = get_font(52, bold=True)
            km = kf.render(key, True, (255,200,80))
            self.screen.blit(km, (ax+18, ay+ah//2-km.get_height()//2))
            vf = get_font(46, bold=True)
            vm = vf.render(val, True, (240,245,255))
            self.screen.blit(vm, (ax+65, ay+ah//2-vm.get_height()//2))
        if answered:
            is_right = (selected or '').upper() == p['correct'].upper()
            fc = (80,220,120) if is_right else (220,80,80)
            ft = "Correct! Well done!" if is_right else f"Incorrect - Answer was {p['correct'].upper()}: {p[p['correct']]}"
            fbf = get_font(48, bold=True)
            fbm = fbf.render(ft, True, fc)
            self.screen.blit(fbm, (self.width//2-fbm.get_width()//2, 408))
        ff = get_font(30)
        fm = ff.render("A/B/C Answer  |  N Next  |  B Back", True, (90,105,125)) if not answered else ff.render("N Next problem  |  B Back", True, (90,105,125))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _edu_vocab(self):
        words = [
            ('Perseverance','Continued effort despite difficulty or delay in achieving success','"Her perseverance paid off when she solved the equation."'),
            ('Hypothesis','An educated guess or proposed explanation for an observation','"The scientist formed a hypothesis before the experiment."'),
            ('Inference','A conclusion reached using evidence and reasoning','"Based on the clues, she made an inference about the answer."'),
            ('Propaganda','Information used to promote a particular point of view','"The poster was propaganda to influence public opinion."'),
            ('Symmetry','Exact match of shape or size across a dividing line','"The butterfly wings showed perfect symmetry."'),
            ('Erosion','The gradual wearing away of rock or soil by water or wind','"Erosion carved the Grand Canyon over millions of years."'),
            ('Democracy','A government system where power comes from the people','"In a democracy, citizens vote for their representatives."'),
            ('Condensation','Water vapor cooling and turning into liquid droplets','"Condensation formed on the cold glass on a hot day."'),
            ('Protagonist','The main character in a story or narrative','"Harry Potter is the protagonist of the series."'),
            ('Legislation','Laws made by a government or legislative body','"New legislation was passed to protect the environment."'),
        ]
        ed = self.realm_data['education']
        idx = ed['vocab_index'] % len(words)
        revealed = ed['vocab_revealed']
        w = words[idx]
        self.screen.fill((12,18,30))
        hf = get_font(48, bold=True)
        hm = hf.render("VOCABULARY", True, (180,120,255))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 25))
        pf = get_font(36)
        pm = pf.render(f"Word {idx+1} of {len(words)}", True, (140,160,185))
        self.screen.blit(pm, (self.width//2-pm.get_width()//2, 82))
        cw2, ch2 = 1000, 360
        cx2 = (self.width-cw2)//2
        cy2 = 128
        pygame.draw.rect(self.screen, (22,18,42), pygame.Rect(cx2,cy2,cw2,ch2), border_radius=20)
        pygame.draw.rect(self.screen, (180,120,255), pygame.Rect(cx2,cy2,cw2,ch2), 3, border_radius=20)
        wf = get_font(72, bold=True)
        wm = wf.render(w[0], True, (220,180,255))
        self.screen.blit(wm, (cx2+cw2//2-wm.get_width()//2, cy2+18))
        if revealed:
            pygame.draw.line(self.screen, (80,60,120), (cx2+40,cy2+110), (cx2+cw2-40,cy2+110), 2)
            df2 = get_font(34)
            dwords = w[1].split()
            dlines, dline = [], []
            for dw in dwords:
                test = ' '.join(dline+[dw])
                if df2.size(test)[0] > cw2-80: dlines.append(' '.join(dline)); dline=[dw]
                else: dline.append(dw)
            if dline: dlines.append(' '.join(dline))
            for i, ln in enumerate(dlines):
                lm = df2.render(ln, True, (200,215,240))
                self.screen.blit(lm, (cx2+cw2//2-lm.get_width()//2, cy2+126+i*42))
            ef2 = get_font(28)
            ef2m = ef2.render(w[2], True, (130,150,130))
            self.screen.blit(ef2m, (cx2+cw2//2-ef2m.get_width()//2, cy2+295))
        else:
            hint = get_font(38)
            hm2 = hint.render("Press SPACE to reveal definition", True, (100,120,150))
            self.screen.blit(hm2, (cx2+cw2//2-hm2.get_width()//2, cy2+155))
        ff = get_font(30)
        fm = ff.render("SPACE Reveal  |  N Next word  |  B Back", True, (90,105,125))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _edu_timer(self):
        import time as _t
        ed = self.realm_data['education']
        modes = [
            {'name':'Focus Session','duration':25*60,'color':(100,200,255)},
            {'name':'Break','duration':5*60,'color':(100,220,130)},
            {'name':'Review Session','duration':10*60,'color':(255,180,80)},
        ]
        mode_idx = ed['timer_mode'] % len(modes)
        mode = modes[mode_idx]
        running = ed['timer_running']
        if running:
            elapsed = ed['timer_elapsed'] + (_t.time() - ed['timer_start'])
        else:
            elapsed = ed['timer_elapsed']
        remaining = max(0, mode['duration'] - elapsed)
        mins = int(remaining) // 60
        secs = int(remaining) % 60
        if remaining <= 0 and running:
            ed['timer_running'] = False
            ed['timer_elapsed'] = mode['duration']
        self.screen.fill((10,14,22))
        mf = get_font(52, bold=True)
        mm = mf.render(mode['name'], True, mode['color'])
        self.screen.blit(mm, (self.width//2-mm.get_width()//2, 40))
        tf2 = get_font(200, bold=True)
        tm2 = tf2.render(f"{mins:02d}:{secs:02d}", True, mode['color'])
        self.screen.blit(tm2, (self.width//2-tm2.get_width()//2, 110))
        bar_w = 800
        bar_x = (self.width-bar_w)//2
        bar_y = 365
        progress = 1-(remaining/mode['duration'])
        pygame.draw.rect(self.screen, (30,40,55), pygame.Rect(bar_x,bar_y,bar_w,18), border_radius=9)
        if progress > 0:
            pygame.draw.rect(self.screen, mode['color'], pygame.Rect(bar_x,bar_y,int(bar_w*progress),18), border_radius=9)
        sf = get_font(40)
        status = "RUNNING" if running else ("COMPLETE" if remaining<=0 else "PAUSED")
        sc = (80,220,120) if running else ((255,180,50) if remaining>0 else (220,100,100))
        sm = sf.render(status, True, sc)
        self.screen.blit(sm, (self.width//2-sm.get_width()//2, 410))
        for i, m in enumerate(modes):
            mc = m['color'] if i==mode_idx else (50,60,80)
            mf2 = get_font(30)
            mbg = pygame.Rect(self.width//2-320+i*215, 468, 190, 40)
            pygame.draw.rect(self.screen, (20,28,44) if i!=mode_idx else (30,42,62), mbg, border_radius=10)
            pygame.draw.rect(self.screen, mc, mbg, 2, border_radius=10)
            mm2 = mf2.render(m['name'], True, mc)
            self.screen.blit(mm2, (mbg.x+mbg.w//2-mm2.get_width()//2, mbg.y+9))
        ff = get_font(30)
        fm = ff.render("S Start/Pause  |  R Reset  |  M Switch mode  |  B Back", True, (80,95,115))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _edu_quiz(self):
        questions = [
            {'q':'What is the capital of the United States?','a':'New York','b':'Washington DC','c':'Los Angeles','d':'Chicago','correct':'b'},
            {'q':'Which planet is known as the Red Planet?','a':'Venus','b':'Jupiter','c':'Mars','d':'Saturn','correct':'c'},
            {'q':'How many sides does a hexagon have?','a':'5','b':'6','c':'7','d':'8','correct':'b'},
            {'q':'Who wrote the Declaration of Independence?','a':'G. Washington','b':'B. Franklin','c':'T. Jefferson','d':'J. Adams','correct':'c'},
            {'q':'What gas do plants absorb from the air?','a':'Oxygen','b':'Nitrogen','c':'Carbon Dioxide','d':'Hydrogen','correct':'c'},
        ]
        ed = self.realm_data['education']
        idx = ed['quiz_index']
        if idx >= len(questions):
            self.screen.fill((12,18,30))
            rf = get_font(72, bold=True)
            rm = rf.render("Quiz Complete!", True, (255,180,50))
            self.screen.blit(rm, (self.width//2-rm.get_width()//2, 180))
            sf2 = get_font(96, bold=True)
            sc2 = (80,220,120) if ed['quiz_score']>=4 else (255,180,50) if ed['quiz_score']>=3 else (220,100,100)
            sm2 = sf2.render(f"{ed['quiz_score']} / {len(questions)}", True, sc2)
            self.screen.blit(sm2, (self.width//2-sm2.get_width()//2, 290))
            msg = "Excellent!" if ed['quiz_score']>=4 else "Good effort!" if ed['quiz_score']>=3 else "Keep practicing!"
            mf3 = get_font(48)
            mm3 = mf3.render(msg, True, sc2)
            self.screen.blit(mm3, (self.width//2-mm3.get_width()//2, 420))
            ff = get_font(32)
            fm = ff.render("R  Restart  |  B  Back", True, (90,105,125))
            self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))
            return
        q = questions[idx]
        answered = ed['quiz_answered']
        sel = ed['quiz_selected']
        self.screen.fill((12,18,30))
        hf = get_font(40, bold=True)
        hm = hf.render(f"QUIZ  -  Question {idx+1} of {len(questions)}  -  Score: {ed['quiz_score']}", True, (255,160,60))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 22))
        qw2, qh2 = 1000, 100
        qx2 = (self.width-qw2)//2
        pygame.draw.rect(self.screen, (22,32,52), pygame.Rect(qx2,72,qw2,qh2), border_radius=14)
        pygame.draw.rect(self.screen, (255,160,60), pygame.Rect(qx2,72,qw2,qh2), 2, border_radius=14)
        qf3 = get_font(42, bold=True)
        qm3 = qf3.render(q['q'], True, (255,255,255))
        self.screen.blit(qm3, (self.width//2-qm3.get_width()//2, 104))
        opts = [('A',q['a']),('B',q['b']),('C',q['c']),('D',q['d'])]
        ow, oh = 460, 76
        ogap = 18
        ox_start = (self.width-(2*ow+ogap))//2
        positions = [(ox_start,205),(ox_start+ow+ogap,205),(ox_start,205+oh+ogap),(ox_start+ow+ogap,205+oh+ogap)]
        for i,((ox,oy),(key,val)) in enumerate(zip(positions,opts)):
            is_correct = key == q['correct'].upper()
            is_sel = key == (sel or '').upper()
            if answered:
                bg = (35,140,65) if is_correct else (140,35,35) if is_sel else (20,28,44)
                bc = (70,210,100) if is_correct else (210,70,70) if is_sel else (45,58,80)
            elif is_sel:
                bg=(35,55,95); bc=(100,150,255)
            else:
                bg=(20,28,44); bc=(55,70,95)
            orect = pygame.Rect(ox,oy,ow,oh)
            pygame.draw.rect(self.screen, bg, orect, border_radius=12)
            pygame.draw.rect(self.screen, bc, orect, 2, border_radius=12)
            kf2 = get_font(42, bold=True)
            km2 = kf2.render(key, True, (255,200,80))
            self.screen.blit(km2, (ox+16, oy+oh//2-km2.get_height()//2))
            vf2 = get_font(36)
            vm2 = vf2.render(val, True, (230,238,255))
            self.screen.blit(vm2, (ox+58, oy+oh//2-vm2.get_height()//2))
        if answered:
            is_right = (sel or '').upper() == q['correct'].upper()
            fc = (80,220,120) if is_right else (220,80,80)
            ft = "Correct!" if is_right else f"Incorrect - Answer: {q['correct'].upper()}"
            fbf2 = get_font(48, bold=True)
            fbm2 = fbf2.render(ft, True, fc)
            self.screen.blit(fbm2, (self.width//2-fbm2.get_width()//2, 408))
        ff = get_font(30)
        fm = ff.render("A/B/C/D Answer  |  N Next  |  B Back", True, (80,95,115)) if not answered else ff.render("N Next question  |  B Back", True, (80,95,115))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _edu_daily(self):
        import datetime
        today = datetime.date.today()
        lessons = [
            ('Fractions & Decimals','Converting between fractions and decimals'),
            ('Reading Comprehension','Main idea, supporting details, and inference'),
            ('Earth Science','The water cycle and weather patterns'),
            ('American History','The Revolution and founding documents'),
            ('Geometry','Perimeter, area, and volume'),
            ('Creative Writing','Story structure and descriptive language'),
            ('Life Science','Cell structure and living organisms'),
        ]
        lesson = lessons[today.weekday() % len(lessons)]
        self.screen.fill((10,16,26))
        hf = get_font(48, bold=True)
        hm = hf.render("DAILY LESSON", True, (255,200,80))
        self.screen.blit(hm, (self.width//2-hm.get_width()//2, 30))
        df3 = get_font(34)
        dm3 = df3.render(today.strftime("Today is %A, %B %d"), True, (140,160,185))
        self.screen.blit(dm3, (self.width//2-dm3.get_width()//2, 88))
        lw, lh = 900, 300
        lx = (self.width-lw)//2
        ly = 140
        pygame.draw.rect(self.screen, (20,30,48), pygame.Rect(lx,ly,lw,lh), border_radius=22)
        pygame.draw.rect(self.screen, (255,200,80), pygame.Rect(lx,ly,lw,lh), 3, border_radius=22)
        tf3 = get_font(62, bold=True)
        tm3 = tf3.render(lesson[0], True, (255,220,120))
        self.screen.blit(tm3, (lx+lw//2-tm3.get_width()//2, ly+60))
        sf3 = get_font(38)
        sm3 = sf3.render(lesson[1], True, (180,200,225))
        self.screen.blit(sm3, (lx+lw//2-sm3.get_width()//2, ly+148))
        tf4 = get_font(32)
        tm4 = tf4.render("Explore this topic in your other learning modules", True, (110,130,155))
        self.screen.blit(tm4, (lx+lw//2-tm4.get_width()//2, ly+220))
        ff = get_font(30)
        fm = ff.render("B  Back to Education", True, (80,95,115))
        self.screen.blit(fm, (self.width//2-fm.get_width()//2, self.height-48))

    def _render_live_question(self):
        q = self.realm_data['education']['live_question']
        answered = self.realm_data['education']['live_answered']
        correct = self.realm_data['education']['live_correct']
        if not q: return
        if not hasattr(self, '_quiz_overlay'):
            self._quiz_overlay = pygame.Surface((self.width, self.height))
            self._quiz_overlay.set_alpha(230)
            self._quiz_overlay.fill((15,20,35))
        self.screen.blit(self._quiz_overlay, (0,0))
        cw3, ch3 = 1000, 540
        cx3 = (self.width-cw3)//2
        cy3 = (self.height-ch3)//2
        pygame.draw.rect(self.screen, (28,38,58), pygame.Rect(cx3,cy3,cw3,ch3), border_radius=20)
        pygame.draw.rect(self.screen, (255,180,50), pygame.Rect(cx3,cy3,cw3,ch3), 3, border_radius=20)
        hf4 = get_font(38, bold=True)
        hm4 = hf4.render("Dad sent you a question!", True, (255,180,50))
        self.screen.blit(hm4, (cx3+cw3//2-hm4.get_width()//2, cy3+16))
        qf4 = get_font(48, bold=True)
        qm4 = qf4.render(q.get('q',''), True, (255,255,255))
        self.screen.blit(qm4, (cx3+40, cy3+72))
        for i,(key,val) in enumerate([('A',q.get('a','')),('B',q.get('b','')),('C',q.get('c',''))]):
            is_correct4 = key.lower() == q.get('correct','')
            ay4 = cy3+150+i*110
            if answered:
                bg4=(40,150,70) if is_correct4 else (50,55,75)
                border4=(80,210,110) if is_correct4 else (70,80,100)
            else:
                bg4=(38,50,72); border4=(90,108,140)
            arect4 = pygame.Rect(cx3+36, ay4, cw3-72, 88)
            pygame.draw.rect(self.screen, bg4, arect4, border_radius=10)
            pygame.draw.rect(self.screen, border4, arect4, 2, border_radius=10)
            kf4 = get_font(52, bold=True)
            km4 = kf4.render(key, True, (255,180,50))
            self.screen.blit(km4, (cx3+55, ay4+20))
            vf4 = get_font(38)
            vm4 = vf4.render(val, True, (240,245,255))
            self.screen.blit(vm4, (cx3+105, ay4+24))
        if answered:
            fc4=(80,220,120) if correct else (220,80,80)
            ft4="Correct! Great job!" if correct else "Not quite - keep trying!"
            fbf4 = get_font(48, bold=True)
            fbm4 = fbf4.render(ft4, True, fc4)
            self.screen.blit(fbm4, (cx3+cw3//2-fbm4.get_width()//2, cy3+490))
        else:
            hf5 = get_font(30)
            hm5 = hf5.render("Press A, B, or C to answer  |  ESC to dismiss", True, (120,138,158))
            self.screen.blit(hm5, (cx3+cw3//2-hm5.get_width()//2, cy3+505))

    def _edu_ambient(self):
        """Ambient sleep mode - cycles flashcards with fade"""
        import time as _ta
        import math
        cards = [
            ('What is photosynthesis?', 'Plants converting sunlight into food'),
            ('Define: Democracy', 'Citizens vote for their representatives'),
            ('What is gravity?', 'The force pulling objects toward each other'),
            ('Define: Fraction', 'A number representing part of a whole'),
            ('What is the water cycle?', 'Evaporation, Condensation, Precipitation'),
            ('What is an ecosystem?', 'Living things interacting with their environment'),
            ('What is a metaphor?', 'A direct comparison between two unlike things'),
            ('Define: Migration', 'Seasonal movement of animals between regions'),
            ('Who was Abraham Lincoln?', '16th US President — ended slavery'),
            ('What is the Constitution?', 'The supreme law of the United States'),
        ]
        ed = self.realm_data['education']
        elapsed = _ta.time() - ed['ambient_start']
        cycle = 15  # seconds per card
        card_idx = int(elapsed / cycle) % len(cards)
        card_phase = (elapsed % cycle) / cycle  # 0.0 to 1.0

        # Fade in/out alpha
        if card_phase < 0.15:
            alpha = int(255 * (card_phase / 0.15))
        elif card_phase > 0.85:
            alpha = int(255 * ((1.0 - card_phase) / 0.15))
        else:
            alpha = 255

        # Soft pulse on the text
        pulse = 0.85 + 0.15 * math.sin(_ta.time() * 0.8)

        self.screen.fill((8, 12, 20))

        card = cards[card_idx]
        show_answer = card_phase > 0.45

        # Question
        qf = get_font(58, bold=True)
        qm = qf.render(card[0], True, (int(220*pulse), int(200*pulse), int(100*pulse)))
        surf_q = pygame.Surface(qm.get_size(), pygame.SRCALPHA)
        surf_q.blit(qm, (0,0))
        surf_q.set_alpha(alpha)
        self.screen.blit(surf_q, (self.width//2 - qm.get_width()//2, self.height//2 - 80))

        if show_answer:
            af = get_font(44)
            am = af.render(card[1], True, (int(100*pulse), int(210*pulse), int(150*pulse)))
            surf_a = pygame.Surface(am.get_size(), pygame.SRCALPHA)
            surf_a.blit(am, (0,0))
            surf_a.set_alpha(alpha)
            self.screen.blit(surf_a, (self.width//2 - am.get_width()//2, self.height//2 + 20))

        # Progress dots
        dot_y = self.height - 60
        dot_spacing = 24
        total_w = len(cards) * dot_spacing
        dot_x_start = self.width//2 - total_w//2
        for i in range(len(cards)):
            color = (200, 180, 80) if i == card_idx else (40, 50, 65)
            pygame.draw.circle(self.screen, color, (dot_x_start + i*dot_spacing, dot_y), 5)

        # Subtle wake hint
        hf = get_font(28)
        hm = hf.render("Press any key to interact", True, (50, 62, 80))
        self.screen.blit(hm, (self.width//2 - hm.get_width()//2, self.height - 32))

    def handle_education_input(self, key):
        import time as _t
        ed = self.realm_data['education']
        module = ed['module']
        ed['last_input_time'] = _t.time()
        if ed['ambient_mode']:
            ed['ambient_mode'] = False
            return

        if ed['live_question_active']:
            q = ed['live_question']
            if not ed['live_answered']:
                answer = None
                if key == pygame.K_a: answer = 'a'
                elif key == pygame.K_b: answer = 'b'
                elif key == pygame.K_c: answer = 'c'
                if answer:
                    correct4 = answer == q.get('correct','')
                    ed['live_answered'] = True
                    ed['live_correct'] = correct4
                    if self.presence:
                        self.presence.broadcast({'type':'EDUCATION_ANSWER','from':'Daughter',
                            'answer':answer.upper(),'correct':correct4,'question':q.get('q','')})
            elif key in (pygame.K_ESCAPE, pygame.K_n):
                ed['live_question_active'] = False
                ed['live_question'] = None
            return

        if module is None:
            if key == pygame.K_LEFT: ed['selected'] = max(0, ed['selected']-1)
            elif key == pygame.K_RIGHT: ed['selected'] = min(5, ed['selected']+1)
            elif key == pygame.K_UP: ed['selected'] = max(0, ed['selected']-3)
            elif key == pygame.K_DOWN: ed['selected'] = min(5, ed['selected']+3)
            elif key == pygame.K_p: ed['preview_open'] = not ed['preview_open']
            elif key == pygame.K_RETURN:
                mods = ['flashcards','math','vocab','timer','quiz','daily']
                ed['module'] = mods[ed['selected']]
                ed['preview_open'] = False
                if ed['module'] == 'flashcards': ed['flashcard_index']=0; ed['flashcard_revealed']=False
                elif ed['module'] == 'math': ed['math_index']=0; ed['math_answered']=False; ed['math_selected']=None
                elif ed['module'] == 'vocab': ed['vocab_index']=0; ed['vocab_revealed']=False
                elif ed['module'] == 'timer': ed['timer_running']=False; ed['timer_mode']=0; ed['timer_start']=0; ed['timer_elapsed']=0
                elif ed['module'] == 'quiz': ed['quiz_index']=0; ed['quiz_selected']=None; ed['quiz_answered']=False; ed['quiz_score']=0
            elif key == pygame.K_ESCAPE: self.go_back()
            return

        if module == 'flashcards':
            if key == pygame.K_SPACE: ed['flashcard_revealed'] = True
            elif key == pygame.K_n: ed['flashcard_index'] += 1; ed['flashcard_revealed'] = False
            elif key in (pygame.K_b, pygame.K_ESCAPE): ed['module'] = None

        elif module == 'math':
            if not ed['math_answered']:
                if key == pygame.K_a: ed['math_selected']='a'; ed['math_answered']=True
                elif key == pygame.K_b: ed['math_selected']='b'; ed['math_answered']=True
                elif key == pygame.K_c: ed['math_selected']='c'; ed['math_answered']=True
            else:
                if key == pygame.K_n: ed['math_index']+=1; ed['math_answered']=False; ed['math_selected']=None
            if key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None

        elif module == 'vocab':
            if key == pygame.K_SPACE: ed['vocab_revealed'] = True
            elif key == pygame.K_n: ed['vocab_index']+=1; ed['vocab_revealed']=False
            elif key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None

        elif module == 'timer':
            if key == pygame.K_s:
                if ed['timer_running']:
                    ed['timer_elapsed'] += _t.time()-ed['timer_start']
                    ed['timer_running'] = False
                else:
                    ed['timer_start'] = _t.time()
                    ed['timer_running'] = True
            elif key == pygame.K_r: ed['timer_running']=False; ed['timer_elapsed']=0; ed['timer_start']=0
            elif key == pygame.K_m: ed['timer_mode']=(ed['timer_mode']+1)%3; ed['timer_running']=False; ed['timer_elapsed']=0
            elif key in (pygame.K_b, pygame.K_ESCAPE): ed['timer_running']=False; ed['module']=None

        elif module == 'quiz':
            questions5 = [{'correct':'b'},{'correct':'c'},{'correct':'b'},{'correct':'c'},{'correct':'c'}]
            if ed['quiz_index'] >= 5:
                if key == pygame.K_r: ed['quiz_index']=0; ed['quiz_score']=0; ed['quiz_selected']=None; ed['quiz_answered']=False
                elif key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None
            elif not ed['quiz_answered']:
                answer2 = None
                if key == pygame.K_a: answer2='A'
                elif key == pygame.K_b: answer2='B'
                elif key == pygame.K_c: answer2='C'
                elif key == pygame.K_d: answer2='D'
                if answer2:
                    ed['quiz_selected'] = answer2
                    ed['quiz_answered'] = True
                    if answer2.lower() == questions5[ed['quiz_index']]['correct']:
                        ed['quiz_score'] += 1
                if key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None
            else:
                if key == pygame.K_n: ed['quiz_index']+=1; ed['quiz_selected']=None; ed['quiz_answered']=False
                elif key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None

        elif module == 'daily':
            if key in (pygame.K_b, pygame.K_ESCAPE): ed['module']=None

    def render_productivity(self):
        """Productivity - Focus. Execute. Progress."""
        data = self.realm_data['productivity']
        selected = data['selected']
        active_module = data['active_module']

        if active_module is not None:
            self._render_productivity_module(active_module)
            return

        tiles = [
            {'emoji': '✅', 'name': 'Tasks',           'sub': 'Your priorities'},
            {'emoji': '⏱️', 'name': 'Focus Timer',     'sub': 'Stay on track'},
            {'emoji': '📝', 'name': 'Quick Notes',     'sub': 'Capture fast'},
            {'emoji': '📅', 'name': 'Daily Plan',      'sub': 'Your day ahead'},
            {'emoji': '🔔', 'name': 'Reminders',       'sub': 'Stay notified'},
            {'emoji': '📊', 'name': 'Session Summary', 'sub': 'How you did'},
        ]

        title_font  = get_font(72, bold=True)
        sub_font    = get_font(42)
        name_font   = get_font(44, bold=True)
        desc_font   = get_font(34)
        hint_font   = get_font(32)
        emoji_font  = load_emoji_font(52)

        title_surf = title_font.render('PRODUCTIVITY', True, (100, 160, 255))
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 38))

        sub_surf = sub_font.render('Focus. Execute. Progress.', True, (140, 170, 210))
        self.screen.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, 118))

        card_w, card_h = 340, 180
        gap_x, gap_y   = 40, 30
        cols = 3
        grid_w = cols * card_w + (cols - 1) * gap_x
        start_x = (self.width - grid_w) // 2
        start_y = 168

        for i, tile in enumerate(tiles):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            is_sel = (i == selected)

            bg = (32, 44, 62) if is_sel else (18, 24, 34)
            pygame.draw.rect(self.screen, bg, (x, y, card_w, card_h), border_radius=12)
            if is_sel:
                pygame.draw.rect(self.screen, (100, 160, 255), (x-4, y-4, card_w+8, card_h+8), width=4, border_radius=14)

            em = emoji_font.render(tile['emoji'], True, (255, 255, 255))
            self.screen.blit(em, (x + 18, y + 22))

            nc = (255, 255, 255) if is_sel else (200, 210, 230)
            ns = name_font.render(tile['name'], True, nc)
            self.screen.blit(ns, (x + 18, y + 88))

            ds = desc_font.render(tile['sub'], True, (130, 150, 180))
            self.screen.blit(ds, (x + 18, y + 132))

        hint = hint_font.render('Arrow Keys: Navigate  |  ENTER: Open  |  ESC: Back', True, (90, 110, 140))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

    def _render_productivity_module(self, module_index):
        import time as _t
        data = self.realm_data['productivity']
        pd   = data.get('mod_data', {})

        title_font  = get_font(62, bold=True)
        body_font   = get_font(44)
        small_font  = get_font(36)
        hint_font   = get_font(32)
        big_font    = get_font(120, bold=True)
        head_font   = get_font(48, bold=True)

        # ── 0: TASKS ──────────────────────────────────────────────
        if module_index == 0:
            tasks = pd.get('tasks', [
                {'text': 'Review patent filing checklist',  'done': False},
                {'text': 'Send VR&E follow-up email',       'done': False},
                {'text': 'Test voice pipeline on Pi 4',     'done': True},
                {'text': 'Update MotiBeamOS realm list',    'done': False},
                {'text': 'Confirm MacroFab BOM review',     'done': False},
                {'text': 'Draft Kickstarter outline',       'done': False},
            ])
            sel = pd.get('task_sel', 0)

            t = title_font.render('TASKS', True, (100, 200, 120))
            self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 40))

            for i, task in enumerate(tasks):
                y = 130 + i * 72
                is_s = (i == sel)
                bg = (28, 48, 32) if is_s else (16, 26, 20)
                pygame.draw.rect(self.screen, bg, (120, y, self.width - 240, 58), border_radius=10)
                if is_s:
                    pygame.draw.rect(self.screen, (80, 200, 100), (116, y-4, self.width-232, 66), width=3, border_radius=12)

                check = '✔' if task['done'] else '○'
                cc    = (80, 220, 100) if task['done'] else (160, 170, 190)
                cs    = body_font.render(check, True, cc)
                self.screen.blit(cs, (140, y + 10))

                tc = (140, 160, 140) if task['done'] else (220, 230, 240)
                ts = body_font.render(task['text'], True, tc)
                self.screen.blit(ts, (200, y + 10))

                if task['done']:
                    done_s = small_font.render('Done', True, (80, 180, 80))
                    self.screen.blit(done_s, (self.width - 220, y + 14))

            hint = hint_font.render('UP/DOWN: Navigate  |  SPACE: Complete  |  B: Back', True, (90, 110, 130))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

        # ── 1: FOCUS TIMER ────────────────────────────────────────
        elif module_index == 1:
            running      = pd.get('timer_running', False)
            mode         = pd.get('timer_mode', 'focus')
            focus_screen = pd.get('focus_screen', False)
            remaining    = pd.get('timer_remaining', 25 * 60)

            if running:
                elapsed   = _t.time() - pd.get('timer_ref', _t.time())
                remaining = max(0, pd.get('timer_snapshot', remaining) - elapsed)
                if remaining == 0:
                    data['mod_data']['timer_running'] = False

            mins = int(remaining) // 60
            secs = int(remaining) % 60
            timer_str  = f'{mins:02d}:{secs:02d}'
            mode_color = (100, 180, 255) if mode == 'focus' else (100, 220, 140)
            mode_label = 'FOCUS MODE' if mode == 'focus' else 'BREAK MODE'

            if focus_screen:
                # ── Immersive Focus Screen ──
                self.screen.fill((0, 0, 0))
                giant_font = get_font(220, bold=True)
                tc = giant_font.render(timer_str, True, mode_color)
                self.screen.blit(tc, (self.width // 2 - tc.get_width() // 2, self.height // 2 - 120))
                dim_hint = hint_font.render('S: Start/Pause  |  F: Exit Focus Mode', True, (50, 60, 70))
                self.screen.blit(dim_hint, (self.width // 2 - dim_hint.get_width() // 2, self.height - 52))
            else:
                # ── Normal Timer View ──
                ml = title_font.render('FOCUS TIMER', True, mode_color)
                self.screen.blit(ml, (self.width // 2 - ml.get_width() // 2, 40))

                mds = head_font.render(mode_label, True, mode_color)
                self.screen.blit(mds, (self.width // 2 - mds.get_width() // 2, 118))

                ts = big_font.render(timer_str, True, (240, 245, 255))
                self.screen.blit(ts, (self.width // 2 - ts.get_width() // 2, self.height // 2 - 80))

                status = 'Running...' if running else 'Paused'
                sc = (100, 220, 100) if running else (200, 160, 80)
                ss = body_font.render(status, True, sc)
                self.screen.blit(ss, (self.width // 2 - ss.get_width() // 2, self.height // 2 + 80))

                hint = hint_font.render('S: Start/Pause  |  R: Reset  |  M: Mode  |  F: Focus Screen  |  B: Back', True, (90, 110, 130))
                self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

        # ── 2: QUICK NOTES ────────────────────────────────────────
        elif module_index == 2:
            notes = pd.get('notes', [
                'Follow up with patent attorney re: PCT deadline Aug 29',
                'VR&E funds — confirm with Laquintic after April 15',
                'MacroFab: send Gerber files + BOM before OEM talks',
                'Kickstarter soft launch target: Q3 2026',
                'Voice pipeline: test SunFounder mic with Vosk on Pi 4',
            ])
            sel = pd.get('note_sel', 0)

            t = title_font.render('QUICK NOTES', True, (255, 210, 80))
            self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 40))

            for i, note in enumerate(notes):
                y = 130 + i * 80
                is_s = (i == sel)
                bg = (48, 40, 18) if is_s else (24, 22, 14)
                pygame.draw.rect(self.screen, bg, (100, y, self.width - 200, 64), border_radius=10)
                if is_s:
                    pygame.draw.rect(self.screen, (255, 200, 60), (96, y-4, self.width-192, 72), width=3, border_radius=12)

                idx_s = small_font.render(f'{i+1}.', True, (180, 160, 80))
                self.screen.blit(idx_s, (120, y + 16))

                nc = (255, 240, 180) if is_s else (200, 195, 160)
                ns = body_font.render(note[:62] + ('…' if len(note) > 62 else ''), True, nc)
                self.screen.blit(ns, (170, y + 16))

            hint = hint_font.render('UP/DOWN: Navigate  |  B: Back', True, (90, 110, 130))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

        # ── 3: DAILY PLAN ─────────────────────────────────────────
        elif module_index == 3:
            plan = pd.get('daily_plan', {
                'Morning':   ['Review patent checklist', 'Check VR&E email', 'Pi 4 voice test'],
                'Afternoon': ['MacroFab BOM draft', 'MotiBeamOS realm review'],
                'Evening':   ['Kickstarter outline', 'Update memory notes'],
            })

            t = title_font.render('DAILY PLAN', True, (160, 140, 255))
            self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 40))

            colors = {'Morning': (255, 200, 80), 'Afternoon': (100, 200, 255), 'Evening': (180, 130, 255)}
            y = 130
            for section, items in plan.items():
                sc = colors.get(section, (200, 200, 200))
                sh = head_font.render(section, True, sc)
                self.screen.blit(sh, (140, y))
                y += 54
                for item in items:
                    dot = small_font.render('•  ' + item, True, (200, 210, 230))
                    self.screen.blit(dot, (180, y))
                    y += 46
                y += 16

            hint = hint_font.render('B: Back', True, (90, 110, 130))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

        # ── 4: REMINDERS ──────────────────────────────────────────
        elif module_index == 4:
            reminders = pd.get('reminders', [
                {'time': '9:00 AM',  'text': 'VR&E check-in call',          'type': 'meeting'},
                {'time': '11:30 AM', 'text': 'Review patent action items',   'type': 'task'},
                {'time': '2:00 PM',  'text': 'Follow up — MacroFab email',   'type': 'follow-up'},
                {'time': '4:00 PM',  'text': 'MotiBeamOS demo run-through',  'type': 'task'},
                {'time': '6:00 PM',  'text': 'End-of-day session summary',   'type': 'review'},
            ])
            sel = pd.get('reminder_sel', 0)

            t = title_font.render('REMINDERS', True, (255, 130, 100))
            self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 40))

            type_colors = {'meeting': (100, 180, 255), 'task': (100, 220, 120), 'follow-up': (255, 200, 80), 'review': (180, 130, 255)}

            for i, rem in enumerate(reminders):
                y = 130 + i * 82
                is_s = (i == sel)
                bg = (48, 28, 22) if is_s else (24, 16, 14)
                pygame.draw.rect(self.screen, bg, (100, y, self.width - 200, 66), border_radius=10)
                if is_s:
                    pygame.draw.rect(self.screen, (255, 120, 80), (96, y-4, self.width-192, 74), width=3, border_radius=12)

                tc = type_colors.get(rem['type'], (200, 200, 200))
                time_s = head_font.render(rem['time'], True, tc)
                self.screen.blit(time_s, (130, y + 14))

                rs = body_font.render(rem['text'], True, (220, 225, 235))
                self.screen.blit(rs, (310, y + 14))

                tag_s = small_font.render(f'[{rem["type"]}]', True, tc)
                self.screen.blit(tag_s, (self.width - 220, y + 20))

            hint = hint_font.render('UP/DOWN: Navigate  |  B: Back', True, (90, 110, 130))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

        # ── 5: SESSION SUMMARY ────────────────────────────────────
        elif module_index == 5:
            completed = sum(1 for t in pd.get('tasks', []) if t.get('done'))
            total     = len(pd.get('tasks', [{'done': False}] * 6))
            focused   = pd.get('focus_minutes', 25)

            if completed >= total:
                msg = 'Outstanding session. All tasks done!'
                mc  = (100, 220, 120)
            elif completed >= total // 2:
                msg = 'Solid progress. Keep the momentum.'
                mc  = (100, 180, 255)
            else:
                msg = 'Good start. More to push through.'
                mc  = (255, 200, 80)

            t = title_font.render('SESSION SUMMARY', True, (180, 200, 255))
            self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 40))

            cy = 160
            stats = [
                ('Tasks Completed', f'{completed} / {total}', (100, 220, 120)),
                ('Focus Time',      f'{focused} min',          (100, 180, 255)),
                ('Session Status',  'Active',                  (255, 200, 80)),
            ]
            for label, value, color in stats:
                ls = head_font.render(label, True, (160, 170, 190))
                vs = big_font.render(value, True, color)
                self.screen.blit(ls, (self.width // 2 - ls.get_width() // 2, cy))
                self.screen.blit(vs, (self.width // 2 - vs.get_width() // 2, cy + 52))
                cy += 160

            ms = body_font.render(msg, True, mc)
            self.screen.blit(ms, (self.width // 2 - ms.get_width() // 2, cy + 10))

            hint = hint_font.render('B: Back', True, (90, 110, 130))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 52))

    def handle_productivity_input(self, key):
        """Handle Productivity realm input"""
        import time as _t
        data = self.realm_data['productivity']
        selected = data['selected']
        active_module = data['active_module']

        if 'mod_data' not in data:
            data['mod_data'] = {}
        pd = data['mod_data']

        if active_module is not None:
            # ── Tasks ──
            if active_module == 0:
                tasks = pd.get('tasks', [
                    {'text': 'Review patent filing checklist',  'done': False},
                    {'text': 'Send VR&E follow-up email',       'done': False},
                    {'text': 'Test voice pipeline on Pi 4',     'done': True},
                    {'text': 'Update MotiBeamOS realm list',    'done': False},
                    {'text': 'Confirm MacroFab BOM review',     'done': False},
                    {'text': 'Draft Kickstarter outline',       'done': False},
                ])
                if 'tasks' not in pd:
                    pd['tasks'] = tasks
                sel = pd.get('task_sel', 0)
                if key == pygame.K_UP:
                    pd['task_sel'] = max(0, sel - 1)
                elif key == pygame.K_DOWN:
                    pd['task_sel'] = min(len(pd['tasks']) - 1, sel + 1)
                elif key == pygame.K_SPACE:
                    pd['tasks'][sel]['done'] = not pd['tasks'][sel]['done']
                elif key in (pygame.K_b, pygame.K_ESCAPE):
                    data['active_module'] = None

            # ── Focus Timer ──
            elif active_module == 1:
                if key == pygame.K_s:
                    running = pd.get('timer_running', False)
                    if running:
                        elapsed = _t.time() - pd.get('timer_ref', _t.time())
                        pd['timer_snapshot'] = max(0, pd.get('timer_snapshot', 25*60) - elapsed)
                        pd['timer_running'] = False
                    else:
                        pd['timer_ref'] = _t.time()
                        if 'timer_snapshot' not in pd:
                            pd['timer_snapshot'] = 25 * 60
                        pd['timer_running'] = True
                elif key == pygame.K_r:
                    mode = pd.get('timer_mode', 'focus')
                    pd['timer_snapshot'] = 25 * 60 if mode == 'focus' else 5 * 60
                    pd['timer_running'] = False
                    pd.pop('timer_ref', None)
                elif key == pygame.K_m:
                    mode = pd.get('timer_mode', 'focus')
                    pd['timer_mode'] = 'break' if mode == 'focus' else 'focus'
                    pd['timer_snapshot'] = 5 * 60 if pd['timer_mode'] == 'break' else 25 * 60
                    pd['timer_running'] = False
                    pd.pop('timer_ref', None)
                elif key == pygame.K_f:
                    pd['focus_screen'] = not pd.get('focus_screen', False)
                elif key in (pygame.K_b, pygame.K_ESCAPE):
                    pd['timer_running'] = False
                    pd['focus_screen'] = False
                    data['active_module'] = None

            # ── Quick Notes ──
            elif active_module == 2:
                notes = pd.get('notes', [])
                sel = pd.get('note_sel', 0)
                if key == pygame.K_UP:
                    pd['note_sel'] = max(0, sel - 1)
                elif key == pygame.K_DOWN:
                    pd['note_sel'] = min(max(0, len(notes) - 1), sel + 1)
                elif key in (pygame.K_b, pygame.K_ESCAPE):
                    data['active_module'] = None

            # ── Daily Plan / Reminders / Summary ──
            elif active_module in (3, 4, 5):
                if active_module == 4:
                    reminders = pd.get('reminders', [{}] * 5)
                    sel = pd.get('reminder_sel', 0)
                    if key == pygame.K_UP:
                        pd['reminder_sel'] = max(0, sel - 1)
                    elif key == pygame.K_DOWN:
                        pd['reminder_sel'] = min(len(reminders) - 1, sel + 1)
                if key in (pygame.K_b, pygame.K_ESCAPE):
                    data['active_module'] = None
            return

        # ── Grid navigation ──
        if key == pygame.K_LEFT:
            if selected % 3 > 0:
                data['selected'] -= 1
        elif key == pygame.K_RIGHT:
            if selected % 3 < 2 and selected < 5:
                data['selected'] += 1
        elif key == pygame.K_UP:
            if selected >= 3:
                data['selected'] -= 3
        elif key == pygame.K_DOWN:
            if selected < 3:
                data['selected'] += 3
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            data['active_module'] = selected


    def handle_presence_event(self, msg):
        """Handle incoming presence events from Pi 5"""
        msg_type = msg.get('type', '')
        sender = msg.get('from', 'Someone')
        print(f"[Presence] Event: {msg_type} from {sender}")

        if msg_type == 'PRESENCE_CALL':
            # Trigger incoming call overlay
            self.call_active = True
            # Find Dad in contacts
            for i, c in enumerate(self.contacts):
                if c['name'].lower() == sender.lower():
                    self.contact_index = i
                    self.call_caller = c
                    break
            else:
                self.call_caller = {'name': sender, 'relation': 'Family', 'emoji': '👤'}
            print(f"[Presence] Incoming call from {sender}")

        elif msg_type == 'PRESENCE_PING':
            import time as _t
            self.missed_presence = True
            self.corner_alert = {'text': f"{sender} thinking of you", 'color': (220, 180, 50)}
            self.corner_alert_time = _t.time()
            ping_msg = f"-> {sender} is thinking of you -> "
            if ping_msg not in self.ticker_text:
                self.ticker_text = ping_msg + self.ticker_text
            print(f"[Presence] PING from {sender}")

        elif msg_type == 'PRESENCE_NUDGE':
            import time as _t
            self.corner_alert = {'text': f"{sender} says hey", 'color': (80, 140, 220)}
            self.corner_alert_time = _t.time()
            nudge_msg = f"-> {sender} says hey -> "
            if nudge_msg not in self.ticker_text:
                self.ticker_text = nudge_msg + self.ticker_text
            print(f"[Presence] NUDGE from {sender}")

        elif msg_type == 'EDUCATION_QUESTION':
            import time as _t
            q = msg.get('question', {})
            self.realm_data['education']['live_question'] = q
            self.realm_data['education']['live_question_active'] = True
            self.realm_data['education']['live_answered'] = False
            self.realm_data['education']['live_correct'] = None
            self.corner_alert = {'text': "Dad sent a question!", 'color': (255, 180, 50)}
            self.corner_alert_time = _t.time()
            self.state = "circlebeam"
            self.enter_realm("education")
            print(f"[Education] Live question received from {sender}")

        elif msg_type == 'EDUCATION_RESULT':
            import time as _t
            result = msg.get('result', '')
            color = (100, 220, 100) if result == 'Correct' else (220, 100, 100)
            self.corner_alert = {'text': f"Dad says: {result}!", 'color': color}
            self.corner_alert_time = _t.time()
            result_msg = f"-> {result}! Keep going! -> "
            if result_msg not in self.ticker_text:
                self.ticker_text = result_msg + self.ticker_text
            print(f"[Education] Result from Dad: {result}")

    def handle_voice_command(self, cmd):
        """Route voice commands to realm actions"""
        print(f"[Voice] Executing: {cmd}")
        if cmd == "WAKE":
            # Visual feedback - flash header
            print("[Voice] Listening...")
        elif cmd == "CIRCLE":
            self.state = "circlebeam"
            self.selected_index = 2
            self.enter_realm("circlebeam")
        elif cmd == "HOME":
            self.state = "circlebeam"
            self.selected_index = 1
            self.enter_realm("home_realm")
        elif cmd == "EDUCATION":
            self.state = "circlebeam"
            self.selected_index = 2
        elif cmd == "HEALTH":
            self.state = "circlebeam"
            self.selected_index = 3
            self.enter_realm("health_wellness")
        elif cmd == "PRODUCTIVITY":
            self.state = "circlebeam"
            self.selected_index = 4
            self.enter_realm("productivity")
        elif cmd == "MARKETPLACE":
            self.state = "circlebeam"
            self.selected_index = 5
            self.enter_realm("marketplace")
        elif cmd == "CALL_DAD":
            if self.presence:
                self.presence.broadcast({"type":"PRESENCE_CALL","from":"Daughter","message":"Incoming call"})
        elif cmd == "NUDGE_DAD":
            if self.presence:
                self.presence.broadcast({"type":"PRESENCE_NUDGE","from":"Daughter","message":"Hey Dad"})
        elif cmd in ["BACK", "EXIT"]:
            self.go_back()

    def run(self):
        print("MotiBeam Spatial OS – clean launcher running (framebuffer-friendly)")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            # Process pending tones from voice pipeline (main thread only)
            if VOICE_ENABLED:
                try:
                    from voice_pipeline import get_pending_tone
                    import numpy as np
                    tone = get_pending_tone()
                    if tone and pygame.mixer.get_init():
                        if tone == 'wake':
                            for freq in [880, 1100]:
                                frames = int(44100 * 0.12)
                                t = np.linspace(0, 0.12, frames)
                                wave = (np.sin(2*np.pi*freq*t)*0.3*32767).astype(np.int16)
                                s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                                s.play()
                                pygame.time.wait(150)
                        elif tone == 'confirm':
                            frames = int(44100 * 0.2)
                            t = np.linspace(0, 0.2, frames)
                            wave = (np.sin(2*np.pi*1320*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                        elif tone == 'back':
                            frames = int(44100 * 0.15)
                            t = np.linspace(0, 0.15, frames)
                            wave = (np.sin(2*np.pi*440*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                except Exception as e:
                    pass

            # Process pending tones from voice pipeline (main thread only)
            if VOICE_ENABLED:
                try:
                    from voice_pipeline import get_pending_tone
                    import numpy as np
                    tone = get_pending_tone()
                    if tone and pygame.mixer.get_init():
                        if tone == 'wake':
                            for freq in [880, 1100]:
                                frames = int(44100 * 0.12)
                                t = np.linspace(0, 0.12, frames)
                                wave = (np.sin(2*np.pi*freq*t)*0.3*32767).astype(np.int16)
                                s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                                s.play()
                                pygame.time.wait(150)
                        elif tone == 'confirm':
                            frames = int(44100 * 0.2)
                            t = np.linspace(0, 0.2, frames)
                            wave = (np.sin(2*np.pi*1320*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                        elif tone == 'back':
                            frames = int(44100 * 0.15)
                            t = np.linspace(0, 0.15, frames)
                            wave = (np.sin(2*np.pi*440*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                except Exception as e:
                    pass

            # Process voice commands
            if self.voice:
                try:
                    while True:
                        cmd = self.voice_queue.get_nowait()
                        self.handle_voice_command(cmd)
                except queue.Empty:
                    pass

            # Process presence events
            if self.presence:
                try:
                    while True:
                        msg = self.presence_queue.get_nowait()
                        self.handle_presence_event(msg)
                except queue.Empty:
                    pass

            # Process pending tones from voice pipeline (main thread only)
            if VOICE_ENABLED:
                try:
                    from voice_pipeline import get_pending_tone
                    import numpy as np
                    tone = get_pending_tone()
                    if tone and pygame.mixer.get_init():
                        if tone == 'wake':
                            for freq in [880, 1100]:
                                frames = int(44100 * 0.12)
                                t = np.linspace(0, 0.12, frames)
                                wave = (np.sin(2*np.pi*freq*t)*0.3*32767).astype(np.int16)
                                s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                                s.play()
                                pygame.time.wait(150)
                        elif tone == 'confirm':
                            frames = int(44100 * 0.2)
                            t = np.linspace(0, 0.2, frames)
                            wave = (np.sin(2*np.pi*1320*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                        elif tone == 'back':
                            frames = int(44100 * 0.15)
                            t = np.linspace(0, 0.15, frames)
                            wave = (np.sin(2*np.pi*440*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                except Exception as e:
                    pass

            # Process pending tones from voice pipeline (main thread only)
            if VOICE_ENABLED:
                try:
                    from voice_pipeline import get_pending_tone
                    import numpy as np
                    tone = get_pending_tone()
                    if tone and pygame.mixer.get_init():
                        if tone == 'wake':
                            for freq in [880, 1100]:
                                frames = int(44100 * 0.12)
                                t = np.linspace(0, 0.12, frames)
                                wave = (np.sin(2*np.pi*freq*t)*0.3*32767).astype(np.int16)
                                s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                                s.play()
                                pygame.time.wait(150)
                        elif tone == 'confirm':
                            frames = int(44100 * 0.2)
                            t = np.linspace(0, 0.2, frames)
                            wave = (np.sin(2*np.pi*1320*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                        elif tone == 'back':
                            frames = int(44100 * 0.15)
                            t = np.linspace(0, 0.15, frames)
                            wave = (np.sin(2*np.pi*440*t)*0.3*32767).astype(np.int16)
                            s = pygame.sndarray.make_sound(np.column_stack([wave,wave]))
                            s.play()
                except Exception as e:
                    pass

            # Process voice commands
            if self.voice:
                try:
                    while True:
                        cmd = self.voice_queue.get_nowait()
                        self.handle_voice_command(cmd)
                except queue.Empty:
                    pass

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

            # CircleBeam live banner — all realms except CircleBeam itself
            if getattr(self, 'circlebeam_active', False) and getattr(self, 'circlebeam_target', None) and self.state != 'circlebeam':
                import math as _hcm, time as _hct
                _now = _hct.time()
                _hp  = (_hcm.sin(_now * 1.4) + 1) / 2
                _hp2 = (_hcm.sin(_now * 2.8) + 1) / 2
                _bw  = self.width - 60
                _bs  = pygame.Surface((_bw, 54), pygame.SRCALPHA)
                _bs.fill((8, 42, 24, int(195 + _hp * 45)))
                self.screen.blit(_bs, (30, 10))
                pygame.draw.rect(self.screen, (45, int(170+_hp*70), 80),
                                 pygame.Rect(30, 10, _bw, 54),
                                 2 if _hp < 0.5 else 3, border_radius=8)
                _dv  = int(120 + _hp2 * 135)
                _dot = get_font(34, bold=True).render('●', True, (50, _dv, 80))
                _dot_x = self.width//2 - 210
                self.screen.blit(_dot, (_dot_x, 20))
                _tv  = int(185 + _hp * 55)
                _bt2 = get_font(34, bold=True).render(
                    f' Live Circle Active — {self.circlebeam_target}',
                    True, (75, _tv, 115))
                self.screen.blit(_bt2, (_dot_x + _dot.get_width(), 20))
                _sess_start = getattr(self, '_cb_presence_start', _now)
                _elapsed    = int(_now - _sess_start)
                _mins, _secs = divmod(_elapsed, 60)
                _dur  = f'{_mins}m {_secs:02d}s' if _mins else f'{_secs}s'
                _ds   = get_font(26).render(_dur, True, (60, int(140+_hp*60), 90))
                self.screen.blit(_ds, (30 + _bw - _ds.get_width() - 14, 28))

            # Draw call overlay on top of everything if active
            if not hasattr(self, '_frame_count'):
                self._frame_count = 0
            self._frame_count += 1
            if self._frame_count % 10 == 0:
                print(f"[FRAME] {self._frame_count} state={self.state}", flush=True)
            self.draw_call_overlay()

            # Draw privacy mode banner if active
            if getattr(self, "privacy_mode", False):
                banner_font = get_font(50, bold=True)
                banner_text = "🔒 Privacy Mode"
                banner_surf = banner_font.render(banner_text, True, (255, 200, 100))
                banner_x = self.width - banner_surf.get_width() - 40
                banner_y = 20
                banner_bg = pygame.Rect(banner_x - 15, banner_y, banner_surf.get_width() + 30, 60)
                pygame.draw.rect(self.screen, (40, 35, 30), banner_bg, border_radius=8)
                pygame.draw.rect(self.screen, (255, 200, 100), banner_bg, width=2, border_radius=8)
                self.screen.blit(banner_surf, (banner_x, banner_y + 15))
            
            if hasattr(self, 'corner_alert') and self.corner_alert and hasattr(self, 'corner_alert_time'):
                import time as _t2
                if _t2.time() - self.corner_alert_time < 8:
                    a = self.corner_alert
                    s = pygame.Surface((300, 55), pygame.SRCALPHA)
                    r,g,b = a['color']
                    s.fill((r,g,b,200))
                    self.screen.blit(s, (self.width-310, 10))
                    af = get_font(30, bold=True)
                    at = af.render(a['text'], True, (255,255,255))
                    self.screen.blit(at, (self.width-305, 24))
                else:
                    self.corner_alert = None
            # Update ticker every 8 seconds
            import time as _tloop
            if not hasattr(self, '_ticker_last_update'):
                self._ticker_last_update = 0
            if _tloop.time() - self._ticker_last_update > 8:
                try:
                    self.ticker_text = self._build_ticker()
                except Exception:
                    pass
                self._ticker_last_update = _tloop.time()

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    app = MotiBeamOS(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    app.run()
