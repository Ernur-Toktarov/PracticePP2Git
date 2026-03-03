import re

# 1) 'a' followed by zero or more 'b'
s = input()
print(bool(re.fullmatch(r'ab*', s)))


# 2) 'a' followed by 2 to 3 'b'
s = input()
print(bool(re.fullmatch(r'ab{2,3}', s)))


# 3) sequences of lowercase letters joined with underscore
s = input()
print(re.findall(r'[a-z]+_[a-z]+', s))


# 4) one uppercase letter followed by lowercase letters
s = input()
print(re.findall(r'[A-Z][a-z]+', s))


# 5) 'a' followed by anything, ending with 'b'
s = input()
print(bool(re.fullmatch(r'a.*b', s)))


# 6) replace space, comma, dot with colon
s = input()
print(re.sub(r'[ ,.]', ':', s))


# 7) snake_case to camelCase
s = input().split('_')
print(s[0] + ''.join(word.capitalize() for word in s[1:]))


# 8) split string at uppercase letters
s = input()
print(re.findall(r'[A-Z][a-z]*', s))


# 9) insert spaces before capital letters
s = input()
print(re.sub(r'([A-Z])', r' \1', s).strip())


# 10) camelCase to snake_case
s = input()
print(re.sub(r'([A-Z])', r'_\1', s).lower())