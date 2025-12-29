import sqlite3

conn = sqlite3.connect("grievance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_text TEXT,
    department TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database created successfully")
