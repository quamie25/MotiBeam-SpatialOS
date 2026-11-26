"""
Notification Beam — wall-card render hook (reference implementation).

This is the piece that gets grafted into spatial_os.py during the joint
install session, once the on-device file is in front of us (device code is
ahead of this repo, so exact line placement happens there, with a timestamped
backup first — same guarded-patch procedure as the mDNS change).

Integration is deliberately tiny: TWO calls.

    # once, near other module init:
    from modules.notification_beam.render_hook_example import NotificationCards
    notification_cards = NotificationCards()

    # once per frame, late in the draw order (after realm content, before flip):
    notification_cards.draw(screen)

No other changes to spatial_os. The daemon and the renderer only share the
spool file, so either side can be restarted independently and neither can
crash the other.
"""

import json
import os
import time

import pygame

SPOOL_FILE = "/tmp/motibeam_notifications/queue.json"
POLL_SECONDS = 0.5          # how often we re-read the spool
CARD_MARGIN = 28            # px from screen edge
CARD_WIDTH = 460
CARD_PAD = 18

# House palette
NAVY = (13, 27, 46)
GOLD = (154, 123, 47)
WHITE = (240, 240, 240)
GREY = (176, 183, 195)


class NotificationCards:
    def __init__(self):
        self._last_poll = 0.0
        self._seen_ts = 0.0       # newest spool entry we have displayed
        self._active = None       # entry currently on the wall
        self._active_until = 0.0
        self._font_app = None
        self._font_title = None
        self._font_body = None

    def _fonts(self):
        if self._font_app is None:
            self._font_app = pygame.font.SysFont("dejavusans", 20, bold=True)
            self._font_title = pygame.font.SysFont("dejavusans", 26, bold=True)
            self._font_body = pygame.font.SysFont("dejavusans", 22)
        return self._font_app, self._font_title, self._font_body

    def _poll(self):
        now = time.time()
        if now - self._last_poll < POLL_SECONDS:
            return
        self._last_poll = now
        try:
            if not os.path.exists(SPOOL_FILE):
                return
            with open(SPOOL_FILE) as f:
                queue = json.load(f)
            if not queue:
                return
            newest = queue[-1]
            if float(newest.get("ts", 0)) > self._seen_ts:
                self._seen_ts = float(newest.get("ts", 0))
                self._active = newest
                self._active_until = now + int(newest.get("card_seconds", 12))
        except Exception:
            # Never let a malformed spool touch the render loop.
            return

    @staticmethod
    def _wrap(text, font, max_w):
        words, lines, cur = (text or "").split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font.size(trial)[0] <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines[:3]  # a wall card is a glance, not a page

    def draw(self, screen):
        """Call once per frame. No-op when there is nothing to show."""
        self._poll()
        if not self._active or time.time() > self._active_until:
            self._active = None
            return

        font_app, font_title, font_body = self._fonts()
        entry = self._active
        inner_w = CARD_WIDTH - 2 * CARD_PAD

        app_s = font_app.render(entry.get("app", "Phone").upper(), True, GOLD)
        title_lines = self._wrap(entry.get("title", ""), font_title, inner_w)
        body_lines = self._wrap(entry.get("body", ""), font_body, inner_w)

        h = CARD_PAD + app_s.get_height() + 8
        h += sum(font_title.size(t)[1] + 2 for t in title_lines)
        if body_lines:
            h += 6 + sum(font_body.size(b)[1] + 2 for b in body_lines)
        h += CARD_PAD

        sw = screen.get_width()
        x = sw - CARD_WIDTH - CARD_MARGIN
        y = CARD_MARGIN

        card = pygame.Surface((CARD_WIDTH, h), pygame.SRCALPHA)
        pygame.draw.rect(card, (*NAVY, 235), card.get_rect(), border_radius=16)
        pygame.draw.rect(card, (*GOLD, 255), card.get_rect(), width=2, border_radius=16)

        cy = CARD_PAD
        card.blit(app_s, (CARD_PAD, cy))
        cy += app_s.get_height() + 8
        for t in title_lines:
            s = font_title.render(t, True, WHITE)
            card.blit(s, (CARD_PAD, cy))
            cy += s.get_height() + 2
        if body_lines:
            cy += 6
            for b in body_lines:
                s = font_body.render(b, True, GREY)
                card.blit(s, (CARD_PAD, cy))
                cy += s.get_height() + 2

        screen.blit(card, (x, y))
