import os
import sqlite3

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/rooster.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tags (
        tag_uid TEXT PRIMARY KEY,
        user_key TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS students (
        user_key TEXT PRIMARY KEY,
        display_name TEXT NOT NULL
    )
    """
)

cursor.executemany(
    "INSERT OR IGNORE INTO tags (tag_uid, user_key, active) VALUES (?, ?, 1)",
    [
        ("04A1B23C9F", "zine"),
        ("12B4C56D8E", "tom"),
        ("99Z8Y7X6W5", "rekawt"),
    ],
)

cursor.executemany(
    "INSERT OR IGNORE INTO students (user_key, display_name) VALUES (?, ?)",
    [
        ("zine", "Zine-Eddine"),
        ("tom", "Tom"),
        ("rekawt", "Rekawt"),
    ],
)

conn.commit()
conn.close()
print("Database aangemaakt: data/rooster.db")
