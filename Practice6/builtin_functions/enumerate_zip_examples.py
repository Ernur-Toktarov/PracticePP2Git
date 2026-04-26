names = ["Ana", "Bob", "Ali"]
for i, name in enumerate(names, start=1):
    print(i, name)
# 1 Ana
# 2 Bob
# 3 Ali

keys = ["a", "b", "c"]
values = [10, 20, 30]

for k, v in zip(keys, values):
    print(k, v)
# a 10
# b 20
# c 30

x = "123"
print(type(x))      # <class 'str'>

y = int(x)
print(y, type(y))   # 123 <class 'int'>

z = float("2.5")
print(z, type(z))   # 2.5 <class 'float'>