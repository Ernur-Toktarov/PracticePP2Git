import csv
import json
import os
from connect import connect_db


BASE_DIR = os.path.dirname(__file__)


def full_path(filename):
    return os.path.join(BASE_DIR, filename)


def run_sql(filename):
    conn = connect_db()
    cur = conn.cursor()

    with open(full_path(filename), "r", encoding="utf-8") as f:
        sql = f.read()
        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


def get_group_id(cur, group_name):
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("INSERT INTO groups(name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def show_rows(rows):
    if not rows:
        print("No contacts found.")
        return

    for row in rows:
        print("\nID:", row[0])
        print("Name:", row[1])
        print("Email:", row[2])
        print("Birthday:", row[3])
        print("Group:", row[4])


def add_contact():
    conn = connect_db()
    cur = conn.cursor()

    print("\nGroup: Family / Work / Friend / Other")
    print("Phone type: home / work / mobile")

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday (YYYY-MM-DD): ").strip()
    group_name = input("Group: ").strip()
    phone = input("Phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip()

    if not name:
        print("Name is required.")
        cur.close()
        conn.close()
        return

    if phone_type not in ["home", "work", "mobile"]:
        print("Wrong phone type.")
        cur.close()
        conn.close()
        return

    group_id = get_group_id(cur, group_name)

    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    row = cur.fetchone()

    if row:
        contact_id = row[0]
        cur.execute("""
            UPDATE contacts
            SET email = %s, birthday = %s, group_id = %s
            WHERE id = %s
        """, (email or None, birthday or None, group_id, contact_id))
    else:
        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email or None, birthday or None, group_id))
        contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
    """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact saved.")


def show_all():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
    """)

    rows = cur.fetchall()
    show_rows(rows)

    cur.close()
    conn.close()


def search_all():
    conn = connect_db()
    cur = conn.cursor()

    text = input("Search text: ").strip()
    cur.execute("SELECT * FROM search_contacts(%s)", (text,))
    rows = cur.fetchall()
    show_rows(rows)

    cur.close()
    conn.close()


def filter_by_group():
    conn = connect_db()
    cur = conn.cursor()

    group_name = input("Group name: ").strip()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
        ORDER BY c.name
    """, (group_name,))

    rows = cur.fetchall()
    show_rows(rows)

    cur.close()
    conn.close()


def search_by_email():
    conn = connect_db()
    cur = conn.cursor()

    text = input("Email text: ").strip()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.email ILIKE %s
        ORDER BY c.name
    """, (f"%{text}%",))

    rows = cur.fetchall()
    show_rows(rows)

    cur.close()
    conn.close()


def sort_contacts():
    conn = connect_db()
    cur = conn.cursor()

    print("1 - Sort by name")
    print("2 - Sort by birthday")
    print("3 - Sort by created_at")
    choice = input("Choose: ").strip()

    order_field = "name"
    if choice == "2":
        order_field = "birthday"
    elif choice == "3":
        order_field = "created_at"

    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_field} NULLS LAST
    """)

    rows = cur.fetchall()
    show_rows(rows)

    cur.close()
    conn.close()


def paginate():
    conn = connect_db()
    cur = conn.cursor()

    page = 0
    limit = 3

    while True:
        offset = page * limit

        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (limit, offset))
        rows = cur.fetchall()

        print(f"\n--- Page {page + 1} ---")
        show_rows(rows)

        cmd = input("next / prev / quit: ").strip().lower()

        if cmd == "next":
            page += 1
        elif cmd == "prev":
            if page > 0:
                page -= 1
        elif cmd == "quit":
            break

    cur.close()
    conn.close()


def export_json():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
    """)

    rows = cur.fetchall()
    data = []

    for row in rows:
        contact_id = row[0]

        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (contact_id,))
        phones = cur.fetchall()

        item = {
            "name": row[1],
            "email": row[2],
            "birthday": str(row[3]) if row[3] else "",
            "group": row[4],
            "phones": []
        }

        for p in phones:
            item["phones"].append({
                "phone": p[0],
                "type": p[1]
            })

        data.append(item)

    with open(full_path("contacts_export.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    cur.close()
    conn.close()
    print("Exported to contacts_export.json")


def import_json():
    filename = input("JSON file name: ").strip()

    with open(full_path(filename), "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = connect_db()
    cur = conn.cursor()

    for item in data:
        name = item["name"]
        email = item.get("email")
        birthday = item.get("birthday")
        group_name = item.get("group", "Other")

        group_id = get_group_id(cur, group_name)

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        row = cur.fetchone()

        if row:
            answer = input(f"{name} exists. skip or overwrite? ").strip().lower()

            if answer == "skip":
                continue

            contact_id = row[0]

            cur.execute("""
                UPDATE contacts
                SET email = %s, birthday = %s, group_id = %s
                WHERE id = %s
            """, (email or None, birthday or None, group_id, contact_id))

            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        else:
            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, email or None, birthday or None, group_id))

            contact_id = cur.fetchone()[0]

        for p in item["phones"]:
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, p["phone"], p["type"]))

    conn.commit()
    cur.close()
    conn.close()
    print("JSON imported.")


def import_csv():
    filename = input("CSV file name: ").strip()

    conn = connect_db()
    cur = conn.cursor()

    with open(full_path(filename), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row["name"]
            email = row["email"]
            birthday = row["birthday"]
            group_name = row["group_name"]
            phone = row["phone"]
            phone_type = row["phone_type"]

            group_id = get_group_id(cur, group_name)

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            old = cur.fetchone()

            if old:
                contact_id = old[0]
                cur.execute("""
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s
                """, (email or None, birthday or None, group_id, contact_id))
            else:
                cur.execute("""
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (name, email or None, birthday or None, group_id))
                contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("CSV imported.")


def add_phone():
    conn = connect_db()
    cur = conn.cursor()

    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip()

    if phone_type not in ["home", "work", "mobile"]:
        print("Wrong phone type.")
        cur.close()
        conn.close()
        return

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Phone added.")


def move_group():
    conn = connect_db()
    cur = conn.cursor()

    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))

    conn.commit()
    cur.close()
    conn.close()
    print("Group changed.")


def menu():
    while True:
        print("\n1 - Create tables")
        print("2 - Create procedures")
        print("3 - Add contact")
        print("4 - Show all contacts")
        print("5 - Search contacts")
        print("6 - Filter by group")
        print("7 - Search by email")
        print("8 - Sort contacts")
        print("9 - Pagination")
        print("10 - Export JSON")
        print("11 - Import JSON")
        print("12 - Import CSV")
        print("13 - Add phone")
        print("14 - Move to group")
        print("0 - Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            run_sql("schema.sql")
        elif choice == "2":
            run_sql("procedures.sql")
        elif choice == "3":
            add_contact()
        elif choice == "4":
            show_all()
        elif choice == "5":
            search_all()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            search_by_email()
        elif choice == "8":
            sort_contacts()
        elif choice == "9":
            paginate()
        elif choice == "10":
            export_json()
        elif choice == "11":
            import_json()
        elif choice == "12":
            import_csv()
        elif choice == "13":
            add_phone()
        elif choice == "14":
            move_group()
        elif choice == "0":
            break


menu()