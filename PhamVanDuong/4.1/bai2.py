text = input("Nhập đoạn văn: ")

# Ghi vào file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)

# Đọc lại và hiển thị
with open("output.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("Nội dung file:")
    print(content)