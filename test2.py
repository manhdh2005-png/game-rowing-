import cv2
import mediapipe as mp
import pygame
import math
import sys
import os 

# ==========================================
# 1. HÀM TÍNH GÓC TOÁN HỌC
# ==========================================
def calculate_angle(a, b, c):
    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return int(angle)

# 2. KHỞI TẠO PYGAME & TẢI HÌNH ẢNH
# ==========================================
pygame.init()
WIDTH, HEIGHT = 600, 800
# Thêm cờ FULLSCREEN (Toàn màn hình) và SCALED (Tự động phóng to theo tỷ lệ)
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Rehab Racing: Đua Thuyền Chuyên Nghiệp")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont(None, 70)
font_medium = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 30)

game_state = "menu"
winner = ""

# --- THÔNG SỐ VẬT LÝ ---
player_y = HEIGHT - 100
ai_y = HEIGHT - 100
ai_speed = 0.45           
player_base_speed = 0.2  
player_speed = 0         
vong_cheo = 0        
stroke_stage = "Hay bat dau vong cheo"
goc_khuyu_tay = 0
goc_vai = 0 

# ==========================================
# --- TẢI HÌNH ẢNH (ASSETS) VÀ FONT 1 LẦN ---
# ==========================================
use_images = os.path.exists("assets/river.png") and os.path.exists("assets/player_reach.png") and os.path.exists("assets/player_drive.png") and os.path.exists("assets/ai_0.png") and os.path.exists("assets/ai_1.png") and os.path.exists("assets/menu_bg.jpg")

if use_images:
    try:
        # Tải nền đại dương cho Màn hình Menu Cấp độ
        level_menu_bg_img = pygame.image.load("assets/level_menu_bg.png").convert()
        level_menu_bg_img = pygame.transform.scale(level_menu_bg_img, (WIDTH, HEIGHT))

        # Nền bãi biển cho Menu chính
        menu_bg_img = pygame.image.load("assets/menu_bg.jpg").convert()
        menu_bg_img = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))

        # Nền dòng sông lúc chơi
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

# Tải Logo RACING BOAT
try:
    logo_img = pygame.image.load("assets/logo.png").convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (550, 250)) 
except:
    logo_img = None

# Tải Font cho chữ START và các nút
try:
    instruct_font_pixel = pygame.font.Font("assets/stardew_valley_font.ttf", 60)
    button_font_pixel = pygame.font.Font("assets/stardew_valley_font.ttf", 35)
except:
    instruct_font_pixel = pygame.font.SysFont("impact", 60)
    button_font_pixel = pygame.font.SysFont("impact", 35)

ai_frame_index = 0
ai_timer = 0

# ==========================================
# --- KHỞI TẠO MENU CẤP ĐỘ ---
# ==========================================
button_width, button_height = 220, 65
start_y = 200
spacing = 90 

level1_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y, button_width, button_height)
level2_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing, button_width, button_height)
level3_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*2, button_width, button_height)
guide_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*3, button_width, button_height)
exit_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y + spacing*4, button_width, button_height)

