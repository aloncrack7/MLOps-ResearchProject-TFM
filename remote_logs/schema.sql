CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    email_address TEXT
);

CREATE TABLE services(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT UNIQUE
);

CREATE TABLE subcriptions(
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    uses_telegram INTEGER,
    uses_email INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    UNIQUE (user_id, service_id)
);

INSERT INTO services (service_name) VALUES ("backup");