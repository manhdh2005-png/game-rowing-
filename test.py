import pygame
import random
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rehab Rowing - Risk vs Control")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(__file__)

# Load assets
background = pygame.image.load(os.path.join(BASE_DIR, "river.png"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

boat_img = pygame.image.load(os.path.join(BASE_DIR, "boat.png"))
boat_img = pygame.transform.scale(boat_img, (80, 50))

obstacle_images = [
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "log.png")), (60, 40)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "crocodile.png")), (80, 50)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "person.png")), (60, 60))
]

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 24)

# Game state
state = "menu"
score = 0
high_score = 0

# Player
boat = pygame.Rect(WIDTH//2 - 40, HEIGHT - 100, 80, 50)
boat_speed = 6

# Obstacles
obstacles = []
spawn_timer = 0

# Background scroll
bg_y = 0

# Rehab variables (RISK vs CONTROL)
speed = 3.0
min_speed = 2.0
max_speed = 9.0
shield = 0

# Simulated stroke (replace later with sensor)
def check_stroke():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        return "correct"   # chèo đúng
    if keys[pygame.K_s]:
        return "wrong"     # chèo sai
    return None

# Button helper
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
        title = font.render("REHAB ROWING", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        if draw_button("BAT DAU", 300, 260, 200, 50):
            state = "play"
            score = 0
            obstacles = []
            speed = 3.0
            shield = 0
            boat.x = WIDTH//2 - 40

        if draw_button("THOAT", 300, 330, 200, 50):
            running = False

    # ===== GAME =====
    elif state == "play":
        # Stroke logic (Risk vs Control)
        result = check_stroke()
        if result == "correct":
            speed = max(min_speed, speed - 0.5)   # đúng -> chậm, dễ kiểm soát
            shield += 1  # mỗi lần chèo đúng nhận 1 khiên (dùng 1 lần)                           # + lá chắn
        elif result == "wrong":
            speed = min(max_speed, speed + 0.7)   # sai -> nhanh, khó điều khiển

        # Background scroll (speed-controlled)
        bg_y += speed
        if bg_y >= HEIGHT:
            bg_y = 0
        screen.blit(background, (0, bg_y - HEIGHT))
        screen.blit(background, (0, bg_y))

        # Horizontal control (harder when fast)
        keys = pygame.key.get_pressed()
        control_factor = max(0.6, 1.2 - speed*0.05)  # nhanh -> khó điều khiển
        if keys[pygame.K_LEFT]:
            boat.x -= boat_speed * control_factor
        if keys[pygame.K_RIGHT]:
            boat.x += boat_speed * control_factor
        boat.x = max(0, min(WIDTH - boat.width, boat.x))

        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer > 40:
            spawn_timer = 0
            x = random.randint(0, WIDTH - 60)
            img = random.choice(obstacle_images)
            rect = img.get_rect()
            rect.topleft = (x, -60)
            obstacles.append((img, rect))

        # Move & collision
        new_obstacles = []
        for img, rect in obstacles:
            rect.y += speed
            if rect.y < HEIGHT:
                new_obstacles.append((img, rect))

            if boat.colliderect(rect):
                if shield > 0:
                    shield -= 1  # xuyên vật
                else:
                    if score > high_score:
                        high_score = score
                    state = "menu"

        obstacles = new_obstacles

        # Draw
        screen.blit(boat_img, (boat.x, boat.y))
        for img, rect in obstacles:
            screen.blit(img, rect.topleft)

        # HUD
        score += int(speed)
        screen.blit(small_font.render(f"Score: {score}", True, (255,255,255)), (10, 10))
        screen.blit(small_font.render(f"Speed: {round(speed,1)}", True, (255,255,0)), (10, 35))
        screen.blit(small_font.render(f"Shield: {shield}", True, (0,255,255)), (10, 60))

        # Warning when too fast
        if speed > 7.5:
            warn = small_font.render("WARNING: TOO FAST!", True, (255,80,80))
            screen.blit(warn, (WIDTH//2 - warn.get_width()//2, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
