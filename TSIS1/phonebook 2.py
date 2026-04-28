import csv
import json
from datetime import datetime
from connect import get_connection


VALID_PHONE_TYPES = {"home", "work", "mobile"}


def normalize_phone_type(value: str) -> str:
    value = (value or "").strip().lower()
    if value not in VALID_PHONE_TYPES:
        return "mobile"
    return value


def get_or_create_group(cur, group_name: str) -> int:
    group_name = (group_name or "Other").strip() or "Other"
    cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0]


def insert_contact(cur, name, email=None, birthday=None, group_name="Other"):
    group_id = get_or_create_group(cur, group_name)
    cur.execute(
        """
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (name, email, birthday or None, group_id),
    )
    return cur.fetchone()[0]


def add_phone_row(cur, contact_id, phone, phone_type="mobile"):
    if not phone:
        return
    cur.execute(
        """
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (contact_id, phone) DO NOTHING
        """,
        (contact_id, phone.strip(), normalize_phone_type(phone_type)),
    )


def add_contact_interactive():
    name = input("Name: ").strip()
    if not name:
        print("Name is required.")
        return

    email = input("Email (optional): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
    group_name = input("Group (Family/Work/Friend/Other): ").strip() or "Other"

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        if cur.fetchone():
            print("Contact with this name already exists.")
            conn.rollback()
            return

        contact_id = insert_contact(cur, name, email, birthday, group_name)

        while True:
            phone = input("Phone (leave empty to stop): ").strip()
            if not phone:
                break
            phone_type = input("Type (home/work/mobile): ").strip()
            add_phone_row(cur, contact_id, phone, phone_type)

        conn.commit()
        print("Contact added.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def add_phone_to_contact():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, normalize_phone_type(phone_type)))
        conn.commit()
        print("Phone added.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def move_contact_group():
    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()
        print("Group updated.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def search_contacts_advanced():
    query = input("Search text (name/email/phone): ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        if not rows:
            print("No results.")
            return
        for r in rows:
            print(f"[{r[0]}] {r[1]} | email={r[2]} | birthday={r[3]} | group={r[4]} | phones={r[5]}")
    finally:
        cur.close()
        conn.close()


def search_by_email_partial():
    part = input("Email contains: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email
            FROM contacts c
            WHERE COALESCE(c.email, '') ILIKE %s
            ORDER BY c.name
            """,
            (f"%{part}%",),
        )
        rows = cur.fetchall()
        if not rows:
            print("No results.")
            return
        for r in rows:
            print(r)
    finally:
        cur.close()
        conn.close()


def browse_with_filters():
    group_filter = input("Filter by group (empty = all): ").strip()
    email_filter = input("Filter by email part (empty = all): ").strip()
    sort_key = input("Sort by (name/birthday/date_added): ").strip().lower() or "name"
    page_size = int(input("Page size: ").strip() or "5")

    order_map = {"name": "c.name", "birthday": "c.birthday NULLS LAST", "date_added": "c.date_added"}
    if sort_key not in order_map:
        sort_key = "name"

    where = []
    params = []

    if group_filter:
        where.append("g.name = %s")
        params.append(group_filter)

    if email_filter:
        where.append("COALESCE(c.email, '') ILIKE %s")
        params.append(f"%{email_filter}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    page = 0
    while True:
        offset = page * page_size

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT COUNT(DISTINCT c.id)
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                {where_sql}
                """,
                tuple(params),
            )
            total = cur.fetchone()[0]
            total_pages = max((total + page_size - 1) // page_size, 1)

            cur.execute(
                f"""
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    c.date_added,
                    g.name AS group_name,
                    COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.id), '') AS phones
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                {where_sql}
                GROUP BY c.id, g.name
                ORDER BY {order_map[sort_key]}
                LIMIT %s OFFSET %s
                """,
                tuple(params + [page_size, offset]),
            )
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        print(f"\nPage {page + 1}/{total_pages} (total: {total})")
        if not rows:
            print("No contacts on this page.")
        else:
            for r in rows:
                print(f"[{r[0]}] {r[1]} | {r[2]} | {r[3]} | {r[4]} | group={r[5]} | phones={r[6]}")

        cmd = input("Command: next / prev / quit: ").strip().lower()
        if cmd == "next":
            if page + 1 < total_pages:
                page += 1
            else:
                print("Last page.")
        elif cmd == "prev":
            if page > 0:
                page -= 1
            else:
                print("First page.")
        elif cmd == "quit":
            break


def export_to_json():
    filename = input("Export file (default contacts_export.json): ").strip() or "contacts_export.json"

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, c.date_added, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.name
            """
        )
        contacts = cur.fetchall()

        result = []
        for c in contacts:
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                (c[0],),
            )
            phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]
            result.append(
                {
                    "name": c[1],
                    "email": c[2],
                    "birthday": str(c[3]) if c[3] else None,
                    "date_added": str(c[4]),
                    "group": c[5],
                    "phones": phones,
                }
            )

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Exported to {filename}")
    finally:
        cur.close()
        conn.close()


