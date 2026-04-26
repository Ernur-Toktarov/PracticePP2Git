import os

os.makedirs("folder1/folder2/folder3", exist_ok=True)
print("Files in current directory")
print(os.listdir("."))

with open("z.txt","w") as f:
    f.write("it is okay but it is not okay")

    
print("TXT files:")
for file in os.listdir():
    if file.endswith(".txt"):
        print(file)