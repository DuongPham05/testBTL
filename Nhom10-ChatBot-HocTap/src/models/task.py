"""
task.py - Định nghĩa data model cho một nhiệm vụ học tập (Task).
Được sử dụng xuyên suốt bởi PlannerController và các module khác.
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional


@dataclass
class Task:
    """Một nhiệm vụ học tập trong planner."""
    title: str
    subject: str
    date: date
    start_time: time
    duration: int          # số phút
    priority: str = "medium"  # "high", "medium", "low"
    notes: str = ""
    done: bool = False
    id: int = 0            # unique ID, sẽ được gán bởi controller/DB

    # Màu sắc tương ứng với mức độ ưu tiên
    PRIORITY_COLORS = {
        "high":   ("#fff5f5", "#e53e3e"),   # background, border
        "medium": ("#fffbeb", "#d69e2e"),
        "low":    ("#f0fff4", "#38a169"),
    }

    # Icon cho từng môn học (có thể dùng emoji)
    SUBJECT_ICONS = {
        "Toán học": "📐",
        "Vật lý":   "⚛️",
        "Hóa học":  "🧪",
        "Sinh học": "🧬",
        "Ngữ văn":  "📚",
        "Tiếng Anh":"🇬🇧",
        "Lịch sử":  "🏛️",
        "Địa lý":   "🌍",
        "Tin học":  "💻",
        "Khác":     "📌"
    }

    @classmethod
    def get_icon(cls, subject: str) -> str:
        """Trả về icon cho môn học, nếu không có trả về icon mặc định."""
        return cls.SUBJECT_ICONS.get(subject, "📌")

    def to_dict(self) -> dict:
        """Chuyển đổi task sang dictionary (phục vụ serialize/json)."""
        return {
            "id": self.id,
            "title": self.title,
            "subject": self.subject,
            "date": self.date.isoformat(),
            "start_time": self.start_time.strftime("%H:%M"),
            "duration": self.duration,
            "priority": self.priority,
            "notes": self.notes,
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Tạo task từ dictionary."""
        return cls(
            id=data.get("id", 0),
            title=data["title"],
            subject=data["subject"],
            date=date.fromisoformat(data["date"]),
            start_time=time.fromisoformat(data["start_time"]),
            duration=data["duration"],
            priority=data.get("priority", "medium"),
            notes=data.get("notes", ""),
            done=data.get("done", False),
        )