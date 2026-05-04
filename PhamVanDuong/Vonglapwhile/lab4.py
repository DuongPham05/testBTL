n = int(input("Nhập n: "))

print("Các số nguyên tố nhỏ hơn", n, "là:")

for num in range(2, n):
    la_so_nguyen_to = True
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            la_so_nguyen_to = False
            break

    if la_so_nguyen_to:
        print(num, end=" ")