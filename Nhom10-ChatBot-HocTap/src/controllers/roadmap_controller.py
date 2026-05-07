"""
roadmap_controller.py
---------------------
Controller cho trang Lộ Trình Học (Roadmap).

Chức năng:
  - Hiển thị thanh tiến độ tổng thể
  - Expand / Collapse từng môn học
  - Lọc theo môn học (ComboBox)
  - Form thêm mục tiêu mới (validate đầy đủ)
  - Cập nhật tiến độ khi trạng thái topic thay đổi
  - Click vào topic → hiện dialog chi tiết
"""

from dataclasses import dataclass, field
from datetime    import date
from typing      import List, Dict

from PyQt6.QtCore    import Qt, QDate, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui     import QColor, QBrush, QFont
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QSizePolicy, QDialog, QDialogButtonBox,
    QTextEdit, QScrollArea, QWidget, QGridLayout, QSpacerItem,
)

from controllers.base_controller import BaseController


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Topic:
    name:    str
    status:  str   # "done" | "in_progress" | "locked"
    detail:  str = ""


@dataclass
class SubjectRoadmap:
    name:     str
    icon:     str
    color:    str          # accent color hex
    topics:   List[Topic] = field(default_factory=list)
    expanded: bool = True

    @property
    def progress(self) -> int:
        if not self.topics:
            return 0
        done = sum(1 for t in self.topics
                   if t.status in ("done", "in_progress"))
        # done = 1 điểm, in_progress = 0.5 điểm
        score = sum(
            1.0 if t.status == "done" else 0.5
            for t in self.topics
        )
        return int(score / len(self.topics) * 100)


@dataclass
class Goal:
    title:   str
    subject: str
    start:   date
    end:     date
    desc:    str = ""


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

ROADMAP_DATA: List[SubjectRoadmap] = [
    SubjectRoadmap("Toán Học", "📐", "#4a6cf7", [
        Topic("Đại số cơ bản",       "done",        "Các phép tính, phương trình bậc 1, bậc 2."),
        Topic("Hàm số & đồ thị",     "done",        "Hàm bậc 1, bậc 2, logarit, mũ."),
        Topic("Giải tích vi phân",   "in_progress", "Giới hạn, đạo hàm, ứng dụng."),
        Topic("Tích phân",           "in_progress", "Tích phân bất định, xác định."),
        Topic("Đại số tuyến tính",   "locked",      "Ma trận, định thức, không gian vectơ."),
        Topic("Xác suất thống kê",   "locked",      "Biến ngẫu nhiên, phân phối xác suất."),
    ]),
    SubjectRoadmap("Hóa Học", "🧪", "#38a169", [
        Topic("Nguyên tử & phân tử",   "done",        "Cấu tạo nguyên tử, liên kết hóa học."),
        Topic("Bảng tuần hoàn",        "done",        "Chu kỳ, nhóm, tính chất các nguyên tố."),
        Topic("Phản ứng oxi hóa khử", "done",        "Cân bằng phương trình oxi hóa khử."),
        Topic("Điện phân dung dịch",   "in_progress", "Điện phân nóng chảy và dung dịch."),
        Topic("Hóa hữu cơ nâng cao",  "locked",      "Hiđrocacbon, dẫn xuất halo, ancol."),
    ]),
    SubjectRoadmap("Vật Lý", "⚛️", "#e53e3e", [
        Topic("Cơ học",              "done",        "Động học, động lực học, định luật Newton."),
        Topic("Nhiệt học",           "done",        "Nguyên lý nhiệt động lực học."),
        Topic("Điện học",            "in_progress", "Điện trường, mạch điện, điện từ."),
        Topic("Sóng & dao động",     "locked",      "Dao động điều hòa, sóng cơ, sóng điện từ."),
        Topic("Quang học",           "locked",      "Phản xạ, khúc xạ, giao thoa ánh sáng."),
        Topic("Vật lý hạt nhân",     "locked",      "Phóng xạ, phân hạch, tổng hợp hạt nhân."),
    ]),
    SubjectRoadmap("Tiếng Anh", "🇬🇧", "#d69e2e", [
        Topic("Ngữ pháp cơ bản",    "done",        "Thì, mệnh đề, câu điều kiện."),
        Topic("Từ vựng A2–B1",      "done",        "2000 từ vựng thông dụng nhất."),
        Topic("Đọc hiểu",           "done",        "Kỹ năng skimming, scanning."),
        Topic("Nghe & Nói",         "in_progress", "Luyện nghe podcast, hội thoại."),
        Topic("Từ vựng B2",         "locked",      "Từ vựng học thuật, chuyên ngành."),
        Topic("IELTS Writing",      "locked",      "Task 1, Task 2 band 6.5+."),
    ]),
]

