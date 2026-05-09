"""
src/views/dashboard/dashboard_view.py
---------------------------------------
View trang Tổng Quan – load từ dashboard_page.ui,
nhận AppState, render toàn bộ dữ liệu.
"""
from datetime import date

from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout

from src.controllers.base_controller       import BaseController
from src.models.app_state                  import AppState
from src.utils.date_helpers                import format_date_vi, relative_time
from src.views.components.stat_card        import StatCard
from src.views.components.subject_progress import SubjectProgressBar
from src.config                            import SUBJECT_COLORS


class DashboardView(BaseController):
    """Controller + View cho trang Dashboard."""

    UI_FILE = "dashboard_page.ui"

    navigate_to = pyqtSignal(int)   # 0=dash 1=chat 2=planner 3=roadmap

    # ------------------------------------------------------------------ #

    def setup_ui(self):
        self._state = AppState.instance()
        self._build_stat_cards()
        self._build_progress_bars()
        self._refresh_date()
        self._refresh_stats()
        self._refresh_recent_chats()

    def connect_signals(self):
        self.btnNewChatQuick.clicked.connect(lambda: self.navigate_to.emit(1))
        self.btnPlannerQuick.clicked.connect(lambda: self.navigate_to.emit(2))
        self.btnRoadmapQuick.clicked.connect(lambda: self.navigate_to.emit(3))
        self.btnSeeAllChats.clicked.connect(lambda: self.navigate_to.emit(1))
        self.recentChatsList.itemDoubleClicked.connect(
            lambda: self.navigate_to.emit(1)
        )

    def refresh(self):
        self._refresh_date()
        self._refresh_stats()
        self._refresh_recent_chats()
        self._refresh_progress_bars()

    # ── Build one-time widgets ─────────────────────────────────────────

    def _build_stat_cards(self):
        """Thay thế 4 QFrame tĩnh bằng StatCard động."""
        gradients = [
            "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #4facfe,stop:1 #00f2fe)",
            "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #43e97b,stop:1 #38f9d7)",
            "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #fa709a,stop:1 #fee140)",
            "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #a18cd1,stop:1 #fbc2eb)",
        ]
        self._card_chat  = StatCard("💬", "Phiên Chat",  "0", "Tháng này",  gradients[0])
        self._card_quest = StatCard("❓", "Câu Hỏi",     "0", "Đã hỏi AI",  gradients[1])
        self._card_task  = StatCard("✅", "Nhiệm Vụ",    "0", "Hoàn thành", gradients[2])
        self._card_stk   = StatCard("🔥", "Streak",      "0", "Học liên tiếp",gradients[3])

        # Nhét vào statsRow (QHBoxLayout đã có trong UI)
        for w in [self._card_chat, self._card_quest,
                  self._card_task, self._card_stk]:
            self.statsRow.addWidget(w)

        # Ẩn QFrame placeholder cứng (nếu còn)
        for name in ["cardChat","cardQuestions","cardTasks","cardStreak"]:
            w = self.findChild(type(self._card_chat).__bases__[0], name)
            if w: w.hide()

    def _build_progress_bars(self):
        """Thêm SubjectProgressBar vào progressFrame."""
        self._prog_bars: dict[str, SubjectProgressBar] = {}
        subjects_colors = [
            ("Toán",      "#4a6cf7"),
            ("Vật Lý",    "#e53e3e"),
            ("Hóa Học",   "#38a169"),
            ("Tiếng Anh", "#d69e2e"),
        ]
        # Tìm layout của progressFrame
        try:
            prog_lay = self.progressFrame.layout()
        except AttributeError:
            return

        for name, color in subjects_colors:
            bar = SubjectProgressBar(name, 0, color)
            self._prog_bars[name] = bar
            prog_lay.insertWidget(prog_lay.count() - 1, bar)

        # Ẩn placeholder
        for w_name in ["progressToan","progressLy","progressHoa","progressAnh"]:
            w = self.findChild(object, w_name)
            if w: w.hide()

    # ── Refresh methods ───────────────────────────────────────────────

    def _refresh_date(self):
        self.dateLabel.setText(format_date_vi(date.today()))

    def _refresh_stats(self):
        st = self._state
        chat_count = len(st.session_order)
        self._card_chat.set_value(str(chat_count))
        self._card_quest.set_value(str(st.total_questions))
        self._card_task.set_value(f"{st.tasks_done}/{st.tasks_total}")
        self._card_stk.set_value(f"{st.streak_days} ngày")

        # Cập nhật chatCountLabel, questionCountLabel... nếu vẫn tồn tại trong UI
        _safe_set(self, "chatCountLabel",     str(chat_count))
        _safe_set(self, "questionCountLabel", str(st.total_questions))
        _safe_set(self, "taskCountLabel",
                  f"{st.tasks_done}/{st.tasks_total}")
        _safe_set(self, "streakCountLabel",   f"{st.streak_days} ngày")

    def _refresh_recent_chats(self):
        self.recentChatsList.clear()
        for sid in self._state.session_order[:8]:
            title = self._state.session_title(sid)
            msgs  = self._state.get_messages(sid)
            last  = msgs[-1].timestamp if msgs else None
            time_str = relative_time(last.date()) if last else "Chưa có tin nhắn"
            self.recentChatsList.addItem(f"💬  {title}  ·  {time_str}")

    def _refresh_progress_bars(self):
        roadmap = self._state.roadmap
        name_map = {
            "Toán":      "Toán Học",
            "Vật Lý":    "Vật Lý",
            "Hóa Học":   "Hóa Học",
            "Tiếng Anh": "Tiếng Anh",
        }
        for bar_key, rm_name in name_map.items():
            bar = self._prog_bars.get(bar_key)
            if not bar: continue
            for rm in roadmap:
                if rm.name == rm_name:
                    bar.set_value(rm.progress)
                    break

    # ── Public API ────────────────────────────────────────────────────

    def on_new_chat(self, title: str):
        """Gọi từ MainWindow khi ChatView tạo session mới."""
        self._refresh_recent_chats()
        self._refresh_stats()

    def on_tasks_changed(self):
        self._refresh_stats()


def _safe_set(widget, attr: str, text: str):
    """Gán text vào QLabel nếu tồn tại trong widget."""
    lbl = getattr(widget, attr, None)
    if lbl and hasattr(lbl, "setText"):
        lbl.setText(text)