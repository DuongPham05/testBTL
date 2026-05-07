"""
app_state.py - Singleton quản lý trạng thái toàn cục của ứng dụng.
"""

from typing import Optional
from src.models.settings import AppSettings
from src.models.task import Task
from src.models.message import Message
from src.models.roadmap_node import RoadmapNode


class AppState:
    """Singleton chứa tất cả trạng thái runtime của app."""
    _instance: Optional['AppState'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.settings = AppSettings()
        self.tasks: list[Task] = []
        self.messages: list[Message] = []          # Lịch sử chat hiện tại
        self.roadmap: Optional[RoadmapNode] = None  # Lộ trình học tập
        self.current_session: str = ""              # Tên phiên chat hiện tại
        self.chat_sessions: dict[str, list[Message]] = {}  # Các phiên chat đã lưu

    # --- Task helpers ---
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_task_stats(self) -> tuple[int, int]:
        """Trả về (done, total)."""
        done = sum(1 for t in self.tasks if t.done)
        return done, len(self.tasks)

    # --- Message helpers ---
    def add_message(self, msg: Message) -> None:
        self.messages.append(msg)
        # Nếu có session hiện tại, lưu vào danh sách session
        if self.current_session:
            if self.current_session not in self.chat_sessions:
                self.chat_sessions[self.current_session] = []
            self.chat_sessions[self.current_session].append(msg)

    def clear_messages(self) -> None:
        self.messages.clear()

    def switch_session(self, session_name: str) -> None:
        """Chuyển sang session chat khác."""
        self.current_session = session_name
        self.messages = self.chat_sessions.get(session_name, [])

    def create_session(self, session_name: str) -> None:
        """Tạo phiên chat mới."""
        self.current_session = session_name
        self.messages = []
        self.chat_sessions[session_name] = []

    # --- Roadmap helpers ---
    def set_roadmap(self, root: RoadmapNode) -> None:
        self.roadmap = root

    def roadmap_progress(self) -> float:
        """Tính % hoàn thành tổng thể của roadmap."""
        if self.roadmap is None:
            return 0.0
        return self.roadmap.progress_percent()