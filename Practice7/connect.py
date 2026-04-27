import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="phonebook_db",
    user="postgres",
    password="your_password"
)

print("Connected successfully!")
conn.close()