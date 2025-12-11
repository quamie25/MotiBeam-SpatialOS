"""
MotiBeam Spatial OS - Maritime Operations Realm
Vessel Navigation, Port Operations, Marine Safety Systems
"""

import random
import time
from datetime import datetime
from core.base_realm import SpatialRealm
from core.spatial_engine import SpatialEngine, BeamNetworkProtocol
from core.global_state import global_state

import pygame


class MaritimeRealm(SpatialRealm):
    """Maritime navigation and port operations realm"""

    def __init__(self, screen=None, global_state_ref=None, standalone=False, **kwargs):
        super().__init__(
            realm_name="Maritime Operations Realm",
            realm_description="Vessel Navigation, Port Operations, Marine Safety"
        )
        self.screen = screen
        self.global_state = global_state_ref if global_state_ref is not None else global_state
        self.standalone = standalone
        self.spatial_engine = SpatialEngine()
        self.beam_network = BeamNetworkProtocol()
        self.active_vessels = []
        self.port_berths = []
        self.sea_conditions = {}

    def initialize(self) -> bool:
        """Initialize maritime operations systems"""
        print("  ⚓ Initializing Maritime Operations Systems...")

        # Initialize maritime spatial domain
        scan = self.spatial_engine.scan_environment("port_waters")
        print(f"  ✓ Port waters mapped: {scan['room_dimensions']}")

        # Establish maritime mesh network
        self.beam_network.establish_mesh("Maritime Network")

        # Initialize vessel traffic
        self.active_vessels = [
            {"imo": "IMO9641766", "name": "MSC MARINA", "type": "Container", "length": 366, "status": "Inbound"},
            {"imo": "IMO9337626", "name": "CARNIVAL GLORY", "type": "Cruise", "length": 290, "status": "Docked"},
            {"imo": "IMO9245829", "name": "NORDIC AURORA", "type": "Tanker", "length": 228, "status": "Outbound"},
            {"imo": "IMO9458891", "name": "COASTAL TRADER", "type": "Cargo", "length": 185, "status": "Anchored"}
        ]

        print("  ✓ Maritime systems operational")
        return True

    def run_demo_cycle(self) -> None:
        """Demonstrate maritime operations capabilities"""
        self.display_header()

        print("\n🌊 PORT OPERATIONS CENTER")
        print("  Location: Port of Boston")
        print("  Active vessels: 42")
        print("  Berths occupied: 12/18")
        print("  Tide: High tide +2.3m at 14:45")
        time.sleep(1)

        # Spatial vessel tracking
        print("\n🛸 3D MARITIME SPATIAL TRACKING")
        print("  Vessel traffic:")
        for vessel in self.active_vessels[:4]:
            print(f"    • {vessel['name']}: {vessel['type']} ({vessel['length']}m) - {vessel['status']}")
        time.sleep(1)

        # Navigation assistance
        print("\n🧭 AUTONOMOUS NAVIGATION ASSISTANCE")
        print("  Vessel: MSC MARINA (inbound)")
        print("  Current position: 42.3251° N, 70.9812° W")
        print("  Distance to berth: 3.2 nautical miles")
        time.sleep(1)

        self.simulate_ai_processing("Optimal approach vector calculation")
        print("  🎯 Navigation plan:")
        print("    • Course: 285° True")
        print("    • Speed: Reduce to 8 knots")
        print("    • Pilot pickup: Station Alpha (1.2 nm)")
        print("    • Berth assignment: Terminal 5, Berth B")
        print("    • Tugs required: 2 (pre-positioned)")
        print("  ✓ Route transmitted to vessel navigation system")
        time.sleep(1)

        # Collision avoidance
        print("\n⚠️  COLLISION AVOIDANCE SYSTEM")
        print("  Alert: Potential crossing situation")
        print("  Vessels: MSC MARINA & NORDIC AURORA")
        print("  CPA: 0.4 nm in 8 minutes (UNSAFE)")
        time.sleep(1)

        self.simulate_ai_processing("Traffic separation scheme analysis")
        print("  ✓ Resolution:")
        print("    • MSC MARINA: Maintain course and speed")
        print("    • NORDIC AURORA: Alter course 15° starboard")
        print("    • New CPA: 1.2 nm (SAFE)")
        print("  ✓ VHF radio advisory transmitted")
        print("  ✓ AIS navigation data updated")
        time.sleep(1)

        # AR bridge integration
        print("\n🔮 AR-ENHANCED BRIDGE SYSTEMS")
        self.spatial_engine.create_ar_overlay("360° navigation overlay", "bridge_HUD")
        print("  ✓ Holographic chart overlay active")
        print("  ✓ Traffic targets rendered in 3D space")
        print("  ✓ Depth contours visualized")
        print("  ✓ Weather cells overlaid on horizon")
        print("  ✓ Navigational aids highlighted")
        time.sleep(1)

        # Weather routing
        print("\n🌦️  INTELLIGENT WEATHER ROUTING")
        print("  Voyage: Boston → Rotterdam (3,200 nm)")
        self.simulate_ai_processing("Ocean weather analysis and route optimization")
        print("  Route analysis:")
        print("    • Standard route: 6.8 days, Force 8 gales expected")
        print("    • Optimized route: 7.1 days, max Force 6 winds")
        print("    • Fuel savings: 8.2 tons")
        print("    • Passenger comfort: +62%")
        print("  ✓ Recommended route loaded to ECDIS")
        time.sleep(1)

        # Port automation
        print("\n🏗️  AUTOMATED PORT OPERATIONS")
        print("  Event: MSC MARINA arriving at berth")
        self.simulate_ai_processing("Coordinating port resources and automation")
        print("  Automation sequence:")
        print("    ✓ Automated mooring system: READY")
        print("    ✓ Gantry cranes: Positioned (8 units)")
        print("    ✓ Container yard: Space allocated (450 TEU)")
        print("    ✓ Customs clearance: Pre-processed")
        print("    ✓ Bunker truck: Scheduled for 22:00")
        print("  → Estimated turnaround: 16 hours")
        time.sleep(1)

        # Environmental monitoring
        print("\n🌊 MARINE ENVIRONMENTAL MONITORING")
        print("  Sea state: 3 (Slight)")
        print("  Wave height: 1.2m")
        print("  Water temp: 12°C")
        print("  Visibility: 8 nm")
        print("  ✓ All vessels operating within safe parameters")

    def get_status(self) -> dict:
        """Get maritime realm status"""
        return {
            "realm": self.realm_name,
            "active": self.is_active,
            "active_vessels": len(self.active_vessels),
            "port_berths": len(self.port_berths),
            "mesh_strength": self.beam_network.mesh_strength
        }

    def track_vessel(self, imo_number: str) -> dict:
        """Track specific vessel"""
        return {
            "imo": imo_number,
            "position": (42.3251, -70.9812),
            "course": random.randint(0, 359),
            "speed": random.uniform(0, 15)
        }

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
                'title': 'PORT OPERATIONS CENTER',
                'items': [
                    "Location: Port of Boston",
                    "Active vessels: 42 tracked",
                    "Berths occupied: 12/18 available",
                    "MSC MARINA: Container (366m) - Inbound",
                    "CARNIVAL GLORY: Cruise (290m) - Docked"
                ]
            },
            {
                'title': 'COLLISION AVOIDANCE ACTIVE',
                'items': [
                    "Potential crossing: MSC MARINA & NORDIC AURORA",
                    "CPA: 0.4 nm in 8 minutes (UNSAFE)",
                    "MSC MARINA: Maintain course and speed",
                    "NORDIC AURORA: Alter 15 degrees starboard",
                    "New CPA: 1.2 nm (SAFE) - VHF advisory sent"
                ]
            },
            {
                'title': 'AR BRIDGE INTEGRATION',
                'items': [
                    "360 degree holographic navigation: ACTIVE",
                    "Traffic targets rendered in 3D space",
                    "Depth contours and weather visualized",
                    "Optimal weather routing: 8.2 tons fuel saved",
                    "Automated port ops: 16hr turnaround"
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
                realm_id='maritime',
                title='MARITIME OPERATIONS',
                subtitle='Vessel Navigation · Port Operations · Marine Safety',
                mode='Ops Mode',
                content_sections=content_sections,
                elapsed=elapsed,
                duration=duration
            )

            clock.tick(30)


