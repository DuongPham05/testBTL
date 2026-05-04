"""
roadmap_node.py - Định nghĩa node trong lộ trình học tập (Roadmap).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoadmapNode:
    """Một nút (chủ đề) trong roadmap."""
    title: str
    description: str = ""
    children: list['RoadmapNode'] = field(default_factory=list)  # Các chủ đề con
    completed: bool = False
    estimated_hours: float = 0.0  # Thời gian dự kiến (giờ)
    resource_links: list[str] = field(default_factory=list)      # Link tài liệu tham khảo

    def add_child(self, child: 'RoadmapNode') -> None:
        """Thêm một chủ đề con."""
        self.children.append(child)

    def progress_percent(self) -> float:
        """Tính % hoàn thành của node này và tất cả node con."""
        if not self.children:
            return 100.0 if self.completed else 0.0
        child_progress = sum(child.progress_percent() for child in self.children)
        return child_progress / len(self.children)

    def to_dict(self) -> dict:
        """Chuyển đổi sang dictionary (hỗ trợ serialize)."""
        return {
            "title": self.title,
            "description": self.description,
            "children": [child.to_dict() for child in self.children],
            "completed": self.completed,
            "estimated_hours": self.estimated_hours,
            "resource_links": self.resource_links,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RoadmapNode':
        """Tạo node từ dictionary."""
        node = cls(
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            estimated_hours=data.get("estimated_hours", 0.0),
            resource_links=data.get("resource_links", []),
        )
        for child_data in data.get("children", []):
            node.add_child(cls.from_dict(child_data))
        return node