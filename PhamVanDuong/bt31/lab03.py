n = int(input("n = "))

if 80 <= n <= 100:
    for i in range(80, n + 1):
        if i % 2 == 0 and i % 3 == 0:
            print(i)