import os
import sys
import pygame

SCREEN_WIDTH = int(os.environ.get("MOTIBEAM_WIDTH", "1024"))
SCREEN_HEIGHT = int(os.environ.get("MOTIBEAM_HEIGHT", "768"))

pygame.init()
pygame.font.init()

flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("MotiBeam Display Test")
pygame.mouse.set_visible(False)

font = pygame.font.SysFont("dejavusans", 80)

clock = pygame.time.Clock()
running = True
print("[TEST] Pygame display started.")

while running:
    dt = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

    screen.fill((200, 40, 40))  # BRIGHT RED

    text_surface = font.render("MOTIBEAM TEST", True, (255, 255, 255))
    rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, rect)

    pygame.display.flip()

pygame.quit()
sys.exit(0)
