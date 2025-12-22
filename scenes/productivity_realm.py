"""
MotiBeam Spatial OS - Productivity Realm
Projection-optimized ambient workflow layer (licensing-first demo)
"""

import pygame
import time
from datetime import datetime


class ProductivityRealm:
    """Productivity realm with huge fonts for 10-15 feet projection readability"""

    # Productivity modules (2x3 grid)
    MODULES = [
        {
            "id": "focus_sprint",
            "name": "Focus Sprint",
            "sublabel": "Pomodoro pacing",
            "icon": "⏱️",
            "status": "READY"
        },
        {
            "id": "task_board",
            "name": "Task Board",
            "sublabel": "Top 3 priorities",
            "icon": "✓",
            "status": "READY"
        },
        {
            "id": "meeting_mode",
            "name": "Meeting Mode",
            "sublabel": "Agenda + presence",
            "icon": "👥",
            "status": "READY"
        },
        {
            "id": "daily_brief",
            "name": "Daily Brief",
            "sublabel": "Schedule + signals",
            "icon": "📅",
            "status": "READY"
        },
        {
            "id": "ops_dashboard",
            "name": "Ops Dashboard",
            "sublabel": "Operational awareness",
            "icon": "📊",
            "status": "READY"
        },
        {
            "id": "deep_work_audio",
            "name": "Deep Work Audio",
            "sublabel": "Focus soundscapes",
            "icon": "🎧",
            "status": "READY"
        }
    ]

    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Calculate scale factor for responsive sizing
        self.scale = min(self.width / 1280, self.height / 720)

        # Projection-readable font sizes (scaled)
        self.font_title = pygame.font.Font(None, int(88 * self.scale))          # 80-96px
        self.font_subtitle = pygame.font.Font(None, int(40 * self.scale))       # 36-44px
        self.font_tile_name = pygame.font.Font(None, int(50 * self.scale))      # 44-56px
        self.font_tile_sublabel = pygame.font.Font(None, int(38 * self.scale))  # 36-44px
        self.font_tile_icon = pygame.font.Font(None, int(72 * self.scale))      # Big icons
        self.font_panel_headline = pygame.font.Font(None, int(64 * self.scale)) # 56-72px
        self.font_panel_bullet = pygame.font.Font(None, int(40 * self.scale))   # 36-44px
        self.font_controls = pygame.font.Font(None, int(33 * self.scale))       # 30-36px
        self.font_status_pill = pygame.font.Font(None, int(32 * self.scale))    # Status pills
        self.font_demo_timer = pygame.font.Font(None, int(180 * self.scale))    # HUGE timer

        # Colors (high contrast)
        self.bg_color = (12, 15, 25)
        self.card_bg = (28, 32, 48)
        self.card_border = (80, 90, 140)
        self.selected_border = (255, 200, 80)
        self.glow_color = (255, 200, 80, 100)
        self.text_primary = (245, 248, 255)
        self.text_secondary = (170, 175, 190)
        self.pill_bg = (60, 200, 100)
        self.pill_text = (255, 255, 255)

        # State
        self.selected_module = 0
        self.show_preview_panel = False
        self.demo_mode = False
        self.demo_timer = 25 * 60  # 25 minutes in seconds (for real demo, use 30 seconds)
        self.demo_paused = False
        self.demo_start_time = None
        self.running = True

        # Grid layout (2x3)
        self.grid_cols = 2
        self.grid_rows = 3

    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

            if event.type == pygame.KEYDOWN:
                # ESC - exit to home or exit demo mode
                if event.key == pygame.K_ESCAPE:
                    if self.demo_mode:
                        self.demo_mode = False
                        self.demo_paused = False
                    else:
                        self.running = False
                        return False

                # Navigation (only when not in demo mode)
                elif not self.demo_mode:
                    if event.key == pygame.K_LEFT:
                        if self.selected_module % self.grid_cols > 0:
                            self.selected_module -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.selected_module % self.grid_cols < self.grid_cols - 1 and \
                           self.selected_module < len(self.MODULES) - 1:
                            self.selected_module += 1
                    elif event.key == pygame.K_UP:
                        if self.selected_module >= self.grid_cols:
                            self.selected_module -= self.grid_cols
                    elif event.key == pygame.K_DOWN:
                        if self.selected_module + self.grid_cols < len(self.MODULES):
                            self.selected_module += self.grid_cols

                    # ENTER - toggle preview panel
                    elif event.key == pygame.K_RETURN:
                        self.show_preview_panel = not self.show_preview_panel

                    # S - start demo mode
                    elif event.key == pygame.K_s:
                        self.demo_mode = True
                        self.demo_start_time = time.time()
                        self.demo_timer = 30  # Fast 30-second demo timer
                        self.demo_paused = False

                # Demo mode controls
                elif self.demo_mode:
                    # SPACE - pause/resume
                    if event.key == pygame.K_SPACE:
                        self.demo_paused = not self.demo_paused
                        if not self.demo_paused:
                            self.demo_start_time = time.time() - (30 - self.demo_timer)
                    # R - reset
                    elif event.key == pygame.K_r:
                        self.demo_timer = 30
                        self.demo_start_time = time.time()
                        self.demo_paused = False

        return True

    def update(self):
        """Update demo timer"""
        if self.demo_mode and not self.demo_paused and self.demo_start_time:
            elapsed = time.time() - self.demo_start_time
            self.demo_timer = max(0, 30 - int(elapsed))

    def draw(self):
        """Main draw function"""
        self.screen.fill(self.bg_color)

        if self.demo_mode:
            self.draw_demo_overlay()
        else:
            self.draw_main_view()

        pygame.display.flip()

    def draw_main_view(self):
        """Draw the main productivity view"""
        # Title
        title_surf = self.font_title.render("PRODUCTIVITY", True, self.text_primary)
        self.screen.blit(title_surf, (int(40 * self.scale), int(30 * self.scale)))

        # Subtitle
        subtitle_surf = self.font_subtitle.render("Ambient Workflow Layer", True, self.text_secondary)
        self.screen.blit(subtitle_surf, (int(40 * self.scale), int(120 * self.scale)))

        # Calculate grid area
        if self.show_preview_panel:
            # Grid takes 60% of width, panel takes 40%
            grid_width = int(self.width * 0.58)
        else:
            grid_width = self.width - int(80 * self.scale)

        grid_start_y = int(180 * self.scale)
        grid_height = self.height - grid_start_y - int(100 * self.scale)

        # Draw module grid
        self.draw_module_grid(int(40 * self.scale), grid_start_y, grid_width, grid_height)

        # Draw preview panel if active
        if self.show_preview_panel:
            panel_x = grid_width + int(60 * self.scale)
            panel_width = self.width - panel_x - int(40 * self.scale)
            self.draw_preview_panel(panel_x, grid_start_y, panel_width, grid_height)

        # Controls footer
        self.draw_controls_footer()

    def draw_module_grid(self, x, y, width, height):
        """Draw 2x3 grid of productivity modules"""
        spacing = int(20 * self.scale)
        tile_width = (width - spacing) // self.grid_cols
        tile_height = (height - spacing * 2) // self.grid_rows

        for idx, module in enumerate(self.MODULES):
            row = idx // self.grid_cols
            col = idx % self.grid_cols

            tile_x = x + col * (tile_width + spacing)
            tile_y = y + row * (tile_height + spacing)

            self.draw_module_tile(module, tile_x, tile_y, tile_width, tile_height,
                                 idx == self.selected_module)

    def draw_module_tile(self, module, x, y, width, height, is_selected):
        """Draw a single module tile"""
        # Create tile rect
        tile_rect = pygame.Rect(x, y, width, height)

        # Background
        if is_selected:
            # Brighter background for selected
            bg_color = (35, 40, 60)
        else:
            # Dimmed for unselected
            bg_color = tuple(int(c * 0.7) for c in self.card_bg)

        pygame.draw.rect(self.screen, bg_color, tile_rect, border_radius=int(18 * self.scale))

        # Border with glow for selected
        if is_selected:
            # Thick yellow border
            pygame.draw.rect(self.screen, self.selected_border, tile_rect,
                           width=int(5 * self.scale), border_radius=int(18 * self.scale))
            # Inner glow
            glow_rect = pygame.Rect(x + int(6 * self.scale), y + int(6 * self.scale),
                                   width - int(12 * self.scale), height - int(12 * self.scale))
            pygame.draw.rect(self.screen, self.selected_border, glow_rect,
                           width=int(2 * self.scale), border_radius=int(15 * self.scale))
        else:
            pygame.draw.rect(self.screen, self.card_border, tile_rect,
                           width=int(2 * self.scale), border_radius=int(18 * self.scale))

        # Content positioning
        content_y = y + int(30 * self.scale)

        # Icon (centered, big)
        icon_surf = self.font_tile_icon.render(module["icon"], True, self.text_primary)
        icon_x = x + (width - icon_surf.get_width()) // 2
        self.screen.blit(icon_surf, (icon_x, content_y))
        content_y += icon_surf.get_height() + int(20 * self.scale)

        # Module name (centered, big)
        name_surf = self.font_tile_name.render(module["name"], True, self.text_primary)
        name_x = x + (width - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, content_y))
        content_y += name_surf.get_height() + int(12 * self.scale)

        # Sublabel (centered)
        sublabel_surf = self.font_tile_sublabel.render(module["sublabel"], True, self.text_secondary)
        sublabel_x = x + (width - sublabel_surf.get_width()) // 2
        self.screen.blit(sublabel_surf, (sublabel_x, content_y))
        content_y += sublabel_surf.get_height() + int(20 * self.scale)

        # Status pill (centered at bottom)
        self.draw_status_pill(module["status"], x, content_y, width)

    def draw_status_pill(self, status, x, y, tile_width):
        """Draw status pill (READY, etc.)"""
        pill_text = self.font_status_pill.render(status, True, self.pill_text)
        pill_width = pill_text.get_width() + int(30 * self.scale)
        pill_height = pill_text.get_height() + int(12 * self.scale)

        pill_x = x + (tile_width - pill_width) // 2
        pill_rect = pygame.Rect(pill_x, y, pill_width, pill_height)

        pygame.draw.rect(self.screen, self.pill_bg, pill_rect,
                        border_radius=int(pill_height // 2))

        text_x = pill_x + (pill_width - pill_text.get_width()) // 2
        text_y = y + (pill_height - pill_text.get_height()) // 2
        self.screen.blit(pill_text, (text_x, text_y))

    def draw_preview_panel(self, x, y, width, height):
        """Draw the licensing/OEM preview panel"""
        # Panel background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (20, 24, 38), panel_rect, border_radius=int(18 * self.scale))
        pygame.draw.rect(self.screen, self.card_border, panel_rect,
                        width=int(2 * self.scale), border_radius=int(18 * self.scale))

        # Content with padding
        content_x = x + int(30 * self.scale)
        content_y = y + int(30 * self.scale)
        content_width = width - int(60 * self.scale)

        # Panel title
        panel_title = self.font_panel_headline.render("Ambient Workflow Layer", True, self.text_primary)
        self.screen.blit(panel_title, (content_x, content_y))
        content_y += panel_title.get_height() + int(40 * self.scale)

        # Section 1: What it enables
        section_title = self.font_panel_bullet.render("What it enables:", True, self.text_primary)
        self.screen.blit(section_title, (content_x, content_y))
        content_y += section_title.get_height() + int(20 * self.scale)

        enables = [
            "• Focus pacing without screens",
            "• Ambient task awareness",
            "• Meeting presence signals",
            "• Ops & workflow visibility"
        ]

        for bullet in enables:
            bullet_surf = self.font_panel_bullet.render(bullet, True, self.text_secondary)
            self.screen.blit(bullet_surf, (content_x, content_y))
            content_y += bullet_surf.get_height() + int(10 * self.scale)

        content_y += int(30 * self.scale)

        # Section 2: OEM / Partner hooks
        section_title2 = self.font_panel_bullet.render("OEM / Partner hooks:", True, self.text_primary)
        self.screen.blit(section_title2, (content_x, content_y))
        content_y += section_title2.get_height() + int(20 * self.scale)

        hooks = [
            "• White-label ready",
            "• Custom integrations",
            "• Partner API access",
            "• Enterprise deployment"
        ]

        for bullet in hooks:
            bullet_surf = self.font_panel_bullet.render(bullet, True, self.text_secondary)
            self.screen.blit(bullet_surf, (content_x, content_y))
            content_y += bullet_surf.get_height() + int(10 * self.scale)

        # Demo script at bottom
        content_y = y + height - int(80 * self.scale)
        demo_label = self.font_controls.render("Demo script (10 seconds):", True, self.text_primary)
        self.screen.blit(demo_label, (content_x, content_y))
        content_y += demo_label.get_height() + int(8 * self.scale)

        demo_text = self.font_controls.render("Press S to see Focus Sprint in action", True, self.text_secondary)
        self.screen.blit(demo_text, (content_x, content_y))

    def draw_demo_overlay(self):
        """Draw full-screen Focus Sprint demo overlay"""
        # Semi-transparent dark background
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((8, 10, 18))
        self.screen.blit(overlay, (0, 0))

        # Center content area
        center_x = self.width // 2
        center_y = self.height // 2

        # Title
        demo_title = self.font_panel_headline.render("FOCUS SPRINT", True, self.text_primary)
        title_x = center_x - demo_title.get_width() // 2
        self.screen.blit(demo_title, (title_x, int(120 * self.scale)))

        # Huge timer
        minutes = self.demo_timer // 60
        seconds = self.demo_timer % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"

        timer_surf = self.font_demo_timer.render(timer_text, True, self.selected_border)
        timer_x = center_x - timer_surf.get_width() // 2
        timer_y = center_y - timer_surf.get_height() // 2
        self.screen.blit(timer_surf, (timer_x, timer_y))

        # Status text
        if self.demo_paused:
            status_text = "PAUSED"
            status_color = (200, 100, 100)
        else:
            status_text = "ACTIVE"
            status_color = (100, 200, 100)

        status_surf = self.font_panel_bullet.render(status_text, True, status_color)
        status_x = center_x - status_surf.get_width() // 2
        status_y = timer_y + timer_surf.get_height() + int(40 * self.scale)
        self.screen.blit(status_surf, (status_x, status_y))

        # Calming message
        message = "Ambient pacing cues. No screens required."
        message_surf = self.font_panel_bullet.render(message, True, self.text_secondary)
        message_x = center_x - message_surf.get_width() // 2
        message_y = self.height - int(200 * self.scale)
        self.screen.blit(message_surf, (message_x, message_y))

        # Controls
        controls = "SPACE pause/resume  •  R reset  •  ESC exit"
        controls_surf = self.font_controls.render(controls, True, self.text_secondary)
        controls_x = center_x - controls_surf.get_width() // 2
        controls_y = self.height - int(100 * self.scale)
        self.screen.blit(controls_surf, (controls_x, controls_y))

    def draw_controls_footer(self):
        """Draw controls help at bottom"""
        footer_y = self.height - int(70 * self.scale)

        # Background bar
        footer_rect = pygame.Rect(0, footer_y, self.width, int(70 * self.scale))
        pygame.draw.rect(self.screen, (18, 20, 30), footer_rect)

        # Controls text (big and readable)
        controls = "← → ↑ ↓ Navigate  |  ENTER Preview  |  S Start Demo  |  ESC Home"
        controls_surf = self.font_controls.render(controls, True, (200, 205, 215))
        controls_x = self.width // 2 - controls_surf.get_width() // 2
        controls_y = footer_y + int(20 * self.scale)
        self.screen.blit(controls_surf, (controls_x, controls_y))

        # Optional disclaimer (single line, readable)
        disclaimer = "Designed for general productivity & workflow awareness."
        disclaimer_surf = self.font_controls.render(disclaimer, True, (140, 145, 160))
        disclaimer_x = self.width // 2 - disclaimer_surf.get_width() // 2
        disclaimer_y = footer_y + int(20 * self.scale) + controls_surf.get_height() + int(4 * self.scale)
        self.screen.blit(disclaimer_surf, (disclaimer_x, disclaimer_y))

    def run(self):
        """Main loop for standalone testing"""
        clock = pygame.time.Clock()

        while self.running:
            if not self.handle_input():
                break

            self.update()
            self.draw()
            clock.tick(30)

        return False  # Return to home


def standalone_test():
    """Standalone test for Productivity realm"""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Productivity Realm - Projection Test")

    realm = ProductivityRealm(screen)
    realm.run()

    pygame.quit()


if __name__ == "__main__":
    standalone_test()
