#!/usr/bin/env python3
"""
Test nhanh 5 form UI sử dụng Qt6 (PySide6)
Chạy: python main.py
"""

import sys
from pathlib import Path

# Yêu cầu PySide6 (Qt6)
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout
    )
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile
except ImportError:
    print("This script requires PySide6 (Qt6). Install it with: pip install pyside6")
    sys.exit(1)


def load_ui(path, parent=None):
    """
    Load a .ui file and return the widget.
    Raises exceptions if the file is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ui_file = QFile(str(path))
    if not ui_file.open(QFile.ReadOnly):
        raise RuntimeError(f"Cannot open file: {path}")

    loader = QUiLoader()
    widget = loader.load(ui_file, parent)
    ui_file.close()

    if widget is None:
        raise RuntimeError(f"Failed to build widget from: {path}")
    return widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test 5 UI forms – Study Planner (Qt6)")
        self.resize(1280, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # List of (tab_name, file_name) to test
        ui_files = [
            ("mainwindow", "mainwindow.ui"),
            ("dashboard", "dashboard_page.ui"),
            ("chat", "chat_page.ui"),
            ("planner", "planner_page.ui"),
            ("roadmap", "roadmap_page.ui"),
        ]

        base_dir = Path(__file__).parent

        for name, filename in ui_files:
            file_path = base_dir / filename
            print(f"Loading: {filename} ...", end=" ")
            try:
                widget = load_ui(file_path)
                self.tabs.addTab(widget, name)
                print("✅ OK")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                # Replace with an error placeholder widget
                error_widget = QWidget()
                layout = QVBoxLayout(error_widget)
                message = QLabel(f"Failed to load {filename}\n\nError: {e}")
                message.setWordWrap(True)
                message.setStyleSheet("font-size: 14px; color: red; padding: 20px; background: white;")
                layout.addWidget(message)
                layout.addStretch()
                self.tabs.addTab(error_widget, f"{name} (error)")


if __name__ == "__main__":
    print("Qt6 (PySide6) UI test for Study Planner\n")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())