#1)Create a generator that generates the squares of numbers up to some number N.
def squares_to_n(n):
    for i in range(n + 1):
        yield i * i

n = int(input())
for x in squares_to_n(n):
    print(x)


#2)Write a program using generator to print the even numbers between 0 and n in comma separated form where n is input from console.
def evens(n):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
print(",".join(str(x) for x in evens(n)))


#3)Define a function with a generator which can iterate the numbers, which are divisible by 3 and 4, between a given range 0 and n.
def mult_12(n):
    for i in range(0, n + 1):
        if i % 12 == 0:
            yield i

n = int(input())
for x in mult_12(n):
    print(x, end=" ")


#4)Implement a generator called squares to yield the square of all numbers from (a) to (b). Test it with a "for" loop and print each of the yielded values.
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

a, b = map(int, input().split())
for x in squares(a, b):
    print(x)


#5)Implement a generator that returns all numbers from (n) down to 0.
def down(n):
    while n >= 0:
        yield n
        n -= 1

n = int(input())
for x in down(n):
    print(x)