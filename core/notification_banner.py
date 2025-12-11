"""
MotiBeam Spatial OS - Notification Banner
Header with system status and alert banners.
"""

import pygame
from datetime import datetime
from core.design_tokens import *

class NotificationBanner:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.current_state = "CALM"
        self.alerts = []  # List of active alerts

    def add_alert(self, alert_type, title, description):
        """Add a new alert to the banner."""
        self.alerts.append({
            "type": alert_type,  # "severe", "medical", "info"
            "title": title,
            "description": description
        })

    def clear_alerts(self):
        """Clear all active alerts."""
        self.alerts = []

    def set_state(self, state):
        """Set system state: CALM, ALERT, or CRITICAL"""
        self.current_state = state

    def draw(self, surface):
        """Draw the header and any active alerts."""
        y_offset = 0

        # Draw active alerts first (at the very top)
        for alert in self.alerts:
            y_offset += self._draw_alert(surface, alert, y_offset)

        # Draw main header
        self._draw_header(surface, y_offset)

        return y_offset + HEADER_HEIGHT

    def _draw_alert(self, surface, alert, y_offset):
        """Draw a single alert banner."""
        alert_height = 70

        # Determine alert color
        if alert["type"] == "severe":
            bg_color = ALERT_RED
        elif alert["type"] == "medical":
            bg_color = ALERT_AMBER
        else:
            bg_color = (59, 130, 246)  # Blue for info

        # Draw alert background (solid, no transparency)
        alert_rect = pygame.Rect(0, y_offset, self.screen_width, alert_height)
        pygame.draw.rect(surface, bg_color, alert_rect)

        # Alert icon
        try:
            icon_font = pygame.font.Font(None, FONT_ALERT_TITLE_SIZE + 4)
            icon_text = "⚠" if alert["type"] == "severe" else "🏥" if alert["type"] == "medical" else "ℹ️"
            icon_surface = icon_font.render(icon_text, True, ALERT_TEXT)
            surface.blit(icon_surface, (PADDING, y_offset + 10))
        except:
            pass

        # Title
        font_title = pygame.font.Font(None, FONT_ALERT_TITLE_SIZE)
        title_surface = font_title.render(alert["title"], True, ALERT_TEXT)
        surface.blit(title_surface, (PADDING + 40, y_offset + 10))

        # Description
        font_body = pygame.font.Font(None, FONT_ALERT_BODY_SIZE)
        desc_surface = font_body.render(alert["description"], True, ALERT_TEXT)
        surface.blit(desc_surface, (PADDING + 40, y_offset + 38))

        return alert_height

    def _draw_header(self, surface, y_offset):
        """Draw the main header bar."""
        # Background
        header_rect = pygame.Rect(0, y_offset, self.screen_width, HEADER_HEIGHT)
        pygame.draw.rect(surface, BG_HEADER, header_rect)

        # Left: System title
        font_header = pygame.font.Font(None, FONT_HEADER_SIZE)
        title_surface = font_header.render("MOTIBEAM SPATIAL OS", True, TEXT_PRIMARY)
        surface.blit(title_surface, (PADDING, y_offset + 15))

        # Right: Time, date, temp, state
        font_meta = pygame.font.Font(None, FONT_HEADER_META_SIZE)

        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip('0')
        date_str = now.strftime("%a, %b %d")
        temp_str = "72°F"  # Mock temperature

        # State color
        if self.current_state == "CALM":
            state_color = STATE_CALM
        elif self.current_state == "ALERT":
            state_color = STATE_ALERT
        else:
            state_color = STATE_CRITICAL

        meta_text = f"{time_str} • {date_str} • {temp_str} • STATE: "
        meta_surface = font_meta.render(meta_text, True, TEXT_SECONDARY)

        state_surface = font_meta.render(self.current_state, True, state_color)

        # Right align
        meta_width = meta_surface.get_width() + state_surface.get_width()
        meta_x = self.screen_width - meta_width - PADDING

        surface.blit(meta_surface, (meta_x, y_offset + 18))
        surface.blit(state_surface, (meta_x + meta_surface.get_width(), y_offset + 18))

        # Subtitle
        font_subtitle = pygame.font.Font(None, FONT_HEADER_META_SIZE - 4)
        subtitle_surface = font_subtitle.render("Projection Operating System v1.0", True, TEXT_MUTED)
        surface.blit(subtitle_surface, (PADDING, y_offset + 48))
