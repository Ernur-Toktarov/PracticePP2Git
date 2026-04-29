CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id),
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

INSERT INTO groups(name) VALUES ('Family') ON CONFLICT (name) DO NOTHING;
INSERT INTO groups(name) VALUES ('Work') ON CONFLICT (name) DO NOTHING;
INSERT INTO groups(name) VALUES ('Friend') ON CONFLICT (name) DO NOTHING;
INSERT INTO groups(name) VALUES ('Other') ON CONFLICT (name) DO NOTHING;