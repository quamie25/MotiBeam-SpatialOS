import os
import pygame

WIDTH, HEIGHT = 1024, 768

def init_display():
    print("Initializing pygame (minimal)...")
    pygame.quit()
    pygame.display.quit()
    pygame.init()

    try:
        os.unsetenv("SDL_VIDEODRIVER")
    except Exception:
        os.putenv("SDL_VIDEODRIVER", "")

    pygame.display.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("MOTIBEAM MINIMAL")
    print("  ✓ Minimal display created")
    return screen

def main():
    screen = init_display()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 72)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # dark background
        screen.fill((10, 10, 20))

        # one bright card
        pygame.draw.rect(screen, (40, 160, 255), (262, 184, 500, 300), border_radius=30)
        text = font.render("MOTIBEAM", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
