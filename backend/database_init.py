import json
import os
import sqlite3

TAG_MAPPING_PATH = "data/tag_mapping.json"

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

with open(TAG_MAPPING_PATH, "r", encoding="utf-8") as mapping_file:
    tag_mapping = json.load(mapping_file)

cursor.executemany(
    "INSERT OR IGNORE INTO tags (tag_uid, user_key, active) VALUES (?, ?, 1)",
    [(tag_uid, user_key) for tag_uid, user_key in tag_mapping.items()],
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
