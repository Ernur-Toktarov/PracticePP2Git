import math
from datetime import datetime
from collections import deque
import pygame


def rect_from_points(start, end):
    return pygame.Rect(
        min(start[0], end[0]),
        min(start[1], end[1]),
        abs(end[0] - start[0]),
        abs(end[1] - start[1])
    )


def draw_rectangle(surface, start, end, color, width):
    pygame.draw.rect(surface, color, rect_from_points(start, end), max(1, width))


def draw_square(surface, start, end, color, width):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    side = min(abs(dx), abs(dy))

    if side == 0:
        return

    x = start[0] if dx >= 0 else start[0] - side
    y = start[1] if dy >= 0 else start[1] - side

    pygame.draw.rect(surface, color, pygame.Rect(x, y, side, side), max(1, width))


def draw_circle(surface, start, end, color, width):
    radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))

    if radius > 0:
        pygame.draw.circle(surface, color, start, radius, max(1, width))


def draw_right_triangle(surface, start, end, color, width):
    points = [
        (start[0], start[1]),
        (start[0], end[1]),
        (end[0], end[1])
    ]
    pygame.draw.polygon(surface, color, points, max(1, width))


def draw_equilateral_triangle(surface, start, end, color, width):
    side = abs(end[0] - start[0])

    if side == 0:
        return

    x1 = start[0]
    x2 = start[0] + side if end[0] >= start[0] else start[0] - side
    height = int(side * math.sqrt(3) / 2)

    if end[1] >= start[1]:
        points = [
            (x1, start[1]),
            (x2, start[1]),
            ((x1 + x2) // 2, start[1] + height)
        ]
    else:
        points = [
            (x1, start[1]),
            (x2, start[1]),
            ((x1 + x2) // 2, start[1] - height)
        ]

    pygame.draw.polygon(surface, color, points, max(1, width))


def draw_rhombus(surface, start, end, color, width):
    left = min(start[0], end[0])
    right = max(start[0], end[0])
    top = min(start[1], end[1])
    bottom = max(start[1], end[1])

    mid_x = (left + right) // 2
    mid_y = (top + bottom) // 2

    points = [
        (mid_x, top),
        (right, mid_y),
        (mid_x, bottom),
        (left, mid_y)
    ]

    pygame.draw.polygon(surface, color, points, max(1, width))


def flood_fill(surface, start_pos, new_color):
    width, height = surface.get_size()
    x, y = start_pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    new_color = pygame.Color(*new_color)

    if target_color == new_color:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), new_color)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas(canvas):
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    print("Saved:", filename)