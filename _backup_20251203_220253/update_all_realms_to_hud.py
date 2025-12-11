#!/usr/bin/env python3
"""
Automated script to update all 9 realms with unified HUD design
Replaces run() methods while keeping existing logic intact
"""

import re
import os

# HUD run() method for each realm (keeps existing logic, adds HUD visual)
REALM_RUN_METHODS = {
    'home_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('home', (0, 255, 200))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "🏡", "HOME REALM",
                          "Smart Home · Family · Ambient Living", accent_color, "LIVE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "MORNING ROUTINE AUTOMATION", [
                    "✓ Sarah waking up detected (6:45 AM)",
                    "✓ Bedroom lights: Gradual warm-up",
                    "✓ Coffee maker: Brewing started",
                    "✓ Personalized news briefing ready"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "FAMILY PRESENCE & ACTIVITY", [
                    "👨 Dad: Home Office (Focus Mode)",
                    "👩 Mom: Kitchen (Meal Prep)",
                    "👧👦 Kids: Playroom (Active Play)",
                    "✓ 47 smart devices synchronized"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "ENERGY & SECURITY", [
                    "⚡ Solar: 6.8 kW generating",
                    "📊 Usage: 4.2 kW consuming",
                    "💰 Net: +2.6 kW to grid",
                    "🔐 All zones secured · No alerts"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Consumer Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'clinical_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('clinical', (100, 255, 180))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "⚕️", "CLINICAL REALM",
                          "Health Monitoring · Wellness · Medical AI", accent_color, "LIVE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "CONTINUOUS VITAL MONITORING", [
                    "💓 Heart Rate: 68 bpm (Normal)",
                    "🩸 Blood Pressure: 118/76 mmHg (Optimal)",
                    "🫁 SpO2: 98% (Excellent)",
                    "😴 Sleep Score: 87/100"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "ACTIVITY & FITNESS TRACKING", [
                    "🏃 Steps: 8,240 / 10,000 (82%)",
                    "⏱️ Active Minutes: 45 min",
                    "🔥 Calories: 420 kcal burned",
                    "✓ On track to meet daily goals"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "PREDICTIVE HEALTH AI", [
                    "⚠️ Irregular sleep pattern (3 days)",
                    "📊 Recommend: Earlier bedtime 10:30 PM",
                    "🎯 Predicted improvement: +8% wellness",
                    "💊 Medication reminder: 8:00 PM today"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Consumer Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'education_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('education', (160, 100, 255))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "📚", "EDUCATION REALM",
                          "Adaptive Learning · Focus · Knowledge AI", accent_color, "LIVE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "ADAPTIVE LEARNING SESSION", [
                    "🎯 Student: Alex (Calculus)",
                    "📖 Topic: Integration by parts",
                    "🧠 Comprehension: 73% (Good)",
                    "✓ Difficulty auto-adjusted to Advanced"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "FOCUS ENVIRONMENT OPTIMIZATION", [
                    "💡 Lighting: Focus mode (cool white)",
                    "🔇 Noise cancellation: Active",
                    "📵 Distractions: 12 notifications blocked",
                    "⏱️ Pomodoro: 22 min remaining"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "LEARNING ANALYTICS & INSIGHTS", [
                    "✓ Differential equations: 92% mastery",
                    "✓ Linear algebra: 88% mastery",
                    "📊 Integration techniques: 65% (practice)",
                    "🎓 Personalized practice set ready"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Consumer Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'transport_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('transport', (0, 240, 220))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "🚗", "TRANSPORT REALM",
                          "Automotive HUD · Navigation · Driver AI", accent_color, "LIVE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "AR NAVIGATION HUD", [
                    "🗺️ Destination: 123 Main St, Boston",
                    "📍 Distance: 12.3 miles",
                    "⏱️ ETA: 18 minutes",
                    "✓ AR arrows on windshield active"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "INTELLIGENT SAFETY SYSTEMS", [
                    "✓ Forward collision: Clear",
                    "⚠️ Blind spot left: Vehicle detected",
                    "✓ Pedestrian detection: Active",
                    "🛡️ Auto-brake ready (55 mph)"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "PREDICTIVE TRAFFIC AI", [
                    "🚧 Accident detected on Route 93",
                    "📊 Impact: +12 min delay avoided",
                    "✓ Alternate route via I-90",
                    "🔋 Battery: 87% (240 mi range)"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Consumer Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'emergency_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('emergency', (255, 80, 100))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "🚨", "EMERGENCY RESPONSE",
                          "911 Dispatch · Crisis Management · Medical AI", accent_color, "CRITICAL")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "INCOMING 911 CALL", [
                    "📞 Elderly male, chest pain",
                    "📍 Boston, MA (42.3601° N)",
                    "🎯 Priority: CRITICAL - Cardiac event",
                    "📊 AI Confidence: 94%"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "RESOURCE ALLOCATION", [
                    "🚑 AMB-01 dispatched (ETA: 3m 45s)",
                    "🚒 FIRE-02 backup (ETA: 4m 12s)",
                    "📡 AR navigation → responders",
                    "✓ Building access codes sent"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "INCIDENT RESOLUTION", [
                    "✓ Paramedics arrived: 3m 28s",
                    "✓ Patient stabilized on-scene",
                    "✓ En route to hospital",
                    "✓ Incident logged for AI learning"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Operations Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'security_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('security', (0, 180, 255))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "🛡️", "SECURITY REALM",
                          "Surveillance · Access Control · Threat Detection", accent_color, "ARMED")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "MULTI-ZONE SURVEILLANCE", [
                    "📹 Cameras online: 40",
                    "🎥 AI-powered analysis: ACTIVE",
                    "👤 Facial recognition: ENABLED",
                    "🔍 Behavior anomaly detection: ON"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "ANOMALY DETECTED", [
                    "⚠️ Location: Loading Dock (ZONE-D)",
                    "🔍 Subject: Unknown individual",
                    "📊 Behavior score: 73/100 (Suspicious)",
                    "✓ Security team alerted"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "AUTOMATED RESPONSE", [
                    "✓ Loading dock: Security dispatched",
                    "✓ Zone D lighting: Increased to 100%",
                    "✓ Warning broadcast: Issued",
                    "✓ Incident logged for analysis"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Operations Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'enterprise_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('enterprise', (100, 200, 255))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "🏢", "ENTERPRISE REALM",
                          "Office · Collaboration · Productivity AI", accent_color, "ACTIVE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "INTELLIGENT WORKSPACE", [
                    "👥 Employees present: 87",
                    "📅 Meeting rooms in use: 5/12",
                    "🖥️ Hot desks available: 23",
                    "🌡️ Environmental comfort: Optimal"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "AI MEETING ORCHESTRATION", [
                    "📅 Team sync requested by Sarah",
                    "⏰ Time: Today, 14:30 (30 min)",
                    "🏠 Room: Innovation Lab (CONF-A)",
                    "✓ Invites sent, AV configured"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "PRODUCTIVITY INSIGHTS", [
                    "📊 Peak collaboration: 10:00-11:30",
                    "🎯 Focus time utilization: 78%",
                    "⭐ Meeting efficiency: 8.4/10",
                    "✓ Workspace wellness: 94/100"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Operations Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'aviation_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('aviation', (0, 200, 255))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "✈️", "AVIATION REALM",
                          "ATC · Flight Safety · Navigation AI", accent_color, "AIRBORNE")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "AIR TRAFFIC CONTROL", [
                    "🛫 Sector: Boston ARTCC (ZBW)",
                    "✈️ Active flights: 127",
                    "🌐 Airspace: Class A (FL180-FL600)",
                    "🌤️ Weather: CAVOK (Clear)"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "COLLISION AVOIDANCE", [
                    "⚠️ Conflict: UAL2847 & DAL1523",
                    "📏 Proximity: 4.2 nm, 1,500 ft",
                    "✓ Resolution: UAL2847 climb FL370",
                    "✓ Safe separation restored"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "FLIGHT OPTIMIZATION", [
                    "🛫 Flight: AAL0345 (Boston → London)",
                    "📊 Route: NAT Track Sierra",
                    "💨 Tailwind: +85kt average",
                    "⏱️ Time savings: 14 minutes"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Operations Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
''',

    'maritime_realm.py': '''
    def run(self, duration=10):
        """Run pygame visual demo with HUD theme"""
        if not PYGAME_AVAILABLE or not self.screen:
            self.run_demo_cycle()
            return

        from core.design_tokens import (
            get_fonts, draw_animated_background, draw_header_bar,
            draw_footer_hud, draw_content_card, REALM_COLORS
        )

        start_time = time.time()
        clock = pygame.time.Clock()
        accent_color = REALM_COLORS.get('maritime', (0, 220, 240))
        fonts = get_fonts(self.screen)

        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            elapsed = time.time() - start_time
            remaining = int(duration - elapsed)

            draw_animated_background(self.screen, elapsed)
            draw_header_bar(self.screen, fonts, "⚓", "MARITIME REALM",
                          "Vessel Navigation · Port Ops · Marine Safety", accent_color, "AT SEA")

            if elapsed < duration / 3:
                draw_content_card(self.screen, fonts, "PORT OPERATIONS CENTER", [
                    "🚢 Location: Port of Boston",
                    "⚓ Active vessels: 42",
                    "🏗️ Berths occupied: 12/18",
                    "🌊 Tide: High +2.3m at 14:45"
                ], accent_color=accent_color)
            elif elapsed < duration * 2 / 3:
                draw_content_card(self.screen, fonts, "NAVIGATION ASSISTANCE", [
                    "🚢 Vessel: MSC MARINA (inbound)",
                    "📍 Position: 42.3251° N, 70.9812° W",
                    "📏 Distance to berth: 3.2 nm",
                    "✓ Route transmitted to vessel"
                ], accent_color=accent_color)
            else:
                draw_content_card(self.screen, fonts, "COLLISION AVOIDANCE", [
                    "⚠️ Crossing: MSC MARINA & NORDIC AURORA",
                    "📊 CPA: 0.4 nm (UNSAFE)",
                    "✓ Resolution: Course adjustment",
                    "✓ New CPA: 1.2 nm (SAFE)"
                ], accent_color=accent_color)

            draw_footer_hud(self.screen, fonts, "Operations Realm",
                          f"{remaining}s remaining", "ESC to exit · Auto-loop ON", accent_color)
            pygame.display.flip()
            clock.tick(30)
'''
}

def update_realm_file(filename):
    """Update a single realm file with HUD design"""
    filepath = f'scenes/{filename}'
    
    if not os.path.exists(filepath):
        print(f"  ⚠️  {filename} not found, skipping")
        return False
    
    print(f"  📝 Updating {filename}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove old run() method if exists
    content = re.sub(
        r'    def run\(self.*?(?=\n    def |\nclass |\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add new HUD run() method before the last closing of the class
    new_run = REALM_RUN_METHODS.get(filename, '')
    
    if new_run:
        # Find the last method and add run() after it
        content = content.rstrip() + '\n' + new_run + '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  ✓ {filename} updated with HUD design")
    return True

# Main execution
print("\n" + "="*70)
print("  MotiBeam Spatial OS - Unified HUD Theme Installer")
print("="*70 + "\n")

print("Updating all 9 realms with futuristic HUD design...\n")

updated_count = 0
for filename in REALM_RUN_METHODS.keys():
    if update_realm_file(filename):
        updated_count += 1

print(f"\n{'='*70}")
print(f"  ✓ Updated {updated_count}/9 realms successfully!")
print(f"{'='*70}\n")

print("All realms now feature:")
print("  • Unified futuristic HUD design")
print("  • Neon cyan/purple glow theme")
print("  • Animated backgrounds")
print("  • Glowing content panels")
print("  • Consistent header/footer bars")
print("  • Larger, readable fonts")
print("\nRun the demo:")
print("  DISPLAY=:0 SDL_VIDEODRIVER=x11 python3 spatial_auto_demo.py\n")
