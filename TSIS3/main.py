"""
main.py — TSIS 3: Racer Game — Main Game Loop
Controls: ← → ↑ ↓  to drive
"""
import pygame, random, sys

from racer import (Player, TrafficCar, Obstacle, PowerUp, Coin, Road,
                   WIN_W, WIN_H, safe_to_spawn, DIFFICULTY_SETTINGS)
from persistence import load_settings, save_score
from ui import (screen_main_menu, screen_settings,
                screen_game_over, screen_leaderboard)

# ── HUD colors ────────────────────────────────────────────────
C_WHITE  = (255,255,255)
C_YELLOW = (255,220,  0)
C_RED    = (220,  30, 30)
C_GREEN  = (0,  200,  0)
C_CYAN   = (0,  200,210)
C_BLACK  = (0,    0,  0)
C_ORANGE = (255,140,  0)
C_BG_HUD = (0, 0, 0, 160)

RACE_DISTANCE = 5000   # metres to finish


# ══════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════
def draw_hud(surf, score, coins, distance, active_pu, pu_timer,
             shield, font, font_sm):
    # semi-transparent bar
    hud = pygame.Surface((WIN_W, 50), pygame.SRCALPHA)
    hud.fill((0,0,0,150))
    surf.blit(hud, (0, 0))

    surf.blit(font.render(f"Score: {score}",  True, C_YELLOW), (10, 8))
    surf.blit(font.render(f"Coins: {coins}",  True, C_WHITE),  (160,8))

    dist_left = max(0, RACE_DISTANCE - distance)
    surf.blit(font.render(f"Dist: {distance}m / {dist_left}m left",
                          True, C_CYAN), (310, 8))

    # active power-up indicator
    if active_pu:
        pu_color = {"nitro": C_ORANGE, "shield": C_CYAN,
                    "repair": C_GREEN}.get(active_pu, C_WHITE)
        secs = round(pu_timer / 60, 1) if pu_timer > 0 else ""
        txt = f"⚡ {active_pu.upper()}" + (f" {secs}s" if secs else "")
        lbl = font_sm.render(txt, True, pu_color)
        surf.blit(lbl, (10, WIN_H - 28))


