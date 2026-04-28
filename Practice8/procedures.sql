CREATE OR REPLACE PROCEDURE upsert_contact(p_username VARCHAR, p_phone VARCHAR)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_username) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE username = p_username;
    ELSE
        INSERT INTO phonebook(username, phone)
        VALUES (p_username, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE username = p_value OR phone = p_value;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE insert_many_contacts(
    IN p_usernames TEXT[],
    IN p_phones TEXT[],
    INOUT invalid_data TEXT[] DEFAULT '{}'
)
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(p_usernames, 1) LOOP
        IF p_phones[i] ~ '^[0-9]{11,15}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_usernames[i]) THEN
                UPDATE phonebook
                SET phone = p_phones[i]
                WHERE username = p_usernames[i];
            ELSE
                INSERT INTO phonebook(username, phone)
                VALUES (p_usernames[i], p_phones[i]);
            END IF;
        ELSE
            invalid_data := array_append(
                invalid_data,
                p_usernames[i] || ' - ' || p_phones[i]
            );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;