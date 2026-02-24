#1)Write a Python program to subtract five days from current date.
from datetime import date, timedelta

today = date.today()
print(today - timedelta(days=5))


#2) Write a Python program to print yesterday, today, tomorrow.
from datetime import date, timedelta

today = date.today()
print(today - timedelta(days=1))
print(today)
print(today + timedelta(days=1))


#3)Write a Python program to drop microseconds from datetime.
from datetime import datetime

now = datetime.now()
print(now.replace(microsecond=0))


#4)Write a Python program to calculate two date difference in seconds.
from datetime import datetime

a = datetime.strptime(input(), "%Y-%m-%d %H:%M:%S")
b = datetime.strptime(input(), "%Y-%m-%d %H:%M:%S")

print(int((b - a).total_seconds()))