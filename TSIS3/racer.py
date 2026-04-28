"""
racer.py — Game objects: Player, Traffic, Obstacles, PowerUps, Road
"""
import pygame, random, math

# ── Layout ────────────────────────────────────────────────────
WIN_W, WIN_H = 600, 700
ROAD_LEFT    = 100
ROAD_RIGHT   = 500
ROAD_W       = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT   = 4
LANE_W       = ROAD_W // LANE_COUNT

def lane_x(lane):   # center x of lane 0-3
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2

# ── Colors ────────────────────────────────────────────────────
C_ROAD      = (50,  50,  50)
C_LANE_MARK = (200,200,  0)
C_GRASS     = (34, 139, 34)
C_WHITE     = (255,255,255)
C_RED       = (220,  30, 30)
C_YELLOW    = (255,220,  0)
C_ORANGE    = (255,140,  0)
C_CYAN      = (0,  220,220)
C_GRAY      = (130,130,130)
C_BLACK     = (0,    0,  0)
C_GREEN     = (0,  200,  0)
C_PURPLE    = (160,  0, 200)
C_BROWN     = (139, 69, 19)

DIFFICULTY_SETTINGS = {
    "easy":   {"traffic_speed": 3,  "spawn_rate": 90, "obstacle_rate": 120},
    "normal": {"traffic_speed": 5,  "spawn_rate": 60, "obstacle_rate": 80},
    "hard":   {"traffic_speed": 8,  "spawn_rate": 35, "obstacle_rate": 50},
}

# ═════════════════════════════════════════════════════════════
# PLAYER
# ═════════════════════════════════════════════════════════════
class Player:
    W, H = 40, 70

    def __init__(self, color):
        self.color   = color
        self.x       = WIN_W // 2
        self.y       = WIN_H - 120
        self.speed_x = 0
        self.lane    = 1
        # power-up state
        self.shield     = False
        self.nitro      = False
        self.nitro_timer= 0
        self.repair_used= False

    @property
    def rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2, self.W, self.H)

    def move(self, keys, road_speed):
        step = 5 + (3 if self.nitro else 0)
        if keys[pygame.K_LEFT]  and self.x - self.W//2 > ROAD_LEFT + 5:
            self.x -= step
        if keys[pygame.K_RIGHT] and self.x + self.W//2 < ROAD_RIGHT - 5:
            self.x += step
        if keys[pygame.K_UP]    and self.y > 50:
            self.y -= step
        if keys[pygame.K_DOWN]  and self.y < WIN_H - 50:
            self.y += step

        if self.nitro:
            self.nitro_timer -= 1
            if self.nitro_timer <= 0:
                self.nitro = False

    def draw(self, surf):
        r = self.rect
        # body
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        # windshield
        pygame.draw.rect(surf, C_CYAN,
                         (r.x+6, r.y+8, r.w-12, 18), border_radius=3)
        # wheels
        for wx, wy in [(r.x-4, r.y+8), (r.x+r.w, r.y+8),
                       (r.x-4, r.y+r.h-22), (r.x+r.w, r.y+r.h-22)]:
            pygame.draw.rect(surf, C_BLACK, (wx, wy, 8, 14), border_radius=3)
        # shield glow
        if self.shield:
            pygame.draw.ellipse(surf, C_CYAN,
                                r.inflate(14, 14), 3)
        # nitro flame
        if self.nitro:
            pts = [(r.centerx-8, r.bottom),
                   (r.centerx,   r.bottom+20),
                   (r.centerx+8, r.bottom)]
            pygame.draw.polygon(surf, C_ORANGE, pts)


# ═════════════════════════════════════════════════════════════
# TRAFFIC CAR
# ═════════════════════════════════════════════════════════════
TRAFFIC_COLORS = [C_RED, C_YELLOW, C_ORANGE, C_WHITE, C_PURPLE, C_BROWN]

class TrafficCar:
    W, H = 40, 70

    def __init__(self, speed):
        self.lane  = random.randint(0, LANE_COUNT-1)
        self.x     = lane_x(self.lane)
        self.y     = -self.H - random.randint(0, 200)
        self.speed = speed + random.uniform(-1, 1)
        self.color = random.choice(TRAFFIC_COLORS)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2, self.W, self.H)

    def update(self, road_speed):
        self.y += self.speed + road_speed * 0.5

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        pygame.draw.rect(surf, C_CYAN,
                         (r.x+6, r.y+r.h-26, r.w-12, 18), border_radius=3)
        for wx, wy in [(r.x-4, r.y+8), (r.x+r.w, r.y+8),
                       (r.x-4, r.y+r.h-22), (r.x+r.w, r.y+r.h-22)]:
            pygame.draw.rect(surf, C_BLACK, (wx, wy, 8, 14), border_radius=3)


# ═════════════════════════════════════════════════════════════
# OBSTACLES
# ═════════════════════════════════════════════════════════════
OBS_TYPES = ["barrier", "oil", "pothole", "bump", "nitro_strip", "slowzone"]

