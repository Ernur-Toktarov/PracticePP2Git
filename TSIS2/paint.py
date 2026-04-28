import pygame
import sys
import datetime
from tools import draw_line, normalize_rect, flood_fill

pygame.init()
pygame.mouse.set_visible(False)

WIDTH, HEIGHT = 900, 600
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Paint")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

colors = [
    BLACK, (255, 0, 0), (0, 180, 0),
    (0, 0, 255), (255, 255, 0),
    (160, 32, 240), (255, 140, 0)
]

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

current_color = BLACK
brush_size = 5
tool = "brush"

drawing = False
start_pos = None
last_pos = None
preview_pos = None

typing = False
text = ""
text_pos = (0, 0)

save_message = ""
save_time = 0

CLEAR_BTN = pygame.Rect(WIDTH - 120, 20, 100, 40)

# ---------------- TEXT FIX ----------------
def commit_text():
    global text, typing
    if text:
        canvas.blit(font.render(text, True, current_color), text_pos)
    text = ""
    typing = False
# ------------------------------------------

def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    msg = "B:Brush L:Line R:Rect O:Circle S:Square F:Fill X:Text | Ctrl+S Save"
    screen.blit(font.render(msg, True, BLACK), (10, 55))

    for i, color in enumerate(colors):
        rect = pygame.Rect(20 + i * 45, 10, 35, 35)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if current_color == color else 1)

    pygame.draw.rect(screen, RED, CLEAR_BTN)
    pygame.draw.rect(screen, BLACK, CLEAR_BTN, 2)
    screen.blit(font.render("Clear", True, WHITE), (CLEAR_BTN.x + 20, CLEAR_BTN.y + 10))

while True:
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if typing:
                commit_text()

            if my < TOOLBAR_HEIGHT:
                if CLEAR_BTN.collidepoint(mx, my):
                    canvas.fill(WHITE)
                else:
                    idx = (mx - 20) // 45
                    if 0 <= idx < len(colors):
                        current_color = colors[idx]

            else:
                if tool == "fill":
                    flood_fill(canvas, mx, my - TOOLBAR_HEIGHT, current_color)

                elif tool == "text":
                    typing = True
                    text = ""
                    text_pos = (mx, my - TOOLBAR_HEIGHT)

                else:
                    drawing = True
                    start_pos = (mx, my - TOOLBAR_HEIGHT)
                    last_pos = start_pos
                    preview_pos = start_pos

        if event.type == pygame.KEYDOWN:

            
            if typing:
                if event.key == pygame.K_RETURN:
                    commit_text()

                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]

                elif event.key == pygame.K_ESCAPE:
                    commit_text()

                else:
                    text += event.unicode

                continue

            if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                filename = f"art_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                pygame.image.save(canvas, filename)
                save_message = f"Saved: {filename}"
                save_time = pygame.time.get_ticks()
                print("SAVED:", filename)

           
            elif event.key == pygame.K_b:
                tool = "brush"
            elif event.key == pygame.K_l:
                tool = "line"
            elif event.key == pygame.K_r:
                tool = "rectangle"
            elif event.key == pygame.K_o:
                tool = "circle"
            elif event.key == pygame.K_s:
                tool = "square"
            elif event.key == pygame.K_f:
                tool = "fill"
            elif event.key == pygame.K_x:
                tool = "text"
            elif event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 15

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                preview_pos = (mx, my - TOOLBAR_HEIGHT)
                if tool == "brush":
                    draw_line(canvas, current_color, last_pos, preview_pos, brush_size)
                    last_pos = preview_pos

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                rect = normalize_rect(start_pos, preview_pos)

                if tool == "line":
                    pygame.draw.line(canvas, current_color, start_pos, preview_pos, brush_size)

                elif tool == "rectangle":
                    pygame.draw.rect(canvas, current_color, rect, brush_size)

                elif tool == "circle":
                    pygame.draw.ellipse(canvas, current_color, rect, brush_size)

                elif tool == "square":
                    side = min(rect.width, rect.height)
                    pygame.draw.rect(canvas, current_color,
                                     (rect.left, rect.top, side, side), brush_size)

                drawing = False

    
    screen.fill(WHITE)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    if drawing and tool != "brush":
        rect = normalize_rect(start_pos, preview_pos)
        d_rect = rect.move(0, TOOLBAR_HEIGHT)
        d_start = (start_pos[0], start_pos[1] + TOOLBAR_HEIGHT)
        d_prev = (preview_pos[0], preview_pos[1] + TOOLBAR_HEIGHT)

        if tool == "line":
            pygame.draw.line(screen, current_color, d_start, d_prev, brush_size)
        elif tool == "rectangle":
            pygame.draw.rect(screen, current_color, d_rect, brush_size)
        elif tool == "circle":
            pygame.draw.ellipse(screen, current_color, d_rect, brush_size)
        elif tool == "square":
            side = min(rect.width, rect.height)
            pygame.draw.rect(screen, current_color,
                             (d_rect.left, d_rect.top, side, side), brush_size)

    draw_toolbar()

    if typing:
        screen.blit(font.render(text + "|", True, current_color),
                    (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

  
    if save_message:
        if pygame.time.get_ticks() - save_time < 2000:
            screen.blit(font.render(save_message, True, BLACK),
                        (WIDTH - 300, HEIGHT - 30))
        else:
            save_message = ""

    pygame.draw.circle(screen, BLACK, (mx, my), brush_size, 1)

    pygame.display.flip()
    clock.tick(120)