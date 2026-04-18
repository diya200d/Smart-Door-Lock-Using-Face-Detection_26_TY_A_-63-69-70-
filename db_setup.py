import sqlite3

# Connect or create database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop tables if they exist (optional)
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS logs")

# Create 'users' table with 'id', 'name', and 'face' columns
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    face BLOB NOT NULL
)
""")

# Create 'logs' table to store access attempts
c.execute("""
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database created successfully with 'users' (including face column) and 'logs' tables!")