class Obstacle:
    def __init__(self, road_speed):
        self.kind  = random.choice(OBS_TYPES)
        self.lane  = random.randint(0, LANE_COUNT-1)
        self.x     = lane_x(self.lane)
        self.y     = -60
        self.speed = road_speed
        self.w, self.h = (80, 18) if self.kind in ("bump","nitro_strip","slowzone") \
                         else (44, 44)

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

    def update(self, road_speed):
        self.y += road_speed

    def draw(self, surf):
        r = self.rect
        if self.kind == "barrier":
            pygame.draw.rect(surf, C_RED,    r, border_radius=4)
            pygame.draw.rect(surf, C_WHITE,  r.inflate(-8,-8), border_radius=2)
        elif self.kind == "oil":
            pygame.draw.ellipse(surf, (20,20,20), r)
            pygame.draw.ellipse(surf, C_PURPLE,   r.inflate(-8,-8))
        elif self.kind == "pothole":
            pygame.draw.ellipse(surf, C_GRAY, r)
            pygame.draw.ellipse(surf, C_BLACK, r.inflate(-10,-10))
        elif self.kind == "bump":
            pygame.draw.rect(surf, C_BROWN, r, border_radius=8)
            font = pygame.font.SysFont("Arial", 11, bold=True)
            surf.blit(font.render("BUMP", True, C_WHITE), (r.x+4, r.y+2))
        elif self.kind == "nitro_strip":
            pygame.draw.rect(surf, C_GREEN, r, border_radius=6)
            font = pygame.font.SysFont("Arial", 11, bold=True)
            surf.blit(font.render("NITRO", True, C_BLACK), (r.x+6, r.y+2))
        elif self.kind == "slowzone":
            pygame.draw.rect(surf, C_YELLOW, r, border_radius=6)
            font = pygame.font.SysFont("Arial", 10, bold=True)
            surf.blit(font.render("SLOW", True, C_BLACK), (r.x+8, r.y+3))


# ═════════════════════════════════════════════════════════════
# POWER-UPS
# ═════════════════════════════════════════════════════════════
POWERUP_TYPES   = ["nitro", "shield", "repair"]
POWERUP_COLORS  = {"nitro": C_ORANGE, "shield": C_CYAN, "repair": C_GREEN}
POWERUP_LETTERS = {"nitro": "N", "shield": "S", "repair": "R"}
POWERUP_LIFETIME = 300  # frames before disappearing

class PowerUp:
    SIZE = 30

    def __init__(self, road_speed):
        self.kind   = random.choice(POWERUP_TYPES)
        self.lane   = random.randint(0, LANE_COUNT-1)
        self.x      = lane_x(self.lane)
        self.y      = -40
        self.speed  = road_speed
        self.life   = POWERUP_LIFETIME

    @property
    def rect(self):
        s = self.SIZE
        return pygame.Rect(self.x - s//2, self.y - s//2, s, s)

    def update(self, road_speed):
        self.y    += road_speed
        self.life -= 1

    def draw(self, surf):
        r = self.rect
        pygame.draw.ellipse(surf, POWERUP_COLORS[self.kind], r)
        pygame.draw.ellipse(surf, C_WHITE, r, 2)
        font = pygame.font.SysFont("Arial", 16, bold=True)
        lbl  = font.render(POWERUP_LETTERS[self.kind], True, C_BLACK)
        surf.blit(lbl, lbl.get_rect(center=r.center))


# ═════════════════════════════════════════════════════════════
# COIN (weighted)
# ═════════════════════════════════════════════════════════════
COIN_WEIGHTS = [(1, 60), (3, 30), (5, 10)]   # (value, weight)

class Coin:
    def __init__(self, road_speed):
        total  = sum(w for _,w in COIN_WEIGHTS)
        r      = random.randint(1, total)
        cumul  = 0
        self.value = 1
        for v, w in COIN_WEIGHTS:
            cumul += w
            if r <= cumul:
                self.value = v
                break
        self.lane  = random.randint(0, LANE_COUNT-1)
        self.x     = lane_x(self.lane)
        self.y     = -20
        self.speed = road_speed

    @property
    def rect(self):
        return pygame.Rect(self.x-12, self.y-12, 24, 24)

    def update(self, road_speed):
        self.y += road_speed

    def draw(self, surf):
        color = {1: C_YELLOW, 3: C_ORANGE, 5: C_CYAN}[self.value]
        pygame.draw.circle(surf, color, (self.x, self.y), 12)
        pygame.draw.circle(surf, C_WHITE, (self.x, self.y), 12, 2)
        font = pygame.font.SysFont("Arial", 11, bold=True)
        lbl  = font.render(str(self.value), True, C_BLACK)
        surf.blit(lbl, lbl.get_rect(center=(self.x, self.y)))


# ═════════════════════════════════════════════════════════════
# ROAD
# ═════════════════════════════════════════════════════════════
class Road:
    def __init__(self):
        self.offset = 0
        self.marks  = list(range(0, WIN_H+60, 60))

    def update(self, speed):
        self.offset = (self.offset + speed) % 60
        self.marks  = [(m + speed) % (WIN_H + 60) - 60 for m in self.marks]

    def draw(self, surf):
        # grass
        surf.fill(C_GRASS)
        # road
        pygame.draw.rect(surf, C_ROAD, (ROAD_LEFT, 0, ROAD_W, WIN_H))
        # lane markings
        for lane in range(1, LANE_COUNT):
            lx = ROAD_LEFT + lane * LANE_W
            for my in self.marks:
                pygame.draw.rect(surf, C_LANE_MARK, (lx-2, my, 4, 40))
        # road edges
        pygame.draw.rect(surf, C_WHITE, (ROAD_LEFT-3,  0, 3, WIN_H))
        pygame.draw.rect(surf, C_WHITE, (ROAD_RIGHT,   0, 3, WIN_H))


# ═════════════════════════════════════════════════════════════
# SAFE SPAWN CHECK
# ═════════════════════════════════════════════════════════════
def safe_to_spawn(new_rect, existing_rects, margin=60):
    nr = new_rect.inflate(margin, margin)
    return not any(nr.colliderect(r) for r in existing_rects)
