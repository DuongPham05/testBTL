n = int(input("Nhập n: "))

if n < 2:
    print(n, "không phải là số nguyên tố")
else:
    la_so_nguyen_to = True
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            la_so_nguyen_to = False
            break

    if la_so_nguyen_to:
        print(n, "là số nguyên tố")
    else:
        print(n, "không phải là số nguyên tố")