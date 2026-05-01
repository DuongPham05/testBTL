"""
api_worker.py - Worker thread để gọi API mà không block UI.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from src.api.anthropic_client import AnthropicClient
from src.api.prompts import SYSTEM_PROMPT


class APIWorker(QThread):
    """Thread riêng để xử lý API call.

    Signals:
        response_ready (str): Phát ra khi nhận được phản hồi thành công.
        error_occurred (str): Phát ra khi có lỗi.
        stream_chunk (str): Phát ra từng chunk khi dùng streaming mode.
    """
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    stream_chunk = pyqtSignal(str)

    def __init__(
        self,
        user_message: str,
        client: AnthropicClient,
        system: str = SYSTEM_PROMPT,
        history: list[dict] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        use_stream: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.user_message = user_message
        self.client = client
        self.system = system
        self.history = history or []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.use_stream = use_stream

    def run(self):
        try:
            if self.use_stream:
                for chunk in self.client.send_message_stream(
                    user_message=self.user_message,
                    system=self.system,
                    history=self.history,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                ):
                    self.stream_chunk.emit(chunk)
            else:
                response = self.client.send_message(
                    user_message=self.user_message,
                    system=self.system,
                    history=self.history,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))