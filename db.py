import sqlite3

DB_PATH = "garage.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name: row["opens_at"]
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS garages (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            opens_at INTEGER NOT NULL,  -- hour of the day, e.g. 9
            closes_at INTEGER NOT NULL  -- e.g. 17 means the last slot starts at 16:00
        );

        -- One row per taken slot. UNIQUE stops the same slot being taken twice.
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            garage_id INTEGER NOT NULL REFERENCES garages(id),
            date TEXT NOT NULL,  -- e.g. 2026-11-10
            time TEXT NOT NULL,  -- e.g. 10:00
            customer_name TEXT NOT NULL,
            UNIQUE (garage_id, date, time)
        );

        INSERT OR IGNORE INTO garages (id, name, opens_at, closes_at)
        VALUES (1, 'Test Garage', 9, 17);

        -- One taken slot, so you can see it missing from the free times.
        INSERT OR IGNORE INTO bookings (garage_id, date, time, customer_name)
        VALUES (1, '2026-11-10', '10:00', 'Test Customer');
        """
    )
    conn.commit()
    conn.close()
