import sys
from datetime import date

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QRadioButton, QCheckBox, QComboBox,
    QHBoxLayout, QVBoxLayout, QButtonGroup, QMessageBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6 import uic


# ─────────────────────────────────────────────────────────────
# Cách 1: Load trực tiếp từ file .ui  (khuyến nghị khi dùng Qt Designer)
# ─────────────────────────────────────────────────────────────
class DangKyFormUI(QWidget):
    """Load giao diện từ file dang_ky.ui (Qt Designer)."""

    def __init__(self):
        super().__init__()
        uic.loadUi("dang_ky.ui", self)   # load file .ui cùng thư mục
        self._populate_combos()
        self._setup_connections()
        self._apply_styles()

    def _populate_combos(self):
        for d in range(1, 32):
            self.cmbNgay.addItem(str(d))
        self.cmbNgay.setCurrentText("14")

        thang_names = [
            "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4",
            "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8",
            "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12",
        ]
        self.cmbThang.addItems(thang_names)
        self.cmbThang.setCurrentText("Tháng 2")

        current_year = date.today().year
        for y in range(current_year, 1923, -1):
            self.cmbNam.addItem(str(y))
        self.cmbNam.setCurrentText("1970")

    def _setup_connections(self):
        self.btnDangKy.clicked.connect(self._on_dang_ky)

    def _apply_styles(self):
        self.chkDongY.setStyleSheet("color: #1877F2; font-weight: bold;")
        self.btnDangKy.setStyleSheet(
            "QPushButton {"
            "  background-color: #1877F2; color: white;"
            "  border-radius: 6px; border: none; font-size: 13px; font-weight: bold;"
            "}"
            "QPushButton:hover  { background-color: #166FE5; }"
            "QPushButton:pressed { background-color: #1565C0; }"
        )

    def _on_dang_ky(self):
        _validate_and_submit(
            ho=self.txtHo.text().strip(),
            ten=self.txtTen.text().strip(),
            sdt_email=self.txtSdtEmail.text().strip(),
            mat_khau=self.txtMatKhau.text().strip(),
            ngay=self.cmbNgay.currentText(),
            thang=self.cmbThang.currentText(),
            nam=self.cmbNam.currentText(),
            gioi_tinh=(
                "Nam" if self.rbNam.isChecked()
                else "Nữ" if self.rbNu.isChecked()
                else ""
            ),
            dong_y=self.chkDongY.isChecked(),
            parent=self,
        )


