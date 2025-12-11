"""
MotiBeam Spatial OS - Emergency Response Realm
911 Dispatch, Crisis Response, Medical Emergency Management
"""

import random
import time
import math
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class EmergencyRealm(SpatialRealm):
    """Emergency response and crisis management realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Emergency Response Realm",
            realm_description="911 Dispatch, Crisis Response, Medical Emergency Management"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.active_incidents = []
        self.emergency_units = []

    def initialize(self) -> bool:
        """Initialize emergency response systems"""
        print("  🚨 Initializing Emergency Response Systems...")

        # Initialize spatial awareness
        scan = self.spatial_engine.scan_environment("emergency")
        print(f"  ✓ Emergency zone mapped: {scan['room_dimensions']}")

        # Establish emergency mesh network
        self.beam_network.establish_mesh("Emergency Response")

        # Initialize emergency units
        self.emergency_units = [
            {"id": "AMB-01", "type": "Ambulance", "status": "Ready", "location": "Station 3"},
            {"id": "FIRE-02", "type": "Fire Engine", "status": "Ready", "location": "Station 1"},
            {"id": "POL-05", "type": "Police", "status": "Patrol", "location": "Sector 7"}
        ]

        print("  ✓ Emergency response systems online")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate emergency response capabilities"""
        self.display_header()

        print("\n📞 INCOMING 911 CALL")
        print("  Caller: Elderly male, chest pain, difficulty breathing")
        print("  Location: 42.3601° N, 71.0589° W (Boston, MA)")
        time.sleep(1)

        # AI Triage
        self.simulate_ai_processing("Emergency triage and classification")
        print("  🎯 Priority: CRITICAL - Suspected cardiac event")
        print("  📊 Confidence: 94%")
        time.sleep(1)

        # Spatial mapping of incident
        print("\n🗺️  SPATIAL INCIDENT MAPPING")
        scan = self.spatial_engine.scan_environment("incident_location")
        print(f"  Location: Residential building, 3rd floor")
        print(f"  Access points: 2 entrances, elevator available")
        print(f"  Nearest AED: 150m (CVS Pharmacy)")
        time.sleep(1)

        # Resource allocation
        print("\n🚑 RESOURCE ALLOCATION")
        self.simulate_ai_processing("Optimal unit dispatch calculation")

        print("  Dispatching:")
        print("    • AMB-01 (ETA: 3m 45s) - Priority 1")
        print("    • FIRE-02 (ETA: 4m 12s) - Support")
        print("    • Alerting nearby civilian AED carriers")
        time.sleep(1)

        # Real-time coordination
        print("\n📡 REAL-TIME COORDINATION")
        self.spatial_engine.create_ar_overlay("Route optimization", "responder_HUD")
        print("  ✓ AR navigation overlay sent to AMB-01")
        print("  ✓ Building access codes transmitted")
        print("  ✓ Patient vitals streaming to paramedics")
        time.sleep(1)

        # Predictive analysis
        print("\n🔮 PREDICTIVE CRISIS ANALYSIS")
        self.simulate_ai_processing("Pattern recognition across city incidents")
        print("  ⚠️  Alert: Traffic congestion detected on Route 9")
        print("  ✓ Auto-routing AMB-01 via alternate path")
        print("  📉 ETA reduced by 47 seconds")
        time.sleep(1)

        # Outcome
        print("\n✅ INCIDENT RESOLUTION")
        print("  • Paramedics arrived: 3m 28s")
        print("  • Patient stabilized on-scene")
        print("  • En route to Mass General Hospital")
        print("  • Family members notified")
        print("  • Incident logged and analyzed for system improvement")

    def get_status(self) -> dict:
        """Get emergency realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "active_incidents": len(self.active_incidents),
            "available_units": len([u for u in self.emergency_units if u["status"] == "Ready"]),
            "mesh_strength": self.beam_network.mesh_strength
        }

    def dispatch_unit(self, unit_id: str, incident_id: str) -> None:
        """Dispatch emergency unit to incident"""
        print(f"  🚨 Dispatching {unit_id} to incident {incident_id}")

    def simulate_emergency_call(self) -> dict:
        """Simulate an incoming emergency call"""
        emergency_types = [
            "Cardiac arrest",
            "Structure fire",
            "Armed robbery",
            "Vehicle accident",
            "Medical emergency"
        ]

        return {
            "type": random.choice(emergency_types),
            "severity": random.choice(["Critical", "High", "Medium"]),
            "location": f"{random.uniform(42.0, 43.0):.4f}° N, {random.uniform(-71.5, -70.5):.4f}° W",
            "timestamp": datetime.now()
        }

    def run(self, duration=12):
        """Run 911 command wall HUD with critical real-time info"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import (
            get_fonts, draw_background, draw_header,
            draw_footer_ticker, REALM_COLORS
        )

        # Emergency red accent
        accent_color = REALM_COLORS.get('emergency', (255, 50, 50))
        COLOR_TEXT_PRIMARY = (240, 240, 240)
        COLOR_TEXT_SECONDARY = (180, 180, 180)
        COLOR_ACCENT_ORANGE = (255, 150, 50)
        COLOR_ACCENT_GREEN = (50, 255, 150)
        COLOR_CRITICAL = (255, 70, 70)
        COLOR_WARNING = (255, 180, 50)

        screen = self.screen
        fonts = get_fonts(screen)
        w, h = screen.get_size()

        start_time = time.time()
        clock = pygame.time.Clock()

        # 3 views that cycle every 4 seconds
        views = [
            {
                'name': 'ACTIVE INCIDENT',
                'call': {
                    'type': 'CARDIAC EVENT',
                    'caller': 'Male, 68 years old',
                    'condition': 'Chest pain, difficulty breathing',
                    'location': '1847 Beacon St, Boston MA',
                    'coordinates': '42.3601 N, 71.0589 W',
                    'confidence': 94,
                    'severity': 'CRITICAL'
                },
                'alerts': [
                    ('Respiratory distress detected', COLOR_CRITICAL),
                    ('Possible MI (myocardial infarction)', COLOR_CRITICAL),
                    ('AMB-01 dispatched — ETA: 4m 12s', COLOR_ACCENT_ORANGE),
                    ('AED available at location', COLOR_ACCENT_GREEN),
                    ('Nearest hospital: 2.8 mi', COLOR_TEXT_SECONDARY)
                ]
            },
            {
                'name': 'RESPONDER STATUS',
                'call': {
                    'type': 'UNIT DEPLOYMENT',
                    'caller': 'AMB-01 En Route',
                    'condition': 'Active navigation to scene',
                    'location': 'Commonwealth Ave → Beacon St',
                    'coordinates': 'Current: 42.3512 N, 71.0693 W',
                    'confidence': 100,
                    'severity': 'DISPATCHED'
                },
                'alerts': [
                    ('GPS tracking active', COLOR_ACCENT_GREEN),
                    ('AR overlay enabled on HUD', COLOR_ACCENT_GREEN),
                    ('Building access codes sent', COLOR_ACCENT_GREEN),
                    ('Traffic route optimized', COLOR_ACCENT_ORANGE),
                    ('ETA updated: 3m 48s', COLOR_TEXT_PRIMARY)
                ]
            },
            {
                'name': 'MEDICAL AI RECOMMENDATIONS',
                'call': {
                    'type': 'AI TRIAGE ANALYSIS',
                    'caller': 'Medical Protocol ML-4',
                    'condition': 'Pattern recognition complete',
                    'location': 'System-wide scan: Boston Metro',
                    'coordinates': 'Coverage: 47 square miles',
                    'confidence': 89,
                    'severity': 'HIGH RISK'
                },
                'alerts': [
                    ('Administer aspirin if conscious', COLOR_CRITICAL),
                    ('Prepare AED immediately', COLOR_CRITICAL),
                    ('Monitor O₂ saturation continuously', COLOR_WARNING),
                    ('Consider nitroglycerin if BP stable', COLOR_WARNING),
                    ('Hospital pre-alert sent', COLOR_ACCENT_GREEN)
                ]
            }
        ]

        # Ticker messages
        ticker_items = [
            "Unit 3 dispatched",
            "EKG streaming active",
            "Oxygen levels: 89% (falling)",
            "ETA: 3m 18s",
            "Traffic reroute in progress",
            "Hospital ER notified",
            "Backup unit on standby",
            "Family contact established"
        ]
        ticker_text = " · ".join(ticker_items) + " · "

        # For SPACE key overlay
        show_overlay = False
        overlay_start_time = 0

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return
                    if event.key == pygame.K_SPACE:
                        show_overlay = True
                        overlay_start_time = time.time()

            elapsed = time.time() - start_time

            # Auto-cycle through views every 4 seconds
            view_index = int(elapsed / 4) % len(views)
            current_view = views[view_index]

            # Draw background
            draw_background(screen, elapsed)

            # Draw header
            draw_header(
                screen, fonts, 'emergency',
                '🚨 EMERGENCY RESPONSE',
                '🚑 911 Dispatch · ⚠️ Crisis Management · 🏥 Medical AI',
                accent_color, "● LIVE"
            )

            # === MIDDLE BAND: Two-column critical info ===
            y_top = 200
            margin = 80
            col_gap = 60
            col_width = (w - 2 * margin - col_gap) // 2

            # LEFT COLUMN: BIG CALL SUMMARY
            left_x = margin
            left_y = y_top

            call = current_view['call']

            # View name indicator
            view_label = fonts['body'].render(current_view['name'], True, COLOR_TEXT_SECONDARY)
            screen.blit(view_label, (left_x, left_y))
            left_y += 70

            # Type in HUGE font
            type_surf = fonts['huge'].render(call['type'], True, accent_color)
            screen.blit(type_surf, (left_x, left_y))
            left_y += 140

            # Caller
            caller_label = fonts['small'].render("CALLER:", True, COLOR_TEXT_SECONDARY)
            screen.blit(caller_label, (left_x, left_y))
            left_y += 45
            caller_surf = fonts['body'].render(call['caller'], True, COLOR_TEXT_PRIMARY)
            screen.blit(caller_surf, (left_x, left_y))
            left_y += 70

            # Condition
            cond_label = fonts['small'].render("CONDITION:", True, COLOR_TEXT_SECONDARY)
            screen.blit(cond_label, (left_x, left_y))
            left_y += 45
            cond_surf = fonts['body'].render(call['condition'], True, COLOR_TEXT_PRIMARY)
            screen.blit(cond_surf, (left_x, left_y))
            left_y += 70

            # Location
            loc_label = fonts['small'].render("LOCATION:", True, COLOR_TEXT_SECONDARY)
            screen.blit(loc_label, (left_x, left_y))
            left_y += 45
            loc_surf = fonts['body'].render(call['location'], True, COLOR_TEXT_PRIMARY)
            screen.blit(loc_surf, (left_x, left_y))
            left_y += 60
            coord_surf = fonts['small'].render(call['coordinates'], True, COLOR_TEXT_SECONDARY)
            screen.blit(coord_surf, (left_x, left_y))
            left_y += 80

            # Confidence & Severity
            conf_text = f"CONFIDENCE: {call['confidence']}%"
            conf_surf = fonts['body'].render(conf_text, True, COLOR_ACCENT_GREEN if call['confidence'] >= 90 else COLOR_WARNING)
            screen.blit(conf_surf, (left_x, left_y))
            left_y += 70

            # Severity in large font with color coding
            severity_color = COLOR_CRITICAL if call['severity'] in ['CRITICAL', 'HIGH RISK'] else COLOR_WARNING
            sev_surf = fonts['header'].render(call['severity'], True, severity_color)
            screen.blit(sev_surf, (left_x, left_y))

            # RIGHT COLUMN: LARGE ALERTS PANEL with glowing edges
            right_x = left_x + col_width + col_gap
            right_y = y_top

            # Alert panel header
            alert_header = fonts['header'].render("ALERTS", True, accent_color)
            screen.blit(alert_header, (right_x, right_y))
            right_y += 100

            # Draw alerts with glowing edge effect
            panel_x = right_x - 20
            panel_y = right_y - 20
            panel_w = col_width + 40
            panel_h = 500

            # Glowing border effect (multiple layers)
            for i in range(5, 0, -1):
                glow_alpha = 20 - (i * 3)
                glow_surf = pygame.Surface((panel_w + i*4, panel_h + i*4), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*accent_color, glow_alpha), (0, 0, panel_w + i*4, panel_h + i*4), border_radius=8)
                screen.blit(glow_surf, (panel_x - i*2, panel_y - i*2))

            # Panel background
            panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_bg, (20, 20, 30, 180), (0, 0, panel_w, panel_h), border_radius=8)
            pygame.draw.rect(panel_bg, (*accent_color, 100), (0, 0, panel_w, panel_h), width=2, border_radius=8)
            screen.blit(panel_bg, (panel_x, panel_y))

            # Alert items
            for i, (alert_text, alert_color) in enumerate(current_view['alerts']):
                alert_y = right_y + i * 85

                # Alert bullet
                bullet_x = right_x
                bullet_y = alert_y + 20
                pygame.draw.circle(screen, alert_color, (bullet_x, bullet_y), 8)

                # Alert text
                alert_surf = fonts['body'].render(alert_text, True, alert_color)
                screen.blit(alert_surf, (right_x + 25, alert_y))

            # Draw footer ticker
            seconds_left = int(duration - elapsed)
            draw_footer_ticker(
                screen, fonts,
                mode_label="OPS MODE",
                seconds_remaining=seconds_left,
                realm_id="EMERGENCY",
                accent_color=accent_color,
                ticker_text=ticker_text,
                elapsed=elapsed
            )

            # NEW EMERGENCY CALL OVERLAY (triggered by SPACE)
            if show_overlay and (time.time() - overlay_start_time < 2.5):
                # Fast slide-in animation
                overlay_elapsed = time.time() - overlay_start_time
                slide_progress = min(1.0, overlay_elapsed / 0.3)  # 0.3s slide-in

                # Ease-out animation
                slide_offset = int((1 - slide_progress) * w)

                # Overlay dimensions
                overlay_w = 800
                overlay_h = 400
                overlay_x = (w - overlay_w) // 2 + slide_offset
                overlay_y = (h - overlay_h) // 2

                # Dark background
                overlay_bg = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
                pygame.draw.rect(overlay_bg, (10, 10, 20, 240), (0, 0, overlay_w, overlay_h), border_radius=12)
                pygame.draw.rect(overlay_bg, (*accent_color, 200), (0, 0, overlay_w, overlay_h), width=4, border_radius=12)
                screen.blit(overlay_bg, (overlay_x, overlay_y))

                # Pulsing "NEW CALL" header
                pulse = 0.8 + 0.2 * math.sin(overlay_elapsed * 8)
                pulse_color = tuple(int(c * pulse) for c in accent_color)

                new_call_surf = fonts['title'].render("🚨 NEW EMERGENCY CALL", True, pulse_color)
                new_call_x = overlay_x + (overlay_w - new_call_surf.get_width()) // 2
                screen.blit(new_call_surf, (new_call_x, overlay_y + 40))

                # Call details
                details_y = overlay_y + 140
                detail_lines = [
                    "Type: Structure Fire",
                    "Location: 324 Cambridge St",
                    "Severity: HIGH",
                    "Units Required: 2 engines, 1 ladder"
                ]
                for line in detail_lines:
                    detail_surf = fonts['body'].render(line, True, COLOR_TEXT_PRIMARY)
                    detail_x = overlay_x + (overlay_w - detail_surf.get_width()) // 2
                    screen.blit(detail_surf, (detail_x, details_y))
                    details_y += 60

            else:
                show_overlay = False

            pygame.display.flip()
            clock.tick(30)


