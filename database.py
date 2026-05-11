import sqlite3
from datetime import datetime

DB_NAME = "RehabData_SD.db" # Đổi tên CSDL để tạo file mới có cột SD

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Bảng 1: Danh sách Bệnh Nhân
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            cccd TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            medical_history TEXT,
            created_at TEXT
        )
    ''')

    # Bảng 2: Lịch sử từng ván chơi (Sessions) - ĐÃ BỔ SUNG cycle_sd
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cccd TEXT,
            play_time TEXT,
            level TEXT,
            result TEXT,
            
            peak_force REAL,          
            sustained_power REAL,     
            total_strokes INTEGER,
            
            avg_angular_velocity REAL,  
            max_angular_accel REAL,     
            avg_stroke_cycle_time REAL, 
            cycle_sd REAL,             -- BỔ SUNG: Độ lệch chuẩn chu kỳ
            
            FOREIGN KEY (cccd) REFERENCES patients (cccd)
        )
    ''')
    conn.commit()
    conn.close()

def add_patient(cccd, name, age=0, gender="", history=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO patients (cccd, full_name, age, gender, medical_history, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cccd, name, age, gender, history, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    conn.close()

# CẬP NHẬT HÀM LƯU: Truyền thêm biến cycle_sd vào cuối cùng
def save_session(cccd, level, result, peak_force, sustained_power, strokes, avg_vel, max_accel, avg_cycle, cycle_sd):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    play_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO sessions (cccd, play_time, level, result, 
                              peak_force, sustained_power, total_strokes, 
                              avg_angular_velocity, max_angular_accel, avg_stroke_cycle_time, cycle_sd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cccd, play_time, level, result, peak_force, sustained_power, strokes, avg_vel, max_accel, avg_cycle, cycle_sd))
    
    conn.commit()
    conn.close()
    print(f"✅ Đã lưu dữ liệu Y khoa (Có SD) cho Bệnh nhân CCCD: {cccd}")