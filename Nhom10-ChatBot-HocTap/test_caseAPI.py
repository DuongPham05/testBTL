import os
from dotenv import load_dotenv, find_dotenv

# Tìm đường dẫn file .env
env_path = find_dotenv()
print(f"🔍 Đường dẫn file .env tìm thấy: {env_path}")

# Load file
loaded = load_dotenv(env_path)
print(f"✅ Load thành công: {loaded}")

# In tất cả biến môi trường có chứa 'API' (để kiểm tra xem key đã vào os.environ chưa)
print("\n📋 Các biến môi trường có 'API':")
for k, v in os.environ.items():
    if 'API' in k:
        print(f"  {k} = {v[:10]}...{v[-5:]}")  # chỉ in vài ký tự để bảo mật

# Lấy key
api_key = os.getenv("GEMINI_API_KEY")
print(f"\n🔑 GEMINI_API_KEY = {api_key}")