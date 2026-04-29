DROP FUNCTION IF EXISTS search_contacts(TEXT);
DROP FUNCTION IF EXISTS get_contacts_page(INTEGER, INTEGER);
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    c_id INTEGER;
BEGIN
    SELECT id INTO c_id
    FROM contacts
    WHERE name = p_contact_name;

    IF c_id IS NOT NULL THEN
        INSERT INTO phones(contact_id, phone, type)
        VALUES (c_id, p_phone, p_type);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    g_id INTEGER;
BEGIN
    SELECT id INTO g_id
    FROM groups
    WHERE name = p_group_name;

    IF g_id IS NULL THEN
        INSERT INTO groups(name)
        VALUES (p_group_name)
        RETURNING id INTO g_id;
    END IF;

    UPDATE contacts
    SET group_id = g_id
    WHERE name = p_contact_name;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR
)
LANGUAGE sql
AS $$
    SELECT DISTINCT c.id, c.name, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%';
$$;


CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR
)
LANGUAGE sql
AS $$
    SELECT c.id, c.name, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
$$;