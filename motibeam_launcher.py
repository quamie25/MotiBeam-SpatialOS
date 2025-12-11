#!/usr/bin/env python3
import pygame
import sys

def main():
    pygame.init()
    print("Initializing pygame (MotiBeam launcher)...")

    # Simple 1024x768 window; we'll adjust later once we confirm it shows
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("MOTIBEAM TEST LAUNCHER")

    # Big fonts for projection
    title_font = pygame.font.SysFont(None, 96)
    body_font  = pygame.font.SysFont(None, 40)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        # Background
        screen.fill((10, 20, 40))

        # Title
        title_surf = title_font.render("MOTIBEAM TEST", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(512, 220))
        screen.blit(title_surf, title_rect)

        # Instructions
        msg_surf = body_font.render(
            "If you can see this, display is working. Press Q or ESC to quit.",
            True,
            (220, 220, 220),
        )
        msg_rect = msg_surf.get_rect(center=(512, 320))
        screen.blit(msg_surf, msg_rect)

        # Three big colored blocks at the bottom
        pygame.draw.rect(screen, (0, 180, 255), (80,  480, 260, 160))
        pygame.draw.rect(screen, (0, 255, 140), (380, 480, 260, 160))
        pygame.draw.rect(screen, (255, 160, 0), (680, 480, 260, 160))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
