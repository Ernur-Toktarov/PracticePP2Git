-- procedures.sql
-- Хранимые процедуры и функции

-- Процедура add_phone: добавляет телефон существующему контакту
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Поиск контакта по имени
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE name = p_contact_name;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name "%" not found', p_contact_name;
    END IF;
    
    -- Добавление телефона
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
    
    RAISE NOTICE 'Phone % added for contact %', p_phone, p_contact_name;
END;
$$;

-- Процедура move_to_group: перемещает контакт в другую группу
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    -- Поиск контакта
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE name = p_contact_name;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name "%" not found', p_contact_name;
    END IF;
    
    -- Поиск или создание группы
    SELECT id INTO v_group_id 
    FROM groups 
    WHERE name = p_group_name;
    
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name)
        RETURNING id INTO v_group_id;
        RAISE NOTICE 'Created new group: %', p_group_name;
    END IF;
    
    -- Перемещение контакта
    UPDATE contacts 
    SET group_id = v_group_id 
    WHERE id = v_contact_id;
    
    RAISE NOTICE 'Contact % moved to group %', p_contact_name, p_group_name;
END;
$$;

-- Функция search_contacts: расширенный поиск по всем полям
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT,
    relevance INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name as group_name,
        STRING_AGG(DISTINCT p.phone || ' (' || p.type || ')', ', ') as phones,
        (
            (CASE WHEN c.name ILIKE '%' || p_query || '%' THEN 3 ELSE 0 END) +
            (CASE WHEN c.email ILIKE '%' || p_query || '%' THEN 2 ELSE 0 END) +
            (CASE WHEN p.phone ILIKE '%' || p_query || '%' THEN 2 ELSE 0 END)
        ) as relevance
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE 
        c.name ILIKE '%' || p_query || '%' OR
        c.email ILIKE '%' || p_query || '%' OR
        p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, g.name, c.name, c.email, c.birthday
    ORDER BY relevance DESC, c.name;
END;
$$ LANGUAGE plpgsql;