"""
message.py - Định nghĩa data model cho một tin nhắn trong chat.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Một tin nhắn trong cuộc trò chuyện."""
    text: str
    is_user: bool                  # True nếu là tin nhắn của người dùng
    timestamp: datetime = field(default_factory=datetime.now)
    attachments: list[str] = field(default_factory=list)  # Danh sách đường dẫn file đính kèm
    metadata: dict = field(default_factory=dict)            # Thông tin bổ sung (subject, sentiment,...)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "is_user": self.is_user,
            "timestamp": self.timestamp.isoformat(),
            "attachments": self.attachments,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            text=data["text"],
            is_user=data["is_user"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            attachments=data.get("attachments", []),
            metadata=data.get("metadata", {}),
        )