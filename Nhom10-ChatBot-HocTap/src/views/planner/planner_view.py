"""
src/views/planner/planner_view.py
-----------------------------------
View trang Lịch Học + Pomodoro Timer.

Layout:
  ┌────────────────────┬─────────────────────┐
  │  Lịch tuần        │  Form thêm task      │
  │  Danh sách hôm nay│  Pomodoro Timer      │
  └────────────────────┴─────────────────────┘
"""
from datetime import date, timedelta

from PyQt6.QtCore    import Qt, QDate, QTime, pyqtSignal, QTimer
from PyQt6.QtGui     import QColor, QBrush
from PyQt6.QtWidgets import (
    QTableWidgetItem, QVBoxLayout, QScrollArea, QWidget,
    QFrame, QSizePolicy,
)

from src.controllers.base_controller      import BaseController
from src.models.app_state                 import AppState
from src.models.task                      import Task, Priority
from src.models.settings                  import AppSettings
from src.utils.date_helpers               import format_date_vi, format_month_vi, week_start
from src.utils.study_subjects             import subject_combo_items, strip_icon
from src.views.components.task_item       import TaskItem
from src.views.components.pomodoro_timer  import PomodoroTimer
from src.views.dialogs.task_dialog        import TaskDialog


class PlannerView(BaseController):
    """Controller + View trang Lịch Học."""

    UI_FILE = "planner_page.ui"

    tasks_changed = pyqtSignal()   # → Dashboard, MainWindow

    def __init__(self, settings: AppSettings, parent=None):
        self._settings = settings
        super().__init__(parent)

    # ── Setup ────────────────────────────────────────────────────────

    def setup_ui(self):
        self._state   = AppState.instance()
        self._week_dt = week_start(date.today())

        # Cài QTableWidget
        self._setup_table()
        # Cài subject combo
        self.taskSubjectCombo.clear()
        self.taskSubjectCombo.addItems(subject_combo_items())
        # Default form
        self.taskDateEdit.setDate(QDate.currentDate())
        self.taskTimeEdit.setTime(QTime(8, 0))
        self.taskDurationSpin.setValue(60)
        self._select_priority("medium")
        # Nhúng Pomodoro vào panel phải (sau addTaskForm)
        self._inject_pomodoro()
        # Render
        self._render_week()
        self._render_today()
        self._update_week_label()

    def connect_signals(self):
        self.btnPrevWeek.clicked.connect(self._prev_week)
        self.btnNextWeek.clicked.connect(self._next_week)
        self.btnWeekView.clicked.connect(lambda: self.btnWeekView.setChecked(True))
        self.btnDayView.clicked.connect(lambda: self.btnDayView.setChecked(True))
        self.btnAddTask.clicked.connect(self._open_task_dialog)
        self.btnSaveTask.clicked.connect(self._save_inline_task)
        self.btnCancelTask.clicked.connect(self._reset_form)
        self.priorityHigh.clicked.connect(lambda: self._select_priority("high"))
        self.priorityMed.clicked.connect(lambda: self._select_priority("medium"))
        self.priorityLow.clicked.connect(lambda: self._select_priority("low"))

    def refresh(self):
        self._render_week()
        self._render_today()

    # ── Week calendar ─────────────────────────────────────────────────

    def _setup_table(self):
        tbl = self.weekCalendar
        tbl.setRowCount(1)
        tbl.setColumnCount(7)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(False)
        tbl.setSelectionMode(tbl.SelectionMode.SingleSelection)
        tbl.horizontalHeader().setSectionResizeMode(
            tbl.horizontalHeader().ResizeMode.Stretch
        )
        tbl.setFixedHeight(80)

    def _render_week(self):
        tbl   = self.weekCalendar
        today = date.today()
        tbl.setHorizontalHeaderLabels(["T2","T3","T4","T5","T6","T7","CN"])
        for col in range(7):
            d       = self._week_dt + timedelta(days=col)
            tasks_n = len(self._state.tasks_for_date(d))
            badge   = f" [{tasks_n}]" if tasks_n else ""
            item    = QTableWidgetItem(f"{d.day}{badge}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if d == today:
                item.setBackground(QBrush(QColor("#4a6cf7")))
                item.setForeground(QBrush(QColor("#ffffff")))
            elif tasks_n:
                item.setBackground(QBrush(QColor("#ebf4ff")))
                item.setForeground(QBrush(QColor("#2b6cb0")))
            tbl.setItem(0, col, item)

    def _update_week_label(self):
        self.weekLabel.setText(format_month_vi(self._week_dt))

    def _prev_week(self):
        self._week_dt -= timedelta(weeks=1)
        self._render_week(); self._update_week_label()

    def _next_week(self):
        self._week_dt += timedelta(weeks=1)
        self._render_week(); self._update_week_label()

    # ── Today tasks ───────────────────────────────────────────────────

    def _render_today(self):
        """Xoá và rebuild danh sách TaskItem cho hôm nay."""
        # Xoá task items cũ (giữ lại label tiêu đề)
        # Tìm container layout chứa task items
        container = self._get_today_container()
        if not container:
            return

        # Xoá widget cũ (bỏ qua widget đầu là QLabel tiêu đề)
        while container.count() > 1:
            item = container.takeAt(1)
            if item and item.widget():
                item.widget().deleteLater()

        today_tasks = self._state.tasks_for_date(date.today())
        if not today_tasks:
            from PyQt6.QtWidgets import QLabel
            empty = QLabel("🎉 Không có nhiệm vụ nào hôm nay!")
            empty.setStyleSheet("color:#718096;font-size:13px;padding:10px;")
            container.addWidget(empty)
        else:
            for task in today_tasks:
                item_w = TaskItem(task)
                item_w.done_changed.connect(self._on_task_done_changed)
                item_w.delete_requested.connect(self._on_task_deleted)
                container.addWidget(item_w)

        self.tasks_changed.emit()

    def _get_today_container(self):
        """Tìm QVBoxLayout của frame chứa danh sách task hôm nay."""
        # Frame được đặt tên trong UI hoặc tìm qua cấu trúc
        frame = getattr(self, "todayTasksFrame", None) or \
                self.findChild(QFrame, "todayTasksFrame")
        if frame and frame.layout():
            return frame.layout()
        # Fallback: dùng task1Done/2/3 parent
        cb = getattr(self, "task1Done", None)
        if cb:
            parent_frame = cb.parentWidget()
            while parent_frame:
                if parent_frame.layout() and parent_frame.layout().count() >= 2:
                    return parent_frame.layout()
                parent_frame = parent_frame.parentWidget()
        return None

    def _on_task_done_changed(self, task: Task, done: bool):
        task.done = done
        self.tasks_changed.emit()
        # Cập nhật checkbox UI cũ nếu còn tồn tại
        for cb_name in ["task1Done","task2Done","task3Done"]:
            cb = getattr(self, cb_name, None)
            if cb:
                cb.blockSignals(True)
                today = [t for t in self._state.tasks if t.date == date.today()]
                idx   = ["task1Done","task2Done","task3Done"].index(cb_name)
                if idx < len(today):
                    cb.setChecked(today[idx].done)
                cb.blockSignals(False)

    def _on_task_deleted(self, task: Task):
        if self.confirm(self, "Xoá nhiệm vụ", f"Xoá nhiệm vụ «{task.title}»?"):
            self._state.remove_task(task.id)
            self._render_today()
            self._render_week()

    # ── Priority ──────────────────────────────────────────────────────

    def _select_priority(self, level: str):
        self.priorityHigh.setChecked(level == "high")
        self.priorityMed.setChecked(level  == "medium")
        self.priorityLow.setChecked(level  == "low")

    def _get_priority(self) -> Priority:
        if self.priorityHigh.isChecked(): return Priority.HIGH
        if self.priorityLow.isChecked():  return Priority.LOW
        return Priority.MEDIUM

    # ── Form ─────────────────────────────────────────────────────────

    def _open_task_dialog(self):
        """Mở dialog thêm task đầy đủ."""
        dlg = TaskDialog(parent=self)
        if dlg.exec() == TaskDialog.DialogCode.Accepted:
            task = dlg.get_task()
            if task:
                self._state.add_task(task)
                self._render_today()
                self._render_week()
                self.show_info(self, "Thành công",
                               f"✅ Đã thêm: {task.title}")

    def _save_inline_task(self):
        """Lưu từ form inline bên phải."""
        title = self.taskNameInput.text().strip()
        if not title:
            self.show_warning(self, "Thiếu thông tin",
                              "Vui lòng nhập tên nhiệm vụ!")
            self.taskNameInput.setFocus()
            return

        qd = self.taskDateEdit.date()
        task = Task(
            title    = title,
            subject  = strip_icon(self.taskSubjectCombo.currentText()),
            date     = date(qd.year(), qd.month(), qd.day()),
            start    = self.taskTimeEdit.time(),
            duration = self.taskDurationSpin.value(),
            priority = self._get_priority(),
            notes    = self.taskNotesInput.toPlainText().strip(),
        )
        self._state.add_task(task)
        self._reset_form()
        self._render_today()
        self._render_week()
        self.show_info(self, "Thành công", f"✅ Đã lưu: {title}")

    def _reset_form(self):
        self.taskNameInput.clear()
        self.taskSubjectCombo.setCurrentIndex(0)
        self.taskDateEdit.setDate(QDate.currentDate())
        self.taskTimeEdit.setTime(QTime(8, 0))
        self.taskDurationSpin.setValue(60)
        self._select_priority("medium")
        self.taskNotesInput.clear()

    # ── Pomodoro ──────────────────────────────────────────────────────

    def _inject_pomodoro(self):
        """Tạo PomodoroTimer và nhúng vào panel phải."""
        # Tìm layout của widget cha chứa addTaskForm
        form = getattr(self, "addTaskForm", None)
        if not form:
            return
        parent_lay = form.parentWidget()
        if not parent_lay or not parent_lay.layout():
            return

        self._pomodoro = PomodoroTimer()
        self._pomodoro.setMinimumWidth(280)
        self._pomodoro.setMaximumWidth(300)
        self._pomodoro.session_completed.connect(self._on_pomodoro_done)

        lay = parent_lay.layout()
        # Chèn sau addTaskForm (index 1)
        lay.insertWidget(1, self._pomodoro)

    def _on_pomodoro_done(self, mode: str):
        if mode == "focus":
            self.show_info(self, "🍅 Pomodoro xong!",
                           "Nghỉ ngơi 5 phút rồi tiếp tục học nhé! 💪")

    # ── Public API ────────────────────────────────────────────────────

    def get_stats(self) -> tuple[int, int]:
        return self._state.tasks_done, self._state.tasks_total