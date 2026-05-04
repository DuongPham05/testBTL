"""
src/views/roadmap/roadmap_view.py
-----------------------------------
View trang Lộ Trình Học.
Render SubjectCard động từ AppState.roadmap.
"""
from datetime import date

from PyQt6.QtCore    import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QSizePolicy, QSpacerItem,
    QDialog, QDialogButtonBox, QWidget, QGridLayout,
)

from src.controllers.base_controller import BaseController
from src.models.app_state            import AppState
from src.models.roadmap_node         import SubjectRoadmap, Topic, TopicStatus
from src.models.settings             import AppSettings
from src.utils.study_subjects        import strip_icon
from src.views.dialogs.task_dialog   import TaskDialog


# ---------------------------------------------------------------------------
# SubjectCard widget
# ---------------------------------------------------------------------------

class SubjectCard(QFrame):
    """Card expand/collapse cho một môn học."""

    def __init__(self, rm: SubjectRoadmap, on_topic, parent=None):
        super().__init__(parent)
        self._rm       = rm
        self._on_topic = on_topic
        self.setStyleSheet(
            "QFrame{background:#ffffff;border-radius:14px;"
            "border:1px solid #e2e8f0;}"
        )
        self._build()

    def _build(self):
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(18, 16, 18, 16)
        self._outer.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        name_lbl = QLabel(f"{self._rm.icon}  {self._rm.name}")
        name_lbl.setStyleSheet(
            "color:#1a1f2e;font-size:15px;font-weight:bold;"
            "background:transparent;border:none;"
        )
        pct_lbl = QLabel(f"{self._rm.progress}%")
        pct_lbl.setStyleSheet(
            f"color:{self._rm.color};font-size:14px;font-weight:bold;"
            "background:transparent;border:none;"
        )
        self._expand_btn = QPushButton("▼" if self._rm.expanded else "▶")
        self._expand_btn.setFixedSize(26, 26)
        self._expand_btn.setStyleSheet(
            "QPushButton{background:transparent;border:none;"
            "color:#718096;font-size:12px;}"
            "QPushButton:hover{color:#2d3748;}"
        )
        self._expand_btn.clicked.connect(self._toggle)
        hdr.addWidget(name_lbl); hdr.addStretch()
        hdr.addWidget(pct_lbl); hdr.addWidget(self._expand_btn)
        self._outer.addLayout(hdr)

        # Progress bar
        pb = QProgressBar()
        pb.setValue(self._rm.progress)
        pb.setTextVisible(False)
        pb.setFixedHeight(6)
        pb.setStyleSheet(
            f"QProgressBar{{background:#e2e8f0;border-radius:3px;border:none;}}"
            f"QProgressBar::chunk{{background:{self._rm.color};border-radius:3px;}}"
        )
        self._outer.addWidget(pb)

        # Topics grid
        self._topics_widget = QWidget()
        self._topics_widget.setStyleSheet("background:transparent;")
        grid = QGridLayout(self._topics_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)
        for i, topic in enumerate(self._rm.topics):
            btn = self._make_topic_btn(topic)
            grid.addWidget(btn, i // 2, i % 2)
        self._outer.addWidget(self._topics_widget)
        self._topics_widget.setVisible(self._rm.expanded)

    def _make_topic_btn(self, topic: Topic) -> QPushButton:
        STYLES = {
            TopicStatus.DONE: (
                f"background:#f0fff4;border:1.5px solid {self._rm.color};"
                "border-radius:10px;color:#276749;",
                f"background:#c6f6d5;border:1.5px solid {self._rm.color};"
                "border-radius:10px;color:#276749;"
            ),
            TopicStatus.IN_PROGRESS: (
                "background:#fffbeb;border:1.5px solid #f6ad55;"
                "border-radius:10px;color:#744210;",
                "background:#fefcbf;border:1.5px solid #f6ad55;"
                "border-radius:10px;color:#744210;"
            ),
            TopicStatus.LOCKED: (
                "background:#f7f8fc;border:1.5px solid #e2e8f0;"
                "border-radius:10px;color:#a0aec0;",
                None
            ),
        }
        normal, hover = STYLES[topic.status]
        btn = QPushButton(topic.display_name)
        btn.setMinimumHeight(36)
        hover_css = f"QPushButton:hover{{" + hover + "}}" if hover else ""
        btn.setStyleSheet(
            f"QPushButton{{font-size:12px;font-weight:500;"
            f"text-align:left;padding:0 10px;{normal}}}"
            + hover_css
        )
        if topic.status != TopicStatus.LOCKED:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, t=topic: self._on_topic(t))
        else:
            btn.setEnabled(False)
        return btn

    def _toggle(self):
        self._rm.expanded = not self._rm.expanded
        self._topics_widget.setVisible(self._rm.expanded)
        self._expand_btn.setText("▼" if self._rm.expanded else "▶")


# ---------------------------------------------------------------------------
# Topic detail dialog
# ---------------------------------------------------------------------------

