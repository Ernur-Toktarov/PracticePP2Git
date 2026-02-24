#1)Write a Python program to convert degree to radian.
deg = float(input())
rad = deg * 3.141592653589793 / 180
print(rad)


#2)Write a Python program to calculate the area of a trapezoid.
h = float(input())
a = float(input())
b = float(input())

area = (a + b) / 2 * h
print(area)


#3)Write a Python program to calculate the area of regular polygon.
import math

n = int(input())
a = float(input())

area = (n * a * a) / (4 * math.tan(math.pi / n))
print(area)


#4)Write a Python program to calculate the area of a parallelogram.
base = float(input())
h = float(input())

print(base * h)