"""
base_controller.py
------------------
Lớp cơ sở cho tất cả các controller trang.
Cung cấp giao diện chung: setup_ui(), connect_signals(), refresh().
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6 import uic
import os


# Lấy thư mục gốc của project: từ base_controller.py lùi lên 2 cấp
from pathlib import Path

UI_DIR = str(Path(__file__).resolve().parent.parent.parent / "forms")


class BaseController(QWidget):
    """
    Lớp cha của mọi PageController.

    Subclass phải override:
        - UI_FILE  : tên file .ui (không có đường dẫn) hoặc để "" nếu tự tạo UI bằng code
        - setup_ui()        : thiết lập dữ liệu ban đầu lên widget
        - connect_signals() : kết nối signals / slots

    Vòng đời khởi tạo:
        __init__ → _load_ui() → setup_ui() → connect_signals()
    """

    # Subclass đặt tên file UI ở đây, vd: "chat_page.ui". Để "" nếu không dùng .ui
    UI_FILE: str = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self.setup_ui()
        self.connect_signals()

    # ------------------------------------------------------------------ #
    #  Internal                                                            #
    # ------------------------------------------------------------------ #

    def _load_ui(self):
        """Nạp file .ui vào chính widget này nếu UI_FILE được chỉ định."""
        if not self.UI_FILE:
            # Không có file UI, bỏ qua (cho phép subclass tự setup_ui)
            return
        path = os.path.join(UI_DIR, self.UI_FILE)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {path}")
        uic.loadUi(path, self)

    # ------------------------------------------------------------------ #
    #  Public interface – override trong subclass                         #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        """Khởi tạo dữ liệu / trạng thái hiển thị ban đầu."""
        pass

    def connect_signals(self):
        """Kết nối tất cả signals → slots của trang này."""
        pass

    def refresh(self):
        """
        Được gọi mỗi khi trang được hiển thị lại (navigate to).
        Dùng để reload dữ liệu nếu cần.
        """
        pass

    def set_widget(self, widget: QWidget):
        """Gán widget chính cho controller (dùng khi thêm vào stackedWidget)."""
        self._widget = widget
        # Nếu controller đã có layout chính, thay thế nội dung
        if self.layout():
            self.layout().addWidget(widget)
        else:
            layout = QVBoxLayout(self)
            layout.addWidget(widget)

    # ------------------------------------------------------------------ #
    #  Helper utilities dùng chung                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def show_info(parent, title: str, message: str):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(parent, title, message)

    @staticmethod
    def show_warning(parent, title: str, message: str):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_error(parent, title: str, message: str):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def confirm(parent, title: str, message: str) -> bool:
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes