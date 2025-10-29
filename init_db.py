è# Initialize / reset the local SQLite database for Farire
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "farire.db")

schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

with sqlite3.connect(DB_PATH) as conn:
    conn.executescript(schema)
    conn.commit()

print("✅ Database ready at", DB_PATH)