# --- KHỞI TẠO NÚT CHO MENU TẠM DỪNG (PAUSE) ---
prev_game_state = "" # Biến lưu lại level đang chơi dở
resume_rect = pygame.Rect(WIDTH//2 - button_width//2, 230, button_width, button_height)
levels_rect = pygame.Rect(WIDTH//2 - button_width//2, 230 + spacing, button_width, button_height)
main_menu_rect = pygame.Rect(WIDTH//2 - button_width//2, 230 + spacing*2, button_width, button_height)

# Nút PAUSE nhỏ góc phải trên cùng màn hình khi chơi
pause_btn_rect = pygame.Rect(WIDTH - 110, 10, 100, 40)

def draw_button(win, rect, text, font):
    mouse_pos = pygame.mouse.get_pos()
    # Hiệu ứng hover
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
            if event.key == pygame.K_SPACE:
                if game_state == "menu":
                    game_state = "level_menu"
                elif game_state == "game_over":
                    game_state = "menu" 
                elif game_state == "guide":
                    game_state = "level_menu"
                    
            # MỚI: Bấm phím ESC để Tạm dừng / Đi tiếp
            if event.key == pygame.K_ESCAPE:
                if game_state in ["playing_level1", "playing_level2", "playing_level3"]:
                    prev_game_state = game_state
                    game_state = "paused"
                elif game_state == "paused":
                    game_state = prev_game_state
                    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                mouse_pos = event.pos
                
                # MỚI: Xử lý click trong Menu Tạm Dừng
                if game_state == "paused":
                    if resume_rect.collidepoint(mouse_pos):
                        game_state = prev_game_state # Chơi tiếp
                    elif levels_rect.collidepoint(mouse_pos):
                        game_state = "level_menu"    # Về chọn cấp độ
                    elif main_menu_rect.collidepoint(mouse_pos):
                        game_state = "menu"          # Về màn hình chính
                        
                # MỚI: Click nút PAUSE nhỏ góc phải khi đang đua
                elif game_state in ["playing_level1", "playing_level2", "playing_level3"]:
                    if pause_btn_rect.collidepoint(mouse_pos):
                        prev_game_state = game_state
                        game_state = "paused"
                
                # Logic click của Menu Cấp Độ cũ (giữ nguyên)
                elif game_state == "level_menu":
                    if exit_rect.collidepoint(mouse_pos):
                        running = False 
                    elif guide_rect.collidepoint(mouse_pos):
                        game_state = "guide"
                    elif level1_rect.collidepoint(mouse_pos) or level2_rect.collidepoint(mouse_pos) or level3_rect.collidepoint(mouse_pos):
                        player_y = HEIGHT - 100
                        ai_y = HEIGHT - 100
                        player_speed = 0 
                        vong_cheo = 0
                        stroke_stage = "Bat dau vong cheo moi"
                        
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
                # 1. NỚI RỘNG GÓC TẠO VÙNG ĐỆM AN TOÀN
                is_duoi = goc_khuyu_tay > 110  # Đòi hỏi duỗi dứt khoát hơn một chút
                is_gap = goc_khuyu_tay < 85    
                
                is_vai_cao = goc_vai > 65      # Hạ bớt chuẩn "vai cao" xuống 65 độ cho đỡ mỏi
                is_vai_thap = goc_vai < 45 
                
                # 2. LOGIC LÀM MỀM (Bỏ bớt điều kiện phụ gây kẹt)
                if vong_cheo == 0 and is_vai_cao and is_gap:
                    vong_cheo = 1
                    stroke_stage = "1. Vai da len. Bay gio DUOI TAY ra!"
                    
                # Bước 2: Hành động chính là DUỖI TAY. (Bỏ yêu cầu vai cao vì khi vươn tay vai hay bị chùng)
                elif vong_cheo == 1 and is_duoi: 
                    vong_cheo = 2
                    stroke_stage = "2. Tot! Keo tay ve va GAP TAY!"
                    
                # Bước 3: Hành động kéo về. Yêu cầu tay gập và vai hạ xuống
                elif vong_cheo == 2 and is_gap and is_vai_thap:
                    vong_cheo = 3
                    stroke_stage = "3. Da keo. Nang vai len de tiep tuc!"
                    
                # Bước 4: Nâng vai lên để lấy đà chèo nhịp mới
                elif vong_cheo == 3 and is_vai_cao:
                    vong_cheo = 1  
                    stroke_stage = "HOAN THANH! Tiep tuc duoi tay!"
                    
                    # Bơm mạnh lực đẩy cho mỗi nhịp chèo (Bù lại độ trượt dài của màn hình rộng)
                    if game_state == "playing_level1":
                        player_speed = 6.5  
                    elif game_state == "playing_level2":
                        player_speed = 5.5  
                    elif game_state == "playing_level3":
                        player_speed = 4.5

            cv2.rectangle(img, (5, 5), (450, 180), (0, 0, 0), -1)
            cv2.putText(img, f"Goc Khuyu: {goc_khuyu_tay} deg", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(img, f"Goc Vai: {goc_vai} deg", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(img, f"Buoc hien tai: {vong_cheo}/4", (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(img, stroke_stage, (15, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

        cv2.imshow("He Thong Giam Sat Rehab", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ==========================================
    # --- GIAO DIỆN GAME ---
    # ==========================================
    
    # 1. Logic vẽ nền
    if use_images:
        if game_state == "menu":
            win.blit(menu_bg_img, (0, 0))
        elif game_state == "level_menu" or game_state == "guide":
            if 'level_menu_bg_img' in locals() and level_menu_bg_img:
                win.blit(level_menu_bg_img, (0, 0))
        elif game_state in ["playing_level1", "playing_level2", "playing_level3", "game_over"]:
            win.blit(bg_img, (0, 0))
    else:
        win.fill((173, 216, 230)) 

    # 2. Logic vẽ các Màn hình
    if game_state == "menu":
        if logo_img:
            logo_rect = logo_img.get_rect(center=(WIDTH//2, 280)) 
            win.blit(logo_img, logo_rect)

        start_box_rect = pygame.Rect(0, 0, 220, 70)
        start_box_rect.center = (WIDTH // 2, 460)
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
            small_logo = pygame.transform.scale(logo_img, (250, 110))
            win.blit(small_logo, small_logo.get_rect(center=(WIDTH//2, 100)))

        draw_button(win, level1_rect, "LEVEL 1", button_font_pixel)
        draw_button(win, level2_rect, "LEVEL 2", button_font_pixel)
        draw_button(win, level3_rect, "LEVEL 3", button_font_pixel)
        draw_button(win, guide_rect, "GUIDE", button_font_pixel)
        draw_button(win, exit_rect, "EXIT", button_font_pixel)

    elif game_state == "guide":
        guide_text1 = font_medium.render("HUONG DAN CHEO THUYEN", True, (255, 255, 255))
        guide_text2 = font_small.render("1. Duoi tay ra truoc", True, (255, 255, 255))
        guide_text3 = font_small.render("2. Keo tay ve phia sau", True, (255, 255, 255))
        guide_text4 = font_small.render("Nhan SPACE de quay lai", True, (255, 215, 0))
        win.blit(guide_text1, (WIDTH//2 - guide_text1.get_width()//2, 200))
        win.blit(guide_text2, (WIDTH//2 - guide_text2.get_width()//2, 300))
        win.blit(guide_text3, (WIDTH//2 - guide_text3.get_width()//2, 350))
        win.blit(guide_text4, (WIDTH//2 - guide_text4.get_width()//2, 500))

    elif game_state in ["playing_level1", "playing_level2", "playing_level3", "paused"]:
        
        # --- CHỈ CẬP NHẬT CHUYỂN ĐỘNG NẾU KHÔNG PAUSE ---
        if game_state != "paused":
            if game_state == "playing_level1": current_ai_speed = 0.4
            if game_state == "playing_level2": current_ai_speed = 0.5
            if game_state == "playing_level3": current_ai_speed = 0.6
            
            player_y -= (player_base_speed + player_speed) 
            player_speed *= 0.7     
            if player_speed < 0.1:   
                player_speed = 0
                
            ai_y -= current_ai_speed 
            
            ai_timer += 1
            if ai_timer > 10: 
                ai_frame_index = (ai_frame_index + 1) % len(ai_frames)
                ai_timer = 0
                
            if player_y <= 50:
                winner, game_state = "YOU", "game_over"
            elif ai_y <= 50:
                winner, game_state = "BOSS", "game_over"

        # --- PHẦN VẼ MẶC ĐỊNH (Luôn vẽ để thấy thuyền đứng im lúc Pause) ---
        pygame.draw.line(win, (255, 50, 50), (0, 50), (WIDTH, 50), 8)
        win.blit(font_medium.render("FINISH LINE", True, (255, 255, 255)), (220, 15))
        
        if use_images:
            current_ai_img = ai_frames[ai_frame_index]
            win.blit(current_ai_img, (150, ai_y))
            current_player_img = player_sprites[vong_cheo]
            win.blit(current_player_img, (390, player_y))
        else:
            pygame.draw.rect(win, (255, 50, 50), (150, ai_y, 60, 100))
            pygame.draw.rect(win, (50, 200, 50), (390, player_y, 60, 100))
        
        pygame.draw.rect(win, (255,255,255), (180, 5, 400, 80), border_radius=10)
        win.blit(font_medium.render(f"Buoc: {vong_cheo}/4", True, (0, 0, 0)), (200, 10))
        win.blit(font_small.render(stroke_stage, True, (0, 100, 0)), (200, 50))
        
        # Vẽ thông tin Level góc trái
        current_lvl_text = prev_game_state if game_state == "paused" else game_state
        level_text = current_lvl_text.replace("playing_", "").upper()
        win.blit(font_small.render(level_text, True, (255, 255, 0)), (10, 10))

        # Vẽ nút PAUSE góc phải trên (Chỉ hiện khi đang chơi)
        if game_state != "paused":
            pygame.draw.rect(win, (205, 133, 63), pause_btn_rect, border_radius=5)
            pygame.draw.rect(win, (101, 67, 33), pause_btn_rect, width=3, border_radius=5)
            pause_text = font_small.render("PAUSE", True, (255, 215, 0))
            win.blit(pause_text, pause_text.get_rect(center=pause_btn_rect.center))

        # --- NẾU ĐANG TẠM DỪNG: PHỦ LỚP MỜ VÀ VẼ MENU TẠM DỪNG ---
        if game_state == "paused":
            # Phủ sương mù đen (alpha 150)
            dim_surface = pygame.Surface((WIDTH, HEIGHT))
            dim_surface.set_alpha(150) 
            dim_surface.fill((0, 0, 0))
            win.blit(dim_surface, (0, 0))
            
            # Chữ tiêu đề
            pause_title = font_large.render("PAUSED", True, (255, 255, 255))
            win.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, 120))
            
            # Vẽ 3 nút gỗ
            draw_button(win, resume_rect, "RESUME", button_font_pixel)
            draw_button(win, levels_rect, "LEVELS", button_font_pixel)
            draw_button(win, main_menu_rect, "MAIN MENU", button_font_pixel)

    elif game_state == "game_over":
        pygame.draw.rect(win, (255,255,255), (WIDTH//2 - 250, 250, 500, 300), border_radius=15)
        color = (0, 150, 0) if winner == "YOU" else (200, 0, 0)
        
        if logo_img:
            logo_rect = logo_img.get_rect(center=(WIDTH//2, 320))
            win.blit(logo_img, logo_rect)
            
        res_text = font_large.render(f"{winner} WIN!", True, color)
        restart = font_medium.render("SPACE to play again", True, (0, 0, 0))
        win.blit(res_text, (WIDTH//2 - res_text.get_width()//2, 420))
        win.blit(restart, (WIDTH//2 - restart.get_width()//2, 480))

    pygame.display.update()

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()