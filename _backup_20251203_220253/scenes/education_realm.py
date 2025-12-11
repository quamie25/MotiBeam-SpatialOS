"""
MotiBeam Spatial OS - Education Realm
Learning Environments, Study Focus, Knowledge Management
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class EducationRealm(SpatialRealm):
    """Education and learning ambient computing realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Education Realm",
            realm_description="Learning Environments, Study Focus, Knowledge Management"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.learning_sessions = []
        self.students = []

    def initialize(self) -> bool:
        """Initialize education realm systems"""
        print("  📚 Initializing Education Realm Systems...")

        scan = self.spatial_engine.scan_environment("education")
        print(f"  ✓ Learning space mapped: {scan['room_dimensions']}")

        self.beam_network.establish_mesh("Education Network")

        self.learning_sessions = [
            {"id": "MATH-101", "subject": "Calculus", "student": "Alex", "progress": 67},
            {"id": "PHYS-201", "subject": "Quantum Mechanics", "student": "Sam", "progress": 82},
            {"id": "LANG-FR", "subject": "French", "student": "Emma", "progress": 45}
        ]

        print("  ✓ Education systems online")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate education realm capabilities (text mode)"""
        self.display_header()

        print("\n📚 LEARNING ENVIRONMENT OVERVIEW")
        print("  Active students: 4")
        print("  Study sessions today: 3")
        print("  Focus score: 88/100")
        print("  Knowledge retention: High")
        time.sleep(1)

        print("\n🎯 ADAPTIVE LEARNING SESSION")
        print("  Student: Alex (Studying Calculus)")
        self.simulate_ai_processing("Personalized learning path optimization")
        print("  Current topic: Integration by parts")
        print("  Comprehension level: 73%")
        print("  ✓ Adjusted difficulty: Medium → Advanced")
        print("  ✓ Recommended: 3 practice problems")
        time.sleep(1)

        print("\n🧠 FOCUS & ATTENTION MANAGEMENT")
        print("  Environment optimization:")
        print("  • Lighting: Adjusted to focus mode (cool white)")
        print("  • Audio: Background noise cancellation active")
        print("  • Distractions blocked: 12 notifications silenced")
        print("  ⏱️  Pomodoro timer: 22 minutes remaining")
        time.sleep(1)

        print("\n📊 LEARNING ANALYTICS")
        self.simulate_ai_processing("Knowledge gap analysis")
        print("  Strengths:")
        print("  • Differential equations: 92% mastery")
        print("  • Linear algebra: 88% mastery")
        print("  Focus areas:")
        print("  • Integration techniques: 65% (practice needed)")
        print("  ✓ Personalized practice set generated")
        time.sleep(1)

        print("\n🎓 STUDY GROUP COORDINATION")
        print("  Detected: 3 students studying related topics")
        print("  ✓ Suggested collaborative session at 3:00 PM")
        print("  ✓ Shared AR whiteboard prepared")
        print("  ✓ Study materials synchronized")

    def run(self, duration=60):
        """Run teacher's assistant display with big flashcard concepts"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import (
            get_fonts, draw_background, draw_header,
            draw_footer_ticker, REALM_COLORS, COLOR_TEXT_PRIMARY,
            COLOR_TEXT_SECONDARY
        )
        from core.global_state import global_state

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('education', (150, 150, 255))
        fonts = get_fonts(self.screen)
        w, h = self.screen.get_size()

        # Manual view control (no auto-cycle, only LEFT/RIGHT)
        current_concept = 0

        # Event state (triggered by SPACE)
        show_event = False
        event_time = 0

        # Flashcard concepts - manual navigation
        concepts = [
            {
                'title': '📐 Concept: Photosynthesis',
                'content': 'Process by which plants convert',
                'content2': 'light energy into chemical energy',
                'detail': 'Uses: CO₂ + H₂O + Light → Glucose + O₂'
            },
            {
                'title': '❓ Question: Why are plants green?',
                'content': 'Plants reflect green wavelengths',
                'content2': 'while absorbing red and blue light',
                'detail': 'Answer: Chlorophyll pigment reflects green'
            },
            {
                'title': '🧬 Concept: Cell Division - Mitosis',
                'content': 'Process where one cell divides',
                'content2': 'into two identical daughter cells',
                'detail': 'Phases: Prophase → Metaphase → Anaphase → Telophase'
            },
            {
                'title': '🔢 Formula: Pythagorean Theorem',
                'content': 'In a right triangle:',
                'content2': 'a² + b² = c²',
                'detail': 'Where c is the hypotenuse (longest side)'
            }
        ]

        # Animated circles - ONLY in corners, far from center text
        circles = [
            {"x": w * 0.08, "y": h * 0.20, "r": 70, "dr": 0.15, "base": 70},
            {"x": w * 0.92, "y": h * 0.25, "r": 85, "dr": -0.12, "base": 85},
            {"x": w * 0.05, "y": h * 0.85, "r": 65, "dr": 0.10, "base": 65},
            {"x": w * 0.95, "y": h * 0.88, "r": 75, "dr": -0.14, "base": 75},
        ]

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

                    # LEFT/RIGHT to navigate concepts
                    elif event.key == pygame.K_LEFT:
                        current_concept = (current_concept - 1) % len(concepts)
                    elif event.key == pygame.K_RIGHT:
                        current_concept = (current_concept + 1) % len(concepts)

                    # SPACE to mark concept mastered
                    elif event.key == pygame.K_SPACE:
                        show_event = True
                        event_time = time.time()

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            # Hide event after 2 seconds
            if show_event and (time.time() - event_time > 2):
                show_event = False

            # Get mode configuration
            mode_config = global_state.get_mode_config()

            # Background
            draw_background(self.screen, elapsed)

            # Draw circles ONLY in NORMAL mode (hide in STUDY/SLEEP for max focus)
            if global_state.mode == "NORMAL":
                for c in circles:
                    # Update radius
                    speed = c["dr"] * mode_config['circle_speed_multiplier']
                    c["r"] += speed
                    if c["r"] > c["base"] + 10 or c["r"] < c["base"] - 10:
                        c["dr"] *= -1

                    radius = int(c["r"])
                    x = int(c["x"])
                    y = int(c["y"])

                    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    glow_alpha = int(15 * mode_config['circle_alpha_multiplier'])
                    pygame.draw.circle(s, (*accent_color, glow_alpha), (radius, radius), radius)
                    stroke_alpha = int(80 * mode_config['circle_alpha_multiplier'])
                    pygame.draw.circle(s, (*accent_color, stroke_alpha), (radius, radius), radius, 2)
                    self.screen.blit(s, (x - radius, y - radius), special_flags=pygame.BLEND_ADD)

            # Header
            draw_header(
                self.screen, fonts, 'education',
                '📚 EDUCATION REALM',
                '🎓 Adaptive Learning · 🧠 Focus · 📖 Knowledge Management',
                accent_color, "● LIVE"
            )

            # === MIDDLE BAND: Big centered flashcard ===
            y_center = 280

            # Current concept
            concept = concepts[current_concept]

            # Draw concept title (huge)
            title_surf = fonts['title'].render(concept['title'], True, accent_color)
            title_w = title_surf.get_width()
            self.screen.blit(title_surf, ((w - title_w) // 2, y_center))

            # Draw content lines (mega font for maximum readability)
            y_content = y_center + 120
            content_surf = fonts['huge'].render(concept['content'], True, COLOR_TEXT_PRIMARY)
            content_w = content_surf.get_width()
            self.screen.blit(content_surf, ((w - content_w) // 2, y_content))

            content2_surf = fonts['huge'].render(concept['content2'], True, COLOR_TEXT_PRIMARY)
            content2_w = content2_surf.get_width()
            self.screen.blit(content2_surf, ((w - content2_w) // 2, y_content + 100))

            # Draw detail/answer (smaller, below)
            detail_surf = fonts['body'].render(concept['detail'], True, COLOR_TEXT_SECONDARY)
            detail_w = detail_surf.get_width()
            self.screen.blit(detail_surf, ((w - detail_w) // 2, y_content + 220))

            # Event notification (if triggered)
            if show_event:
                event_y = h - 180
                event_surf = pygame.Surface((w - 200, 70), pygame.SRCALPHA)
                pygame.draw.rect(event_surf, (0, 0, 0, 200), (0, 0, w - 200, 70), border_radius=10)
                pygame.draw.rect(event_surf, (100, 255, 100), (0, 0, w - 200, 70), 3, border_radius=10)
                self.screen.blit(event_surf, (100, event_y))

                event_text = "✅ Concept marked as mastered!"
                event_text_surf = fonts['body'].render(event_text, True, (100, 255, 100))
                event_text_rect = event_text_surf.get_rect(center=(w // 2, event_y + 35))
                self.screen.blit(event_text_surf, event_text_rect)

            # Bottom footer with controls
            footer_y = h - 90
            mode_text = f"Mode: {global_state.mode}"
            mode_surf = fonts['small'].render(mode_text, True, accent_color)
            self.screen.blit(mode_surf, (50, footer_y))

            card_text = f"Concept {current_concept + 1}/{len(concepts)}"
            card_surf = fonts['small'].render(card_text, True, (180, 190, 210))
            card_rect = card_surf.get_rect(center=(w // 2, footer_y))
            self.screen.blit(card_surf, card_rect)

            controls_text = "← → : Navigate · SPACE: Master · ESC: Exit"
            controls_surf = fonts['small'].render(controls_text, True, (180, 190, 210))
            controls_rect = controls_surf.get_rect(right=w - 50, centery=footer_y)
            self.screen.blit(controls_surf, controls_rect)

            pygame.display.flip()
            clock.tick(30)

    def get_status(self) -> dict:
        """Get education realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "learning_sessions": len(self.learning_sessions),
            "students": len(self.students),
            "mesh_strength": self.beam_network.mesh_strength
        }
