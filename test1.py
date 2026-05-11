import cv2
import mediapipe as mp
import pygame
import math
import sys
import os
import time
import database # Import file CSDL của chúng ta

# --- FIX LỖI KHÔNG TÌM THẤY ẢNH ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ----------------------------------

# Khởi tạo CSDL
database.create_tables()

# ==========================================
# 1. HÀM TÍNH GÓC TOÁN HỌC
# ==========================================
def calculate_angle(a, b, c):
    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return int(angle)

# ==========================================
# 2. KHỞI TẠO PYGAME & TẢI HÌNH ẢNH
# ==========================================
pygame.init()
WIDTH, HEIGHT = 1200, 675
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Rehab Racing: Kỹ Thuật Y Sinh Pro")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont(None, 70)
font_medium = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 30)

game_state = "login" 
winner = ""
current_cccd = "" 

# --- THÔNG SỐ VẬT LÝ & CHIẾN ĐẤU ---
player_y = HEIGHT - 120
ai_y = HEIGHT - 120
ai_speed = 0.45           
player_base_speed = 0.8  
player_speed = 0         
vong_cheo = 0        
stroke_stage = "Hay bat dau vong cheo"
goc_khuyu_tay = 0
goc_vai = 0 

player_health = 100
boss_health = 100
player_x_drift = 0  
boss_x_drift = 0
collision_timer = 0 

# ==========================================
# --- CÁC BIẾN THEO DÕI ĐỘNG HỌC (KINEMATICS) ---
# ==========================================
max_angle_session = 0
min_angle_session = 180
total_strokes_session = 0

prev_angle = 0
prev_time = time.time()
prev_velocity = 0
sum_velocity = 0
velocity_count = 0
max_acceleration = 0

cycle_start_time = 0
sum_cycle_time = 0
list_cycle_times = []
session_saved = False

# ==========================================
# --- TẢI HÌNH ẢNH (ASSETS) VÀ FONT ---
# ==========================================
use_images = os.path.exists("assets/river.png") and os.path.exists("assets/player_reach.png") and os.path.exists("assets/player_drive.png") and os.path.exists("assets/ai_0.png") and os.path.exists("assets/ai_1.png") and os.path.exists("assets/menu_bg.jpg")

if use_images:
    try:
        level_menu_bg_img = pygame.image.load("assets/level_menu_bg.png").convert()
        level_menu_bg_img = pygame.transform.scale(level_menu_bg_img, (WIDTH, HEIGHT))

        menu_bg_img = pygame.image.load("assets/menu_bg.jpg").convert()
        menu_bg_img = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))

        bg_img = pygame.image.load("assets/river.png").convert()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        
        reach_img = pygame.image.load("assets/player_reach.png").convert_alpha()
        reach_img = pygame.transform.scale(reach_img, (120, 100))
        
        drive_img = pygame.image.load("assets/player_drive.png").convert_alpha()
        drive_img = pygame.transform.scale(drive_img, (120, 100))
        
        player_sprites = [reach_img, reach_img, drive_img, reach_img]

        ai_frames = [
            pygame.transform.scale(pygame.image.load("assets/ai_0.png").convert_alpha(), (120, 100)),
            pygame.transform.scale(pygame.image.load("assets/ai_1.png").convert_alpha(), (120, 100))
        ]
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy đủ file ảnh trong thư mục assets!")
        use_images = False 

# Tải background Guide.jpg (Lưu ý viết hoa chữ G cho đúng tên file bạn gửi)
try:
    guide_bg_img = pygame.image.load("assets/Guide.jpg").convert()
    guide_bg_img = pygame.transform.scale(guide_bg_img, (WIDTH, HEIGHT))
    print("✅ Da tai thanh cong anh Guide.jpg!")
except Exception as e:
    print(f"❌ LOI TAI ANH GUIDE: {e}")
    guide_bg_img = None
try:
    logo_img = pygame.image.load("assets/logo.png").convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (600, 280)) 
except:
    logo_img = None

try:
    instruct_font_pixel = pygame.font.Font("assets/stardew_valley_font.ttf", 60)
    button_font_pixel = pygame.font.Font("assets/stardew_valley_font.ttf", 35)
except:
    instruct_font_pixel = pygame.font.SysFont("impact", 60)
    button_font_pixel = pygame.font.SysFont("impact", 35)

