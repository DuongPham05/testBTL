lst = [1, 2, 3, 4, 5, 6, 7, 8, 9]
even = [x for x in lst if x % 2 == 0]
odd = [x for x in lst if x % 2 != 0]

print("Chẵn:", even)
print("Lẻ:", odd)