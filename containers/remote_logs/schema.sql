CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    email_address TEXT
);

CREATE TABLE IF NOT EXISTS services(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS subscriptions(
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    uses_telegram INTEGER,
    uses_email INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    UNIQUE (user_id, service_id)
);

INSERT OR IGNORE INTO services (service_name) VALUES ("backup");
INSERT OR IGNORE INTO services (service_name) VALUES ("versions");