SUBJECT_NAMES = ["Tất cả môn học"] + [s.name for s in ROADMAP_DATA]


# ---------------------------------------------------------------------------
# Helper widgets
# ---------------------------------------------------------------------------

STATUS_STYLE = {
    "done": (
        "background:#f0fff4;border-radius:10px;border:1.5px solid {color};",
        "color:{dark};font-size:12px;font-weight:500;background:transparent;border:none;",
        "✅ {name}",
    ),
    "in_progress": (
        "background:#fffbeb;border-radius:10px;border:1.5px solid #f6ad55;",
        "color:#744210;font-size:12px;font-weight:500;background:transparent;border:none;",
        "⏳ {name}",
    ),
    "locked": (
        "background:#f7f8fc;border-radius:10px;border:1.5px solid #e2e8f0;",
        "color:#a0aec0;font-size:12px;font-weight:500;background:transparent;border:none;",
        "🔒 {name}",
    ),
}


def _dark(hex_color: str) -> str:
    """Trả về màu tối hơn một chút (dùng cho text done)."""
    return "#276749"  # default dark-green; cải tiến sau nếu cần


def make_topic_frame(topic: Topic, color: str,
                     on_click=None) -> QPushButton:
    """Tạo một QPushButton hình card cho một topic."""
    style_frame, style_lbl, text_tpl = STATUS_STYLE[topic.status]

    btn = QPushButton()
    btn.setText(text_tpl.format(name=topic.name))
    btn.setMinimumHeight(36)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setToolTip(topic.detail or topic.name)

    if topic.status == "done":
        frame_css = style_frame.replace("{color}", color)
        text_css  = style_lbl.replace("{dark}", _dark(color))
        btn.setStyleSheet(
            f"QPushButton{{{frame_css}color:{_dark(color)};"
            f"font-size:12px;font-weight:500;text-align:left;padding:0 10px;}}"
            f"QPushButton:hover{{opacity:0.85;border-width:2px;}}"
        )
    elif topic.status == "in_progress":
        btn.setStyleSheet(
            "QPushButton{background:#fffbeb;border-radius:10px;"
            "border:1.5px solid #f6ad55;color:#744210;"
            "font-size:12px;font-weight:500;text-align:left;padding:0 10px;}"
            "QPushButton:hover{background:#fefcbf;}"
        )
    else:
        btn.setStyleSheet(
            "QPushButton{background:#f7f8fc;border-radius:10px;"
            "border:1.5px solid #e2e8f0;color:#a0aec0;"
            "font-size:12px;font-weight:500;text-align:left;padding:0 10px;}"
        )
        btn.setEnabled(False)

    if on_click and topic.status != "locked":
        btn.clicked.connect(lambda _, t=topic: on_click(t))

    return btn


# ---------------------------------------------------------------------------
# Topic detail dialog
# ---------------------------------------------------------------------------

class TopicDetailDialog(QDialog):
    def __init__(self, topic: Topic, parent=None):
        super().__init__(parent)
        self.setWindowTitle(topic.name)
        self.setMinimumWidth(400)
        self.setStyleSheet("font-family:'Segoe UI',Arial,sans-serif;")

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # Title
        title_lbl = QLabel(f"📚 {topic.name}")
        title_lbl.setStyleSheet("font-size:16px;font-weight:bold;color:#1a1f2e;")
        layout.addWidget(title_lbl)

        # Status badge
        badge_map = {
            "done":        ("✅ Đã hoàn thành", "#f0fff4", "#276749"),
            "in_progress": ("⏳ Đang học",       "#fffbeb", "#744210"),
            "locked":      ("🔒 Chưa mở",        "#f7f8fc", "#718096"),
        }
        badge_text, bg, fg = badge_map[topic.status]
        badge = QLabel(badge_text)
        badge.setStyleSheet(
            f"background:{bg};color:{fg};border-radius:8px;"
            f"padding:6px 14px;font-size:13px;font-weight:600;"
        )
        badge.setFixedHeight(32)
        layout.addWidget(badge)

        # Description
        if topic.detail:
            desc = QLabel(topic.detail)
            desc.setWordWrap(True)
            desc.setStyleSheet("color:#4a5568;font-size:13px;line-height:1.6;")
            layout.addWidget(desc)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(self.accept)
        btns.setStyleSheet(
            "QPushButton{background:#4a6cf7;color:white;border:none;"
            "border-radius:8px;padding:8px 20px;font-size:13px;}"
            "QPushButton:hover{background:#3b5bdb;}"
        )
        layout.addWidget(btns)


