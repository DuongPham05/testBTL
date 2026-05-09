"""
study_subjects.py - Danh sách môn học và các thông tin liên quan.
"""

# Danh sách môn học chính thức (không dấu để dễ tìm kiếm)
SUBJECTS = [
    "Toán học",
    "Vật lý",
    "Hóa học",
    "Sinh học",
    "Ngữ văn",
    "Tiếng Anh",
    "Lịch sử",
    "Địa lý",
    "Giáo dục công dân",
    "Tin học",
    "Công nghệ",
    "Thể dục",
    "Âm nhạc",
    "Mỹ thuật",
]

# Icon emoji tương ứng
SUBJECT_ICONS = {
    "Toán học": "📐",
    "Vật lý": "⚛️",
    "Hóa học": "🧪",
    "Sinh học": "🧬",
    "Ngữ văn": "📚",
    "Tiếng Anh": "🇬🇧",
    "Lịch sử": "🏛️",
    "Địa lý": "🌍",
    "Giáo dục công dân": "⚖️",
    "Tin học": "💻",
    "Công nghệ": "🔧",
    "Thể dục": "⚽",
    "Âm nhạc": "🎵",
    "Mỹ thuật": "🎨",
}

# Màu sắc đại diện cho từng môn (hex)
SUBJECT_COLORS = {
    "Toán học": "#e53e3e",
    "Vật lý": "#dd6b20",
    "Hóa học": "#38a169",
    "Sinh học": "#319795",
    "Ngữ văn": "#805ad5",
    "Tiếng Anh": "#3182ce",
    "Lịch sử": "#d69e2e",
    "Địa lý": "#2b6cb0",
    "Giáo dục công dân": "#718096",
    "Tin học": "#e53e3e",
    "Công nghệ": "#e53e3e",
    "Thể dục": "#e53e3e",
    "Âm nhạc": "#e53e3e",
    "Mỹ thuật": "#e53e3e",
}


def get_subject_icon(subject: str) -> str:
    """Trả về icon cho môn học, nếu không có trả về icon mặc định."""
    return SUBJECT_ICONS.get(subject, "📌")

def get_subject_color(subject: str) -> str:
    """Trả về màu đại diện cho môn học, mặc định là xám."""
    return SUBJECT_COLORS.get(subject, "#a0aec0")