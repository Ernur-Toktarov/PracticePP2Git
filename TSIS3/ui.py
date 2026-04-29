import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def menu_screen(screen, font):
    while True:
        screen.fill(WHITE)

        screen.blit(font.render("TSIS3 Racer", True, BLACK), (320, 80))
        screen.blit(font.render("1 - Play", True, BLACK), (320, 180))
        screen.blit(font.render("2 - Leaderboard", True, BLACK), (320, 230))
        screen.blit(font.render("3 - Settings", True, BLACK), (320, 280))
        screen.blit(font.render("4 - Exit", True, BLACK), (320, 330))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                elif event.key == pygame.K_2:
                    return "leaderboard"
                elif event.key == pygame.K_3:
                    return "settings"
                elif event.key == pygame.K_4:
                    return "exit"


def leaderboard_screen(screen, font, data):
    while True:
        screen.fill(WHITE)

        screen.blit(font.render("Leaderboard", True, BLACK), (320, 60))

        y = 130
        if not data:
            screen.blit(font.render("No scores yet", True, BLACK), (300, y))
        else:
            for i, item in enumerate(data, 1):
                text = f"{i}. {item['name']} | score: {item['score']} | dist: {item['distance']}"
                screen.blit(font.render(text, True, BLACK), (80, y))
                y += 40

        screen.blit(font.render("Press ESC to go back", True, BLACK), (240, 540))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def settings_screen(screen, font, settings):
    while True:
        screen.fill(WHITE)

        screen.blit(font.render("Settings", True, BLACK), (350, 60))
        screen.blit(font.render(f"S - Sound: {settings['sound']}", True, BLACK), (220, 180))
        screen.blit(font.render(f"D - Difficulty: {settings['difficulty']}", True, BLACK), (220, 230))
        screen.blit(font.render("B - Blue car", True, BLACK), (220, 280))
        screen.blit(font.render("R - Red car", True, BLACK), (220, 330))
        screen.blit(font.render("G - Green car", True, BLACK), (220, 380))
        screen.blit(font.render("Enter - Save and Back", True, BLACK), (220, 460))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    settings["sound"] = not settings["sound"]

                elif event.key == pygame.K_d:
                    if settings["difficulty"] == "easy":
                        settings["difficulty"] = "normal"
                    elif settings["difficulty"] == "normal":
                        settings["difficulty"] = "hard"
                    else:
                        settings["difficulty"] = "easy"

                elif event.key == pygame.K_b:
                    settings["car_color"] = [0, 100, 255]

                elif event.key == pygame.K_r:
                    settings["car_color"] = [220, 0, 0]

                elif event.key == pygame.K_g:
                    settings["car_color"] = [0, 180, 0]

                elif event.key == pygame.K_RETURN:
                    return settings