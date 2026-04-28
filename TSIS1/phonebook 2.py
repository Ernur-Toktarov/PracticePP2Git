import csv
import json
from datetime import date, datetime

from connect import get_connection


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def print_table(rows, headers):
    if not rows:
        print("  [пусто]")
        return
    widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
              for i, h in enumerate(headers)]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  " + "-" * (sum(widths) + 2 * len(widths)))
    for r in rows:
        print(fmt.format(*[str(v) if v is not None else "" for v in r]))


def json_serial(obj):
    """Сериализатор для date/datetime в JSON."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# ══════════════════════════════════════════════════════════════
# 3.2  ADVANCED CONSOLE SEARCH & FILTER
# ══════════════════════════════════════════════════════════════

def filter_by_group():
    """Показать контакты выбранной группы."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name;")
            groups = cur.fetchall()

    if not groups:
        print("  Групп нет.")
        return

    print("\n  Доступные группы:")
    for g in groups:
        print(f"    {g[0]}. {g[1]}")
    gid = input("  Введи ID группы: ").strip()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.username, c.email, c.birthday,
                       STRING_AGG(p.phone || '(' || COALESCE(p.type,'?') || ')', ', ') AS phones
                FROM contacts c
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE c.group_id = %s
                GROUP BY c.id, c.username, c.email, c.birthday
                ORDER BY c.username;
            """, (gid,))
            rows = cur.fetchall()

    print_table(rows, ["ID", "Username", "Email", "Birthday", "Phones"])


def search_by_email():
    """Поиск по частичному совпадению email."""
    pattern = input("  Email (или часть): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.username, c.email, c.birthday
                FROM contacts c
                WHERE c.email ILIKE %s
                ORDER BY c.username;
            """, (f"%{pattern}%",))
            rows = cur.fetchall()
    print_table(rows, ["ID", "Username", "Email", "Birthday"])


def sort_contacts():
    """Вывести все контакты с сортировкой."""
    print("  Сортировать по:")
    print("    1 - username")
    print("    2 - birthday")
    print("    3 - created_at (дата добавления)")
    choice = input("  Выбор: ").strip()
    order = {"1": "username", "2": "birthday", "3": "created_at"}.get(choice, "username")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.username, c.email, c.birthday, c.created_at::date,
                       STRING_AGG(p.phone || '(' || COALESCE(p.type,'?') || ')', ', ')
                FROM contacts c
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.username, c.email, c.birthday, c.created_at
                ORDER BY c.{order} NULLS LAST;
            """)
            rows = cur.fetchall()
    print_table(rows, ["ID", "Username", "Email", "Birthday", "Added", "Phones"])


def paginated_navigation():
    """Листать контакты страницами: next / prev / quit."""
    limit = 5
    offset = 0

    while True:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_page(%s, %s);", (limit, offset))
                rows = cur.fetchall()

        page = offset // limit + 1
        print(f"\n  ── Страница {page} ──")
        print_table(rows, ["ID", "Username", "Phone"])

        cmd = input("  [next / prev / quit]: ").strip().lower()
        if cmd == "next":
            if len(rows) == limit:
                offset += limit
            else:
                print("  Это последняя страница.")
        elif cmd == "prev":
            offset = max(0, offset - limit)
        elif cmd == "quit":
            break


# ══════════════════════════════════════════════════════════════
# 3.3  IMPORT / EXPORT
# ══════════════════════════════════════════════════════════════

def export_to_json():
    """Экспорт всех контактов (с телефонами и группой) в JSON."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.username, c.email, c.birthday,
                       g.name AS group_name,
                       COALESCE(
                           JSON_AGG(
                               JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                           ) FILTER (WHERE p.id IS NOT NULL),
                           '[]'
                       ) AS phones
                FROM contacts c
                LEFT JOIN groups  g ON g.id = c.group_id
                LEFT JOIN phones  p ON p.contact_id = c.id
                GROUP BY c.id, c.username, c.email, c.birthday, g.name
                ORDER BY c.username;
            """)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

    contacts = [dict(zip(cols, r)) for r in rows]
    filename = input("  Имя файла (например contacts.json): ").strip() or "contacts.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  ✅ Экспортировано {len(contacts)} контактов → {filename}")


def import_from_json():
    """Импорт контактов из JSON; при дубликате спрашивает: skip / overwrite."""
    filename = input("  Имя JSON-файла: ").strip()
    try:
        with open(filename, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"  ❌ Файл {filename} не найден.")
        return

    inserted = updated = skipped = 0

    with get_connection() as conn:
        for c in contacts:
            username = c.get("username", "").strip()
            phone    = c.get("phone", c.get("phones", [{}])[0].get("phone", "")) if not c.get("phone") else c.get("phone","")
            email    = c.get("email")
            birthday = c.get("birthday")
            group_name = c.get("group_name") or c.get("group")
            phones_list = c.get("phones", [])

            with conn.cursor() as cur:
                # Проверяем существование
                cur.execute("SELECT id FROM contacts WHERE username = %s;", (username,))
                existing = cur.fetchone()

                if existing:
                    action = input(f"  '{username}' уже есть. [skip/overwrite]: ").strip().lower()
                    if action != "overwrite":
                        skipped += 1
                        continue
                    # Получаем group_id
                    gid = None
                    if group_name:
                        cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                        g = cur.fetchone()
                        gid = g[0] if g else None
                    cur.execute("""
                        UPDATE contacts SET email=%s, birthday=%s, group_id=%s
                        WHERE username=%s;
                    """, (email, birthday, gid, username))
                    updated += 1
                else:
                    # group
                    gid = None
                    if group_name:
                        cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                        g = cur.fetchone()
                        if g:
                            gid = g[0]
                        else:
                            cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id;", (group_name,))
                            gid = cur.fetchone()[0]

                    # основной номер из старой схемы (Practice 7)
                    main_phone = phone or (phones_list[0].get("phone","") if phones_list else "")
                    cur.execute("""
                        INSERT INTO contacts (username, phone, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (username, main_phone, email, birthday, gid))
                    cid = cur.fetchone()[0]

                    # дополнительные телефоны
                    for ph in phones_list:
                        cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s);",
                                    (cid, ph.get("phone"), ph.get("type")))
                    inserted += 1

            conn.commit()

    print(f"  ✅ Вставлено: {inserted}, обновлено: {updated}, пропущено: {skipped}")


