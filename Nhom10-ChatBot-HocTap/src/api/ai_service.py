import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Xác định thư mục gốc dự án và nạp biến môi trường
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# AIService
# ---------------------------------------------------------------------------

class AIService:
    """
    Dịch vụ giao tiếp với Gemini API.
    Tự động chọn model 2.5 Flash mới nhất hoặc model hỗ trợ generateContent đầu tiên.
    """

    def __init__(self, model_name: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Chưa có GEMINI_API_KEY trong file .env")

        genai.configure(api_key=api_key)

        # ----- Tự động dò tìm model -----
        if model_name is None:
            self.model_name = self._find_best_model()
        else:
            self.model_name = model_name

        print(f"✅ Sử dụng model: {self.model_name}", file=sys.stderr)
        self.model = genai.GenerativeModel(self.model_name)

    # ------------------------------------------------------------------ #
    #  Tự động chọn model có thể dùng                                     #
    # ------------------------------------------------------------------ #

    def _find_best_model(self) -> str:
        """
        Liệt kê toàn bộ model từ Gemini API, chỉ giữ những model hỗ trợ
        generateContent, sau đó chọn model phù hợp nhất (ưu tiên 2.5 flash).
        """
        try:
            models = genai.list_models()
        except Exception as e:
            print(f"⚠️ Không thể liệt kê model: {e}", file=sys.stderr)
            return "gemini-2.5-flash"  # fallback phổ biến nhất

        available = []
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                available.append(m.name)

        if not available:
            return "gemini-2.5-flash"  # fallback cuối cùng

        # In ra để tiện kiểm tra (có thể xóa sau)
        print(f"📋 Các model khả dụng: {available}", file=sys.stderr)

        # ----- Ưu tiên chọn model 2.5 flash -----
        priority_keywords = [
            "gemini-2.5-flash",  # mạnh mẽ nhất
            "gemini-2.0-flash",
            "gemini-pro",        # legacy
        ]

        for keyword in priority_keywords:
            for name in available:
                if keyword in name:
                    return name

        # Nếu không có model ưu tiên, trả về model đầu tiên hỗ trợ generateContent
        return available[0]

    # ------------------------------------------------------------------ #
    #  Gửi prompt                                                        #
    # ------------------------------------------------------------------ #

    def chat(
        self,
        user_message: str,
        subject: str = "",
        history: list[dict] | None = None,
    ) -> str:
        """Gửi câu hỏi tới Gemini và nhận câu trả lời (có ngữ cảnh môn học)."""

        # Xây dựng system prompt theo môn học
        if subject:
            system_prompt = (
                f"Bạn là trợ lý học tập hữu ích cho môn {subject}. "
                "Trả lời bằng tiếng Việt, giải thích rõ ràng, dễ hiểu, có ví dụ nếu cần."
            )
        else:
            system_prompt = (
                "Bạn là trợ lý học tập đa môn. "
                "Trả lời bằng tiếng Việt, rõ ràng, dễ hiểu."
            )

        # Chuẩn bị lịch sử hội thoại
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Gộp hướng dẫn + câu hỏi mới
        full_prompt = f"{system_prompt}\n\nHọc sinh hỏi: {user_message}"
        contents.append({"role": "user", "parts": [{"text": full_prompt}]})

        try:
            response = self.model.generate_content(
                contents,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1000,
                },
            )
            return response.text
        except Exception as e:
            return f"❌ Lỗi khi kết nối AI: {str(e)}"