# ---------------------------------------------------------------------------
# Goal detail dialog
# ---------------------------------------------------------------------------

class AddGoalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Mục Tiêu Mới")
        self.setMinimumWidth(420)
        self.setStyleSheet("font-family:'Segoe UI',Arial,sans-serif;background:#fff;")
        self._result: Goal | None = None

        from PyQt6.QtWidgets import (
            QFormLayout, QLineEdit, QComboBox,
            QDateEdit, QPlainTextEdit, QDialogButtonBox
        )
        from PyQt6.QtCore import QDate

        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(14)

        title_lbl = QLabel("🎯 Thêm Mục Tiêu Học Tập")
        title_lbl.setStyleSheet("font-size:16px;font-weight:bold;color:#1a1f2e;")
        main.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        field_style = (
            "QLineEdit,QComboBox,QDateEdit,QPlainTextEdit{"
            "background:#f7f8fc;border:1px solid #e2e8f0;"
            "border-radius:8px;padding:6px 12px;font-size:13px;color:#2d3748;}"
            "QLineEdit:focus,QComboBox:focus,QDateEdit:focus,QPlainTextEdit:focus{"
            "border-color:#4a6cf7;background:#fff;}"
        )
        lbl_style = "color:#4a5568;font-size:12px;font-weight:600;"

        self.titleEdit = QLineEdit()
        self.titleEdit.setPlaceholderText("Tiêu đề mục tiêu...")
        self.titleEdit.setMinimumHeight(38)
        self.titleEdit.setStyleSheet(field_style)

        self.subjectCombo = QComboBox()
        self.subjectCombo.addItems(
            ["📐 Toán Học", "🧪 Hóa Học", "⚛️ Vật Lý",
             "🇬🇧 Tiếng Anh", "📖 Ngữ Văn", "🌿 Sinh Học"]
        )
        self.subjectCombo.setMinimumHeight(38)
        self.subjectCombo.setStyleSheet(field_style)

        self.startDate = QDateEdit(QDate.currentDate())
        self.startDate.setCalendarPopup(True)
        self.startDate.setMinimumHeight(38)
        self.startDate.setStyleSheet(field_style)

        self.endDate = QDateEdit(QDate.currentDate().addDays(30))
        self.endDate.setCalendarPopup(True)
        self.endDate.setMinimumHeight(38)
        self.endDate.setStyleSheet(field_style)

        self.descEdit = QPlainTextEdit()
        self.descEdit.setPlaceholderText("Mô tả chi tiết mục tiêu...")
        self.descEdit.setFixedHeight(80)
        self.descEdit.setStyleSheet(field_style)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(lbl_style)
            return l

        form.addRow(lbl("Tiêu đề *"),   self.titleEdit)
        form.addRow(lbl("Môn học"),     self.subjectCombo)
        form.addRow(lbl("Bắt đầu"),     self.startDate)
        form.addRow(lbl("Kết thúc"),    self.endDate)
        form.addRow(lbl("Mô tả"),       self.descEdit)
        main.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.setStyleSheet(
            "QPushButton{background:#4a6cf7;color:white;border:none;"
            "border-radius:8px;padding:8px 20px;font-size:13px;}"
            "QPushButton:hover{background:#3b5bdb;}"
        )
        btns.accepted.connect(self._on_save)
        btns.rejected.connect(self.reject)
        main.addWidget(btns)

    def _on_save(self):
        from PyQt6.QtWidgets import QMessageBox
        title = self.titleEdit.text().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng nhập tiêu đề mục tiêu!")
            return
        sd = self.startDate.date()
        ed = self.endDate.date()
        if ed < sd:
            QMessageBox.warning(self, "Ngày không hợp lệ",
                                "Ngày kết thúc phải sau ngày bắt đầu!")
            return
        subject = self.subjectCombo.currentText()
        for name in ["Toán Học", "Hóa Học", "Vật Lý",
                     "Tiếng Anh", "Ngữ Văn", "Sinh Học"]:
            if name in subject:
                subject = name
                break
        self._result = Goal(
            title=title, subject=subject,
            start=date(sd.year(), sd.month(), sd.day()),
            end=date(ed.year(), ed.month(), ed.day()),
            desc=self.descEdit.toPlainText().strip(),
        )
        self.accept()

    def get_goal(self) -> "Goal | None":
        return self._result


# ---------------------------------------------------------------------------
# Subject card widget (inline, không dùng file .ui)
# ---------------------------------------------------------------------------

