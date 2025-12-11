#!/usr/bin/env python3
"""
MotiBeam Spatial OS - Spatial Auto Demo
Fullscreen pygame visualization for Kickstarter projector demo

Run with:
    DISPLAY=:0 SDL_VIDEODRIVER=x11 python3 spatial_auto_demo.py

Controls:
    ESC - Return to loop / Exit
    Q - Quit demo
"""

import sys
import os
import time
import importlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    logger.error("pygame not available! Install with: pip3 install pygame")
    PYGAME_AVAILABLE = False
    sys.exit(1)

# Import config
from config.realms_config import REALMS_CONFIG, AUTO_DEMO_ORDER, SYSTEM_CONFIG


class SpatialAutoDemo:
    """Main auto-demo loop controller"""

    def __init__(self, fullscreen=True):
        """Initialize the demo system"""
        pygame.init()

        self.fullscreen = fullscreen
        self.running = True
        self.screen = None
        self.clock = pygame.time.Clock()

        # Display setup with true borderless fullscreen (no Pi desktop bar)
        self.display_info = pygame.display.Info()
        if self.fullscreen:
            # True fullscreen: borderless, no frame, no desktop bar
            flags = pygame.FULLSCREEN | pygame.NOFRAME
            self.screen = pygame.display.set_mode(
                (self.display_info.current_w, self.display_info.current_h),
                flags
            )
            logger.info(f"True fullscreen mode (borderless): {self.screen.get_size()}")
        else:
            # Windowed mode: 80% of display size
            windowed_w = int(self.display_info.current_w * 0.8)
            windowed_h = int(self.display_info.current_h * 0.8)
            self.screen = pygame.display.set_mode((windowed_w, windowed_h))
            logger.info(f"Windowed mode (80%): {windowed_w}x{windowed_h}")

        pygame.display.set_caption("MotiBeam Spatial OS - Auto Demo")

        # Get actual screen size
        self.width, self.height = self.screen.get_size()
        logger.info(f"Screen dimensions: {self.width}x{self.height}")

        # Demo settings
        self.realm_duration = SYSTEM_CONFIG.get('demo_cycle_duration', 10)
        self.transition_delay = SYSTEM_CONFIG.get('auto_loop_delay', 2)

        # Realm cache
        self.realm_instances = {}

    def load_realm(self, realm_id):
        """Dynamically load a realm from config"""
        if realm_id in self.realm_instances:
            return self.realm_instances[realm_id]

        try:
            config = REALMS_CONFIG[realm_id]
            module_path = config['module_path']
            class_name = config['class_name']

            logger.info(f"Loading realm: {realm_id} ({module_path}.{class_name})")

            # Import module
            module = importlib.import_module(module_path)

            # Get class
            realm_class = getattr(module, class_name)

            # Instantiate with standalone=False
            realm_instance = realm_class(standalone=False)
            realm_instance.screen = self.screen

            # Initialize
            realm_instance.initialize()

            # Cache it
            self.realm_instances[realm_id] = realm_instance

            logger.info(f"✓ Realm {realm_id} loaded successfully")
            return realm_instance

        except Exception as e:
            logger.error(f"✗ Failed to load realm {realm_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def show_transition(self, next_realm_name):
        """Show transition screen between realms"""
        BG = (20, 20, 30)
        WHITE = (255, 255, 255)
        ACCENT = (100, 200, 255)

        try:
            font = pygame.font.Font(None, 72)
            small_font = pygame.font.Font(None, 48)
        except:
            font = pygame.font.SysFont('arial', 72, bold=True)
            small_font = pygame.font.SysFont('arial', 48)

        self.screen.fill(BG)

        # "Next up" text
        next_text = font.render("NEXT UP", True, ACCENT)
        next_rect = next_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(next_text, next_rect)

        # Realm name
        realm_text = small_font.render(next_realm_name, True, WHITE)
        realm_rect = realm_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(realm_text, realm_rect)

        pygame.display.flip()
        time.sleep(self.transition_delay)

    def show_error(self, realm_id, error_msg):
        """Show error screen if a realm fails"""
        BG = (40, 20, 20)
        WHITE = (255, 255, 255)
        RED = (255, 100, 100)

        try:
            font = pygame.font.Font(None, 64)
            small_font = pygame.font.Font(None, 36)
        except:
            font = pygame.font.SysFont('arial', 64, bold=True)
            small_font = pygame.font.SysFont('arial', 36)

        self.screen.fill(BG)

        error_text = font.render(f"ERROR: {realm_id}", True, RED)
        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(error_text, error_rect)

        msg_text = small_font.render(str(error_msg)[:60], True, WHITE)
        msg_rect = msg_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(msg_text, msg_rect)

        continue_text = small_font.render("Continuing in 3 seconds...", True, WHITE)
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 120))
        self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()
        time.sleep(3)

    def run_realm(self, realm_id):
        """Run a single realm demo"""
        logger.info(f"Running realm: {realm_id}")

        try:
            realm = self.load_realm(realm_id)

            if realm is None:
                self.show_error(realm_id, "Failed to load realm")
                return False

            # Run the realm's visual demo
            # The realm's run() method should handle its own event loop
            # and respect ESC key to return early
            realm.run(duration=self.realm_duration)

            logger.info(f"✓ Realm {realm_id} completed")
            return True

        except KeyboardInterrupt:
            logger.info("Realm interrupted by user")
            raise
        except Exception as e:
            logger.error(f"✗ Realm {realm_id} failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(realm_id, str(e))
            return False

    def run(self):
        """Main auto-demo loop"""
        logger.info("Starting MotiBeam Spatial OS Auto Demo")
        logger.info(f"Realm order: {AUTO_DEMO_ORDER}")
        logger.info(f"Duration per realm: {self.realm_duration}s")
        logger.info("Press ESC to exit")

        try:
            loop_count = 0
            while self.running:
                loop_count += 1
                logger.info(f"\n=== Demo Loop #{loop_count} ===")

                for realm_id in AUTO_DEMO_ORDER:
                    # Check for quit events before each realm
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            break
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                                logger.info("User requested quit")
                                self.running = False
                                break
                            elif event.key == pygame.K_f:
                                # Toggle fullscreen
                                self.toggle_fullscreen()
                                # Update screen reference for all loaded realms
                                for realm in self.realm_instances.values():
                                    realm.screen = self.screen

                    if not self.running:
                        break

                    # Show transition
                    config = REALMS_CONFIG[realm_id]
                    self.show_transition(config['name'])

                    # Run realm
                    self.run_realm(realm_id)

                if not self.running:
                    break

                # Brief pause before restarting loop
                logger.info(f"\nCompleted loop #{loop_count}, restarting...")
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\nDemo interrupted by user (Ctrl+C)")

        finally:
            self.shutdown()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            # Switch to true borderless fullscreen
            flags = pygame.FULLSCREEN | pygame.NOFRAME
            self.screen = pygame.display.set_mode(
                (self.display_info.current_w, self.display_info.current_h),
                flags
            )
            logger.info(f"Switched to fullscreen mode: {self.screen.get_size()}")
        else:
            # Switch to windowed mode (80% of display)
            windowed_w = int(self.display_info.current_w * 0.8)
            windowed_h = int(self.display_info.current_h * 0.8)
            self.screen = pygame.display.set_mode((windowed_w, windowed_h))
            logger.info(f"Switched to windowed mode: {windowed_w}x{windowed_h}")

        # Update dimensions
        self.width, self.height = self.screen.get_size()

    def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down MotiBeam Spatial OS Auto Demo")
        pygame.quit()
        logger.info("Goodbye!")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           MotiBeam Spatial OS - Fullscreen Auto Demo                ║
║                    Kickstarter Projector Mode                        ║
╚══════════════════════════════════════════════════════════════════════╝

9 Realms in Auto-Loop:
  1. Home Realm (Smart Home, Family)
  2. Clinical Realm (Health & Wellness)
  3. Education Realm (Learning & Focus)
  4. Transport Realm (Automotive HUD)
  5. Emergency Realm (911 Dispatch)
  6. Security Realm (Surveillance)
  7. Enterprise Realm (Office)
  8. Aviation Realm (Air Traffic)
  9. Maritime Realm (Vessel Navigation)

Controls:
  ESC or Q - Exit demo
  F - Toggle fullscreen/windowed mode

Starting in 2 seconds...
""")

    time.sleep(2)

    # Determine fullscreen mode
    fullscreen = True
    if len(sys.argv) > 1 and sys.argv[1] == '--windowed':
        fullscreen = False

    # Create and run demo
    demo = SpatialAutoDemo(fullscreen=fullscreen)
    demo.run()


if __name__ == "__main__":
    main()
