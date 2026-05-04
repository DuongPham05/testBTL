n = int(input("Nhap so nguyen duong: "))

chia2 = (n % 2 == 0)
chia3 = (n % 3 == 0)

if chia2 and chia3:
    print(f"{n} chia het cho ca 2 va 3")
elif chia2:
    print(f"{n} chi chia het cho 2")
elif chia3:
    print(f"{n} chi chia het cho 3")
else:
    print(f"{n} khong chia het cho 2 va khong chia het cho 3")