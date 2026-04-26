nums_str = ["1", "2", "3"]
nums = list(map(int, nums_str))
print(nums)  # [1, 2, 3]

nums = [1, -2, 3, 0, 4]
pos = list(filter(lambda x: x > 0, nums))
print(pos)  # [1, 3, 4]

from functools import reduce

nums = [1, 2, 3, 4]
s = reduce(lambda a, b: a + b, nums)
print(s)  # 10