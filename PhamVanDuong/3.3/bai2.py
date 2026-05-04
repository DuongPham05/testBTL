# Nhập 3 số nguyên dương
a = int(input("Nhập a: "))
b = int(input("Nhập b: "))
c = int(input("Nhập c: "))

# Điều kiện tam giác
if a + b > c and a + c > b and b + c > a:
    print("Độ dài ba cạnh tam giác")
else:
    print("Đây không phải độ dài ba cạnh tam giác")