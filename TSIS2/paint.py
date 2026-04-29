import sys
import pygame

from tools import *


WIDTH = 1200
HEIGHT = 700
TOOLBAR_HEIGHT = 120
CANVAS_TOP = TOOLBAR_HEIGHT
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 214, 220)
DARK_GRAY = (69, 75, 85)
BLUE = (45, 113, 235)

COLORS = [
    ("Black", BLACK),
    ("Red", (229, 57, 53)),
    ("Green", (67, 160, 71)),
    ("Blue", (30, 136, 229)),
    ("Yellow", (251, 192, 45)),
    ("Purple", (142, 68, 173)),
    ("Orange", (245, 124, 0)),
]

TOOLS = [
    ("pencil", "Pencil"),
    ("line", "Line"),
    ("rectangle", "Rect"),
    ("circle", "Circle"),
    ("square", "Square"),
    ("right_triangle", "R-Tri"),
    ("equilateral_triangle", "E-Tri"),
    ("rhombus", "Rhomb"),
    ("fill", "Fill"),
    ("text", "Text"),
    ("eraser", "Eraser"),
]

BRUSH_SIZES = {
    1: 2,
    2: 5,
    3: 10
}


def main():
    pygame.init()
    pygame.display.set_caption("TSIS2 Paint Application")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 20)
    text_font = pygame.font.SysFont("Arial", 28)

    canvas = pygame.Surface((WIDTH, HEIGHT - CANVAS_TOP))
    canvas.fill(WHITE)

    tool = "pencil"
    color = BLACK
    brush_size = 5
    eraser_size = 20

    drawing = False
    start_pos = None
    last_pos = None
    preview_pos = None

    text_mode = False
    text_pos = None
    typed_text = ""

    toolbar_items = layout_toolbar()

    while True:
        pressed = pygame.key.get_pressed()
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                if text_mode:
                    if event.key == pygame.K_RETURN:
                        if typed_text:
                            canvas.blit(text_font.render(typed_text, True, color), text_pos)

                        text_mode = False
                        typed_text = ""
                        text_pos = None

                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        typed_text = ""
                        text_pos = None

                    elif event.key == pygame.K_BACKSPACE:
                        typed_text = typed_text[:-1]

                    else:
                        typed_text += event.unicode

                    continue

                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_s and ctrl_held:
                    save_canvas(canvas)
                    continue

                if event.key == pygame.K_c and ctrl_held:
                    canvas.fill(WHITE)
                    continue

                if event.key == pygame.K_1:
                    brush_size = BRUSH_SIZES[1]

                elif event.key == pygame.K_2:
                    brush_size = BRUSH_SIZES[2]

                elif event.key == pygame.K_3:
                    brush_size = BRUSH_SIZES[3]

                elif event.key == pygame.K_p:
                    tool = "pencil"

                elif event.key == pygame.K_l:
                    tool = "line"

                elif event.key == pygame.K_r:
                    tool = "rectangle"

                elif event.key == pygame.K_o:
                    tool = "circle"

                elif event.key == pygame.K_s:
                    tool = "square"

                elif event.key == pygame.K_t:
                    tool = "right_triangle"

                elif event.key == pygame.K_q:
                    tool = "equilateral_triangle"

                elif event.key == pygame.K_h:
                    tool = "rhombus"

                elif event.key == pygame.K_f:
                    tool = "fill"

                elif event.key == pygame.K_x:
                    tool = "text"

                elif event.key == pygame.K_e:
                    tool = "eraser"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos

                    clicked = toolbar_hit_test(pos, toolbar_items)

                    if clicked:
                        kind, value = clicked

                        if kind == "tool":
                            tool = value
                            text_mode = False

                        elif kind == "color":
                            color = value
                            if tool == "eraser":
                                tool = "pencil"

                        elif kind == "size":
                            brush_size = value

                        elif kind == "clear":
                            canvas.fill(WHITE)

                        continue

                    if is_on_canvas(pos):
                        canvas_pos = to_canvas_pos(pos)

                        if tool == "fill":
                            flood_fill(canvas, canvas_pos, color)

                        elif tool == "text":
                            text_mode = True
                            text_pos = canvas_pos
                            typed_text = ""

                        else:
                            drawing = True
                            start_pos = canvas_pos
                            last_pos = canvas_pos
                            preview_pos = canvas_pos

                            if tool == "pencil":
                                pygame.draw.circle(canvas, color, canvas_pos, brush_size)

                            elif tool == "eraser":
                                pygame.draw.circle(canvas, WHITE, canvas_pos, eraser_size)

                elif event.button == 4:
                    brush_size = min(50, brush_size + 1)

                elif event.button == 5:
                    brush_size = max(1, brush_size - 1)

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = clamp_canvas_pos(event.pos)
                    preview_pos = current_pos

                    if tool == "pencil":
                        pygame.draw.line(canvas, color, last_pos, current_pos, brush_size)
                        last_pos = current_pos

                    elif tool == "eraser":
                        pygame.draw.line(canvas, WHITE, last_pos, current_pos, eraser_size)
                        last_pos = current_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = clamp_canvas_pos(event.pos)

                    if tool == "line":
                        pygame.draw.line(canvas, color, start_pos, end_pos, brush_size)

                    elif tool == "rectangle":
                        draw_rectangle(canvas, start_pos, end_pos, color, brush_size)

                    elif tool == "circle":
                        draw_circle(canvas, start_pos, end_pos, color, brush_size)

                    elif tool == "square":
                        draw_square(canvas, start_pos, end_pos, color, brush_size)

                    elif tool == "right_triangle":
                        draw_right_triangle(canvas, start_pos, end_pos, color, brush_size)

                    elif tool == "equilateral_triangle":
                        draw_equilateral_triangle(canvas, start_pos, end_pos, color, brush_size)

                    elif tool == "rhombus":
                        draw_rhombus(canvas, start_pos, end_pos, color, brush_size)

                    drawing = False
                    start_pos = None
                    last_pos = None
                    preview_pos = None

        screen.fill(GRAY)

        draw_toolbar(
            screen,
            toolbar_items,
            font,
            small_font,
            tool,
            color,
            brush_size,
            eraser_size
        )

        screen.blit(canvas, (0, CANVAS_TOP))

        if drawing and tool in (
            "line",
            "rectangle",
            "circle",
            "square",
            "right_triangle",
            "equilateral_triangle",
            "rhombus"
        ):
            draw_preview(screen, tool, start_pos, preview_pos, color, brush_size)

        if text_mode and text_pos is not None:
            screen_pos = from_canvas_pos(text_pos)
            text_surface = text_font.render(typed_text + "|", True, color)
            screen.blit(text_surface, screen_pos)

        pygame.display.flip()
        clock.tick(FPS)