def import_from_csv_extended():
    """
    Расширенный CSV-импорт: поддерживает поля email, birthday, group, phone_type.
    Формат заголовка: username,phone,email,birthday,group,phone_type
    """
    filename = input("  CSV-файл: ").strip()
    try:
        f = open(filename, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"  ❌ Файл {filename} не найден.")
        return

    inserted = skipped = 0
    with f, get_connection() as conn:
        reader = csv.DictReader(f)
        for row in reader:
            username   = row.get("username","").strip()
            phone      = row.get("phone","").strip()
            email      = row.get("email","").strip() or None
            birthday   = row.get("birthday","").strip() or None
            group_name = row.get("group","").strip() or None
            ph_type    = row.get("phone_type","").strip() or None

            if not username or not phone:
                skipped += 1
                continue

            with conn.cursor() as cur:
                # group
                gid = None
                if group_name:
                    cur.execute("SELECT id FROM groups WHERE name=%s;", (group_name,))
                    g = cur.fetchone()
                    if g:
                        gid = g[0]
                    else:
                        cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id;", (group_name,))
                        gid = cur.fetchone()[0]

                # upsert contact
                cur.execute("""
                    INSERT INTO contacts (username, phone, email, birthday, group_id)
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT (username) DO UPDATE
                        SET email=EXCLUDED.email,
                            birthday=EXCLUDED.birthday,
                            group_id=EXCLUDED.group_id
                    RETURNING id;
                """, (username, phone, email, birthday, gid))
                cid = cur.fetchone()[0]

                # телефон → таблица phones
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type)
                    VALUES (%s,%s,%s)
                    ON CONFLICT DO NOTHING;
                """, (cid, phone, ph_type))

            conn.commit()
            inserted += 1

    print(f"  ✅ Обработано: {inserted}, пропущено: {skipped}")


# ══════════════════════════════════════════════════════════════
# 3.4  NEW STORED PROCEDURES (вызов из Python)
# ══════════════════════════════════════════════════════════════

def add_phone_to_contact():
    """Вызывает PROCEDURE add_phone."""
    username = input("  Username контакта: ").strip()
    phone    = input("  Номер телефона (+7...): ").strip()
    print("  Тип: home / work / mobile")
    ptype    = input("  Тип: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s);", (username, phone, ptype))
        conn.commit()
    print("  ✅ Телефон добавлен.")


def move_contact_to_group():
    """Вызывает PROCEDURE move_to_group."""
    username   = input("  Username контакта: ").strip()
    group_name = input("  Название группы: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s);", (username, group_name))
        conn.commit()
    print(f"  ✅ Контакт перемещён в группу '{group_name}'.")


def search_all():
    """Вызывает FUNCTION search_contacts (расширенная)."""
    query = input("  Поиск (имя / email / телефон): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (query,))
            rows = cur.fetchall()
    print_table(rows, ["ID", "Username", "Email", "Birthday", "Group", "Phones"])



def main():
    actions = {
        "1":  filter_by_group,
        "2":  search_by_email,
        "3":  sort_contacts,
        "4":  paginated_navigation,
        "5":  export_to_json,
        "6":  import_from_json,
        "7":  import_from_csv_extended,
        "8":  add_phone_to_contact,
        "9":  move_contact_to_group,
        "10": search_all,
    }
    while True:
        print(MENU)
        choice = input("Выбери пункт: ").strip()
        if choice == "0":
            print("Пока!")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
        else:
            print("  Неверный пункт.")


if __name__ == "__main__":
    main()
