"""
src/views/chat/chat_view.py
----------------------------
View trang Chat với AI – phiên bản hoàn chỉnh.

Flow:
  User nhập → _send() → ApiWorker(QThread) → _on_reply()
                      ↘ _show_typing()    ↗

Tính năng:
  - Lịch sử chat nhiều session, lưu DB
  - AI nhận context cá nhân hóa từ DBManager (tiến độ, mục tiêu, điểm yếu)
  - Gửi kèm môn học để AI phân tích đúng môn
  - Lưu toàn bộ hội thoại vào MySQL (chat_history)
  - Block gửi khi đang chờ reply, hủy worker cũ nếu có
  - Attach ảnh / file / chèn ký hiệu toán
"""

from __future__ import annotations

from datetime import datetime
from typing   import Optional

from PyQt6.QtCore    import pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import (
    QListWidgetItem, QFileDialog,
    QSizePolicy, QSpacerItem, QMessageBox,
)

from src.controllers.base_controller  import BaseController
from src.models.app_state             import AppState
from src.models.message               import Message, MessageRole
from src.models.settings              import AppSettings
from src.api.api_worker               import ApiWorker
from src.api.prompts                  import SYSTEM_CHAT
from src.views.components.chat_bubble import ChatBubble, TypingIndicator
from src.utils.study_subjects         import strip_icon

# DB (import có fallback để app vẫn chạy khi chưa có DB)
try:
    from src.database.db_manager      import DBManager
    from src.database.context_builder import build_system_prompt
    _DB_AVAILABLE = True
except ImportError:
    _DB_AVAILABLE = False


# ---------------------------------------------------------------------------
# ChatView
# ---------------------------------------------------------------------------

