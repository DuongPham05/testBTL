"""
chat_controller.py
------------------
Controller cho trang Chat với AI.

Chức năng:
  - Quản lý danh sách phiên chat (session list bên trái)
  - Gửi / nhận tin nhắn (tích hợp Gemini API)
  - Lọc môn học qua ComboBox
  - Gợi ý câu hỏi nhanh (suggestion buttons)
  - Đính kèm ảnh / file (mở dialog chọn file)
  - Xoá lịch sử chat
  - Tìm kiếm trong danh sách phiên
"""
from google.genai import types
import textwrap
from datetime import datetime
import json
# Xóa import json cũ nếu không dùng
# import json 
from google.genai import types # Thêm import này

def get_tools_definitions(self):
    """Trả về danh sách các tool schema cho Gemini SDK mới."""
    schedule_schema = types.FunctionDeclaration(
        name="create_learning_schedule",
        description="Tạo một lịch trình học tập chi tiết cho một chủ đề nhất định.",
        parameters={
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Chủ đề cần học (ví dụ: Python, Machine Learning)."},
                "level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "description": "Trình độ của người học."},
                "duration_weeks": {"type": "integer", "description": "Thời lượng của khóa học (tuần). Mặc định là 4."},
                "hours_per_week": {"type": "integer", "description": "Số giờ học dự kiến mỗi tuần. Mặc định là 5."}
            },
            "required": ["topic", "level"]
        },
    )

    roadmap_schema = types.FunctionDeclaration(
        name="generate_learning_roadmap",
        description="Tạo một lộ trình học tập (roadmap) cho một môn học cụ thể.",
        parameters={
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Tên môn học cần tạo roadmap (ví dụ: Python)."},
                "level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "description": "Trình độ của người học."}
            },
            "required": ["subject"]
        }
    )

    # Trả về một đối tượng Tool duy nhất chứa danh sách các function declarations
    return types.Tool(function_declarations=[schedule_schema, roadmap_schema])
from PyQt6.QtCore    import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui     import QColor, QKeyEvent
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QSizePolicy, QFileDialog, QListWidgetItem,
    QSpacerItem, QPlainTextEdit, QWidget
)

from controllers.base_controller import BaseController
from api.ai_service import AIService

# ---------------------------------------------------------------------------
# Dữ liệu mẫu cho danh sách session
# ---------------------------------------------------------------------------

SAMPLE_SESSIONS = [
    "Giải PT bậc 2",
    "Định luật Newton",
    "Phản ứng oxi hóa khử",
    "Tích phân cơ bản",
    "Ngữ pháp tiếng Anh",
]


# ---------------------------------------------------------------------------
# Worker thread – gọi API thật (Gemini) không chặn UI
# ---------------------------------------------------------------------------

class BotWorker(QThread):
    """Chạy gọi API AI trong thread riêng."""

    response_ready = pyqtSignal(object)  # ĐỔI: từ str thành object để nhận response raw
    tool_call_request = pyqtSignal(str, dict)  # THÊM MỚI: signal để yêu cầu gọi tool (tên tool, args)
    def __init__(self, user_text: str, subject: str = "", history: list[dict] | None = None):
        super().__init__()
        self.user_text = user_text
        self.subject = subject
        self.history = history or []

    def run(self):
         # THAY ĐỔI: sử dụng chat_with_tools thay vì chat
        ai = AIService()
        tools_def = get_tools_definitions()
        response = ai.chat_with_tools(
            user_message=self.user_text,
            tools=tools_def,
            subject=self.subject,
            history=self.history
        )
        # Kiểm tra response có chứa lời đề nghị gọi function không
        if response.candidates:
         candidate = response.candidates[0]
        # Kiểm tra phần tử đầu tiên có phải là function_call không
        part = candidate.content.parts[0]
        if hasattr(part, 'function_call') and part.function_call:
            tool_name = part.function_call.name
            tool_args = part.function_call.args
            self.tool_call_request.emit(tool_name, tool_args)
            return
            
    # Nếu không có function call, lấy text response
    # ... phần còn lại giữ nguyên ...
        text_response = response.text if response.text else "Xin lỗi, tôi không thể xử lý yêu cầu này."
        self.response_ready.emit(text_response)


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------

