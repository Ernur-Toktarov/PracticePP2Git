import csv
from connect import connect


# 🔹 CREATE — добавить контакт
def insert_contact(name, phone):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added!")


# 🔹 INSERT из CSV
def insert_from_csv(filename):
    conn = connect()
    cur = conn.cursor()

    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (row['name'], row['phone'])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV data inserted!")


# 🔹 READ — получить все
def get_all_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# 🔹 FILTER (по имени)
def search_by_name(name):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s",
        ('%' + name + '%',)
    )

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


# 🔹 FILTER (по номеру)
def search_by_phone(prefix):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE phone LIKE %s",
        (prefix + '%',)
    )

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


# 🔹 UPDATE
def update_contact(old_name, new_name=None, new_phone=None):
    conn = connect()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE contacts SET name=%s WHERE name=%s",
            (new_name, old_name)
        )

    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone=%s WHERE name=%s",
            (new_phone, old_name)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Updated!")


# 🔹 DELETE
def delete_contact(name=None, phone=None):
    conn = connect()
    cur = conn.cursor()

    if name:
        cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
    elif phone:
        cur.execute("DELETE FROM contacts WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()
    print("Deleted!")


# 🔹 МЕНЮ
def menu():
    while True:
        print("\nPhoneBook Menu:")
        print("1. Add contact")
        print("2. Insert from CSV")
        print("3. Show all contacts")
        print("4. Search by name")
        print("5. Search by phone")
        print("6. Update contact")
        print("7. Delete contact")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)

        elif choice == "2":
            insert_from_csv("contacts.csv")

        elif choice == "3":
            get_all_contacts()

        elif choice == "4":
            name = input("Enter name: ")
            search_by_name(name)

        elif choice == "5":
            prefix = input("Enter phone prefix: ")
            search_by_phone(prefix)

        elif choice == "6":
            old = input("Old name: ")
            new_name = input("New name (or Enter): ")
            new_phone = input("New phone (or Enter): ")

            update_contact(
                old,
                new_name if new_name else None,
                new_phone if new_phone else None
            )

        elif choice == "7":
            name = input("Name to delete (or Enter): ")
            phone = input("Phone to delete (or Enter): ")

            delete_contact(
                name if name else None,
                phone if phone else None
            )

        elif choice == "0":
            break


if __name__ == "__main__":
    menu()