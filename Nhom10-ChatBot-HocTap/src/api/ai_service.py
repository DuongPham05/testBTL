from google import genai
from google.genai import types
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# Xác định thư mục gốc dự án và nạp biến môi trường
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# AIService
# ---------------------------------------------------------------------------

class AIService:
    def __init__(self):
        # Load biến môi trường (nếu cần, dù SDK mới tự động đọc GEMINI_API_KEY)
        load_dotenv()
        # SDK mới sẽ tự động lấy API key từ biến môi trường GEMINI_API_KEY
        self.client = genai.Client()
        # Chỉ định model bạn muốn sử dụng, ví dụ: gemini-2.5-flash
        self.model_name = "gemini-2.5-flash"

    def chat(
        self,
        user_message: str,
        subject: str = "",
        history: list[dict] | None = None,
    ) -> str:
        """Phương thức chat đơn giản, không dùng tool."""
        # Xây dựng system prompt
        system_prompt = "Bạn là trợ lý học tập hữu ích."
        if subject:
            system_prompt = f"Bạn là trợ lý học tập cho môn {subject}. Trả lời bằng tiếng Việt."

        # Tạo nội dung cho API call
        contents = []
        # Thêm system instruction
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        )
        
        # Thêm lịch sử chat
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        # Thêm tin nhắn hiện tại
        contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        # Gọi API
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )
        return response.text

    def chat_with_tools(
        self,
        user_message: str,
        tools_def: list,
        subject: str = "",
        history: list[dict] | None = None,
    ):
        """Phương thức chat hỗ trợ tool calling."""
        system_prompt = "Bạn là trợ lý học tập hữu ích."
        if subject:
            system_prompt = f"Bạn là trợ lý học tập cho môn {subject}. Trả lời bằng tiếng Việt."

        # Chuẩn bị nội dung và config với tools
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            tools=tools_def,  # Thêm tools vào config
        )
        
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        # Gọi API với tools
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )
        return response