class SubjectCard(QFrame):
    """Card hiển thị lộ trình một môn, có nút expand/collapse."""

    def __init__(self, roadmap: SubjectRoadmap, on_topic_click, parent=None):
        super().__init__(parent)
        self._roadmap = roadmap
        self._on_topic_click = on_topic_click
        self._expanded = roadmap.expanded
        self._build()

    def _build(self):
        self.setStyleSheet(
            "QFrame{background:#ffffff;border-radius:14px;"
            "border:1px solid #e2e8f0;}"
        )
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(18, 16, 18, 16)
        self._outer.setSpacing(12)

        # ── Header row ──
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        name_lbl = QLabel(f"{self._roadmap.icon}  {self._roadmap.name}")
        name_lbl.setStyleSheet(
            "color:#1a1f2e;font-size:15px;font-weight:bold;"
            "background:transparent;border:none;"
        )

        pct_lbl = QLabel(f"{self._roadmap.progress}%")
        pct_lbl.setStyleSheet(
            f"color:{self._roadmap.color};font-size:14px;"
            f"font-weight:bold;background:transparent;border:none;"
        )

        self._expand_btn = QPushButton("▼" if self._expanded else "▶")
        self._expand_btn.setFixedSize(26, 26)
        self._expand_btn.setStyleSheet(
            "QPushButton{background:transparent;border:none;"
            "color:#718096;font-size:12px;}"
            "QPushButton:hover{color:#2d3748;}"
        )
        self._expand_btn.clicked.connect(self._toggle)

        hdr.addWidget(name_lbl)
        hdr.addStretch()
        hdr.addWidget(pct_lbl)
        hdr.addWidget(self._expand_btn)
        self._outer.addLayout(hdr)

        # ── Progress bar ──
        pbar = QProgressBar()
        pbar.setValue(self._roadmap.progress)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(6)
        pbar.setStyleSheet(
            f"QProgressBar{{background:#e2e8f0;border-radius:3px;border:none;}}"
            f"QProgressBar::chunk{{background:{self._roadmap.color};border-radius:3px;}}"
        )
        self._outer.addWidget(pbar)

        # ── Topics grid (collapsible) ──
        self._topics_widget = QWidget()
        self._topics_widget.setStyleSheet("background:transparent;")
        grid = QGridLayout(self._topics_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        cols = 2
        for i, topic in enumerate(self._roadmap.topics):
            btn = make_topic_frame(
                topic, self._roadmap.color, self._on_topic_click
            )
            grid.addWidget(btn, i // cols, i % cols)

        self._outer.addWidget(self._topics_widget)
        self._topics_widget.setVisible(self._expanded)

    def _toggle(self):
        self._expanded = not self._expanded
        self._topics_widget.setVisible(self._expanded)
        self._expand_btn.setText("▼" if self._expanded else "▶")
        self._roadmap.expanded = self._expanded


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------

class RoadmapController(BaseController):
    """Controller trang Lộ Trình Học."""

    UI_FILE = "roadmap_page.ui"

    goal_added = pyqtSignal(str)   # tên môn học được thêm goal

    # ------------------------------------------------------------------ #
    #  Khởi tạo                                                           #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        self._goals: list[Goal] = []
        self._filter: str = "Tất cả môn học"
        self._subject_cards: list[SubjectCard] = []

        # Xóa nội dung mẫu cứng trong .ui, render lại từ data
        self._clear_roadmap_layout()
        self._build_roadmap_cards()
        self._update_overall_progress()

        # Populate subject filter combo
        self.roadmapSubjectFilter.clear()
        self.roadmapSubjectFilter.addItems(SUBJECT_NAMES)

    def connect_signals(self):
        self.btnAddGoal.clicked.connect(self._open_add_goal_dialog)
        self.roadmapSubjectFilter.currentTextChanged.connect(
            self._on_filter_changed
        )

        # Form bên phải (vẫn giữ nhanh cho người dùng nhập inline)
        self.btnSaveGoal.clicked.connect(self._save_goal_inline)

    def refresh(self):
        self._update_overall_progress()

    # ------------------------------------------------------------------ #
    #  Build roadmap                                                       #
    # ------------------------------------------------------------------ #

    def _clear_roadmap_layout(self):
        """Xóa toàn bộ widget cũ trong scroll area."""
        layout = self.roadmapItemsLayout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _build_roadmap_cards(self):
        self._subject_cards.clear()
        layout = self.roadmapItemsLayout
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        for roadmap in ROADMAP_DATA:
            if self._filter not in ("Tất cả môn học",) and \
               self._filter not in roadmap.name:
                continue
            card = SubjectCard(roadmap, self._show_topic_detail, self)
            self._subject_cards.append(card)
            layout.addWidget(card)

        # Spacer cuối
        layout.addItem(
            QSpacerItem(0, 0,
                        QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )

    def _on_filter_changed(self, text: str):
        self._filter = text
        self._clear_roadmap_layout()
        self._build_roadmap_cards()

    # ------------------------------------------------------------------ #
    #  Overall progress                                                    #
    # ------------------------------------------------------------------ #

    def _update_overall_progress(self):
        total_topics = sum(len(r.topics) for r in ROADMAP_DATA)
        done_topics  = sum(
            sum(1 for t in r.topics if t.status == "done")
            for r in ROADMAP_DATA
        )
        pct = int(done_topics / total_topics * 100) if total_topics else 0
        self.overallProgress.setValue(pct)

        remaining = total_topics - done_topics
        # Cập nhật label trong gradient card
        # (label nằm trong layout của overallProgress's parent)
        # Tìm QLabel con hiển thị text tóm tắt
        for lbl in self.findChildren(QLabel):
            if "hoàn thành" in lbl.text() and "chủ đề" in lbl.text():
                lbl.setText(
                    f"{pct}% hoàn thành  ·  {remaining} chủ đề còn lại"
                )
                break

    # ------------------------------------------------------------------ #
    #  Topic detail                                                        #
    # ------------------------------------------------------------------ #

    def _show_topic_detail(self, topic: Topic):
        dlg = TopicDetailDialog(topic, self)
        dlg.exec()

    # ------------------------------------------------------------------ #
    #  Add goal – Dialog                                                   #
    # ------------------------------------------------------------------ #

    def _open_add_goal_dialog(self):
        dlg = AddGoalDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            goal = dlg.get_goal()
            if goal:
                self._goals.append(goal)
                self.goal_added.emit(goal.subject)
                self.show_info(
                    self, "Thành công",
                    f"✅ Đã thêm mục tiêu:\n«{goal.title}»"
                )

    # ------------------------------------------------------------------ #
    #  Add goal – Inline form (bên phải UI)                               #
    # ------------------------------------------------------------------ #

    def _save_goal_inline(self):
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

        subject_raw = self.goalSubjectCombo.currentText()
        subject = subject_raw
        for name in ["Toán Học", "Hóa Học", "Vật Lý",
                     "Tiếng Anh", "Ngữ Văn", "Sinh Học"]:
            if name in subject_raw:
                subject = name
                break

        goal = Goal(
            title=title, subject=subject,
            start=date(sd.year(), sd.month(), sd.day()),
            end=date(ed.year(), ed.month(), ed.day()),
            desc=self.goalDescInput.toPlainText().strip(),
        )
        self._goals.append(goal)
        self.goal_added.emit(goal.subject)

        # Reset form
        self.goalTitleInput.clear()
        self.goalDescInput.clear()

        self.show_info(self, "Thành công",
                       f"✅ Đã thêm mục tiêu:\n«{goal.title}»")
        # ---------- THÊM HÀM MỚI NÀY ĐỂ PHỤC VỤ TOOL ----------
def generate_learning_roadmap(self, subject: str, level: str = "beginner") -> dict:
    """Hàm tạo lộ trình học tập dạng roadmap. Dùng làm tool cho Gemini."""
    # Logic tạo roadmap đơn giản dựa trên môn học
    roadmap = {
        "subject": subject,
        "level": level,
        "topics": []
    }
    # Ví dụ cho Python
    if subject.lower() == "python":
        roadmap["icon"] = "🐍"
        roadmap["color"] = "#306998"
        roadmap["topics"] = [
            {"name": "Cú pháp cơ bản", "status": "done" if level == "beginner" else "done", "detail": "Biến, vòng lặp, câu lệnh điều kiện"},
            {"name": "Hàm và module", "status": "in_progress" if level == "beginner" else "done", "detail": "Định nghĩa hàm, import module"},
            {"name": "Lập trình hướng đối tượng", "status": "locked" if level == "beginner" else "in_progress", "detail": "Class, object, kế thừa"}
        ]
    else:
        roadmap["icon"] = "📚"
        roadmap["color"] = "#4a6cf7"
        roadmap["topics"] = [
            {"name": f"Nhập môn {subject}", "status": "in_progress", "detail": f"Các khái niệm cơ bản của {subject}"},
            {"name": f"{subject} nâng cao", "status": "locked", "detail": f"Các chủ đề chuyên sâu của {subject}"}
        ]
    return roadmap