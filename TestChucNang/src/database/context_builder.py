"""
context_builder.py - Xây dựng system prompt từ dữ liệu người dùng.
"""
from datetime import date
from .db_manager import DBManager


def build_system_prompt(subject: str = None) -> str:
    """
    Tạo system prompt đầy đủ context người dùng.
    AI sẽ đọc prompt này trước khi trả lời.
    """
    db  = DBManager.instance()
    ctx = db.get_user_context(subject)

    lines = [
        "Bạn là trợ lý học tập AI của EduBot.",
        "Dưới đây là hồ sơ học tập thực tế của người dùng:",
        "",
    ]

    # Mục tiêu
    if ctx["related_goal"]:
        g = ctx["related_goal"]
        days_left = (g['deadline'] - date.today()).days
        lines += [
            f"📌 MỤC TIÊU: Hoàn thành {g['target_pct']}% môn {g['subject']}",
            f"   Chủ đề: {g['topic']}",
            f"   Deadline: {g['deadline']} ({days_left} ngày nữa)",
            "",
        ]

    # Tiến độ hiện tại
    if ctx["sessions"]:
        lines += [
            f"📊 TIẾN ĐỘ HIỆN TẠI: {ctx['current_pct']}%",
            f"   Tổng thời gian đã học: {ctx['total_study_min']} phút "
            f"({ctx['total_study_min']//60} giờ {ctx['total_study_min']%60} phút)",
            f"   Số buổi học: {len(ctx['sessions'])}",
            "",
        ]

        # Chi tiết các buổi học gần đây
        recent = ctx["sessions"][-5:]
        lines.append("   Buổi học gần đây:")
        for s in recent:
            lines.append(
                f"   • {s['studied_at'].strftime('%d/%m')}: "
                f"{s['topic']} – {s['duration_min']} phút – "
                f"đạt {s['progress_pct']}%"
            )
        lines.append("")

    # Điểm yếu từ quiz
    if ctx["top_weak_areas"]:
        weak_str = ", ".join(f"{w[0]} ({w[1]} lần)" for w in ctx["top_weak_areas"])
        lines += [
            f"⚠️  ĐIỂM YẾU HAY GẶP: {weak_str}",
            "",
        ]

    # Kết quả quiz gần nhất
    if ctx["quiz_results"]:
        scores = [q['score'] for q in ctx["quiz_results"]]
        avg_score = sum(scores) / len(scores)
        trend = "tăng" if len(scores) >= 2 and scores[-1] > scores[-2] else "giảm/ổn định"
        lines += [
            f"📝 KẾT QUẢ QUIZ: {len(scores)} bài – "
            f"TB {avg_score:.1f}/10 – xu hướng {trend}",
            "",
        ]

    lines += [
        "Dựa trên dữ liệu trên, hãy trả lời câu hỏi của người dùng",
        "một cách cụ thể, cá nhân hóa cho đúng tình huống của họ.",
        "Tránh trả lời chung chung. Đưa ra con số, mốc thời gian cụ thể.",
    ]

    return "\n".join(lines)