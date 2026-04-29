from connect import get_connection
import json

def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (group,))

    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    group_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING
    """, (name, email, birthday, group_id))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added")


def add_phone():
    name = input("Contact name: ")
    phone = input("Phone: ")
    phone_type = input("Type (home/work/mobile): ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Phone added")


def search():
    query = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def filter_by_group():
    group = input("Group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
    """, (group,))

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


def sort_contacts():
    sort_by = input("Sort by (name/birthday/created_at): ")

    if sort_by not in ["name", "birthday", "created_at"]:
        print("Wrong field")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT name, email, birthday, created_at
        FROM contacts
        ORDER BY {sort_by}
    """)

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


def export_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)

    contacts = []

    for contact in cur.fetchall():
        contact_id, name, email, birthday, group = contact

        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
        """, (contact_id,))

        phones = cur.fetchall()

        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday),
            "group": group,
            "phones": [
                {"phone": p[0], "type": p[1]} for p in phones
            ]
        })

    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

    cur.close()
    conn.close()
    print("Exported to contacts.json")


def menu():
    while True:
        print("""
1. Add contact
2. Add phone
3. Search
4. Filter by group
5. Sort
6. Export JSON
0. Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            add_phone()
        elif choice == "3":
            search()
        elif choice == "4":
            filter_by_group()
        elif choice == "5":
            sort_contacts()
        elif choice == "6":
            export_json()
        elif choice == "0":
            break
        else:
            print("Wrong choice")


menu()