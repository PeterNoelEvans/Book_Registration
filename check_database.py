import sqlite3

# Quick check to verify database exists and tables were created
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

conn.close()
