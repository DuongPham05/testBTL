n = int(input("Nhập n: "))
giai_thua = 1

for i in range(1, n + 1):
    giai_thua *= i

print(f"{n}! =", giai_thua)