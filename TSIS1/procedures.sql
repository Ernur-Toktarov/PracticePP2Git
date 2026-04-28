-- PROCEDURE: add_phone
-- Добавляет новый номер телефона существующему контакту
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR  -- 'home', 'work', 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;

-- Пример:
-- CALL add_phone('alice', '+77001112233', 'mobile');


-- ─────────────────────────────────────────────────────────────
-- PROCEDURE: move_to_group
-- Переносит контакт в группу; создаёт группу, если не существует
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id   INT;
    v_contact_id INT;
BEGIN
    -- Найти или создать группу
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;

    -- Найти контакт
    SELECT id INTO v_contact_id FROM contacts WHERE username = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Обновить группу
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;

-- Пример:
-- CALL move_to_group('alice', 'Family');


-- ─────────────────────────────────────────────────────────────
-- FUNCTION: search_contacts (расширенная — Practice 8 + email + phones)
-- Ищет по username, email и всем телефонам из таблицы phones
-- ─────────────────────────────────────────────────────────────
DROP FUNCTION IF EXISTS search_contacts(TEXT);

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id       INT,
    username VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT
) AS $$
BEGIN
    RETURN QUERY
        SELECT
            c.id,
            c.username,
            c.email,
            c.birthday,
            g.name          AS grp,
            STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE
            c.username ILIKE '%' || p_query || '%'
            OR c.email  ILIKE '%' || p_query || '%'
            OR p.phone  ILIKE '%' || p_query || '%'
        GROUP BY c.id, c.username, c.email, c.birthday, g.name
        ORDER BY c.username;
END;
$$ LANGUAGE plpgsql;

-- Пример:
-- SELECT * FROM search_contacts('alice');
-- SELECT * FROM search_contacts('gmail');
-- SELECT * FROM search_contacts('+770');
