"""
╔══════════════════════════════════════════════╗
║      QUẢN LÝ NHÂN SỰ - Python + MySQL        ║
║      Kết nối XAMPP (localhost:3306)           ║
╚══════════════════════════════════════════════╝

Yêu cầu:
  pip install mysql-connector-python
  XAMPP đang chạy (MySQL service)
  Đã import file database.sql vào phpMyAdmin
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import os
import sys

# ─── CẤU HÌNH KẾT NỐI ───────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",          # Mặc định XAMPP để trống
    "database": "qlnhansu",
    "charset":  "utf8mb4",
}

# ─── MÀU SẮC TERMINAL ────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BG_BLUE = "\033[44m"

def clr(): os.system("cls" if os.name == "nt" else "clear")

def ok(msg):    print(f"{C.GREEN}✔  {msg}{C.RESET}")
def err(msg):   print(f"{C.RED}✘  {msg}{C.RESET}")
def info(msg):  print(f"{C.CYAN}ℹ  {msg}{C.RESET}")
def warn(msg):  print(f"{C.YELLOW}⚠  {msg}{C.RESET}")

def title(text):
    w = 56
    print(f"\n{C.BG_BLUE}{C.WHITE}{C.BOLD}{'':^{w}}{C.RESET}")
    print(f"{C.BG_BLUE}{C.WHITE}{C.BOLD}{text:^{w}}{C.RESET}")
    print(f"{C.BG_BLUE}{C.WHITE}{C.BOLD}{'':^{w}}{C.RESET}\n")

def sep(): print(f"{C.BLUE}{'─'*56}{C.RESET}")


# ─── KẾT NỐI DATABASE ────────────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        err(f"Không thể kết nối MySQL: {e}")
        print(f"\n{C.YELLOW}Hãy kiểm tra:{C.RESET}")
        print("  • XAMPP đang chạy và MySQL đã Start")
        print("  • Database 'qlnhansu' đã được tạo (import database.sql)")
        print(f"  • Thông tin kết nối trong DB_CONFIG đúng\n")
        sys.exit(1)


# ─── VALIDATE ─────────────────────────────────────────────────────
def validate_cccd(cccd: str) -> bool:
    return cccd.isdigit() and len(cccd) == 12

def validate_date(date_str: str):
    """Trả về đối tượng date hoặc None nếu sai định dạng."""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None

def input_required(prompt: str, max_len: int = 200) -> str:
    while True:
        val = input(f"  {C.CYAN}{prompt}{C.RESET}").strip()
        if val:
            if len(val) <= max_len:
                return val
            warn(f"Tối đa {max_len} ký tự!")
        else:
            warn("Không được để trống!")

def input_cccd(prompt="Số CCCD (12 chữ số): ", exclude_id=None) -> str:
    conn = get_connection()
    cur  = conn.cursor()
    while True:
        cccd = input_required(prompt)
        if not validate_cccd(cccd):
            warn("CCCD phải gồm đúng 12 chữ số!")
            continue
        # Kiểm tra trùng
        if exclude_id:
            cur.execute("SELECT id FROM nhan_su WHERE so_cccd=%s AND id!=%s", (cccd, exclude_id))
        else:
            cur.execute("SELECT id FROM nhan_su WHERE so_cccd=%s", (cccd,))
        if cur.fetchone():
            warn("Số CCCD đã tồn tại trong hệ thống!")
        else:
            cur.close(); conn.close()
            return cccd

def input_date(prompt="Ngày sinh (dd/mm/yyyy): ") -> date:
    while True:
        ds = input_required(prompt)
        d  = validate_date(ds)
        if d is None:
            warn("Định dạng ngày không hợp lệ! Dùng dd/mm/yyyy")
        elif d >= date.today():
            warn("Ngày sinh phải nhỏ hơn ngày hôm nay!")
        else:
            return d

def input_gender() -> str:
    options = {"1": "Nam", "2": "Nữ", "3": "Khác"}
    while True:
        print(f"  {C.CYAN}Giới tính: [1] Nam  [2] Nữ  [3] Khác{C.RESET}", end=" ")
        ch = input().strip()
        if ch in options:
            return options[ch]
        warn("Chọn 1, 2 hoặc 3!")


# ─── HIỂN THỊ BẢNG ────────────────────────────────────────────────
def print_table(rows: list):
    if not rows:
        warn("Không có dữ liệu.")
        return

    # Header
    print(f"\n{C.BOLD}"
          f"{'STT':>4}  "
          f"{'Số CCCD':<14}"
          f"{'Họ và tên':<25}"
          f"{'Ngày sinh':<12}"
          f"{'GT':<6}"
          f"{'Địa chỉ'}"
          f"{C.RESET}")
    sep()

    for i, r in enumerate(rows, 1):
        ns  = r["ngay_sinh"].strftime("%d/%m/%Y") if isinstance(r["ngay_sinh"], date) else str(r["ngay_sinh"])
        dc  = r["dia_chi"]
        dc  = dc[:35] + "…" if len(dc) > 36 else dc
        gt  = r["gioi_tinh"]
        color = C.WHITE if i % 2 == 0 else ""
        print(f"{color}"
              f"{i:>4}  "
              f"{r['so_cccd']:<14}"
              f"{r['ho_ten']:<25}"
              f"{ns:<12}"
              f"{gt:<6}"
              f"{dc}"
              f"{C.RESET}")
    sep()
    print(f"  Tổng: {C.BOLD}{len(rows)}{C.RESET} nhân sự\n")


# ══════════════════════════════════════════════
# CHỨC NĂNG 1 – HIỂN THỊ DANH SÁCH
# ══════════════════════════════════════════════
def xem_danh_sach():
    title("  DANH SÁCH NHÂN SỰ  ")
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM nhan_su ORDER BY ho_ten")
    rows = cur.fetchall()
    cur.close(); conn.close()
    print_table(rows)
    input(f"  {C.YELLOW}[Enter] để quay lại...{C.RESET}")


# ══════════════════════════════════════════════
# CHỨC NĂNG 2 – THÊM MỚI
# ══════════════════════════════════════════════
def them_nhan_su():
    title("  THÊM NHÂN SỰ MỚI  ")
    print(f"  {C.YELLOW}(Nhấn Ctrl+C để hủy){C.RESET}\n")
    try:
        cccd  = input_cccd()
        ten   = input_required("Họ và tên: ", max_len=100)
        ns    = input_date()
        gt    = input_gender()
        dc    = input_required("Địa chỉ thường trú: ", max_len=300)

        sep()
        print(f"\n  {C.BOLD}Thông tin vừa nhập:{C.RESET}")
        print(f"  CCCD      : {cccd}")
        print(f"  Họ tên    : {ten}")
        print(f"  Ngày sinh : {ns.strftime('%d/%m/%Y')}")
        print(f"  Giới tính : {gt}")
        print(f"  Địa chỉ   : {dc}\n")

        xn = input(f"  {C.CYAN}Xác nhận thêm? [y/N]: {C.RESET}").strip().lower()
        if xn not in ("y", "yes"):
            warn("Đã hủy thao tác.")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO nhan_su (so_cccd, ho_ten, ngay_sinh, gioi_tinh, dia_chi) "
            "VALUES (%s, %s, %s, %s, %s)",
            (cccd, ten, ns, gt, dc)
        )
        conn.commit()
        cur.close(); conn.close()
        ok("Thêm nhân sự thành công!")

    except KeyboardInterrupt:
        warn("\nĐã hủy.")
    input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")


# ══════════════════════════════════════════════
# CHỨC NĂNG 3 – SỬA THÔNG TIN
# ══════════════════════════════════════════════
def sua_nhan_su():
    title("  SỬA THÔNG TIN NHÂN SỰ  ")
    try:
        cccd_search = input_required("Nhập số CCCD cần sửa: ")

        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM nhan_su WHERE so_cccd=%s", (cccd_search,))
        ns_row = cur.fetchone()
        cur.close(); conn.close()

        if not ns_row:
            err(f"Không tìm thấy nhân sự có CCCD: {cccd_search}")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        info(f"Tìm thấy: {ns_row['ho_ten']} (ID: {ns_row['id']})")
        print(f"\n  {C.YELLOW}(Enter để giữ nguyên giá trị cũ){C.RESET}\n")

        # CCCD mới
        new_cccd = input(f"  {C.CYAN}Số CCCD [{ns_row['so_cccd']}]: {C.RESET}").strip()
        if new_cccd == "":
            new_cccd = ns_row["so_cccd"]
        elif not validate_cccd(new_cccd):
            warn("CCCD không hợp lệ, giữ nguyên giá trị cũ.")
            new_cccd = ns_row["so_cccd"]

        # Họ tên
        new_ten = input(f"  {C.CYAN}Họ và tên [{ns_row['ho_ten']}]: {C.RESET}").strip()
        if not new_ten: new_ten = ns_row["ho_ten"]

        # Ngày sinh
        new_ns_str = input(f"  {C.CYAN}Ngày sinh [{ns_row['ngay_sinh'].strftime('%d/%m/%Y')}]: {C.RESET}").strip()
        if new_ns_str:
            new_ns = validate_date(new_ns_str)
            if new_ns is None:
                warn("Ngày không hợp lệ, giữ nguyên.")
                new_ns = ns_row["ngay_sinh"]
        else:
            new_ns = ns_row["ngay_sinh"]

        # Giới tính
        print(f"  {C.CYAN}Giới tính [{ns_row['gioi_tinh']}] [1]Nam [2]Nữ [3]Khác (Enter bỏ qua): {C.RESET}", end="")
        gt_ch = input().strip()
        gt_map = {"1": "Nam", "2": "Nữ", "3": "Khác"}
        new_gt = gt_map.get(gt_ch, ns_row["gioi_tinh"])

        # Địa chỉ
        new_dc = input(f"  {C.CYAN}Địa chỉ [{ns_row['dia_chi'][:40]}…]: {C.RESET}").strip()
        if not new_dc: new_dc = ns_row["dia_chi"]

        xn = input(f"\n  {C.CYAN}Xác nhận cập nhật? [y/N]: {C.RESET}").strip().lower()
        if xn not in ("y", "yes"):
            warn("Đã hủy thao tác.")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        conn = get_connection()
        cur  = conn.cursor()
        # Kiểm tra CCCD trùng với người khác
        cur.execute("SELECT id FROM nhan_su WHERE so_cccd=%s AND id!=%s", (new_cccd, ns_row["id"]))
        if cur.fetchone():
            cur.close(); conn.close()
            err("Số CCCD đã tồn tại, cập nhật thất bại!")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        cur.execute(
            "UPDATE nhan_su SET so_cccd=%s, ho_ten=%s, ngay_sinh=%s, gioi_tinh=%s, dia_chi=%s "
            "WHERE id=%s",
            (new_cccd, new_ten, new_ns, new_gt, new_dc, ns_row["id"])
        )
        conn.commit()
        cur.close(); conn.close()
        ok("Cập nhật thành công!")

    except KeyboardInterrupt:
        warn("\nĐã hủy.")
    input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")


# ══════════════════════════════════════════════
# CHỨC NĂNG 4 – XÓA
# ══════════════════════════════════════════════
def xoa_nhan_su():
    title("  XÓA NHÂN SỰ  ")
    try:
        cccd_search = input_required("Nhập số CCCD cần xóa: ")

        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM nhan_su WHERE so_cccd=%s", (cccd_search,))
        ns_row = cur.fetchone()
        cur.close(); conn.close()

        if not ns_row:
            err(f"Không tìm thấy nhân sự có CCCD: {cccd_search}")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        print(f"\n  {C.RED}Sắp xóa:{C.RESET}")
        print(f"  • Họ tên  : {C.BOLD}{ns_row['ho_ten']}{C.RESET}")
        print(f"  • CCCD    : {ns_row['so_cccd']}")
        print(f"  • Địa chỉ : {ns_row['dia_chi']}\n")
        warn("Hành động này KHÔNG thể hoàn tác!")

        xn = input(f"  {C.RED}Gõ 'XOA' để xác nhận: {C.RESET}").strip()
        if xn != "XOA":
            warn("Đã hủy thao tác.")
            input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")
            return

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM nhan_su WHERE id=%s", (ns_row["id"],))
        conn.commit()
        cur.close(); conn.close()
        ok(f"Đã xóa nhân sự: {ns_row['ho_ten']}")

    except KeyboardInterrupt:
        warn("\nĐã hủy.")
    input(f"\n  {C.YELLOW}[Enter] để quay lại...{C.RESET}")


# ══════════════════════════════════════════════
# CHỨC NĂNG 5 – TÌM KIẾM
# ══════════════════════════════════════════════
def tim_kiem():
    title("  TÌM KIẾM NHÂN SỰ  ")
    print(f"  Tìm theo: {C.CYAN}[1]{C.RESET} Số CCCD  "
          f"{C.CYAN}[2]{C.RESET} Họ tên  "
          f"{C.CYAN}[3]{C.RESET} Địa chỉ  "
          f"{C.CYAN}[4]{C.RESET} Tất cả\n")

    ch = input(f"  {C.CYAN}Chọn (mặc định 4): {C.RESET}").strip() or "4"
    field_map = {
        "1": ("so_cccd", "Số CCCD"),
        "2": ("ho_ten",  "Họ tên"),
        "3": ("dia_chi", "Địa chỉ"),
        "4": ("all",     "Tất cả"),
    }
    field, label = field_map.get(ch, ("all", "Tất cả"))

    kw = input_required(f"Từ khóa tìm kiếm ({label}): ")

    conn = get_connection()
    cur  = conn.cursor(dictionary=True)

    if field == "all":
        sql = ("SELECT * FROM nhan_su "
               "WHERE so_cccd LIKE %s OR ho_ten LIKE %s OR dia_chi LIKE %s "
               "ORDER BY ho_ten")
        cur.execute(sql, (f"%{kw}%", f"%{kw}%", f"%{kw}%"))
    else:
        sql = f"SELECT * FROM nhan_su WHERE {field} LIKE %s ORDER BY ho_ten"
        cur.execute(sql, (f"%{kw}%",))

    rows = cur.fetchall()
    cur.close(); conn.close()

    info(f"Kết quả tìm kiếm '{kw}' theo {label}:")
    print_table(rows)
    input(f"  {C.YELLOW}[Enter] để quay lại...{C.RESET}")


# ══════════════════════════════════════════════
# MENU CHÍNH
# ══════════════════════════════════════════════
MENU_ITEMS = [
    ("1", "Xem danh sách nhân sự",   xem_danh_sach),
    ("2", "Thêm nhân sự mới",        them_nhan_su),
    ("3", "Sửa thông tin nhân sự",   sua_nhan_su),
    ("4", "Xóa nhân sự",             xoa_nhan_su),
    ("5", "Tìm kiếm nhân sự",        tim_kiem),
    ("0", "Thoát",                   None),
]

def main():
    # Kiểm tra kết nối lần đầu
    info("Đang kết nối MySQL (XAMPP)...")
    conn = get_connection()
    conn.close()
    ok("Kết nối thành công!\n")

    while True:
        clr()
        title("   HỆ THỐNG QUẢN LÝ NHÂN SỰ   ")
        for key, label, _ in MENU_ITEMS:
            color = C.RED if key == "0" else C.CYAN
            print(f"    {color}[{key}]{C.RESET}  {label}")
        sep()

        ch = input(f"\n  {C.YELLOW}Chọn chức năng: {C.RESET}").strip()
        clr()

        if ch == "0":
            print(f"\n  {C.GREEN}Tạm biệt! 👋{C.RESET}\n")
            break

        matched = next((fn for key, _, fn in MENU_ITEMS if key == ch and fn), None)
        if matched:
            matched()
        else:
            err("Lựa chọn không hợp lệ!")
            import time; time.sleep(1)


if __name__ == "__main__":
    main()
