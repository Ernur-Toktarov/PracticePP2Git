"""
paint.py — TSIS 2: Paint Application — Extended Drawing Tools

Управление:
  Инструменты:  P=pencil  L=line  R=rect  C=circle
                S=square  T=right_triangle  E=equil_triangle
                H=rhombus  F=fill  X=eraser  W=text
  Размер кисти: 1=small(2px)  2=medium(5px)  3=large(10px)
  Сохранить:    Ctrl+S  → canvas_YYYY-MM-DD_HH-MM-SS.png
  Выход:        Escape (вне режима текста)
"""

import pygame
import sys
from datetime import datetime
from tools import flood_fill, draw_shape, BRUSH_SIZES, COLORS, SHAPE_TOOLS

# ── Размеры окна ──────────────────────────────────────────────
WIN_W, WIN_H = 1100, 700
TOOLBAR_H    = 60
CANVAS_TOP   = TOOLBAR_H
CANVAS_H     = WIN_H - TOOLBAR_H

# ── Цвета UI ─────────────────────────────────────────────────
BG_COLOR      = (240, 240, 240)
TOOLBAR_COLOR = (50, 50, 50)
CANVAS_COLOR  = (255, 255, 255)
HIGHLIGHT     = (255, 215, 0)
TEXT_UI       = (220, 220, 220)


# ══════════════════════════════════════════════════════════════
# TOOLBAR
# ══════════════════════════════════════════════════════════════

TOOL_LABELS = {
    "pencil": "P:Pencil", "line": "L:Line",
    "rectangle": "R:Rect", "circle": "C:Circle",
    "square": "S:Square", "right_triangle": "T:RTri",
    "equilateral_triangle": "E:EqTri", "rhombus": "H:Rhomb",
    "fill": "F:Fill", "eraser": "X:Erase", "text": "W:Text",
}

SIZE_LABELS = {"small": "1:S", "medium": "2:M", "large": "3:L"}


def draw_toolbar(screen, font, cur_tool, cur_size, cur_color):
    pygame.draw.rect(screen, TOOLBAR_COLOR, (0, 0, WIN_W, TOOLBAR_H))

    # ── Инструменты ──
    x = 5
    for tool, label in TOOL_LABELS.items():
        color = HIGHLIGHT if tool == cur_tool else (100, 100, 100)
        rect  = pygame.Rect(x, 5, 68, 24)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        txt = font.render(label, True, (0,0,0))
        screen.blit(txt, (x+3, 9))
        x += 72

    # ── Размеры кисти ──
    x = 5
    for size, label in SIZE_LABELS.items():
        color = HIGHLIGHT if size == cur_size else (100, 100, 100)
        rect  = pygame.Rect(x, 32, 52, 22)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        txt = font.render(label, True, (0,0,0))
        screen.blit(txt, (x+3, 35))
        x += 56

    # ── Палитра цветов ──
    px = 180
    for i, col in enumerate(COLORS):
        rect = pygame.Rect(px, 33, 20, 20)
        pygame.draw.rect(screen, col, rect)
        if col == cur_color:
            pygame.draw.rect(screen, HIGHLIGHT, rect, 2)
        px += 23

    # ── Текущий цвет ──
    pygame.draw.rect(screen, cur_color, (px+5, 33, 30, 20))
    lbl = font.render("Ctrl+S=Save", True, TEXT_UI)
    screen.blit(lbl, (WIN_W - 110, 20))


