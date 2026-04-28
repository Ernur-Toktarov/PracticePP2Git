import pygame
import datetime
import os
import sys

pygame.init()

W, H = 900, 900
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

base = os.path.dirname(__file__)
img_path = os.path.join(base, "images")

# --- LOAD ---
face = pygame.image.load(os.path.join(img_path, "clock.png")).convert_alpha()
mickey = pygame.image.load(os.path.join(img_path, "mickey.png")).convert_alpha()
left_hand = pygame.image.load(os.path.join(img_path, "hand_left.png")).convert_alpha()
right_hand = pygame.image.load(os.path.join(img_path, "hand_right.png")).convert_alpha()

# --- SCALE ---
face = pygame.transform.smoothscale(face, (900, 700))   # +10%
mickey = pygame.transform.smoothscale(mickey, (370, 630))  # +25%
left_hand = pygame.transform.smoothscale(left_hand, (100, 190))   # уменьшили
right_hand = pygame.transform.smoothscale(right_hand, (100, 190))

CENTER = (W // 2, H // 2)

# 🔥 смещение центра вправо
HAND_CENTER = (CENTER[0] + 20, CENTER[1] + 40)


def draw_hand(surface, image, angle):
    pivot = (image.get_width() // 2, image.get_height() - 5)

    rotated = pygame.transform.rotate(image, -angle)

    offset = pygame.math.Vector2(pivot)
    rotated_offset = offset.rotate(angle)

    rect = rotated.get_rect(center=(
        HAND_CENTER[0] - rotated_offset.x,
        HAND_CENTER[1] - rotated_offset.y
    ))

    surface.blit(rotated, rect)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    now = datetime.datetime.now()

    sec = now.second
    minute = now.minute

    sec_angle = sec * 6
    min_angle = minute * 6

    screen.fill((255, 255, 255))

    # --- CLOCK ---
    face_rect = face.get_rect(center=CENTER)
    screen.blit(face, face_rect)

    # --- MICKEY (чуть ниже центра)
    mickey_rect = mickey.get_rect(center=(CENTER[0], CENTER[1] + 90))
    screen.blit(mickey, mickey_rect)

    # --- HANDS ---
    draw_hand(screen, right_hand, sec_angle)
    draw_hand(screen, left_hand, min_angle)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()