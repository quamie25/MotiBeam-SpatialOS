"""
MotiBeam Spatial OS - Notification Ticker
Footer with scrolling notifications and keyboard shortcuts.
"""

import pygame
import time
from core.design_tokens import *

class NotificationTicker:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.messages = []
        self.current_message_index = 0
        self.scroll_x = 0
        self.last_message_change = time.time()

    def add_message(self, message):
        """Add a message to the ticker."""
        if message not in self.messages:
            self.messages.append(message)

    def clear_messages(self):
        """Clear all ticker messages."""
        self.messages = []
        self.current_message_index = 0
        self.scroll_x = 0

    def update(self):
        """Update ticker animation."""
        current_time = time.time()

        # Cycle messages every TICKER_MESSAGE_DURATION seconds
        if len(self.messages) > 0:
            if current_time - self.last_message_change > TICKER_MESSAGE_DURATION:
                self.current_message_index = (self.current_message_index + 1) % len(self.messages)
                self.scroll_x = self.screen_width
                self.last_message_change = current_time
            else:
                # Smooth scroll
                self.scroll_x -= TICKER_SCROLL_SPEED

    def draw(self, surface):
        """Draw the footer ticker and shortcuts."""
        footer_y = self.screen_height - TICKER_HEIGHT

        # Background
        footer_rect = pygame.Rect(0, footer_y, self.screen_width, TICKER_HEIGHT)
        pygame.draw.rect(surface, BG_FOOTER, footer_rect)

        # Ticker messages (scrolling)
        if len(self.messages) > 0:
            font_ticker = pygame.font.Font(None, FONT_TICKER_SIZE)
            current_message = self.messages[self.current_message_index]

            # Add bullet point
            message_text = f"• {current_message}"
            ticker_surface = font_ticker.render(message_text, True, TEXT_PRIMARY)

            # Scroll from right to left
            surface.blit(ticker_surface, (int(self.scroll_x), footer_y + 10))

            # Reset scroll when message goes off screen
            if self.scroll_x + ticker_surface.get_width() < 0:
                self.scroll_x = self.screen_width

        # Keyboard shortcuts (bottom line, centered)
        font_hints = pygame.font.Font(None, FONT_FOOTER_HINT_SIZE)
        shortcuts_text = "Arrow Keys: Navigate  •  Enter: Select  •  1-9: Realm Quick-Select  •  A: Alert  •  M: Medical  •  C: Calm  •  Q: Quit"
        hints_surface = font_hints.render(shortcuts_text, True, TEXT_MUTED)

        # Center horizontally
        hints_x = (self.screen_width - hints_surface.get_width()) // 2
        surface.blit(hints_surface, (hints_x, footer_y + TICKER_HEIGHT - 28))
