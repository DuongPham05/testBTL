"""
config.py - Cấu hình toàn cục cho ứng dụng.
"""

import os
from pathlib import Path

# Đường dẫn gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

# Thư mục dữ liệu
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# File lưu trữ
SETTINGS_FILE = DATA_DIR / "settings.json"
TASKS_FILE = DATA_DIR / "tasks.json"
ROADMAP_FILE = DATA_DIR / "roadmap.json"
CHAT_HISTORY_DIR = DATA_DIR / "chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

# API defaults
DEFAULT_MODEL = "claude-3-haiku-20240307"
MAX_TOKENS = 1024
TEMPERATURE = 0.7

# Giao diện
APP_NAME = "EduBot - Study Planner"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# Định dạng ngày tháng
DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# Môn học mặc định
DEFAULT_SUBJECTS = [
    "Toán học", "Vật lý", "Hóa học", "Sinh học",
    "Ngữ văn", "Tiếng Anh", "Lịch sử", "Địa lý",
    "Giáo dục công dân", "Tin học"
]