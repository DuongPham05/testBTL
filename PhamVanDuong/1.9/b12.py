# ==========================================
# BÀI 1: CLASS HỌC VIÊN
# ==========================================

class HocVien:
    """Lớp mô tả thông tin của một học viên"""

    def __init__(self, ho_ten, ngay_sinh, email, dien_thoai, dia_chi, lop):
        """
        Hàm khởi tạo - nhận các thông tin cơ bản của học viên
        """
        self.ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh
        self.email = email
        self.dien_thoai = dien_thoai
        self.dia_chi = dia_chi
        self.lop = lop

    # ---- b) Phương thức hiển thị thông tin ----
    def show_info(self):
        """Hiển thị đầy đủ thông tin của học viên"""
        print("=" * 40)
        print("       THÔNG TIN HỌC VIÊN")
        print("=" * 40)
        print(f"  Họ tên     : {self.ho_ten}")
        print(f"  Ngày sinh  : {self.ngay_sinh}")
        print(f"  Email      : {self.email}")
        print(f"  Điện thoại : {self.dien_thoai}")
        print(f"  Địa chỉ   : {self.dia_chi}")
        print(f"  Lớp        : {self.lop}")
        print("=" * 40)

    # ---- c) Phương thức thay đổi thông tin ----
    def change_info(self, ho_ten=None, ngay_sinh=None, email=None,
                    dien_thoai=None, dia_chi="Hà Nội", lop="IT12.x"):
        """
        Thay đổi thông tin học viên.
        Tham số mặc định: dia_chi = 'Hà Nội', lop = 'IT12.x'
        Nếu tham số nào không truyền vào thì giữ nguyên giá trị cũ.
        """
        if ho_ten is not None:
            self.ho_ten = ho_ten
        if ngay_sinh is not None:
            self.ngay_sinh = ngay_sinh
        if email is not None:
            self.email = email
        if dien_thoai is not None:
            self.dien_thoai = dien_thoai

        # dia_chi và lop luôn được cập nhật (có giá trị mặc định)
        self.dia_chi = dia_chi
        self.lop = lop

        print(">> Cập nhật thông tin thành công!")


# ==========================================
# d) CHƯƠNG TRÌNH CHÍNH
# ==========================================

# Tạo đối tượng học viên thuộc lớp HocVien
hoc_vien_1 = HocVien(
    ho_ten="Nguyen Van A",
    ngay_sinh="01/01/2000",
    email="vanA@gmail.com",
    dien_thoai="0901234567",
    dia_chi="TP. Hồ Chí Minh",
    lop="IT10.a"
)

# Gọi phương thức show_info() để hiển thị thông tin ban đầu
print("\n--- Thông tin ban đầu ---")
hoc_vien_1.show_info()

# Gọi phương thức change_info() với tham số mặc định (dia_chi, lop)
print("\n--- Sau khi cập nhật (dùng tham số mặc định) ---")
hoc_vien_1.change_info()
hoc_vien_1.show_info()

# Gọi change_info() với tham số tùy chỉnh
print("\n--- Sau khi cập nhật (tùy chỉnh đầy đủ) ---")
hoc_vien_1.change_info(
    ho_ten="Nguyen Van A (updated)",
    email="vanA_new@gmail.com",
    dien_thoai="0999999999",
    dia_chi="Hà Nội",
    lop="IT12.x"
)
hoc_vien_1.show_info()