def layout_toolbar():
    items = []

    x = 10
    y = 10
    button_width = 92
    button_height = 32
    gap = 6

    for tool_id, label in TOOLS:
        rect = pygame.Rect(x, y, button_width, button_height)
        items.append(("tool", tool_id, label, rect))

        x += button_width + gap

        if x + button_width > WIDTH - 130:
            x = 10
            y += 38

    x = 10
    y = 82

    for label, color in COLORS:
        rect = pygame.Rect(x, y, 30, 30)
        items.append(("color", color, label, rect))
        x += 38

    size_x = 395

    for size in [2, 5, 10]:
        rect = pygame.Rect(size_x, 82, 45, 30)
        items.append(("size", size, f"{size}px", rect))
        size_x += 52

    clear_rect = pygame.Rect(WIDTH - 110, 82, 95, 30)
    items.append(("clear", "clear", "Clear", clear_rect))

    return items


def toolbar_hit_test(pos, toolbar_items):
    if pos[1] >= TOOLBAR_HEIGHT:
        return None

    for kind, value, label, rect in toolbar_items:
        if rect.collidepoint(pos):
            return kind, value

    return None


def draw_toolbar(screen, toolbar_items, font, small_font, selected_tool, selected_color, brush_size, eraser_size):
    pygame.draw.rect(screen, (244, 246, 248), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (172, 178, 187), (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    for kind, value, label, rect in toolbar_items:
        if kind == "tool":
            active = value == selected_tool

            button_color = (226, 235, 255) if active else WHITE
            border_color = BLUE if active else DARK_GRAY

            pygame.draw.rect(screen, button_color, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=6)
            draw_centered_text(screen, font, label, DARK_GRAY, rect)

        elif kind == "color":
            pygame.draw.rect(screen, value, rect, border_radius=4)

            border_width = 4 if value == selected_color else 2
            border_color = BLUE if value == selected_color else DARK_GRAY

            pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=4)

        elif kind == "size":
            active = value == brush_size

            button_color = (226, 235, 255) if active else WHITE
            border_color = BLUE if active else DARK_GRAY

            pygame.draw.rect(screen, button_color, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=6)
            draw_centered_text(screen, font, label, DARK_GRAY, rect)

        elif kind == "clear":
            pygame.draw.rect(screen, WHITE, rect, border_radius=6)
            pygame.draw.rect(screen, DARK_GRAY, rect, width=2, border_radius=6)
            draw_centered_text(screen, font, label, DARK_GRAY, rect)

    clear_rect = None

    for kind, value, label, rect in toolbar_items:
        if kind == "clear":
            clear_rect = rect
            break

    hint1 = "P Pencil | L Line | R Rect | O Circle | S Square | T Right | Q Equil | H Rhomb"
    hint2 = f"F Fill | X Text | E Eraser | Brush: {brush_size}px | Eraser: {eraser_size}px | Ctrl+C Clear | Ctrl+S Save"

    text1 = small_font.render(hint1, True, DARK_GRAY)
    text2 = small_font.render(hint2, True, DARK_GRAY)

    max_right = clear_rect.left - 15 if clear_rect else WIDTH - 15

    x1 = max_right - text1.get_width()
    x2 = max_right - text2.get_width()

    x1 = max(620, x1)
    x2 = max(620, x2)

    screen.blit(text1, (x1, 82))
    screen.blit(text2, (x2, 102))


def draw_centered_text(screen, font, text, color, rect):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=rect.center))


