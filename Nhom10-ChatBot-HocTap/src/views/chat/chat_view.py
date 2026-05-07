"""
src/views/chat/chat_view.py
----------------------------
View trang Chat với AI.

Flow:
  User nhập → _send() → ApiWorker(QThread) → _on_reply()
                      ↘ _show_typing()    ↗

State được lưu trong AppState (in-memory, không cần DB).
"""
from datetime import datetime

from PyQt6.QtCore    import pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import (QListWidgetItem, QFileDialog,
                              QSizePolicy, QSpacerItem)

from src.controllers.base_controller    import BaseController
from src.models.app_state               import AppState
from src.models.message                 import Message, MessageRole
from src.models.settings                import AppSettings
from src.api.api_worker                 import ApiWorker
from src.api.prompts                    import SYSTEM_CHAT
from src.views.components.chat_bubble   import ChatBubble, TypingIndicator
from src.utils.study_subjects           import strip_icon


class ChatView(BaseController):
    """Controller + View trang Chat."""

    UI_FILE = "chat_page.ui"

    new_session_created = pyqtSignal(str)   # → Dashboard
    message_sent        = pyqtSignal()       # → Dashboard stats

    def __init__(self, settings: AppSettings, parent=None):
        self._settings = settings
        self._worker: ApiWorker | None = None
        self._typing:  TypingIndicator | None = None
        super().__init__(parent)

    # ── Setup ────────────────────────────────────────────────────────

    def setup_ui(self):
        self._state   = AppState.instance()
        self._curr_sid = self._state.current_session
        self._populate_sessions()
        self._render_history(self._curr_sid)

    def connect_signals(self):
        # Sidebar
        self.btnNewChat.clicked.connect(self._new_session)
        self.searchSessions.textChanged.connect(self._filter_sessions)
        self.sessionsList.itemClicked.connect(self._on_session_clicked)

        # Send
        self.btnSend.clicked.connect(self._send)
        self.chatInputField.keyPressEvent = self._key_press

        # Subject
        self.subjectCombo.currentTextChanged.connect(self._on_subject_changed)

        # Suggestions
        self.suggBtn1.clicked.connect(
            lambda: self._fill("Giải thích định lý Pitago cho mình nghe")
        )
        self.suggBtn2.clicked.connect(
            lambda: self._fill("Công thức hóa học và tính chất của HCl là gì?")
        )
        self.suggBtn3.clicked.connect(
            lambda: self._fill("Luyện tập từ vựng tiếng Anh B1 theo chủ đề")
        )

        # Toolbar
        self.btnClearChat.clicked.connect(self._clear_chat)
        self.btnAttachImage.clicked.connect(self._attach_image)
        self.btnAttachFile.clicked.connect(self._attach_file)
        self.btnFormulaInput.clicked.connect(self._insert_formula)

    def refresh(self):
        self._populate_sessions()

    # ── Session management ───────────────────────────────────────────

    def _populate_sessions(self, filter_text: str = ""):
        self.sessionsList.clear()
        for sid in self._state.session_order:
            title = self._state.session_title(sid)
            if filter_text.lower() in title.lower():
                item = QListWidgetItem(f"💬  {title}")
                item.setData(Qt.ItemDataRole.UserRole, sid)
                self.sessionsList.addItem(item)
        # Chọn current
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
            self._curr_sid = sid
            self._state.current_session = sid
            self._clear_messages_ui()
            self._render_history(sid)

    def _new_session(self):
        sid = self._state.new_session()
        self._curr_sid = sid
        self._state.current_session = sid
        self._populate_sessions()
        self._clear_messages_ui()
        title = self._state.session_title(sid)
        self.new_session_created.emit(title)

    # ── Message rendering ────────────────────────────────────────────

    def _render_history(self, sid: str):
        for msg in self._state.get_messages(sid):
            self._add_bubble(msg)
        QTimer.singleShot(80, self._scroll_bottom)

    def _add_bubble(self, msg: Message):
        layout = self.messagesLayout
        # Remove trailing spacer
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
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )

    def _scroll_bottom(self):
        sb = self.chatScrollArea.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Send / receive ───────────────────────────────────────────────

    def _key_press(self, event):
        from PyQt6.QtWidgets import QPlainTextEdit
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            self._send()
        else:
            QPlainTextEdit.keyPressEvent(self.chatInputField, event)

    def _send(self):
        text = self.chatInputField.toPlainText().strip()
        if not text or self._worker:   # block nếu đang chờ reply
            return

        # Lưu & hiển thị tin user
        msg = self._state.add_message(self._curr_sid, MessageRole.USER, text)
        self._add_bubble(msg)
        self.chatInputField.clear()
        self.btnSend.setEnabled(False)
        self.message_sent.emit()

        self._show_typing()

        # Subject context
        subject = strip_icon(self.subjectCombo.currentText())

        self._worker = ApiWorker(
            user_text=text,
            history=self._state.get_messages(self._curr_sid),
            system=SYSTEM_CHAT,
            subject=subject,
            api_key=self._settings.api_key,
            parent=self,
        )
        self._worker.response_ready.connect(self._on_reply)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished_work.connect(self._on_worker_done)
        self._worker.start()

    def _on_reply(self, text: str):
        self._hide_typing()
        msg = self._state.add_message(self._curr_sid, MessageRole.ASSISTANT, text)
        self._add_bubble(msg)
        QTimer.singleShot(50, self._scroll_bottom)

    def _on_error(self, err: str):
        self._hide_typing()
        # Hiện lỗi như tin nhắn bot
        from src.models.message import Message, MessageRole
        fake = Message(MessageRole.ASSISTANT, f"⚠️ {err}")
        self._add_bubble(fake)

    def _on_worker_done(self):
        self._worker = None
        self.btnSend.setEnabled(True)

    # ── Helpers ──────────────────────────────────────────────────────

    def _on_subject_changed(self, text: str):
        subject = strip_icon(text)
        self.botStatusLabel.setText(
            f"🟢 Sẵn sàng – {subject}" if subject and "Tất cả" not in subject
            else "🟢 Sẵn sàng hỗ trợ"
        )

    def _fill(self, text: str):
        self.chatInputField.setPlainText(text)
        self.chatInputField.setFocus()

    def _clear_chat(self):
        if not self.confirm(self, "Xoá Chat",
                            "Xoá toàn bộ lịch sử chat này?"):
            return
        self._state.sessions[self._curr_sid] = []
        self._clear_messages_ui()

    def _attach_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            fname = path.replace("\\", "/").split("/")[-1]
            self._fill(f"[Ảnh: {fname}] ")

    def _attach_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file", "",
            "Documents (*.pdf *.docx *.txt *.xlsx);;All (*)"
        )
        if path:
            fname = path.replace("\\", "/").split("/")[-1]
            self._fill(f"[File: {fname}] ")

    def _insert_formula(self):
        cur = self.chatInputField.toPlainText()
        self.chatInputField.setPlainText(cur + " ∑ ")
        self.chatInputField.setFocus()
    