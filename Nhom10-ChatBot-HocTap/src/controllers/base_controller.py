"""
base_controller.py
------------------
Lớp cơ sở cho tất cả các controller trang.
Cung cấp giao diện chung: setup_ui(), connect_signals(), refresh().
"""

from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
import os


UI_DIR = os.path.join(os.path.dirname(__file__))


class BaseController(QWidget):
    """
    Lớp cha của mọi PageController.

    Subclass phải override:
        - UI_FILE  : tên file .ui (không có đường dẫn)
        - setup_ui()        : thiết lập dữ liệu ban đầu lên widget
        - connect_signals() : kết nối signals / slots

    Vòng đời khởi tạo:
        __init__ → _load_ui() → setup_ui() → connect_signals()
    """

    # Subclass đặt tên file UI ở đây, vd: "chat_page.ui"
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
        """Nạp file .ui vào chính widget này."""
        if not self.UI_FILE:
            raise NotImplementedError(
                f"{self.__class__.__name__} phải khai báo UI_FILE"
            )
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
