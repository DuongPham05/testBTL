import math

a = float(input("Nhap a: "))
b = float(input("Nhap b: "))
c = float(input("Nhap c: "))

if a == 0:
    # Phuong trinh bac 1
    if b == 0:
        if c == 0:
            print("Phuong trinh vo so nghiem")
        else:
            print("Phuong trinh vo nghiem")
    else:
        print(f"Phuong trinh bac 1, nghiem x = {-c/b}")
else:
    delta = b**2 - 4*a*c
    if delta > 0:
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        print(f"Delta = {delta} > 0: 2 nghiem phan biet")
        print(f"  x1 = {x1}")
        print(f"  x2 = {x2}")
    elif delta == 0:
        x = -b / (2*a)
        print(f"Delta = 0: nghiem kep x = {x}")
    else:
        print(f"Delta = {delta} < 0: phuong trinh vo nghiem thuc")