import pygame
from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import menu_screen, leaderboard_screen, settings_screen
from racer import run_game

pygame.init()

screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("TSIS3 Racer")
font = pygame.font.SysFont("Arial", 28)

settings = load_settings()


def ask_name():
    username = ""

    while True:
        screen.fill((255, 255, 255))
        screen.blit(font.render("Enter your name and press Enter:", True, (0, 0, 0)), (200, 250))
        screen.blit(font.render(username, True, (0, 0, 255)), (200, 310))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    if event.unicode.isprintable():
                        username += event.unicode


running = True

while running:
    choice = menu_screen(screen, font)

    if choice == "exit":
        running = False

    elif choice == "leaderboard":
        leaderboard_screen(screen, font, load_leaderboard())

    elif choice == "settings":
        settings = settings_screen(screen, font, settings)
        save_settings(settings)

    elif choice == "play":
        name = ask_name()

        if not name:
            running = False
            continue

        result = run_game(screen, font, name, settings)

        if result is None:
            running = False
            continue

        save_score(name, result["score"], result["distance"])

        waiting = True
        while waiting:
            screen.fill((255, 255, 255))
            screen.blit(font.render("Game Over", True, (0, 0, 0)), (340, 150))
            screen.blit(font.render(f"Score: {result['score']}", True, (0, 0, 0)), (320, 230))
            screen.blit(font.render(f"Distance: {result['distance']}", True, (0, 0, 0)), (320, 280))
            screen.blit(font.render(f"Coins: {result['coins']}", True, (0, 0, 0)), (320, 330))
            screen.blit(font.render("Press M for Menu", True, (0, 0, 0)), (280, 430))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        waiting = False

pygame.quit()