class ChatView(BaseController):
    """Controller + View trang Chat."""

    UI_FILE = "chat_page.ui"

    # Signals ra ngoài
    new_session_created = pyqtSignal(str)   # title → Dashboard recent list
    message_sent        = pyqtSignal()       # → Dashboard stats (đếm câu hỏi)

    # ------------------------------------------------------------------ #
    #  Khởi tạo                                                           #
    # ------------------------------------------------------------------ #

    def __init__(self, settings: AppSettings, parent=None):
        self._settings = settings
        self._worker:  Optional[ApiWorker]      = None
        self._typing:  Optional[TypingIndicator] = None
        super().__init__(parent)

    # ------------------------------------------------------------------ #
    #  BaseController interface                                            #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        self._state    = AppState.instance()
        self._curr_sid = self._state.current_session

        # Nếu chưa có session nào, tạo mặc định
        if not self._curr_sid:
            self._curr_sid = self._state.new_session("Chat mới")

        self._populate_sessions()
        self._render_history(self._curr_sid)

    def connect_signals(self):
        # ── Sidebar ──────────────────────────────────────────────────
        self.btnNewChat.clicked.connect(self._new_session)
        self.searchSessions.textChanged.connect(self._filter_sessions)
        self.sessionsList.itemClicked.connect(self._on_session_clicked)

        # ── Gửi tin nhắn ─────────────────────────────────────────────
        self.btnSend.clicked.connect(self._send)
        self.chatInputField.keyPressEvent = self._key_press

        # ── Môn học ──────────────────────────────────────────────────
        self.subjectCombo.currentTextChanged.connect(self._on_subject_changed)

        # ── Gợi ý nhanh ──────────────────────────────────────────────
        self.suggBtn1.clicked.connect(
            lambda: self._fill("Giải thích định lý Pitago cho mình nghe")
        )
        self.suggBtn2.clicked.connect(
            lambda: self._fill("Công thức hóa học và tính chất của HCl là gì?")
        )
        self.suggBtn3.clicked.connect(
            lambda: self._fill("Luyện tập từ vựng tiếng Anh B1 theo chủ đề")
        )

        # ── Toolbar ──────────────────────────────────────────────────
        self.btnClearChat.clicked.connect(self._clear_chat)
        self.btnAttachImage.clicked.connect(self._attach_image)
        self.btnAttachFile.clicked.connect(self._attach_file)
        self.btnFormulaInput.clicked.connect(self._insert_formula)

    def refresh(self):
        self._populate_sessions()

    # ================================================================== #
    #  Session management                                                  #
    # ================================================================== #

    def _populate_sessions(self, filter_text: str = ""):
        """Render danh sách session vào sidebar."""
        self.sessionsList.clear()
        for sid in self._state.session_order:
            title = self._state.session_title(sid)
            if filter_text.lower() in title.lower():
                item = QListWidgetItem(f"💬  {title}")
                item.setData(Qt.ItemDataRole.UserRole, sid)
                self.sessionsList.addItem(item)

        # Highlight session đang mở
        for i in range(self.sessionsList.count()):
            item = self.sessionsList.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._curr_sid:
                self.sessionsList.setCurrentItem(item)
                break

    def _filter_sessions(self, text: str):
        self._populate_sessions(text)

    def _on_session_clicked(self, item: QListWidgetItem):
        sid = item.data(Qt.ItemDataRole.UserRole)
        if sid and sid != self._curr_sid:
            self._cancel_worker()           # hủy worker của session cũ nếu đang chạy
            self._curr_sid                 = sid
            self._state.current_session    = sid
            self._clear_messages_ui()
            self._render_history(sid)

    def _new_session(self):
        """Tạo session chat mới."""
        self._cancel_worker()
        now   = datetime.now().strftime("%d/%m %H:%M")
        title = f"Chat {now}"
        sid   = self._state.new_session(title)

        self._curr_sid              = sid
        self._state.current_session = sid

        self._populate_sessions()
        self._clear_messages_ui()
        self.new_session_created.emit(title)

    # ================================================================== #
    #  Message rendering                                                   #
    # ================================================================== #

    def _render_history(self, sid: str):
        """Vẽ lại toàn bộ lịch sử chat của session."""
        for msg in self._state.get_messages(sid):
            self._add_bubble(msg)
        QTimer.singleShot(80, self._scroll_bottom)

    def _add_bubble(self, msg: Message):
        layout = self.messagesLayout
        self._pop_spacer(layout)
        bubble = ChatBubble(msg)
        layout.addWidget(bubble)
        self._push_spacer(layout)

    def _show_typing(self):
        layout = self.messagesLayout
        self._pop_spacer(layout)
        self._typing = TypingIndicator()
        layout.addWidget(self._typing)
        self._push_spacer(layout)
        QTimer.singleShot(50, self._scroll_bottom)

    def _hide_typing(self):
        if self._typing:
            self._typing.setParent(None)
            self._typing.deleteLater()
            self._typing = None

    def _clear_messages_ui(self):
        """Xóa toàn bộ bubble khỏi layout (không xóa data)."""
        layout = self.messagesLayout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _pop_spacer(layout):
        last = layout.count() - 1
        if last >= 0 and layout.itemAt(last).spacerItem():
            layout.removeItem(layout.itemAt(last))

    @staticmethod
    def _push_spacer(layout):
        layout.addItem(
            QSpacerItem(
                0, 0,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding,
            )
        )

    def _scroll_bottom(self):
        sb = self.chatScrollArea.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ================================================================== #
    #  Gửi / nhận tin nhắn                                                #
    # ================================================================== #

    def _key_press(self, event):
        """Enter gửi, Shift+Enter xuống dòng."""
        from PyQt6.QtWidgets import QPlainTextEdit
        if (
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            self._send()
        else:
            QPlainTextEdit.keyPressEvent(self.chatInputField, event)

    def _send(self):
        text = self.chatInputField.toPlainText().strip()
        if not text:
            return
        if self._worker:
            # Có worker đang chạy → hủy và chờ, không gửi chồng
            return

        subject = strip_icon(self.subjectCombo.currentText())

        # ── Lưu & hiển thị tin user ───────────────────────────────────
        msg = self._state.add_message(self._curr_sid, MessageRole.USER, text)
        self._add_bubble(msg)
        self.chatInputField.clear()
        self.btnSend.setEnabled(False)
        self.message_sent.emit()

        # Lưu vào DB nếu có
        if _DB_AVAILABLE:
            try:
                DBManager.instance().save_chat_message(
                    role="user",
                    content=text,
                    session_name=self._state.session_title(self._curr_sid),
                )
            except Exception:
                pass   # DB lỗi không làm crash app

        self._show_typing()

        # ── Xây system prompt có context cá nhân hóa ─────────────────
        system = self._build_system(subject)

        # ── Khởi động worker ─────────────────────────────────────────
        self._worker = ApiWorker(
            user_text=text,
            history=self._state.get_messages(self._curr_sid),
            system=system,
            subject=subject,
            api_key=self._settings.api_key,
            parent=self,
        )
        self._worker.response_ready.connect(self._on_reply)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished_work.connect(self._on_worker_done)
        self._worker.start()

    def _build_system(self, subject: str) -> str:
        """
        Xây dựng system prompt.
        - Nếu DB có sẵn và có dữ liệu người dùng → prompt cá nhân hóa
        - Ngược lại → fallback về SYSTEM_CHAT chung
        """
        if not _DB_AVAILABLE:
            return SYSTEM_CHAT

        try:
            prompt = build_system_prompt(
                subject=subject if subject and "Tất cả" not in subject else None
            )
            return prompt
        except Exception:
            # DB chưa kết nối hoặc chưa có dữ liệu → dùng prompt mặc định
            return SYSTEM_CHAT

    def _on_reply(self, text: str):
        """Nhận phản hồi từ AI."""
        self._hide_typing()
        msg = self._state.add_message(self._curr_sid, MessageRole.ASSISTANT, text)
        self._add_bubble(msg)

        # Lưu reply vào DB
        if _DB_AVAILABLE:
            try:
                DBManager.instance().save_chat_message(
                    role="assistant",
                    content=text,
                    session_name=self._state.session_title(self._curr_sid),
                )
            except Exception:
                pass

        QTimer.singleShot(50, self._scroll_bottom)

    def _on_error(self, err: str):
        """Hiển thị lỗi như tin nhắn bot."""
        self._hide_typing()
        fake_msg = Message(
            role=MessageRole.ASSISTANT,
            content=f"⚠️ Không thể kết nối AI: {err}\n"
                    "Vui lòng kiểm tra API key hoặc kết nối mạng.",
        )
        self._add_bubble(fake_msg)

    def _on_worker_done(self):
        """Worker kết thúc (dù thành công hay lỗi)."""
        self._worker = None
        self.btnSend.setEnabled(True)

    def _cancel_worker(self):
        """Hủy worker đang chạy (khi chuyển session hoặc tạo session mới)."""
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(2000)   # chờ tối đa 2s
        self._worker = None
        self._hide_typing()
        self.btnSend.setEnabled(True)

    # ================================================================== #
    #  Helpers / Toolbar                                                   #
    # ================================================================== #

    def _on_subject_changed(self, text: str):
        subject = strip_icon(text)
        if subject and "Tất cả" not in subject:
            self.botStatusLabel.setText(f"🟢 Sẵn sàng – {subject}")
        else:
            self.botStatusLabel.setText("🟢 Sẵn sàng hỗ trợ")

    def _fill(self, text: str):
        """Điền sẵn text vào ô nhập."""
        self.chatInputField.setPlainText(text)
        self.chatInputField.setFocus()

    def _clear_chat(self):
        """Xóa lịch sử chat của session hiện tại."""
        if not self.confirm(
            self, "Xoá Chat",
            "Xoá toàn bộ lịch sử chat này?\nHành động không thể hoàn tác."
        ):
            return
        self._cancel_worker()
        # Xóa trong state
        if self._curr_sid in self._state.sessions:
            self._state.sessions[self._curr_sid] = []
        self._clear_messages_ui()
        self.botStatusLabel.setText("🟢 Chat đã được xóa")

    def _attach_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            fname = path.replace("\\", "/").split("/")[-1]
            self._fill(f"[Ảnh đính kèm: {fname}]\n")

    def _attach_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file", "",
            "Documents (*.pdf *.docx *.txt *.xlsx *.pptx);;All Files (*)"
        )
        if path:
            fname = path.replace("\\", "/").split("/")[-1]
            self._fill(f"[File đính kèm: {fname}]\n")

    def _insert_formula(self):
        """Chèn ký hiệu toán học vào vị trí con trỏ."""
        from PyQt6.QtWidgets import QMenu, QAction
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu{background:#2d3748;color:#e2e8f0;border:1px solid #4a5568;"
            "border-radius:8px;padding:4px;}"
            "QMenu::item{padding:6px 16px;border-radius:4px;}"
            "QMenu::item:selected{background:#4a6cf7;}"
        )
        symbols = [
            ("∑  Tổng",          "∑"),
            ("√  Căn bậc hai",   "√"),
            ("π  Pi",            "π"),
            ("∞  Vô cực",        "∞"),
            ("∫  Tích phân",     "∫"),
            ("∂  Đạo hàm riêng", "∂"),
            ("≤  Nhỏ hơn bằng",  "≤"),
            ("≥  Lớn hơn bằng",  "≥"),
            ("≠  Khác",          "≠"),
            ("α β γ  Hy Lạp",   "α β γ δ ε λ μ σ θ φ"),
        ]
        for label, sym in symbols:
            act = QAction(label, self)
            act.triggered.connect(lambda _, s=sym: self._insert_symbol(s))
            menu.addAction(act)

        menu.exec(self.btnFormulaInput.mapToGlobal(
            self.btnFormulaInput.rect().bottomLeft()
        ))

    def _insert_symbol(self, sym: str):
        cur = self.chatInputField.toPlainText()
        self.chatInputField.setPlainText(cur + sym + " ")
        self.chatInputField.setFocus()
        # Đặt con trỏ về cuối
        cursor = self.chatInputField.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chatInputField.setTextCursor(cursor)

    # ================================================================== #
    #  Public API – MainWindow / Controller khác có thể gọi              #
    # ================================================================== #

    def set_main_window(self, mw):
        """Giữ reference đến MainWindow (nếu cần navigate)."""
        self._main_window = mw

    def send_message_programmatic(self, text: str, subject: str = ""):
        """
        Gửi tin nhắn từ code (VD: từ Planner/Roadmap khi muốn hỏi AI).
        Tự động chọn môn học nếu truyền vào.
        """
        if subject:
            idx = self.subjectCombo.findText(subject, Qt.MatchFlag.MatchContains)
            if idx >= 0:
                self.subjectCombo.setCurrentIndex(idx)
        self._fill(text)
        self._send()

    def get_current_session_title(self) -> str:
        return self._state.session_title(self._curr_sid)