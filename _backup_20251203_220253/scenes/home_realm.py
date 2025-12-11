"""
MotiBeam Spatial OS - Home Realm
Smart Home, Family Management, Ambient Living
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class HomeRealm(SpatialRealm):
    """Smart home and family ambient computing realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Home Realm",
            realm_description="Smart Home, Family Management, Ambient Living"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.smart_devices = []
        self.family_members = []

    def initialize(self) -> bool:
        """Initialize home realm systems"""
        print("  🏡 Initializing Home Realm Systems...")

        scan = self.spatial_engine.scan_environment("home")
        print(f"  ✓ Home mapped: {scan['room_dimensions']}")

        self.beam_network.establish_mesh("Home Network")

        self.smart_devices = [
            {"id": "LIGHT-01", "type": "Smart Lights", "room": "Living Room", "status": "On"},
            {"id": "THERM-01", "type": "Thermostat", "room": "Main", "status": "Auto"},
            {"id": "CAM-01", "type": "Security Camera", "room": "Front Door", "status": "Active"},
            {"id": "LOCK-01", "type": "Smart Lock", "room": "Front Door", "status": "Locked"}
        ]

        print("  ✓ Home systems online")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate home realm capabilities (text mode)"""
        self.display_header()

        print("\n🏡 SMART HOME OVERVIEW")
        print("  Connected devices: 47")
        print("  Family members home: 3/4")
        print("  Energy usage: Optimal")
        print("  Security: All zones secured")
        time.sleep(1)

        print("\n🌅 MORNING ROUTINE AUTOMATION")
        print("  Detected: Sarah waking up (6:45 AM)")
        self.simulate_ai_processing("Personalized morning routine")
        print("  ✓ Bedroom lights: Gradual warm-up started")
        print("  ✓ Thermostat: Raised to 72°F")
        print("  ✓ Coffee maker: Brewing started")
        print("  ✓ News briefing: Queued on kitchen display")
        time.sleep(1)

        print("\n👨‍👩‍👧‍👦 FAMILY PRESENCE & ACTIVITY")
        print("  • Dad: Home office (focused work mode)")
        print("  • Mom: Kitchen (meal prep detected)")
        print("  • Kids: Playroom (active play mode)")
        print("  ✓ Adjusted lighting, climate, and audio zones")
        time.sleep(1)

        print("\n🔐 PROACTIVE SECURITY")
        print("  Event: Package delivered at front door")
        self.simulate_ai_processing("Facial recognition and authorization")
        print("  ✓ Delivery person recognized (USPS)")
        print("  ✓ Package logged and family notified")
        print("  ✓ No action needed - expected delivery")
        time.sleep(1)

        print("\n⚡ ENERGY OPTIMIZATION")
        print("  Current usage: 4.2 kW")
        print("  Solar generation: 6.8 kW")
        print("  Net: +2.6 kW (feeding grid)")
        print("  💰 Today's savings: $12.40")

    def run(self, duration=60):
        """Run live HUD demo with enhanced wall-readable two-column layout"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import (
            get_fonts, draw_background, draw_header,
            draw_two_column_layout, draw_footer_ticker,
            REALM_COLORS, render_icon
        )
        from core.global_state import global_state

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('home', (100, 200, 255))
        fonts = get_fonts(self.screen)
        w, h = self.screen.get_size()

        # View state (manual control with LEFT/RIGHT)
        current_view = 0
        num_views = 4

        # Event state (triggered by SPACE)
        show_event = False
        event_time = 0
        event_text = ""

        # Scrolling ticker updates
        ticker_items = [
            "Laundry done in 12m",
            "Front door locked",
            "Bedtime routine in 2h 15m",
            "Thermostat adjusted to 68°F",
            "Living room lights dimmed",
            "Coffee maker ready for 6:45 AM",
            "Security system armed",
            "Energy grid: selling 2.6 kW"
        ]
        ticker_text = " · ".join(ticker_items) + " · "

        # Animated breathing neon circles (Home realm specific)
        # Positioned to avoid text overlap
        circles = [
            {"x": w * 0.15, "y": h * 0.30, "r": 90, "dr": 0.25, "base": 90},
            {"x": w * 0.88, "y": h * 0.50, "r": 130, "dr": -0.2, "base": 130},
            {"x": w * 0.12, "y": h * 0.75, "r": 110, "dr": 0.18, "base": 110},
        ]

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

                    # LEFT/RIGHT to cycle views
                    elif event.key == pygame.K_LEFT:
                        current_view = (current_view - 1) % num_views
                    elif event.key == pygame.K_RIGHT:
                        current_view = (current_view + 1) % num_views

                    # SPACE to trigger event
                    elif event.key == pygame.K_SPACE:
                        show_event = True
                        event_time = time.time()
                        event_text = "Front doorbell rang! Package detected"

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            # Hide event after 3 seconds
            if show_event and (time.time() - event_time > 3):
                show_event = False

            # Get mode configuration for dimming
            mode_config = global_state.get_mode_config()

            # Background with living motion
            draw_background(self.screen, elapsed)

            # Draw animated breathing circles (Home realm ambient effect)
            # Respects mode dimming
            for c in circles:
                # Update radius (breathing effect) with mode speed multiplier
                speed = c["dr"] * mode_config['circle_speed_multiplier']
                c["r"] += speed
                if c["r"] > c["base"] + 15 or c["r"] < c["base"] - 15:
                    c["dr"] *= -1

                # Draw circle with neon glow
                radius = int(c["r"])
                x = int(c["x"])
                y = int(c["y"])

                # Create surface for circle with transparency
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

                # Draw glow (outer circle, semi-transparent) - mode dimmed
                glow_alpha = int(25 * mode_config['circle_alpha_multiplier'])
                pygame.draw.circle(s, (*accent_color, glow_alpha), (radius, radius), radius)

                # Draw stroke (neon outline) - mode dimmed
                stroke_alpha = int(120 * mode_config['circle_alpha_multiplier'])
                pygame.draw.circle(s, (*accent_color, stroke_alpha), (radius, radius), radius, 3)

                # Blit to screen
                self.screen.blit(s, (x - radius, y - radius), special_flags=pygame.BLEND_ADD)

            # Header band with emoji
            draw_header(
                self.screen, fonts, 'home',
                '🏡 HOME REALM',
                '🏠 Smart Home · 👨‍👩‍👧‍👦 Family · ☀️ Ambient Living',
                accent_color, "● LIVE"
            )

            # Middle band - Four rotating views
            if current_view == 0:
                # View 1: Family Presence & Status
                left_section = {
                    'title': 'FAMILY PRESENCE',
                    'items': [
                        "Dad: Home Office (Focus Mode)",
                        "Mom: Kitchen (Meal Prep)",
                        "Kids: Playroom (Active Play)",
                        "",
                        "",
                        ""
                    ]
                }

                right_section = {
                    'title': 'SMART HOME STATUS',
                    'items': [
                        "Devices online: 47",
                        "Deliveries today: 1",
                        "Quiet hours: 10:00 PM – 6:00 AM",
                        "Rooms active: 3",
                        "",
                        ""
                    ]
                }

            elif current_view == 1:
                # View 2: Energy & Climate
                left_section = {
                    'title': 'ENERGY MANAGEMENT',
                    'items': [
                        "Solar generation: 6.8 kW",
                        "Current usage: 4.2 kW",
                        "Net: +2.6 kW (feeding grid)",
                        "",
                        "Today's savings: $12.40",
                        "This month: $287.50"
                    ]
                }

                right_section = {
                    'title': 'CLIMATE & COMFORT',
                    'items': [
                        "Living Room: 72°F (normal)",
                        "Bedroom: 68°F (sleep)",
                        "Office: 70°F (focus mode)",
                        "",
                        "Air quality: Excellent",
                        "Humidity: 45% (ideal)"
                    ]
                }

            elif current_view == 2:
                # View 3: Scenes & Routines
                left_section = {
                    'title': 'SMART SCENES',
                    'items': [
                        "Morning Boost",
                        "  Lights warm · Coffee on · News brief",
                        "",
                        "Study Mode",
                        "  Distraction-free · Notifications low",
                        ""
                    ]
                }

                right_section = {
                    'title': 'AUTOMATION MODES',
                    'items': [
                        "Movie Night",
                        "  Lights dim · Speakers on · Do Not Disturb",
                        "",
                        "Away / Travel",
                        "  Security armed · Random lights · Package alerts",
                        ""
                    ]
                }

            else:
                # View 4: Ambient Loop (Centered status display)
                # Get current date/time
                now = datetime.now()
                weekday = now.strftime("%A")
                current_time = now.strftime("%I:%M %p").lstrip("0")

                left_section = {
                    'title': 'HOME STATUS',
                    'items': [
                        "",
                        "Home Secure · All doors locked · Quiet hours",
                        "",
                        f"{weekday} · {current_time}",
                        "",
                        ""
                    ]
                }

                right_section = {
                    'title': 'AMBIENT',
                    'items': [
                        "",
                        "Family home & comfortable",
                        "",
                        "Energy: Optimal",
                        "",
                        ""
                    ]
                }

            draw_two_column_layout(
                self.screen, fonts,
                left_section, right_section,
                y_start=250, accent_color=accent_color
            )

            # Event notification (if triggered)
            if show_event:
                event_y = h - 180
                event_surf = pygame.Surface((w - 200, 80), pygame.SRCALPHA)
                pygame.draw.rect(event_surf, (0, 0, 0, 180), (0, 0, w - 200, 80), border_radius=10)
                pygame.draw.rect(event_surf, accent_color, (0, 0, w - 200, 80), 3, border_radius=10)
                self.screen.blit(event_surf, (100, event_y))

                event_text_surf = fonts['body'].render(event_text, True, (255, 255, 255))
                event_text_rect = event_text_surf.get_rect(center=(w // 2, event_y + 40))
                self.screen.blit(event_text_surf, event_text_rect)

            # Bottom band - Updated footer with controls
            footer_y = h - 90
            mode_text = f"Mode: {global_state.mode}"
            mode_surf = fonts['small'].render(mode_text, True, accent_color)
            self.screen.blit(mode_surf, (50, footer_y))

            view_text = f"View {current_view + 1}/{num_views}"
            view_surf = fonts['small'].render(view_text, True, (180, 190, 210))
            view_rect = view_surf.get_rect(center=(w // 2, footer_y))
            self.screen.blit(view_surf, view_rect)

            controls_text = "← → : Views · SPACE: Event · ESC: Exit"
            controls_surf = fonts['small'].render(controls_text, True, (180, 190, 210))
            controls_rect = controls_surf.get_rect(right=w - 50, centery=footer_y)
            self.screen.blit(controls_surf, controls_rect)

            pygame.display.flip()
            clock.tick(30)

    def get_status(self) -> dict:
        """Get home realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "smart_devices": len(self.smart_devices),
            "family_members": len(self.family_members),
            "mesh_strength": self.beam_network.mesh_strength
        }
