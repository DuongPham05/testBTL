# QUẢN LÝ NHÂN SỰ — Python + MySQL (XAMPP)

## Cài đặt & Chạy

### Bước 1 — Cài thư viện
```
pip install mysql-connector-python
```

### Bước 2 — Tạo Database
1. Mở XAMPP → Start **MySQL** và **Apache**
2. Mở trình duyệt vào: http://localhost/phpmyadmin
3. Chọn tab **SQL** → paste toàn bộ nội dung file `database.sql` → Bấm **Go**

### Bước 3 — Chạy chương trình
```
python main.py
```

---

## Chỉnh cấu hình kết nối (nếu cần)
Mở `main.py`, sửa phần `DB_CONFIG`:
```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",   # Nếu XAMPP có đặt mật khẩu thì điền vào đây
    "database": "qlnhansu",
}
```

---

## Chức năng
| # | Chức năng |
|---|-----------|
| 1 | Xem danh sách toàn bộ nhân sự |
| 2 | Thêm nhân sự mới |
| 3 | Sửa thông tin nhân sự (tìm theo CCCD) |
| 4 | Xóa nhân sự (xác nhận 2 bước) |
| 5 | Tìm kiếm theo CCCD / Họ tên / Địa chỉ |

## Cấu trúc Database
Bảng `nhan_su`:
- `so_cccd` — Số CCCD 12 chữ số (duy nhất)
- `ho_ten` — Họ và tên
- `ngay_sinh` — Ngày sinh (DATE)
- `gioi_tinh` — Nam / Nữ / Khác
- `dia_chi` — Địa chỉ thường trú
