import re

# 1. 'a' followed by zero or more 'b's
s = input()
print(bool(re.fullmatch(r'ab*', s)))


# 2. 'a' followed by two to three 'b'
s = input()
print(bool(re.fullmatch(r'ab{2,3}', s)))


# 3. Lowercase letters joined with a underscore
s = input()
print(re.findall(r'[a-z]+_[a-z]+', s))


# 4. One upper case letter followed by lower case letters
s = input()
print(re.findall(r'[A-Z][a-z]+', s))


# 5. 'a' followed by anything, ending in 'b'
s = input()
print(bool(re.fullmatch(r'a.*b', s)))


# 6. Replace space, comma, or dot with a colon
s = input()
print(re.sub(r'[ ,.]', ':', s))


# 7. Snake case to camel case (Пример: my_snake_case -> MySnakeCase)
s = input().split('_')
print(''.join(word.capitalize() for word in s))


# 8. Split a string at uppercase letters
s = input()
print(re.findall(r'[A-Z][^A-Z]*', s))


# 9. Insert spaces between words starting with capital letters
s = input()
print(re.sub(r'([a-z])([A-Z])', r'\1 \2', s))


# 10. Camel case to snake case (Пример: CamelCase -> camel_case)
s = input()
# Находим места, где маленькая буква (или цифра) граничит с большой
result = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
print(result.lower().lstrip('_'))