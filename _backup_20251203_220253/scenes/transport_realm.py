"""
MotiBeam Spatial OS - Transport Realm
Automotive HUD, Navigation, Driver Assistance
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class TransportRealm(SpatialRealm):
    """Automotive and transport ambient computing realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Transport Realm",
            realm_description="Automotive HUD, Navigation, Driver Assistance"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.vehicles = []
        self.routes = []

    def initialize(self) -> bool:
        """Initialize transport realm systems"""
        print("  🚗 Initializing Transport Realm Systems...")

        scan = self.spatial_engine.scan_environment("vehicle")
        print(f"  ✓ Vehicle environment mapped: {scan['room_dimensions']}")

        self.beam_network.establish_mesh("Transport Network")

        self.vehicles = [
            {"id": "VEH-001", "type": "Tesla Model 3", "status": "Active", "battery": 87},
            {"id": "VEH-002", "type": "Family SUV", "status": "Parked", "fuel": 65}
        ]

        print("  ✓ Transport systems online")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate transport realm capabilities (text mode)"""
        self.display_header()

        print("\n🚗 AUTOMOTIVE OVERVIEW")
        print("  Active vehicle: Tesla Model 3")
        print("  Speed: 55 mph")
        print("  Battery: 87% (240 miles range)")
        print("  Autopilot: Engaged")
        time.sleep(1)

        print("\n🗺️  AR NAVIGATION HUD")
        print("  Destination: 123 Main St, Boston MA")
        self.simulate_ai_processing("Real-time route optimization")
        print("  Distance: 12.3 miles")
        print("  ETA: 18 minutes")
        print("  ✓ AR arrows overlaid on windshield")
        print("  ✓ Lane guidance: Keep right, exit in 2 miles")
        time.sleep(1)

        print("\n⚠️  INTELLIGENT SAFETY SYSTEMS")
        print("  Active monitoring:")
        print("  • Forward collision: Clear")
        print("  • Blind spot left: Vehicle detected")
        print("  • Blind spot right: Clear")
        print("  ⚠️  Alert: Pedestrian ahead, reducing speed")
        print("  ✓ Auto-brake engaged: 55 → 30 mph")
        time.sleep(1)

        print("\n🌐 PREDICTIVE TRAFFIC AI")
        self.simulate_ai_processing("Traffic pattern analysis")
        print("  Detected: Accident on Route 93")
        print("  Impact: +12 minute delay")
        print("  ✓ Alternate route calculated (via I-90)")
        print("  ✓ New ETA: 19 minutes (saves 11 min)")
        time.sleep(1)

        print("\n🔋 ENERGY OPTIMIZATION")
        print("  Current efficiency: 4.2 mi/kWh")
        print("  Regenerative braking: Active")
        print("  Supercharger nearby: 0.8 miles")
        print("  ✓ Route optimized for battery range")

    def run(self, duration=12):
        """Run windshield HUD with speed, navigation, and safety info"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import (
            get_fonts, draw_header, REALM_COLORS,
            COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
            COLOR_ACCENT_GREEN, COLOR_ACCENT_ORANGE, COLOR_BG
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('transport', (100, 180, 255))
        fonts = get_fonts(self.screen)
        w, h = self.screen.get_size()

        # Driving scenarios that cycle
        scenarios = [
            {'mode': 'STANDARD', 'speed': 55, 'condition': 'Clear', 'alert': None},
            {'mode': 'RAIN', 'speed': 45, 'condition': 'Low Visibility', 'alert': 'Wipers: Auto'},
            {'mode': 'HIGHWAY', 'speed': 70, 'condition': 'Cruise Active', 'alert': None},
        ]

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            # Minimal background - like glass HUD (fewer/smaller circles)
            self.screen.fill(COLOR_BG)

            # Subtle horizontal bands for HUD feel
            for i in range(3):
                band_y = 300 + i * 200
                band_surf = pygame.Surface((w, 2), pygame.SRCALPHA)
                pygame.draw.rect(band_surf, (*accent_color, 15), (0, 0, w, 2))
                self.screen.blit(band_surf, (0, band_y))

            # Header (minimal for HUD)
            draw_header(
                self.screen, fonts, 'transport',
                '🚗 TRANSPORT REALM',
                '🛣️ Automotive HUD · 🗺️ Navigation · 🚦 Driver Assistance',
                accent_color, "● LIVE"
            )

            # Determine scenario (cycle every 4 seconds)
            scenario_index = int(elapsed / 4) % len(scenarios)
            scenario = scenarios[scenario_index]

            # === CENTER-RIGHT: HUGE SPEED ===
            speed_x = w - 500
            speed_y = 350

            speed_text = str(scenario['speed'])
            speed_surf = fonts['mega'].render(speed_text, True, accent_color)
            self.screen.blit(speed_surf, (speed_x, speed_y))

            unit_surf = fonts['header'].render("mph", True, COLOR_TEXT_SECONDARY)
            self.screen.blit(unit_surf, (speed_x + 200, speed_y + 120))

            # Mode indicator
            mode_surf = fonts['body'].render(scenario['mode'], True, accent_color)
            self.screen.blit(mode_surf, (speed_x, speed_y - 60))

            # Condition
            cond_surf = fonts['small'].render(scenario['condition'], True, COLOR_TEXT_SECONDARY)
            self.screen.blit(cond_surf, (speed_x, speed_y + 200))

            # === LEFT SIDE: NAVIGATION ===
            nav_x = 120
            nav_y = 350

            # Navigation arrow (simple triangle pointing up/right)
            arrow_points = [
                (nav_x + 40, nav_y),
                (nav_x + 70, nav_y + 30),
                (nav_x + 40, nav_y + 60),
                (nav_x + 45, nav_y + 30)
            ]
            pygame.draw.polygon(self.screen, accent_color, arrow_points)

            # Distance to turn
            dist_surf = fonts['header'].render("2.3 mi", True, accent_color)
            self.screen.blit(dist_surf, (nav_x + 100, nav_y + 10))

            # Direction
            dir_surf = fonts['body'].render("Exit right onto I-90", True, COLOR_TEXT_PRIMARY)
            self.screen.blit(dir_surf, (nav_x, nav_y + 90))

            # Destination
            dest_surf = fonts['small'].render("Destination: 123 Main St", True, COLOR_TEXT_SECONDARY)
            self.screen.blit(dest_surf, (nav_x, nav_y + 140))

            eta_surf = fonts['small'].render("ETA: 18 min", True, COLOR_TEXT_SECONDARY)
            self.screen.blit(eta_surf, (nav_x, nav_y + 180))

            # === BOTTOM: LANE & PROXIMITY ===
            bottom_y = h - 180

            # Blind spot indicators
            left_status = "Vehicle" if scenario['mode'] == 'HIGHWAY' else "CLEAR"
            right_status = "CLEAR"

            left_color = COLOR_ACCENT_ORANGE if left_status == "Vehicle" else COLOR_ACCENT_GREEN
            right_color = COLOR_ACCENT_GREEN

            # Left blind spot
            left_surf = fonts['small'].render(f"Left: {left_status}", True, left_color)
            self.screen.blit(left_surf, (120, bottom_y))

            # Forward collision
            fwd_surf = fonts['small'].render("Forward: Clear", True, COLOR_ACCENT_GREEN)
            self.screen.blit(fwd_surf, ((w - fwd_surf.get_width()) // 2, bottom_y))

            # Right blind spot
            right_surf = fonts['small'].render(f"Right: {right_status}", True, right_color)
            self.screen.blit(right_surf, (w - 300, bottom_y))

            # Lane guidance visual
            lane_y = bottom_y + 60
            lane_width = 600
            lane_x = (w - lane_width) // 2

            # Draw lane markers
            pygame.draw.line(self.screen, COLOR_TEXT_SECONDARY,
                           (lane_x, lane_y), (lane_x, lane_y + 40), 3)
            pygame.draw.line(self.screen, COLOR_TEXT_SECONDARY,
                           (lane_x + lane_width, lane_y), (lane_x + lane_width, lane_y + 40), 3)

            # Center dashed line
            for i in range(5):
                dash_x = lane_x + lane_width // 2
                dash_y = lane_y + i * 10
                pygame.draw.line(self.screen, COLOR_TEXT_SECONDARY,
                               (dash_x, dash_y), (dash_x, dash_y + 5), 2)

            # Vehicle position indicator
            car_x = lane_x + lane_width // 2 - 20
            car_y = lane_y + 10
            pygame.draw.rect(self.screen, accent_color, (car_x, car_y, 40, 20), border_radius=3)

            # Alert overlay if applicable
            if scenario['alert']:
                alert_y = h - 280
                alert_surf = fonts['body'].render(scenario['alert'], True, COLOR_ACCENT_ORANGE)
                alert_w = alert_surf.get_width()
                # Semi-transparent background
                alert_bg = pygame.Surface((alert_w + 40, 60), pygame.SRCALPHA)
                pygame.draw.rect(alert_bg, (0, 0, 0, 120), (0, 0, alert_w + 40, 60), border_radius=10)
                self.screen.blit(alert_bg, ((w - alert_w - 40) // 2, alert_y - 10))
                self.screen.blit(alert_surf, ((w - alert_w) // 2, alert_y))

            # Footer status bar (minimal)
            footer_y = h - 50
            footer_surf = fonts['small'].render(
                f"Consumer Mode · [TRANSPORT] · {remaining}s remaining",
                True, accent_color
            )
            footer_w = footer_surf.get_width()
            self.screen.blit(footer_surf, ((w - footer_w) // 2, footer_y))

            pygame.display.flip()
            clock.tick(30)

    def get_status(self) -> dict:
        """Get transport realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "vehicles": len(self.vehicles),
            "routes": len(self.routes),
            "mesh_strength": self.beam_network.mesh_strength
        }
