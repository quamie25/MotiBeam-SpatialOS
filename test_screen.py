import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 36)

# Draw a border to see screen edges
pygame.draw.rect(screen, (255, 0, 0), (0, 0, 1280, 720), 4)

# Draw 3 rectangles at different widths
widths = [1000, 1100, 1200]  # Test different widths
colors = [(0, 255, 0), (0, 200, 100), (0, 150, 150)]

for i, width in enumerate(widths):
    x = (1280 - width) // 2
    pygame.draw.rect(screen, colors[i], (x, 100, width, 200), 3)
    text = font.render(f"{width}px wide", True, (255, 255, 255))
    screen.blit(text, (x + 20, 120 + i*40))

# Draw MotiBeam-like grid for comparison
for col in range(3):
    card_width = 400
    x = 100 + col * (card_width + 20)
    pygame.draw.rect(screen, (100, 100, 255), (x, 350, card_width, 200), 3)
    text = font.render(f"400px card", True, (255, 255, 255))
    screen.blit(text, (x + 20, 400))

# Show resolution
res_text = font.render("Testing 1280x720 output", True, (255, 255, 255))
screen.blit(res_text, (1280//2 - res_text.get_width()//2, 600))

pygame.display.flip()

# Wait
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    clock.tick(30)

pygame.quit()
