"""
date_helpers.py - Các hàm tiện ích xử lý ngày tháng.
"""

from datetime import date, timedelta
from typing import Optional


def get_week_start(d: Optional[date] = None) -> date:
    """Trả về ngày thứ Hai của tuần chứa ngày d (mặc định hôm nay)."""
    if d is None:
        d = date.today()
    return d - timedelta(days=d.weekday())

def get_week_end(d: Optional[date] = None) -> date:
    """Trả về ngày Chủ Nhật của tuần chứa ngày d."""
    start = get_week_start(d)
    return start + timedelta(days=6)

def get_week_range(d: Optional[date] = None) -> tuple[date, date]:
    """Trả về (start_of_week, end_of_week)."""
    start = get_week_start(d)
    return start, start + timedelta(days=6)

def format_date_vi(d: date) -> str:
    """Định dạng ngày tháng theo tiếng Việt: 'Thứ 2, 01/01/2024'."""
    weekdays = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    return f"{weekdays[d.weekday()]}, {d.strftime('%d/%m/%Y')}"

def format_month_year(d: date) -> str:
    """Định dạng tháng/năm: 'Tháng 1, 2024'."""
    months = [
        "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
        "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"
    ]
    return f"{months[d.month-1]}, {d.year}"

def is_today(d: date) -> bool:
    """Kiểm tra xem ngày d có phải hôm nay không."""
    return d == date.today()

def is_tomorrow(d: date) -> bool:
    """Kiểm tra xem ngày d có phải ngày mai không."""
    return d == date.today() + timedelta(days=1)