class ChatController(BaseController):
    """Controller trang Chat với AI."""

    UI_FILE = "chat_page.ui"

    # Phát ra khi có session chat mới (để Dashboard cập nhật)
    new_session_created = pyqtSignal(str)

    # ------------------------------------------------------------------ #
    #  Khởi tạo                                                           #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        self._sessions: list[str] = list(SAMPLE_SESSIONS)
        self._current_session: str = ""
        self._bot_worker: BotWorker | None = None
        self._typing_timer = QTimer(self)
        self._typing_timer.setSingleShot(True)
        self._chat_history: list[dict] = []  # Lịch sử hội thoại cho AI

        self._populate_sessions()
        # Chọn session đầu tiên
        if self._sessions:
            self.sessionsList.setCurrentRow(0)
            self._on_session_selected()

    def connect_signals(self):
        # Sidebar
        self.btnNewChat.clicked.connect(self._new_session)
        self.searchSessions.textChanged.connect(self._filter_sessions)
        self.sessionsList.itemClicked.connect(self._on_session_selected)

        # Gửi tin nhắn
        self.btnSend.clicked.connect(self._send_message)
        self.chatInputField.keyPressEvent = self._input_key_press

        # Suggestion buttons
        self.suggBtn1.clicked.connect(
            lambda: self._fill_input("Giải thích định lý Pitago")
        )
        self.suggBtn2.clicked.connect(
            lambda: self._fill_input("Công thức hóa học HCl là gì?")
        )
        self.suggBtn3.clicked.connect(
            lambda: self._fill_input("Luyện tập từ vựng tiếng Anh B1")
        )

        # Toolbar chat
        self.btnClearChat.clicked.connect(self._clear_chat)
        self.btnAttachImage.clicked.connect(self._attach_image)
        self.btnAttachFile.clicked.connect(self._attach_file)
        self.btnFormulaInput.clicked.connect(self._insert_formula)

    def refresh(self):
        pass  # không cần reload gì thêm

    # ------------------------------------------------------------------ #
    #  Session management                                                  #
    # ------------------------------------------------------------------ #

    def _populate_sessions(self, filter_text: str = ""):
        self.sessionsList.clear()
        for s in self._sessions:
            if filter_text.lower() in s.lower():
                item = QListWidgetItem(f"💬  {s}")
                self.sessionsList.addItem(item)

    def _filter_sessions(self, text: str):
        self._populate_sessions(text)

    def _on_session_selected(self, *_):
        item = self.sessionsList.currentItem()
        if item:
            name = item.text().replace("💬  ", "")
            self._current_session = name

    def _new_session(self):
        now = datetime.now().strftime("%H:%M")
        name = f"Chat {now}"
        self._sessions.insert(0, name)
        self._populate_sessions()
        self.sessionsList.setCurrentRow(0)
        self._current_session = name
        self._clear_chat(confirm=False)
        self._chat_history = []  # Reset lịch sử AI
        self.new_session_created.emit(name)

    # ------------------------------------------------------------------ #
    #  Messaging (đã tích hợp AI)                                         #
    # ------------------------------------------------------------------ #

    def _input_key_press(self, event):
        """Enter gửi tin; Shift+Enter xuống dòng."""
        if (
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            self._send_message()
        else:
            # Gọi lại hàm gốc cho các phím khác
            QPlainTextEdit.keyPressEvent(self.chatInputField, event)

    def _send_message(self):
        text = self.chatInputField.toPlainText().strip()
        if not text:
         return

    # Hiển thị tin nhắn người dùng
        self._append_message(text, is_user=True)

    # Lưu vào lịch sử hội thoại
        self._chat_history.append({"role": "user", "content": text})
        self.chatInputField.clear()

    # Hiển thị hiệu ứng đang gõ
        self._show_typing_indicator()

    # Tạo worker mới và kết nối signals
        self._bot_worker = BotWorker(
        user_text=text,
        subject=self.subject_combo.currentText() if hasattr(self, 'subject_combo') else "",
        history=self._chat_history
    )
    # Kết nối signal cho response bình thường
        self._bot_worker.response_ready.connect(self._handle_ai_response)
    # Kết nối signal cho tool call request
        self._bot_worker.tool_call_request.connect(self._handle_tool_call)
        self._bot_worker.start()

def _handle_tool_call(self, tool_name: str, tool_args: dict):
    """Xử lý khi AI yêu cầu gọi một công cụ nào đó."""
    self._remove_typing()
    result = None
    # Gọi đúng controller dựa trên tên tool
    if tool_name == "create_learning_schedule":
        # Lấy PlannerController (cần có tham chiếu đến main_window)
        planner_ctrl = self.main_window.planner_controller
        result = planner_ctrl.create_learning_schedule(**tool_args)
        # Hiển thị kết quả dưới dạng bảng trong chat (tuỳ chọn)
        schedule_text = f"**📅 Lịch trình học {tool_args.get('topic')}**\n\n"
        schedule_text += f"**Cấp độ:** {tool_args.get('level')}\n"
        schedule_text += f"**Thời lượng:** {tool_args.get('duration_weeks', 4)} tuần\n"
        schedule_text += f"**Giờ mỗi tuần:** {tool_args.get('hours_per_week', 5)} giờ\n\n"
        for week in result.get("weeks", []):
            schedule_text += f"**Tuần {week['week']}:** {week['focus']}\n"
            schedule_text += "  - " + "\n  - ".join(week['tasks']) + "\n\n"
        # Gửi kết quả vào chat
        self._append_message(schedule_text, is_user=False)
        # Lưu response vào lịch sử
        self._chat_history.append({"role": "assistant", "content": schedule_text})

    elif tool_name == "generate_learning_roadmap":
        roadmap_ctrl = self.main_window.roadmap_controller
        result = roadmap_ctrl.generate_learning_roadmap(**tool_args)
        roadmap_text = f"**🗺️ Lộ trình học {tool_args.get('subject')}**\n\n"
        for topic in result.get("topics", []):
            roadmap_text += f"- **{topic['name']}** ({topic['status']}): {topic['detail']}\n"
        self._append_message(roadmap_text, is_user=False)
        self._chat_history.append({"role": "assistant", "content": roadmap_text})
    else:
        self._append_message(f"⚠️ Tôi chưa được huấn luyện để thực hiện tác vụ '{tool_name}'.", is_user=False)

def _handle_ai_response(self, reply: str):
    """Xử lý response text thông thường từ AI."""
    self._remove_typing()
    self._append_message(reply, is_user=False)
    self._chat_history.append({"role": "assistant", "content": reply})
    def _on_bot_reply(self, reply: str):
        self._remove_typing()
        self._append_message(reply, is_user=False)
        # Lưu phản hồi bot vào lịch sử
        self._chat_history.append({"role": "assistant", "content": reply})
        self.btnSend.setEnabled(True)

    def _fill_input(self, text: str):
        self.chatInputField.setPlainText(text)
        self.chatInputField.setFocus()

def _add_widget_to_chat(self, widget: QWidget):
    """Chèn một widget tùy chỉnh vào khung chat (ví dụ lịch trình)."""
    scroll_area = self.chatScrollArea  # Lấy scroll area của chat
    container = scroll_area.widget() or scroll_area
    layout = container.layout()
    # Thêm widget mới vào layout
    layout.addWidget(widget)
    # ------------------------------------------------------------------ #
    #  Render messages                                                     #
    # ------------------------------------------------------------------ #

    def _append_message(self, text: str, is_user: bool):
        """Tạo bubble tin nhắn và chèn vào messagesLayout."""
        layout = self.messagesLayout

        # Xoá spacer cuối (luôn là item cuối)
        last_idx = layout.count() - 1
        if last_idx >= 0:
            spacer_item = layout.itemAt(last_idx)
            if spacer_item and spacer_item.spacerItem():
                layout.removeItem(spacer_item)

        # Tạo frame bong bóng
        bubble = self._make_bubble(text, is_user)
        layout.addWidget(bubble)

        # Thêm lại spacer cuối
        layout.addItem(
            QSpacerItem(0, 0,
                        QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )

        # Scroll xuống đáy
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _make_bubble(self, text: str, is_user: bool) -> QFrame:
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Avatar
        avatar = QLabel("👤" if is_user else "🤖")
        avatar.setStyleSheet("font-size:22px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignTop)
        avatar.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        # Bubble
        bubble = QFrame()
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        if is_user:
            bubble.setStyleSheet(
                "QFrame{"
                "  background-color:#4a6cf7;"
                "  border-radius:14px 0px 14px 14px;"
                "}"
            )
            lbl.setStyleSheet(
                "color:#ffffff;font-size:14px;"
                "background:transparent;border:none;"
            )
        else:
            bubble.setStyleSheet(
                "QFrame{"
                "  background-color:#ffffff;"
                "  border-radius:0px 14px 14px 14px;"
                "  border:1px solid #e2e8f0;"
                "}"
            )
            lbl.setStyleSheet(
                "color:#2d3748;font-size:14px;line-height:1.6;"
                "background:transparent;border:none;"
            )

        b_layout.addWidget(lbl)

        # Spacer giãn giữa bubble và mép màn hình
        spacer_lbl = QLabel()
        spacer_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        if is_user:
            row_layout.addWidget(spacer_lbl)
            row_layout.addWidget(bubble)
            row_layout.addWidget(avatar)
        else:
            row_layout.addWidget(avatar)
            row_layout.addWidget(bubble)
            row_layout.addWidget(spacer_lbl)

        return row

    def _show_typing(self):
        """Hiện bubble 'đang soạn...' tạm thời."""
        self._typing_bubble = self._make_bubble("⏳  EduBot đang soạn câu trả lời...", is_user=False)
        layout = self.messagesLayout
        last_idx = layout.count() - 1
        if last_idx >= 0 and layout.itemAt(last_idx).spacerItem():
            layout.removeItem(layout.itemAt(last_idx))
        layout.addWidget(self._typing_bubble)
        layout.addItem(
            QSpacerItem(0, 0,
                        QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _remove_typing(self):
        if hasattr(self, "_typing_bubble") and self._typing_bubble:
            self._typing_bubble.setParent(None)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def _scroll_to_bottom(self):
        sb = self.chatScrollArea.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------ #
    #  Toolbar actions                                                     #
    # ------------------------------------------------------------------ #

    def _clear_chat(self, confirm: bool = True):
        if confirm:
            if not self.confirm(self, "Xoá Chat",
                                "Bạn có chắc muốn xoá toàn bộ lịch sử chat này?"):
                return
        # Xoá tất cả widget trong messagesLayout trừ spacer cuối
        layout = self.messagesLayout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._chat_history = []  # Reset lịch sử AI

    def _attach_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            fname = path.split("/")[-1].split("\\")[-1]
            self._append_message(f"📎 [Ảnh đính kèm: {fname}]", is_user=True)

    def _attach_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file", "",
            "Documents (*.pdf *.docx *.txt *.xlsx *.pptx);;All (*)"
        )
        if path:
            fname = path.split("/")[-1].split("\\")[-1]
            self._append_message(f"📄 [File đính kèm: {fname}]", is_user=True)

    def _insert_formula(self):
        current = self.chatInputField.toPlainText()
        self.chatInputField.setPlainText(current + " ∑ ")
        self.chatInputField.setFocus()
        def _clear_chat(self):
          """Xóa toàn bộ lịch sử tin nhắn trong chat view."""
    # Lấy layout của scroll area chứa chat message
    # Giả sử bạn có một layout tên là chat_layout trong scroll area
    # Bạn cần thay đổi tên biến này cho phù hợp với code của mình
    if hasattr(self, 'chat_layout'):
        # Xóa tất cả widget con trong layout
        for i in reversed(range(self.chat_layout.count())): 
            widget = self.chat_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Xóa lịch sử chat trong bộ nhớ
        self._chat_history.clear()
        # (Tùy chọn) Thêm lại một tin nhắn chào mừng hoặc để trống khu vực chat
        self._append_message("Cuộc trò chuyện đã được xóa. Bạn cần tôi hỗ trợ gì thêm không?", is_user=False)