# ─────────────────────────────────────────────────────────────
# Cách 2: Xây dựng giao diện thuần bằng code (không cần file .ui)
# ─────────────────────────────────────────────────────────────
class DangKyFormCode(QWidget):
    """Xây dựng giao diện hoàn toàn bằng PyQt6 code."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng ký")
        self.setFixedWidth(480)
        self.setMinimumHeight(580)
        self._build_ui()
        self._populate_combos()
        self._setup_connections()

    # ── Build UI ─────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # Tiêu đề
        lbl_title = QLabel("Đăng ký")
        lbl_title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Nhanh chóng và dễ dàng")
        layout.addWidget(lbl_sub)

        # Họ & Tên
        row_name = QHBoxLayout()
        row_name.setSpacing(10)
        self.txt_ho = _make_line_edit("Họ")
        self.txt_ten = _make_line_edit("Tên")
        row_name.addWidget(self.txt_ho)
        row_name.addWidget(self.txt_ten)
        layout.addLayout(row_name)

        # SĐT / Email
        self.txt_sdt_email = _make_line_edit("Số di động hoặc email")
        layout.addWidget(self.txt_sdt_email)

        # Mật khẩu
        self.txt_mat_khau = _make_line_edit("Mật khẩu mới")
        self.txt_mat_khau.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.txt_mat_khau)

        # Ngày sinh
        lbl_ns = QLabel("Ngày sinh")
        lbl_ns.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_ns)

        row_dob = QHBoxLayout()
        row_dob.setSpacing(10)
        self.cmb_ngay = QComboBox(); self.cmb_ngay.setFixedHeight(32)
        self.cmb_thang = QComboBox(); self.cmb_thang.setFixedHeight(32)
        self.cmb_nam = QComboBox(); self.cmb_nam.setFixedHeight(32)
        row_dob.addWidget(self.cmb_ngay)
        row_dob.addWidget(self.cmb_thang)
        row_dob.addWidget(self.cmb_nam)
        layout.addLayout(row_dob)

        # Giới tính
        lbl_gt = QLabel("Giới tính")
        lbl_gt.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_gt)

        row_gender = QHBoxLayout()
        row_gender.setSpacing(30)
        self.rb_nam = QRadioButton("Nam")
        self.rb_nu = QRadioButton("Nữ")
        self._gender_group = QButtonGroup()
        self._gender_group.addButton(self.rb_nam)
        self._gender_group.addButton(self.rb_nu)
        row_gender.addWidget(self.rb_nam)
        row_gender.addWidget(self.rb_nu)
        row_gender.addStretch()
        layout.addLayout(row_gender)

        # Điều khoản
        lbl_dk = QLabel(
            "Bằng cách nhấp vào Đăng ký, bạn đồng ý với Điều khoản, "
            "Chính sách dữ liệu và Chính sách cookie của chúng tôi. Bạn có "
            "thể nhận được thông báo của chúng tôi qua SMS và hủy nhận "
            "bất kỳ lúc nào."
        )
        lbl_dk.setWordWrap(True)
        lbl_dk.setFont(QFont("Arial", 9))
        layout.addWidget(lbl_dk)

        # Checkbox
        self.chk_dong_y = QCheckBox("Tôi đồng ý với các điều khoản trên")
        self.chk_dong_y.setStyleSheet("color: #1877F2; font-weight: bold;")
        layout.addWidget(self.chk_dong_y)

        layout.addStretch()

        # Nút đăng ký
        self.btn_dang_ky = QPushButton("Đăng ký")
        self.btn_dang_ky.setFixedHeight(42)
        self.btn_dang_ky.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_dang_ky.setStyleSheet(
            "QPushButton {"
            "  background-color: #1877F2; color: white;"
            "  border-radius: 6px; border: none;"
            "}"
            "QPushButton:hover  { background-color: #166FE5; }"
            "QPushButton:pressed { background-color: #1565C0; }"
        )
        layout.addWidget(self.btn_dang_ky)
        self.setLayout(layout)

    def _populate_combos(self):
        for d in range(1, 32):
            self.cmb_ngay.addItem(str(d))
        self.cmb_ngay.setCurrentText("14")

        thang_names = [
            "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4",
            "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8",
            "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12",
        ]
        self.cmb_thang.addItems(thang_names)
        self.cmb_thang.setCurrentText("Tháng 2")

        current_year = date.today().year
        for y in range(current_year, 1923, -1):
            self.cmb_nam.addItem(str(y))
        self.cmb_nam.setCurrentText("1970")

    def _setup_connections(self):
        self.btn_dang_ky.clicked.connect(self._on_dang_ky)

    def _on_dang_ky(self):
        _validate_and_submit(
            ho=self.txt_ho.text().strip(),
            ten=self.txt_ten.text().strip(),
            sdt_email=self.txt_sdt_email.text().strip(),
            mat_khau=self.txt_mat_khau.text().strip(),
            ngay=self.cmb_ngay.currentText(),
            thang=self.cmb_thang.currentText(),
            nam=self.cmb_nam.currentText(),
            gioi_tinh=(
                "Nam" if self.rb_nam.isChecked()
                else "Nữ" if self.rb_nu.isChecked()
                else ""
            ),
            dong_y=self.chk_dong_y.isChecked(),
            parent=self,
        )


# ─────────────────────────────────────────────────────────────
# Helpers dùng chung
# ─────────────────────────────────────────────────────────────
def _make_line_edit(placeholder: str) -> QLineEdit:
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setFixedHeight(36)
    return le


def _validate_and_submit(
    ho, ten, sdt_email, mat_khau,
    ngay, thang, nam, gioi_tinh, dong_y, parent
):
    errors = []
    if not ho:          errors.append("• Vui lòng nhập Họ.")
    if not ten:         errors.append("• Vui lòng nhập Tên.")
    if not sdt_email:   errors.append("• Vui lòng nhập số di động hoặc email.")
    if not mat_khau:    errors.append("• Vui lòng nhập mật khẩu mới.")
    if not gioi_tinh:   errors.append("• Vui lòng chọn giới tính.")
    if not dong_y:      errors.append("• Vui lòng đồng ý với các điều khoản.")

    if errors:
        QMessageBox.warning(parent, "Thiếu thông tin", "\n".join(errors))
        return

    QMessageBox.information(
        parent,
        "Đăng ký thành công",
        f"Chào mừng {ho} {ten}!\n"
        f"Tài khoản : {sdt_email}\n"
        f"Ngày sinh : {ngay} {thang} {nam}\n"
        f"Giới tính : {gioi_tinh}",
    )


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Chọn một trong hai cách:
    #   - DangKyFormUI  : load từ dang_ky.ui  (cần file .ui cùng thư mục)
    #   - DangKyFormCode: xây dựng thuần code (không cần file .ui)
    window = DangKyFormCode()   # đổi thành DangKyFormUI() nếu dùng file .ui
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
