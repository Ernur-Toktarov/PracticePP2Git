"""
ui.py — Game Screens: MainMenu, Settings, GameOver, Leaderboard
"""
import pygame
from persistence import load_leaderboard, load_settings, save_settings

C_BG     = (20,  20,  40)
C_WHITE  = (255,255,255)
C_YELLOW = (255,220,  0)
C_GRAY   = (160,160,160)
C_GREEN  = (0,  200,  0)
C_RED    = (220,  30, 30)
C_CYAN   = (0,  200,210)
C_BLACK  = (0,    0,  0)
C_DARK   = (40,  40,  70)


def draw_button(surf, text, rect, color, font, hover=False):
    c = tuple(min(255, v+30) for v in color) if hover else color
    pygame.draw.rect(surf, c, rect, border_radius=8)
    pygame.draw.rect(surf, C_WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, C_WHITE)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


def is_hovered(rect):
    return rect.collidepoint(pygame.mouse.get_pos())


# ═════════════════════════════════════════════════════════════
# MAIN MENU
# ═════════════════════════════════════════════════════════════
def screen_main_menu(surf, clock):
    """Returns: 'play', 'leaderboard', 'settings', 'quit'"""
    font_big  = pygame.font.SysFont("Arial", 52, bold=True)
    font_med  = pygame.font.SysFont("Arial", 28)
    font_sub  = pygame.font.SysFont("Arial", 20)
    W, H = surf.get_size()

    buttons = {
        "play":        pygame.Rect(W//2-110, 220, 220, 55),
        "leaderboard": pygame.Rect(W//2-110, 295, 220, 55),
        "settings":    pygame.Rect(W//2-110, 370, 220, 55),
        "quit":        pygame.Rect(W//2-110, 445, 220, 55),
    }
    labels = {"play":"▶  Play", "leaderboard":"🏆  Leaderboard",
              "settings":"⚙  Settings", "quit":"✕  Quit"}
    colors = {"play":(0,150,0),"leaderboard":(0,100,180),
              "settings":(120,80,0),"quit":(160,0,0)}

    username = ""
    input_active = True
    input_rect   = pygame.Rect(W//2-110, 155, 220, 40)

    while True:
        surf.fill(C_BG)
        title = font_big.render("RACER", True, C_YELLOW)
        surf.blit(title, title.get_rect(center=(W//2, 90)))
        sub = font_sub.render("TSIS 3 — Advanced Driving", True, C_GRAY)
        surf.blit(sub, sub.get_rect(center=(W//2, 145)))

        # username input
        pygame.draw.rect(surf, C_DARK, input_rect, border_radius=6)
        pygame.draw.rect(surf, C_CYAN if input_active else C_GRAY,
                         input_rect, 2, border_radius=6)
        prompt = font_sub.render("Name: " + username + ("|" if input_active else ""),
                                 True, C_WHITE)
        surf.blit(prompt, (input_rect.x+8, input_rect.y+10))

        for key, rect in buttons.items():
            draw_button(surf, labels[key], rect, colors[key],
                        font_med, hover=is_hovered(rect))

        pygame.display.flip()
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", "Player"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif e.key == pygame.K_RETURN:
                    input_active = False
                elif e.unicode and len(username) < 16:
                    username += e.unicode
            if e.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in buttons.items():
                    if rect.collidepoint(e.pos):
                        return key, username or "Player"


# ═════════════════════════════════════════════════════════════
# SETTINGS
# ═════════════════════════════════════════════════════════════
def screen_settings(surf, clock):
    """Returns updated settings dict."""
    font_big  = pygame.font.SysFont("Arial", 38, bold=True)
    font_med  = pygame.font.SysFont("Arial", 24)
    W, H = surf.get_size()
    settings = load_settings()

    CAR_COLORS = [
        ("Blue",   (0,  120,255)),
        ("Red",    (220, 30, 30)),
        ("Green",  (0,  200,  0)),
        ("Yellow", (240,200,  0)),
        ("White",  (240,240,240)),
        ("Purple", (160,  0,200)),
    ]
    DIFFS = ["easy", "normal", "hard"]

    back_btn = pygame.Rect(W//2-90, H-80, 180, 45)

    while True:
        surf.fill(C_BG)
        title = font_big.render("Settings", True, C_YELLOW)
        surf.blit(title, title.get_rect(center=(W//2, 55)))

        # Sound toggle
        s_lbl = font_med.render("Sound:", True, C_WHITE)
        surf.blit(s_lbl, (80, 120))
        s_rect = pygame.Rect(260, 115, 100, 36)
        s_on   = settings["sound"]
        draw_button(surf, "ON" if s_on else "OFF", s_rect,
                    (0,150,0) if s_on else (150,0,0), font_med,
                    hover=is_hovered(s_rect))

        # Car color
        c_lbl = font_med.render("Car Color:", True, C_WHITE)
        surf.blit(c_lbl, (80, 180))
        for i, (name, col) in enumerate(CAR_COLORS):
            cr = pygame.Rect(80 + i*72, 215, 64, 36)
            border = C_YELLOW if tuple(settings["car_color"]) == col else C_GRAY
            pygame.draw.rect(surf, col, cr, border_radius=6)
            pygame.draw.rect(surf, border, cr, 3, border_radius=6)
            lbl = pygame.font.SysFont("Arial",14).render(name, True, C_BLACK)
            surf.blit(lbl, lbl.get_rect(center=cr.center))

        # Difficulty
        d_lbl = font_med.render("Difficulty:", True, C_WHITE)
        surf.blit(d_lbl, (80, 275))
        for i, d in enumerate(DIFFS):
            dr = pygame.Rect(80 + i*140, 310, 120, 36)
            active = settings["difficulty"] == d
            draw_button(surf, d.capitalize(), dr,
                        (0,140,0) if active else (60,60,90),
                        font_med, hover=is_hovered(dr))

        draw_button(surf, "← Back & Save", back_btn, (80,40,0),
                    font_med, hover=is_hovered(back_btn))

        pygame.display.flip()
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_settings(settings); return settings
            if e.type == pygame.MOUSEBUTTONDOWN:
                if s_rect.collidepoint(e.pos):
                    settings["sound"] = not settings["sound"]
                for _, (name, col) in enumerate(CAR_COLORS):
                    cr = pygame.Rect(80 + _ *72, 215, 64, 36)
                    if cr.collidepoint(e.pos):
                        settings["car_color"] = list(col)
                for i, d in enumerate(DIFFS):
                    dr = pygame.Rect(80 + i*140, 310, 120, 36)
                    if dr.collidepoint(e.pos):
                        settings["difficulty"] = d
                if back_btn.collidepoint(e.pos):
                    save_settings(settings); return settings


# ═════════════════════════════════════════════════════════════
# GAME OVER
# ═════════════════════════════════════════════════════════════
def screen_game_over(surf, clock, score, distance, coins):
    """Returns 'retry' or 'menu'."""
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_med = pygame.font.SysFont("Arial", 26)
    W, H = surf.get_size()
    retry_btn = pygame.Rect(W//2-140, H-160, 120, 50)
    menu_btn  = pygame.Rect(W//2+20,  H-160, 120, 50)

    while True:
        surf.fill(C_BG)
        go = font_big.render("GAME OVER", True, C_RED)
        surf.blit(go, go.get_rect(center=(W//2, 120)))

        for i, (label, val) in enumerate([
            ("Score",    score),
            ("Distance", f"{distance} m"),
            ("Coins",    coins),
        ]):
            line = font_med.render(f"{label}:  {val}", True, C_WHITE)
            surf.blit(line, line.get_rect(center=(W//2, 220 + i*50)))

        draw_button(surf, "Retry",     retry_btn, (0,130,0),
                    font_med, hover=is_hovered(retry_btn))
        draw_button(surf, "Main Menu", menu_btn,  (0,60,160),
                    font_med, hover=is_hovered(menu_btn))

        pygame.display.flip()
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "menu"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(e.pos): return "retry"
                if menu_btn.collidepoint(e.pos):  return "menu"


# ═════════════════════════════════════════════════════════════
# LEADERBOARD
# ═════════════════════════════════════════════════════════════
def screen_leaderboard(surf, clock):
    font_big = pygame.font.SysFont("Arial", 40, bold=True)
    font_med = pygame.font.SysFont("Arial", 22)
    font_sm  = pygame.font.SysFont("Arial", 18)
    W, H = surf.get_size()
    back_btn = pygame.Rect(W//2-80, H-70, 160, 45)
    board = load_leaderboard()

    while True:
        surf.fill(C_BG)
        title = font_big.render("🏆 Leaderboard", True, C_YELLOW)
        surf.blit(title, title.get_rect(center=(W//2, 55)))

        headers = ["#", "Name", "Score", "Distance"]
        for i, h in enumerate(headers):
            lbl = font_med.render(h, True, C_CYAN)
            surf.blit(lbl, (50 + i*130, 100))
        pygame.draw.line(surf, C_GRAY, (40, 125), (W-40, 125), 1)

        for rank, entry in enumerate(board[:10], 1):
            y = 135 + rank * 38
            color = C_YELLOW if rank == 1 else C_WHITE
            row = [str(rank), entry["username"],
                   str(entry["score"]), f"{entry['distance']} m"]
            for i, val in enumerate(row):
                lbl = font_sm.render(val, True, color)
                surf.blit(lbl, (50 + i*130, y))

        draw_button(surf, "← Back", back_btn, (80,40,0),
                    font_med, hover=is_hovered(back_btn))
        pygame.display.flip()
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(e.pos): return
