import sqlite3


conn = sqlite3.connect('instance/finance.db')
cursor = conn.cursor()


# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL
)
''')


# Transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
amount REAL NOT NULL,
category TEXT NOT NULL,
note TEXT
)
''')


conn.commit()
conn.close()
print("Database initialized successfully!")