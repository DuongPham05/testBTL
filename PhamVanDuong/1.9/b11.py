lst = ["hello", "hi", "python", "code"]
n = int(input("Nhập n: "))

result = [word for word in lst if len(word) > n]
print(result)