import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
database_name = 'example.db'
connection = sqlite3.connect(database_name)

# Create a cursor object using the cursor() method
cursor = connection.cursor()

# Create a table example
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
)
''')

# Commit the changes and close the connection
connection.commit()
connection.close()