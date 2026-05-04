lst = ['abc', 'xyz', 'abc', '12', 'ii', '12', '5a']
new = [x for x in lst if lst.count(x) == 1]
print(new)