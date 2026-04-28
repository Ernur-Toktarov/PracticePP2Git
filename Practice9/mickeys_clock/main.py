import pygame
from clock import MickeysClock

pygame.init()

app = MickeysClock()
screen = pygame.display.set_mode((app.width, app.height))
pygame.display.set_caption("Mickey's Clock")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    app.update()
    app.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()