class TopicDialog(QDialog):
    def __init__(self, topic: Topic, parent=None):
        super().__init__(parent)
        self.setWindowTitle(topic.name)
        self.setMinimumWidth(380)
        self.setStyleSheet(
            "QDialog{background:#fff;font-family:'Segoe UI',Arial,sans-serif;}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        title = QLabel(f"📚 {topic.name}")
        title.setStyleSheet("font-size:16px;font-weight:bold;color:#1a1f2e;")
        lay.addWidget(title)

        badge_info = {
            TopicStatus.DONE:        ("✅ Đã hoàn thành", "#f0fff4", "#276749"),
            TopicStatus.IN_PROGRESS: ("⏳ Đang học",       "#fffbeb", "#744210"),
            TopicStatus.LOCKED:      ("🔒 Chưa mở khóa",  "#f7f8fc", "#718096"),
        }
        txt, bg, fg = badge_info[topic.status]
        badge = QLabel(txt)
        badge.setStyleSheet(
            f"background:{bg};color:{fg};border-radius:8px;"
            f"padding:6px 14px;font-size:13px;font-weight:600;"
        )
        badge.setFixedHeight(34)
        lay.addWidget(badge)

        if topic.detail:
            desc = QLabel(topic.detail)
            desc.setWordWrap(True)
            desc.setStyleSheet("color:#4a5568;font-size:13px;")
            lay.addWidget(desc)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.setStyleSheet(
            "QPushButton{background:#4a6cf7;color:white;border:none;"
            "border-radius:8px;padding:8px 20px;font-size:13px;}"
            "QPushButton:hover{background:#3b5bdb;}"
        )
        btns.accepted.connect(self.accept)
        lay.addWidget(btns)


# ---------------------------------------------------------------------------
# RoadmapView
# ---------------------------------------------------------------------------

class RoadmapView(BaseController):
    """Controller + View trang Lộ Trình."""

    UI_FILE = "roadmap_page.ui"

    goal_added = pyqtSignal(str)

    def __init__(self, settings: AppSettings, parent=None):
        self._settings = settings
        super().__init__(parent)

    def setup_ui(self):
        self._state  = AppState.instance()
        self._filter = "Tất cả môn học"

        # Populate subject filter
        self.roadmapSubjectFilter.clear()
        subjects = ["Tất cả môn học"] + [r.name for r in self._state.roadmap]
        self.roadmapSubjectFilter.addItems(subjects)

        # Populate goal subject combo
        self.goalSubjectCombo.clear()
        self.goalSubjectCombo.addItems([r.name for r in self._state.roadmap])

        # Render
        self._build_cards()
        self._update_overall()

    def connect_signals(self):
        self.roadmapSubjectFilter.currentTextChanged.connect(self._on_filter)
        self.btnAddGoal.clicked.connect(self._add_goal_dialog)
        self.btnSaveGoal.clicked.connect(self._save_inline_goal)

    def refresh(self):
        self._update_overall()
        self._rebuild_cards()

    # ── Cards ─────────────────────────────────────────────────────────

    def _build_cards(self):
        layout = self.roadmapItemsLayout
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        # Xoá placeholder
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for rm in self._state.roadmap:
            if self._filter not in ("Tất cả môn học",) and self._filter != rm.name:
                continue
            card = SubjectCard(rm, self._show_topic, self)
            layout.addWidget(card)

        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )

    def _rebuild_cards(self):
        self._build_cards()

    def _on_filter(self, text: str):
        self._filter = text
        self._build_cards()

    # ── Overall progress ──────────────────────────────────────────────

    def _update_overall(self):
        pct = self._state.overall_progress
        self.overallProgress.setValue(pct)
        total     = sum(len(r.topics) for r in self._state.roadmap)
        remaining = total - sum(
            sum(1 for t in r.topics if t.status == TopicStatus.DONE)
            for r in self._state.roadmap
        )
        for lbl in self.findChildren(QLabel):
            if "hoàn thành" in lbl.text() and "chủ đề" in lbl.text():
                lbl.setText(f"{pct}% hoàn thành  ·  {remaining} chủ đề còn lại")
                break

    # ── Topic dialog ─────────────────────────────────────────────────

    def _show_topic(self, topic: Topic):
        dlg = TopicDialog(topic, self)
        dlg.exec()

    # ── Goal ─────────────────────────────────────────────────────────

    def _add_goal_dialog(self):
        """Dùng TaskDialog để thêm goal (tạm dùng chung)."""
        from src.views.dialogs.task_dialog import TaskDialog
        dlg = TaskDialog(parent=self)
        if dlg.exec() == TaskDialog.DialogCode.Accepted:
            task = dlg.get_task()
            if task:
                self._state.add_task(task)
                self.goal_added.emit(task.subject)
                self.show_info(self, "Thành công",
                               f"✅ Đã thêm mục tiêu: {task.title}")

    def _save_inline_goal(self):
        title = self.goalTitleInput.text().strip()
        if not title:
            self.show_warning(self, "Thiếu thông tin",
                              "Vui lòng nhập tiêu đề mục tiêu!")
            self.goalTitleInput.setFocus()
            return
        sd = self.goalStartDate.date()
        ed = self.goalEndDate.date()
        if ed < sd:
            self.show_warning(self, "Ngày không hợp lệ",
                              "Ngày kết thúc phải sau ngày bắt đầu!")
            return
        subject = strip_icon(self.goalSubjectCombo.currentText())
        self.goal_added.emit(subject)
        self.goalTitleInput.clear()
        self.goalDescInput.clear()
        self.show_info(self, "Thành công",
                       f"✅ Đã thêm mục tiêu:\n«{title}»")