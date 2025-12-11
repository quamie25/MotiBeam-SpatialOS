"""
MotiBeam Spatial OS - Design Tokens
Font sizes and colors optimized for 6-10 ft projection viewing distance.
"""

# ============================================================================
# FONT SIZES - Optimized for projection viewing from 6-10 ft
# ============================================================================

# Header / banner
FONT_HEADER_SIZE = 28          # "MOTIBEAM SPATIAL OS"
FONT_HEADER_META_SIZE = 22     # time / temp / state
FONT_ALERT_TITLE_SIZE = 26     # "SEVERE WEATHER WARNING"
FONT_ALERT_BODY_SIZE = 20      # alert description text

# Realm cards
FONT_EMOJI_SIZE = 48           # emoji icon (large and clear)
FONT_REALM_TITLE_SIZE = 36     # e.g. "CircleBeam"
FONT_REALM_SUBTITLE_SIZE = 20  # e.g. "Living relationships"

# Footer / ticker
FONT_TICKER_SIZE = 20          # scrolling ticker text
FONT_FOOTER_HINT_SIZE = 18     # keyboard shortcuts line

# ============================================================================
# COLORS - Enterprise clean, high contrast
# ============================================================================

# Background
BG_COLOR = (30, 30, 35)        # Dark charcoal
BG_HEADER = (20, 20, 25)       # Slightly darker for header
BG_FOOTER = (20, 20, 25)       # Same as header

# Text
TEXT_PRIMARY = (255, 255, 255)  # White - high contrast
TEXT_SECONDARY = (180, 180, 190) # Light gray for subtitles
TEXT_MUTED = (140, 140, 150)    # Muted for hints

# Alert colors
ALERT_RED = (220, 38, 38)       # Severe weather
ALERT_AMBER = (245, 158, 11)    # Medical/warning
ALERT_TEXT = (255, 255, 255)    # Always white on alerts

# State indicator colors
STATE_CALM = (34, 197, 94)      # Green
STATE_ALERT = (245, 158, 11)    # Amber
STATE_CRITICAL = (220, 38, 38)  # Red

# Realm card border colors (from screenshot)
REALM_COLORS = {
    "circlebeam": (59, 130, 246),    # Blue
    "legacybeam": (34, 197, 94),     # Green
    "lockboxbeam": (147, 51, 234),   # Purple
    "marketplace": (234, 179, 8),    # Yellow
    "home": (34, 197, 94),           # Green
    "clinical": (239, 68, 68),       # Red
    "education": (59, 130, 246),     # Blue
    "emergency": (220, 38, 38),      # Bright red
    "transport": (59, 130, 246),     # Blue
    "security": (147, 51, 234),      # Purple
    "aviation": (59, 130, 246),      # Blue
    "maritime": (59, 130, 246),      # Blue
}

# Selection highlight
SELECTION_COLOR = (250, 204, 21)   # Bright yellow - highly visible
SELECTION_WIDTH = 4                # Thick border for visibility

# ============================================================================
# SPACING & LAYOUT
# ============================================================================

PADDING = 20
CARD_PADDING = 16
CARD_RADIUS = 8
CARD_SPACING = 16

# Header
HEADER_HEIGHT = 80

# Footer ticker
TICKER_HEIGHT = 70
TICKER_SCROLL_SPEED = 1.5          # Slow, comfortable scroll
TICKER_MESSAGE_DURATION = 15.0     # 15 seconds per message

# Grid layout
GRID_COLS = 4
GRID_ROWS = 3
