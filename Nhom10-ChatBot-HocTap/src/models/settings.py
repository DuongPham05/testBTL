"""
settings.py - Model lưu trữ cài đặt người dùng.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppSettings:
    """Cài đặt ứng dụng."""
    theme: str = "light"                     # "light" hoặc "dark"
    language: str = "vi"                     # Ngôn ngữ giao diện
    api_key: Optional[str] = None            # API key cho Anthropic (nếu dùng)
    api_model: str = "claude-3-haiku-20240307"  # Model mặc định
    max_tokens: int = 1024
    temperature: float = 0.7

    # Cài đặt học tập
    default_subject: str = "Toán học"
    daily_goal_minutes: int = 120            # Mục tiêu học mỗi ngày (phút)
    reminder_enabled: bool = False
    reminder_time: str = "20:00"             # Giờ nhắc nhở

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "language": self.language,
            "api_key": self.api_key,
            "api_model": self.api_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "default_subject": self.default_subject,
            "daily_goal_minutes": self.daily_goal_minutes,
            "reminder_enabled": self.reminder_enabled,
            "reminder_time": self.reminder_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        return cls(
            theme=data.get("theme", "light"),
            language=data.get("language", "vi"),
            api_key=data.get("api_key"),
            api_model=data.get("api_model", "claude-3-haiku-20240307"),
            max_tokens=data.get("max_tokens", 1024),
            temperature=data.get("temperature", 0.7),
            default_subject=data.get("default_subject", "Toán học"),
            daily_goal_minutes=data.get("daily_goal_minutes", 120),
            reminder_enabled=data.get("reminder_enabled", False),
            reminder_time=data.get("reminder_time", "20:00"),
        )