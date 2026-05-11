import pygame
import random
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rehab Rowing - Race Mode")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(__file__)

# Load ảnh
background = pygame.image.load(os.path.join(BASE_DIR, "river.png"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

boat_player_img = pygame.image.load(os.path.join(BASE_DIR, "boat.png"))
boat_player_img = pygame.transform.scale(boat_player_img, (80, 50))

boat_ai_img = pygame.transform.rotate(boat_player_img, 0)

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 24)

# State
state = "menu"

# Player
player_x = WIDTH//2 - 150
player_y = HEIGHT - 100
player_speed = 3

# AI
ai_x = WIDTH//2 + 50
ai_y = HEIGHT - 100
ai_speed = 3.5

# Background scroll
bg_y = 0

# Distance
player_distance = 0
ai_distance = 0

# Stroke simulation (sau này thay bằng cảm biến)
def check_stroke():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        return "correct"
    if keys[pygame.K_s]:
        return "wrong"
    return None

# Button
def draw_button(text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    color = (0, 200, 0) if rect.collidepoint(mouse) else (0, 150, 0)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    txt = small_font.render(text, True, (255,255,255))
    screen.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))
    return rect.collidepoint(mouse) and click[0]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== MENU =====
    if state == "menu":
        screen.blit(background, (0, 0))

        title = font.render("ROWING RACE REHAB", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        if draw_button("BAT DAU", 300, 300, 200, 50):
            state = "play"
            player_speed = 3
            ai_speed = 3.5
            player_distance = 0
            ai_distance = 0

        if draw_button("THOAT", 300, 370, 200, 50):
            running = False

    # ===== GAME =====
    elif state == "play":
        result = check_stroke()

        # Logic rehab
        if result == "correct":
            player_speed = min(8, player_speed + 0.3)
        elif result == "wrong":
            player_speed = max(1.5, player_speed - 0.5)

        # AI chạy ổn định
        ai_speed += random.uniform(-0.05, 0.05)
        ai_speed = max(2.5, min(4.5, ai_speed))

        # Background scroll theo người chơi
        bg_y += player_speed
        if bg_y >= HEIGHT:
            bg_y = 0

        screen.blit(background, (0, bg_y - HEIGHT))
        screen.blit(background, (0, bg_y))

        # Update distance
        player_distance += player_speed
        ai_distance += ai_speed

        # Draw boats
        screen.blit(boat_player_img, (player_x, player_y))
        screen.blit(boat_ai_img, (ai_x, ai_y))

        # HUD
        screen.blit(small_font.render(f"Your Speed: {round(player_speed,1)}", True, (255,255,255)), (10, 10))
        screen.blit(small_font.render(f"AI Speed: {round(ai_speed,1)}", True, (255,255,0)), (10, 35))

        screen.blit(small_font.render(f"Your Distance: {int(player_distance)}", True, (0,255,255)), (10, 60))
        screen.blit(small_font.render(f"AI Distance: {int(ai_distance)}", True, (255,100,100)), (10, 85))

        # Determine winner
        if player_distance >= 2000:
            state = "win"
        elif ai_distance >= 2000:
            state = "lose"

    # ===== WIN =====
    elif state == "win":
        screen.fill((0,0,0))
        txt = font.render("BAN THANG!", True, (0,255,0))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 250))

        if draw_button("CHOI LAI", 300, 350, 200, 50):
            state = "menu"

    # ===== LOSE =====
    elif state == "lose":
        screen.fill((0,0,0))
        txt = font.render("BAN THUA!", True, (255,0,0))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 250))

        if draw_button("THU LAI", 300, 350, 200, 50):
            state = "menu"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
