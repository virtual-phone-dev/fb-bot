import sqlite3

conn = sqlite3.connect("artistes2.db")  # ex: "artistes2.db", "pages_collecter_artistes.db", etc.

conn.execute("ALTER TABLE pages ADD COLUMN email TEXT")
conn.commit()
conn.close()