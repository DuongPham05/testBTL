lst = ['abc', 'xyz', 'abc', '12', 'ii', '12', '5a']
new = list(dict.fromkeys(lst))  # giữ thứ tự
print(new)