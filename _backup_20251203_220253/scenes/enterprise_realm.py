"""
MotiBeam Spatial OS - Enterprise Workspace Realm
Office Environments, Collaboration, Productivity Enhancement
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class EnterpriseRealm(SpatialRealm):
    """Enterprise workspace and collaboration realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Enterprise Workspace Realm",
            realm_description="Office Environments, Collaboration, Productivity Enhancement"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.meeting_rooms = []
        self.active_employees = []
        self.smart_devices = []

    def initialize(self) -> bool:
        """Initialize enterprise workspace systems"""
        print("  🏢 Initializing Enterprise Workspace Systems...")

        # Initialize spatial office mapping
        scan = self.spatial_engine.scan_environment("office_space")
        print(f"  ✓ Office space mapped: {scan['room_dimensions']}")

        # Establish enterprise mesh network
        self.beam_network.establish_mesh("Enterprise Network")

        # Initialize workspace resources
        self.meeting_rooms = [
            {"id": "CONF-A", "name": "Innovation Lab", "capacity": 12, "status": "Available"},
            {"id": "CONF-B", "name": "Boardroom", "capacity": 20, "status": "In Use"},
            {"id": "HUDDLE-1", "name": "Huddle Room 1", "capacity": 4, "status": "Available"},
            {"id": "FOCUS-POD", "name": "Focus Pod 3", "capacity": 1, "status": "Available"}
        ]

        print("  ✓ Enterprise systems online")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate enterprise workspace capabilities"""
        self.display_header()

        print("\n👥 INTELLIGENT WORKSPACE MANAGEMENT")
        print("  Employees present: 87")
        print("  Meeting rooms in use: 5/12")
        print("  Hot desks available: 23")
        print("  Environmental comfort: Optimal")
        time.sleep(1)

        # Spatial presence detection
        print("\n📍 SPATIAL PRESENCE & ACTIVITY MAPPING")
        scan = self.spatial_engine.scan_environment("floor_3")
        print(f"  Floor 3 occupancy: {scan['people_detected']} people")
        print(f"  Temperature: {scan['temperature']}")
        print(f"  Lighting: {scan['lighting']}")
        print("  ✓ Environmental controls auto-adjusting")
        time.sleep(1)

        # Smart meeting scheduling
        print("\n📅 AI-POWERED MEETING ORCHESTRATION")
        print("  Event: Team sync requested by Sarah Chen")
        self.simulate_ai_processing("Analyzing schedules, locations, and preferences")
        print("  🎯 Optimal solution found:")
        print("    • Time: Today, 14:30 (30 min)")
        print("    • Room: Innovation Lab (CONF-A)")
        print("    • Attendees: 6 available, 2 remote")
        print("    • Coffee service: Pre-ordered")
        print("  ✓ Invites sent, room reserved, AV configured")
        time.sleep(1)

        # AR collaboration
        print("\n🔮 AR-ENHANCED COLLABORATION")
        self.spatial_engine.create_ar_overlay("3D design review", "meeting_space")
        print("  ✓ Spatial holographic display activated")
        print("  ✓ Remote participants rendered as holograms")
        print("  ✓ Shared 3D workspace synchronized")
        print("  📊 Collaboration efficiency: +47% vs traditional video")
        time.sleep(1)

        # Productivity insights
        print("\n📊 PRODUCTIVITY & WELLNESS ANALYTICS")
        self.simulate_ai_processing("Analyzing workspace utilization patterns")
        print("  Insights:")
        print("    • Peak collaboration hours: 10:00-11:30")
        print("    • Focus time utilization: 78% optimal")
        print("    • Meeting efficiency score: 8.4/10")
        print("    • Recommended break time: 15:30 (based on activity)")
        time.sleep(1)

        # Smart resource allocation
        print("\n⚡ INTELLIGENT RESOURCE ALLOCATION")
        print("  Event: Surprise visit from 15 clients")
        self.simulate_ai_processing("Dynamic workspace reconfiguration")
        print("  ✓ Conference room auto-reserved")
        print("  ✓ Parking spots allocated (visitor lot)")
        print("  ✓ Catering ordered (dietary preferences matched)")
        print("  ✓ Welcome AR wayfinding activated")
        print("  ✓ Presentation materials loaded to room displays")
        time.sleep(1)

        # Environmental optimization
        print("\n🌡️  ENVIRONMENTAL WELLNESS OPTIMIZATION")
        print("  Monitoring:")
        print("    • Air quality: Excellent (PM2.5: 8 μg/m³)")
        print("    • CO₂ levels: 450 ppm (optimal)")
        print("    • Natural light: Maximized (blinds auto-adjusted)")
        print("    • Noise zones: Quiet areas protected")
        print("  ✓ Workspace wellness score: 94/100")

    def get_status(self) -> dict:
        """Get enterprise realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "meeting_rooms": len(self.meeting_rooms),
            "active_employees": len(self.active_employees),
            "mesh_strength": self.beam_network.mesh_strength
        }

    def book_meeting_room(self, room_id: str, duration: int) -> bool:
        """Book a meeting room"""
        print(f"  📅 Booking {room_id} for {duration} minutes")
        return True

    def run(self, duration=12):
        """Run pygame visual demo with unified Neon HUD theme"""
        if not self.screen:
            self.run_demo_cycle()
            return

        from scenes.theme_neon import render_realm_hud

        start_time = time.time()
        clock = pygame.time.Clock()

        # Define content sections that rotate over time
        content_sections = [
            {
                'title': 'INTELLIGENT WORKSPACE',
                'items': [
                    "Employees present: 87 across 3 floors",
                    "Meeting rooms: 5/12 in use",
                    "Hot desks available: 23 stations",
                    "Environmental comfort: Optimal",
                    "Adaptive lighting and climate control"
                ]
            },
            {
                'title': 'AI MEETING ORCHESTRATION',
                'items': [
                    "Team sync requested by Sarah Chen",
                    "Optimal time: Today, 14:30 (30 min)",
                    "Room: Innovation Lab (CONF-A)",
                    "6 attendees local, 2 remote holograms",
                    "Invites sent, AV configured, coffee ordered"
                ]
            },
            {
                'title': 'AR COLLABORATION ACTIVE',
                'items': [
                    "Spatial holographic display: ENABLED",
                    "Remote participants as real-time holograms",
                    "Shared 3D workspace synchronized",
                    "Collaboration efficiency: +47% vs video",
                    "Productivity and wellness optimized"
                ]
            }
        ]

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return

            elapsed = time.time() - start_time

            render_realm_hud(
                screen=self.screen,
                realm_id='enterprise',
                title='ENTERPRISE WORKSPACE',
                subtitle='Office Environments · Collaboration · Productivity AI',
                mode='Ops Mode',
                content_sections=content_sections,
                elapsed=elapsed,
                duration=duration
            )

            clock.tick(30)


