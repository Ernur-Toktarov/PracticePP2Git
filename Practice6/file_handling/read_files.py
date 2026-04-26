f = open("demofile.txt", "r")

print(f.read())


f = open("D:\\myfiles\welcome.txt")
print(f.read())

with open("demofile.txt") as f:
  print(f.read())


  f = open("demofile.txt")
print(f.readline())
f.close()

with open("demofile.txt") as f:
  print(f.read(5))