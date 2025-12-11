#!/usr/bin/env python3
"""
MotiBeam Spatial OS (MOS-1.0) - Main Entrypoint
Multi-Realm Ambient Computing Platform

Realms:
  - Emergency Response (911, Crisis Management)
  - Security & Surveillance (Access Control, Threat Detection)
  - Enterprise Workspace (Collaboration, Productivity)
  - Aviation Control (ATC, Flight Safety)
  - Maritime Operations (Vessel Navigation, Port Ops)
"""

import sys
import time
import os
from typing import Optional

# Import realms
from scenes.emergency_realm import EmergencyRealm
from scenes.security_realm import SecurityRealm
from scenes.enterprise_realm import EnterpriseRealm
from scenes.aviation_realm import AviationRealm
from scenes.maritime_realm import MaritimeRealm
from config.realms_config import REALMS_CONFIG, SYSTEM_CONFIG


class MotiBeamSpatialOS:
    """Main MotiBeam Spatial OS system controller"""

    def __init__(self):
        self.version = SYSTEM_CONFIG["version"]
        self.codename = SYSTEM_CONFIG["codename"]
        self.realms = {
            "emergency": EmergencyRealm(),
            "security": SecurityRealm(),
            "enterprise": EnterpriseRealm(),
            "aviation": AviationRealm(),
            "maritime": MaritimeRealm()
        }
        self.current_realm = None

    def display_banner(self):
        """Display MotiBeam OS banner"""
        os.system('clear' if os.name != 'nt' else 'cls')
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ███╗   ███╗ ██████╗ ████████╗██╗██████╗ ███████╗ █████╗ ███╗   ███╗
║    ████╗ ████║██╔═══██╗╚══██╔══╝██║██╔══██╗██╔════╝██╔══██╗████╗ ████║
║    ██╔████╔██║██║   ██║   ██║   ██║██████╔╝█████╗  ███████║██╔████╔██║
║    ██║╚██╔╝██║██║   ██║   ██║   ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
║    ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║██████╔╝███████╗██║  ██║██║ ╚═╝ ██║
║    ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
║                                                                      ║
║                      SPATIAL OS — {version}                           ║
║              Multi-Realm Ambient Computing Platform                 ║
║                   [{codename}]                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """.format(version=self.version, codename=self.codename))

    def display_main_menu(self):
        """Display main menu"""
        print("\n" + "="*70)
        print("  AVAILABLE REALMS")
        print("="*70)

        menu_items = [
            ("1", "emergency", "Emergency Response Realm", "🚨"),
            ("2", "security", "Security & Surveillance Realm", "🛡️"),
            ("3", "enterprise", "Enterprise Workspace Realm", "🏢"),
            ("4", "aviation", "Aviation Control Realm", "✈️"),
            ("5", "maritime", "Maritime Operations Realm", "⚓"),
            ("", "", "", ""),
            ("A", "auto", "Auto-Loop Demo (All Realms)", "🔄"),
            ("Q", "quit", "Quit MotiBeam OS", "👋")
        ]

        for num, key, name, icon in menu_items:
            if num:
                print(f"  [{num}] {icon}  {name}")
            else:
                print()

        print("="*70)

    def run_realm(self, realm_key: str) -> None:
        """Run a specific realm demo"""
        if realm_key not in self.realms:
            print(f"❌ Error: Unknown realm '{realm_key}'")
            return

        realm = self.realms[realm_key]
        realm.activate()
        realm.run_demo_cycle()
        realm.deactivate()

        print("\n" + "="*70)
        input("  Press Enter to return to main menu...")

    def run_auto_loop_demo(self) -> None:
        """Run auto-looping demo of all realms"""
        os.system('clear' if os.name != 'nt' else 'cls')
        print("\n" + "="*70)
        print("  🔄 AUTO-LOOP KICKSTARTER DEMO MODE")
        print("  Cycling through all realms continuously...")
        print("  Press Ctrl+C to return to main menu")
        print("="*70)
        time.sleep(2)

        realm_order = ["emergency", "security", "enterprise", "aviation", "maritime"]

        try:
            while True:
                for realm_key in realm_order:
                    realm = self.realms[realm_key]
                    realm.activate()
                    realm.run_demo_cycle()
                    realm.deactivate()

                    print("\n" + "="*70)
                    print(f"  Next realm in {SYSTEM_CONFIG['auto_loop_delay']} seconds...")
                    print("="*70)
                    time.sleep(SYSTEM_CONFIG['auto_loop_delay'])

                print("\n" + "="*70)
                print("  🔄 Restarting demo loop...")
                print("="*70)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  Auto-loop demo stopped by user")
            print("="*70)
            time.sleep(1)

    def run_interactive_mode(self) -> None:
        """Run interactive menu mode"""
        while True:
            self.display_banner()
            self.display_main_menu()

            try:
                choice = input("\n  Select option: ").strip().upper()

                if choice == 'Q':
                    self.shutdown()
                    break
                elif choice == 'A':
                    self.run_auto_loop_demo()
                elif choice in ['1', '2', '3', '4', '5']:
                    realm_map = {
                        '1': 'emergency',
                        '2': 'security',
                        '3': 'enterprise',
                        '4': 'aviation',
                        '5': 'maritime'
                    }
                    self.run_realm(realm_map[choice])
                else:
                    print("\n  ❌ Invalid selection. Please try again.")
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n")
                self.shutdown()
                break
            except Exception as e:
                print(f"\n  ❌ Error: {e}")
                time.sleep(2)

    def shutdown(self) -> None:
        """Shutdown MotiBeam OS"""
        print("\n" + "="*70)
        print("  Shutting down MotiBeam Spatial OS...")
        print("  Thank you for experiencing the future of spatial computing!")
        print("="*70 + "\n")

    def run(self, mode: Optional[str] = None) -> None:
        """Main run method"""
        if mode == "auto":
            self.display_banner()
            time.sleep(1)
            self.run_auto_loop_demo()
        else:
            self.run_interactive_mode()


def main():
    """Main entry point"""
    os_instance = MotiBeamSpatialOS()

    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--auto", "-a", "auto"]:
            os_instance.run(mode="auto")
        elif sys.argv[1] in ["--help", "-h"]:
            print("""
MotiBeam Spatial OS - Usage

  python motibeam_spatial_os.py          Run in interactive menu mode
  python motibeam_spatial_os.py --auto   Run in auto-loop demo mode
  python motibeam_spatial_os.py --help   Show this help message

Realms Available:
  • Emergency Response (911, Crisis Management)
  • Security & Surveillance (Access Control, Threat Detection)
  • Enterprise Workspace (Collaboration, Productivity)
  • Aviation Control (ATC, Flight Safety)
  • Maritime Operations (Vessel Navigation, Port Ops)
            """)
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            return
    else:
        os_instance.run()


if __name__ == "__main__":
    main()