def import_from_json():
    filename = input("Import file (default contacts_export.json): ").strip() or "contacts_export.json"

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()
    try:
        for item in data:
            name = (item.get("name") or "").strip()
            if not name:
                continue

            email = item.get("email")
            birthday = item.get("birthday")
            group_name = item.get("group") or "Other"
            phones = item.get("phones", [])

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                decision = input(f'"{name}" exists. skip or overwrite? [s/o]: ').strip().lower()
                if decision == "s":
                    continue
                if decision == "o":
                    cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                else:
                    continue

            contact_id = insert_contact(cur, name, email, birthday, group_name)
            for ph in phones:
                add_phone_row(cur, contact_id, ph.get("phone"), ph.get("type", "mobile"))

        conn.commit()
        print("JSON import done.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def parse_phones_field(phones_field: str):
    """
    Format example:
    mobile:7771112233;home:7774445566
    """
    result = []
    if not phones_field:
        return result
    chunks = [x.strip() for x in phones_field.split(";") if x.strip()]
    for ch in chunks:
        if ":" in ch:
            t, p = ch.split(":", 1)
            result.append((p.strip(), normalize_phone_type(t.strip())))
        else:
            result.append((ch.strip(), "mobile"))
    return result


def import_from_csv():
    filename = input("CSV file (default contacts.csv): ").strip() or "contacts.csv"

    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    try:
        with open(filename, "r", encoding="utf-8") as f:
            sample = f.read(2048)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            has_header = csv.Sniffer().has_header(sample)

            if has_header:
                reader = csv.DictReader(f, dialect=dialect)
                for row in reader:
                    name = (row.get("name") or "").strip()
                    if not name:
                        continue

                    email = (row.get("email") or "").strip() or None
                    birthday = (row.get("birthday") or "").strip() or None
                    group_name = (row.get("group") or "Other").strip() or "Other"

                    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                    existing = cur.fetchone()
                    if existing:
                        contact_id = existing[0]
                        cur.execute(
                            """
                            UPDATE contacts
                            SET email = COALESCE(%s, email),
                                birthday = COALESCE(%s, birthday),
                                group_id = %s
                            WHERE id = %s
                            """,
                            (email, birthday, get_or_create_group(cur, group_name), contact_id),
                        )
                    else:
                        contact_id = insert_contact(cur, name, email, birthday, group_name)
                        inserted += 1

                    if row.get("phones"):
                        for p, t in parse_phones_field(row.get("phones")):
                            add_phone_row(cur, contact_id, p, t)
                    else:
                        add_phone_row(cur, contact_id, row.get("phone"), row.get("type", "mobile"))
            else:
                reader = csv.reader(f, dialect=dialect)
                for row in reader:
                    if len(row) < 2:
                        continue
                    name = row[0].strip()
                    phone = row[1].strip()
                    if not name:
                        continue

                    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                    existing = cur.fetchone()
                    if existing:
                        contact_id = existing[0]
                    else:
                        contact_id = insert_contact(cur, name, None, None, "Other")
                        inserted += 1

                    add_phone_row(cur, contact_id, phone, "mobile")

        conn.commit()
        print(f"CSV import done. New contacts inserted: {inserted}")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def run_sql_file(path):
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()
        print(f"Executed: {path}")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def init_db():
    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")
    print("Database initialized.")

def menu():
    while True:
        print("\n--- PhoneBook Extended ---")
        print("1. Init DB (schema + procedures)")
        print("2. Add contact")
        print("3. Add phone to existing contact (procedure)")
        print("4. Move contact to group (procedure)")
        print("5. Search (name/email/phone) via function")
        print("6. Search by email (partial)")
        print("7. Browse with filters + sort + next/prev pagination")
        print("8. Import from CSV (extended)")
        print("9. Export to JSON")
        print("10. Import from JSON")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            init_db()
        elif choice == "2":
            add_contact_interactive()
        elif choice == "3":
            add_phone_to_contact()
        elif choice == "4":
            move_contact_group()
        elif choice == "5":
            search_contacts_advanced()
        elif choice == "6":
            search_by_email_partial()
        elif choice == "7":
            browse_with_filters()
        elif choice == "8":
            import_from_csv()
        elif choice == "9":
            export_to_json()
        elif choice == "10":
            import_from_json()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()