ai_frame_index = 0
ai_timer = 0

# ==========================================
# --- KHỞI TẠO NÚT BẤM ---
# ==========================================
button_width, button_height = 220, 60
start_y = 220
spacing = 80 

level1_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y, button_width, button_height)
level2_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing, button_width, button_height)
level3_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*2, button_width, button_height)
guide_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*3, button_width, button_height)
exit_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*4, button_width, button_height)

prev_game_state = ""
resume_rect = pygame.Rect(WIDTH//2 - button_width//2, 280, button_width, button_height)
levels_rect = pygame.Rect(WIDTH//2 - button_width//2, 280 + spacing, button_width, button_height)
main_menu_rect = pygame.Rect(WIDTH//2 - button_width//2, 280 + spacing*2, button_width, button_height)

pause_btn_rect = pygame.Rect(WIDTH - 130, 80, 110, 45) 
login_box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 40, 400, 80)

def draw_button(win, rect, text, font):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(win, (222, 184, 135), rect, border_radius=10)
    else:
        pygame.draw.rect(win, (205, 133, 63), rect, border_radius=10)
        
    pygame.draw.rect(win, (101, 67, 33), rect, width=4, border_radius=10)
    instruct_outline = font.render(text, True, (40, 20, 0)) 
    instruct_outline_rect = instruct_outline.get_rect(center=(rect.centerx + 3, rect.centery + 3)) 
    win.blit(instruct_outline, instruct_outline_rect) 
    instruct_main = font.render(text, True, (255, 215, 0)) 
    instruct_main_rect = instruct_main.get_rect(center=rect.center)
    win.blit(instruct_main, instruct_main_rect)

# ==========================================
# 3. KHỞI TẠO CAMERA & MEDIA PIPE
# ==========================================
cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# ==========================================
# 4. VÒNG LẶP CHÍNH
# ==========================================
running = True
while running:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == "login":
                if event.key == pygame.K_RETURN: 
                    if len(current_cccd) > 0:
                        database.add_patient(current_cccd, f"BN_{current_cccd}") 
                        game_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    current_cccd = current_cccd[:-1]
                else:
                    if event.unicode.isdigit() and len(current_cccd) < 12: 
                        current_cccd += event.unicode

            elif event.key == pygame.K_SPACE:
                if game_state == "menu":
                    game_state = "level_menu"
                elif game_state == "game_over":
                    game_state = "menu" 
                elif game_state == "guide":
                    game_state = "level_menu"
                    
            elif event.key == pygame.K_ESCAPE:
                if game_state in ["playing_level1", "playing_level2", "playing_level3"]:
                    prev_game_state = game_state
                    game_state = "paused"
                elif game_state == "paused":
                    game_state = prev_game_state
                elif game_state == "login":
                    running = False 
                    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                mouse_pos = event.pos
                if game_state == "paused":
                    if resume_rect.collidepoint(mouse_pos):
                        game_state = prev_game_state 
                    elif levels_rect.collidepoint(mouse_pos):
                        game_state = "level_menu"    
                    elif main_menu_rect.collidepoint(mouse_pos):
                        game_state = "menu"          
                        
                elif game_state in ["playing_level1", "playing_level2", "playing_level3"]:
                    if pause_btn_rect.collidepoint(mouse_pos):
                        prev_game_state = game_state
                        game_state = "paused"
                
                elif game_state == "level_menu":
                    if exit_rect.collidepoint(mouse_pos):
                        running = False 
                    elif guide_rect.collidepoint(mouse_pos):
                        game_state = "guide"
                    elif level1_rect.collidepoint(mouse_pos) or level2_rect.collidepoint(mouse_pos) or level3_rect.collidepoint(mouse_pos):
                        player_y = HEIGHT - 120
                        ai_y = HEIGHT - 120
                        player_speed = 0 
                        vong_cheo = 0
                        player_health = 100
                        boss_health = 100
                        player_x_drift = 0
                        boss_x_drift = 0
                        collision_timer = 0
                        stroke_stage = "Bat dau vong cheo moi"
                        
                        max_angle_session = 0
                        min_angle_session = 180
                        total_strokes_session = 0
                        prev_angle = 0
                        prev_velocity = 0
                        sum_velocity = 0
                        velocity_count = 0
                        max_acceleration = 0
                        sum_cycle_time = 0
                        session_saved = False
                        
                        if level1_rect.collidepoint(mouse_pos): game_state = "playing_level1"
                        if level2_rect.collidepoint(mouse_pos): game_state = "playing_level2"
                        if level3_rect.collidepoint(mouse_pos): game_state = "playing_level3"

    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            
            vai = [landmarks[12].x, landmarks[12].y]
            khuyu = [landmarks[14].x, landmarks[14].y]
            co_tay = [landmarks[16].x, landmarks[16].y]
            hong = [landmarks[24].x, landmarks[24].y] 
            
            goc_khuyu_tay = calculate_angle(vai, khuyu, co_tay)
            goc_vai = calculate_angle(hong, vai, khuyu) 

            if game_state in ["playing_level1", "playing_level2", "playing_level3"]:
                current_time = time.time()
                dt = current_time - prev_time
                if dt > 0:
                    angular_vel = abs(goc_khuyu_tay - prev_angle) / dt
                    sum_velocity += angular_vel
                    velocity_count += 1
                    
                    angular_accel = abs(angular_vel - prev_velocity) / dt
                    if angular_accel > max_acceleration:
                        max_acceleration = angular_accel
                        
                    prev_angle = goc_khuyu_tay
                    prev_velocity = angular_vel
                prev_time = current_time
                
                if goc_khuyu_tay > max_angle_session: max_angle_session = goc_khuyu_tay
                if goc_khuyu_tay < min_angle_session: min_angle_session = goc_khuyu_tay

                is_duoi = goc_khuyu_tay > 105  
                is_gap = goc_khuyu_tay < 85    
                is_vai_cao = goc_vai > 60  
                is_vai_thap = goc_vai < 45 
                
                if vong_cheo == 0 and is_vai_cao and is_gap:
                    vong_cheo = 1
                    stroke_stage = "1. Vai da len. Bay gio DUOI TAY ra!"
                    cycle_start_time = time.time() 
                    
                elif vong_cheo == 1 and is_duoi: 
                    vong_cheo = 2
                    stroke_stage = "2. Tot! Keo cui cho ve va GAP TAY!"
                elif vong_cheo == 2 and is_gap and is_vai_thap:
                    vong_cheo = 3
                    stroke_stage = "3. Da keo. Nang vai len de tiep tuc!"
                elif vong_cheo == 3 and is_vai_cao:
                    vong_cheo = 1  
                    stroke_stage = "HOAN THANH! Tiep tuc duoi tay!"
                    
                    total_strokes_session += 1
                    if cycle_start_time > 0:
                        t_cycle = time.time() - cycle_start_time
                        sum_cycle_time += t_cycle
                        list_cycle_times.append(t_cycle)
                    cycle_start_time = time.time() 
                    
                    if game_state == "playing_level1": player_speed = 12.0
                    elif game_state == "playing_level2": player_speed = 9.0
                    elif game_state == "playing_level3": player_speed = 6.0

            cv2.rectangle(img, (5, 5), (450, 180), (0, 0, 0), -1)
            cv2.putText(img, f"Goc Khuyu: {goc_khuyu_tay} deg", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(img, f"Goc Vai: {goc_vai} deg", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(img, f"Buoc hien tai: {vong_cheo}/4", (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(img, stroke_stage, (15, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

        cv2.imshow("He Thong Giam Sat Rehab", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ==========================================
    # --- GIAO DIỆN GAME (WIDESCREEN) ---
    # ==========================================
    if use_images:
        if game_state in ["login", "menu"]:
            win.blit(menu_bg_img, (0, 0))
        elif game_state == "level_menu":
            if 'level_menu_bg_img' in locals() and level_menu_bg_img:
                win.blit(level_menu_bg_img, (0, 0))
        elif game_state in ["playing_level1", "playing_level2", "playing_level3", "paused", "game_over"]:
            win.blit(bg_img, (0, 0))
    else:
        win.fill((173, 216, 230)) 

    if game_state == "login":
        title_surf = font_large.render("NHAP CCCD BENH NHAN", True, (255, 255, 255))
        win.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 120))
        
        pygame.draw.rect(win, (255, 255, 255), login_box_rect, border_radius=10)
        pygame.draw.rect(win, (0, 0, 0), login_box_rect, width=4, border_radius=10)
        
        text_surf = font_large.render(current_cccd, True, (0, 0, 0))
        win.blit(text_surf, (login_box_rect.x + 20, login_box_rect.y + 15))
        
        sub_text = font_small.render("Nhan ENTER de tiep tuc", True, (255, 215, 0))
        win.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, HEIGHT//2 + 60))

    elif game_state == "menu":
        user_txt = font_small.render(f"Tai khoan: {current_cccd}", True, (255,255,255))
        win.blit(user_txt, (10,10))
        
        if logo_img:
            logo_rect = logo_img.get_rect(center=(WIDTH//2, 250)) 
            win.blit(logo_img, logo_rect)

        start_box_rect = pygame.Rect(0, 0, 260, 80)
        start_box_rect.center = (WIDTH // 2, 550)
        pygame.draw.rect(win, (205, 133, 63), start_box_rect, border_radius=10)
        pygame.draw.rect(win, (101, 67, 33), start_box_rect, width=4, border_radius=10)

        instruct_text = "START"
        instruct_outline = instruct_font_pixel.render(instruct_text, True, (40, 20, 0)) 
        instruct_outline_rect = instruct_outline.get_rect(center=(start_box_rect.centerx + 3, start_box_rect.centery + 3)) 
        instruct_main = instruct_font_pixel.render(instruct_text, True, (255, 215, 0)) 
        instruct_main_rect = instruct_main.get_rect(center=start_box_rect.center)
        
        if pygame.time.get_ticks() % 1000 < 600: 
            win.blit(instruct_outline, instruct_outline_rect)
            win.blit(instruct_main, instruct_main_rect)

    elif game_state == "level_menu":
        if logo_img:
            small_logo = pygame.transform.scale(logo_img, (350, 160))
            win.blit(small_logo, small_logo.get_rect(center=(WIDTH//2, 100)))

        draw_button(win, level1_rect, "LEVEL 1", button_font_pixel)
        draw_button(win, level2_rect, "LEVEL 2", button_font_pixel)
        draw_button(win, level3_rect, "LEVEL 3", button_font_pixel)
        draw_button(win, guide_rect, "GUIDE", button_font_pixel)
        draw_button(win, exit_rect, "EXIT", button_font_pixel)

    elif game_state == "guide":
        # 1. Vẽ Background Guide.jpg
        if 'guide_bg_img' in locals() and guide_bg_img:
            win.blit(guide_bg_img, (0, 0))
        else:
            win.fill((20, 50, 80)) 

        # --- ĐÃ XÓA PHẦN TIÊU ĐỀ LỚN THEO YÊU CẦU ---

        # 2. NỘI DUNG CHI TIẾT (Căn chỉnh lọt lòng khung viền vàng)
        lines = [
            "1. CHUAN BI THE TRANG:",
            " - Ngoi thang lung tren ghe, cach camera khoang 1 den 1.5 met.",
            " - Dam bao camera nhin ro tu hong tro len den dinh dau.",
            "",
            "2. CHU KY CHEO THUYEN (4 BUOC KHEP KIN):",
            " - Buoc 1: Vuon vai len, DUOI THANG TAY (Goc khuylu > 105 do).",
            " - Buoc 2: Keo manh tay ve sat nguoi, GAP SAU TAY (Goc khuylu < 85 do).",
            " - Buoc 3: Ha thap vai xuong de lay da.",
            " - Buoc 4: Nang vai len de chuan bi cho nhip cheo tiep theo.",
            "",
            "3. CHIEN THUAT TREN DUONG DUA:",
            " - Khong can cheo qua nhanh, hay DUNG DONG TAC va VUON HET BIEN DO.",
            " - Neu ban cheo nhanh hon Boss, ban se huc Boss bi choang ngat!"
        ]

        # Đẩy chữ lên cao hơn (y=150) vì không còn tiêu đề
        y_offset = 80 
        start_x = WIDTH//2 - 350 # Căn lề trái sao cho vừa vặn trong khung

        for line in lines:
            if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                text_main = font_medium.render(line, True, (255, 255, 255)) # Mục chính màu trắng
                text_shadow = font_medium.render(line, True, (0, 0, 0))
                y_offset += 15 # Tăng khoảng cách cho dễ đọc
            else:
                text_main = font_small.render(line, True, (200, 230, 255)) # Nội dung xanh lơ nhạt
                text_shadow = font_small.render(line, True, (0, 0, 0))
            
            # Vẽ bóng đổ trước, vẽ chữ chính đè lên sau
            win.blit(text_shadow, (start_x + 2, y_offset + 2))
            win.blit(text_main, (start_x, y_offset))
            
            y_offset += 35 # Khoảng cách xuống dòng

        # 3. DÒNG CHỮ THOÁT (Nhấp nháy góc dưới cùng)
        exit_str = "[ NHAN PHIM SPACE DE QUAY LAI MENU ]"
        exit_shadow = font_medium.render(exit_str, True, (0, 0, 0))
        exit_text = font_medium.render(exit_str, True, (255, 255, 0))
        
        if pygame.time.get_ticks() % 1000 < 600:
            win.blit(exit_shadow, (WIDTH//2 - exit_text.get_width()//2 + 3, 633))
            win.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, 630))

    elif game_state in ["playing_level1", "playing_level2", "playing_level3", "paused"]:
        
        if game_state != "paused":
            if game_state == "playing_level1": current_ai_speed = 1.0
            if game_state == "playing_level2": current_ai_speed = 1.5
            if game_state == "playing_level3": current_ai_speed = 2.0
            
            if abs(player_y - ai_y) < 80:
                if collision_timer == 0:
                    if player_speed > current_ai_speed + 0.5:
                        boss_health -= 15
                        collision_timer = 45 
                        player_x_drift = -40 
                        boss_x_drift = -60   
                    elif current_ai_speed > player_speed + 0.2:
                        player_health -= 15
                        collision_timer = 45
                        boss_x_drift = 40    
                        player_x_drift = 60  
                        
            player_x_drift *= 0.85
            boss_x_drift *= 0.85
            if collision_timer > 0: collision_timer -= 1
            
            player_y -= (player_base_speed + player_speed) 
            player_speed *= 0.92     
            if player_speed < 0.1: player_speed = 0
            ai_y -= current_ai_speed 
            
            ai_timer += 1
            if ai_timer > 10: 
                ai_frame_index = (ai_frame_index + 1) % len(ai_frames)
                ai_timer = 0
                
            if player_health <= 0 or ai_y <= 80:
                played_level_name = game_state
                winner, game_state = "BOSS", "game_over"
            elif boss_health <= 0 or player_y <= 80:
                played_level_name = game_state
                winner, game_state = "YOU", "game_over"
                
        finish_y = 65
        sq_size = 15 
        for x in range(0, WIDTH, sq_size):
            color1 = (255, 255, 255) if (x // sq_size) % 2 == 0 else (20, 20, 20)
            pygame.draw.rect(win, color1, (x, finish_y, sq_size, sq_size))
            color2 = (20, 20, 20) if (x // sq_size) % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(win, color2, (x, finish_y + sq_size, sq_size, sq_size))
        
        fl_text = "FINISH LINE"
        fl_outline = font_large.render(fl_text, True, (0, 0, 0))
        fl_rect = fl_outline.get_rect(center=(WIDTH//2, 35))
        win.blit(fl_outline, (fl_rect.x + 3, fl_rect.y + 3)) 
        fl_main = font_large.render(fl_text, True, (255, 215, 0))
        win.blit(fl_main, fl_rect)
        
        base_ai_x = WIDTH // 2 - 250
        base_player_x = WIDTH // 2 + 130
        ai_x = base_ai_x + boss_x_drift
        player_x = base_player_x + player_x_drift

        if use_images:
            current_ai_img = ai_frames[ai_frame_index]
            win.blit(current_ai_img, (ai_x, ai_y))
            current_player_img = player_sprites[vong_cheo]
            win.blit(current_player_img, (player_x, player_y))
        else:
            pygame.draw.rect(win, (255, 50, 50), (ai_x, ai_y, 60, 100))
            pygame.draw.rect(win, (50, 200, 50), (player_x, player_y, 60, 100))
        
        pygame.draw.rect(win, (150, 0, 0), (20, 80, 250, 25), border_radius=5)
        if boss_health > 0:
            pygame.draw.rect(win, (255, 50, 50), (20, 80, 250 * (boss_health/100), 25), border_radius=5)
        win.blit(font_small.render(f"BOSS HP: {boss_health}%", True, (255, 255, 255)), (25, 55))
        
        pygame.draw.rect(win, (0, 100, 0), (WIDTH - 270, 80, 250, 25), border_radius=5)
        if player_health > 0:
            pygame.draw.rect(win, (50, 255, 50), (WIDTH - 270, 80, 250 * (player_health/100), 25), border_radius=5)
        win.blit(font_small.render(f"YOUR HP: {player_health}%", True, (255, 255, 255)), (WIDTH - 265, 55))

        pygame.draw.rect(win, (255,255,255), (WIDTH//2 - 250, HEIGHT - 100, 500, 90), border_radius=10)
        win.blit(font_medium.render(f"Buoc: {vong_cheo}/4", True, (0, 0, 0)), (WIDTH//2 - 230, HEIGHT - 90))
        win.blit(font_small.render(stroke_stage, True, (0, 100, 0)), (WIDTH//2 - 230, HEIGHT - 40))
        
        current_lvl_text = prev_game_state if game_state == "paused" else game_state
        level_text = current_lvl_text.replace("playing_", "").upper()
        win.blit(font_medium.render(level_text, True, (255, 255, 0)), (20, 20))

        if game_state != "paused":
            pygame.draw.rect(win, (205, 133, 63), pause_btn_rect, border_radius=5)
            pygame.draw.rect(win, (101, 67, 33), pause_btn_rect, width=3, border_radius=5)
            pause_text = font_small.render("PAUSE", True, (255, 215, 0))
            win.blit(pause_text, pause_text.get_rect(center=pause_btn_rect.center))

        if game_state == "paused":
            dim_surface = pygame.Surface((WIDTH, HEIGHT))
            dim_surface.set_alpha(150) 
            dim_surface.fill((0, 0, 0))
            win.blit(dim_surface, (0, 0))
            
            pause_title = font_large.render("PAUSED", True, (255, 255, 255))
            win.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, 180))
            
            draw_button(win, resume_rect, "RESUME", button_font_pixel)
            draw_button(win, levels_rect, "LEVELS", button_font_pixel)
            draw_button(win, main_menu_rect, "MAIN MENU", button_font_pixel)

    elif game_state == "game_over":
        
        if not session_saved:
            import math # Tự động gọi thư viện toán học
            
            avg_vel = round(sum_velocity / velocity_count if velocity_count > 0 else 0, 2)
            max_accel = round(max_acceleration, 2)
            avg_cyc = round(sum_cycle_time / total_strokes_session if total_strokes_session > 0 else 0, 2)
            
            # --- TÍNH ĐỘ LỆCH CHUẨN (SD) ---
            cycle_sd = 0.0
            if total_strokes_session > 1 and len(list_cycle_times) > 1: 
                # Tính phương sai và độ lệch chuẩn
                variance = sum((x - avg_cyc) ** 2 for x in list_cycle_times) / (len(list_cycle_times) - 1)
                cycle_sd = round(math.sqrt(variance), 2)
            
            # --- TÍNH LỰC & CÔNG SUẤT ---
            K_RESISTANCE = 0.5  
            MASS_FACTOR = 1.2   
            luc_keo_toi_da = round(max_accel * MASS_FACTOR, 2)
            cong_suat_duy_tri = round((avg_vel / avg_cyc) * K_RESISTANCE, 2) if avg_cyc > 0 else 0.0

            lvl_name = played_level_name.replace("playing_", "").upper() if 'played_level_name' in locals() else "UNKNOWN"
            
            # --- LƯU 10 THÔNG SỐ VÀO CSDL ---
            database.save_session(current_cccd, lvl_name, winner, 
                                  luc_keo_toi_da, cong_suat_duy_tri, total_strokes_session, 
                                  avg_vel, max_accel, avg_cyc, cycle_sd)
            session_saved = True

        pygame.draw.rect(win, (255,255,255), (WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400), border_radius=15)
        color = (0, 150, 0) if winner == "YOU" else (200, 0, 0)
        
        if logo_img:
            small_logo = pygame.transform.scale(logo_img, (400, 180))
            logo_rect = small_logo.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
            win.blit(small_logo, logo_rect)
            
        res_text = font_large.render(f"{winner} WIN !", True, color)
        restart = font_medium.render("SPACE to play again", True, (0, 0, 0))
        win.blit(res_text, (WIDTH//2 - res_text.get_width()//2, HEIGHT//2 + 50))
        win.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 130))

    pygame.display.update()

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()