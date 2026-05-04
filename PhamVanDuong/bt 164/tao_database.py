import sqlite3

# 1. Tạo kết nối và tạo file database
conn = sqlite3.connect('nhansu.db')
cursor = conn.cursor()

# 2. Tạo bảng (nếu chưa có)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS NhanSu (
        SoCCCD TEXT PRIMARY KEY,
        HoTen TEXT NOT NULL,
        NgaySinh TEXT,
        GioiTinh TEXT,
        DiaChi TEXT
    )
''')

# 3. Danh sách dữ liệu ban đầu
danh_sach_nhan_su = [
    ('012345678912', 'Nguyễn Văn A', '2000-01-15', 'Nam', 'Hà Nội'),
    ('031095001234', 'Trần Thị Bình', '1995-05-20', 'Nữ', 'Quận 1, TP.HCM'),
    ('001092005678', 'Lê Hoàng Nam', '1992-11-10', 'Nam', 'Quận Cầu Giấy, Hà Nội'),
    ('040088009999', 'Phạm Minh Đức', '1988-02-28', 'Nam', 'Quận Hải Châu, Đà Nẵng'),
    ('052099001122', 'Hoàng Thu Thảo', '1999-08-15', 'Nữ', 'TP. Biên Hòa, Đồng Nai'),
    ('060090003344', 'Đỗ Anh Tuấn', '1990-12-05', 'Nam', 'Quận Ninh Kiều, Cần Thơ')
]

# 4. Chèn toàn bộ dữ liệu vào database
try:
    cursor.executemany('''
        INSERT INTO NhanSu (SoCCCD, HoTen, NgaySinh, GioiTinh, DiaChi)
        VALUES (?, ?, ?, ?, ?)
    ''', danh_sach_nhan_su)
    conn.commit()
    print("Đã tạo Database và thêm toàn bộ dữ liệu mẫu thành công!")
except sqlite3.IntegrityError:
    print("Dữ liệu mẫu đã tồn tại trong Database, không thêm lại để tránh trùng lặp.")

# 5. Đóng kết nối
conn.close()