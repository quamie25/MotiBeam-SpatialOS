"""
MotiBeam Spatial OS - Security & Surveillance Realm
Perimeter Defense, Access Control, Threat Detection
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class SecurityRealm(SpatialRealm):
    """Security, surveillance, and access control realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Security & Surveillance Realm",
            realm_description="Perimeter Defense, Access Control, Threat Detection"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.security_zones = []
        self.access_points = []
        self.detected_threats = []

    def initialize(self) -> bool:
        """Initialize security systems"""
        print("  🛡️  Initializing Security & Surveillance Systems...")

        # Initialize spatial security mapping
        scan = self.spatial_engine.scan_environment("security_perimeter")
        print(f"  ✓ Security perimeter mapped: {scan['room_dimensions']}")

        # Establish secure mesh network
        self.beam_network.establish_mesh("Security Operations")

        # Initialize security zones
        self.security_zones = [
            {"id": "ZONE-A", "name": "Main Entrance", "level": "Public", "cameras": 4},
            {"id": "ZONE-B", "name": "Server Room", "level": "Restricted", "cameras": 8},
            {"id": "ZONE-C", "name": "Executive Floor", "level": "High Security", "cameras": 12},
            {"id": "ZONE-D", "name": "Perimeter", "level": "Monitored", "cameras": 16}
        ]

        print("  ✓ Security systems armed and ready")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate security and surveillance capabilities"""
        self.display_header()

        print("\n🎥 MULTI-ZONE SURVEILLANCE ACTIVE")
        print("  Cameras online: 40")
        print("  AI-powered analysis: ENABLED")
        print("  Facial recognition: ACTIVE")
        print("  Behavior anomaly detection: MONITORING")
        time.sleep(1)

        # Perimeter monitoring
        print("\n🌐 SPATIAL PERIMETER MONITORING")
        scan = self.spatial_engine.scan_environment("perimeter")
        print(f"  Zone coverage: 360° panoramic")
        print(f"  Objects tracked: {scan['objects_detected']}")
        print(f"  Personnel detected: {scan['people_detected']}")
        time.sleep(1)

        # Anomaly detection
        print("\n⚠️  ANOMALY DETECTED")
        print("  Location: Loading Dock (ZONE-D)")
        print("  Event: Unauthorized access attempt")
        print("  Time: " + datetime.now().strftime("%H:%M:%S"))
        time.sleep(1)

        self.simulate_ai_processing("Facial recognition and behavior analysis")
        print("  🔍 Subject: Unknown individual")
        print("  📊 Behavior score: 73/100 (Suspicious)")
        print("  🎯 Threat level: MODERATE")
        time.sleep(1)

        # AR-enhanced surveillance
        print("\n🔮 AR-ENHANCED SURVEILLANCE")
        self.spatial_engine.create_ar_overlay("Subject tracking overlay", "security_HUD")
        print("  ✓ Real-time subject tracking enabled")
        print("  ✓ Movement prediction: 85% confidence")
        print("  ✓ Security team alerted")
        time.sleep(1)

        # Access control
        print("\n🚪 INTELLIGENT ACCESS CONTROL")
        print("  Event: Badge scan at Server Room entrance")
        self.simulate_ai_processing("Multi-factor authentication verification")
        print("  ✓ Badge: VALID (Employee ID: E-7842)")
        print("  ✓ Biometric: MATCH (Fingerprint)")
        print("  ✓ Location context: APPROVED")
        print("  ✓ Time-based access: AUTHORIZED")
        print("  → Access GRANTED")
        time.sleep(1)

        # Predictive security
        print("\n🔮 PREDICTIVE SECURITY ANALYSIS")
        self.simulate_ai_processing("Pattern analysis across security logs")
        print("  📊 Insights:")
        print("    • Peak traffic: 09:00-09:30, 17:30-18:00")
        print("    • Anomaly clusters: Loading dock (Wed-Fri evenings)")
        print("    • Recommendation: Deploy additional cameras at dock area")
        print("    • Predicted risk reduction: 34%")
        time.sleep(1)

        # Threat response
        print("\n✅ AUTOMATED THREAT RESPONSE")
        print("  • Loading dock intruder: Security team dispatched")
        print("  • Zone D lighting: Increased to 100%")
        print("  • Warning broadcast: Issued to subject")
        print("  • Law enforcement: Notified (standby)")
        print("  • Incident logged for pattern analysis")

    def get_status(self) -> dict:
        """Get security realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "security_zones": len(self.security_zones),
            "active_threats": len(self.detected_threats),
            "mesh_strength": self.beam_network.mesh_strength
        }

    def scan_zone(self, zone_id: str) -> dict:
        """Scan specific security zone"""
        return {
            "zone": zone_id,
            "status": "clear",
            "occupancy": random.randint(0, 10),
            "last_scan": datetime.now()
        }

    def run(self, duration=12):
        """Run Security & Surveillance command wall HUD"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import (
            get_fonts, draw_background, draw_header,
            draw_footer_ticker, REALM_COLORS
        )

        # Security blue/cyan accent
        accent_color = REALM_COLORS.get('security', (50, 180, 255))
        COLOR_TEXT_PRIMARY = (240, 240, 240)
        COLOR_TEXT_SECONDARY = (180, 180, 180)
        COLOR_THREAT_LOW = (50, 255, 150)
        COLOR_THREAT_MED = (255, 200, 50)
        COLOR_THREAT_HIGH = (255, 150, 50)
        COLOR_THREAT_CRITICAL = (255, 70, 70)

        screen = self.screen
        fonts = get_fonts(screen)
        w, h = screen.get_size()

        start_time = time.time()
        clock = pygame.time.Clock()

        # 3 views that cycle every 4 seconds
        views = [
            {
                'name': 'THREAT SNAPSHOT',
                'threat': {
                    'headline': 'UNAUTHORIZED ACCESS – LOADING DOCK',
                    'location': 'ZONE D · Loading Dock · East Entrance',
                    'subject': 'Male, approx. 35 years old, no badge visible',
                    'behavior_score': 73,
                    'threat_level': 'MODERATE',
                    'threat_color': COLOR_THREAT_MED
                },
                'zones': [
                    ('ZONE A', 'Main Entrance', 'CLEAR', COLOR_THREAT_LOW),
                    ('ZONE D', 'Loading Dock', 'INVESTIGATING', COLOR_THREAT_MED),
                    ('ZONE F', 'Parking Lot', 'CLEAR', COLOR_THREAT_LOW),
                    ('ZONE B', 'Server Room', 'SECURED', COLOR_THREAT_LOW)
                ]
            },
            {
                'name': 'ACCESS LOGS',
                'threat': {
                    'headline': 'RECENT ACCESS ACTIVITY',
                    'location': 'System-wide · Last 5 minutes',
                    'subject': '12 badge swipes · 3 door openings · 1 denial',
                    'behavior_score': 98,
                    'threat_level': 'LOW',
                    'threat_color': COLOR_THREAT_LOW
                },
                'zones': [
                    ('08:47:23', 'Badge E-7842 · Server Room', 'GRANTED', COLOR_THREAT_LOW),
                    ('08:45:12', 'Badge E-5501 · Main Entrance', 'GRANTED', COLOR_THREAT_LOW),
                    ('08:43:08', 'Unknown badge · Loading Dock', 'DENIED', COLOR_THREAT_HIGH),
                    ('08:41:55', 'Badge E-9234 · Parking Access', 'GRANTED', COLOR_THREAT_LOW)
                ]
            },
            {
                'name': 'CAMERA FOCUS',
                'threat': {
                    'headline': 'CAMERA 07 – ZONE D – ACTIVE TRACKING',
                    'location': 'Loading Dock · Southeast Corner',
                    'subject': 'Zoomed on subject · AI-enhanced clarity',
                    'behavior_score': 73,
                    'threat_level': 'MODERATE',
                    'threat_color': COLOR_THREAT_MED
                },
                'zones': [
                    ('CAM 07', 'Loading Dock · Southeast', 'TRACKING', COLOR_THREAT_MED),
                    ('CAM 14', 'Loading Dock · Northwest', 'NIGHT VISION', accent_color),
                    ('CAM 22', 'Parking Lot · Overview', 'MONITORING', COLOR_THREAT_LOW),
                    ('CAM 03', 'Main Entrance · Front', 'MONITORING', COLOR_THREAT_LOW)
                ]
            }
        ]

        # Ticker messages
        ticker_items = [
            "Camera 14 switched to night vision",
            "Badge swipe failure ZONE D",
            "Patrol unit en route",
            "Face match: No records",
            "AI confidence: 85%",
            "Zone D lighting: 100%",
            "Security team: ETA 2m",
            "All other zones: CLEAR"
        ]
        ticker_text = " · ".join(ticker_items) + " · "

        # For manual view switching
        current_view_index = 0
        last_space_time = 0

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return
                    if event.key == pygame.K_SPACE:
                        # Manual jump to next view
                        now = time.time()
                        if now - last_space_time > 0.5:  # Debounce
                            current_view_index = (current_view_index + 1) % len(views)
                            last_space_time = now

            elapsed = time.time() - start_time

            # Auto-cycle through views every 4 seconds (unless manually overridden)
            if time.time() - last_space_time > 4:
                current_view_index = int(elapsed / 4) % len(views)

            current_view = views[current_view_index]

            # Draw background
            draw_background(screen, elapsed)

            # Draw header
            draw_header(
                screen, fonts, 'security',
                '[S] SECURITY & SURVEILLANCE',
                'Perimeter Defense · Access Control · Threat Detection',
                accent_color, "● ACTIVE"
            )

            # === MAIN BODY: Two-column layout ===
            y_top = 200
            margin = 80
            col_gap = 80
            left_width = int((w - 2 * margin - col_gap) * 0.65)
            right_width = int((w - 2 * margin - col_gap) * 0.35)

            # LEFT COLUMN (65%): THREAT OVERVIEW
            left_x = margin
            left_y = y_top

            threat = current_view['threat']

            # View name indicator
            view_label = fonts['small'].render(current_view['name'], True, COLOR_TEXT_SECONDARY)
            screen.blit(view_label, (left_x, left_y))
            left_y += 55

            # Panel title
            panel_title = fonts['header'].render("CURRENT THREAT SNAPSHOT", True, accent_color)
            screen.blit(panel_title, (left_x, left_y))
            left_y += 100

            # BIG HEADLINE (80-100px font - use 'title' which is 80px)
            # Split headline into lines if needed
            headline_words = threat['headline'].split()
            if len(' '.join(headline_words)) > 30:
                # Try to split into 2 lines
                mid = len(headline_words) // 2
                line1 = ' '.join(headline_words[:mid])
                line2 = ' '.join(headline_words[mid:])

                headline1_surf = fonts['title'].render(line1, True, threat['threat_color'])
                screen.blit(headline1_surf, (left_x, left_y))
                left_y += 90

                headline2_surf = fonts['title'].render(line2, True, threat['threat_color'])
                screen.blit(headline2_surf, (left_x, left_y))
                left_y += 110
            else:
                headline_surf = fonts['title'].render(threat['headline'], True, threat['threat_color'])
                screen.blit(headline_surf, (left_x, left_y))
                left_y += 110

            # Bullet points
            bullet_spacing = 75

            # Location
            loc_label = fonts['small'].render("LOCATION:", True, COLOR_TEXT_SECONDARY)
            screen.blit(loc_label, (left_x, left_y))
            left_y += 42
            pygame.draw.circle(screen, accent_color, (left_x, left_y + 15), 6)
            loc_surf = fonts['body'].render(threat['location'], True, COLOR_TEXT_PRIMARY)
            screen.blit(loc_surf, (left_x + 20, left_y))
            left_y += bullet_spacing

            # Subject
            subj_label = fonts['small'].render("SUBJECT:", True, COLOR_TEXT_SECONDARY)
            screen.blit(subj_label, (left_x, left_y))
            left_y += 42
            pygame.draw.circle(screen, accent_color, (left_x, left_y + 15), 6)
            subj_surf = fonts['body'].render(threat['subject'], True, COLOR_TEXT_PRIMARY)
            screen.blit(subj_surf, (left_x + 20, left_y))
            left_y += bullet_spacing

            # Behavior score
            behav_label = fonts['small'].render("BEHAVIOR SCORE:", True, COLOR_TEXT_SECONDARY)
            screen.blit(behav_label, (left_x, left_y))
            left_y += 42
            pygame.draw.circle(screen, accent_color, (left_x, left_y + 15), 6)

            # Score with color coding
            score_text = f"{threat['behavior_score']}/100"
            if threat['behavior_score'] >= 80:
                score_color = COLOR_THREAT_LOW
                score_desc = "Normal"
            elif threat['behavior_score'] >= 60:
                score_color = COLOR_THREAT_MED
                score_desc = "Suspicious"
            else:
                score_color = COLOR_THREAT_HIGH
                score_desc = "Highly Suspicious"

            score_surf = fonts['body'].render(f"{score_text} – {score_desc}", True, score_color)
            screen.blit(score_surf, (left_x + 20, left_y))
            left_y += bullet_spacing

            # Threat level
            threat_label = fonts['small'].render("THREAT LEVEL:", True, COLOR_TEXT_SECONDARY)
            screen.blit(threat_label, (left_x, left_y))
            left_y += 42
            pygame.draw.circle(screen, threat['threat_color'], (left_x, left_y + 15), 6)
            threat_surf = fonts['header'].render(threat['threat_level'], True, threat['threat_color'])
            screen.blit(threat_surf, (left_x + 20, left_y))

            # RIGHT COLUMN (35%): LIVE ZONES
            right_x = left_x + left_width + col_gap
            right_y = y_top

            # Zones header
            zones_header = fonts['header'].render("LIVE ZONES", True, accent_color)
            screen.blit(zones_header, (right_x, right_y))
            right_y += 100

            # Zone bars
            for zone_id, zone_name, status, status_color in current_view['zones']:
                # Bar background
                bar_height = 90
                bar_y = right_y

                # Highlight non-clear zones
                if status not in ['CLEAR', 'SECURED', 'MONITORING', 'GRANTED']:
                    # Glowing background for active zones
                    glow_surf = pygame.Surface((right_width + 10, bar_height + 10), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*status_color, 40), (0, 0, right_width + 10, bar_height + 10), border_radius=6)
                    screen.blit(glow_surf, (right_x - 5, bar_y - 5))

                # Bar
                bar_surf = pygame.Surface((right_width, bar_height), pygame.SRCALPHA)
                pygame.draw.rect(bar_surf, (20, 25, 35, 200), (0, 0, right_width, bar_height), border_radius=6)
                pygame.draw.rect(bar_surf, (*status_color, 150), (0, 0, right_width, bar_height), width=2, border_radius=6)
                screen.blit(bar_surf, (right_x, bar_y))

                # Zone text
                zone_id_surf = fonts['body'].render(zone_id, True, status_color)
                screen.blit(zone_id_surf, (right_x + 15, bar_y + 10))

                zone_name_surf = fonts['small'].render(zone_name, True, COLOR_TEXT_SECONDARY)
                screen.blit(zone_name_surf, (right_x + 15, bar_y + 45))

                # Status text (right-aligned in bar)
                status_surf = fonts['small'].render(status, True, status_color)
                status_x = right_x + right_width - status_surf.get_width() - 15
                screen.blit(status_surf, (status_x, bar_y + 28))

                right_y += bar_height + 15

            # Draw footer ticker
            seconds_left = int(duration - elapsed)
            draw_footer_ticker(
                screen, fonts,
                mode_label="OPS MODE",
                seconds_remaining=seconds_left,
                realm_id="SECURITY",
                accent_color=accent_color,
                ticker_text=ticker_text,
                elapsed=elapsed
            )

            pygame.display.flip()
            clock.tick(30)


