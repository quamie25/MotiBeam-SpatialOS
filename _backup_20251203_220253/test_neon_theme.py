#!/usr/bin/env python3
"""
Quick test script for Neon HUD theme
Tests each realm for 5 seconds in windowed mode
"""

import sys
import os
import time
import importlib
import pygame

# Import config
from config.realms_config import REALMS_CONFIG, AUTO_DEMO_ORDER

def test_realm(screen, realm_id, duration=5):
    """Test a single realm"""
    try:
        config = REALMS_CONFIG[realm_id]
        module_path = config['module_path']
        class_name = config['class_name']

        print(f"\nTesting: {realm_id} ({config['name']})")

        # Import and instantiate
        module = importlib.import_module(module_path)
        realm_class = getattr(module, class_name)
        realm = realm_class(standalone=False)
        realm.screen = screen
        realm.initialize()

        # Run for specified duration
        realm.run(duration=duration)

        print(f"  ✓ {realm_id} passed")
        return True

    except Exception as e:
        print(f"  ✗ {realm_id} FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           MotiBeam Spatial OS - Neon Theme Test Suite               ║
║                Testing all 9 realms (5s each)                        ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("MotiBeam - Theme Test")

    passed = 0
    failed = 0

    for realm_id in AUTO_DEMO_ORDER:
        if test_realm(screen, realm_id, duration=5):
            passed += 1
        else:
            failed += 1

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                print("\n\nTest interrupted by user")
                pygame.quit()
                return

        time.sleep(1)

    pygame.quit()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                          TEST RESULTS                                ║
╚══════════════════════════════════════════════════════════════════════╝

Total Realms: {passed + failed}
Passed: {passed}
Failed: {failed}

{'✅ ALL TESTS PASSED!' if failed == 0 else '❌ SOME TESTS FAILED'}
""")

if __name__ == "__main__":
    main()
