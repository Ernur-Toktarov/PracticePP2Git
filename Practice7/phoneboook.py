from connect import connect


def create_table():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100),
                    phone VARCHAR(20) UNIQUE
                )
            """)


def add_or_update_contact():
    username = input("Введите имя: ")
    phone = input("Введите телефон: ")

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (username, phone))

    print("Контакт добавлен или обновлен")


def search_contacts():
    pattern = input("Введите текст для поиска: ")

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            rows = cur.fetchall()

    for row in rows:
        print(row)


def show_contacts_page():
    limit_value = input("Введите limit: ")
    offset_value = input("Введите offset: ")

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_contacts_page(%s, %s)",
                (int(limit_value), int(offset_value))
            )
            rows = cur.fetchall()

    for row in rows:
        print(row)


def delete_contact():
    value = input("Введите имя или телефон: ")

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (value,))

    print("Контакт удален")


def show_all_contacts():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM phonebook ORDER BY id")
            rows = cur.fetchall()

    for row in rows:
        print(row)


def menu():
    create_table()

    while True:
        print("\nPHONEBOOK PRACTICE 8")
        print("1 - Добавить или обновить контакт")
        print("2 - Найти контакт")
        print("3 - Показать контакты по страницам")
        print("4 - Удалить контакт")
        print("5 - Показать все контакты")
        print("0 - Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            add_or_update_contact()
        elif choice == "2":
            search_contacts()
        elif choice == "3":
            show_contacts_page()
        elif choice == "4":
            delete_contact()
        elif choice == "5":
            show_all_contacts()
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неверный ввод")


menu()