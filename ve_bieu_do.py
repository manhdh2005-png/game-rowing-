import sqlite3
import os
import tkinter as tk
from tkinter import ttk
import numpy as np 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_NAME = "RehabData_SD.db"

def ve_bieu_do_benh_nhan():
    print("="*50)
    print("HỆ THỐNG APP PHÂN TÍCH Y KHOA (BẢN 6 TABS - RADAR 5 ĐỈNH)")
    print("="*50)
    
    cccd = input("\nNhập số CCCD của bệnh nhân cần xem biểu đồ: ")
    
    if not os.path.exists(DB_NAME):
        print("Lỗi: Không tìm thấy Cơ sở dữ liệu. Hãy chơi game trước!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT full_name FROM patients WHERE cccd = ?", (cccd,))
    patient = cursor.fetchone()

    if not patient:
        print(f"\n❌ Không tìm thấy hồ sơ bệnh nhân mang CCCD: {cccd}")
        conn.close()
        return

    ten_bn = patient[0]

    # ĐÃ BỎ CỘT sustained_power (CÔNG SUẤT) KHỎI CÂU LỆNH TRUY VẤN
    cursor.execute('''
        SELECT play_time, peak_force, avg_angular_velocity, max_angular_accel, avg_stroke_cycle_time, cycle_sd
        FROM sessions 
        WHERE cccd = ? 
        ORDER BY play_time ASC
    ''', (cccd,))
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"\n⚠️ Bệnh nhân {ten_bn} chưa có dữ liệu tập luyện.")
        return

    thoi_gian = []
    luc_keo = []     
    van_toc_tb = []
    gia_toc_max = [] 
    chu_ky_tb = []
    do_lech_chuan = [] 

    for i, row in enumerate(rows):
        time_str = row[0][5:16].replace(" ", "\n") 
        thoi_gian.append(f"Lần {i+1}\n{time_str}") 
        luc_keo.append(row[1])
        # Điều chỉnh lại Index do đã bỏ đi 1 cột
        van_toc_tb.append(row[2])
        gia_toc_max.append(row[3]) 
        chu_ky_tb.append(row[4])
        do_lech_chuan.append(row[5]) 

    # ==========================================
    # TẠO GIAO DIỆN APP (TKINTER)
    # ==========================================
    root = tk.Tk()
    root.title("Dashboard Phục Hồi Chức Năng ProMax")
    root.geometry("1100x750")
    root.configure(bg='#f4f6f9')

    lbl_title = tk.Label(root, text=f"BÁO CÁO TIẾN TRIỂN SỨC MẠNH & PHỤC HỒI\nBệnh nhân: {ten_bn} ({cccd})", 
                         font=("Helvetica", 16, "bold"), fg="#1f3a93", bg="#f4f6f9", pady=15)
    lbl_title.pack()

    style = ttk.Style()
    style.theme_use('default')
    style.configure('TNotebook.Tab', font=('Helvetica', 11, 'bold'), padding=[15, 5])
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # ----------------------------------------------------
    # HÀM HỖ TRỢ 1: VẼ BIỂU ĐỒ ĐƯỜNG (LINE CHART)
    # ----------------------------------------------------
    def tao_tab_bieu_do(tab_name, title, ylabel, y_data1, y_data2=None, color1='', color2='', label1='', label2='', fill_color=''):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=tab_name)
        
        fig = Figure(figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111)

        if y_data2 is not None:
            ax.fill_between(thoi_gian, y_data2, y_data1, color=fill_color, alpha=0.15)
            ax.plot(thoi_gian, y_data2, marker='s', markersize=8, color=color2, linewidth=2.5, label=label2)
        else:
            ax.fill_between(thoi_gian, y_data1, 0, color=fill_color, alpha=0.1)

        ax.plot(thoi_gian, y_data1, marker='o', markersize=8, color=color1, linewidth=2.5, label=label1)

        ax.set_title(title, fontsize=14, fontweight='bold', color='#34495e', pad=15)
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(thoi_gian)))
        ax.set_xticklabels(thoi_gian, rotation=0, fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')
        ax.legend(loc='best', frameon=True, shadow=True, fontsize=10)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # ----------------------------------------------------
    # HÀM HỖ TRỢ 2: VẼ BIỂU ĐỒ RADAR (NGŨ GIÁC - 5 ĐỈNH)
    # ----------------------------------------------------
    def tao_tab_radar(tab_name):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=tab_name)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111, polar=True)
        
        # ĐÃ BỎ CÔNG SUẤT - CHỈ CÒN 5 CHỈ SỐ
        categories = ['Lực kéo\nbộc phát', 'Vận tốc\nkhớp', 'Gia tốc\nbộc phát', 'Tốc độ chèo\n(Chu kỳ)', 'Độ ổn định\n(Nhịp SD)']
        num_vars = len(categories)

        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1] 

        max_lk = max(luc_keo) if luc_keo else 1
        max_vt = max(van_toc_tb) if van_toc_tb else 1
        max_gt = max(gia_toc_max) if gia_toc_max else 1
        max_ck = max(chu_ky_tb) if chu_ky_tb else 1
        max_sd = max(do_lech_chuan) if do_lech_chuan else 1

        def score_normal(val, m_val):
            return (val / m_val * 100) if m_val > 0 else 0

        def score_inverse(val, m_val):
            if m_val == 0: return 100
            diem = 100 - (val / m_val * 100)
            return max(10, diem) 

        first_vals = [
            score_normal(luc_keo[0], max_lk),
            score_normal(van_toc_tb[0], max_vt),
            score_normal(gia_toc_max[0], max_gt),
            score_inverse(chu_ky_tb[0], max_ck),
            score_inverse(do_lech_chuan[0], max_sd)
        ]
        first_vals += first_vals[:1]

        last_vals = [
            score_normal(luc_keo[-1], max_lk),
            score_normal(van_toc_tb[-1], max_vt),
            score_normal(gia_toc_max[-1], max_gt),
            score_inverse(chu_ky_tb[-1], max_ck),
            score_inverse(do_lech_chuan[-1], max_sd)
        ]
        last_vals += last_vals[:1]

        if len(rows) > 1:
            ax.plot(angles, first_vals, color='#e74c3c', linewidth=2, linestyle='--', label=f'Lần Đầu Tiên ({thoi_gian[0].replace(chr(10), " ")})')
            ax.fill(angles, first_vals, color='#e74c3c', alpha=0.1)

        ax.plot(angles, last_vals, color='#2980b9', linewidth=3, marker='o', markersize=8, label=f'Gần Nhất ({thoi_gian[-1].replace(chr(10), " ")})')
        ax.fill(angles, last_vals, color='#3498db', alpha=0.35)

        ax.set_theta_offset(np.pi / 2) 
        ax.set_theta_direction(-1) 
        ax.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=11, fontweight='bold', color='#2c3e50')
        ax.set_ylim(0, 100) 
        ax.set_rlabel_position(0)
        ax.set_yticklabels(['20', '40', '60', '80', '100%'], color="grey", size=9)
        
        ax.set_title('BẢN ĐỒ TIẾN TRIỂN TỔNG THỂ (THANG ĐIỂM 100%)', fontsize=14, fontweight='bold', color='#1f3a93', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # ----------------------------------------------------
    # KHỞI TẠO 6 TABS 
    # ----------------------------------------------------
    tao_tab_radar("🌟 Tổng Thể (Radar)")
    
    # Tab 2 giờ chỉ còn 1 đường Lực Kéo
    tao_tab_bieu_do("💪 Lực kéo bộc phát", "ĐÁNH GIÁ SỨC MẠNH PHÁT LỰC", "Chỉ số Lực", luc_keo, None, '#2980b9', '', 'Lực kéo bộc phát', '', '#3498db')
    
    tao_tab_bieu_do("⚡ Gia tốc bộc phát", "KHẢ NĂNG BỘC PHÁT LỰC (GIA TỐC GÓC TỐI ĐA)", "Gia tốc (Độ/s²)", gia_toc_max, None, '#c0392b', '', 'Gia tốc góc Max (Độ/s²)', '', '#e74c3c')
    tao_tab_bieu_do("🔄 Vận tốc khớp", "SỰ CẢI THIỆN ĐỘ TRƠN TRU CỦA KHỚP (VẬN TỐC)", "Vận tốc (Độ/s)", van_toc_tb, None, '#f39c12', '', 'Vận tốc góc TB (Độ/s)', '', '#f1c40f')
    tao_tab_bieu_do("⏱️ Nhịp điệu chèo", "NHỊP ĐIỆU TẬP LUYỆN (SỰ ỔN ĐỊNH KHI CHÈO)", "Thời gian (s)", chu_ky_tb, None, '#8e44ad', '', 'Thời gian 1 chu kỳ (Giây)', '', '#9b59b6')
    tao_tab_bieu_do("🎯 Ổn định (SD)", "MỨC ĐỘ ỔN ĐỊNH / NHỊP NHÀNG KHI CHÈO (ĐỘ LỆCH CHUẨN)", "Độ lệch chuẩn SD (s)", do_lech_chuan, None, '#16a085', '', 'Mức độ gián đoạn/mất nhịp (Giây)', '', '#1abc9c')

    print(f"\n✅ Đang mở Dashboard Y tế cho bệnh nhân {ten_bn}...")
    root.mainloop()

if __name__ == "__main__":
    ve_bieu_do_benh_nhan()