def draw_preview(screen, tool, start, end, color, width):
    if start is None or end is None:
        return

    preview_start = from_canvas_pos(start)
    preview_end = from_canvas_pos(end)

    if tool == "line":
        pygame.draw.line(screen, color, preview_start, preview_end, width)

    elif tool == "rectangle":
        rect = rect_from_points(preview_start, preview_end)
        pygame.draw.rect(screen, color, rect, width)

    elif tool == "circle":
        radius = int(((preview_end[0] - preview_start[0]) ** 2 + (preview_end[1] - preview_start[1]) ** 2) ** 0.5)

        if radius > 0:
            pygame.draw.circle(screen, color, preview_start, radius, width)

    elif tool == "square":
        dx = preview_end[0] - preview_start[0]
        dy = preview_end[1] - preview_start[1]
        side = min(abs(dx), abs(dy))

        if side > 0:
            x = preview_start[0] if dx >= 0 else preview_start[0] - side
            y = preview_start[1] if dy >= 0 else preview_start[1] - side
            pygame.draw.rect(screen, color, pygame.Rect(x, y, side, side), width)

    elif tool == "right_triangle":
        points = [
            (preview_start[0], preview_start[1]),
            (preview_start[0], preview_end[1]),
            (preview_end[0], preview_end[1])
        ]

        pygame.draw.polygon(screen, color, points, width)

    elif tool == "equilateral_triangle":
        side = abs(preview_end[0] - preview_start[0])

        if side > 0:
            x1 = preview_start[0]
            x2 = preview_start[0] + side if preview_end[0] >= preview_start[0] else preview_start[0] - side
            height = int(side * (3 ** 0.5) / 2)

            if preview_end[1] >= preview_start[1]:
                points = [
                    (x1, preview_start[1]),
                    (x2, preview_start[1]),
                    ((x1 + x2) // 2, preview_start[1] + height)
                ]
            else:
                points = [
                    (x1, preview_start[1]),
                    (x2, preview_start[1]),
                    ((x1 + x2) // 2, preview_start[1] - height)
                ]

            pygame.draw.polygon(screen, color, points, width)

    elif tool == "rhombus":
        left = min(preview_start[0], preview_end[0])
        right = max(preview_start[0], preview_end[0])
        top = min(preview_start[1], preview_end[1])
        bottom = max(preview_start[1], preview_end[1])

        mid_x = (left + right) // 2
        mid_y = (top + bottom) // 2

        points = [
            (mid_x, top),
            (right, mid_y),
            (mid_x, bottom),
            (left, mid_y)
        ]

        pygame.draw.polygon(screen, color, points, width)


def is_on_canvas(pos):
    return pos[1] >= CANVAS_TOP


def to_canvas_pos(pos):
    return pos[0], pos[1] - CANVAS_TOP


def from_canvas_pos(pos):
    return pos[0], pos[1] + CANVAS_TOP


def clamp_canvas_pos(pos):
    x = max(0, min(WIDTH - 1, pos[0]))
    y = max(CANVAS_TOP, min(HEIGHT - 1, pos[1]))
    return x, y - CANVAS_TOP


if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()