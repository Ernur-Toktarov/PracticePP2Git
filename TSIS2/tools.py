import pygame
from collections import deque

BRUSH_SIZES = {"small": 2, "medium": 5, "large": 10}

COLORS = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0),
    (0, 200, 0), (0, 0, 255), (255, 255, 0),
    (255, 165, 0), (128, 0, 128), (0, 255, 255),
    (255, 192, 203), (139, 69, 19), (128, 128, 128),
]

SHAPE_TOOLS = ["rectangle", "circle", "square",
               "right_triangle", "equilateral_triangle", "rhombus", "line"]


# ── Flood Fill ────────────────────────────────────────────────
def flood_fill(surface: pygame.Surface, x: int, y: int, fill_color):
    w, h = surface.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return
    target = surface.get_at((x, y))[:3]
    fc = tuple(fill_color[:3])
    if target == fc:
        return
    queue = deque([(x, y)])
    visited = {(x, y)}
    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), fc)
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                visited.add((nx,ny))
                queue.append((nx,ny))


# ── Shape drawing ─────────────────────────────────────────────
def draw_shape(surface, tool, color, start, end, brush_size):
    import math
    w = brush_size
    x0, y0 = start
    x1, y1 = end

    if tool == "line":
        pygame.draw.line(surface, color, start, end, w)

    elif tool == "rectangle":
        rx = min(x0,x1); ry = min(y0,y1)
        pygame.draw.rect(surface, color,
                         (rx, ry, abs(x1-x0), abs(y1-y0)), w)

    elif tool == "circle":
        cx = (x0+x1)//2; cy = (y0+y1)//2
        r  = int(math.hypot(x1-x0, y1-y0) // 2)
        pygame.draw.circle(surface, color, (cx,cy), max(r,1), w)

    elif tool == "square":
        side = min(abs(x1-x0), abs(y1-y0))
        sx = x0 if x1 >= x0 else x0-side
        sy = y0 if y1 >= y0 else y0-side
        pygame.draw.rect(surface, color, (sx, sy, side, side), w)

    elif tool == "right_triangle":
        pygame.draw.polygon(surface, color,
                            [start, (x0, y1), end], w)

    elif tool == "equilateral_triangle":
        base = abs(x1-x0)
        h    = int(base * math.sqrt(3) / 2)
        cx   = (x0+x1)//2
        pygame.draw.polygon(surface, color,
                            [(x0, y0+h), (x1, y0+h), (cx, y0)], w)

    elif tool == "rhombus":
        cx = (x0+x1)//2; cy = (y0+y1)//2
        pygame.draw.polygon(surface, color,
                            [(cx,y0),(x1,cy),(cx,y1),(x0,cy)], w)
