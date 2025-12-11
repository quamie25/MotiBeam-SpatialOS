"""
Clinical Realm v3 - Mind · Body · Spirit · Trends

Controls (inside realm):
    LEFT / RIGHT   - Switch screens
    UP / DOWN      - Also switch screens (pillar-style)
    1 / 2 / 3      - Quick jump: Mind / Body / Spirit
    SPACE          - Trigger ECG-style alert overlay
    ESC            - Return to launcher
"""

import pygame
import math
from datetime import datetime


class ClinicalRealm:
    def __init__(self, screen, clock, global_state=None, standalone=False):
        self.screen = screen
        self.clock = clock
        self.global_state = global_state or {}
        self.standalone = standalone

        self.running = False
        self.current_view = 0  # 0: Mind, 1: Body, 2: Spirit, 3: Trends

        # ECG Alert state
        self.ecg_alert_active = False
        self.ecg_alert_start = 0
        self.ecg_alert_duration = 2500  # ms

        # Cached size
        self.width, self.height = self.screen.get_size()

        # Data for demo
        self.mind_score = 82
        self.body_score = 76
        self.spirit_score = 89

        self.sleep_hours = 7.2
        self.hr_rest = 63
        self.hrv_score = 71

        self.meditation_streak = 9  # days
        self.gratitude_entries = 4

        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("DejaVu Sans", 50, bold=True)
        self.font_subtitle = pygame.font.SysFont("DejaVu Sans", 26)
        self.font_body = pygame.font.SysFont("DejaVu Sans", 24)
        self.font_small = pygame.font.SysFont("DejaVu Sans", 20)
        self.font_huge = pygame.font.SysFont("DejaVu Sans", 80, bold=True)

    # --------- Helpers ---------

    def _get_theme_colors(self):
        """Use launcher theme if available, otherwise default."""
        theme = (self.global_state or {}).get("theme", "NEON")

        if theme == "NEON":
            return {
                "bg": (6, 10, 18),
                "mind": (160, 120, 255),
                "body": (0, 220, 190),
                "spirit": (255, 210, 110),
                "grid": (40, 60, 90),
                "text_main": (230, 240, 255),
                "text_dim": (150, 170, 200),
                "alert": (255, 80, 110),
            }
        elif theme == "MINIMAL":
            return {
                "bg": (240, 242, 245),
                "mind": (120, 90, 200),
                "body": (0, 160, 140),
                "spirit": (210, 170, 90),
                "grid": (190, 200, 210),
                "text_main": (40, 50, 60),
                "text_dim": (110, 120, 130),
                "alert": (200, 60, 80),
            }
        else:  # NIGHT
            return {
                "bg": (3, 3, 8),
                "mind": (180, 140, 255),
                "body": (0, 190, 170),
                "spirit": (255, 210, 130),
                "grid": (45, 50, 75),
                "text_main": (220, 225, 255),
                "text_dim": (140, 150, 180),
                "alert": (255, 90, 120),
            }

    def _get_mode_dim(self):
        mode = (self.global_state or {}).get("mode", "NORMAL")
        if mode == "STUDY":
            return 0.85
        elif mode == "SLEEP":
            return 0.55
        return 1.0

    def _draw_header(self, colors):
        """Top bar: title + date + current view name."""
        dim = self._get_mode_dim()
        text_main = tuple(int(c * dim) for c in colors["text_main"])
        text_dim = tuple(int(c * dim) for c in colors["text_dim"])

        # Pillar titles
        view_names = ["Mind", "Body", "Spirit", "Trends"]
        view_emojis = ["🧠", "💪", "✨", "📈"]
        view_colors = [colors["mind"], colors["body"], colors["spirit"], colors["grid"]]

        title = f"{view_emojis[self.current_view]} Clinical · {view_names[self.current_view]}"
        title_surf = self.font_title.render(title, True, text_main)
        title_rect = title_surf.get_rect(midleft=(60, 60))
        self.screen.blit(title_surf, title_rect)

        # Date/time right side
        now = datetime.now()
        dt_str = now.strftime("%a • %b %d · %I:%M %p").lstrip("0")
        dt_surf = self.font_subtitle.render(dt_str, True, text_dim)
        dt_rect = dt_surf.get_rect(topright=(self.width - 60, 40))
        self.screen.blit(dt_surf, dt_rect)

        # Pillar chips under title
        chip_y = 110
        chip_x = 60
        spacing = 150

        for i, name in enumerate(["Mind", "Body", "Spirit"]):
            active = (i == self.current_view)
            col = view_colors[i]
            bg_alpha = 50 if active else 20
            border = 2 if active else 1

            chip_w, chip_h = 120, 34
            chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
            pygame.draw.rect(
                chip_surf,
                (*col, bg_alpha),
                (0, 0, chip_w, chip_h),
                border_radius=14,
            )
            pygame.draw.rect(
                chip_surf, col, (0, 0, chip_w, chip_h), border, border_radius=14
            )
            self.screen.blit(chip_surf, (chip_x + i * spacing, chip_y))

            label_surf = self.font_small.render(name, True, text_main if active else text_dim)
            label_rect = label_surf.get_rect(center=(chip_x + i * spacing + chip_w // 2,
                                                     chip_y + chip_h // 2))
            self.screen.blit(label_surf, label_rect)

    def _draw_footer(self, colors):
        dim = self._get_mode_dim()
        text_dim = tuple(int(c * dim) for c in colors["text_dim"])

        footer_text = "← / → / ↑ / ↓: Switch pillar · 1/2/3: Quick jump · SPACE: ECG Alert · ESC: Back"
        surf = self.font_small.render(footer_text, True, text_dim)
        rect = surf.get_rect(midbottom=(self.width // 2, self.height - 30))
        self.screen.blit(surf, rect)

    def _draw_radial_score(self, center, radius, score, color, label, colors):
        """Big circular gauge for 0–100 scores."""
        cx, cy = center
        dim = self._get_mode_dim()
        base = tuple(int(c * dim) for c in color)
        text_main = tuple(int(c * dim) for c in colors["text_main"])
        text_dim = tuple(int(c * dim) for c in colors["text_dim"])

        # Background circle
        pygame.draw.circle(self.screen, colors["grid"], center, radius, width=4)

        # Arc for score
        start_angle = math.radians(140)
        end_angle = math.radians(40)
        span = start_angle - end_angle
        frac = max(0.0, min(1.0, score / 100.0))
        angle = start_angle - span * frac

        # Draw arc in segments
        steps = 80
        for i in range(int(steps * frac)):
            t0 = i / steps
            t1 = (i + 1) / steps
            a0 = start_angle - span * t0
            a1 = start_angle - span * t1
            x0 = cx + radius * math.cos(a0)
            y0 = cy + radius * math.sin(a0)
            x1 = cx + radius * math.cos(a1)
            y1 = cy + radius * math.sin(a1)
            pygame.draw.line(self.screen, base, (x0, y0), (x1, y1), 6)

        # Score text
        score_str = f"{int(score)}"
        score_surf = self.font_huge.render(score_str, True, text_main)
        score_rect = score_surf.get_rect(center=(cx, cy - 10))
        self.screen.blit(score_surf, score_rect)

        label_surf = self.font_subtitle.render(label, True, text_dim)
        label_rect = label_surf.get_rect(center=(cx, cy + radius + 30))
        self.screen.blit(label_surf, label_rect)

    def _draw_cards_column(self, x, y, w, h, rows, colors):
        dim = self._get_mode_dim()
        text_main = tuple(int(c * dim) for c in colors["text_main"])
        text_dim = tuple(int(c * dim) for c in colors["text_dim"])

        row_h = h // len(rows)
        for i, (title, value, note) in enumerate(rows):
            top = y + i * row_h + 10
            card_h = row_h - 20

            # Card background
            card_surf = pygame.Surface((w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(
                card_surf,
                (*colors["grid"], 90),
                (0, 0, w, card_h),
                border_radius=12,
            )
            self.screen.blit(card_surf, (x, top))

            title_surf = self.font_small.render(title, True, text_dim)
            title_rect = title_surf.get_rect(topleft=(x + 18, top + 8))
            self.screen.blit(title_surf, title_rect)

            value_surf = self.font_body.render(value, True, text_main)
            value_rect = value_surf.get_rect(topleft=(x + 18, top + 32))
            self.screen.blit(value_surf, value_rect)

            if note:
                note_surf = self.font_small.render(note, True, text_dim)
                note_rect = note_surf.get_rect(topright=(x + w - 18, top + 32))
                self.screen.blit(note_surf, note_rect)

    def _draw_trend_graph(self, rect, colors):
        """Simple line-like trend bands to hint at 7-day insight."""
        dim = self._get_mode_dim()
        text_main = tuple(int(c * dim) for c in colors["text_main"])
        grid = colors["grid"]

        x, y, w, h = rect

        # Background
        bg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (*grid, 90), (0, 0, w, h), border_radius=16)
        self.screen.blit(bg_surf, (x, y))

        # Title
        title_surf = self.font_subtitle.render("7-Day Stability Map", True, text_main)
        title_rect = title_surf.get_rect(topleft=(x + 20, y + 16))
        self.screen.blit(title_surf, title_rect)

        # Axes
        gx0, gy0 = x + 40, y + 70
        gx1, gy1 = x + w - 30, y + h - 40
        # Vertical grid lines (days)
        for i in range(8):
            t = i / 7
            xx = gx0 + (gx1 - gx0) * t
            pygame.draw.line(self.screen, grid, (xx, gy0), (xx, gy1), 1)

        # Horizontal bands (Mind/Body/Spirit)
        band_height = (gy1 - gy0) / 3
        colors_bands = [colors["mind"], colors["body"], colors["spirit"]]
        labels = ["Mind", "Body", "Spirit"]

        for i in range(3):
            top = gy0 + i * band_height
            c = colors_bands[i]
            alpha = int(90 * dim)
            band_surf = pygame.Surface((gx1 - gx0, int(band_height) - 6), pygame.SRCALPHA)
            pygame.draw.rect(
                band_surf,
                (*c, alpha),
                (0, 0, gx1 - gx0, int(band_height) - 6),
                border_radius=10,
            )
            self.screen.blit(band_surf, (gx0, top + 3))

            label_surf = self.font_small.render(labels[i], True, text_main)
            label_rect = label_surf.get_rect(topleft=(gx0 + 10, top + 8))
            self.screen.blit(label_surf, label_rect)

    # --------- View Renderers ---------

    def _render_mind(self, colors):
        center = (self.width // 3, self.height // 2 + 20)
        self._draw_radial_score(center, 130, self.mind_score, colors["mind"],
                                "Cognitive Load · Focus", colors)

        right_x = self.width * 2 // 3
        top_y = 180
        col_w = self.width // 3 + 80
        col_h = self.height - top_y - 120

        rows = [
            ("Focus Window", "25–40 min", "Optimal deep work"),
            ("Context Switching", "Low", "Notifications softened"),
            ("Overwhelm Index", "2 / 10", "Green zone"),
            ("Session Recommendation", "Next: 18 min focus", "Auto-scheduled"),
        ]
        self._draw_cards_column(right_x - col_w // 2, top_y, col_w, col_h, rows, colors)

    def _render_body(self, colors):
        center = (self.width // 3, self.height // 2 + 20)
        combined_score = int((self.body_score + self.hrv_score) / 2)
        self._draw_radial_score(center, 130, combined_score, colors["body"],
                                "Recovery · Vital Capacity", colors)

        right_x = self.width * 2 // 3
        top_y = 180
        col_w = self.width // 3 + 80
        col_h = self.height - top_y - 120

        rows = [
            ("Sleep (last night)", f"{self.sleep_hours:.1f} hrs", "Target: 7.5 hrs"),
            ("Resting Heart Rate", f"{self.hr_rest} bpm", "Calm baseline"),
            ("HRV", f"{self.hrv_score}/100", "Stable, trending up"),
            ("Today’s Recommendation", "20 min walk · 2L water", "Auto-synced"),
        ]
        self._draw_cards_column(right_x - col_w // 2, top_y, col_w, col_h, rows, colors)

    def _render_spirit(self, colors):
        center = (self.width // 3, self.height // 2 + 20)
        self._draw_radial_score(center, 130, self.spirit_score, colors["spirit"],
                                "Calm · Purpose · Alignment", colors)

        right_x = self.width * 2 // 3
        top_y = 180
        col_w = self.width // 3 + 80
        col_h = self.height - top_y - 120

        rows = [
            ("Meditation Streak", f"{self.meditation_streak} days", "Micro-sessions: 3–5 min"),
            ("Gratitude Log", f"{self.gratitude_entries} entries", "Today"),
            ("Social Check-In", "2 close contacts", "Last 48 hrs"),
            ("Today’s Recommendation", "Evening wind-down beam", "Guided by MotiBeam"),
        ]
        self._draw_cards_column(right_x - col_w // 2, top_y, col_w, col_h, rows, colors)

    def _render_trends(self, colors):
        rect = (
            int(self.width * 0.10),
            170,
            int(self.width * 0.80),
            self.height - 260,
        )
        self._draw_trend_graph(rect, colors)

        dim = self._get_mode_dim()
        text_main = tuple(int(c * dim) for c in colors["text_main"])
        text_dim = tuple(int(c * dim) for c in colors["text_dim"])

        # Caption line
        caption = "OEM View: 7-day stability bands · Perfect for dashboards, clinics, and smart home hubs."
        cap_surf = self.font_body.render(caption, True, text_dim)
        cap_rect = cap_surf.get_rect(midtop=(self.width // 2, rect[1] + rect[3] + 14))
        self.screen.blit(cap_surf, cap_rect)

        # Highlight bullet
        line2 = "• Single projection, three pillars · Mind, Body, Spirit · All ambient, zero clutter."
        l2_surf = self.font_small.render(line2, True, text_main)
        l2_rect = l2_surf.get_rect(midtop=(self.width // 2, cap_rect.bottom + 6))
        self.screen.blit(l2_surf, l2_rect)

    # --------- ECG Alert ---------

    def _draw_ecg_alert(self, colors):
        """Overlay for SPACE-triggered ECG alert."""
        if not self.ecg_alert_active:
            return

        elapsed = pygame.time.get_ticks() - self.ecg_alert_start
        if elapsed > self.ecg_alert_duration:
            self.ecg_alert_active = False
            return

        alpha = 200
        # Fade out near the end
        if elapsed > self.ecg_alert_duration * 0.7:
            frac = 1 - (elapsed - self.ecg_alert_duration * 0.7) / (self.ecg_alert_duration * 0.3)
            alpha = max(0, int(alpha * frac))

        overlay = pygame.Surface((self.width, 140), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay,
            (*colors["alert"], alpha),
            (0, 0, self.width, 140),
        )
        self.screen.blit(overlay, (0, self.height // 2 - 70))

        text = "ECG Pattern Spike Detected · Auto-adjusting beam · Press ESC to acknowledge"
        dim = self._get_mode_dim()
        text_main = tuple(int(c * dim) for c in colors["bg"])  # dark text on bright bar

        text_surf = self.font_body.render(text, True, text_main)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surf, text_rect)

        # Simple ECG line
        ecg_y = self.height // 2 + 30
        ecg_color = text_main
        start_x = int(self.width * 0.15)
        end_x = int(self.width * 0.85)
        pygame.draw.line(self.screen, ecg_color, (start_x, ecg_y), (end_x, ecg_y), 2)

        # Spike shape
        mid = (start_x + end_x) // 2
        pygame.draw.line(self.screen, ecg_color, (mid - 40, ecg_y), (mid - 20, ecg_y - 25), 2)
        pygame.draw.line(self.screen, ecg_color, (mid - 20, ecg_y - 25), (mid, ecg_y + 10), 2)
        pygame.draw.line(self.screen, ecg_color, (mid, ecg_y + 10), (mid + 40, ecg_y), 2)

    # --------- Main Loop ---------

    def run(self, duration=60):
        """Main Clinical realm loop."""
        # Intro banner (like other realms)
        print("  ⚕️  Initializing Clinical Realm Systems...")
        print("  📡 Spatial scan initiated for clinical...")
        print("  ✓ Clinical space mapped: 23m x 31m x 5m")
        print("  🌐 Establishing BeamNet mesh for Clinical Network...")
        print("  ✓ Mesh established - Strength: 82.4%")
        print("  ✓ Clinical Mind-Body-Spirit systems online")

        self.running = True
        start_time = pygame.time.get_ticks()

        while self.running:
            dt = self.clock.tick(30) / 1000.0

            # Optional timeout
            if duration is not None:
                if (pygame.time.get_ticks() - start_time) > duration * 1000:
                    break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                        self.current_view = (self.current_view + 1) % 4

                    elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                        self.current_view = (self.current_view - 1) % 4

                    elif event.key == pygame.K_1:
                        self.current_view = 0  # Mind
                    elif event.key == pygame.K_2:
                        self.current_view = 1  # Body
                    elif event.key == pygame.K_3:
                        self.current_view = 2  # Spirit

                    elif event.key == pygame.K_SPACE:
                        # Trigger ECG alert
                        self.ecg_alert_active = True
                        self.ecg_alert_start = pygame.time.get_ticks()

            # Draw
            colors = self._get_theme_colors()
            dim = self._get_mode_dim()
            bg = tuple(int(c * dim) for c in colors["bg"])
            self.screen.fill(bg)

            self._draw_header(colors)

            # Choose view
            if self.current_view == 0:
                self._render_mind(colors)
            elif self.current_view == 1:
                self._render_body(colors)
            elif self.current_view == 2:
                self._render_spirit(colors)
            else:
                self._render_trends(colors)

            self._draw_footer(colors)
            self._draw_ecg_alert(colors)

            pygame.display.flip()

        # Exit back to launcher
        return
