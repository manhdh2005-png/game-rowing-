# Căn chỉnh toàn bộ bố cục tự động, chừa không gian cho chữ nghiêng
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, hspace=0.6, bottom=0.15)
    
    print(f"\n✅ Đang mở cửa sổ biểu đồ cho bệnh nhân {ten_bn}...")
    plt.show()

if __name__ == "__main__":
    ve_bieu_do_benh_nhan()