def get_toolbar_click(pos, cur_tool, cur_size, cur_color):
    """Возвращает (tool, size, color) после клика по тулбару."""
    x, y = pos
    # инструменты (строка 1)
    tx = 5
    for tool in TOOL_LABELS:
        if tx <= x <= tx+68 and 5 <= y <= 29:
            return tool, cur_size, cur_color
        tx += 72
    # размеры (строка 2)
    sx = 5
    for size in SIZE_LABELS:
        if sx <= x <= sx+52 and 32 <= y <= 54:
            return cur_tool, size, cur_color
        sx += 56
    # цвета
    px = 180
    for col in COLORS:
        if px <= x <= px+20 and 33 <= y <= 53:
            return cur_tool, cur_size, col
        px += 23
    return cur_tool, cur_size, cur_color


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint — TSIS 2")

    font      = pygame.font.SysFont("Arial", 12, bold=True)
    text_font = pygame.font.SysFont("Arial", 24)

    # Холст
    canvas = pygame.Surface((WIN_W, CANVAS_H))
    canvas.fill(CANVAS_COLOR)

    # Состояние
    cur_tool   = "pencil"
    cur_size   = "medium"
    cur_color  = (0, 0, 0)
    drawing    = False
    start_pos  = None
    prev_pos   = None

    # Для line preview
    preview_canvas = None

    # Для текстового инструмента
    text_mode   = False
    text_cursor = (0, 0)
    text_buffer = ""

    clock = pygame.time.Clock()

    while True:
        brush = BRUSH_SIZES[cur_size]

        for event in pygame.event.get():

            # ── QUIT ──────────────────────────────────────────
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── КЛАВИАТУРА ────────────────────────────────────
            elif event.type == pygame.KEYDOWN:

                # Текстовый режим
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Рендерим текст на холст
                        surf = text_font.render(text_buffer, True, cur_color)
                        canvas.blit(surf, text_cursor)
                        text_mode   = False
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode:
                            text_buffer += event.unicode
                    continue

                # Горячие клавиши инструментов
                key_tool = {
                    pygame.K_p: "pencil",    pygame.K_l: "line",
                    pygame.K_r: "rectangle", pygame.K_c: "circle",
                    pygame.K_s: "square",    pygame.K_t: "right_triangle",
                    pygame.K_e: "equilateral_triangle",
                    pygame.K_h: "rhombus",   pygame.K_f: "fill",
                    pygame.K_x: "eraser",    pygame.K_w: "text",
                }.get(event.key)
                if key_tool:
                    cur_tool = key_tool

                # Размер кисти 1/2/3
                if event.key == pygame.K_1: cur_size = "small"
                if event.key == pygame.K_2: cur_size = "medium"
                if event.key == pygame.K_3: cur_size = "large"

                # Ctrl+S — сохранить
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    ts       = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"canvas_{ts}.png"
                    pygame.image.save(canvas, filename)
                    pygame.display.set_caption(f"Saved: {filename}")

                # Escape — выход
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            # ── МЫШЬ: нажатие ────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Клик по тулбару
                if my < TOOLBAR_H:
                    cur_tool, cur_size, cur_color = get_toolbar_click(
                        (mx, my), cur_tool, cur_size, cur_color)
                    continue

                # Координата на холсте
                cx, cy = mx, my - TOOLBAR_H

                # Fill
                if cur_tool == "fill":
                    flood_fill(canvas, cx, cy, cur_color)
                    continue

                # Text
                if cur_tool == "text":
                    text_mode   = True
                    text_cursor = (cx, cy)
                    text_buffer = ""
                    continue

                # Начало рисования
                drawing  = True
                start_pos = (cx, cy)
                prev_pos  = (cx, cy)

                if cur_tool == "line":
                    preview_canvas = canvas.copy()

            # ── МЫШЬ: движение ───────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                if not drawing:
                    continue
                mx, my = event.pos
                cx, cy = mx, my - TOOLBAR_H

                if cur_tool == "pencil":
                    pygame.draw.line(canvas, cur_color, prev_pos, (cx,cy), brush)
                    prev_pos = (cx, cy)

                elif cur_tool == "eraser":
                    pygame.draw.circle(canvas, CANVAS_COLOR, (cx,cy), brush*2)
                    prev_pos = (cx, cy)

                elif cur_tool == "line":
                    # Live preview
                    preview_canvas = preview_canvas  # уже скопирован при mousedown
                    pass  # preview рисуем при отрисовке экрана

                # Для shape-инструментов — preview не рисуем в motion (рисуем в отрисовке)
                prev_pos = (cx, cy)

            # ── МЫШЬ: отпускание ─────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP:
                if not drawing:
                    continue
                drawing = False
                mx, my  = event.pos
                cx, cy  = mx, my - TOOLBAR_H

                if cur_tool == "line":
                    draw_shape(canvas, "line", cur_color, start_pos, (cx,cy), brush)
                    preview_canvas = None

                elif cur_tool in SHAPE_TOOLS and cur_tool != "line":
                    draw_shape(canvas, cur_tool, cur_color, start_pos, (cx,cy), brush)

        # ══════════════════════════════════════════════════════
        # ОТРИСОВКА
        # ══════════════════════════════════════════════════════
        screen.fill(BG_COLOR)

        # Холст
        display_canvas = canvas.copy()

        # Line live preview
        if drawing and cur_tool == "line" and preview_canvas and start_pos:
            display_canvas = preview_canvas.copy()
            mx, my = pygame.mouse.get_pos()
            cx, cy = mx, my - TOOLBAR_H
            pygame.draw.line(display_canvas, cur_color, start_pos, (cx,cy), brush)

        # Shape live preview (все остальные фигуры)
        if drawing and cur_tool in SHAPE_TOOLS and cur_tool != "line" and start_pos:
            mx, my = pygame.mouse.get_pos()
            cx, cy = mx, my - TOOLBAR_H
            draw_shape(display_canvas, cur_tool, cur_color, start_pos, (cx,cy), brush)

        # Текстовый курсор / preview
        if text_mode:
            preview = text_font.render(text_buffer + "|", True, cur_color)
            display_canvas.blit(preview, text_cursor)

        screen.blit(display_canvas, (0, CANVAS_TOP))
        draw_toolbar(screen, font, cur_tool, cur_size, cur_color)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