# ══════════════════════════════════════════════════════════════
# PLAY ONE ROUND
# ══════════════════════════════════════════════════════════════
def play_game(screen, clock, settings, username):
    diff   = DIFFICULTY_SETTINGS[settings.get("difficulty", "normal")]
    player = Player(tuple(settings.get("car_color", [0,120,255])))
    road   = Road()

    road_speed   = 4
    score        = 0
    coins        = 0
    distance     = 0
    frame        = 0

    traffic   = []
    obstacles = []
    powerups  = []
    coin_objs = []

    active_powerup  = None   # "nitro"/"shield"/"repair"
    powerup_timer   = 0

    font    = pygame.font.SysFont("Arial", 20, bold=True)
    font_sm = pygame.font.SysFont("Arial", 16)

    running = True
    while running:
        clock.tick(60)
        frame += 1

        # ── Events ────────────────────────────────────────────
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "menu", score, distance, coins

        keys = pygame.key.get_pressed()
        player.move(keys, road_speed)

        # ── Difficulty scaling ─────────────────────────────────
        road_speed = 4 + distance // 300
        road_speed = min(road_speed, 14)

        spawn_rate   = max(20, diff["spawn_rate"]   - distance // 400)
        obs_rate     = max(30, diff["obstacle_rate"] - distance // 300)
        traffic_spd  = diff["traffic_speed"] + distance // 500

        # ── Spawn traffic ──────────────────────────────────────
        if frame % spawn_rate == 0:
            car = TrafficCar(traffic_spd)
            occupied = [t.rect for t in traffic] + [o.rect for o in obstacles]
            if safe_to_spawn(car.rect, occupied):
                traffic.append(car)

        # ── Spawn obstacles ────────────────────────────────────
        if frame % obs_rate == 0:
            obs = Obstacle(road_speed)
            occupied = [t.rect for t in traffic] + [o.rect for o in obstacles]
            if safe_to_spawn(obs.rect, occupied):
                obstacles.append(obs)

        # ── Spawn power-ups ────────────────────────────────────
        if frame % 180 == 0 and len(powerups) < 2:
            pu = PowerUp(road_speed)
            occupied = [t.rect for t in traffic] + [o.rect for o in obstacles]
            if safe_to_spawn(pu.rect, occupied):
                powerups.append(pu)

        # ── Spawn coins ────────────────────────────────────────
        if frame % 40 == 0:
            c = Coin(road_speed)
            occupied = [t.rect for t in traffic] + [o.rect for o in obstacles]
            if safe_to_spawn(c.rect, occupied):
                coin_objs.append(c)

        # ── Update everything ─────────────────────────────────
        road.update(road_speed)
        distance += road_speed // 4

        for t in traffic:   t.update(road_speed)
        for o in obstacles: o.update(road_speed)
        for pu in powerups: pu.update(road_speed)
        for c in coin_objs: c.update(road_speed)

        # active power-up timer
        if active_powerup in ("nitro",):
            powerup_timer -= 1
            if powerup_timer <= 0:
                active_powerup = None
                player.nitro   = False

        # remove off-screen
        traffic   = [t for t in traffic   if t.y < WIN_H + 80]
        obstacles = [o for o in obstacles if o.y < WIN_H + 80]
        powerups  = [p for p in powerups  if p.y < WIN_H + 80 and p.life > 0]
        coin_objs = [c for c in coin_objs if c.y < WIN_H + 80]

        # ── Collect coins ──────────────────────────────────────
        for c in coin_objs[:]:
            if player.rect.colliderect(c.rect):
                coins += c.value
                score += c.value * 10
                coin_objs.remove(c)

        # ── Collect power-ups ─────────────────────────────────
        for pu in powerups[:]:
            if player.rect.colliderect(pu.rect):
                powerups.remove(pu)
                if active_powerup is None or active_powerup != pu.kind:
                    if pu.kind == "nitro":
                        active_powerup = "nitro"
                        powerup_timer  = random.randint(180, 300)
                        player.nitro   = True
                        player.nitro_timer = powerup_timer
                    elif pu.kind == "shield":
                        active_powerup = "shield"
                        powerup_timer  = -1  # until hit
                        player.shield  = True
                    elif pu.kind == "repair":
                        active_powerup = None
                        score += 50

        # ── Obstacle collisions ────────────────────────────────
        for o in obstacles[:]:
            if player.rect.colliderect(o.rect):
                if o.kind == "nitro_strip":
                    player.nitro       = True
                    player.nitro_timer = 180
                    active_powerup     = "nitro"
                    powerup_timer      = 180
                    obstacles.remove(o)
                elif o.kind == "slowzone":
                    road_speed = max(2, road_speed - 1)
                    obstacles.remove(o)
                elif o.kind == "bump":
                    score = max(0, score - 5)
                    obstacles.remove(o)
                else:
                    if player.shield:
                        player.shield  = False
                        active_powerup = None
                        obstacles.remove(o)
                    else:
                        # CRASH
                        return "dead", score, distance, coins

        # ── Traffic collisions ─────────────────────────────────
        for t in traffic:
            if player.rect.colliderect(t.rect):
                if player.shield:
                    player.shield  = False
                    active_powerup = None
                else:
                    return "dead", score, distance, coins

        # ── Score for distance ────────────────────────────────
        if frame % 60 == 0:
            score += 1

        # ── Finish line ────────────────────────────────────────
        if distance >= RACE_DISTANCE:
            score += 500
            return "finish", score, distance, coins

        # ── Draw ──────────────────────────────────────────────
        road.draw(screen)
        for c in coin_objs: c.draw(screen)
        for o in obstacles: o.draw(screen)
        for t in traffic:   t.draw(screen)
        for p in powerups:  p.draw(screen)
        player.draw(screen)

        draw_hud(screen, score, coins, distance,
                 active_powerup, powerup_timer, player.shield,
                 font, font_sm)

        pygame.display.flip()

    return "menu", score, distance, coins


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("TSIS 3 — Racer")
    clock    = pygame.time.Clock()
    settings = load_settings()
    username = "Player"

    while True:
        action, username = screen_main_menu(screen, clock)

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            settings = screen_settings(screen, clock)

        elif action == "play":
            while True:
                result, score, distance, coins = play_game(
                    screen, clock, settings, username)

                save_score(username, score, distance)

                if result in ("dead", "finish"):
                    choice = screen_game_over(screen, clock,
                                              score, distance, coins)
                    if choice == "retry":
                        continue
                    else:
                        break
                else:
                    break


if __name__ == "__main__":
    main()
