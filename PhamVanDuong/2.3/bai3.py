# Nhập 3 số nguyên
a = int(input("Nhập a: "))
b = int(input("Nhập b: "))
c = int(input("Nhập c: "))

# a) Tổng và tích
tong = a + b + c
tich = a * b * c
print("Tổng =", tong)
print("Tích =", tich)

# b) Hiệu (ví dụ: a - b, b - c, a - c)
print("Hiệu a - b =", a - b)
print("Hiệu b - c =", b - c)
print("Hiệu a - c =", a - c)

# c) Chia (lấy 2 số bất kỳ, ví dụ a và b)
if b != 0:
    print("Chia nguyên a // b =", a // b)
    print("Chia dư a % b =", a % b)
    print("Chia chính xác a / b =", a / b)
else:
    print("Không thể chia cho 0")