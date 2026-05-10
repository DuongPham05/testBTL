"""
db_manager.py - Kết nối và thao tác MySQL qua pymysql.
Cài: pip install pymysql
"""
import pymysql
import json
from datetime import date, datetime
from typing import Optional


class DBManager:
    _instance = None

    @classmethod
    def instance(cls) -> 'DBManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._conn = None
        self._user_id: Optional[int] = None

    # ── Kết nối ──────────────────────────────────────────────────────

    def connect(self, host="localhost", user="root",
                password="", db="edubot", port=3306):
        self._conn = pymysql.connect(
            host=host, user=user, password=password,
            database=db, port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def disconnect(self):
        if self._conn:
            self._conn.close()

    # ── User ─────────────────────────────────────────────────────────

    def get_or_create_user(self, name: str, grade: str = "") -> int:
        """Trả về user_id, tạo mới nếu chưa có."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE name=%s", (name,))
            row = cur.fetchone()
            if row:
                self._user_id = row['id']
                return self._user_id
            cur.execute(
                "INSERT INTO users (name, grade) VALUES (%s, %s)",
                (name, grade)
            )
            self._user_id = self._conn.insert_id()
            return self._user_id

    # ── Goals ────────────────────────────────────────────────────────

    def save_goal(self, subject: str, topic: str,
                  target_pct: int, deadline: date) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO goals
                   (user_id, subject, topic, target_pct, deadline)
                   VALUES (%s,%s,%s,%s,%s)""",
                (self._user_id, subject, topic, target_pct, deadline)
            )
            return self._conn.insert_id()

    def get_goals(self) -> list[dict]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM goals WHERE user_id=%s ORDER BY deadline",
                (self._user_id,)
            )
            return cur.fetchall()

    # ── Study sessions ───────────────────────────────────────────────

    def save_study_session(self, subject: str, topic: str,
                           duration_min: int, progress_pct: int,
                           note: str = "", goal_id: int = None):
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO study_sessions
                   (user_id, goal_id, subject, topic,
                    duration_min, progress_pct, note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (self._user_id, goal_id, subject, topic,
                 duration_min, progress_pct, note)
            )

    def get_sessions_for_subject(self, subject: str) -> list[dict]:
        with self._conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM study_sessions
                   WHERE user_id=%s AND subject=%s
                   ORDER BY studied_at""",
                (self._user_id, subject)
            )
            return cur.fetchall()

    # ── Quiz results ─────────────────────────────────────────────────

    def save_quiz_result(self, subject: str, topic: str,
                         score: float, total_q: int,
                         correct_q: int, weak_areas: list[str]):
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO quiz_results
                   (user_id, subject, topic, score,
                    total_q, correct_q, weak_areas)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (self._user_id, subject, topic, score,
                 total_q, correct_q, json.dumps(weak_areas, ensure_ascii=False))
            )

    def get_quiz_results(self, subject: str = None) -> list[dict]:
        with self._conn.cursor() as cur:
            if subject:
                cur.execute(
                    """SELECT * FROM quiz_results
                       WHERE user_id=%s AND subject=%s
                       ORDER BY taken_at""",
                    (self._user_id, subject)
                )
            else:
                cur.execute(
                    "SELECT * FROM quiz_results WHERE user_id=%s ORDER BY taken_at",
                    (self._user_id,)
                )
            rows = cur.fetchall()
            for r in rows:
                if isinstance(r['weak_areas'], str):
                    r['weak_areas'] = json.loads(r['weak_areas'])
            return rows

    # ── Chat history ─────────────────────────────────────────────────

    def save_chat_message(self, role: str, content: str,
                          session_name: str = ""):
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO chat_history
                   (user_id, session_name, role, content)
                   VALUES (%s,%s,%s,%s)""",
                (self._user_id, session_name, role, content)
            )

    def get_recent_chat(self, limit: int = 20) -> list[dict]:
        with self._conn.cursor() as cur:
            cur.execute(
                """SELECT role, content FROM chat_history
                   WHERE user_id=%s
                   ORDER BY created_at DESC LIMIT %s""",
                (self._user_id, limit)
            )
            rows = cur.fetchall()
            return list(reversed(rows))  # chronological order

    # ── Context tổng hợp cho AI ──────────────────────────────────────

    def get_user_context(self, subject: str = None) -> dict:
        """
        Trả về dict tổng hợp toàn bộ dữ liệu người dùng
        để đưa vào system prompt của AI.
        """
        goals    = self.get_goals()
        sessions = (self.get_sessions_for_subject(subject)
                    if subject else [])
        quizzes  = self.get_quiz_results(subject)

        # Tính tổng thời gian học và % hiện tại
        total_min  = sum(s['duration_min'] for s in sessions)
        current_pct = sessions[-1]['progress_pct'] if sessions else 0

        # Tìm goal liên quan
        related_goal = next(
            (g for g in goals
             if subject and g['subject'] == subject), None
        )

        # Tổng hợp điểm yếu từ quiz
        all_weak = []
        for q in quizzes:
            all_weak.extend(q.get('weak_areas') or [])
        from collections import Counter
        weak_freq = Counter(all_weak).most_common(5)

        return {
            "goals":           goals,
            "sessions":        sessions,
            "quiz_results":    quizzes,
            "total_study_min": total_min,
            "current_pct":     current_pct,
            "related_goal":    related_goal,
            "top_weak_areas":  weak_freq,
        }