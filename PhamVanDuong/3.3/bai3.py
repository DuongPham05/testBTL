import time

# Nhập năm sinh
nam_sinh = int(input("Nhập năm sinh: "))

# Lấy năm hiện tại
x = time.localtime()
nam_hien_tai = x[0]

tuoi = nam_hien_tai - nam_sinh

print(f"Năm sinh {nam_sinh}, vậy bạn {tuoi} tuổi")