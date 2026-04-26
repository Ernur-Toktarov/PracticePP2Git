import shutil
import os

os.makedirs("files", exist_ok=True)

#1 Move file to folder
if os.path.exists("example.txt"):
    shutil.move("example.txt", "files/example.txt")

#2 Copy file from folder
if os.path.exists("files/example.txt"):
    shutil.copy("files/example.txt", "copy_example.txt")

#3 Move file back
if os.path.exists("files/example.txt"):
    shutil.move("files/example.txt", "example.txt")

#4 Copy file to another folder
os.makedirs("backup", exist_ok=True)
shutil.copy("example.txt", "backup/example_copy.txt")

#5 Remove empty directory
# os.rmdir("files")  # only if empty

#6 List files after operations
print("Current files:", os.listdir("."))