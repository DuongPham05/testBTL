"""
main.py
-------
Entry-point của ứng dụng EduBot – Chatbot Hỗ Trợ Học Tập.

Kiến trúc:
  MainWindow  (mainwindow.ui)
  ├── Sidebar navigation (btnDashboard / btnChat / btnPlanner / btnRoadmap)
  └── QStackedWidget
      ├── [0] DashboardController  (dashboard_page.ui)
      ├── [1] ChatController       (chat_page.ui)
      ├── [2] PlannerController    (planner_page.ui)
      └── [3] RoadmapController    (roadmap_page.ui)

Chạy:
  python main.py
"""

import sys
import os

# Lấy thư mục gốc project (Nhom10-ChatBot-HocTap)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QButtonGroup
from PyQt6.QtCore    import Qt, QSize
from PyQt6.QtGui     import QIcon, QFont
from PyQt6           import uic

from controllers.dashboard_controller import DashboardController
from controllers.chat_controller import ChatController
from controllers.planner_controller import PlannerController
from controllers.roadmap_controller import RoadmapController
from controllers.base_controller import BaseController

# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Cửa sổ chính – quản lý navigation và kết nối các controller."""

    # Thứ tự phải khớp với index trong stackedWidget
    PAGE_DASHBOARD = 0
    PAGE_CHAT      = 1
    PAGE_PLANNER   = 2
    PAGE_ROADMAP   = 3

    def __init__(self):
        super().__init__()
        self._load_ui()
        self._init_pages()
        self._init_nav()
        self._connect_cross_page_signals()
        self._apply_global_style()

        
        self._navigate(self.PAGE_DASHBOARD)

    

    def _load_ui(self):
        ui_path = os.path.join(os.path.dirname(__file__), "mainwindow.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("EduBot – Chatbot Hỗ Trợ Học Tập")
        self.resize(1280, 800)
        self.setMinimumSize(QSize(1100, 700))

    def _init_pages(self):
        """Tạo các controller và nạp vào stackedWidget."""
        self.dashboard = DashboardController()
        self.chat      = ChatController()
        self.chat.set_main_window(self) 
        self.planner   = PlannerController()
        self.roadmap   = RoadmapController()

        self.stackedWidget.addWidget(self.dashboard)   # index 0
        self.stackedWidget.addWidget(self.chat)        # index 1
        self.stackedWidget.addWidget(self.planner)     # index 2
        self.stackedWidget.addWidget(self.roadmap)     # index 3

    def _init_nav(self):
        """Nhóm các nav button để chỉ một button active tại một thời điểm."""
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        nav_buttons = [
            self.btnDashboard,
            self.btnChat,
            self.btnPlanner,
            self.btnRoadmap,
        ]
        for i, btn in enumerate(nav_buttons):
            btn.setCheckable(True)
            self._nav_group.addButton(btn, i)
            btn.clicked.connect(lambda _, idx=i: self._navigate(idx))

        # Menu actions
        self.actionNewChat.triggered.connect(
            lambda: self._navigate(self.PAGE_CHAT)
        )
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self._show_about)
        self.actionExport.triggered.connect(self._export_history)

        # Settings button (profile area)
        self.btnSettings.clicked.connect(self._open_settings)

    def _connect_cross_page_signals(self):
        """Kết nối signals giữa các controller."""

        # Dashboard → navigate
        self.dashboard.navigate_to.connect(self._navigate)

        # Chat → thêm session vào Dashboard recent
        self.chat.new_session_created.connect(
            self.dashboard.add_recent_chat
        )

        # Planner → cập nhật task stats trên Dashboard
        self.planner.tasks_updated.connect(self._on_tasks_updated)

        # Roadmap → (tuỳ chọn) log goal
        self.roadmap.goal_added.connect(
            lambda subject: self.statusBar().showMessage(
                f"🎯 Đã thêm mục tiêu môn {subject}", 3000
            )
        )

    def _apply_global_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f8fc;
            }
            QMenuBar {
                background-color: #1a1f2e;
                color: #a0aec0;
                font-size: 13px;
                padding: 2px;
            }
            QMenuBar::item:selected {
                background-color: #2d3748;
                color: #ffffff;
                border-radius: 4px;
            }
            QMenu {
                background-color: #2d3748;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #4a6cf7;
                color: white;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #1a1f2e;
                color: #718096;
                font-size: 12px;
            }
        """)

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def _navigate(self, index: int):
        """Chuyển trang và cập nhật trạng thái nav button."""
        # Clamp
        index = max(0, min(index, 3))

        self.stackedWidget.setCurrentIndex(index)

        # Đồng bộ button checked
        btn = self._nav_group.button(index)
        if btn:
            btn.setChecked(True)

        # Gọi refresh trang đang hiển thị
        pages = [self.dashboard, self.chat, self.planner, self.roadmap]
        pages[index].refresh()

        # Cập nhật status bar
        page_names = ["Tổng Quan", "Chat với AI", "Lịch Học", "Lộ Trình"]
        self.statusBar().showMessage(f"📍 {page_names[index]}", 2000)

    # ------------------------------------------------------------------ #
    #  Cross-page slot handlers                                            #
    # ------------------------------------------------------------------ #

    def _on_tasks_updated(self, done: int, total: int):
        """Cập nhật thống kê task trên Dashboard khi Planner thay đổi."""
        self.dashboard.update_stats({
            "task_done":  done,
            "task_total": total,
        })

    # ------------------------------------------------------------------ #
    #  Menu actions                                                        #
    # ------------------------------------------------------------------ #

    def _show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Giới Thiệu EduBot")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText("""
            <div style='font-family:Segoe UI,Arial;'>
            <h2 style='color:#4a6cf7;'>🎓 EduBot</h2>
            <p><b>Chatbot Hỗ Trợ Học Tập</b></p>
            <p style='color:#718096;'>
                Phiên bản: 1.0.0<br>
                Nền tảng: Python 3.12 + PyQt6<br>
                Giao diện: Qt Designer (.ui files)
            </p>
            <p>EduBot giúp học sinh:</p>
            <ul>
                <li>Chat với AI để giải đáp bài tập</li>
                <li>Lên lịch học theo tuần</li>
                <li>Theo dõi lộ trình học tập</li>
            </ul>
            </div>
        """)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _export_history(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getSaveFileName(
            self, "Xuất Lịch Sử Chat", "chat_history.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("=== Lịch Sử Chat EduBot ===\n\n")
                    f.write("(Tính năng xuất đầy đủ sẽ được phát triển sau)\n")
                QMessageBox.information(
                    self, "Thành công", f"✅ Đã xuất lịch sử ra:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{e}")

    def _open_settings(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel,
            QLineEdit, QComboBox, QPushButton, QDialogButtonBox
        )

        dlg = QDialog(self)
        dlg.setWindowTitle("Cài Đặt")
        dlg.setMinimumWidth(380)
        dlg.setStyleSheet(
            "font-family:'Segoe UI',Arial,sans-serif;"
            "background:#fff;"
        )

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("⚙️ Cài Đặt")
        title.setStyleSheet("font-size:17px;font-weight:bold;color:#1a1f2e;")
        layout.addWidget(title)

        fld_style = (
            "QLineEdit,QComboBox{background:#f7f8fc;border:1px solid #e2e8f0;"
            "border-radius:8px;padding:6px 12px;font-size:13px;color:#2d3748;}"
            "QLineEdit:focus,QComboBox:focus{border-color:#4a6cf7;}"
        )
        lbl_style = "color:#4a5568;font-size:12px;font-weight:600;margin-bottom:2px;"

        # Tên học sinh
        layout.addWidget(_make_lbl("Tên học sinh", lbl_style))
        name_edit = QLineEdit("Học Sinh")
        name_edit.setMinimumHeight(38)
        name_edit.setStyleSheet(fld_style)
        layout.addWidget(name_edit)

        # Lớp
        layout.addWidget(_make_lbl("Lớp / Cấp học", lbl_style))
        grade_combo = QComboBox()
        grade_combo.addItems([
            "Lớp 10", "Lớp 11", "Lớp 12",
            "Đại học năm 1", "Đại học năm 2", "Khác"
        ])
        grade_combo.setMinimumHeight(38)
        grade_combo.setStyleSheet(fld_style)
        layout.addWidget(grade_combo)

        # Theme
        layout.addWidget(_make_lbl("Giao diện", lbl_style))
        theme_combo = QComboBox()
        theme_combo.addItems(["🌙 Tối (Sidebar)", "☀️ Sáng toàn bộ"])
        theme_combo.setMinimumHeight(38)
        theme_combo.setStyleSheet(fld_style)
        layout.addWidget(theme_combo)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.setStyleSheet(
            "QPushButton{background:#4a6cf7;color:white;border:none;"
            "border-radius:8px;padding:8px 20px;font-size:13px;}"
            "QPushButton:hover{background:#3b5bdb;}"
        )

        def _save():
            name = name_edit.text().strip() or "Học Sinh"
            self.userNameLabel.setText(name)
            self.dashboard.pageTitle.setText(f"Xin chào, {name}! 👋")
            dlg.accept()
            self.statusBar().showMessage("✅ Đã lưu cài đặt", 2000)

        btns.accepted.connect(_save)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        dlg.exec()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_lbl(text: str, style: str):
    from PyQt6.QtWidgets import QLabel
    lbl = QLabel(text)
    lbl.setStyleSheet(style)
    return lbl


# ---------------------------------------------------------------------------
# Application bootstrap
# ---------------------------------------------------------------------------

def main():
    # Hi-DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("EduBot")
    app.setApplicationVersion("1.0.0")

    # Font mặc định
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)
    app.setStyleSheet("""
    QLabel, QTextEdit, QPushButton {
        font-family: 'Segoe UI';
        font-size: 10pt;
        }
    """)

    window = MainWindow()
    window.show()
    window.statusBar().showMessage("🎓 EduBot sẵn sàng hỗ trợ học tập!", 3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()